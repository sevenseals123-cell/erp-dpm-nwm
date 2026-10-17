import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

# --- 1. CONFIGURATION ET BASE DE DONNÉES ---
st.set_page_config(page_title="DPM Nador West Med - ERP Ressources Matérielles", layout="wide")

# Initialisation de la connexion SQLite
conn = sqlite3.connect('dpm_rm.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    # Table Equipements (Regroupe VHF, Vigie, Ameublement pour simplifier)
    c.execute('''CREATE TABLE IF NOT EXISTS equipements 
                 (id INTEGER PRIMARY KEY, categorie TEXT, designation TEXT, num_serie TEXT, 
                  date_reception DATE, garantie_mois INTEGER, statut TEXT, affectation TEXT, prix_unitaire REAL)''')
    # Table Consommables (Généraux et Pharmacie)
    c.execute('''CREATE TABLE IF NOT EXISTS consommables 
                 (id INTEGER PRIMARY KEY, type TEXT, article TEXT, quantite_stock INTEGER, prix_unitaire REAL, date_expiration DATE)''')
    # Table Pilotine
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

# --- 3. MODULE : TABLEAU DE BORD (Objectifs DPM_FI_02) ---
if menu == "Tableau de Bord ISPO":
    st.title("Tableau de Bord & Alertes ISPO")
    st.write("Indicateur de Performance : Disponibilité des ressources matérielles critiques (DPM_FI_02).")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Équipements Actifs", "24")
    col2.metric("Alertes Péremption (30j)", "2", delta="-1", delta_color="inverse")
    col3.metric("Anomalies Signalées", "0")
    
    st.subheader("Alertes Critiques (EPI & Pharmacie)")
    st.warning("⚠️ 2 EPI (Gilets de sauvetage) arrivent à expiration dans moins de 30 jours. Renouvellement requis.")

# --- 4. MODULE : GESTION DES ÉQUIPEMENTS (Le cas d'usage VHF) ---
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
            
            submitted = st.form_submit_button("Enregistrer l'équipement")
            if submitted:
                c.execute("INSERT INTO equipements (categorie, designation, num_serie, date_reception, garantie_mois, statut, prix_unitaire) VALUES (?,?,?,?,?,?,?)",
                          (cat, desig, serie, date_rec, garantie, "En stock", prix))
                conn.commit()
                st.success("Équipement ajouté avec succès à la base de données de la DPM !")
                
    st.subheader("Registre Unifié des Équipements")
    df_equip = pd.read_sql_query("SELECT * FROM equipements", conn)
    st.dataframe(df_equip, use_container_width=True)

# --- 5. MODULE : BUDGET (DPM_FO_30) ---
elif menu == "Préparation Budget (FO_30)":
    st.title("Génération du Budget DPM (Formulaire DPM_FO_30)")
    st.write("Ce module consolide automatiquement les achats saisis dans les autres formulaires pour calculer la variation budgétaire.")
    
    df_budget = pd.read_sql_query("SELECT categorie, SUM(prix_unitaire) as Total_Depense FROM equipements GROUP BY categorie", conn)
    
    if not df_budget.empty:
        st.dataframe(df_budget, use_container_width=True)
        total = df_budget['Total_Depense'].sum()
        st.metric("Total des Investissements (MAD)", f"{total:,.2f} MAD")
    else:
        st.info("Aucune donnée financière enregistrée pour le moment.")
