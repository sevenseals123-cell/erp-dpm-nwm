import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import sqlite3
import plotly.express as px
from io import BytesIO

# ==============================================================================
# 1. CONFIGURATION DE LA PAGE & STYLE PROFESSIONNEL
# ==============================================================================
st.set_page_config(
    page_title="DPM Nador West Med - ERP Ressources Matérielles (SM ISPO)",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #0b2545 0%, #134074 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    .main-header h2 { color: white; margin: 0; font-size: 1.6rem; }
    .main-header p { color: #eef4ed; margin: 0.2rem 0 0 0; font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. BASE DE DONNÉES SQLITE & PRÉ-CHARGEMENT INITIAL (VHF SOREMAR)
# ==============================================================================
conn = sqlite3.connect('dpm_nwm_ispo_erp.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    # DPM_FO_23 : Le Registre des Infrastructures de La DPM
    c.execute('''CREATE TABLE IF NOT EXISTS fo23_infrastructures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        infrastructure TEXT,
        besoins_reparation TEXT,
        reparations_commentaire TEXT,
        reparations_cout REAL,
        criticite TEXT,
        date_mise_a_jour DATE,
        observations TEXT
    )''')

    # DPM_FO_24 & DPM_FO_25 & Classes DMP_PR_02 : Ameublement, Vigie, VHF, PPUs, Simulateur, Voitures
    c.execute('''CREATE TABLE IF NOT EXISTS fo24_25_equipements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        classe TEXT,
        article TEXT,
        reference_serie TEXT,
        cout_estime REAL,
        util_etat TEXT,
        util_quantite INTEGER,
        util_emplacement TEXT,
        stock_quantite INTEGER,
        stock_localisation TEXT,
        besoin_achat TEXT,
        besoin_reparation TEXT,
        date_reception DATE,
        echeance_garantie DATE,
        observations TEXT
    )''')

    # DPM_FO_26 & DPM_FO_27 : Consommations Générales et Pharmaceutiques
    c.execute('''CREATE TABLE IF NOT EXISTS fo26_27_consommables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categorie TEXT,
        article TEXT,
        emplacement TEXT,
        debut_qte INTEGER,
        debut_prix_unit REAL,
        debut_date_expir DATE,
        livre_qte INTEGER,
        livre_prix_unit REAL,
        fin_qte INTEGER,
        fin_prix_unit REAL,
        fin_date_expir DATE,
        observations TEXT
    )''')

    # DPM_FO_28 : Le Registre de la Consommation de la Pilotine
    c.execute('''CREATE TABLE IF NOT EXISTS fo28_pilotine (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_pilotine TEXT,
        debut_date DATE,
        debut_gasoil REAL,
        debut_lubrif REAL,
        livre_date DATE,
        livre_gasoil REAL,
        livre_lubrif REAL,
        fin_date DATE,
        fin_gasoil REAL,
        fin_lubrif REAL,
        observations TEXT
    )''')

    # DPM_FO_29 : Le Registre des EPIs
    c.execute('''CREATE TABLE IF NOT EXISTS fo29_epis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        article TEXT,
        util_nombre INTEGER,
        util_etat TEXT,
        util_echeance DATE,
        util_cout REAL,
        stock_nombre INTEGER,
        stock_etat TEXT,
        stock_echeance DATE,
        stock_cout REAL,
        stock_local TEXT,
        besoin_achat TEXT,
        besoin_maintenance TEXT,
        observations TEXT
    )''')

    # DPM_FO_30 : Préparation du Budget (Prévisions & Investissements)
    c.execute('''CREATE TABLE IF NOT EXISTS fo30_budget_lignes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_ligne TEXT,
        classe_rubrique TEXT,
        article_investissement TEXT,
        justification TEXT,
        prix_unitaire_estime REAL,
        besoin_unites_estime REAL,
        cout_estime_n REAL,
        qte_annee_prec REAL,
        cout_annee_prec REAL,
        observations TEXT
    )''')

    # DPM_CL_06 & DPM_CL_07 : Checklists Spécifications d'Achat & Maintenance/Utilisation
    c.execute('''CREATE TABLE IF NOT EXISTS cl06_07_checklists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_checklist TEXT,
        equipement_rubrique TEXT,
        specifications_achat TEXT,
        recommandations_utilisation TEXT,
        recommandations_maintenance TEXT,
        observations TEXT
    )''')
    conn.commit()

def seed_initial_data():
    """Pré-charge la réception officielle des VHF SOREMAR si la table est vide."""
    c.execute("SELECT COUNT(*) FROM fo24_25_equipements")
    if c.fetchone()[0] == 0:
        serials_vhf = [
            "627RBX0048", "627RBX0057", "627RBX0067", "627RBX0104", "627TUT2578",
            "627RBX0029", "627RBX0033", "627RBX0035", "627RBX0039", "627RBX0045"
        ]
        # Insertion des 10 Radios VHF Motorola DP4801 ATEX (15 800 MAD HT / unité)
        for idx, sn in enumerate(serials_vhf, start=1):
            c.execute('''INSERT INTO fo24_25_equipements (
                classe, article, reference_serie, cout_estime,
                util_etat, util_quantite, util_emplacement,
                stock_quantite, stock_localisation,
                besoin_achat, besoin_reparation,
                date_reception, echeance_garantie, observations
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                "Radios Portatifs VHF",
                f"Radio VHF Marine ATEX Motorola DP4801 Ex #{idx:02d}",
                f"S/N: {sn} (Code C0100087)",
                15800.00,
                "Bon", 1, "Station de Pilotage / Pilotes",
                0, "Magasin DPM",
                "Aucun", "Aucune",
                "2026-10-15", "2028-10-15",
                "BC N°20260014 | BL-CAS2610/0453 | Facture F-RAD26/0024 SOREMAR | PV Réception Définitive du 15/10/2026 (Garantie 2 ans)"
            ))

        # Insertion des 15 Batteries de rechange ATEX DP4401 (57 750 MAD HT total)
        c.execute('''INSERT INTO fo24_25_equipements (
            classe, article, reference_serie, cout_estime,
            util_etat, util_quantite, util_emplacement,
            stock_quantite, stock_localisation,
            besoin_achat, besoin_reparation,
            date_reception, echeance_garantie, observations
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            "Radios Portatifs VHF",
            "Batterie de rechange ATEX DP4401 (Lot de 15)",
            "Code C0113530 (PU: 3 850,00 MAD)",
            57750.00,
            "Bon", 10, "En service avec VHF",
            5, "Armoire de charge Vigie",
            "Aucun", "Aucune",
            "2026-10-15", "2028-10-15",
            "BC N°20260014 | Facture F-RAD26/0024 SOREMAR | 15 unités à 3 850 MAD HT"
        ))

        # Insertion des accessoires inclus (Housses & IMPRES ATEX Noise Can)
        c.execute('''INSERT INTO fo24_25_equipements (
            classe, article, reference_serie, cout_estime,
            util_etat, util_quantite, util_emplacement,
            stock_quantite, stock_localisation,
            besoin_achat, besoin_reparation,
            date_reception, echeance_garantie, observations
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            "Radios Portatifs VHF",
            "Accessoires VHF : 10 Housses FUNDA DURA + 10 Motorola IMPRES ATEX Noise Can",
            "Codes C0126461 & C0326460",
            0.00,
            "Bon", 10, "Station de Pilotage",
            0, "Magasin DPM",
            "Aucun", "Aucune",
            "2026-10-15", "2028-10-15",
            "Inclus dans le pack VHF BC N°20260014 (BL-CAS2610/0453)"
        ))

    # Pré-chargement Checklists CL_06 & CL_07 pour les VHF ATEX si vide
    c.execute("SELECT COUNT(*) FROM cl06_07_checklists")
    if c.fetchone()[0] == 0:
        c.execute('''INSERT INTO cl06_07_checklists (
            type_checklist, equipement_rubrique, specifications_achat,
            recommandations_utilisation, recommandations_maintenance, observations
        ) VALUES (?,?,?,?,?,?)''', (
            "DPM_CL_06 & DPM_CL_07 (Critique)",
            "Radios Portatifs VHF Marines ATEX (Motorola DP4801 Ex)",
            "Certification ATEX poussières/gaz, étanchéité IP67, bande VHF marine 136-174 MHz, GPS intégré, chargeurs IMPRES, garantie min. 2 ans.",
            "Utiliser exclusivement avec la batterie ATEX DP4401 et la housse de protection. Vérifier le niveau de charge avant chaque manœuvre.",
            "Ne jamais ouvrir ou charger en atmosphère explosive. Nettoyer les contacts à l'eau douce après exposition saline. Contrôle annuel d'étanchéité.",
            "Fournisseur : SOREMAR (Beni Ansar / Casablanca)"
        ))

    # Pré-chargement de la ligne budgétaire VHF dans FO_30 si vide
    c.execute("SELECT COUNT(*) FROM fo30_budget_lignes")
    if c.fetchone()[0] == 0:
        c.execute('''INSERT INTO fo30_budget_lignes (
            type_ligne, classe_rubrique, article_investissement, justification,
            prix_unitaire_estime, besoin_unites_estime, cout_estime_n,
            qte_annee_prec, cout_annee_prec, observations
        ) VALUES (?,?,?,?,?,?,?,?,?,?)''', (
            "Investissement",
            "Radios Portatifs VHF",
            "Acquisition de 10 Radios VHF portatives marines ATEX + 15 Batteries de rechange",
            "Dotation initiale de sécurité pour les opérations de pilotage maritime à Nador West Med",
            21575.00, 10.0, 215750.00,
            0.0, 0.0,
            "BC N°20260014 - Facture SOREMAR F-RAD26/0024 (215 750,00 MAD TTC)"
        ))
    conn.commit()

init_db()
seed_initial_data()

# ==============================================================================
# 3. FONCTIONS UTILITAIRES (EXPORT EXCEL SIMPLE & MULTI-FEUILLES)
# ==============================================================================
def to_excel_single(df, sheet_name="Registre_ISPO"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    return output.getvalue()

def to_excel_global():
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.read_sql_query("SELECT * FROM fo23_infrastructures", conn).to_excel(writer, index=False, sheet_name="FO_23_Infrastructures")
        pd.read_sql_query("SELECT * FROM fo24_25_equipements", conn).to_excel(writer, index=False, sheet_name="FO_24_25_Equipements")
        pd.read_sql_query("SELECT * FROM fo26_27_consommables", conn).to_excel(writer, index=False, sheet_name="FO_26_27_Consommables")
        pd.read_sql_query("SELECT * FROM fo28_pilotine", conn).to_excel(writer, index=False, sheet_name="FO_28_Pilotine")
        pd.read_sql_query("SELECT * FROM fo29_epis", conn).to_excel(writer, index=False, sheet_name="FO_29_EPIs")
        pd.read_sql_query("SELECT * FROM fo30_budget_lignes", conn).to_excel(writer, index=False, sheet_name="FO_30_Budget")
        pd.read_sql_query("SELECT * FROM cl06_07_checklists", conn).to_excel(writer, index=False, sheet_name="CL_06_07_Checklists")
    return output.getvalue()

def parse_date_safe(val):
    try:
        if pd.isna(val) or not str(val).strip():
            return date.today()
        return pd.to_datetime(val).date()
    except Exception:
        return date.today()

# ==============================================================================
# 4. BARRE LATÉRALE DE NAVIGATION
# ==============================================================================
st.sidebar.markdown("## ⚓ DPM Nador West Med")
st.sidebar.markdown("**Périmètre :** Ressources Matérielles  \n**Référentiel :** SM ISPO (`DMP_PR_02`)  \n**Pilote Responsable RM :** Omar Dialmy")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation Officielle SM ISPO",
    [
        "📊 Tableau de Bord ISPO (DPM_FI_02)",
        "🏗️ Infrastructures (DPM_FO_23)",
        "📡 Équipements, Vigie, Ameublement & VHF (FO_24/25)",
        "📦 Consommables & Pharmacie (FO_26/27)",
        "🚤 Consommation Pilotine (DPM_FO_28)",
        "🦺 Registre des EPIs (DPM_FO_29)",
        "✅ Checklists Achats & Maintenance (CL_06/07)",
        "💰 Préparation du Budget (DPM_FO_30)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 Télécharger le Cartable Complet (Excel)",
    data=to_excel_global(),
    file_name=f"Cartable_RM_DPM_NWM_ISPO_{date.today()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

# En-tête principal
st.markdown("""
<div class="main-header">
    <h2>⚓ Direction du Pilotage Maritime — Nador West Med</h2>
    <p>Système de Management ISPO • Gestion Intégrée des Ressources Matérielles (DMP_PR_02 / DPM_FI_02)</p>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# MODULE 1 : TABLEAU DE BORD ISPO (DPM_FI_02)
# ==============================================================================
if menu == "📊 Tableau de Bord ISPO (DPM_FI_02)":
    st.subheader("📊 Tableau de Bord & Surveillance du Processus RM (`DPM_FI_02`)")
    st.caption("Finalité : Garantir la disponibilité et l'adéquation des ressources matérielles critiques pour la qualité et la sécurité du pilotage maritime.")

    df_infra = pd.read_sql_query("SELECT * FROM fo23_infrastructures", conn)
    df_equip = pd.read_sql_query("SELECT * FROM fo24_25_equipements", conn)
    df_conso = pd.read_sql_query("SELECT * FROM fo26_27_consommables", conn)
    df_pil = pd.read_sql_query("SELECT * FROM fo28_pilotine", conn)
    df_epi = pd.read_sql_query("SELECT * FROM fo29_epis", conn)

    aujourd_hui = pd.Timestamp(date.today())
    limite_30j = aujourd_hui + pd.Timedelta(days=30)

    # 1. Calcul des indisponibilités / réparations critiques (KPI DPM_FI_02)
    nb_indispo_equip = len(df_equip[df_equip['util_etat'].isin(['À réparer', 'Hors service'])]) if not df_equip.empty else 0
    nb_indispo_infra = len(df_infra[df_infra['criticite'] == 'Critique - Urgent']) if not df_infra.empty else 0
    kpi_indispo = nb_indispo_equip + nb_indispo_infra

    # 2. Calcul des alertes d'échéance EPI (30 jours ou dépassé)
    alertes_epi_df = pd.DataFrame()
    if not df_epi.empty:
        df_epi['util_echeance_dt'] = pd.to_datetime(df_epi['util_echeance'], errors='coerce')
        alertes_epi_df = df_epi[df_epi['util_echeance_dt'] <= limite_30j]

    # 3. Calcul des alertes Pharmacie (30 jours ou dépassé)
    alertes_pharma_df = pd.DataFrame()
    df_pharma = df_conso[df_conso['categorie'] == 'Pharmacie (FO_27)'].copy() if not df_conso.empty else pd.DataFrame()
    if not df_pharma.empty:
        df_pharma['fin_date_expir_dt'] = pd.to_datetime(df_pharma['fin_date_expir'], errors='coerce')
        alertes_pharma_df = df_pharma[df_pharma['fin_date_expir_dt'] <= limite_30j]

    # 4. Valeur totale du patrimoine matériel enregistré
    total_patrimoine = (df_equip['cout_estime'].sum() if not df_equip.empty else 0.0) + \
                       (df_epi['util_cout'].sum() + df_epi['stock_cout'].sum() if not df_epi.empty else 0.0) + \
                       (df_infra['reparations_cout'].sum() if not df_infra.empty else 0.0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("KPI ISPO : Indisponibilités Critiques", f"{kpi_indispo}", delta="Cible : 0 (Mensuel)", delta_color="inverse" if kpi_indispo > 0 else "normal")
    col2.metric("Dotations & Équipements Actifs", f"{int(df_equip['util_quantite'].sum()) if not df_equip.empty else 0} unités")
    col3.metric("Alertes Échéances (EPI & Pharmacie)", f"{len(alertes_epi_df) + len(alertes_pharma_df)}", delta_color="inverse" if (len(alertes_epi_df) + len(alertes_pharma_df)) > 0 else "normal")
    col4.metric("Valeur Matérielle Engagée", f"{total_patrimoine:,.2f} MAD")

    if kpi_indispo == 0 and len(alertes_epi_df) == 0 and len(alertes_pharma_df) == 0:
        st.success("✅ **Conformité ISPO Totale :** Aucune indisponibilité critique ni échéance dépassée à moins de 30 jours.")
    else:
        if kpi_indispo > 0:
            st.error(f"🚨 **Point Critique (`DPM_FI_02`) :** {kpi_indispo} ressource(s) matérielle(s) signalée(s) en état 'À réparer / Hors service' ou 'Critique'.")
        if not alertes_epi_df.empty:
            st.warning(f"⚠️ **Alerte EPI (`DPM_FO_29`) :** {len(alertes_epi_df)} lot(s) d'EPI arrivent à échéance dans moins de 30 jours.")
            st.dataframe(alertes_epi_df[['id', 'article', 'util_nombre', 'util_echeance', 'observations']], use_container_width=True)
        if not alertes_pharma_df.empty:
            st.warning(f"⚠️ **Alerte Infirmerie (`DPM_FO_27`) :** {len(alertes_pharma_df)} article(s) pharmaceutique(s) arrivent à péremption.")
            st.dataframe(alertes_pharma_df[['id', 'article', 'fin_qte', 'fin_date_expir', 'observations']], use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Analyse Visuelle des Ressources Matérielles")
    c_graph1, c_graph2 = st.columns(2)

    with c_graph1:
        st.markdown("**Répartition de la Valeur par Classe de Ressources (`DMP_PR_02`)**")
        if not df_equip.empty and df_equip['cout_estime'].sum() > 0:
            df_grp = df_equip.groupby('classe', as_index=False)['cout_estime'].sum()
            fig_pie = px.pie(df_grp, values='cout_estime', names='classe', hole=0.45, color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Aucun coût d'équipement enregistré.")

    with c_graph2:
        st.markdown("**Suivi des Consommations Gasoil & Lubrifiant Pilotine (`DPM_FO_28`)**")
        if not df_pil.empty:
            df_pil['gasoil_consomme'] = df_pil['debut_gasoil'] + df_pil['livre_gasoil'] - df_pil['fin_gasoil']
            df_pil['lubrif_consomme'] = df_pil['debut_lubrif'] + df_pil['livre_lubrif'] - df_pil['fin_lubrif']
            fig_bar = px.bar(df_pil, x='fin_date', y=['gasoil_consomme', 'lubrif_consomme'], barmode='group', labels={'value': 'Litres', 'fin_date': 'Période'})
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Saisissez un relevé dans 'Consommation Pilotine (DPM_FO_28)' pour afficher le graphique.")

# ==============================================================================
# MODULE 2 : INFRASTRUCTURES PERMANENTES (DPM_FO_23)
# ==============================================================================
elif menu == "🏗️ Infrastructures (DPM_FO_23)":
    st.subheader("🏗️ Registre des Infrastructures de La DPM (`DPM_FO_23`)")
    tab1, tab2, tab3 = st.tabs(["📋 Registre & Export", "➕ Nouvel Enregistrement", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_infra = pd.read_sql_query("SELECT * FROM fo23_infrastructures", conn)
        st.dataframe(df_infra, use_container_width=True)
        if not df_infra.empty:
            st.download_button("📥 Exporter DPM_FO_23 (Excel)", data=to_excel_single(df_infra, "DPM_FO_23"), file_name="DPM_FO_23_Infrastructures.xlsx")

    with tab2:
        with st.form("add_fo23"):
            c1, c2 = st.columns(2)
            with c1:
                infra = st.text_input("Infrastructure (ex: Station de Pilotage, Quai Pilotine, Vigie)")
                besoins = st.text_area("Besoins de réparation")
                criticite = st.selectbox("Niveau de Criticité ISPO", ["Normal", "Moyen", "Critique - Urgent"])
            with c2:
                rep_comm = st.text_area("Réparations réalisées - Commentaire")
                rep_cout = st.number_input("Réparations réalisées - Coût (MAD)", min_value=0.0, step=100.0)
                dt_maj = st.date_input("Date de relevé", date.today())
                obs = st.text_input("Observations")
            if st.form_submit_button("➕ Enregistrer dans DPM_FO_23"):
                c.execute('''INSERT INTO fo23_infrastructures (
                    infrastructure, besoins_reparation, reparations_commentaire,
                    reparations_cout, criticite, date_mise_a_jour, observations
                ) VALUES (?,?,?,?,?,?,?)''', (infra, besoins, rep_comm, rep_cout, criticite, str(dt_maj), obs))
                conn.commit()
                st.success("Infrastructure enregistrée avec succès !")
                st.rerun()

    with tab3:
        df_infra = pd.read_sql_query("SELECT * FROM fo23_infrastructures", conn)
        if not df_infra.empty:
            id_sel = st.selectbox(
                "Sélectionner la ligne à modifier ou supprimer",
                df_infra['id'].tolist(),
                format_func=lambda x: f"ID #{x} — {df_infra[df_infra['id']==x]['infrastructure'].values[0]}"
            )
            row = df_infra[df_infra['id'] == id_sel].iloc[0]
            with st.form("edit_fo23"):
                c1, c2 = st.columns(2)
                with c1:
                    u_infra = st.text_input("Infrastructure", value=str(row['infrastructure']))
                    u_besoins = st.text_area("Besoins de réparation", value=str(row['besoins_reparation']))
                    crit_list = ["Normal", "Moyen", "Critique - Urgent"]
                    u_crit = st.selectbox("Niveau de Criticité ISPO", crit_list, index=crit_list.index(row['criticite']) if row['criticite'] in crit_list else 0)
                with c2:
                    u_comm = st.text_area("Réparations réalisées - Commentaire", value=str(row['reparations_commentaire']))
                    u_cout = st.number_input("Réparations réalisées - Coût (MAD)", min_value=0.0, value=float(row['reparations_cout']))
                    u_dt = st.date_input("Date de relevé", value=parse_date_safe(row['date_mise_a_jour']))
                    u_obs = st.text_input("Observations", value=str(row['observations']))

                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Enregistrer toutes les modifications"):
                    c.execute('''UPDATE fo23_infrastructures SET
                        infrastructure=?, besoins_reparation=?, reparations_commentaire=?,
                        reparations_cout=?, criticite=?, date_mise_a_jour=?, observations=?
                        WHERE id=?''', (u_infra, u_besoins, u_comm, u_cout, u_crit, str(u_dt), u_obs, id_sel))
                    conn.commit()
                    st.success("Modification enregistrée !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo23_infrastructures WHERE id=?", (id_sel,))
                    conn.commit()
                    st.warning("Enregistrement supprimé.")
                    st.rerun()
        else:
            st.info("Aucune infrastructure enregistrée.")

# ==============================================================================
# MODULE 3 : ÉQUIPEMENTS, VIGIE, AMEUBLEMENT & VHF (DPM_FO_24 / DPM_FO_25)
# ==============================================================================
elif menu == "📡 Équipements, Vigie, Ameublement & VHF (FO_24/25)":
    st.subheader("📡 Registre des Équipements : Ameublement (`FO_24`), Vigie (`FO_25`), VHF, PPU, Simulateur & Voitures")
    classes_pr02 = [
        "Radios Portatifs VHF",
        "Équipements de la Vigie (DPM_FO_25)",
        "Équipements d'Ameublement (DPM_FO_24)",
        "PPUs (Portable Pilot Units)",
        "Simulateur de La DPM",
        "Parc des Voitures de Service",
        "Parc des Pilotines (Armement)"
    ]
    etats_list = ["Bon", "Moyen", "À réparer", "Hors service"]

    tab1, tab2, tab3 = st.tabs(["📋 Registre & Export", "➕ Nouvel Équipement", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_eq = pd.read_sql_query("SELECT * FROM fo24_25_equipements", conn)
        filtre_classe = st.multiselect("Filtrer par Classe (`DMP_PR_02`)", options=classes_pr02, default=classes_pr02)
        df_filtered = df_eq[df_eq['classe'].isin(filtre_classe)] if not df_eq.empty else df_eq
        st.dataframe(df_filtered, use_container_width=True)
        if not df_filtered.empty:
            st.download_button("📥 Exporter la sélection (Excel)", data=to_excel_single(df_filtered, "Equipements_DPM"), file_name="DPM_FO_24_25_Equipements.xlsx")

    with tab2:
        with st.form("add_fo24_25"):
            c1, c2, c3 = st.columns(3)
            with c1:
                classe = st.selectbox("Classe de Ressource (`DMP_PR_02`)", classes_pr02)
                article = st.text_input("Article / Désignation")
                ref_serie = st.text_input("Numéro de Série / Code Article")
                cout_est = st.number_input("Coût Estimé / Prix d'achat HT (MAD)", min_value=0.0, step=100.0)
            with c2:
                st.markdown("**En Utilisation**")
                u_etat = st.selectbox("État (En utilisation)", etats_list)
                u_qte = st.number_input("Quantité en utilisation", min_value=0, value=1)
                u_emp = st.text_input("Emplacement / Affectation", value="Station de Pilotage")
                st.markdown("**En Stock**")
                s_qte = st.number_input("Quantité en stock", min_value=0, value=0)
                s_loc = st.text_input("Localisation stock", value="Magasin DPM")
            with c3:
                st.markdown("**Besoins & Traçabilité ISPO**")
                b_achat = st.text_input("Besoin d'Achat", value="Aucun")
                b_repa = st.text_input("Besoin de Réparation", value="Aucune")
                dt_rec = st.date_input("Date de Réception", date.today())
                dt_gar = st.date_input("Échéance Garantie / Révision", date.today() + timedelta(days=730))
                obs = st.text_area("Observations (N° BC, BL, Facture, PV)")

            if st.form_submit_button("➕ Enregistrer l'équipement"):
                c.execute('''INSERT INTO fo24_25_equipements (
                    classe, article, reference_serie, cout_estime,
                    util_etat, util_quantite, util_emplacement,
                    stock_quantite, stock_localisation,
                    besoin_achat, besoin_reparation,
                    date_reception, echeance_garantie, observations
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                    classe, article, ref_serie, cout_est,
                    u_etat, u_qte, u_emp, s_qte, s_loc,
                    b_achat, b_repa, str(dt_rec), str(dt_gar), obs
                ))
                conn.commit()
                st.success("Équipement ajouté avec succès !")
                st.rerun()

    with tab3:
        df_eq = pd.read_sql_query("SELECT * FROM fo24_25_equipements", conn)
        if not df_eq.empty:
            id_sel = st.selectbox(
                "Sélectionner l'ID de l'équipement à modifier ou supprimer",
                df_eq['id'].tolist(),
                format_func=lambda x: f"ID #{x} — [{df_eq[df_eq['id']==x]['classe'].values[0]}] {df_eq[df_eq['id']==x]['article'].values[0]} ({df_eq[df_eq['id']==x]['reference_serie'].values[0]})"
            )
            row = df_eq[df_eq['id'] == id_sel].iloc[0]
            with st.form("edit_fo24_25"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    u_classe = st.selectbox("Classe de Ressource", classes_pr02, index=classes_pr02.index(row['classe']) if row['classe'] in classes_pr02 else 0)
                    u_article = st.text_input("Article / Désignation", value=str(row['article']))
                    u_ref = st.text_input("Numéro de Série / Code", value=str(row['reference_serie']))
                    u_cout = st.number_input("Coût Estimé / Prix HT (MAD)", min_value=0.0, value=float(row['cout_estime']))
                with c2:
                    u_etat = st.selectbox("État (En utilisation)", etats_list, index=etats_list.index(row['util_etat']) if row['util_etat'] in etats_list else 0)
                    u_qte = st.number_input("Quantité en utilisation", min_value=0, value=int(row['util_quantite']))
                    u_emp = st.text_input("Emplacement / Affectation", value=str(row['util_emplacement']))
                    s_qte = st.number_input("Quantité en stock", min_value=0, value=int(row['stock_quantite']))
                    s_loc = st.text_input("Localisation stock", value=str(row['stock_localisation']))
                with c3:
                    b_achat = st.text_input("Besoin d'Achat", value=str(row['besoin_achat']))
                    b_repa = st.text_input("Besoin de Réparation", value=str(row['besoin_reparation']))
                    dt_rec = st.date_input("Date de Réception", value=parse_date_safe(row['date_reception']))
                    dt_gar = st.date_input("Échéance Garantie / Révision", value=parse_date_safe(row['echeance_garantie']))
                    obs = st.text_area("Observations", value=str(row['observations']))

                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Enregistrer toutes les modifications"):
                    c.execute('''UPDATE fo24_25_equipements SET
                        classe=?, article=?, reference_serie=?, cout_estime=?,
                        util_etat=?, util_quantite=?, util_emplacement=?,
                        stock_quantite=?, stock_localisation=?,
                        besoin_achat=?, besoin_reparation=?,
                        date_reception=?, echeance_garantie=?, observations=?
                        WHERE id=?''', (
                        u_classe, u_article, u_ref, u_cout,
                        u_etat, u_qte, u_emp, s_qte, s_loc,
                        b_achat, b_repa, str(dt_rec), str(dt_gar), obs, id_sel
                    ))
                    conn.commit()
                    st.success("Tous les paramètres de l'équipement ont été mis à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement cet équipement"):
                    c.execute("DELETE FROM fo24_25_equipements WHERE id=?", (id_sel,))
                    conn.commit()
                    st.warning("Équipement supprimé.")
                    st.rerun()
        else:
            st.info("Aucun équipement enregistré.")

# ==============================================================================
# MODULE 4 : CONSOMMABLES GÉNÉRAUX & PHARMACIE (DPM_FO_26 & DPM_FO_27)
# ==============================================================================
elif menu == "📦 Consommables & Pharmacie (FO_26/27)":
    st.subheader("📦 État des Consommations Générales (`DPM_FO_26`) & Pharmaceutiques (`DPM_FO_27`)")
    tab1, tab2, tab3 = st.tabs(["📋 États & Calculs Automatiques", "➕ Ajouter un Article", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_c = pd.read_sql_query("SELECT * FROM fo26_27_consommables", conn)
        if not df_c.empty:
            df_c['Coût Début'] = df_c['debut_qte'] * df_c['debut_prix_unit']
            df_c['Coût Livré'] = df_c['livre_qte'] * df_c['livre_prix_unit']
            df_c['Coût Fin'] = df_c['fin_qte'] * df_c['fin_prix_unit']
            df_c['Qté Consommée'] = (df_c['debut_qte'] + df_c['livre_qte']) - df_c['fin_qte']
            df_c['Coût des Consommations (MAD)'] = (df_c['Coût Début'] + df_c['Coût Livré']) - df_c['Coût Fin']

            st.metric("Coût Total des Consommations de la Période", f"{df_c['Coût des Consommations (MAD)'].sum():,.2f} MAD")
            st.dataframe(df_c, use_container_width=True)
            st.download_button("📥 Exporter FO_26 / FO_27 (Excel)", data=to_excel_single(df_c, "FO_26_27_Consommations"), file_name="DPM_FO_26_27_Consommables.xlsx")
        else:
            st.info("Aucun consommable ou produit pharmaceutique enregistré.")

    with tab2:
        with st.form("add_fo26_27"):
            c1, c2, c3 = st.columns(3)
            with c1:
                cat = st.selectbox("Registre", ["Consommations Générales (FO_26)", "Pharmacie (FO_27)"])
                art = st.text_input("Article / Médicament")
                emp = st.text_input("Emplacement", value="Station de Pilotage / Infirmerie")
                obs = st.text_input("Observation")
            with c2:
                st.markdown("**Existant Début & Livré**")
                d_qte = st.number_input("Qté Début de période", min_value=0, value=0)
                d_pu = st.number_input("Prix Unitaire Début (MAD)", min_value=0.0, value=0.0)
                d_exp = st.date_input("Date Expiration (Stock Début - si Pharmacie)", date.today() + timedelta(days=365))
                l_qte = st.number_input("Qté Livrée durant la période", min_value=0, value=0)
                l_pu = st.number_input("Prix Unitaire Livré (MAD)", min_value=0.0, value=0.0)
            with c3:
                st.markdown("**Existant Fin de Période**")
                f_qte = st.number_input("Qté Fin de période", min_value=0, value=0)
                f_pu = st.number_input("Prix Unitaire Fin (MAD)", min_value=0.0, value=0.0)
                f_exp = st.date_input("Date Expiration (Stock Fin - si Pharmacie)", date.today() + timedelta(days=365))

            if st.form_submit_button("➕ Enregistrer"):
                c.execute('''INSERT INTO fo26_27_consommables (
                    categorie, article, emplacement,
                    debut_qte, debut_prix_unit, debut_date_expir,
                    livre_qte, livre_prix_unit,
                    fin_qte, fin_prix_unit, fin_date_expir, observations
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', (
                    cat, art, emp, d_qte, d_pu, str(d_exp), l_qte, l_pu, f_qte, f_pu, str(f_exp), obs
                ))
                conn.commit()
                st.success("Article enregistré avec succès !")
                st.rerun()

    with tab3:
        df_c = pd.read_sql_query("SELECT * FROM fo26_27_consommables", conn)
        if not df_c.empty:
            id_sel = st.selectbox(
                "Sélectionner l'ID à modifier ou supprimer",
                df_c['id'].tolist(),
                format_func=lambda x: f"ID #{x} — [{df_c[df_c['id']==x]['categorie'].values[0]}] {df_c[df_c['id']==x]['article'].values[0]}"
            )
            row = df_c[df_c['id'] == id_sel].iloc[0]
            with st.form("edit_fo26_27"):
                c1, c2, c3 = st.columns(3)
                cats = ["Consommations Générales (FO_26)", "Pharmacie (FO_27)"]
                with c1:
                    u_cat = st.selectbox("Registre", cats, index=cats.index(row['categorie']) if row['categorie'] in cats else 0)
                    u_art = st.text_input("Article", value=str(row['article']))
                    u_emp = st.text_input("Emplacement", value=str(row['emplacement']))
                    u_obs = st.text_input("Observation", value=str(row['observations']))
                with c2:
                    u_dqte = st.number_input("Qté Début", min_value=0, value=int(row['debut_qte']))
                    u_dpu = st.number_input("PU Début (MAD)", min_value=0.0, value=float(row['debut_prix_unit']))
                    u_dexp = st.date_input("Date Expir Début", value=parse_date_safe(row['debut_date_expir']))
                    u_lqte = st.number_input("Qté Livrée", min_value=0, value=int(row['livre_qte']))
                    u_lpu = st.number_input("PU Livré (MAD)", min_value=0.0, value=float(row['livre_prix_unit']))
                with c3:
                    u_fqte = st.number_input("Qté Fin", min_value=0, value=int(row['fin_qte']))
                    u_fpu = st.number_input("PU Fin (MAD)", min_value=0.0, value=float(row['fin_prix_unit']))
                    u_fexp = st.date_input("Date Expir Fin", value=parse_date_safe(row['fin_date_expir']))

                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Enregistrer toutes les modifications"):
                    c.execute('''UPDATE fo26_27_consommables SET
                        categorie=?, article=?, emplacement=?,
                        debut_qte=?, debut_prix_unit=?, debut_date_expir=?,
                        livre_qte=?, livre_prix_unit=?,
                        fin_qte=?, fin_prix_unit=?, fin_date_expir=?, observations=?
                        WHERE id=?''', (
                        u_cat, u_art, u_emp, u_dqte, u_dpu, str(u_dexp),
                        u_lqte, u_lpu, u_fqte, u_fpu, str(u_fexp), u_obs, id_sel
                    ))
                    conn.commit()
                    st.success("Modification enregistrée !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo26_27_consommables WHERE id=?", (id_sel,))
                    conn.commit()
                    st.warning("Article supprimé.")
                    st.rerun()
        else:
            st.info("Aucun enregistrement à modifier.")

# ==============================================================================
# MODULE 5 : REGISTRE DE LA CONSOMMATION DE LA PILOTINE (DPM_FO_28)
# ==============================================================================
elif menu == "🚤 Consommation Pilotine (DPM_FO_28)":
    st.subheader("🚤 Registre de la Consommation de la Pilotine (`DPM_FO_28`)")
    tab1, tab2, tab3 = st.tabs(["📋 Registre & Bilan Périodique", "➕ Nouveau Relevé", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_p = pd.read_sql_query("SELECT * FROM fo28_pilotine", conn)
        if not df_p.empty:
            df_p['Gasoil Consommé (L)'] = df_p['debut_gasoil'] + df_p['livre_gasoil'] - df_p['fin_gasoil']
            df_p['Lubrifiant Consommé (L)'] = df_p['debut_lubrif'] + df_p['livre_lubrif'] - df_p['fin_lubrif']

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Consommation Totale Gasoil", f"{df_p['Gasoil Consommé (L)'].sum():,.1f} L")
            k2.metric("Consommation Moyenne Gasoil / Période", f"{df_p['Gasoil Consommé (L)'].mean():,.1f} L")
            k3.metric("Consommation Totale Lubrifiant", f"{df_p['Lubrifiant Consommé (L)'].sum():,.1f} L")
            k4.metric("Consommation Moyenne Lubrifiant", f"{df_p['Lubrifiant Consommé (L)'].mean():,.1f} L")

            st.dataframe(df_p, use_container_width=True)
            st.download_button("📥 Exporter DPM_FO_28 (Excel)", data=to_excel_single(df_p, "DPM_FO_28_Pilotine"), file_name="DPM_FO_28_Pilotine.xlsx")
        else:
            st.info("Aucun relevé de consommation pilotine enregistré.")

    with tab2:
        with st.form("add_fo28"):
            nom_pil = st.text_input("Identification de la Pilotine", value="Pilotine NWM 1")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Existant Début de Période**")
                d_dt = st.date_input("Date Début", date.today() - timedelta(days=30))
                d_gas = st.number_input("Gasoil Début (L)", min_value=0.0, value=0.0)
                d_lub = st.number_input("Lubrifiant Début (L)", min_value=0.0, value=0.0)
            with c2:
                st.markdown("**Livré durant la Période**")
                l_dt = st.date_input("Date Livraison", date.today() - timedelta(days=15))
                l_gas = st.number_input("Gasoil Livré (L)", min_value=0.0, value=0.0)
                l_lub = st.number_input("Lubrifiant Livré (L)", min_value=0.0, value=0.0)
            with c3:
                st.markdown("**Existant Fin de Période**")
                f_dt = st.date_input("Date Fin", date.today())
                f_gas = st.number_input("Gasoil Fin (L)", min_value=0.0, value=0.0)
                f_lub = st.number_input("Lubrifiant Fin (L)", min_value=0.0, value=0.0)
            obs = st.text_input("Observation")

            if st.form_submit_button("➕ Enregistrer le relevé FO_28"):
                c.execute('''INSERT INTO fo28_pilotine (
                    nom_pilotine, debut_date, debut_gasoil, debut_lubrif,
                    livre_date, livre_gasoil, livre_lubrif,
                    fin_date, fin_gasoil, fin_lubrif, observations
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (
                    nom_pil, str(d_dt), d_gas, d_lub, str(l_dt), l_gas, l_lub, str(f_dt), f_gas, f_lub, obs
                ))
                conn.commit()
                st.success("Relevé Pilotine enregistré !")
                st.rerun()

    with tab3:
        df_p = pd.read_sql_query("SELECT * FROM fo28_pilotine", conn)
        if not df_p.empty:
            id_sel = st.selectbox(
                "Sélectionner le relevé à modifier ou supprimer",
                df_p['id'].tolist(),
                format_func=lambda x: f"ID #{x} — {df_p[df_p['id']==x]['nom_pilotine'].values[0]} (Fin: {df_p[df_p['id']==x]['fin_date'].values[0]})"
            )
            row = df_p[df_p['id'] == id_sel].iloc[0]
            with st.form("edit_fo28"):
                u_nom = st.text_input("Identification de la Pilotine", value=str(row['nom_pilotine']))
                c1, c2, c3 = st.columns(3)
                with c1:
                    u_ddt = st.date_input("Date Début", value=parse_date_safe(row['debut_date']))
                    u_dgas = st.number_input("Gasoil Début (L)", min_value=0.0, value=float(row['debut_gasoil']))
                    u_dlub = st.number_input("Lubrifiant Début (L)", min_value=0.0, value=float(row['debut_lubrif']))
                with c2:
                    u_ldt = st.date_input("Date Livraison", value=parse_date_safe(row['livre_date']))
                    u_lgas = st.number_input("Gasoil Livré (L)", min_value=0.0, value=float(row['livre_gasoil']))
                    u_llub = st.number_input("Lubrifiant Livré (L)", min_value=0.0, value=float(row['livre_lubrif']))
                with c3:
                    u_fdt = st.date_input("Date Fin", value=parse_date_safe(row['fin_date']))
                    u_fgas = st.number_input("Gasoil Fin (L)", min_value=0.0, value=float(row['fin_gasoil']))
                    u_flub = st.number_input("Lubrifiant Fin (L)", min_value=0.0, value=float(row['fin_lubrif']))
                u_obs = st.text_input("Observation", value=str(row['observations']))

                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Enregistrer toutes les modifications"):
                    c.execute('''UPDATE fo28_pilotine SET
                        nom_pilotine=?, debut_date=?, debut_gasoil=?, debut_lubrif=?,
                        livre_date=?, livre_gasoil=?, livre_lubrif=?,
                        fin_date=?, fin_gasoil=?, fin_lubrif=?, observations=?
                        WHERE id=?''', (
                        u_nom, str(u_ddt), u_dgas, u_dlub, str(u_ldt), u_lgas, u_llub, str(u_fdt), u_fgas, u_flub, u_obs, id_sel
                    ))
                    conn.commit()
                    st.success("Relevé mis à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo28_pilotine WHERE id=?", (id_sel,))
                    conn.commit()
                    st.warning("Relevé supprimé.")
                    st.rerun()
        else:
            st.info("Aucun relevé à modifier.")

# ==============================================================================
# MODULE 6 : REGISTRE DES EPIs (DPM_FO_29)
# ==============================================================================
elif menu == "🦺 Registre des EPIs (DPM_FO_29)":
    st.subheader("🦺 Registre des Équipements de Protection Individuelle (`DPM_FO_29`)")
    etats_epi = ["Neuf", "Bon", "Moyen", "À remplacer"]
    tab1, tab2, tab3 = st.tabs(["📋 Registre & Export", "➕ Nouvel EPI", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_e = pd.read_sql_query("SELECT * FROM fo29_epis", conn)
        st.dataframe(df_e, use_container_width=True)
        if not df_e.empty:
            st.download_button("📥 Exporter DPM_FO_29 (Excel)", data=to_excel_single(df_e, "DPM_FO_29_EPIs"), file_name="DPM_FO_29_EPIs.xlsx")

    with tab2:
        with st.form("add_fo29"):
            art = st.text_input("Article EPI (ex: Gilet de sauvetage gonflable 275N SOLAS, Casque marin, Chaussures de sécurité)")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**En Utilisation**")
                u_nb = st.number_input("Nombre (En utilisation)", min_value=0, value=1)
                u_et = st.selectbox("État (En utilisation)", etats_epi)
                u_ec = st.date_input("Échéance Révision/Péremption (Util.)", date.today() + timedelta(days=365))
                u_ct = st.number_input("Coût Utilisation (MAD)", min_value=0.0, value=0.0)
            with c2:
                st.markdown("**En Stock**")
                s_nb = st.number_input("Nombre (En stock)", min_value=0, value=0)
                s_et = st.selectbox("État (En stock)", etats_epi)
                s_ec = st.date_input("Échéance (Stock)", date.today() + timedelta(days=730))
                s_ct = st.number_input("Coût Stock (MAD)", min_value=0.0, value=0.0)
                s_loc = st.text_input("Local de stockage", value="Vestiaire / Magasin DPM")
            with c3:
                st.markdown("**Besoins & Observations**")
                b_ach = st.text_input("Besoins Achat", value="Aucun")
                b_mnt = st.text_input("Besoins Maintenance / Certif.", value="Contrôle annuel")
                obs = st.text_area("Observations")

            if st.form_submit_button("➕ Enregistrer l'EPI"):
                c.execute('''INSERT INTO fo29_epis (
                    article, util_nombre, util_etat, util_echeance, util_cout,
                    stock_nombre, stock_etat, stock_echeance, stock_cout, stock_local,
                    besoin_achat, besoin_maintenance, observations
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                    art, u_nb, u_et, str(u_ec), u_ct, s_nb, s_et, str(s_ec), s_ct, s_loc, b_ach, b_mnt, obs
                ))
                conn.commit()
                st.success("EPI enregistré avec succès !")
                st.rerun()

    with tab3:
        df_e = pd.read_sql_query("SELECT * FROM fo29_epis", conn)
        if not df_e.empty:
            id_sel = st.selectbox(
                "Sélectionner l'ID de l'EPI à modifier ou supprimer",
                df_e['id'].tolist(),
                format_func=lambda x: f"ID #{x} — {df_e[df_e['id']==x]['article'].values[0]}"
            )
            row = df_e[df_e['id'] == id_sel].iloc[0]
            with st.form("edit_fo29"):
                u_art = st.text_input("Article EPI", value=str(row['article']))
                c1, c2, c3 = st.columns(3)
                with c1:
                    u_nb = st.number_input("Nombre (En utilisation)", min_value=0, value=int(row['util_nombre']))
                    u_et = st.selectbox("État (Util.)", etats_epi, index=etats_epi.index(row['util_etat']) if row['util_etat'] in etats_epi else 0)
                    u_ec = st.date_input("Échéance (Util.)", value=parse_date_safe(row['util_echeance']))
                    u_ct = st.number_input("Coût Utilisation (MAD)", min_value=0.0, value=float(row['util_cout']))
                with c2:
                    s_nb = st.number_input("Nombre (En stock)", min_value=0, value=int(row['stock_nombre']))
                    s_et = st.selectbox("État (Stock)", etats_epi, index=etats_epi.index(row['stock_etat']) if row['stock_etat'] in etats_epi else 0)
                    s_ec = st.date_input("Échéance (Stock)", value=parse_date_safe(row['stock_echeance']))
                    s_ct = st.number_input("Coût Stock (MAD)", min_value=0.0, value=float(row['stock_cout']))
                    s_loc = st.text_input("Local de stockage", value=str(row['stock_local']))
                with c3:
                    b_ach = st.text_input("Besoins Achat", value=str(row['besoin_achat']))
                    b_mnt = st.text_input("Besoins Maintenance", value=str(row['besoin_maintenance']))
                    obs = st.text_area("Observations", value=str(row['observations']))

                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Enregistrer toutes les modifications"):
                    c.execute('''UPDATE fo29_epis SET
                        article=?, util_nombre=?, util_etat=?, util_echeance=?, util_cout=?,
                        stock_nombre=?, stock_etat=?, stock_echeance=?, stock_cout=?, stock_local=?,
                        besoin_achat=?, besoin_maintenance=?, observations=?
                        WHERE id=?''', (
                        u_art, u_nb, u_et, str(u_ec), u_ct, s_nb, s_et, str(s_ec), s_ct, s_loc, b_ach, b_mnt, obs, id_sel
                    ))
                    conn.commit()
                    st.success("EPI mis à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo29_epis WHERE id=?", (id_sel,))
                    conn.commit()
                    st.warning("EPI supprimé.")
                    st.rerun()
        else:
            st.info("Aucun EPI enregistré.")

# ==============================================================================
# MODULE 7 : CHECKLISTS SPÉCIFICATIONS D'ACHAT & MAINTENANCE (CL_06 & CL_07)
# ==============================================================================
elif menu == "✅ Checklists Achats & Maintenance (CL_06/07)":
    st.subheader("✅ Checklists des Spécifications d'Achat (`DPM_CL_06`) & Recommandations Maintenance/Utilisation (`DPM_CL_07`)")
    tab1, tab2, tab3 = st.tabs(["📋 Fiches Checklists", "➕ Nouvelle Fiche Équipement", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_cl = pd.read_sql_query("SELECT * FROM cl06_07_checklists", conn)
        st.dataframe(df_cl, use_container_width=True)
        if not df_cl.empty:
            st.download_button("📥 Exporter Checklists CL_06 & CL_07 (Excel)", data=to_excel_single(df_cl, "Checklists_CL06_07"), file_name="DPM_CL_06_07_Checklists.xlsx")

    with tab2:
        with st.form("add_cl"):
            tp = st.selectbox("Type de Checklist", ["DPM_CL_06 & DPM_CL_07 (Critique)", "DPM_CL_06 (Spécifications d'Achat)", "DPM_CL_07 (Utilisation & Maintenance)"])
            eq = st.text_input("Équipement / Rubrique Critique")
            spec = st.text_area("Principales Spécifications d'Achat (DPM_CL_06)")
            rec_u = st.text_area("Principales Recommandations d'Utilisation (DPM_CL_07)")
            rec_m = st.text_area("Principales Recommandations de Maintenance (DPM_CL_07)")
            obs = st.text_input("Observations / Références Normatives")
            if st.form_submit_button("➕ Enregistrer la Checklist"):
                c.execute('''INSERT INTO cl06_07_checklists (
                    type_checklist, equipement_rubrique, specifications_achat,
                    recommandations_utilisation, recommandations_maintenance, observations
                ) VALUES (?,?,?,?,?,?)''', (tp, eq, spec, rec_u, rec_m, obs))
                conn.commit()
                st.success("Checklist enregistrée !")
                st.rerun()

    with tab3:
        df_cl = pd.read_sql_query("SELECT * FROM cl06_07_checklists", conn)
        if not df_cl.empty:
            id_sel = st.selectbox(
                "Sélectionner la fiche à modifier ou supprimer",
                df_cl['id'].tolist(),
                format_func=lambda x: f"ID #{x} — {df_cl[df_cl['id']==x]['equipement_rubrique'].values[0]}"
            )
            row = df_cl[df_cl['id'] == id_sel].iloc[0]
            with st.form("edit_cl"):
                tps = ["DPM_CL_06 & DPM_CL_07 (Critique)", "DPM_CL_06 (Spécifications d'Achat)", "DPM_CL_07 (Utilisation & Maintenance)"]
                u_tp = st.selectbox("Type de Checklist", tps, index=tps.index(row['type_checklist']) if row['type_checklist'] in tps else 0)
                u_eq = st.text_input("Équipement / Rubrique", value=str(row['equipement_rubrique']))
                u_spec = st.text_area("Principales Spécifications d'Achat (DPM_CL_06)", value=str(row['specifications_achat']))
                u_rec_u = st.text_area("Principales Recommandations d'Utilisation (DPM_CL_07)", value=str(row['recommandations_utilisation']))
                u_rec_m = st.text_area("Principales Recommandations de Maintenance (DPM_CL_07)", value=str(row['recommandations_maintenance']))
                u_obs = st.text_input("Observations", value=str(row['observations']))

                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Enregistrer toutes les modifications"):
                    c.execute('''UPDATE cl06_07_checklists SET
                        type_checklist=?, equipement_rubrique=?, specifications_achat=?,
                        recommandations_utilisation=?, recommandations_maintenance=?, observations=?
                        WHERE id=?''', (u_tp, u_eq, u_spec, u_rec_u, u_rec_m, u_obs, id_sel))
                    conn.commit()
                    st.success("Checklist mise à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM cl06_07_checklists WHERE id=?", (id_sel,))
                    conn.commit()
                    st.warning("Checklist supprimée.")
                    st.rerun()

# ==============================================================================
# MODULE 8 : FORMULAIRE DE PRÉPARATION DU BUDGET (DPM_FO_30)
# ==============================================================================
elif menu == "💰 Préparation du Budget (DPM_FO_30)":
    st.subheader("💰 Formulaire de Préparation du Budget de La DPM (`DPM_FO_30`)")

    tab1, tab2, tab3 = st.tabs(["📊 Synthèse Budgétaire Officielle (FO_30)", "➕ Ajouter une Ligne Budgétaire", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_b = pd.read_sql_query("SELECT * FROM fo30_budget_lignes", conn)
        if not df_b.empty:
            df_b['Variation Budget (MAD)'] = df_b['cout_estime_n'] - df_b['cout_annee_prec']

            df_conso_b = df_b[df_b['type_ligne'] == 'Consommation (Générale / Pharmacie)']
            df_invest_b = df_b[df_b['type_ligne'] == 'Investissement']

            st.markdown("#### 1. Partie Consommations Générales / Consommations Pharmacie")
            st.dataframe(df_conso_b, use_container_width=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("Besoins Annuels Consommations (N)", f"{df_conso_b['cout_estime_n'].sum():,.2f} MAD")
            c2.metric("Utilisés Année Précédente (N-1)", f"{df_conso_b['cout_annee_prec'].sum():,.2f} MAD")
            c3.metric("Variation Budget Consommations", f"{df_conso_b['Variation Budget (MAD)'].sum():+,.2f} MAD")

            st.markdown("---")
            st.markdown("#### 2. Partie Investissements (Formations / EPIs / Tenue / Peinture / Construction / Vigie / VHF / PCs...)")
            st.dataframe(df_invest_b, use_container_width=True)

            tot_n = df_b['cout_estime_n'].sum()
            tot_prec = df_b['cout_annee_prec'].sum()
            tot_var = tot_n - tot_prec

            st.markdown("---")
            st.markdown("#### 3. Récapitulatif Global (`DPM_FO_30`)")
            k1, k2, k3 = st.columns(3)
            k1.metric("Budget Année Précédente", f"{tot_prec:,.2f} MAD")
            k2.metric("Budget Année en Objet (Total Estimé)", f"{tot_n:,.2f} MAD")
            k3.metric("Variation Globale du Budget", f"{tot_var:+,.2f} MAD")

            st.download_button(
                "📥 Exporter le Formulaire Officiel DPM_FO_30 (Excel)",
                data=to_excel_single(df_b, "DPM_FO_30_Budget"),
                file_name="DPM_FO_30_Preparation_Budget.xlsx"
            )
        else:
            st.info("Aucune ligne budgétaire enregistrée.")

    with tab2:
        with st.form("add_fo30"):
            c1, c2 = st.columns(2)
            with c1:
                tl = st.selectbox("Partie du Budget (`DPM_FO_30`)", ["Investissement", "Consommation (Générale / Pharmacie)"])
                cl = st.selectbox("Classe / Rubrique", [
                    "Radios Portatifs VHF", "EPIs", "Tenue", "Formations", "Vigie",
                    "PCs & Informatique", "Peinture & Infrastructures", "Consommation Générale", "Consommation Pharmacie", "Autre"
                ])
                art = st.text_input("Article ou Intitulé de l'Investissement")
                justif = st.text_area("Justifications (Pour la partie Investissements)")
            with c2:
                pu = st.number_input("Prix Unitaire Estimé (MAD)", min_value=0.0, value=0.0, step=100.0)
                qte_n = st.number_input("Besoins Estimés (Unités)", min_value=0.0, value=1.0, step=1.0)
                qte_prec = st.number_input("Quantité Consommée Année Précédente (Unités)", min_value=0.0, value=0.0)
                cout_prec = st.number_input("Coût Année Précédente (MAD)", min_value=0.0, value=0.0)
                obs = st.text_input("Observations")

            if st.form_submit_button("➕ Enregistrer dans DPM_FO_30"):
                cout_n = pu * qte_n
                c.execute('''INSERT INTO fo30_budget_lignes (
                    type_ligne, classe_rubrique, article_investissement, justification,
                    prix_unitaire_estime, besoin_unites_estime, cout_estime_n,
                    qte_annee_prec, cout_annee_prec, observations
                ) VALUES (?,?,?,?,?,?,?,?,?,?)''', (
                    tl, cl, art, justif, pu, qte_n, cout_n, qte_prec, cout_prec, obs
                ))
                conn.commit()
                st.success(f"Ligne budgétaire ajoutée (Coût calculé : {cout_n:,.2f} MAD) !")
                st.rerun()

    with tab3:
        df_b = pd.read_sql_query("SELECT * FROM fo30_budget_lignes", conn)
        if not df_b.empty:
            id_sel = st.selectbox(
                "Sélectionner la ligne budgétaire à modifier ou supprimer",
                df_b['id'].tolist(),
                format_func=lambda x: f"ID #{x} — [{df_b[df_b['id']==x]['type_ligne'].values[0]}] {df_b[df_b['id']==x]['article_investissement'].values[0]}"
            )
            row = df_b[df_b['id'] == id_sel].iloc[0]
            with st.form("edit_fo30"):
                c1, c2 = st.columns(2)
                tls = ["Investissement", "Consommation (Générale / Pharmacie)"]
                cls_list = [
                    "Radios Portatifs VHF", "EPIs", "Tenue", "Formations", "Vigie",
                    "PCs & Informatique", "Peinture & Infrastructures", "Consommation Générale", "Consommation Pharmacie", "Autre"
                ]
                with c1:
                    u_tl = st.selectbox("Partie du Budget", tls, index=tls.index(row['type_ligne']) if row['type_ligne'] in tls else 0)
                    u_cl = st.selectbox("Classe / Rubrique", cls_list, index=cls_list.index(row['classe_rubrique']) if row['classe_rubrique'] in cls_list else 0)
                    u_art = st.text_input("Article / Investissement", value=str(row['article_investissement']))
                    u_just = st.text_area("Justifications", value=str(row['justification']))
                with c2:
                    u_pu = st.number_input("Prix Unitaire Estimé (MAD)", min_value=0.0, value=float(row['prix_unitaire_estime']))
                    u_qten = st.number_input("Besoins Estimés (Unités)", min_value=0.0, value=float(row['besoin_unites_estime']))
                    u_qteprec = st.number_input("Quantité Année Précédente", min_value=0.0, value=float(row['qte_annee_prec']))
                    u_coutprec = st.number_input("Coût Année Précédente (MAD)", min_value=0.0, value=float(row['cout_annee_prec']))
                    u_obs = st.text_input("Observations", value=str(row['observations']))

                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Enregistrer toutes les modifications"):
                    u_coutn = u_pu * u_qten
                    c.execute('''UPDATE fo30_budget_lignes SET
                        type_ligne=?, classe_rubrique=?, article_investissement=?, justification=?,
                        prix_unitaire_estime=?, besoin_unites_estime=?, cout_estime_n=?,
                        qte_annee_prec=?, cout_annee_prec=?, observations=?
                        WHERE id=?''', (
                        u_tl, u_cl, u_art, u_just, u_pu, u_qten, u_coutn, u_qteprec, u_coutprec, u_obs, id_sel
                    ))
                    conn.commit()
                    st.success("Ligne budgétaire mise à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo30_budget_lignes WHERE id=?", (id_sel,))
                    conn.commit()
                    st.warning("Ligne budgétaire supprimée.")
                    st.rerun()
        else:
            st.info("Aucune ligne budgétaire à modifier.")
