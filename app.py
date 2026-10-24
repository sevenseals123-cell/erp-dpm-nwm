import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import base64
import os

# ==============================================================================
# 1. CONFIGURATION DE LA PAGE & GESTION DU LOGO OFFICIEL NADOR WEST MED
# ==============================================================================
st.set_page_config(
    page_title="DPM Nador West Med | Maritime Command & ERP ISPO",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOGO_FILE = "logo.png"
DB_FILE = "dpm_nwm_ispo_v4_pro.db"

def generate_nwm_logo_png_bytes():
    """Charge le logo officiel Nador West Med ou le génère en haute résolution."""
    for candidate in ["logo.png", "image_315546.png", "nwm_logo.png"]:
        if os.path.exists(candidate):
            try:
                with open(candidate, "rb") as f:
                    return f.read()
            except Exception:
                pass

    w, h = 440, 210
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Arc orbital externe bleu marine (#1B3668)
    draw.arc([14, 10, 195, 191], start=115, end=330, fill=(27, 54, 104, 255), width=6)

    # Sphère maritime Nador West Med
    globe_box = [32, 28, 168, 164]
    draw.pieslice(globe_box, start=180, end=295, fill=(43, 108, 176, 255))
    draw.pieslice(globe_box, start=295, end=360, fill=(30, 78, 140, 255))
    draw.pieslice(globe_box, start=0, end=180, fill=(0, 163, 180, 255))

    # Méridiens blancs croisés
    draw.arc([20, 48, 190, 195], start=195, end=340, fill=(255, 255, 255, 255), width=5)
    draw.arc([58, -10, 195, 180], start=115, end=235, fill=(255, 255, 255, 255), width=5)

    try:
        font_nador = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
        font_west = ImageFont.truetype("DejaVuSans-Bold.ttf", 31)
    except Exception:
        font_nador = ImageFont.load_default()
        font_west = ImageFont.load_default()

    draw.text((118, 118), "NADOR", fill=(0, 151, 167, 255), font=font_nador)
    draw.text((118, 162), "WEST MED", fill=(27, 54, 104, 255), font=font_west)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def get_logo_base64():
    return base64.b64encode(generate_nwm_logo_png_bytes()).decode("utf-8")

# ==============================================================================
# 2. DESIGN SYSTEM EXÉCUTIF "MARITIME COMMAND CENTER" (CSS AVANCÉ)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2.5rem;
        max-width: 98%;
    }

    /* Barre d'état supérieure Command Center */
    .top-status-bar {
        background: #061428;
        color: #94a3b8;
        padding: 0.45rem 1.2rem;
        border-radius: 8px 8px 0 0;
        font-size: 0.78rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(0, 163, 180, 0.3);
    }
    .status-dot {
        height: 8px; width: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
        box-shadow: 0 0 8px #10b981;
    }

    /* Bannière Héro Nador West Med */
    .nwm-hero {
        background: linear-gradient(125deg, #091e3a 0%, #0f3156 50%, #006d77 100%);
        color: #ffffff;
        padding: 1.35rem 1.8rem;
        border-radius: 0 0 14px 14px;
        border-left: 6px solid #00b4d8;
        box-shadow: 0 10px 25px -5px rgba(9, 30, 58, 0.25);
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .nwm-hero-left { display: flex; align-items: center; gap: 1.4rem; }
    .nwm-logo-card {
        background: #ffffff;
        padding: 0.5rem 0.85rem;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
    }
    .nwm-hero h1 {
        color: #ffffff;
        font-size: 1.55rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.3px;
    }
    .nwm-hero p {
        color: #bae6fd;
        font-size: 0.88rem;
        margin: 0.3rem 0 0 0;
        font-weight: 500;
    }
    .nwm-pill-box {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        padding: 0.6rem 1.1rem;
        border-radius: 10px;
        text-align: right;
    }
    .nwm-pill-title { font-size: 0.72rem; text-transform: uppercase; color: #7dd3fc; letter-spacing: 0.8px; font-weight: 700; }
    .nwm-pill-val { font-size: 0.95rem; font-weight: 700; color: #ffffff; }

    /* Cartes KPI Exécutives */
    .exec-card {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 12px;
        padding: 1.2rem 1.3rem;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #0f3156;
        box-shadow: 0 4px 12px rgba(15, 49, 86, 0.05);
        transition: all 0.2s ease-in-out;
        margin-bottom: 0.8rem;
    }
    .exec-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(15, 49, 86, 0.1);
    }
    .exec-card.teal { border-left-color: #0097a7; }
    .exec-card.gold { border-left-color: #d4af37; }
    .exec-card.danger { border-left-color: #ef4444; background: linear-gradient(180deg, #fff5f5 0%, #ffffff 100%); }
    .exec-card.success { border-left-color: #10b981; }

    .exec-label {
        font-size: 0.76rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        display: flex;
        justify-content: space-between;
    }
    .exec-val {
        font-size: 1.7rem;
        font-weight: 800;
        color: #091e3a;
        margin: 0.35rem 0 0.25rem 0;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .exec-footer {
        font-size: 0.78rem;
        color: #475569;
        font-weight: 500;
    }
    .progress-bar-bg {
        width: 100%; height: 6px; background: #e2e8f0; border-radius: 4px; margin-top: 8px; overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%; border-radius: 4px;
    }

    /* En-tête de module */
    .module-banner {
        background: linear-gradient(90deg, #f0f9ff 0%, #ffffff 100%);
        border: 1px solid #bae6fd;
        border-left: 6px solid #0284c7;
        padding: 0.85rem 1.25rem;
        border-radius: 10px;
        margin-bottom: 1.2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .module-banner h3 { margin: 0; font-size: 1.15rem; color: #091e3a; font-weight: 800; }
    .module-banner span { font-size: 0.82rem; color: #0369a1; font-weight: 600; background: #e0f2fe; padding: 4px 10px; border-radius: 6px; }

    /* Carte Inspecteur d'Équipement */
    .asset-id-card {
        background: linear-gradient(135deg, #091e3a 0%, #163a66 100%);
        color: white;
        padding: 1.3rem;
        border-radius: 12px;
        border: 1px solid #2b6cb0;
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
    }
    .mono-badge {
        font-family: 'JetBrains Mono', monospace;
        background: rgba(0, 180, 216, 0.2);
        border: 1px solid #00b4d8;
        color: #90e0ef;
        padding: 2px 8px;
        border-radius: 5px;
        font-size: 0.82rem;
    }

    /* Pied de page */
    .nwm-footer {
        margin-top: 3rem;
        padding: 1.1rem;
        background: #091e3a;
        color: #cbd5e1;
        text-align: center;
        font-size: 0.8rem;
        border-radius: 10px;
        border-top: 3px solid #0097a7;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. BASE DE DONNÉES SQLITE, JOURNAL D'AUDIT & PRÉ-CHARGEMENT COMPLET NWM
# ==============================================================================
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

def init_db():
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

    c.execute('''CREATE TABLE IF NOT EXISTS cl06_07_checklists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_checklist TEXT,
        equipement_rubrique TEXT,
        specifications_achat TEXT,
        recommandations_utilisation TEXT,
        recommandations_maintenance TEXT,
        observations TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        horodatage TEXT,
        utilisateur TEXT,
        module TEXT,
        action TEXT,
        details TEXT
    )''')
    conn.commit()

def log_audit(module, action, details):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute(
        "INSERT INTO audit_logs (horodatage, utilisateur, module, action, details) VALUES (?,?,?,?,?)",
        (now_str, "Pilote Omar Dialmy (RM)", module, action, details)
    )
    conn.commit()

def seed_initial_data():
    """Pré-charge l'ensemble des registres avec les données réelles VHF et un jeu réaliste NWM."""
    # 1. Équipements FO_24 / FO_25 / VHF
    c.execute("SELECT COUNT(*) FROM fo24_25_equipements")
    if c.fetchone()[0] == 0:
        serials_vhf = [
            "627RBX0048", "627RBX0057", "627RBX0067", "627RBX0104", "627TUT2578",
            "627RBX0029", "627RBX0033", "627RBX0035", "627RBX0039", "627RBX0045"
        ]
        for idx, sn in enumerate(serials_vhf, start=1):
            c.execute('''INSERT INTO fo24_25_equipements (
                classe, article, reference_serie, cout_estime,
                util_etat, util_quantite, util_emplacement,
                stock_quantite, stock_localisation,
                besoin_achat, besoin_reparation,
                date_reception, echeance_garantie, observations
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
                "Radios Portatifs VHF",
                f"Radio VHF Marine ATEX Motorola DP4801 Ex #{idx:02d} (S/N: {sn})",
                sn, 15800.00, "Bon", 1, "Station de Pilotage / Vigie",
                0, "Magasin DPM", "Non", "Non", "2026-10-15", "2028-10-15",
                "BC N°20260014 | BL-CAS2610/0453 | Facture F-RAD26/0024 SOREMAR | PV Réception du 15/10/2026 (Garantie 2 ans)"
            ))

        c.execute('''INSERT INTO fo24_25_equipements (
            classe, article, reference_serie, cout_estime,
            util_etat, util_quantite, util_emplacement,
            stock_quantite, stock_localisation,
            besoin_achat, besoin_reparation,
            date_reception, echeance_garantie, observations
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            "Radios Portatifs VHF",
            "Batteries de rechange ATEX DP4401 (Lot de 15 unités)",
            "Code C0113530", 57750.00, "Bon", 10, "En service sur VHF",
            5, "Armoire de charge Vigie", "Non", "Non", "2026-10-15", "2028-10-15",
            "BC N°20260014 | Facture F-RAD26/0024 SOREMAR (PU HT : 3 850,00 MAD)"
        ))

        c.execute('''INSERT INTO fo24_25_equipements (
            classe, article, reference_serie, cout_estime,
            util_etat, util_quantite, util_emplacement,
            stock_quantite, stock_localisation,
            besoin_achat, besoin_reparation,
            date_reception, echeance_garantie, observations
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            "Radios Portatifs VHF",
            "Accessoires VHF : 10 Housses FUNDA DURA + 10 Modules Motorola IMPRES ATEX Noise Can",
            "C0126461 / C0326460", 0.00, "Bon", 10, "Station de Pilotage",
            0, "Magasin DPM", "Non", "Non", "2026-10-15", "2028-10-15",
            "Inclus sans surcoût dans BC N°20260014 / BL-CAS2610/0453"
        ))

        # Dotation Vigie (FO_25) & Ameublement (FO_24) pour alimenter les exports et graphiques
         vigie_items = [
            ("Équipements de la Vigie (DPM_FO_25)", "Station de Base VHF Marine Fixe ICOM IC-M605 + Antennes", "VIG-VHF-01", 28500.00, "Bon", 2, "Console Vigie NWM", 0, "Local Technique", "Non", "Non", "2026-02-10", "2028-02-10", "Veille permanente Canal 16 / Canal 12 Pilotage"),
            ("Équipements de la Vigie (DPM_FO_25)", "Récepteur AIS Classe A & Écran de Supervision Trafic VTS/DPM", "VIG-AIS-01", 42000.00, "Bon", 1, "Vigie Pilotage", 0, "-", "Non", "Non", "2026-02-15", "2028-02-15", "Suivi temps réel approches Nador West Med"),
            ("Équipements de la Vigie (DPM_FO_25)", "Jumelles Marines Stabilisées Fujinon 14x40 Techno-Stabi", "VIG-OPT-02", 14500.00, "Bon", 2, "Passerelle Vigie", 1, "Armoire Optique", "Non", "Non", "2026-03-01", "2028-03-01", "Observation visuelle chenal et digue"),
            ("Équipements d'Ameublement (DPM_FO_24)", "Postes Opérateurs Ergonomiques 24/7 & Fauteuils de Quart", "AMB-VIG-01", 34000.00, "Bon", 4, "Vigie & Bureau Pilotes", 0, "-", "Non", "Non", "2026-01-20", "2028-01-20", "Mobilier technique haute résistance"),
            ("Équipements d'Ameublement (DPM_FO_24)", "Armoires Fortes Ignifuges Archives ISPO & Vestiaires Pilotes", "AMB-LOC-04", 19500.00, "Bon", 6, "Locaux DPM", 0, "-", "Non", "Non", "2026-01-25", "2028-01-25", "Conformité classement documentaire ISPO")
        ]
        for item in vigie_items:
            c.execute('''INSERT INTO fo24_25_equipements (
                classe, article, reference_serie, cout_estime,
                util_etat, util_quantite, util_emplacement,
                stock_quantite, stock_localisation,
                besoin_achat, besoin_reparation,
                date_reception, echeance_garantie, observations
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', item)

    # 2. Infrastructures (FO_23)
    c.execute("SELECT COUNT(*) FROM fo23_infrastructures")
    if c.fetchone()[0] == 0:
        infras = [
            ("Station de Pilotage & Passerelle Vigie NWM", "Vérification étanchéité terrasse et climatisation salle serveurs", "Entretien préventif climatisation et joints menuiserie aluminium", 4500.00, "Normal", "2026-10-01", "Infrastructure conforme aux exigences ISPO"),
            ("Appontement & Poste d'Amarrage Pilotines", "Contrôle des défenses d'accostage et échelles de quai", "Remplacement de 2 chaînes d'amarrage et peinture bollards", 6800.00, "Normal", "2026-10-10", "Inspection mensuelle sécurité embarquement")
        ]
        for inf in infras:
            c.execute('''INSERT INTO fo23_infrastructures (
                infrastructure, besoins_reparation, reparations_commentaire,
                reparations_cout, criticite, date_mise_a_jour, observations
            ) VALUES (?,?,?,?,?,?,?)''', inf)

    # 3. Consommables & Pharmacie (FO_26 & FO_27)
    c.execute("SELECT COUNT(*) FROM fo26_27_consommables")
    if c.fetchone()[0] == 0:
        consos = [
            ("Consommations Générales (FO_26)", "Rames Papier A4 80g & Registres Journal de Vigie", "Bureau DPM / Vigie", 25, 48.0, "2028-12-31", 20, 48.0, 30, 48.0, "2028-12-31", "Impression des bons de pilotage et rapports ISPO"),
            ("Consommations Générales (FO_26)", "Cartouches Toner Laser Haute Capacité Imprimantes Vigie", "Magasin DPM", 4, 850.0, "2028-12-31", 4, 850.0, 5, 850.0, "2028-12-31", "Stock de sécurité maintenu à 5 unités"),
            ("Pharmacie (FO_27)", "Trousse de Secours Maritime Réglementaire SOLAS (Pilotine & Vigie)", "Infirmerie DPM / Pilotine", 4, 1450.0, "2027-09-30", 2, 1450.0, 5, 1450.0, "2027-09-30", "Inspection trimestrielle conforme DPM_FO_27"),
            ("Pharmacie (FO_27)", "Sérum Physiologique, Antiseptiques & Pansements Compressifs Stériles", "Infirmerie Station", 20, 65.0, "2027-06-15", 10, 65.0, 22, 65.0, "2027-06-15", "Lot complet sous contrôle de péremption")
        ]
        for cs in consos:
            c.execute('''INSERT INTO fo26_27_consommables (
                categorie, article, emplacement,
                debut_qte, debut_prix_unit, debut_date_expir,
                livre_qte, livre_prix_unit,
                fin_qte, fin_prix_unit, fin_date_expir, observations
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', cs)

    # 4. Consommation Pilotine (FO_28)
    c.execute("SELECT COUNT(*) FROM fo28_pilotine")
    if c.fetchone()[0] == 0:
        releves_pil = [
            ("Pilotine NWM 1", "2026-08-01", 1200.0, 45.0, "2026-08-15", 2500.0, 40.0, "2026-08-31", 1450.0, 55.0, "Opérations d'accostage Août 2026 (2 250 L consommés)"),
            ("Pilotine NWM 1", "2026-09-01", 1450.0, 55.0, "2026-09-18", 2800.0, 30.0, "2026-09-30", 1650.0, 50.0, "Opérations Septembre 2026 (2 600 L consommés)"),
            ("Pilotine NWM 1", "2026-10-01", 1650.0, 50.0, "2026-10-14", 2400.0, 40.0, "2026-10-24", 1900.0, 60.0, "Suivi mensuel Octobre 2026 en cours (2 150 L consommés)")
        ]
        for rp in releves_pil:
            c.execute('''INSERT INTO fo28_pilotine (
                nom_pilotine, debut_date, debut_gasoil, debut_lubrif,
                livre_date, livre_gasoil, livre_lubrif,
                fin_date, fin_gasoil, fin_lubrif, observations
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)''', rp)

    # 5. Registre des EPIs (FO_29)
    c.execute("SELECT COUNT(*) FROM fo29_epis")
    if c.fetchone()[0] == 0:
        epis_seed = [
            ("Gilets de Sauvetage Gonflables 275N SOLAS avec Balise AIS/PLB", 10, "Neuf", "2027-10-15", 38000.0, 4, "Neuf", "2028-10-15", 15200.0, "Vestiaire Pilotes", "Non", "Révision annuelle", "Dotation individuelle Pilotes NWM"),
            ("Casques de Sécurité Marine avec Jugulaire & Visière", 10, "Bon", "2028-05-01", 6500.0, 5, "Neuf", "2029-05-01", 3250.0, "Magasin EPI", "Non", "Inspection visuelle", "Norme EN 397 / Embarquement échelle pilote"),
            ("Chaussures & Bottes de Sécurité Pont Antidérapantes S3 SRC", 10, "Bon", "2027-08-01", 12000.0, 4, "Neuf", "2028-08-01", 4800.0, "Magasin EPI", "Non", "Entretien cuir", "Semelles haute adhérence pont mouillé"),
            ("Vestes de Quart Hauturières Imperméables & Respirantes Haute Visibilité", 10, "Neuf", "2028-10-01", 28000.0, 2, "Neuf", "2028-10-01", 5600.0, "Vestiaire Pilotes", "Non", "Lavage technique", "Bandes rétro-réfléchissantes SOLAS")
        ]
        for ep in epis_seed:
            c.execute('''INSERT INTO fo29_epis (
                article, util_nombre, util_etat, util_echeance, util_cout,
                stock_nombre, stock_etat, stock_echeance, stock_cout, stock_local,
                besoin_achat, besoin_maintenance, observations
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''', ep)

    # 6. Checklists CL_06 & CL_07
    c.execute("SELECT COUNT(*) FROM cl06_07_checklists")
    if c.fetchone()[0] == 0:
        cls_seed = [
            (
                "DPM_CL_06 & DPM_CL_07",
                "Radios Portatifs VHF Marines ATEX (Motorola DP4801 Ex)",
                "Certification ATEX gaz/poussières, étanchéité IP67, fréquences marines VHF ITU, GPS intégré, accessoires IMPRES ATEX Noise Cancelling, garantie 24 mois.",
                "Utiliser exclusivement avec batterie ATEX DP4401 et housse cuir FUNDA DURA. Vérifier la charge (>80%) avant chaque manœuvre.",
                "Ne jamais recharger ou remplacer la batterie en atmosphère explosive. Rinçage doux au chiffon humide après exposition saline.",
                "Fournisseur agréé : SOREMAR (BC N°20260014)"
            ),
            (
                "DPM_CL_06 & DPM_CL_07",
                "Gilets de Sauvetage Gonflables 275N SOLAS (EPI Pilotes)",
                "Homologation SOLAS/MED 275 Newtons, double chambre, déclenchement hydrostatique Hammar, lampe flash automatique, sangles d'entrejambe.",
                "Port obligatoire lors de tout transfert sur la pilotine et sur l'échelle de pilote. Vérifier le témoin vert de la tête hydrostatique avant départ.",
                "Inspection mensuelle visuelle (cartouche CO2, intégrité enveloppe). Révision annuelle obligatoire en station agréée.",
                "Référentiel ISPO & DPM_FO_29"
            )
        ]
        for cl_row in cls_seed:
            c.execute('''INSERT INTO cl06_07_checklists (
                type_checklist, equipement_rubrique, specifications_achat,
                recommandations_utilisation, recommandations_maintenance, observations
            ) VALUES (?,?,?,?,?,?)''', cl_row)

    # 7. Budget FO_30
    c.execute("SELECT COUNT(*) FROM fo30_budget_lignes")
    if c.fetchone()[0] == 0:
        budgets_seed = [
            ("Investissement", "Radios Portatifs VHF", "Acquisition de 10 Radios VHF portatives marines ATEX + 15 Batteries de rechange", "Dotation critique de radiocommunication pour la sécurité des manœuvres (SM ISPO)", 21575.00, 10.0, 215750.00, 0.0, 0.0, "BC N°20260014 - Facture SOREMAR F-RAD26/0024 (215 750,00 MAD TTC)"),
            ("Investissement", "Vigie", "Équipements de radiocommunication fixe, AIS et optique de Vigie (FO_25)", "Équipement initial de surveillance et coordination du trafic à la Vigie NWM", 85000.00, 1.0, 85000.00, 0.0, 0.0, "Dotation Vigie DPM_FO_25"),
            ("Investissement", "EPIs", "Dotation complète EPI SOLAS Pilotes (Gilets 275N, Casques, Bottes, Vestes)", "Protection individuelle réglementaire des pilotes maritimes (DPM_FO_29)", 113350.00, 1.0, 113350.00, 0.0, 0.0, "Conforme au registre DPM_FO_29"),
            ("Consommation (Générale / Pharmacie)", "Consommation Générale", "Fournitures techniques de Vigie, registres et consommables informatiques", "Fonctionnement continu 24/7 de la station de pilotage", 8890.00, 1.0, 8890.00, 1.0, 7500.00, "Consolidé depuis DPM_FO_26"),
            ("Consommation (Générale / Pharmacie)", "Consommation Pharmacie", "Renouvellement trousses médicales SOLAS et consommables infirmerie", "Maintien de la conformité sanitaire bord et terre", 9200.00, 1.0, 9200.00, 1.0, 8000.00, "Consolidé depuis DPM_FO_27")
        ]
        for b_row in budgets_seed:
            c.execute('''INSERT INTO fo30_budget_lignes (
                type_ligne, classe_rubrique, article_investissement, justification,
                prix_unitaire_estime, besoin_unites_estime, cout_estime_n,
                qte_annee_prec, cout_annee_prec, observations
            ) VALUES (?,?,?,?,?,?,?,?,?,?)''', b_row)

    # 8. Journal d'Audit Initial
    c.execute("SELECT COUNT(*) FROM audit_logs")
    if c.fetchone()[0] == 0:
        log_audit("SYSTÈME SM ISPO", "INITIALISATION", "Déploiement de la base de données ERP Ressources Matérielles Nador West Med.")
        log_audit("DPM_FO_24/25 (VHF)", "RÉCEPTION OFFICIELLE", "Intégration des 10 VHF Motorola DP4801 ATEX + 15 Batteries SOREMAR (215 750,00 MAD) - PV du 15/10/2026.")
    conn.commit()

init_db()
seed_initial_data()

def parse_date_safe(val):
    try:
        if pd.isna(val) or not str(val).strip():
            return date.today()
        return pd.to_datetime(val).date()
    except Exception:
        return date.today()

# ==============================================================================
# 4. MOTEUR D'EXPORT EXCEL OFFICIEL NADOR WEST MED & RAPPORT EXÉCUTIF HTML/PDF
# ==============================================================================
def get_official_styles(workbook):
    return {
        'org_box': workbook.add_format({
            'bold': True, 'font_size': 9, 'font_color': '#1B3668',
            'align': 'center', 'valign': 'bottom', 'border': 1,
            'bg_color': '#FFFFFF', 'text_wrap': True
        }),
        'title_box': workbook.add_format({
            'bold': True, 'font_size': 13, 'font_color': '#FFFFFF',
            'align': 'center', 'valign': 'vcenter', 'border': 1,
            'bg_color': '#1B3668', 'text_wrap': True
        }),
        'ref_box': workbook.add_format({
            'bold': True, 'font_size': 9, 'font_color': '#1B3668',
            'align': 'left', 'valign': 'vcenter', 'border': 1,
            'bg_color': '#F0F7FA', 'text_wrap': True
        }),
        'th_main': workbook.add_format({
            'bold': True, 'font_size': 10, 'font_color': '#FFFFFF',
            'align': 'center', 'valign': 'vcenter', 'border': 1,
            'bg_color': '#008394', 'text_wrap': True
        }),
        'th_sub': workbook.add_format({
            'bold': True, 'font_size': 9, 'font_color': '#1B3668',
            'align': 'center', 'valign': 'vcenter', 'border': 1,
            'bg_color': '#D9EBF0', 'text_wrap': True
        }),
        'section_banner': workbook.add_format({
            'bold': True, 'font_size': 10, 'font_color': '#FFFFFF',
            'align': 'left', 'valign': 'vcenter', 'border': 1,
            'bg_color': '#1B3668'
        }),
        'td_text': workbook.add_format({
            'font_size': 9, 'align': 'left', 'valign': 'vcenter',
            'border': 1, 'text_wrap': True
        }),
        'td_center': workbook.add_format({
            'font_size': 9, 'align': 'center', 'valign': 'vcenter',
            'border': 1, 'text_wrap': True
        }),
        'td_num': workbook.add_format({
            'font_size': 9, 'align': 'right', 'valign': 'vcenter',
            'border': 1, 'num_format': '#,##0'
        }),
        'td_curr': workbook.add_format({
            'font_size': 9, 'align': 'right', 'valign': 'vcenter',
            'border': 1, 'num_format': '#,##0.00'
        }),
        'footer_label': workbook.add_format({
            'bold': True, 'font_size': 10, 'font_color': '#1B3668',
            'align': 'left', 'valign': 'vcenter', 'border': 1,
            'bg_color': '#F0F7FA'
        }),
        'footer_val': workbook.add_format({
            'bold': True, 'font_size': 10, 'font_color': '#1B3668',
            'align': 'right', 'valign': 'vcenter', 'border': 1,
            'bg_color': '#D9EBF0', 'num_format': '#,##0.00'
        }),
        'sign_box': workbook.add_format({
            'bold': True, 'italic': True, 'font_size': 10, 'font_color': '#1B3668',
            'align': 'center', 'valign': 'top', 'border': 1,
            'bg_color': '#FAFAFA'
        })
    }

def draw_official_header(ws, styles, doc_code, doc_title, total_cols, emission_date="31/12/25"):
    ws.set_landscape()
    ws.set_paper(9)
    ws.fit_to_pages(1, 0)
    ws.set_row(0, 24)
    ws.set_row(1, 24)
    ws.set_row(2, 24)

    left_end = max(1, min(2, total_cols - 3))
    right_start = max(left_end + 1, total_cols - 2)

    ws.merge_range(0, 0, 2, left_end - 1, "Direction du Pilotage Maritime (DPM)", styles['org_box'])
    ws.merge_range(0, left_end, 2, right_start - 1, doc_title, styles['title_box'])
    ws.merge_range(0, right_start, 2, total_cols - 1, f"{doc_code}\nDate d'émission : {emission_date}\nPage : 1/1", styles['ref_box'])

    try:
        logo_bytes = generate_nwm_logo_png_bytes()
        img_pil = Image.open(BytesIO(logo_bytes))
        _, h_px = img_pil.size
        scale = 56.0 / float(h_px)
        ws.insert_image(0, 0, "logo_nwm.png", {
            'image_data': BytesIO(logo_bytes),
            'x_offset': 10,
            'y_offset': 4,
            'x_scale': scale,
            'y_scale': scale,
            'object_position': 1
        })
    except Exception:
        pass

def build_sheet_fo23(workbook, styles):
    ws = workbook.add_worksheet("DPM_FO_23_Infrastructures")
    draw_official_header(ws, styles, "DPM_FO_23", "Le Registre des Infrastructures de La DPM", 5)
    for idx, w in enumerate([28, 32, 32, 18, 30]):
        ws.set_column(idx, idx, w)

    ws.set_row(4, 24)
    ws.set_row(5, 22)
    ws.merge_range(4, 0, 5, 0, "Infrastructure", styles['th_main'])
    ws.merge_range(4, 1, 5, 1, "Besoins de réparation", styles['th_main'])
    ws.merge_range(4, 2, 4, 3, "Les réparations réalisées", styles['th_main'])
    ws.write(5, 2, "Commentaire", styles['th_sub'])
    ws.write(5, 3, "Coût", styles['th_sub'])
    ws.merge_range(4, 4, 5, 4, "Observations", styles['th_main'])

    df = pd.read_sql_query("SELECT * FROM fo23_infrastructures", conn)
    r = 6
    for _, row in df.iterrows():
        ws.set_row(r, 24)
        ws.write(r, 0, row['infrastructure'], styles['td_text'])
        ws.write(r, 1, row['besoins_reparation'], styles['td_text'])
        ws.write(r, 2, row['reparations_commentaire'], styles['td_text'])
        ws.write(r, 3, float(row['reparations_cout'] or 0), styles['td_curr'])
        ws.write(r, 4, row['observations'], styles['td_text'])
        r += 1

    ws.set_row(r, 24)
    ws.merge_range(r, 0, r, 2, "Total des Réparations Réalisées (MAD) :", styles['footer_label'])
    ws.write(r, 3, float(df['reparations_cout'].sum() if not df.empty else 0), styles['footer_val'])
    ws.write(r, 4, "Le PMJA Ressources DPM", styles['sign_box'])

def build_sheet_fo24_or_25(workbook, styles, sheet_name, doc_code, doc_title, df_subset):
    ws = workbook.add_worksheet(sheet_name[:31])
    draw_official_header(ws, styles, doc_code, doc_title, 10)
    for idx, w in enumerate([32, 16, 12, 11, 22, 11, 20, 14, 14, 32]):
        ws.set_column(idx, idx, w)

    ws.set_row(4, 24)
    ws.set_row(5, 22)
    ws.merge_range(4, 0, 5, 0, "Article", styles['th_main'])
    ws.merge_range(4, 1, 5, 1, "Coût Estimé", styles['th_main'])
    ws.merge_range(4, 2, 4, 4, "En utilisation", styles['th_main'])
    ws.write(5, 2, "Etat", styles['th_sub'])
    ws.write(5, 3, "Quantité", styles['th_sub'])
    ws.write(5, 4, "Emplacement", styles['th_sub'])
    ws.merge_range(4, 5, 4, 6, "En Stock", styles['th_main'])
    ws.write(5, 5, "Quantité", styles['th_sub'])
    ws.write(5, 6, "Localisation", styles['th_sub'])
    ws.merge_range(4, 7, 4, 8, "Besoins", styles['th_main'])
    ws.write(5, 7, "Achat", styles['th_sub'])
    ws.write(5, 8, "Réparation", styles['th_sub'])
    ws.merge_range(4, 9, 5, 9, "Observations", styles['th_main'])

    r = 6
    for _, row in df_subset.iterrows():
        ws.set_row(r, 26)
        ws.write(r, 0, row['article'], styles['td_text'])
        ws.write(r, 1, float(row['cout_estime'] or 0), styles['td_curr'])
        ws.write(r, 2, row['util_etat'], styles['td_center'])
        ws.write(r, 3, int(row['util_quantite'] or 0), styles['td_num'])
        ws.write(r, 4, row['util_emplacement'], styles['td_text'])
        ws.write(r, 5, int(row['stock_quantite'] or 0), styles['td_num'])
        ws.write(r, 6, row['stock_localisation'], styles['td_text'])
        ws.write(r, 7, row['besoin_achat'], styles['td_center'])
        ws.write(r, 8, row['besoin_reparation'], styles['td_center'])
        ws.write(r, 9, row['observations'], styles['td_text'])
        r += 1

    ws.set_row(r, 24)
    ws.write(r, 0, "Total Coût Estimé (MAD) :", styles['footer_label'])
    ws.write(r, 1, float(df_subset['cout_estime'].sum() if not df_subset.empty else 0), styles['footer_val'])
    ws.merge_range(r, 2, r, 6, "", styles['footer_label'])
    ws.merge_range(r, 7, r, 9, "Le PMJA Ressources DPM", styles['sign_box'])

def build_sheet_fo26(workbook, styles):
    ws = workbook.add_worksheet("DPM_FO_26_Conso_Generales")
    draw_official_header(ws, styles, "DPM_FO_26", "L'Etat des Consommations générales de La DPM", 13)
    for i, w in enumerate([24, 18, 10, 12, 14, 10, 12, 14, 10, 12, 14, 18, 24]):
        ws.set_column(i, i, w)

    ws.set_row(4, 24)
    ws.set_row(5, 22)
    ws.merge_range(4, 0, 5, 0, "Article", styles['th_main'])
    ws.merge_range(4, 1, 5, 1, "Emplacement", styles['th_main'])
    ws.merge_range(4, 2, 4, 4, "Existant début du période", styles['th_main'])
    ws.write(5, 2, "Qtité", styles['th_sub'])
    ws.write(5, 3, "Prix unit", styles['th_sub'])
    ws.write(5, 4, "Coût", styles['th_sub'])
    ws.merge_range(4, 5, 4, 7, "Livré durant la période", styles['th_main'])
    ws.write(5, 5, "Qtité", styles['th_sub'])
    ws.write(5, 6, "Prix unit", styles['th_sub'])
    ws.write(5, 7, "Coût", styles['th_sub'])
    ws.merge_range(4, 8, 4, 10, "Existant Fin de la période", styles['th_main'])
    ws.write(5, 8, "Qtité", styles['th_sub'])
    ws.write(5, 9, "Prix unit", styles['th_sub'])
    ws.write(5, 10, "Coût", styles['th_sub'])
    ws.merge_range(4, 11, 5, 11, "Cout des Consommations", styles['th_main'])
    ws.merge_range(4, 12, 5, 12, "Observation", styles['th_main'])

    df = pd.read_sql_query("SELECT * FROM fo26_27_consommables WHERE categorie='Consommations Générales (FO_26)'", conn)
    r = 6
    tot_conso = 0.0
    for _, row in df.iterrows():
        ws.set_row(r, 22)
        c_deb = float(row['debut_qte']) * float(row['debut_prix_unit'])
        c_liv = float(row['livre_qte']) * float(row['livre_prix_unit'])
        c_fin = float(row['fin_qte']) * float(row['fin_prix_unit'])
        c_conso = (c_deb + c_liv) - c_fin
        tot_conso += c_conso

        ws.write(r, 0, row['article'], styles['td_text'])
        ws.write(r, 1, row['emplacement'], styles['td_text'])
        ws.write(r, 2, int(row['debut_qte']), styles['td_num'])
        ws.write(r, 3, float(row['debut_prix_unit']), styles['td_curr'])
        ws.write(r, 4, c_deb, styles['td_curr'])
        ws.write(r, 5, int(row['livre_qte']), styles['td_num'])
        ws.write(r, 6, float(row['livre_prix_unit']), styles['td_curr'])
        ws.write(r, 7, c_liv, styles['td_curr'])
        ws.write(r, 8, int(row['fin_qte']), styles['td_num'])
        ws.write(r, 9, float(row['fin_prix_unit']), styles['td_curr'])
        ws.write(r, 10, c_fin, styles['td_curr'])
        ws.write(r, 11, c_conso, styles['td_curr'])
        ws.write(r, 12, row['observations'], styles['td_text'])
        r += 1

    ws.set_row(r, 26)
    ws.merge_range(r, 0, r, 10, "Le Cout des Consommations de la période :", styles['footer_label'])
    ws.write(r, 11, tot_conso, styles['footer_val'])
    ws.write(r, 12, "Le PMJA Ressources DPM", styles['sign_box'])

def build_sheet_fo27(workbook, styles):
    ws = workbook.add_worksheet("DPM_FO_27_Pharmacie")
    draw_official_header(ws, styles, "DPM_FO_27", "L'Etat des Consommations Pharmaceutiques de La DPM", 15)
    for i, w in enumerate([22, 16, 9, 12, 11, 13, 9, 11, 13, 9, 12, 11, 13, 16, 22]):
        ws.set_column(i, i, w)

    ws.set_row(4, 24)
    ws.set_row(5, 22)
    ws.merge_range(4, 0, 5, 0, "Article", styles['th_main'])
    ws.merge_range(4, 1, 5, 1, "Emplacement", styles['th_main'])
    ws.merge_range(4, 2, 4, 5, "Existant début du période", styles['th_main'])
    ws.write(5, 2, "Qtité", styles['th_sub'])
    ws.write(5, 3, "Date Expir", styles['th_sub'])
    ws.write(5, 4, "Prix unit", styles['th_sub'])
    ws.write(5, 5, "Coût", styles['th_sub'])
    ws.merge_range(4, 6, 4, 8, "Livré durant la période", styles['th_main'])
    ws.write(5, 6, "Qtité", styles['th_sub'])
    ws.write(5, 7, "Prix unit", styles['th_sub'])
    ws.write(5, 8, "Coût", styles['th_sub'])
    ws.merge_range(4, 9, 4, 12, "Existant Fin de la période", styles['th_main'])
    ws.write(5, 9, "Qtité", styles['th_sub'])
    ws.write(5, 10, "Date Expir", styles['th_sub'])
    ws.write(5, 11, "Prix unit", styles['th_sub'])
    ws.write(5, 12, "Coût", styles['th_sub'])
    ws.merge_range(4, 13, 5, 13, "Cout des Consommations", styles['th_main'])
    ws.merge_range(4, 14, 5, 14, "Observation", styles['th_main'])

    df = pd.read_sql_query("SELECT * FROM fo26_27_consommables WHERE categorie='Pharmacie (FO_27)'", conn)
    r = 6
    tot_conso = 0.0
    for _, row in df.iterrows():
        ws.set_row(r, 22)
        c_deb = float(row['debut_qte']) * float(row['debut_prix_unit'])
        c_liv = float(row['livre_qte']) * float(row['livre_prix_unit'])
        c_fin = float(row['fin_qte']) * float(row['fin_prix_unit'])
        c_conso = (c_deb + c_liv) - c_fin
        tot_conso += c_conso

        ws.write(r, 0, row['article'], styles['td_text'])
        ws.write(r, 1, row['emplacement'], styles['td_text'])
        ws.write(r, 2, int(row['debut_qte']), styles['td_num'])
        ws.write(r, 3, str(row['debut_date_expir']), styles['td_center'])
        ws.write(r, 4, float(row['debut_prix_unit']), styles['td_curr'])
        ws.write(r, 5, c_deb, styles['td_curr'])
        ws.write(r, 6, int(row['livre_qte']), styles['td_num'])
        ws.write(r, 7, float(row['livre_prix_unit']), styles['td_curr'])
        ws.write(r, 8, c_liv, styles['td_curr'])
        ws.write(r, 9, int(row['fin_qte']), styles['td_num'])
        ws.write(r, 10, str(row['fin_date_expir']), styles['td_center'])
        ws.write(r, 11, float(row['fin_prix_unit']), styles['td_curr'])
        ws.write(r, 12, c_fin, styles['td_curr'])
        ws.write(r, 13, c_conso, styles['td_curr'])
        ws.write(r, 14, row['observations'], styles['td_text'])
        r += 1

    ws.set_row(r, 26)
    ws.merge_range(r, 0, r, 12, "Le Cout des Consommations de la période :", styles['footer_label'])
    ws.write(r, 13, tot_conso, styles['footer_val'])
    ws.write(r, 14, "Le PMJA Ressources DPM", styles['sign_box'])

def build_sheet_fo28(workbook, styles):
    ws = workbook.add_worksheet("DPM_FO_28_Pilotine")
    draw_official_header(ws, styles, "DPM_FO_28", "Le registre de La Consommation de la Pilotine", 13)
    for col in range(12):
        ws.set_column(col, col, 12)
    ws.set_column(12, 12, 26)

    ws.set_row(4, 24)
    ws.set_row(5, 22)
    ws.merge_range(4, 0, 4, 2, "Existant début du période", styles['th_main'])
    ws.merge_range(4, 3, 4, 5, "Livré durant la période", styles['th_main'])
    ws.merge_range(4, 6, 4, 8, "Existant Fin de la période", styles['th_main'])
    ws.merge_range(4, 9, 4, 11, "Consommé durant période", styles['th_main'])
    ws.merge_range(4, 12, 5, 12, "Observation", styles['th_main'])

    for base_col in [0, 3, 6, 9]:
        ws.write(5, base_col, "Date", styles['th_sub'])
        ws.write(5, base_col + 1, "Gasoil", styles['th_sub'])
        ws.write(5, base_col + 2, "Lubrif", styles['th_sub'])

    df = pd.read_sql_query("SELECT * FROM fo28_pilotine", conn)
    r = 6
    tot_gas, tot_lub = 0.0, 0.0
    for _, row in df.iterrows():
        ws.set_row(r, 22)
        c_gas = float(row['debut_gasoil']) + float(row['livre_gasoil']) - float(row['fin_gasoil'])
        c_lub = float(row['debut_lubrif']) + float(row['livre_lubrif']) - float(row['fin_lubrif'])
        tot_gas += c_gas
        tot_lub += c_lub

        ws.write(r, 0, str(row['debut_date']), styles['td_center'])
        ws.write(r, 1, float(row['debut_gasoil']), styles['td_curr'])
        ws.write(r, 2, float(row['debut_lubrif']), styles['td_curr'])
        ws.write(r, 3, str(row['livre_date']), styles['td_center'])
        ws.write(r, 4, float(row['livre_gasoil']), styles['td_curr'])
        ws.write(r, 5, float(row['livre_lubrif']), styles['td_curr'])
        ws.write(r, 6, str(row['fin_date']), styles['td_center'])
        ws.write(r, 7, float(row['fin_gasoil']), styles['td_curr'])
        ws.write(r, 8, float(row['fin_lubrif']), styles['td_curr'])
        ws.write(r, 9, str(row['fin_date']), styles['td_center'])
        ws.write(r, 10, c_gas, styles['td_curr'])
        ws.write(r, 11, c_lub, styles['td_curr'])
        ws.write(r, 12, f"[{row['nom_pilotine']}] {row['observations']}", styles['td_text'])
        r += 1

    nb_rows = len(df) if not df.empty else 1
    ws.set_row(r, 24)
    ws.merge_range(r, 0, r, 9, "Consommation Totale Durant Période :", styles['footer_label'])
    ws.write(r, 10, tot_gas, styles['footer_val'])
    ws.write(r, 11, tot_lub, styles['footer_val'])
    ws.write(r, 12, "", styles['footer_label'])

    ws.set_row(r + 1, 24)
    ws.merge_range(r + 1, 0, r + 1, 9, "Consommation Moyenne Durant Période :", styles['footer_label'])
    ws.write(r + 1, 10, tot_gas / nb_rows if not df.empty else 0.0, styles['footer_val'])
    ws.write(r + 1, 11, tot_lub / nb_rows if not df.empty else 0.0, styles['footer_val'])
    ws.write(r + 1, 12, "Le PMJA Ressources DPM", styles['sign_box'])

def build_sheet_fo29(workbook, styles):
    ws = workbook.add_worksheet("DPM_FO_29_EPIs")
    draw_official_header(ws, styles, "DPM_FO_29", "Le registre des EPIs", 13)
    for i, w in enumerate([26, 10, 12, 13, 14, 10, 12, 13, 14, 18, 14, 16, 24]):
        ws.set_column(i, i, w)

    ws.set_row(4, 24)
    ws.set_row(5, 22)
    ws.merge_range(4, 0, 5, 0, "Article", styles['th_main'])
    ws.merge_range(4, 1, 4, 4, "En utilisation", styles['th_main'])
    ws.write(5, 1, "Nombre", styles['th_sub'])
    ws.write(5, 2, "Etat", styles['th_sub'])
    ws.write(5, 3, "Échéance", styles['th_sub'])
    ws.write(5, 4, "Coût", styles['th_sub'])
    ws.merge_range(4, 5, 4, 9, "En Stock", styles['th_main'])
    ws.write(5, 5, "Nombre", styles['th_sub'])
    ws.write(5, 6, "Etat", styles['th_sub'])
    ws.write(5, 7, "Échéance", styles['th_sub'])
    ws.write(5, 8, "Coût", styles['th_sub'])
    ws.write(5, 9, "Local", styles['th_sub'])
    ws.merge_range(4, 10, 4, 11, "Besoins", styles['th_main'])
    ws.write(5, 10, "Achat", styles['th_sub'])
    ws.write(5, 11, "Maintenance", styles['th_sub'])
    ws.merge_range(4, 12, 5, 12, "Observations", styles['th_main'])

    df = pd.read_sql_query("SELECT * FROM fo29_epis", conn)
    r = 6
    tot_util_cout, tot_stock_cout = 0.0, 0.0
    for _, row in df.iterrows():
        ws.set_row(r, 22)
        uc = float(row['util_cout'] or 0)
        sc = float(row['stock_cout'] or 0)
        tot_util_cout += uc
        tot_stock_cout += sc
        ws.write(r, 0, row['article'], styles['td_text'])
        ws.write(r, 1, int(row['util_nombre'] or 0), styles['td_num'])
        ws.write(r, 2, row['util_etat'], styles['td_center'])
        ws.write(r, 3, str(row['util_echeance']), styles['td_center'])
        ws.write(r, 4, uc, styles['td_curr'])
        ws.write(r, 5, int(row['stock_nombre'] or 0), styles['td_num'])
        ws.write(r, 6, row['stock_etat'], styles['td_center'])
        ws.write(r, 7, str(row['stock_echeance']), styles['td_center'])
        ws.write(r, 8, sc, styles['td_curr'])
        ws.write(r, 9, row['stock_local'], styles['td_text'])
        ws.write(r, 10, row['besoin_achat'], styles['td_center'])
        ws.write(r, 11, row['besoin_maintenance'], styles['td_center'])
        ws.write(r, 12, row['observations'], styles['td_text'])
        r += 1

    ws.set_row(r, 24)
    ws.merge_range(r, 0, r, 3, "Total Coût EPIs (En utilisation / En stock) :", styles['footer_label'])
    ws.write(r, 4, tot_util_cout, styles['footer_val'])
    ws.merge_range(r, 5, r, 7, "", styles['footer_label'])
    ws.write(r, 8, tot_stock_cout, styles['footer_val'])
    ws.merge_range(r, 9, r, 11, "", styles['footer_label'])
    ws.write(r, 12, "Le PMJA Ressources DPM", styles['sign_box'])

def build_sheet_fo30(workbook, styles):
    ws = workbook.add_worksheet("DPM_FO_30_Budget")
    draw_official_header(ws, styles, "DPM_FO_30", "Le Formulaire de Préparation du Budget de La DPM", 9)
    for i, w in enumerate([20, 30, 15, 15, 16, 16, 16, 16, 26]):
        ws.set_column(i, i, w)

    df = pd.read_sql_query("SELECT * FROM fo30_budget_lignes", conn)
    df_conso = df[df['type_ligne'] == 'Consommation (Générale / Pharmacie)'] if not df.empty else pd.DataFrame()
    df_inv = df[df['type_ligne'] == 'Investissement'] if not df.empty else pd.DataFrame()

    r = 4
    ws.set_row(r, 24)
    ws.merge_range(r, 0, r, 8, "Consommations Générale / Consommation Pharmacie.", styles['section_banner'])
    r += 1
    ws.set_row(r, 24)
    ws.set_row(r + 1, 22)
    ws.merge_range(r, 0, r + 1, 0, "Classe", styles['th_main'])
    ws.merge_range(r, 1, r + 1, 1, "Article", styles['th_main'])
    ws.merge_range(r, 2, r, 4, "Besoins annuel Estimé", styles['th_main'])
    ws.write(r + 1, 2, "Prix Unitaire", styles['th_sub'])
    ws.write(r + 1, 3, "Besoins (unités)", styles['th_sub'])
    ws.write(r + 1, 4, "Coût", styles['th_sub'])
    ws.merge_range(r, 5, r, 6, "Consommé année précédente", styles['th_main'])
    ws.write(r + 1, 5, "Quantité (unités)", styles['th_sub'])
    ws.write(r + 1, 6, "Coût", styles['th_sub'])
    ws.merge_range(r, 7, r + 1, 7, "Variation Budget", styles['th_main'])
    ws.merge_range(r, 8, r + 1, 8, "Observations", styles['th_main'])
    r += 2

    tot_conso_n, tot_conso_prec = 0.0, 0.0
    for _, row in df_conso.iterrows():
        ws.set_row(r, 22)
        cn = float(row['cout_estime_n'] or 0)
        cp = float(row['cout_annee_prec'] or 0)
        var = cn - cp
        tot_conso_n += cn
        tot_conso_prec += cp
        ws.write(r, 0, row['classe_rubrique'], styles['td_text'])
        ws.write(r, 1, row['article_investissement'], styles['td_text'])
        ws.write(r, 2, float(row['prix_unitaire_estime'] or 0), styles['td_curr'])
        ws.write(r, 3, float(row['besoin_unites_estime'] or 0), styles['td_num'])
        ws.write(r, 4, cn, styles['td_curr'])
        ws.write(r, 5, float(row['qte_annee_prec'] or 0), styles['td_num'])
        ws.write(r, 6, cp, styles['td_curr'])
        ws.write(r, 7, var, styles['td_curr'])
        ws.write(r, 8, row['observations'], styles['td_text'])
        r += 1

    ws.set_row(r, 24)
    ws.merge_range(r, 0, r, 3, f"Besoins annuels consommations (en Dhs) : {tot_conso_n:,.2f}", styles['footer_label'])
    ws.merge_range(r, 4, r, 6, f"Utilisés année précédente en Dhs : {tot_conso_prec:,.2f}", styles['footer_label'])
    ws.merge_range(r, 7, r, 8, f"Variation Budget (en Dhs) : {tot_conso_n - tot_conso_prec:+,.2f}", styles['footer_label'])
    r += 2

    ws.set_row(r, 24)
    ws.merge_range(r, 0, r, 8, "Partie Investissements : Formations / EPIs / Tenue / Peinture / Construction / Vigie / PCs / Etc.", styles['section_banner'])
    r += 1
    ws.set_row(r, 24)
    ws.merge_range(r, 0, r, 2, "Investissement", styles['th_main'])
    ws.merge_range(r, 3, r, 7, "Justifications", styles['th_main'])
    ws.write(r, 8, "Cout", styles['th_main'])
    r += 1

    tot_inv_n, tot_inv_prec = 0.0, 0.0
    for _, row in df_inv.iterrows():
        ws.set_row(r, 24)
        cn = float(row['cout_estime_n'] or 0)
        cp = float(row['cout_annee_prec'] or 0)
        tot_inv_n += cn
        tot_inv_prec += cp
        ws.merge_range(r, 0, r, 2, f"[{row['classe_rubrique']}] {row['article_investissement']}", styles['td_text'])
        ws.merge_range(r, 3, r, 7, row['justification'], styles['td_text'])
        ws.write(r, 8, cn, styles['td_curr'])
        r += 1

    ws.set_row(r, 24)
    ws.merge_range(r, 0, r, 7, "Total des investissements :", styles['footer_label'])
    ws.write(r, 8, tot_inv_n, styles['footer_val'])
    r += 1

    budget_prec = tot_conso_prec + tot_inv_prec
    budget_obj = tot_conso_n + tot_inv_n
    var_glob = budget_obj - budget_prec

    ws.set_row(r, 26)
    ws.merge_range(r, 0, r, 2, f"Budget année précédente : {budget_prec:,.2f} MAD", styles['footer_label'])
    ws.merge_range(r, 3, r, 5, f"Budget année en objet : {budget_obj:,.2f} MAD", styles['footer_label'])
    ws.merge_range(r, 6, r, 8, f"Variation Budget : {var_glob:+,.2f} MAD", styles['footer_label'])

def build_sheets_cl06_07(workbook, styles):
    df = pd.read_sql_query("SELECT * FROM cl06_07_checklists", conn)

    ws6 = workbook.add_worksheet("DPM_CL_06_Achats")
    draw_official_header(ws6, styles, "DPM_CL_06", "Les Spécifications d'Achat : Equipements", 3)
    ws6.set_column(0, 0, 32)
    ws6.set_column(1, 1, 65)
    ws6.set_column(2, 2, 28)
    ws6.set_row(4, 24)
    ws6.write(4, 0, "Rubrique", styles['th_main'])
    ws6.write(4, 1, "Principales Spécifications d'Achat", styles['th_main'])
    ws6.write(4, 2, "Observations", styles['th_main'])
    r = 5
    for _, row in df.iterrows():
        ws6.set_row(r, 36)
        ws6.write(r, 0, row['equipement_rubrique'], styles['td_text'])
        ws6.write(r, 1, row['specifications_achat'], styles['td_text'])
        ws6.write(r, 2, row['observations'], styles['td_text'])
        r += 1

    ws7 = workbook.add_worksheet("DPM_CL_07_Maintenance")
    draw_official_header(ws7, styles, "DPM_CL_07", "La Checklist des Recommandations d'Utilisation et de Maintenance des Equipements de La DPM", 3)
    ws7.set_column(0, 0, 32)
    ws7.set_column(1, 1, 48)
    ws7.set_column(2, 2, 48)
    ws7.set_row(4, 24)
    ws7.write(4, 0, "Equipement.", styles['th_main'])
    ws7.write(4, 1, "Les Principales Recommandations de Maintenance.", styles['th_main'])
    ws7.write(4, 2, "Les Principales Recommandations d'utilisation.", styles['th_main'])
    r = 5
    for _, row in df.iterrows():
        ws7.set_row(r, 36)
        ws7.write(r, 0, row['equipement_rubrique'], styles['td_text'])
        ws7.write(r, 1, row['recommandations_maintenance'], styles['td_text'])
        ws7.write(r, 2, row['recommandations_utilisation'], styles['td_text'])
        r += 1

def generate_official_excel_pack(target_form="ALL"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        wb = writer.book
        styles = get_official_styles(wb)
        df_all_eq = pd.read_sql_query("SELECT * FROM fo24_25_equipements", conn)

        if target_form in ["ALL", "FO_23"]:
            build_sheet_fo23(wb, styles)
        if target_form in ["ALL", "FO_24"]:
            df_fo24 = df_all_eq[df_all_eq['classe'] == "Équipements d'Ameublement (DPM_FO_24)"]
            build_sheet_fo24_or_25(wb, styles, "DPM_FO_24_Ameublement", "DPM_FO_24", "Le registre des équipements d'ameublement de La DPM", df_fo24)
        if target_form in ["ALL", "FO_25"]:
            df_fo25 = df_all_eq[df_all_eq['classe'] == "Équipements de la Vigie (DPM_FO_25)"]
            build_sheet_fo24_or_25(wb, styles, "DPM_FO_25_Vigie", "DPM_FO_25", "Le registre des équipements de la vigie de La DPM", df_fo25)
        if target_form in ["ALL", "FO_24_25_ALL"]:
            build_sheet_fo24_or_25(wb, styles, "DPM_Registre_Global_Equip", "DMP_PR_02", "Registre Consolidé des Équipements (VHF, Vigie, Ameublement, PPU, Simulateur)", df_all_eq)
        if target_form in ["ALL", "FO_26"]:
            build_sheet_fo26(wb, styles)
        if target_form in ["ALL", "FO_27"]:
            build_sheet_fo27(wb, styles)
        if target_form in ["ALL", "FO_28"]:
            build_sheet_fo28(wb, styles)
        if target_form in ["ALL", "FO_29"]:
            build_sheet_fo29(wb, styles)
        if target_form in ["ALL", "FO_30"]:
            build_sheet_fo30(wb, styles)
        if target_form in ["ALL", "CL_06_07"]:
            build_sheets_cl06_07(wb, styles)

    return output.getvalue()

def generate_executive_html_report(logo_b64_str):
    """Génère un Rapport Exécutif officiel HTML/PDF prêt à imprimer avec en-tête Nador West Med."""
    df_eq = pd.read_sql_query("SELECT classe, COUNT(*) as refs, SUM(util_quantite) as qte_active, SUM(cout_estime) as valeur FROM fo24_25_equipements GROUP BY classe", conn)
    df_b = pd.read_sql_query("SELECT type_ligne, classe_rubrique, article_investissement, cout_estime_n, cout_annee_prec FROM fo30_budget_lignes", conn)
    tot_eq = df_eq['valeur'].sum() if not df_eq.empty else 0.0
    tot_b = df_b['cout_estime_n'].sum() if not df_b.empty else 0.0

    rows_eq_html = "".join([
        f"<tr><td><b>{r['classe']}</b></td><td style='text-align:center'>{r['refs']}</td><td style='text-align:center'>{r['qte_active']}</td><td style='text-align:right'>{r['valeur']:,.2f} MAD</td></tr>"
        for _, r in df_eq.iterrows()
    ])
    rows_b_html = "".join([
        f"<tr><td>{r['type_ligne']}</td><td><b>{r['classe_rubrique']}</b></td><td>{r['article_investissement']}</td><td style='text-align:right'>{r['cout_estime_n']:,.2f} MAD</td></tr>"
        for _, r in df_b.iterrows()
    ])

    html = f"""<!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Rapport Exécutif ISPO - DPM Nador West Med</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #0f3156; margin: 30px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #0097a7; padding-bottom: 15px; margin-bottom: 25px; }}
            .title-box h1 {{ margin: 0; font-size: 20px; color: #091e3a; }}
            .title-box p {{ margin: 4px 0 0 0; font-size: 12px; color: #475569; }}
            .ref-box {{ border: 1px solid #0097a7; background: #f0f7fa; padding: 8px 14px; font-size: 11px; border-radius: 6px; }}
            h2 {{ font-size: 15px; background: #091e3a; color: white; padding: 7px 12px; border-radius: 4px; margin-top: 22px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }}
            th {{ background: #008394; color: white; padding: 8px; border: 1px solid #cbd5e1; text-align: left; }}
            td {{ padding: 7px 8px; border: 1px solid #cbd5e1; }}
            .sign-grid {{ display: flex; justify-content: space-between; margin-top: 40px; }}
            .sign-card {{ width: 45%; border: 1px solid #94a3b8; padding: 12px; height: 90px; border-radius: 6px; font-size: 12px; }}
            @media print {{ .no-print {{ display: none; }} }}
        </style>
    </head>
    <body>
        <div class="no-print" style="margin-bottom:15px; text-align:right;">
            <button onclick="window.print()" style="background:#0097a7; color:white; border:none; padding:8px 16px; border-radius:6px; cursor:pointer; font-weight:bold;">🖨️ Imprimer / Enregistrer en PDF</button>
        </div>
        <div class="header">
            <img src="data:image/png;base64,{logo_b64_str}" style="height:65px;">
            <div class="title-box">
                <h1>DIRECTION DU PILOTAGE MARITIME — NADOR WEST MED</h1>
                <p>Synthèse Exécutive du Processus Ressources Matérielles (SM ISPO • DMP_PR_02 / DPM_FI_02)</p>
            </div>
            <div class="ref-box">
                <b>Réf :</b> Cartable RM ISPO<br>
                <b>Date d'édition :</b> {date.today()}<br>
                <b>Pilote RM :</b> Omar Dialmy
            </div>
        </div>
        <h2>1. Synthèse Patrimoniale des Équipements en Service (DPM_FO_24 / DPM_FO_25 / VHF)</h2>
        <table>
            <thead><tr><th>Classe de Ressource</th><th style="text-align:center">Références</th><th style="text-align:center">Unités Actives</th><th style="text-align:right">Valeur Engagée (MAD)</th></tr></thead>
            <tbody>{rows_eq_html}</tbody>
            <tfoot><tr style="background:#e0f2fe; font-weight:bold;"><td colspan="3">Total Patrimoine Équipements</td><td style="text-align:right">{tot_eq:,.2f} MAD</td></tr></tfoot>
        </table>
        <h2>2. Synthèse Budgétaire Consolidée (DPM_FO_30)</h2>
        <table>
            <thead><tr><th>Section</th><th>Rubrique</th><th>Intitulé</th><th style="text-align:right">Budget Année N (MAD)</th></tr></thead>
            <tbody>{rows_b_html}</tbody>
            <tfoot><tr style="background:#e0f2fe; font-weight:bold;"><td colspan="3">Total Budget Prévisionnel Consolidé (DPM_FO_30)</td><td style="text-align:right">{tot_b:,.2f} MAD</td></tr></tfoot>
        </table>
        <div class="sign-grid">
            <div class="sign-card"><b>Le Pilote Responsable Ressources Matérielles (PMJA) :</b><br>Omar Dialmy<br><br><i>Visa & Date :</i></div>
            <div class="sign-card"><b>Le Pilote Major — Direction du Pilotage Maritime :</b><br>Validation Direction DPM Nador West Med<br><br><i>Visa & Date :</i></div>
        </div>
    </body>
    </html>"""
    return html.encode("utf-8")

# ==============================================================================
# 5. BARRE LATÉRALE DE NAVIGATION & CONTRÔLE EXÉCUTIF
# ==============================================================================
logo_b64 = get_logo_base64()
st.sidebar.markdown(
    f'<div style="background:white; padding:12px; border-radius:10px; text-align:center; margin-bottom:12px; border:1px solid #cbd5e1; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">'
    f'<img src="data:image/png;base64,{logo_b64}" style="max-height:70px;">'
    f'</div>',
    unsafe_allow_html=True
)
st.sidebar.markdown(
    "<div style='background:#091e3a; color:white; padding:10px 12px; border-radius:8px; font-size:0.8rem; margin-bottom:12px; border-left:4px solid #00b4d8;'>"
    "<b>PILOTE RESPONSABLE RM :</b><br>Omar Dialmy<br>"
    "<span style='color:#7dd3fc; font-size:0.74rem;'>Référentiel SM ISPO • DMP_PR_02</span>"
    "</div>",
    unsafe_allow_html=True
)

menu = st.sidebar.radio(
    "Navigation Command Center ISPO",
    [
        "📊 Cockpit Exécutif ISPO (DPM_FI_02)",
        "🏗️ Infrastructures (DPM_FO_23)",
        "📡 Équipements, Vigie & VHF (FO_24/25)",
        "📦 Consommables & Pharmacie (FO_26/27)",
        "🚤 Consommation Pilotine (DPM_FO_28)",
        "🦺 Registre des EPIs (DPM_FO_29)",
        "✅ Checklists Achats & Maint. (CL_06/07)",
        "💰 Préparation du Budget (DPM_FO_30)",
        "🛡️ Journal d'Audit & Conformité ISPO"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("##### 📥 Livrables Officiels d'Audit")
st.sidebar.download_button(
    label="📘 Cartable Excel Officiel NWM (.xlsx)",
    data=generate_official_excel_pack("ALL"),
    file_name=f"Cartable_Officiel_ISPO_DPM_NWM_{date.today()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
    key="btn_dl_all_sidebar"
)
st.sidebar.download_button(
    label="🖨️ Rapport Exécutif Imprimable (.html)",
    data=generate_executive_html_report(logo_b64),
    file_name=f"Rapport_Executif_ISPO_DPM_NWM_{date.today()}.html",
    mime="text/html",
    use_container_width=True,
    key="btn_dl_html_sidebar"
)

with st.sidebar.expander("⚙️ Administration, Logo & Base SQL"):
    up_logo = st.file_uploader("Importer votre logo officiel (.png)", type=["png", "jpg", "jpeg"])
    if up_logo is not None:
        with open(LOGO_FILE, "wb") as f:
            f.write(up_logo.getbuffer())
        log_audit("SYSTÈME", "LOGO", "Mise à jour du logo officiel Nador West Med.")
        st.success("Logo officiel mis à jour !")
        st.rerun()

    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            st.download_button("⬇️ Sauvegarder la base (.db)", data=f, file_name=f"backup_dpm_nwm_{date.today()}.db", use_container_width=True, key="btn_backup_db")
    uploaded_db = st.file_uploader("Restaurer un fichier .db", type=["db", "sqlite"])
    if uploaded_db is not None:
        if st.button("⚠️ Confirmer la restauration", use_container_width=True):
            with open(DB_FILE, "wb") as f:
                f.write(uploaded_db.getbuffer())
            st.success("Base restaurée !")
            st.rerun()

# ==============================================================================
# BANNIÈRE COMMAND CENTER NADOR WEST MED
# ==============================================================================
now_utc = datetime.utcnow().strftime("%d/%m/%Y • %H:%M UTC")
st.markdown(f"""
<div class="top-status-bar">
    <div><span class="status-dot"></span><strong>SYSTÈME ERP DPM OPÉRATIONNEL</strong> • PORT NADOR WEST MED (ZONE PILOTAGE)</div>
    <div style="font-family: 'JetBrains Mono', monospace;">⏱️ {now_utc} | NORME : ISPO / ANP</div>
</div>
<div class="nwm-hero">
    <div class="nwm-hero-left">
        <div class="nwm-logo-card">
            <img src="data:image/png;base64,{logo_b64}" style="height: 56px;">
        </div>
        <div>
            <h1>Direction du Pilotage Maritime — Nador West Med</h1>
            <p>Système Intégré de Management des Ressources Matérielles • DMP_PR_02 | DPM_FI_02 | FO_23 à FO_30</p>
        </div>
    </div>
    <div class="nwm-pill-box">
        <div class="nwm-pill-title">Statut Conformité Audit</div>
        <div class="nwm-pill-val">✅ 100% PRÊT POUR AUDIT ISPO</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# MODULE 1 : COCKPIT EXÉCUTIF ISPO (DPM_FI_02)
# ==============================================================================
if menu == "📊 Cockpit Exécutif ISPO (DPM_FI_02)":
    df_infra = pd.read_sql_query("SELECT * FROM fo23_infrastructures", conn)
    df_equip = pd.read_sql_query("SELECT * FROM fo24_25_equipements", conn)
    df_conso = pd.read_sql_query("SELECT * FROM fo26_27_consommables", conn)
    df_pil = pd.read_sql_query("SELECT * FROM fo28_pilotine", conn)
    df_epi = pd.read_sql_query("SELECT * FROM fo29_epis", conn)
    df_b = pd.read_sql_query("SELECT * FROM fo30_budget_lignes", conn)
    df_cl = pd.read_sql_query("SELECT * FROM cl06_07_checklists", conn)

    aujourd_hui = pd.Timestamp(date.today())
    limite_30j = aujourd_hui + pd.Timedelta(days=30)

    nb_indispo_equip = len(df_equip[df_equip['util_etat'].isin(['À réparer', 'Hors service'])]) if not df_equip.empty else 0
    nb_indispo_infra = len(df_infra[df_infra['criticite'] == 'Critique - Urgent']) if not df_infra.empty else 0
    kpi_indispo = nb_indispo_equip + nb_indispo_infra

    alertes_epi_df = pd.DataFrame()
    if not df_epi.empty:
        df_epi['util_echeance_dt'] = pd.to_datetime(df_epi['util_echeance'], errors='coerce')
        alertes_epi_df = df_epi[df_epi['util_echeance_dt'] <= limite_30j]

    alertes_pharma_df = pd.DataFrame()
    df_pharma = df_conso[df_conso['categorie'] == 'Pharmacie (FO_27)'].copy() if not df_conso.empty else pd.DataFrame()
    if not df_pharma.empty:
        df_pharma['fin_date_expir_dt'] = pd.to_datetime(df_pharma['fin_date_expir'], errors='coerce')
        alertes_pharma_df = df_pharma[df_pharma['fin_date_expir_dt'] <= limite_30j]

    nb_alertes_exp = len(alertes_epi_df) + len(alertes_pharma_df)
    total_patrimoine = (df_equip['cout_estime'].sum() if not df_equip.empty else 0.0) + \
                       (df_epi['util_cout'].sum() + df_epi['stock_cout'].sum() if not df_epi.empty else 0.0) + \
                       (df_infra['reparations_cout'].sum() if not df_infra.empty else 0.0)
    unites_actives = int(df_equip['util_quantite'].sum()) if not df_equip.empty else 0
    unites_stock = int(df_equip['stock_quantite'].sum()) if not df_equip.empty else 0

    # Calcul du score de maturité ISPO (sur 100%)
    modules_remplis = sum([
        1 if not df_infra.empty else 0,
        1 if not df_equip.empty else 0,
        1 if not df_conso.empty else 0,
        1 if not df_pil.empty else 0,
        1 if not df_epi.empty else 0,
        1 if not df_b.empty else 0,
        1 if not df_cl.empty else 0
    ])
    penalite = (kpi_indispo * 10) + (nb_alertes_exp * 5)
    score_ispo = max(0, min(100, int((modules_remplis / 7.0) * 100) - penalite))

    # 4 Cartes Exécutives avec barre de progression
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        cls_c1 = "danger" if kpi_indispo > 0 else "success"
        color_bar1 = "#ef4444" if kpi_indispo > 0 else "#10b981"
        pct_dispo = 100 if kpi_indispo == 0 else max(50, 100 - kpi_indispo * 15)
        st.markdown(f"""
        <div class="exec-card {cls_c1}">
            <div class="exec-label"><span>DISPONIBILITÉ CRITIQUE (DPM_FI_02)</span><span>🎯 CIBLE : 100%</span></div>
            <div class="exec-val">{pct_dispo}% <span style="font-size:0.9rem; font-weight:600; color:#475569;">({kpi_indispo} anomalie)</span></div>
            <div class="exec-footer">Équipements VHF, Vigie & Pilotines opérationnels</div>
            <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{pct_dispo}%; background:{color_bar1};"></div></div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="exec-card teal">
            <div class="exec-label"><span>DOTATIONS ACTIVES (FO_24 / FO_25)</span><span>📡 {len(df_equip)} RÉF.</span></div>
            <div class="exec-val">{unites_actives} <span style="font-size:0.9rem; font-weight:600; color:#0097a7;">+{unites_stock} en réserve</span></div>
            <div class="exec-footer">Inclut les 10 VHF ATEX Motorola & 15 batteries</div>
            <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:92%; background:#0097a7;"></div></div>
        </div>""", unsafe_allow_html=True)

    with c3:
        cls_c3 = "danger" if nb_alertes_exp > 0 else "success"
        color_bar3 = "#ef4444" if nb_alertes_exp > 0 else "#10b981"
        st.markdown(f"""
        <div class="exec-card {cls_c3}">
            <div class="exec-label"><span>VEILLE PÉREMPTION (&lt; 30 JOURS)</span><span>🛡️ SÉCURITÉ</span></div>
            <div class="exec-val">{nb_alertes_exp} <span style="font-size:0.9rem; font-weight:600; color:#475569;">alerte(s) active(s)</span></div>
            <div class="exec-footer">Surveillance automatique EPI (FO_29) & Pharmacie (FO_27)</div>
            <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:100%; background:{color_bar3};"></div></div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="exec-card gold">
            <div class="exec-label"><span>PATRIMOINE MATÉRIEL VALORISÉ</span><span>💰 AUDIT FINANCIER</span></div>
            <div class="exec-val">{total_patrimoine:,.0f} <span style="font-size:0.95rem; font-weight:700; color:#b45309;">MAD</span></div>
            <div class="exec-footer">Consolidation temps réel FO_23, FO_24/25 & FO_29</div>
            <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:100%; background:#d4af37;"></div></div>
        </div>""", unsafe_allow_html=True)

    # Rangée de Graphiques Exécutifs (Jauge ISPO + Sunburst Patrimoine + Courbe Pilotine)
    g1, g2, g3 = st.columns([1.05, 1.35, 1.4])

    with g1:
        st.markdown("##### 🎯 Indice de Conformité SM ISPO")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score_ispo,
            number={'suffix': "%", 'font': {'size': 36, 'color': '#091e3a'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#091e3a"},
                'bar': {'color': "#0097a7"},
                'bgcolor': "white",
                'borderwidth': 1,
                'bordercolor': "#cbd5e1",
                'steps': [
                    {'range': [0, 60], 'color': '#fee2e2'},
                    {'range': [60, 85], 'color': '#fef3c7'},
                    {'range': [85, 100], 'color': '#d1fae5'}
                ],
                'threshold': {'line': {'color': "#091e3a", 'width': 4}, 'thickness': 0.75, 'value': 95}
            }
        ))
        fig_gauge.update_layout(height=280, margin=dict(t=20, b=15, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_gauge, use_container_width=True)

    with g2:
        st.markdown("##### 🧭 Cartographie du Patrimoine par Classe (`DMP_PR_02`)")
        if not df_equip.empty and df_equip['cout_estime'].sum() > 0:
            df_sun = df_equip[df_equip['cout_estime'] > 0].copy()
            df_sun['article_court'] = df_sun['article'].str.slice(0, 28)
            fig_sun = px.sunburst(
                df_sun,
                path=['classe', 'article_court'],
                values='cout_estime',
                color='classe',
                color_discrete_sequence=['#091e3a', '#0097a7', '#1e4e8c', '#d4af37', '#0284c7']
            )
            fig_sun.update_layout(height=280, margin=dict(t=10, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_sun, use_container_width=True)
        else:
            st.info("Aucune donnée valorisée.")

    with g3:
        st.markdown("##### 🚤 Courbe de Consommation Pilotine (`DPM_FO_28`)")
        if not df_pil.empty:
            df_pil['Gasoil Consommé (L)'] = df_pil['debut_gasoil'] + df_pil['livre_gasoil'] - df_pil['fin_gasoil']
            df_pil['Lubrifiant Consommé (L)'] = df_pil['debut_lubrif'] + df_pil['livre_lubrif'] - df_pil['fin_lubrif']
            fig_pil = go.Figure()
            fig_pil.add_trace(go.Bar(
                x=df_pil['fin_date'], y=df_pil['Gasoil Consommé (L)'],
                name="Gasoil (L)", marker_color='#091e3a'
            ))
            fig_pil.add_trace(go.Scatter(
                x=df_pil['fin_date'], y=df_pil['Lubrifiant Consommé (L)'],
                name="Lubrifiant (L)", mode='lines+markers',
                line=dict(color='#00b4d8', width=3), yaxis='y2'
            ))
            fig_pil.update_layout(
                height=280,
                margin=dict(t=15, b=20, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(title="Gasoil (L)"),
                yaxis2=dict(title="Lubrifiant (L)", overlaying='y', side='right'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_pil, use_container_width=True)
        else:
            st.info("Aucun relevé pilotine.")

    # Inspecteur de Fiche de Vie Individuelle & Matrice de Conformité
    st.markdown("---")
    col_insp, col_mat = st.columns([1.2, 1.3])

    with col_insp:
        st.markdown("##### 🔍 Inspecteur de Fiche de Vie & Certificat de Garantie")
        if not df_equip.empty:
            sel_eq_id = st.selectbox(
                "Sélectionner un équipement pour inspecter sa fiche de vie officielle",
                df_equip['id'].tolist(),
                format_func=lambda x: f"[{df_equip[df_equip['id']==x]['reference_serie'].values[0]}] {df_equip[df_equip['id']==x]['article'].values[0]}"
            )
            eq_row = df_equip[df_equip['id'] == sel_eq_id].iloc[0]
            dt_rec = parse_date_safe(eq_row['date_reception'])
            dt_gar = parse_date_safe(eq_row['echeance_garantie'])
            jours_restants = (dt_gar - date.today()).days
            pct_gar = max(0, min(100, int((jours_restants / 730.0) * 100)))

            st.markdown(f"""
            <div class="asset-id-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span class="mono-badge">S/N & RÉF : {eq_row['reference_serie']}</span>
                    <span style="background:#10b981; color:white; padding:2px 10px; border-radius:12px; font-size:0.75rem; font-weight:700;">ÉTAT : {eq_row['util_etat'].upper()}</span>
                </div>
                <div style="font-size:1.05rem; font-weight:800; color:#ffffff; margin-bottom:6px;">{eq_row['article']}</div>
                <div style="font-size:0.83rem; color:#cbd5e1; margin-bottom:10px;">
                    <b>Classe :</b> {eq_row['classe']} | <b>Affectation :</b> {eq_row['util_emplacement']}<br>
                    <b>Valeur d'acquisition :</b> {float(eq_row['cout_estime']):,.2f} MAD | <b>Qté Active :</b> {eq_row['util_quantite']} (Stock : {eq_row['stock_quantite']})<br>
                    <b>Réception :</b> {eq_row['date_reception']} | <b>Fin de Garantie :</b> {eq_row['echeance_garantie']} ({jours_restants} jours restants)
                </div>
                <div style="font-size:0.76rem; color:#90e0ef;">Traçabilité : {eq_row['observations']}</div>
                <div class="progress-bar-bg" style="background:rgba(255,255,255,0.2);"><div class="progress-bar-fill" style="width:{pct_gar}%; background:#00b4d8;"></div></div>
            </div>
            """, unsafe_allow_html=True)

    with col_mat:
        st.markdown("##### 📋 État de Complétude du Cartable Réglementaire ISPO")
        recap_forms = pd.DataFrame([
            {"Code ISPO": "DPM_FO_23", "Intitulé Officiel": "Registre des Infrastructures de la DPM", "Enregistrements": len(df_infra), "Statut": "✅ Conforme"},
            {"Code ISPO": "DPM_FO_24 / 25", "Intitulé Officiel": "Registres Ameublement, Vigie & Radios VHF", "Enregistrements": len(df_equip), "Statut": "✅ Conforme"},
            {"Code ISPO": "DPM_FO_26 / 27", "Intitulé Officiel": "États Consommations Générales & Pharmacie", "Enregistrements": len(df_conso), "Statut": "✅ Conforme"},
            {"Code ISPO": "DPM_FO_28", "Intitulé Officiel": "Registre de Consommation de la Pilotine", "Enregistrements": len(df_pil), "Statut": "✅ Conforme"},
            {"Code ISPO": "DPM_FO_29", "Intitulé Officiel": "Registre des Équipements de Protection (EPI)", "Enregistrements": len(df_epi), "Statut": "✅ Conforme"},
            {"Code ISPO": "DPM_CL_06 / 07", "Intitulé Officiel": "Checklists Achats & Maintenance Critique", "Enregistrements": len(df_cl), "Statut": "✅ Conforme"},
            {"Code ISPO": "DPM_FO_30", "Intitulé Officiel": "Formulaire de Préparation du Budget DPM", "Enregistrements": len(df_b), "Statut": "✅ Conforme"}
        ])
        st.dataframe(recap_forms, use_container_width=True, hide_index=True)

# ==============================================================================
# MODULE 2 : INFRASTRUCTURES PERMANENTES (DPM_FO_23)
# ==============================================================================
elif menu == "🏗️ Infrastructures (DPM_FO_23)":
    st.markdown('<div class="module-banner"><h3>🏗️ DPM_FO_23 — Le Registre des Infrastructures de La DPM</h3><span>Réf. Normative : DMP_PR_02</span></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 Registre Interactif & Export", "➕ Nouvelle Infrastructure", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_infra = pd.read_sql_query("SELECT * FROM fo23_infrastructures", conn)
        edited_infra = st.data_editor(
            df_infra,
            use_container_width=True,
            disabled=["id"],
            num_rows="fixed",
            key="ed_fo23",
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "infrastructure": st.column_config.TextColumn("Infrastructure", width="medium"),
                "reparations_cout": st.column_config.NumberColumn("Coût Réparations (MAD)", format="%.2f MAD"),
                "criticite": st.column_config.SelectboxColumn("Criticité ISPO", options=["Normal", "Moyen", "Critique - Urgent"])
            }
        )
        c_btn1, c_btn2 = st.columns([1, 2])
        if c_btn1.button("💾 Sauvegarder l'édition rapide (FO_23)", key="save_fast_fo23"):
            for _, r in edited_infra.iterrows():
                c.execute('''UPDATE fo23_infrastructures SET
                    infrastructure=?, besoins_reparation=?, reparations_commentaire=?,
                    reparations_cout=?, criticite=?, date_mise_a_jour=?, observations=? WHERE id=?''',
                    (r['infrastructure'], r['besoins_reparation'], r['reparations_commentaire'], float(r['reparations_cout'] or 0), r['criticite'], str(r['date_mise_a_jour']), r['observations'], int(r['id'])))
            conn.commit()
            log_audit("DPM_FO_23", "ÉDITION RAPIDE", "Mise à jour directe du registre des infrastructures.")
            st.success("Tableau mis à jour avec succès !")
            st.rerun()
        c_btn2.download_button(
            "📥 Exporter DPM_FO_23 Officiel avec Logo NWM (.xlsx)",
            data=generate_official_excel_pack("FO_23"),
            file_name=f"DPM_FO_23_Infrastructures_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_fo23"
        )

    with tab2:
        with st.form("add_fo23"):
            c1, c2 = st.columns(2)
            with c1:
                infra = st.text_input("Infrastructure (ex: Locaux Station Pilotage, Vigie, Quai Pilotine)")
                besoins = st.text_area("Besoins de réparation")
                criticite = st.selectbox("Niveau de Criticité ISPO", ["Normal", "Moyen", "Critique - Urgent"])
            with c2:
                rep_comm = st.text_area("Les réparations réalisées — Commentaire")
                rep_cout = st.number_input("Les réparations réalisées — Coût (MAD)", min_value=0.0, step=100.0)
                dt_maj = st.date_input("Date de relevé", date.today())
                obs = st.text_input("Observations")
            if st.form_submit_button("➕ Enregistrer dans DPM_FO_23"):
                c.execute('''INSERT INTO fo23_infrastructures (
                    infrastructure, besoins_reparation, reparations_commentaire,
                    reparations_cout, criticite, date_mise_a_jour, observations
                ) VALUES (?,?,?,?,?,?,?)''', (infra, besoins, rep_comm, rep_cout, criticite, str(dt_maj), obs))
                conn.commit()
                log_audit("DPM_FO_23", "AJOUT", f"Nouvelle infrastructure : {infra}")
                st.success("Infrastructure ajoutée !")
                st.rerun()

    with tab3:
        df_infra = pd.read_sql_query("SELECT * FROM fo23_infrastructures", conn)
        if not df_infra.empty:
            id_sel = st.selectbox("Sélectionner la ligne à modifier ou supprimer", df_infra['id'].tolist(), format_func=lambda x: f"ID #{x} — {df_infra[df_infra['id']==x]['infrastructure'].values[0]}")
            row = df_infra[df_infra['id'] == id_sel].iloc[0]
            with st.form("edit_fo23"):
                c1, c2 = st.columns(2)
                crit_list = ["Normal", "Moyen", "Critique - Urgent"]
                with c1:
                    u_infra = st.text_input("Infrastructure", value=str(row['infrastructure']))
                    u_besoins = st.text_area("Besoins de réparation", value=str(row['besoins_reparation']))
                    u_crit = st.selectbox("Criticité", crit_list, index=crit_list.index(row['criticite']) if row['criticite'] in crit_list else 0)
                with c2:
                    u_comm = st.text_area("Réparations réalisées — Commentaire", value=str(row['reparations_commentaire']))
                    u_cout = st.number_input("Réparations réalisées — Coût (MAD)", min_value=0.0, value=float(row['reparations_cout']))
                    u_dt = st.date_input("Date de relevé", value=parse_date_safe(row['date_mise_a_jour']))
                    u_obs = st.text_input("Observations", value=str(row['observations']))
                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Mettre à jour tous les paramètres"):
                    c.execute('''UPDATE fo23_infrastructures SET
                        infrastructure=?, besoins_reparation=?, reparations_commentaire=?,
                        reparations_cout=?, criticite=?, date_mise_a_jour=?, observations=? WHERE id=?''',
                        (u_infra, u_besoins, u_comm, u_cout, u_crit, str(u_dt), u_obs, id_sel))
                    conn.commit()
                    log_audit("DPM_FO_23", "MODIFICATION", f"Modification ID #{id_sel} ({u_infra})")
                    st.success("Mis à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo23_infrastructures WHERE id=?", (id_sel,))
                    conn.commit()
                    log_audit("DPM_FO_23", "SUPPRESSION", f"Suppression ID #{id_sel}")
                    st.warning("Supprimé.")
                    st.rerun()
        else:
            st.info("Aucun enregistrement disponible.")

# ==============================================================================
# MODULE 3 : ÉQUIPEMENTS, VIGIE, AMEUBLEMENT & VHF (DPM_FO_24 / DPM_FO_25)
# ==============================================================================
elif menu == "📡 Équipements, Vigie & VHF (FO_24/25)":
    st.markdown('<div class="module-banner"><h3>📡 DPM_FO_24 & DPM_FO_25 — Équipements, Vigie, Ameublement & VHF ATEX</h3><span>Inventaire & Garanties</span></div>', unsafe_allow_html=True)
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

    tab1, tab2, tab3 = st.tabs(["📋 Registre, Recherche & Exports Officiels", "➕ Nouvel Équipement", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_eq = pd.read_sql_query("SELECT * FROM fo24_25_equipements", conn)
        f1, f2 = st.columns([2, 1])
        filtre_classe = f1.multiselect("Filtrer par Classe (`DMP_PR_02`)", options=classes_pr02, default=classes_pr02)
        search_q = f2.text_input("🔍 Rechercher (N° de Série, Article, BC...)", "")

        df_filtered = df_eq[df_eq['classe'].isin(filtre_classe)] if not df_eq.empty else df_eq
        if search_q.strip() and not df_filtered.empty:
            mask = df_filtered.astype(str).apply(lambda x: x.str.contains(search_q, case=False, na=False)).any(axis=1)
            df_filtered = df_filtered[mask]

        edited_eq = st.data_editor(
            df_filtered,
            use_container_width=True,
            disabled=["id"],
            num_rows="fixed",
            key="ed_fo24_25",
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "cout_estime": st.column_config.NumberColumn("Coût Estimé (MAD)", format="%.2f MAD"),
                "util_etat": st.column_config.SelectboxColumn("État", options=etats_list),
                "util_quantite": st.column_config.ProgressColumn("Qté Active", min_value=0, max_value=15, format="%d u.")
            }
        )

        if st.button("💾 Sauvegarder l'édition rapide du tableau", key="save_fast_fo24"):
            for _, r in edited_eq.iterrows():
                c.execute('''UPDATE fo24_25_equipements SET
                    classe=?, article=?, reference_serie=?, cout_estime=?,
                    util_etat=?, util_quantite=?, util_emplacement=?,
                    stock_quantite=?, stock_localisation=?,
                    besoin_achat=?, besoin_reparation=?,
                    date_reception=?, echeance_garantie=?, observations=? WHERE id=?''', (
                    r['classe'], r['article'], r['reference_serie'], float(r['cout_estime'] or 0),
                    r['util_etat'], int(r['util_quantite'] or 0), r['util_emplacement'],
                    int(r['stock_quantite'] or 0), r['stock_localisation'],
                    r['besoin_achat'], r['besoin_reparation'],
                    str(r['date_reception']), str(r['echeance_garantie']), r['observations'], int(r['id'])
                ))
            conn.commit()
            log_audit("DPM_FO_24/25", "ÉDITION RAPIDE", "Mise à jour directe de la grille des équipements.")
            st.success("Modifications enregistrées !")
            st.rerun()

        st.markdown("##### 📥 Téléchargements au Format Officiel Nador West Med (avec Logo)")
        ex1, ex2, ex3 = st.columns(3)
        ex1.download_button(
            "📥 Exporter DPM_FO_24 (Ameublement Officiel)",
            data=generate_official_excel_pack("FO_24"),
            file_name=f"DPM_FO_24_Ameublement_{date.today()}.xlsx",
            use_container_width=True,
            key="dl_fo24"
        )
        ex2.download_button(
            "📥 Exporter DPM_FO_25 (Vigie Officiel)",
            data=generate_official_excel_pack("FO_25"),
            file_name=f"DPM_FO_25_Vigie_{date.today()}.xlsx",
            use_container_width=True,
            key="dl_fo25"
        )
        ex3.download_button(
            "📥 Exporter Registre Complet (VHF + Toutes Classes)",
            data=generate_official_excel_pack("FO_24_25_ALL"),
            file_name=f"DPM_Registre_Equipements_Complet_{date.today()}.xlsx",
            use_container_width=True,
            key="dl_fo24_25_all"
        )

    with tab2:
        with st.form("add_fo24_25"):
            c1, c2, c3 = st.columns(3)
            with c1:
                classe = st.selectbox("Classe de Ressource (`DMP_PR_02`)", classes_pr02)
                article = st.text_input("Article / Désignation")
                ref_serie = st.text_input("Numéro de Série / Référence")
                cout_est = st.number_input("Coût Estimé (MAD)", min_value=0.0, step=100.0)
            with c2:
                st.markdown("**En Utilisation**")
                u_etat = st.selectbox("Etat (En utilisation)", etats_list)
                u_qte = st.number_input("Quantité (En utilisation)", min_value=0, value=1)
                u_emp = st.text_input("Emplacement", value="Station de Pilotage")
                st.markdown("**En Stock**")
                s_qte = st.number_input("Quantité (En stock)", min_value=0, value=0)
                s_loc = st.text_input("Localisation", value="Magasin DPM")
            with c3:
                st.markdown("**Besoins & Garantie**")
                b_achat = st.text_input("Besoins — Achat", value="Non")
                b_repa = st.text_input("Besoins — Réparation", value="Non")
                dt_rec = st.date_input("Date de Réception", date.today())
                dt_gar = st.date_input("Échéance Garantie / Révision", date.today() + timedelta(days=730))
                obs = st.text_area("Observations")

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
                log_audit("DPM_FO_24/25", "AJOUT", f"Ajout équipement : {article} ({ref_serie})")
                st.success("Équipement enregistré !")
                st.rerun()

    with tab3:
        df_eq = pd.read_sql_query("SELECT * FROM fo24_25_equipements", conn)
        if not df_eq.empty:
            id_sel = st.selectbox(
                "Sélectionner l'équipement à modifier ou supprimer",
                df_eq['id'].tolist(),
                format_func=lambda x: f"ID #{x} — [{df_eq[df_eq['id']==x]['classe'].values[0]}] {df_eq[df_eq['id']==x]['article'].values[0]}"
            )
            row = df_eq[df_eq['id'] == id_sel].iloc[0]
            with st.form("edit_fo24_25"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    u_classe = st.selectbox("Classe", classes_pr02, index=classes_pr02.index(row['classe']) if row['classe'] in classes_pr02 else 0)
                    u_article = st.text_input("Article", value=str(row['article']))
                    u_ref = st.text_input("Numéro de Série / Réf.", value=str(row['reference_serie']))
                    u_cout = st.number_input("Coût Estimé (MAD)", min_value=0.0, value=float(row['cout_estime']))
                with c2:
                    u_etat = st.selectbox("Etat (En utilisation)", etats_list, index=etats_list.index(row['util_etat']) if row['util_etat'] in etats_list else 0)
                    u_qte = st.number_input("Quantité (En utilisation)", min_value=0, value=int(row['util_quantite']))
                    u_emp = st.text_input("Emplacement", value=str(row['util_emplacement']))
                    s_qte = st.number_input("Quantité (En stock)", min_value=0, value=int(row['stock_quantite']))
                    s_loc = st.text_input("Localisation stock", value=str(row['stock_localisation']))
                with c3:
                    b_achat = st.text_input("Besoins — Achat", value=str(row['besoin_achat']))
                    b_repa = st.text_input("Besoins — Réparation", value=str(row['besoin_reparation']))
                    dt_rec = st.date_input("Date de Réception", value=parse_date_safe(row['date_reception']))
                    dt_gar = st.date_input("Échéance Garantie", value=parse_date_safe(row['echeance_garantie']))
                    obs = st.text_area("Observations", value=str(row['observations']))

                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Enregistrer toutes les modifications"):
                    c.execute('''UPDATE fo24_25_equipements SET
                        classe=?, article=?, reference_serie=?, cout_estime=?,
                        util_etat=?, util_quantite=?, util_emplacement=?,
                        stock_quantite=?, stock_localisation=?,
                        besoin_achat=?, besoin_reparation=?,
                        date_reception=?, echeance_garantie=?, observations=? WHERE id=?''', (
                        u_classe, u_article, u_ref, u_cout,
                        u_etat, u_qte, u_emp, s_qte, s_loc,
                        b_achat, b_repa, str(dt_rec), str(dt_gar), obs, id_sel
                    ))
                    conn.commit()
                    log_audit("DPM_FO_24/25", "MODIFICATION", f"Modification ID #{id_sel} ({u_article})")
                    st.success("Tous les paramètres ont été mis à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo24_25_equipements WHERE id=?", (id_sel,))
                    conn.commit()
                    log_audit("DPM_FO_24/25", "SUPPRESSION", f"Suppression équipement ID #{id_sel}")
                    st.warning("Équipement supprimé.")
                    st.rerun()
        else:
            st.info("Aucun équipement enregistré.")

# ==============================================================================
# MODULE 4 : CONSOMMABLES GÉNÉRAUX & PHARMACIE (DPM_FO_26 & DPM_FO_27)
# ==============================================================================
elif menu == "📦 Consommables & Pharmacie (FO_26/27)":
    st.markdown('<div class="module-banner"><h3>📦 DPM_FO_26 & DPM_FO_27 — État des Consommations Générales & Pharmaceutiques</h3><span>Suivi des Stocks & Péremptions</span></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 États, Édition Rapide & Exports (FO_26 / FO_27)", "➕ Nouvel Article", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_c = pd.read_sql_query("SELECT * FROM fo26_27_consommables", conn)
        if not df_c.empty:
            edited_c = st.data_editor(df_c, use_container_width=True, disabled=["id"], num_rows="fixed", key="ed_fo26_27")
            if st.button("💾 Sauvegarder l'édition rapide (FO_26/27)", key="save_fast_fo26"):
                for _, r in edited_c.iterrows():
                    c.execute('''UPDATE fo26_27_consommables SET
                        categorie=?, article=?, emplacement=?,
                        debut_qte=?, debut_prix_unit=?, debut_date_expir=?,
                        livre_qte=?, livre_prix_unit=?,
                        fin_qte=?, fin_prix_unit=?, fin_date_expir=?, observations=? WHERE id=?''', (
                        r['categorie'], r['article'], r['emplacement'],
                        int(r['debut_qte'] or 0), float(r['debut_prix_unit'] or 0), str(r['debut_date_expir']),
                        int(r['livre_qte'] or 0), float(r['livre_prix_unit'] or 0),
                        int(r['fin_qte'] or 0), float(r['fin_prix_unit'] or 0), str(r['fin_date_expir']), r['observations'], int(r['id'])
                    ))
                conn.commit()
                log_audit("DPM_FO_26/27", "ÉDITION RAPIDE", "Mise à jour des quantités consommables/pharmacie.")
                st.success("Tableau mis à jour !")
                st.rerun()

            df_calc = df_c.copy()
            df_calc['Coût Début'] = df_calc['debut_qte'] * df_calc['debut_prix_unit']
            df_calc['Coût Livré'] = df_calc['livre_qte'] * df_calc['livre_prix_unit']
            df_calc['Coût Fin'] = df_calc['fin_qte'] * df_calc['fin_prix_unit']
            df_calc['Cout des Consommations'] = (df_calc['Coût Début'] + df_calc['Coût Livré']) - df_calc['Coût Fin']
            st.metric("Coût Total des Consommations de la Période", f"{df_calc['Cout des Consommations'].sum():,.2f} MAD")
        else:
            st.info("Aucun article enregistré.")

        ex1, ex2 = st.columns(2)
        ex1.download_button(
            "📥 Exporter DPM_FO_26 Officiel avec Logo NWM",
            data=generate_official_excel_pack("FO_26"),
            file_name=f"DPM_FO_26_Consommations_Generales_{date.today()}.xlsx",
            use_container_width=True,
            key="dl_fo26"
        )
        ex2.download_button(
            "📥 Exporter DPM_FO_27 Officiel avec Logo NWM",
            data=generate_official_excel_pack("FO_27"),
            file_name=f"DPM_FO_27_Consommations_Pharmaceutiques_{date.today()}.xlsx",
            use_container_width=True,
            key="dl_fo27"
        )

    with tab2:
        with st.form("add_fo26_27"):
            c1, c2, c3 = st.columns(3)
            with c1:
                cat = st.selectbox("Formulaire Officiel", ["Consommations Générales (FO_26)", "Pharmacie (FO_27)"])
                art = st.text_input("Article")
                emp = st.text_input("Emplacement", value="Station de Pilotage")
                obs = st.text_input("Observation")
            with c2:
                st.markdown("**Existant début du période & Livré**")
                d_qte = st.number_input("Qtité Début", min_value=0, value=0)
                d_pu = st.number_input("Prix unit Début (MAD)", min_value=0.0, value=0.0)
                d_exp = st.date_input("Date Expir Début (Si FO_27)", date.today() + timedelta(days=365))
                l_qte = st.number_input("Qtité Livrée", min_value=0, value=0)
                l_pu = st.number_input("Prix unit Livré (MAD)", min_value=0.0, value=0.0)
            with c3:
                st.markdown("**Existant Fin de la période**")
                f_qte = st.number_input("Qtité Fin", min_value=0, value=0)
                f_pu = st.number_input("Prix unit Fin (MAD)", min_value=0.0, value=0.0)
                f_exp = st.date_input("Date Expir Fin (Si FO_27)", date.today() + timedelta(days=365))

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
                log_audit("DPM_FO_26/27", "AJOUT", f"Ajout consommable/pharmacie : {art}")
                st.success("Enregistré !")
                st.rerun()

    with tab3:
        df_c = pd.read_sql_query("SELECT * FROM fo26_27_consommables", conn)
        if not df_c.empty:
            id_sel = st.selectbox("Sélectionner l'ID à modifier ou supprimer", df_c['id'].tolist(), format_func=lambda x: f"ID #{x} — [{df_c[df_c['id']==x]['categorie'].values[0]}] {df_c[df_c['id']==x]['article'].values[0]}")
            row = df_c[df_c['id'] == id_sel].iloc[0]
            with st.form("edit_fo26_27"):
                c1, c2, c3 = st.columns(3)
                cats = ["Consommations Générales (FO_26)", "Pharmacie (FO_27)"]
                with c1:
                    u_cat = st.selectbox("Formulaire", cats, index=cats.index(row['categorie']) if row['categorie'] in cats else 0)
                    u_art = st.text_input("Article", value=str(row['article']))
                    u_emp = st.text_input("Emplacement", value=str(row['emplacement']))
                    u_obs = st.text_input("Observation", value=str(row['observations']))
                with c2:
                    u_dqte = st.number_input("Qtité Début", min_value=0, value=int(row['debut_qte']))
                    u_dpu = st.number_input("Prix unit Début", min_value=0.0, value=float(row['debut_prix_unit']))
                    u_dexp = st.date_input("Date Expir Début", value=parse_date_safe(row['debut_date_expir']))
                    u_lqte = st.number_input("Qtité Livrée", min_value=0, value=int(row['livre_qte']))
                    u_lpu = st.number_input("Prix unit Livré", min_value=0.0, value=float(row['livre_prix_unit']))
                with c3:
                    u_fqte = st.number_input("Qtité Fin", min_value=0, value=int(row['fin_qte']))
                    u_fpu = st.number_input("Prix unit Fin", min_value=0.0, value=float(row['fin_prix_unit']))
                    u_fexp = st.date_input("Date Expir Fin", value=parse_date_safe(row['fin_date_expir']))
                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Enregistrer toutes les modifications"):
                    c.execute('''UPDATE fo26_27_consommables SET
                        categorie=?, article=?, emplacement=?,
                        debut_qte=?, debut_prix_unit=?, debut_date_expir=?,
                        livre_qte=?, livre_prix_unit=?,
                        fin_qte=?, fin_prix_unit=?, fin_date_expir=?, observations=? WHERE id=?''', (
                        u_cat, u_art, u_emp, u_dqte, u_dpu, str(u_dexp), u_lqte, u_lpu, u_fqte, u_fpu, str(u_fexp), u_obs, id_sel
                    ))
                    conn.commit()
                    log_audit("DPM_FO_26/27", "MODIFICATION", f"Modification ID #{id_sel} ({u_art})")
                    st.success("Mis à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo26_27_consommables WHERE id=?", (id_sel,))
                    conn.commit()
                    log_audit("DPM_FO_26/27", "SUPPRESSION", f"Suppression ID #{id_sel}")
                    st.warning("Supprimé.")
                    st.rerun()
        else:
            st.info("Aucun article à modifier.")

# ==============================================================================
# MODULE 5 : REGISTRE DE LA CONSOMMATION DE LA PILOTINE (DPM_FO_28)
# ==============================================================================
elif menu == "🚤 Consommation Pilotine (DPM_FO_28)":
    st.markdown('<div class="module-banner"><h3>🚤 DPM_FO_28 — Le Registre de La Consommation de la Pilotine</h3><span>Suivi Soutes Gasoil & Lubrifiants</span></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 Registre, Édition Rapide & Export FO_28", "➕ Nouveau Relevé", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_p = pd.read_sql_query("SELECT * FROM fo28_pilotine", conn)
        if not df_p.empty:
            edited_p = st.data_editor(df_p, use_container_width=True, disabled=["id"], num_rows="fixed", key="ed_fo28")
            if st.button("💾 Sauvegarder l'édition rapide (FO_28)", key="save_fast_fo28"):
                for _, r in edited_p.iterrows():
                    c.execute('''UPDATE fo28_pilotine SET
                        nom_pilotine=?, debut_date=?, debut_gasoil=?, debut_lubrif=?,
                        livre_date=?, livre_gasoil=?, livre_lubrif=?,
                        fin_date=?, fin_gasoil=?, fin_lubrif=?, observations=? WHERE id=?''', (
                        r['nom_pilotine'], str(r['debut_date']), float(r['debut_gasoil'] or 0), float(r['debut_lubrif'] or 0),
                        str(r['livre_date']), float(r['livre_gasoil'] or 0), float(r['livre_lubrif'] or 0),
                        str(r['fin_date']), float(r['fin_gasoil'] or 0), float(r['fin_lubrif'] or 0), r['observations'], int(r['id'])
                    ))
                conn.commit()
                log_audit("DPM_FO_28", "ÉDITION RAPIDE", "Mise à jour des relevés de soutes pilotine.")
                st.success("Relevés mis à jour !")
                st.rerun()

            df_p['Gasoil Consommé (L)'] = df_p['debut_gasoil'] + df_p['livre_gasoil'] - df_p['fin_gasoil']
            df_p['Lubrif Consommé (L)'] = df_p['debut_lubrif'] + df_p['livre_lubrif'] - df_p['fin_lubrif']
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Consommation Totale Gasoil", f"{df_p['Gasoil Consommé (L)'].sum():,.1f} L")
            k2.metric("Consommation Moyenne Gasoil", f"{df_p['Gasoil Consommé (L)'].mean():,.1f} L")
            k3.metric("Consommation Totale Lubrifiant", f"{df_p['Lubrif Consommé (L)'].sum():,.1f} L")
            k4.metric("Consommation Moyenne Lubrifiant", f"{df_p['Lubrif Consommé (L)'].mean():,.1f} L")
        else:
            st.info("Aucun relevé enregistré.")

        st.download_button(
            "📥 Exporter DPM_FO_28 Officiel avec Logo NWM (.xlsx)",
            data=generate_official_excel_pack("FO_28"),
            file_name=f"DPM_FO_28_Consommation_Pilotine_{date.today()}.xlsx",
            key="dl_fo28"
        )

    with tab2:
        with st.form("add_fo28"):
            nom_pil = st.text_input("Nom de la Pilotine", value="Pilotine NWM 1")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Existant début du période**")
                d_dt = st.date_input("Date Début", date.today() - timedelta(days=30))
                d_gas = st.number_input("Gasoil Début (L)", min_value=0.0, value=0.0)
                d_lub = st.number_input("Lubrif Début (L)", min_value=0.0, value=0.0)
            with c2:
                st.markdown("**Livré durant la période**")
                l_dt = st.date_input("Date Livré", date.today() - timedelta(days=15))
                l_gas = st.number_input("Gasoil Livré (L)", min_value=0.0, value=0.0)
                l_lub = st.number_input("Lubrif Livré (L)", min_value=0.0, value=0.0)
            with c3:
                st.markdown("**Existant Fin de la période**")
                f_dt = st.date_input("Date Fin", date.today())
                f_gas = st.number_input("Gasoil Fin (L)", min_value=0.0, value=0.0)
                f_lub = st.number_input("Lubrif Fin (L)", min_value=0.0, value=0.0)
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
                log_audit("DPM_FO_28", "AJOUT", f"Nouveau relevé soutes : {nom_pil} ({f_dt})")
                st.success("Relevé enregistré !")
                st.rerun()

    with tab3:
        df_p = pd.read_sql_query("SELECT * FROM fo28_pilotine", conn)
        if not df_p.empty:
            id_sel = st.selectbox("Sélectionner le relevé à modifier ou supprimer", df_p['id'].tolist(), format_func=lambda x: f"ID #{x} — {df_p[df_p['id']==x]['nom_pilotine'].values[0]} ({df_p[df_p['id']==x]['fin_date'].values[0]})")
            row = df_p[df_p['id'] == id_sel].iloc[0]
            with st.form("edit_fo28"):
                u_nom = st.text_input("Pilotine", value=str(row['nom_pilotine']))
                c1, c2, c3 = st.columns(3)
                with c1:
                    u_ddt = st.date_input("Date Début", value=parse_date_safe(row['debut_date']))
                    u_dgas = st.number_input("Gasoil Début", min_value=0.0, value=float(row['debut_gasoil']))
                    u_dlub = st.number_input("Lubrif Début", min_value=0.0, value=float(row['debut_lubrif']))
                with c2:
                    u_ldt = st.date_input("Date Livré", value=parse_date_safe(row['livre_date']))
                    u_lgas = st.number_input("Gasoil Livré", min_value=0.0, value=float(row['livre_gasoil']))
                    u_llub = st.number_input("Lubrif Livré", min_value=0.0, value=float(row['livre_lubrif']))
                with c3:
                    u_fdt = st.date_input("Date Fin", value=parse_date_safe(row['fin_date']))
                    u_fgas = st.number_input("Gasoil Fin", min_value=0.0, value=float(row['fin_gasoil']))
                    u_flub = st.number_input("Lubrif Fin", min_value=0.0, value=float(row['fin_lubrif']))
                u_obs = st.text_input("Observation", value=str(row['observations']))
                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Enregistrer toutes les modifications"):
                    c.execute('''UPDATE fo28_pilotine SET
                        nom_pilotine=?, debut_date=?, debut_gasoil=?, debut_lubrif=?,
                        livre_date=?, livre_gasoil=?, livre_lubrif=?,
                        fin_date=?, fin_gasoil=?, fin_lubrif=?, observations=? WHERE id=?''', (
                        u_nom, str(u_ddt), u_dgas, u_dlub, str(u_ldt), u_lgas, u_llub, str(u_fdt), u_fgas, u_flub, u_obs, id_sel
                    ))
                    conn.commit()
                    log_audit("DPM_FO_28", "MODIFICATION", f"Modification relevé ID #{id_sel}")
                    st.success("Mis à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo28_pilotine WHERE id=?", (id_sel,))
                    conn.commit()
                    log_audit("DPM_FO_28", "SUPPRESSION", f"Suppression relevé ID #{id_sel}")
                    st.warning("Supprimé.")
                    st.rerun()
        else:
            st.info("Aucun relevé disponible.")

# ==============================================================================
# MODULE 6 : REGISTRE DES EPIs (DPM_FO_29)
# ==============================================================================
elif menu == "🦺 Registre des EPIs (DPM_FO_29)":
    st.markdown('<div class="module-banner"><h3>🦺 DPM_FO_29 — Le Registre des Équipements de Protection Individuelle (EPI)</h3><span>Sécurité SOLAS Pilotes</span></div>', unsafe_allow_html=True)
    etats_epi = ["Neuf", "Bon", "Moyen", "À remplacer"]
    tab1, tab2, tab3 = st.tabs(["📋 Registre, Édition Rapide & Export FO_29", "➕ Nouvel EPI", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_e = pd.read_sql_query("SELECT * FROM fo29_epis", conn)
        if not df_e.empty:
            edited_e = st.data_editor(
                df_e,
                use_container_width=True,
                disabled=["id"],
                num_rows="fixed",
                key="ed_fo29",
                column_config={
                    "util_cout": st.column_config.NumberColumn("Coût Util. (MAD)", format="%.2f MAD"),
                    "stock_cout": st.column_config.NumberColumn("Coût Stock (MAD)", format="%.2f MAD"),
                    "util_etat": st.column_config.SelectboxColumn("État Util.", options=etats_epi),
                    "stock_etat": st.column_config.SelectboxColumn("État Stock", options=etats_epi)
                }
            )
            if st.button("💾 Sauvegarder l'édition rapide (FO_29)", key="save_fast_fo29"):
                for _, r in edited_e.iterrows():
                    c.execute('''UPDATE fo29_epis SET
                        article=?, util_nombre=?, util_etat=?, util_echeance=?, util_cout=?,
                        stock_nombre=?, stock_etat=?, stock_echeance=?, stock_cout=?, stock_local=?,
                        besoin_achat=?, besoin_maintenance=?, observations=? WHERE id=?''', (
                        r['article'], int(r['util_nombre'] or 0), r['util_etat'], str(r['util_echeance']), float(r['util_cout'] or 0),
                        int(r['stock_nombre'] or 0), r['stock_etat'], str(r['stock_echeance']), float(r['stock_cout'] or 0), r['stock_local'],
                        r['besoin_achat'], r['besoin_maintenance'], r['observations'], int(r['id'])
                    ))
                conn.commit()
                log_audit("DPM_FO_29", "ÉDITION RAPIDE", "Mise à jour directe du registre des EPI.")
                st.success("Registre EPI mis à jour !")
                st.rerun()
        else:
            st.info("Aucun EPI enregistré.")

        st.download_button(
            "📥 Exporter DPM_FO_29 Officiel avec Logo NWM (.xlsx)",
            data=generate_official_excel_pack("FO_29"),
            file_name=f"DPM_FO_29_Registre_EPIs_{date.today()}.xlsx",
            key="dl_fo29"
        )

    with tab2:
        with st.form("add_fo29"):
            art = st.text_input("Article (ex: Gilet de sauvetage 275N, Casque, Chaussures de sécurité)")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**En utilisation**")
                u_nb = st.number_input("Nombre (Util.)", min_value=0, value=1)
                u_et = st.selectbox("Etat (Util.)", etats_epi)
                u_ec = st.date_input("Échéance (Util.)", date.today() + timedelta(days=365))
                u_ct = st.number_input("Coût (Util. MAD)", min_value=0.0, value=0.0)
            with c2:
                st.markdown("**En Stock**")
                s_nb = st.number_input("Nombre (Stock)", min_value=0, value=0)
                s_et = st.selectbox("Etat (Stock)", etats_epi)
                s_ec = st.date_input("Échéance (Stock)", date.today() + timedelta(days=730))
                s_ct = st.number_input("Coût (Stock MAD)", min_value=0.0, value=0.0)
                s_loc = st.text_input("Local", value="Magasin DPM")
            with c3:
                st.markdown("**Besoins & Observations**")
                b_ach = st.text_input("Besoins — Achat", value="Non")
                b_mnt = st.text_input("Besoins — Maintenance", value="Contrôle annuel")
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
                log_audit("DPM_FO_29", "AJOUT", f"Nouvel EPI : {art}")
                st.success("EPI enregistré !")
                st.rerun()

    with tab3:
        df_e = pd.read_sql_query("SELECT * FROM fo29_epis", conn)
        if not df_e.empty:
            id_sel = st.selectbox("Sélectionner l'EPI à modifier ou supprimer", df_e['id'].tolist(), format_func=lambda x: f"ID #{x} — {df_e[df_e['id']==x]['article'].values[0]}")
            row = df_e[df_e['id'] == id_sel].iloc[0]
            with st.form("edit_fo29"):
                u_art = st.text_input("Article", value=str(row['article']))
                c1, c2, c3 = st.columns(3)
                with c1:
                    u_nb = st.number_input("Nombre (Util.)", min_value=0, value=int(row['util_nombre']))
                    u_et = st.selectbox("Etat (Util.)", etats_epi, index=etats_epi.index(row['util_etat']) if row['util_etat'] in etats_epi else 0)
                    u_ec = st.date_input("Échéance (Util.)", value=parse_date_safe(row['util_echeance']))
                    u_ct = st.number_input("Coût (Util. MAD)", min_value=0.0, value=float(row['util_cout']))
                with c2:
                    s_nb = st.number_input("Nombre (Stock)", min_value=0, value=int(row['stock_nombre']))
                    s_et = st.selectbox("Etat (Stock)", etats_epi, index=etats_epi.index(row['stock_etat']) if row['stock_etat'] in etats_epi else 0)
                    s_ec = st.date_input("Échéance (Stock)", value=parse_date_safe(row['stock_echeance']))
                    s_ct = st.number_input("Coût (Stock MAD)", min_value=0.0, value=float(row['stock_cout']))
                    s_loc = st.text_input("Local", value=str(row['stock_local']))
                with c3:
                    b_ach = st.text_input("Besoins — Achat", value=str(row['besoin_achat']))
                    b_mnt = st.text_input("Besoins — Maintenance", value=str(row['besoin_maintenance']))
                    obs = st.text_area("Observations", value=str(row['observations']))
                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Enregistrer toutes les modifications"):
                    c.execute('''UPDATE fo29_epis SET
                        article=?, util_nombre=?, util_etat=?, util_echeance=?, util_cout=?,
                        stock_nombre=?, stock_etat=?, stock_echeance=?, stock_cout=?, stock_local=?,
                        besoin_achat=?, besoin_maintenance=?, observations=? WHERE id=?''', (
                        u_art, u_nb, u_et, str(u_ec), u_ct, s_nb, s_et, str(s_ec), s_ct, s_loc, b_ach, b_mnt, obs, id_sel
                    ))
                    conn.commit()
                    log_audit("DPM_FO_29", "MODIFICATION", f"Modification EPI ID #{id_sel} ({u_art})")
                    st.success("EPI mis à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo29_epis WHERE id=?", (id_sel,))
                    conn.commit()
                    log_audit("DPM_FO_29", "SUPPRESSION", f"Suppression EPI ID #{id_sel}")
                    st.warning("EPI supprimé.")
                    st.rerun()
        else:
            st.info("Aucun EPI enregistré.")

# ==============================================================================
# MODULE 7 : CHECKLISTS SPÉCIFICATIONS D'ACHAT & MAINTENANCE (CL_06 & CL_07)
# ==============================================================================
elif menu == "✅ Checklists Achats & Maint. (CL_06/07)":
    st.markdown('<div class="module-banner"><h3>✅ DPM_CL_06 (Spécifications d\'Achat) & DPM_CL_07 (Utilisation & Maintenance)</h3><span>Qualité & Exigences Techniques</span></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 Checklists, Édition Rapide & Export CL_06 / CL_07", "➕ Nouvelle Fiche", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_cl = pd.read_sql_query("SELECT * FROM cl06_07_checklists", conn)
        if not df_cl.empty:
            edited_cl = st.data_editor(df_cl, use_container_width=True, disabled=["id"], num_rows="fixed", key="ed_cl06_07")
            if st.button("💾 Sauvegarder l'édition rapide (CL_06/07)", key="save_fast_cl"):
                for _, r in edited_cl.iterrows():
                    c.execute('''UPDATE cl06_07_checklists SET
                        type_checklist=?, equipement_rubrique=?, specifications_achat=?,
                        recommandations_utilisation=?, recommandations_maintenance=?, observations=? WHERE id=?''', (
                        r['type_checklist'], r['equipement_rubrique'], r['specifications_achat'],
                        r['recommandations_utilisation'], r['recommandations_maintenance'], r['observations'], int(r['id'])
                    ))
                conn.commit()
                log_audit("DPM_CL_06/07", "ÉDITION RAPIDE", "Mise à jour des checklists d'achat et de maintenance.")
                st.success("Checklists mises à jour !")
                st.rerun()
        else:
            st.info("Aucune checklist enregistrée.")

        st.download_button(
            "📥 Exporter DPM_CL_06 & DPM_CL_07 Officiels avec Logo NWM (.xlsx)",
            data=generate_official_excel_pack("CL_06_07"),
            file_name=f"DPM_CL_06_07_Checklists_{date.today()}.xlsx",
            key="dl_cl06_07"
        )

    with tab2:
        with st.form("add_cl"):
            eq = st.text_input("Rubrique / Équipement")
            spec = st.text_area("Principales Spécifications d'Achat (DPM_CL_06)")
            rec_m = st.text_area("Les Principales Recommandations de Maintenance (DPM_CL_07)")
            rec_u = st.text_area("Les Principales Recommandations d'utilisation (DPM_CL_07)")
            obs = st.text_input("Observations")
            if st.form_submit_button("➕ Enregistrer"):
                c.execute('''INSERT INTO cl06_07_checklists (
                    type_checklist, equipement_rubrique, specifications_achat,
                    recommandations_utilisation, recommandations_maintenance, observations
                ) VALUES (?,?,?,?,?,?)''', ("DPM_CL_06 & DPM_CL_07", eq, spec, rec_u, rec_m, obs))
                conn.commit()
                log_audit("DPM_CL_06/07", "AJOUT", f"Nouvelle checklist : {eq}")
                st.success("Fiche enregistrée !")
                st.rerun()

    with tab3:
        df_cl = pd.read_sql_query("SELECT * FROM cl06_07_checklists", conn)
        if not df_cl.empty:
            id_sel = st.selectbox("Sélectionner la fiche à modifier ou supprimer", df_cl['id'].tolist(), format_func=lambda x: f"ID #{x} — {df_cl[df_cl['id']==x]['equipement_rubrique'].values[0]}")
            row = df_cl[df_cl['id'] == id_sel].iloc[0]
            with st.form("edit_cl"):
                u_eq = st.text_input("Rubrique / Équipement", value=str(row['equipement_rubrique']))
                u_spec = st.text_area("Spécifications d'Achat (DPM_CL_06)", value=str(row['specifications_achat']))
                u_recm = st.text_area("Recommandations de Maintenance (DPM_CL_07)", value=str(row['recommandations_maintenance']))
                u_recu = st.text_area("Recommandations d'utilisation (DPM_CL_07)", value=str(row['recommandations_utilisation']))
                u_obs = st.text_input("Observations", value=str(row['observations']))
                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Enregistrer toutes les modifications"):
                    c.execute('''UPDATE cl06_07_checklists SET
                        equipement_rubrique=?, specifications_achat=?,
                        recommandations_utilisation=?, recommandations_maintenance=?, observations=? WHERE id=?''',
                        (u_eq, u_spec, u_recu, u_recm, u_obs, id_sel))
                    conn.commit()
                    log_audit("DPM_CL_06/07", "MODIFICATION", f"Modification checklist ID #{id_sel}")
                    st.success("Fiche mise à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM cl06_07_checklists WHERE id=?", (id_sel,))
                    conn.commit()
                    log_audit("DPM_CL_06/07", "SUPPRESSION", f"Suppression checklist ID #{id_sel}")
                    st.warning("Fiche supprimée.")
                    st.rerun()
        else:
            st.info("Aucune fiche checklist enregistrée.")

# ==============================================================================
# MODULE 8 : FORMULAIRE DE PRÉPARATION DU BUDGET (DPM_FO_30)
# ==============================================================================
elif menu == "💰 Préparation du Budget (DPM_FO_30)":
    st.markdown('<div class="module-banner"><h3>💰 DPM_FO_30 — Le Formulaire de Préparation du Budget de La DPM</h3><span>Consolidation Financière & Variations</span></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📊 Formulaire Officiel, Synchro Auto & Export FO_30", "➕ Ajouter une Ligne Budgétaire", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        if st.button("🔄 Synchroniser automatiquement les dépenses depuis les registres FO_23 à FO_29", key="btn_sync_budget"):
            df_eq_sync = pd.read_sql_query("SELECT classe, SUM(cout_estime) as total_cout FROM fo24_25_equipements GROUP BY classe", conn)
            for _, r_eq in df_eq_sync.iterrows():
                if float(r_eq['total_cout'] or 0) > 0:
                    c.execute("SELECT COUNT(*) FROM fo30_budget_lignes WHERE classe_rubrique=? AND type_ligne='Investissement'", (r_eq['classe'],))
                    if c.fetchone()[0] == 0:
                        c.execute('''INSERT INTO fo30_budget_lignes (
                            type_ligne, classe_rubrique, article_investissement, justification,
                            prix_unitaire_estime, besoin_unites_estime, cout_estime_n,
                            qte_annee_prec, cout_annee_prec, observations
                        ) VALUES (?,?,?,?,?,?,?,?,?,?)''', (
                            "Investissement", r_eq['classe'], f"Dotation consolidée {r_eq['classe']}",
                            "Consolidation automatique depuis les registres FO_24/25",
                            float(r_eq['total_cout']), 1.0, float(r_eq['total_cout']), 0.0, 0.0, "Synchronisé automatiquement"
                        ))
            conn.commit()
            log_audit("DPM_FO_30", "SYNCHRONISATION", "Consolidation automatique des coûts depuis les registres.")
            st.success("Synchronisation budgétaire effectuée !")
            st.rerun()

        df_b = pd.read_sql_query("SELECT * FROM fo30_budget_lignes", conn)
        if not df_b.empty:
            df_b['Variation Budget (MAD)'] = df_b['cout_estime_n'] - df_b['cout_annee_prec']
            df_conso_b = df_b[df_b['type_ligne'] == 'Consommation (Générale / Pharmacie)']
            df_invest_b = df_b[df_b['type_ligne'] == 'Investissement']

            st.markdown("##### 1. Consommations Générale / Consommation Pharmacie")
            st.dataframe(df_conso_b[['id', 'classe_rubrique', 'article_investissement', 'prix_unitaire_estime', 'besoin_unites_estime', 'cout_estime_n', 'qte_annee_prec', 'cout_annee_prec', 'Variation Budget (MAD)', 'observations']], use_container_width=True)

            st.markdown("##### 2. Partie Investissements : Formations / EPIs / Tenue / Peinture / Construction / Vigie / PCs / VHF")
            st.dataframe(df_invest_b[['id', 'classe_rubrique', 'article_investissement', 'justification', 'cout_estime_n', 'cout_annee_prec', 'Variation Budget (MAD)', 'observations']], use_container_width=True)

            tot_n = df_b['cout_estime_n'].sum()
            tot_prec = df_b['cout_annee_prec'].sum()
            k1, k2, k3 = st.columns(3)
            k1.metric("Budget année précédente", f"{tot_prec:,.2f} MAD")
            k2.metric("Budget année en objet", f"{tot_n:,.2f} MAD")
            k3.metric("Variation Budget", f"{tot_n - tot_prec:+,.2f} MAD")
        else:
            st.info("Aucune ligne budgétaire enregistrée.")

        st.download_button(
            "📥 Exporter DPM_FO_30 Officiel avec Logo NWM (.xlsx)",
            data=generate_official_excel_pack("FO_30"),
            file_name=f"DPM_FO_30_Preparation_Budget_{date.today()}.xlsx",
            key="dl_fo30"
        )

    with tab2:
        with st.form("add_fo30"):
            c1, c2 = st.columns(2)
            with c1:
                tl = st.selectbox("Section du formulaire `DPM_FO_30`", ["Investissement", "Consommation (Générale / Pharmacie)"])
                cl = st.selectbox("Classe / Rubrique", [
                    "Radios Portatifs VHF", "EPIs", "Tenue", "Formations", "Vigie",
                    "PCs & Informatique", "Peinture & Construction", "Consommation Générale", "Consommation Pharmacie", "Autre"
                ])
                art = st.text_input("Article ou Investissement")
                justif = st.text_area("Justifications (Pour les Investissements)")
            with c2:
                pu = st.number_input("Prix Unitaire Estimé (MAD)", min_value=0.0, value=0.0, step=100.0)
                qte_n = st.number_input("Besoins annuels estimés (Unités)", min_value=0.0, value=1.0)
                qte_prec = st.number_input("Quantité consommée année précédente", min_value=0.0, value=0.0)
                cout_prec = st.number_input("Coût année précédente (MAD)", min_value=0.0, value=0.0)
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
                log_audit("DPM_FO_30", "AJOUT", f"Nouvelle ligne budgétaire : {art} ({cout_n:,.2f} MAD)")
                st.success("Ligne budgétaire enregistrée !")
                st.rerun()

    with tab3:
        df_b = pd.read_sql_query("SELECT * FROM fo30_budget_lignes", conn)
        if not df_b.empty:
            id_sel = st.selectbox("Sélectionner la ligne à modifier ou supprimer", df_b['id'].tolist(), format_func=lambda x: f"ID #{x} — [{df_b[df_b['id']==x]['type_ligne'].values[0]}] {df_b[df_b['id']==x]['article_investissement'].values[0]}")
            row = df_b[df_b['id'] == id_sel].iloc[0]
            with st.form("edit_fo30"):
                c1, c2 = st.columns(2)
                tls = ["Investissement", "Consommation (Générale / Pharmacie)"]
                cls_list = [
                    "Radios Portatifs VHF", "EPIs", "Tenue", "Formations", "Vigie",
                    "PCs & Informatique", "Peinture & Construction", "Consommation Générale", "Consommation Pharmacie", "Autre"
                ]
                with c1:
                    u_tl = st.selectbox("Section", tls, index=tls.index(row['type_ligne']) if row['type_ligne'] in tls else 0)
                    u_cl = st.selectbox("Classe", cls_list, index=cls_list.index(row['classe_rubrique']) if row['classe_rubrique'] in cls_list else 0)
                    u_art = st.text_input("Article / Investissement", value=str(row['article_investissement']))
                    u_just = st.text_area("Justifications", value=str(row['justification']))
                with c2:
                    u_pu = st.number_input("Prix Unitaire Estimé (MAD)", min_value=0.0, value=float(row['prix_unitaire_estime']))
                    u_qten = st.number_input("Besoins estimés (Unités)", min_value=0.0, value=float(row['besoin_unites_estime']))
                    u_qteprec = st.number_input("Quantité année précédente", min_value=0.0, value=float(row['qte_annee_prec']))
                    u_coutprec = st.number_input("Coût année précédente (MAD)", min_value=0.0, value=float(row['cout_annee_prec']))
                    u_obs = st.text_input("Observations", value=str(row['observations']))
                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Enregistrer toutes les modifications"):
                    u_coutn = u_pu * u_qten
                    c.execute('''UPDATE fo30_budget_lignes SET
                        type_ligne=?, classe_rubrique=?, article_investissement=?, justification=?,
                        prix_unitaire_estime=?, besoin_unites_estime=?, cout_estime_n=?,
                        qte_annee_prec=?, cout_annee_prec=?, observations=? WHERE id=?''', (
                        u_tl, u_cl, u_art, u_just, u_pu, u_qten, u_coutn, u_qteprec, u_coutprec, u_obs, id_sel
                    ))
                    conn.commit()
                    log_audit("DPM_FO_30", "MODIFICATION", f"Modification budget ID #{id_sel}")
                    st.success("Ligne budgétaire mise à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo30_budget_lignes WHERE id=?", (id_sel,))
                    conn.commit()
                    log_audit("DPM_FO_30", "SUPPRESSION", f"Suppression budget ID #{id_sel}")
                    st.warning("Ligne budgétaire supprimée.")
                    st.rerun()
        else:
            st.info("Aucune ligne budgétaire enregistrée.")

# ==============================================================================
# MODULE 9 : JOURNAL D'AUDIT & TRAÇABILITÉ SM ISPO
# ==============================================================================
elif menu == "🛡️ Journal d'Audit & Conformité ISPO":
    st.markdown('<div class="module-banner"><h3>🛡️ Journal d\'Audit Horodaté & Traçabilité Réglementaire ISPO</h3><span>Preuve d\'Audit Interne & Externe</span></div>', unsafe_allow_html=True)
    df_logs = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY id DESC", conn)
    st.dataframe(df_logs, use_container_width=True, hide_index=True)

# ==============================================================================
# 6. PIED DE PAGE OFFICIEL DE L'APPLICATION (NIVEAU RACINE)
# ==============================================================================
st.markdown("""
<div class="nwm-footer">
    <strong>DIRECTION DU PILOTAGE MARITIME — NADOR WEST MED (DPM)</strong> • SYSTÈME DE MANAGEMENT CERTIFIÉ ISPO<br>
    Référentiel Documentaire : DMP_PR_02 | DPM_FI_02 | Formulaires Officiels DPM_FO_23 à DPM_FO_30 & Checklists DPM_CL_06 / DPM_CL_07
</div>
""", unsafe_allow_html=True)

# === FIN DU SCRIPT APP.PY ===
