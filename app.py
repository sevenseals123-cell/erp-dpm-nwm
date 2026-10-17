import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import plotly.express as px
from io import BytesIO

# --- 1. CONFIGURATION ET BASE DE DONNÉES ---
st.set_page_config(page_title="DPM Nador West Med - ERP Ressources Matérielles", layout="wide")

conn = sqlite3.connect('dpm_rm_complet.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS equipements_infrastructures 
                 (id INTEGER PRIMARY KEY, classe TEXT, article_infrastructure TEXT, 
                  num_serie_localisation TEXT, etat TEXT, quantite_en_utilisation INTEGER, 
                  quantite_en_stock INTEGER, date_reception DATE, cout_estime REAL, 
                  besoin_achat_repa TEXT, observations TEXT)''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS consommables 
                 (id INTEGER PRIMARY KEY, classe TEXT, article TEXT, emplacement TEXT, 
                  quantite_debut INTEGER, livre_periode INTEGER, quantite_fin INTEGER, 
                  prix_unitaire REAL, date_expiration DATE, observations TEXT)''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS pilotine 
                 (id INTEGER PRIMARY KEY, date_releve DATE, gasoil_livre REAL, 
                  lubrifiant_livre REAL, gasoil_consomme REAL, lubrifiant_consomme REAL, 
                  observations TEXT)''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS epis 
                 (id INTEGER PRIMARY KEY, article TEXT, nombre_utilisation INTEGER, 
                  etat_utilisation TEXT, echeance_utilisation DATE, nombre_stock INTEGER, 
                  etat_stock TEXT, echeance_stock DATE, cout REAL, besoin_local TEXT, 
                  observations TEXT)''')
    conn.commit()

init_db()

# --- FONCTION D'EXPORT EXCEL ---
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

# --- 2. BARRE LATÉRALE (NAVIGATION) ---
st.sidebar.title("ERP - DPM Nador West Med")
st.sidebar.write("Pilote Responsable : Omar Dialmy")
menu = st.sidebar.radio("Navigation", [
    "Tableau de Bord ISPO", 
    "Infrastructures, Vigie & Équipements", 
    "Consommables & Pharmacie", 
    "Suivi Pilotine", 
    "Sécurité & EPI",
    "Préparation Budget (FO_30)"
])

# --- 3. MODULE : TABLEAU DE BORD (AVEC GRAPHIQUES) ---
if menu == "Tableau de Bord ISPO":
    st.title("Tableau de Bord & Alertes ISPO")
    
    # KPIs Alertes
    df_epi = pd.read_sql_query("SELECT * FROM epis", conn)
    df_pharma = pd.read_sql_query("SELECT * FROM consommables WHERE classe='Pharmacie'", conn)
    
    aujourd_hui = pd.Timestamp(datetime.today().date())
    limite_30j = aujourd_hui + pd.Timedelta(days=30)
    
    alertes_epi = 0
    if not df_epi.empty:
        df_epi['echeance_utilisation'] = pd.to_datetime(df_epi['echeance_utilisation'], errors='coerce')
        epi_alerte = df_epi[(df_epi['echeance_utilisation'] <= limite_30j) & (df_epi['echeance_utilisation'] >= aujourd_hui)]
        alertes_epi = len(epi_alerte)
        
    alertes_pharma = 0
    if not df_pharma.empty:
        df_pharma['date_expiration'] = pd.to_datetime(df_pharma['date_expiration'], errors='coerce')
        pharma_alerte = df_pharma[(df_pharma['date_expiration'] <= limite_30j) & (df_pharma['date_expiration'] >= aujourd_hui)]
        alertes_pharma = len(pharma_alerte)

    col1, col2, col3 = st.columns(3)
    col1.metric("Alertes EPI (30j)", alertes_epi, delta_color="inverse" if alertes_epi > 0 else "normal")
    col2.metric("Alertes Pharmacie (30j)", alertes_pharma, delta_color="inverse" if alertes_pharma > 0 else "normal")
    
    if alertes_epi > 0 or alertes_pharma > 0:
        st.error(f"⚠️ {alertes_epi + alertes_pharma} article(s) arrivent à expiration.")
    else:
        st.success("✅ Aucun équipement critique n'arrive à expiration prochainement.")

    # Data Visualisation
    st.markdown("---")
    st.subheader("Analyse Visuelle (Données ISPO)")
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.write("**Répartition Budgétaire par Classe**")
        df_b_infra = pd.read_sql_query("SELECT classe, SUM(cout_estime) as Cout FROM equipements_infrastructures GROUP BY classe", conn)
        df_b_epi = pd.read_sql_query("SELECT 'EPIs' as classe, SUM(cout) as Cout FROM epis", conn)
        df_chart_budget = pd.concat([df_b_infra, df_b_epi])
        if not df_chart_budget.empty and df_chart_budget['Cout'].sum() > 0:
            fig1 = px.pie(df_chart_budget, values='Cout', names='classe', hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("Données budgétaires insuffisantes pour le graphique.")

    with col_chart2:
        st.write("**Évolution de la Consommation Pilotine**")
        df_chart_pil = pd.read_sql_query("SELECT date_releve, gasoil_consomme FROM pilotine ORDER BY date_releve", conn)
        if not df_chart_pil.empty:
            fig2 = px.line(df_chart_pil, x='date_releve', y='gasoil_consomme', markers=True, title="Gasoil (L)")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Aucun relevé de pilotine.")

# --- 4. MODULE : INFRASTRUCTURES, VIGIE & AMEUBLEMENT ---
elif menu == "Infrastructures, Vigie & Équipements":
    st.title("Infrastructures & Équipements (FO_23, 24, 25)")
    
    with st.form("form_infra"):
        col1, col2 = st.columns(2)
        with col1:
            classe = st.selectbox("Classe", ["Infrastructures (FO_23)", "Ameublement (FO_24)", "Vigie (FO_25)", "VHF", "Simulateur"])
            article = st.text_input("Article / Infrastructure")
            localisation = st.text_input("Emplacement / Numéro de série")
            etat = st.selectbox("État", ["Bon", "Moyen", "À réparer"])
        with col2:
            date_rec = st.date_input("Date (Réception/Inspection)")
            qte_util = st.number_input("Quantité en utilisation", min_value=0, value=1)
            qte_stock = st.number_input("Quantité en stock", min_value=0, value=0)
            cout = st.number_input("Coût (MAD)", value=0.0)
            besoin = st.text_input("Besoins (Achat / Réparation)")
            obs = st.text_input("Observations")
            
        if st.form_submit_button("Enregistrer"):
            c.execute("INSERT INTO equipements_infrastructures (classe, article_infrastructure, num_serie_localisation, etat, quantite_en_utilisation, quantite_en_stock, date_reception, cout_estime, besoin_achat_repa, observations) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (classe, article, localisation, etat, qte_util, qte_stock, date_rec, cout, besoin, obs))
            conn.commit()
            st.success("Enregistrement validé !")
            
    df_infra = pd.read_sql_query("SELECT * FROM equipements_infrastructures", conn)
    st.dataframe(df_infra, use_container_width=True)
    
    if not df_infra.empty:
        excel_data = to_excel(df_infra)
        st.download_button(label="📥 Exporter vers Excel (Archivage ISPO)", data=excel_data, file_name='Registre_Equipements.xlsx', mime='application/vnd.ms-excel')

# --- 5. MODULE : CONSOMMABLES & PHARMACIE ---
elif menu == "Consommables & Pharmacie":
    st.title("Consommables & Pharmacie (FO_26, 27)")
    
    with st.form("form_conso"):
        classe = st.selectbox("Type", ["Générales (FO_26)", "Pharmacie (FO_27)"])
        article = st.text_input("Article")
        col1, col2, col3 = st.columns(3)
        with col1:
            q_debut = st.number_input("Existant Début", min_value=0, value=0)
        with col2:
            q_livre = st.number_input("Livré", min_value=0, value=0)
        with col3:
            q_fin = st.number_input("Existant Fin", min_value=0, value=0)
            
        prix_u = st.number_input("Prix Unitaire (MAD)", value=0.0)
        date_exp = st.date_input("Date Expiration (Si Pharmacie)", datetime.today())
        
        if st.form_submit_button("Enregistrer"):
            c.execute("INSERT INTO consommables (classe, article, quantite_debut, livre_periode, quantite_fin, prix_unitaire, date_expiration) VALUES (?,?,?,?,?,?,?)",
                      (classe, article, q_debut, q_livre, q_fin, prix_u, date_exp))
            conn.commit()
            st.success("Consommable enregistré !")

    df_conso = pd.read_sql_query("SELECT article, quantite_debut, livre_periode, quantite_fin, (quantite_debut + livre_periode - quantite_fin) as Consommé, ((quantite_debut + livre_periode - quantite_fin) * prix_unitaire) as Cout_Total FROM consommables", conn)
    st.dataframe(df_conso, use_container_width=True)
    
    if not df_conso.empty:
        excel_data = to_excel(df_conso)
        st.download_button(label="📥 Exporter vers Excel", data=excel_data, file_name='Etat_Consommables.xlsx', mime='application/vnd.ms-excel')

# --- 6. MODULE : SUIVI PILOTINE ---
elif menu == "Suivi Pilotine":
    st.title("Registre de la Pilotine (FO_28)")
    
    with st.form("form_pilotine"):
        date_p = st.date_input("Date")
        col1, col2 = st.columns(2)
        with col1:
            g_livre = st.number_input("Gasoil Livré (L)", value=0.0)
            g_cons = st.number_input("Gasoil Consommé (L)", value=0.0)
        with col2:
            l_livre = st.number_input("Lubrifiant Livré (L)", value=0.0)
            l_cons = st.number_input("Lubrifiant Consommé (L)", value=0.0)
            
        if st.form_submit_button("Enregistrer"):
            c.execute("INSERT INTO pilotine (date_releve, gasoil_livre, gasoil_consomme, lubrifiant_livre, lubrifiant_consomme) VALUES (?,?,?,?,?)",
                      (date_p, g_livre, g_cons, l_livre, l_cons))
            conn.commit()
            st.success("Relevé Pilotine enregistré !")
            
    df_pil = pd.read_sql_query("SELECT * FROM pilotine", conn)
    st.dataframe(df_pil, use_container_width=True)
    
    if not df_pil.empty:
        excel_data = to_excel(df_pil)
        st.download_button(label="📥 Exporter vers Excel", data=excel_data, file_name='Suivi_Pilotine.xlsx', mime='application/vnd.ms-excel')

# --- 7. MODULE : SÉCURITÉ & EPI ---
elif menu == "Sécurité & EPI":
    st.title("Registre des EPIs (FO_29)")
    
    with st.form("form_epi"):
        article = st.text_input("Article (EPI)")
        col1, col2 = st.columns(2)
        with col1:
            st.write("En Utilisation")
            n_util = st.number_input("Nombre (Util)", min_value=0, value=0)
            d_util = st.date_input("Échéance (Util)")
        with col2:
            st.write("En Stock")
            n_stock = st.number_input("Nombre (Stock)", min_value=0, value=0)
            d_stock = st.date_input("Échéance (Stock)")
            
        cout = st.number_input("Coût (MAD)", value=0.0)
        
        if st.form_submit_button("Enregistrer"):
            c.execute("INSERT INTO epis (article, nombre_utilisation, echeance_utilisation, nombre_stock, echeance_stock, cout) VALUES (?,?,?,?,?,?)",
                      (article, n_util, d_util, n_stock, d_stock, cout))
            conn.commit()
            st.success("EPI enregistré !")
            
    df_epi_show = pd.read_sql_query("SELECT article, nombre_utilisation, echeance_utilisation, nombre_stock, echeance_stock, cout FROM epis", conn)
    st.dataframe(df_epi_show, use_container_width=True)
    
    if not df_epi_show.empty:
        excel_data = to_excel(df_epi_show)
        st.download_button(label="📥 Exporter vers Excel", data=excel_data, file_name='Registre_EPI.xlsx', mime='application/vnd.ms-excel')

# --- 8. MODULE : BUDGET ---
elif menu == "Préparation Budget (FO_30)":
    st.title("Préparation du Budget (FO_30)")
    st.write("Consolidation des coûts de toutes les classes.")
    
    df_b_infra = pd.read_sql_query("SELECT classe, SUM(cout_estime) as Investissements FROM equipements_infrastructures GROUP BY classe", conn)
    df_b_epi = pd.read_sql_query("SELECT 'EPIs' as classe, SUM(cout) as Investissements FROM epis", conn)
    
    df_budget_total = pd.concat([df_b_infra, df_b_epi])
    st.dataframe(df_budget_total, use_container_width=True)
    st.metric("Total Investissements (MAD)", df_budget_total['Investissements'].sum())
    
    if not df_budget_total.empty:
        excel_data = to_excel(df_budget_total)
        st.download_button(label="📥 Exporter le Budget (Excel)", data=excel_data, file_name='Budget_FO30.xlsx', mime='application/vnd.ms-excel')
