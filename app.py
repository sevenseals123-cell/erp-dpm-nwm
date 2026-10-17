import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

# --- 1. CONFIGURATION ET BASE DE DONNÉES ---
st.set_page_config(page_title="DPM Nador West Med - ERP Ressources Matérielles", layout="wide")

conn = sqlite3.connect('dpm_rm_complet.db', check_same_thread=False)
c = conn.cursor()

def init_db():
    # Remplace FO_23, FO_24, FO_25, VHF, Simulateur, etc.
    c.execute('''CREATE TABLE IF NOT EXISTS equipements_infrastructures 
                 (id INTEGER PRIMARY KEY, 
                  classe TEXT, 
                  article_infrastructure TEXT, 
                  num_serie_localisation TEXT, 
                  etat TEXT, 
                  quantite_en_utilisation INTEGER, 
                  quantite_en_stock INTEGER, 
                  date_reception DATE, 
                  cout_estime REAL, 
                  besoin_achat_repa TEXT, 
                  observations TEXT)''')
                  
    # Remplace FO_26 (Générales) et FO_27 (Pharmacie)
    c.execute('''CREATE TABLE IF NOT EXISTS consommables 
                 (id INTEGER PRIMARY KEY, 
                  classe TEXT, 
                  article TEXT, 
                  emplacement TEXT, 
                  quantite_debut INTEGER, 
                  livre_periode INTEGER, 
                  quantite_fin INTEGER, 
                  prix_unitaire REAL, 
                  date_expiration DATE, 
                  observations TEXT)''')
                  
    # Remplace FO_28 (Pilotine)
    c.execute('''CREATE TABLE IF NOT EXISTS pilotine 
                 (id INTEGER PRIMARY KEY, 
                  date_releve DATE, 
                  gasoil_livre REAL, 
                  lubrifiant_livre REAL, 
                  gasoil_consomme REAL, 
                  lubrifiant_consomme REAL, 
                  observations TEXT)''')
                  
    # Remplace FO_29 (EPIs)
    c.execute('''CREATE TABLE IF NOT EXISTS epis 
                 (id INTEGER PRIMARY KEY, 
                  article TEXT, 
                  nombre_utilisation INTEGER, 
                  etat_utilisation TEXT, 
                  echeance_utilisation DATE, 
                  nombre_stock INTEGER, 
                  etat_stock TEXT, 
                  echeance_stock DATE, 
                  cout REAL, 
                  besoin_local TEXT, 
                  observations TEXT)''')
                  
    conn.commit()

init_db()

# --- 2. BARRE LATÉRALE (NAVIGATION) ---
st.sidebar.title("ERP - DPM Nador West Med")
st.sidebar.write("Pilote Responsable : Omar Dialmy")
menu = st.sidebar.radio("Navigation", [
    "Tableau de Bord ISPO", 
    "Infrastructures, Vigie & Équipements (FO_23, 24, 25)", 
    "Consommables & Pharmacie (FO_26, 27)", 
    "Suivi Pilotine (FO_28)", 
    "Sécurité & EPI (FO_29)",
    "Préparation Budget (FO_30)"
])

# --- 3. MODULE : TABLEAU DE BORD ---
if menu == "Tableau de Bord ISPO":
    st.title("Tableau de Bord & Alertes ISPO")
    
    # Récupération dynamique
    df_epi = pd.read_sql_query("SELECT * FROM epis", conn)
    df_pharma = pd.read_sql_query("SELECT * FROM consommables WHERE classe='Pharmacie'", conn)
    
    aujourd_hui = pd.Timestamp(datetime.today().date())
    limite_30j = aujourd_hui + pd.Timedelta(days=30)
    
    # Alertes EPI
    alertes_epi = 0
    if not df_epi.empty:
        df_epi['echeance_utilisation'] = pd.to_datetime(df_epi['echeance_utilisation'], errors='coerce')
        epi_alerte = df_epi[(df_epi['echeance_utilisation'] <= limite_30j) & (df_epi['echeance_utilisation'] >= aujourd_hui)]
        alertes_epi = len(epi_alerte)
        
    # Alertes Pharmacie
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

# --- 4. MODULE : INFRASTRUCTURES, VIGIE & AMEUBLEMENT (FO_23, 24, 25) ---
elif menu == "Infrastructures, Vigie & Équipements (FO_23, 24, 25)":
    st.title("Infrastructures & Équipements")
    
    with st.form("form_infra"):
        col1, col2 = st.columns(2)
        with col1:
            classe = st.selectbox("Classe", ["Infrastructures (FO_23)", "Ameublement (FO_24)", "Vigie (FO_25)", "VHF", "Simulateur"])
            article = st.text_input("Article / Infrastructure")
            localisation = st.text_input("Emplacement / Numéro de série")
            etat = st.selectbox("État", ["Bon", "Moyen", "À réparer"])
        with col2:
            qte_util = st.number_input("Quantité en utilisation", min_value=0, value=1)
            qte_stock = st.number_input("Quantité en stock", min_value=0, value=0)
            cout = st.number_input("Coût (MAD)", value=0.0)
            besoin = st.text_input("Besoins (Achat / Réparation)")
            obs = st.text_input("Observations")
            
        if st.form_submit_button("Enregistrer"):
            c.execute("INSERT INTO equipements_infrastructures (classe, article_infrastructure, num_serie_localisation, etat, quantite_en_utilisation, quantite_en_stock, cout_estime, besoin_achat_repa, observations) VALUES (?,?,?,?,?,?,?,?,?)",
                      (classe, article, localisation, etat, qte_util, qte_stock, cout, besoin, obs))
            conn.commit()
            st.success("Enregistrement validé !")
            
    df_infra = pd.read_sql_query("SELECT * FROM equipements_infrastructures", conn)
    st.dataframe(df_infra, use_container_width=True)

# --- 5. MODULE : CONSOMMABLES & PHARMACIE (FO_26, 27) ---
elif menu == "Consommables & Pharmacie (FO_26, 27)":
    st.title("Consommables & Pharmacie")
    
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

# --- 6. MODULE : SUIVI PILOTINE (FO_28) ---
elif menu == "Suivi Pilotine (FO_28)":
    st.title("Registre de la Pilotine")
    
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

# --- 7. MODULE : SÉCURITÉ & EPI (FO_29) ---
elif menu == "Sécurité & EPI (FO_29)":
    st.title("Registre des EPIs")
    
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

# --- 8. MODULE : BUDGET (FO_30) ---
elif menu == "Préparation Budget (FO_30)":
    st.title("Préparation du Budget")
    st.write("Consolidation des coûts de toutes les classes.")
    
    df_b_infra = pd.read_sql_query("SELECT classe, SUM(cout_estime) as Investissements FROM equipements_infrastructures GROUP BY classe", conn)
    df_b_epi = pd.read_sql_query("SELECT 'EPIs' as classe, SUM(cout) as Investissements FROM epis", conn)
    
    df_budget_total = pd.concat([df_b_infra, df_b_epi])
    st.dataframe(df_budget_total, use_container_width=True)
    st.metric("Total Investissements (MAD)", df_budget_total['Investissements'].sum())
