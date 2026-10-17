import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

# --- 1. CONFIGURATION ET BASE DE DONNÉES ---
st.set_page_config(page_title="DPM Nador West Med - ERP Ressources Matérielles", layout="wide")

conn = sqlite3.connect('dpm_rm.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    c.execute('''CREATE TABLE IF NOT EXISTS equipements 
                 (id INTEGER PRIMARY KEY, categorie TEXT, designation TEXT, num_serie TEXT, 
                  date_reception DATE, garantie_mois INTEGER, statut TEXT, affectation TEXT, prix_unitaire REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS consommables 
                 (id INTEGER PRIMARY KEY, type TEXT, article TEXT, quantite_stock INTEGER, prix_unitaire REAL, date_expiration DATE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pilotine 
                 (id INTEGER PRIMARY KEY, date_saisie DATE, gasoil_litre REAL, lubrifiant_litre REAL)''')
    conn.commit()

init_db()

# --- 2. BARRE LATÉRALE (NAVIGATION) ---
st.sidebar.title("ERP - DPM Nador West Med")
st.sidebar.write("Pilote Responsable : Omar Dialmy")
menu = st.sidebar.radio("Navigation", [
    "Tableau de Bord ISPO", 
    "Gestion des Équipements", 
    "Sécurité & EPI", 
    "Suivi Pilotine", 
    "Préparation Budget (FO_30)"
])

# --- 3. MODULE : TABLEAU DE BORD (DPM_FI_02) ---
if menu == "Tableau de Bord ISPO":
    st.title("Tableau de Bord & Alertes ISPO")
    st.write("Indicateur de Performance : Disponibilité des ressources matérielles critiques (DPM_FI_02).")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Équipements Actifs", "24")
    col2.metric("Alertes Péremption (30j)", "2", delta="-1", delta_color="inverse")
    col3.metric("Anomalies Signalées", "0")
    
    st.subheader("Alertes Critiques (EPI & Pharmacie)")
    st.warning("⚠️ 2 EPI (Gilets de sauvetage) arrivent à expiration dans moins de 30 jours. Renouvellement requis.")

# --- 4. MODULE : GESTION DES ÉQUIPEMENTS (VHF, etc.) ---
elif menu == "Gestion des Équipements":
    st.title("Gestion des Équipements (Remplace FO_24, FO_25)")
    with st.expander("➕ Ajouter une nouvelle réception (ex: VHF SOREMAR)"):
        with st.form("form_equip"):
            cat = st.selectbox("Catégorie", ["Radios VHF", "Ameublement", "Vigie", "PPUs", "Simulateur"])
            desig = st.text_input("Désignation", value="Motorola DP4801 ATEX")
            serie = st.text_input("Numéro de Série")
            date_rec = st.date_input("Date de réception", datetime(2026, 10, 15))
            garantie = st.number_input("Garantie (en mois)", value=24)
            prix = st.number_input("Prix Unitaire HT (MAD)", value=15800.00)
            
            if st.form_submit_button("Enregistrer l'équipement"):
                c.execute("INSERT INTO equipements (categorie, designation, num_serie, date_reception, garantie_mois, statut, prix_unitaire) VALUES (?,?,?,?,?,?,?)",
                          (cat, desig, serie, date_rec, garantie, "En stock", prix))
                conn.commit()
                st.success("Équipement ajouté avec succès !")
                
    st.subheader("Registre Unifié des Équipements")
    df_equip = pd.read_sql_query("SELECT * FROM equipements", conn)
    st.dataframe(df_equip, use_container_width=True)

# --- 5. MODULE : SÉCURITÉ & EPI (DPM_FO_29) ---
elif menu == "Sécurité & EPI":
    st.title("Registre des EPIs (Remplace FO_29)")
    with st.expander("➕ Ajouter / Renouveler un EPI"):
        with st.form("form_epi"):
            article = st.text_input("Article (ex: Gilet de sauvetage 275N, Casque, Ligne de vie)")
            nombre = st.number_input("Quantité", min_value=1, value=1)
            etat = st.selectbox("État", ["Neuf", "Bon", "À remplacer"])
            echeance = st.date_input("Date d'échéance", datetime.today() + timedelta(days=365))
            cout = st.number_input("Coût total (MAD)", value=0.0)
            
            if st.form_submit_button("Enregistrer l'EPI"):
                c.execute("INSERT INTO consommables (type, article, quantite_stock, prix_unitaire, date_expiration) VALUES (?,?,?,?,?)",
                          ("EPI", article, nombre, cout, echeance))
                conn.commit()
                st.success("EPI enregistré dans le système !")

    st.subheader("État du parc EPI")
    df_epi = pd.read_sql_query("SELECT article, quantite_stock as Nombre, prix_unitaire as Cout, date_expiration as Echeance FROM consommables WHERE type='EPI'", conn)
    st.dataframe(df_epi, use_container_width=True)

# --- 6. MODULE : SUIVI PILOTINE (DPM_FO_28) ---
elif menu == "Suivi Pilotine":
    st.title("Consommation Pilotine (Remplace FO_28)")
    with st.expander("➕ Saisir un relevé de consommation"):
        with st.form("form_pilotine"):
            date_saisie = st.date_input("Date du relevé", datetime.today())
            gasoil = st.number_input("Gasoil livré/consommé (Litres)", min_value=0.0, value=0.0)
            lubrifiant = st.number_input("Lubrifiant livré/consommé (Litres)", min_value=0.0, value=0.0)
            
            if st.form_submit_button("Valider le relevé"):
                c.execute("INSERT INTO pilotine (date_saisie, gasoil_litre, lubrifiant_litre) VALUES (?,?,?)",
                          (date_saisie, gasoil, lubrifiant))
                conn.commit()
                st.success("Relevé de consommation enregistré !")

    st.subheader("Historique des Consommations")
    df_pil = pd.read_sql_query("SELECT date_saisie as Date, gasoil_litre as Gasoil, lubrifiant_litre as Lubrifiant FROM pilotine", conn)
    if not df_pil.empty:
        st.dataframe(df_pil, use_container_width=True)
        col1, col2 = st.columns(2)
        col1.metric("Consommation Totale Gasoil (L)", f"{df_pil['Gasoil'].sum():.2f}")
        col2.metric("Consommation Totale Lubrifiant (L)", f"{df_pil['Lubrifiant'].sum():.2f}")
    else:
        st.info("Aucun relevé pour le moment.")

# --- 7. MODULE : BUDGET (DPM_FO_30) ---
elif menu == "Préparation Budget (FO_30)":
    st.title("Génération du Budget DPM (Formulaire FO_30)")
    df_budget = pd.read_sql_query("SELECT categorie, SUM(prix_unitaire) as Total_Depense FROM equipements GROUP BY categorie", conn)
    
    if not df_budget.empty:
        st.dataframe(df_budget, use_container_width=True)
        total = df_budget['Total_Depense'].sum()
        st.metric("Total des Investissements (MAD)", f"{total:,.2f} MAD")
    else:
        st.info("Aucune donnée financière enregistrée pour le moment.")
