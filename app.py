import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import sqlite3
import plotly.express as px
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import base64
import os

# ==============================================================================
# 1. CONFIGURATION DE LA PAGE & LOGO OFFICIEL NADOR WEST MED
# ==============================================================================
st.set_page_config(
    page_title="Nador West Med - La DPM | Ressources Matérielles ISPO",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOGO_FILE = "logo.png"
DB_FILE = "dpm_nwm_ispo_officiel.db"

def generate_nwm_logo_png_bytes():
    """Charge le fichier logo.png s'il existe, sinon génère le logo Nador West Med."""
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

    # Arc orbital bleu marine (#1B3668)
    draw.arc([14, 10, 195, 191], start=115, end=330, fill=(27, 54, 104, 255), width=6)

    # Sphère Nador West Med
    globe_box = [32, 28, 168, 164]
    draw.pieslice(globe_box, start=180, end=295, fill=(43, 108, 176, 255))
    draw.pieslice(globe_box, start=295, end=360, fill=(30, 78, 140, 255))
    draw.pieslice(globe_box, start=0, end=180, fill=(0, 163, 180, 255))

    # Lignes blanches croisées
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
# 2. FEUILLE DE STYLE INSTITUTIONNELLE NADOR WEST MED (SOBRE & ÉLÉGANTE)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 97%;
    }

    /* En-tête officiel Nador West Med - La DPM */
    .nwm-header {
        background: linear-gradient(135deg, #1b3668 0%, #134074 60%, #008394 100%);
        color: #ffffff;
        padding: 1.3rem 1.8rem;
        border-radius: 12px;
        border-bottom: 4px solid #00a3b4;
        box-shadow: 0 6px 18px rgba(27, 54, 104, 0.12);
        margin-bottom: 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .nwm-header-left {
        display: flex;
        align-items: center;
        gap: 1.3rem;
    }
    .nwm-logo-wrapper {
        background: #ffffff;
        padding: 0.45rem 0.8rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
        display: flex;
        align-items: center;
    }
    .nwm-header h1 {
        color: #ffffff;
        font-size: 1.45rem;
        font-weight: 700;
        margin: 0;
    }
    .nwm-header p {
        color: #e0f2fe;
        font-size: 0.9rem;
        margin: 0.25rem 0 0 0;
    }
    .nwm-ref-box {
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 0.55rem 1rem;
        border-radius: 8px;
        text-align: right;
        font-size: 0.8rem;
        line-height: 1.4;
    }

    /* Cartes d'indicateurs épurées */
    .metric-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 1.15rem 1.3rem;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #1b3668;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        margin-bottom: 0.8rem;
    }
    .metric-card.turquoise { border-top-color: #0097a7; }
    .metric-card.success { border-top-color: #10b981; }
    .metric-card.danger { border-top-color: #ef4444; background: #fffafa; }
    .metric-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #1b3668;
        margin: 0.3rem 0;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #475569;
    }

    /* Bandeau de titre des formulaires */
    .section-title {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #1b3668;
        padding: 0.75rem 1.15rem;
        border-radius: 8px;
        margin-bottom: 1.1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .section-title h3 {
        margin: 0;
        font-size: 1.1rem;
        color: #1b3668;
        font-weight: 700;
    }
    .section-badge {
        background: #e0f2fe;
        color: #0369a1;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 6px;
    }

    /* Pied de page sobre */
    .nwm-footer {
        margin-top: 2.5rem;
        padding: 1rem;
        background: #f8fafc;
        border-top: 2px solid #e2e8f0;
        text-align: center;
        color: #64748b;
        font-size: 0.8rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. BASE DE DONNÉES SQLITE & PRÉ-CHARGEMENT EXCLUSIF DES VHF RÉCEPTIONNÉES
# ==============================================================================
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
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

    # DPM_FO_24, DPM_FO_25 & Classes DMP_PR_02
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

    # DPM_FO_28 : Le Registre de La Consommation de la Pilotine
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

    # DPM_FO_30 : Le Formulaire de Préparation du Budget de La DPM
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

    # DPM_CL_06 & DPM_CL_07 : Checklists
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
    """Pré-charge uniquement les données réelles de la livraison des VHF SOREMAR."""
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
                f"Radio VHF Portative Marine ATEX Motorola DP4801 Ex #{idx:02d}",
                sn,
                15800.00,
                "Bon", 1, "La DPM",
                0, "Magasin DPM",
                "Non", "Non",
                "2026-10-15", "2028-10-15",
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
            "Code C0113530",
            57750.00,
            "Bon", 10, "En service",
            5, "Magasin DPM",
            "Non", "Non",
            "2026-10-15", "2028-10-15",
            "BC N°20260014 | Facture F-RAD26/0024 SOREMAR (15 unités x 3 850,00 MAD HT)"
        ))

        c.execute('''INSERT INTO fo24_25_equipements (
            classe, article, reference_serie, cout_estime,
            util_etat, util_quantite, util_emplacement,
            stock_quantite, stock_localisation,
            besoin_achat, besoin_reparation,
            date_reception, echeance_garantie, observations
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
            "Radios Portatifs VHF",
            "Accessoires VHF : 10 Housses FUNDA DURA + 10 Motorola IMPRES ATEX Noise Can",
            "C0126461 / C0326460",
            0.00,
            "Bon", 10, "La DPM",
            0, "Magasin DPM",
            "Non", "Non",
            "2026-10-15", "2028-10-15",
            "Inclus dans la livraison BC N°20260014 / BL-CAS2610/0453"
        ))

    c.execute("SELECT COUNT(*) FROM cl06_07_checklists")
    if c.fetchone()[0] == 0:
        c.execute('''INSERT INTO cl06_07_checklists (
            type_checklist, equipement_rubrique, specifications_achat,
            recommandations_utilisation, recommandations_maintenance, observations
        ) VALUES (?,?,?,?,?,?)''', (
            "DPM_CL_06 & DPM_CL_07",
            "Radios Portatifs VHF Marines ATEX (Motorola DP4801 Ex)",
            "Certification ATEX, étanchéité IP67, bande VHF marine, GPS intégré, accessoires IMPRES ATEX, garantie 2 ans.",
            "Utiliser avec batterie ATEX DP4401 et housse de protection. Vérifier le niveau de charge avant chaque opération.",
            "Ne pas charger en zone ATEX. Nettoyer au chiffon doux humide après exposition saline.",
            "Fournisseur : SOREMAR (BC N°20260014)"
        ))

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
            "Dotation des équipements de radiocommunication VHF ATEX de La DPM",
            21575.00, 10.0, 215750.00,
            0.0, 0.0,
            "BC N°20260014 - Facture SOREMAR F-RAD26/0024 (215 750,00 MAD)"
        ))
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
# 4. MOTEUR D'EXPORT EXCEL OFFICIEL NADOR WEST MED (FORMATS EXACTS FO_23 À FO_30)
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

    ws.merge_range(0, 0, 2, left_end - 1, "NADOR WEST MED — La DPM", styles['org_box'])
    ws.merge_range(0, left_end, 2, right_start - 1, doc_title, styles['title_box'])
    ws.merge_range(0, right_start, 2, total_cols - 1, f"{doc_code}\nDate d'émission : {emission_date}\nPage : 1/1", styles['ref_box'])

    try:
        logo_bytes = generate_nwm_logo_png_bytes()
        img_pil = Image.open(BytesIO(logo_bytes))
        _, h_px = img_pil.size
        scale = 54.0 / float(h_px)
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
    if df.empty:
        for _ in range(5):
            ws.set_row(r, 22)
            for col in range(5):
                ws.write(r, col, "", styles['td_text'])
            r += 1
    else:
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
    if df_subset.empty:
        for _ in range(5):
            ws.set_row(r, 22)
            for col in range(10):
                ws.write(r, col, "", styles['td_text'])
            r += 1
    else:
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
    if df.empty:
        for _ in range(5):
            ws.set_row(r, 22)
            for col in range(13):
                ws.write(r, col, "", styles['td_text'])
            r += 1
    else:
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
    if df.empty:
        for _ in range(5):
            ws.set_row(r, 22)
            for col in range(15):
                ws.write(r, col, "", styles['td_text'])
            r += 1
    else:
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
    if df.empty:
        for _ in range(4):
            ws.set_row(r, 22)
            for col in range(13):
                ws.write(r, col, "", styles['td_text'])
            r += 1
    else:
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
    if df.empty:
        for _ in range(5):
            ws.set_row(r, 22)
            for col in range(13):
                ws.write(r, col, "", styles['td_text'])
            r += 1
    else:
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
    if df_conso.empty:
        for _ in range(3):
            ws.set_row(r, 20)
            for col in range(9):
                ws.write(r, col, "", styles['td_text'])
            r += 1
    else:
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
    if df_inv.empty:
        for _ in range(3):
            ws.set_row(r, 22)
            ws.merge_range(r, 0, r, 2, "", styles['td_text'])
            ws.merge_range(r, 3, r, 7, "", styles['td_text'])
            ws.write(r, 8, "", styles['td_curr'])
            r += 1
    else:
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
            build_sheet_fo24_or_25(wb, styles, "DPM_Registre_Equipements", "DMP_PR_02", "Registre Consolidé des Équipements de La DPM", df_all_eq)
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

# ==============================================================================
# 5. BARRE LATÉRALE DE NAVIGATION
# ==============================================================================
logo_b64 = get_logo_base64()
st.sidebar.markdown(
    f'<div style="background:white; padding:12px; border-radius:10px; text-align:center; margin-bottom:12px; border:1px solid #e2e8f0;">'
    f'<img src="data:image/png;base64,{logo_b64}" style="max-height:68px;">'
    f'</div>',
    unsafe_allow_html=True
)
st.sidebar.markdown(
    "<div style='background:#f8fafc; color:#1b3668; padding:10px 12px; border-radius:8px; font-size:0.82rem; margin-bottom:12px; border:1px solid #e2e8f0; border-left:4px solid #1b3668;'>"
    "<b>Le PMJA Ressources DPM :</b><br>Omar Dialmy<br>"
    "<span style='color:#008394; font-size:0.75rem; font-weight:600;'>Système de Management ISPO</span>"
    "</div>",
    unsafe_allow_html=True
)

menu = st.sidebar.radio(
    "Formulaires Officiels de La DPM",
    [
        "📊 Tableau de Bord ISPO (DPM_FI_02)",
        "🏗️ Infrastructures (DPM_FO_23)",
        "📡 Équipements, Vigie & VHF (FO_24/25)",
        "📦 Consommables & Pharmacie (FO_26/27)",
        "🚤 Consommation Pilotine (DPM_FO_28)",
        "🦺 Registre des EPIs (DPM_FO_29)",
        "✅ Checklists Achats & Maint. (CL_06/07)",
        "💰 Préparation du Budget (DPM_FO_30)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📘 Télécharger Cartable Complet (.xlsx)",
    data=generate_official_excel_pack("ALL"),
    file_name=f"Cartable_Officiel_DPM_NWM_{date.today()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
    key="btn_dl_all_sidebar"
)

with st.sidebar.expander("🖼️ Logo & Sauvegarde Base SQL"):
    up_logo = st.file_uploader("Importer votre logo officiel (.png)", type=["png", "jpg", "jpeg"])
    if up_logo is not None:
        with open(LOGO_FILE, "wb") as f:
            f.write(up_logo.getbuffer())
        st.success("Logo officiel enregistré !")
        st.rerun()

    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            st.download_button("⬇️ Sauvegarder la base (.db)", data=f, file_name=f"backup_dpm_nwm_{date.today()}.db", use_container_width=True, key="btn_backup_db")
    uploaded_db = st.file_uploader("Restaurer un fichier .db", type=["db", "sqlite"])
    if uploaded_db is not None:
        if st.button("⚠️ Confirmer la restauration", use_container_width=True):
            with open(DB_FILE, "wb") as f:
                f.write(uploaded_db.getbuffer())
            st.success("Base restaurée avec succès !")
            st.rerun()

# ==============================================================================
# EN-TÊTE PRINCIPAL OFFICIEL NADOR WEST MED — LA DPM
# ==============================================================================
st.markdown(f"""
<div class="nwm-header">
    <div class="nwm-header-left">
        <div class="nwm-logo-wrapper">
            <img src="data:image/png;base64,{logo_b64}" style="height: 54px;">
        </div>
        <div>
            <h1>NADOR WEST MED — La DPM</h1>
            <p>Système de Management ISPO • Gestion des Ressources Matérielles (DMP_PR_02 / DPM_FI_02)</p>
        </div>
    </div>
    <div class="nwm-ref-box">
        <strong>Référentiel Documentaire DPM</strong><br>
        Formulaires DPM_FO_23 à FO_30 • CL_06 / CL_07<br>
        Date d'émission : 31/12/25
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# MODULE 1 : TABLEAU DE BORD ISPO (DPM_FI_02)
# ==============================================================================
if menu == "📊 Tableau de Bord ISPO (DPM_FI_02)":
    df_infra = pd.read_sql_query("SELECT * FROM fo23_infrastructures", conn)
    df_equip = pd.read_sql_query("SELECT * FROM fo24_25_equipements", conn)
    df_conso = pd.read_sql_query("SELECT * FROM fo26_27_consommables", conn)
    df_pil = pd.read_sql_query("SELECT * FROM fo28_pilotine", conn)
    df_epi = pd.read_sql_query("SELECT * FROM fo29_epis", conn)

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

    # 4 Cartes KPI Sobres et Professionnelles
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        cls_1 = "danger" if kpi_indispo > 0 else "success"
        st.markdown(f"""
        <div class="metric-card {cls_1}">
            <div class="metric-label">Disponibilité Critique (DPM_FI_02)</div>
            <div class="metric-value">{kpi_indispo} anomalie</div>
            <div class="metric-sub">Objectif ISPO : 0 indisponibilité non traitée</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card turquoise">
            <div class="metric-label">Équipements Actifs & Stock</div>
            <div class="metric-value">{unites_actives} en service</div>
            <div class="metric-sub">{unites_stock} en réserve ({len(df_equip)} lignes enregistrées)</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        cls_3 = "danger" if nb_alertes_exp > 0 else "success"
        st.markdown(f"""
        <div class="metric-card {cls_3}">
            <div class="metric-label">Alertes Échéances (&lt; 30 jours)</div>
            <div class="metric-value">{nb_alertes_exp} alerte(s)</div>
            <div class="metric-sub">Surveillance EPIs (FO_29) & Pharmacie (FO_27)</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Valeur Matérielle Enregistrée</div>
            <div class="metric-value">{total_patrimoine:,.2f} MAD</div>
            <div class="metric-sub">Total cumulé des équipements & dotations</div>
        </div>""", unsafe_allow_html=True)

    if kpi_indispo == 0 and nb_alertes_exp == 0:
        st.success("✅ **Indicateur `DPM_FI_02` Conforme :** Aucun équipement critique hors service et aucune échéance EPI ou Pharmacie à moins de 30 jours.")
    else:
        if kpi_indispo > 0:
            st.error(f"🚨 **Alerte `DPM_FI_02` :** {kpi_indispo} équipement(s) ou infrastructure(s) signalé(s) à réparer.")
        if not alertes_epi_df.empty:
            st.warning(f"⚠️ **Échéance EPI (`DPM_FO_29`) :** {len(alertes_epi_df)} lot(s) d'EPI arrivent à échéance dans moins de 30 jours.")
            st.dataframe(alertes_epi_df[['id', 'article', 'util_nombre', 'util_echeance', 'observations']], use_container_width=True, hide_index=True)
        if not alertes_pharma_df.empty:
            st.warning(f"⚠️ **Péremption Pharmacie (`DPM_FO_27`) :** {len(alertes_pharma_df)} article(s) pharmaceutique(s) arrivent à expiration.")
            st.dataframe(alertes_pharma_df[['id', 'article', 'fin_qte', 'fin_date_expir', 'observations']], use_container_width=True, hide_index=True)

    # Graphiques Simples, Élégants et Lisibles
    st.markdown("---")
    g1, g2 = st.columns(2)

    with g1:
        st.markdown("##### 💰 Valeur des Équipements par Classe (`DMP_PR_02`)")
        if not df_equip.empty and df_equip['cout_estime'].sum() > 0:
            df_val = df_equip.groupby('classe', as_index=False)['cout_estime'].sum().sort_values('cout_estime', ascending=True)
            fig_val = px.bar(
                df_val,
                x='cout_estime',
                y='classe',
                orientation='h',
                text_auto=',.0f',
                labels={'cout_estime': 'Valeur (MAD)', 'classe': ''},
                color_discrete_sequence=['#1B3668']
            )
            fig_val.update_traces(textPosition='outside', cliponaxis=False)
            fig_val.update_layout(
                height=320,
                margin=dict(t=10, b=20, l=10, r=40),
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                yaxis=dict(showgrid=False)
            )
            st.plotly_chart(fig_val, use_container_width=True)
        else:
            st.info("Aucun coût d'équipement enregistré pour le moment.")

    with g2:
        st.markdown("##### 📦 Dotations En Utilisation vs En Stock (Unités)")
        if not df_equip.empty:
            df_qte = df_equip.groupby('classe', as_index=False)[['util_quantite', 'stock_quantite']].sum()
            df_melt = df_qte.melt(id_vars='classe', value_vars=['util_quantite', 'stock_quantite'], var_name='Statut', value_name='Unités')
            df_melt['Statut'] = df_melt['Statut'].replace({'util_quantite': 'En utilisation', 'stock_quantite': 'En stock'})
            fig_qte = px.bar(
                df_melt,
                x='classe',
                y='Unités',
                color='Statut',
                barmode='group',
                text_auto=True,
                labels={'classe': '', 'Unités': 'Nombre d\'unités'},
                color_discrete_map={'En utilisation': '#1B3668', 'En stock': '#0097A7'}
            )
            fig_qte.update_layout(
                height=320,
                margin=dict(t=10, b=20, l=10, r=10),
                plot_bgcolor='white',
                paper_bgcolor='white',
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None)
            )
            st.plotly_chart(fig_qte, use_container_width=True)
        else:
            st.info("Aucun équipement enregistré.")

    # Troisième graphique simple : Suivi Pilotine (FO_28) + Tableau de synthèse des registres
    st.markdown("---")
    b1, b2 = st.columns([1.2, 1.1])

    with b1:
        st.markdown("##### 🚤 Suivi de la Consommation de la Pilotine (`DPM_FO_28`)")
        if not df_pil.empty:
            df_pil['Gasoil Consommé (L)'] = df_pil['debut_gasoil'] + df_pil['livre_gasoil'] - df_pil['fin_gasoil']
            df_pil['Lubrifiant Consommé (L)'] = df_pil['debut_lubrif'] + df_pil['livre_lubrif'] - df_pil['fin_lubrif']
            fig_pil = px.bar(
                df_pil,
                x='fin_date',
                y=['Gasoil Consommé (L)', 'Lubrifiant Consommé (L)'],
                barmode='group',
                text_auto='.1f',
                labels={'fin_date': 'Date de fin de période', 'value': 'Litres consommés', 'variable': 'Fluide'},
                color_discrete_sequence=['#1B3668', '#0097A7']
            )
            fig_pil.update_layout(
                height=300,
                margin=dict(t=10, b=20, l=10, r=10),
                plot_bgcolor='white',
                paper_bgcolor='white',
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None)
            )
            st.plotly_chart(fig_pil, use_container_width=True)
        else:
            st.info("Aucun relevé saisi dans 'Consommation Pilotine (DPM_FO_28)'. Le graphique s'affichera automatiquement dès votre premier relevé.")

    with b2:
        st.markdown("##### 📋 État des Registres Réglementaires de La DPM")
        df_b = pd.read_sql_query("SELECT * FROM fo30_budget_lignes", conn)
        df_cl = pd.read_sql_query("SELECT * FROM cl06_07_checklists", conn)
        recap_df = pd.DataFrame([
            {"Référence": "DPM_FO_23", "Registre Officiel": "Le Registre des Infrastructures de La DPM", "Lignes": len(df_infra)},
            {"Référence": "DPM_FO_24 / 25", "Registre Officiel": "Équipements d'Ameublement, Vigie & VHF", "Lignes": len(df_equip)},
            {"Référence": "DPM_FO_26 / 27", "Registre Officiel": "États des Consommations Générales & Pharmacie", "Lignes": len(df_conso)},
            {"Référence": "DPM_FO_28", "Registre Officiel": "Le Registre de La Consommation de la Pilotine", "Lignes": len(df_pil)},
            {"Référence": "DPM_FO_29", "Registre Officiel": "Le Registre des EPIs", "Lignes": len(df_epi)},
            {"Référence": "DPM_CL_06 / 07", "Registre Officiel": "Checklists Spécifications d'Achat & Maintenance", "Lignes": len(df_cl)},
            {"Référence": "DPM_FO_30", "Registre Officiel": "Le Formulaire de Préparation du Budget de La DPM", "Lignes": len(df_b)}
        ])
        st.dataframe(recap_df, use_container_width=True, hide_index=True)

# ==============================================================================
# MODULE 2 : INFRASTRUCTURES PERMANENTES (DPM_FO_23)
# ==============================================================================
elif menu == "🏗️ Infrastructures (DPM_FO_23)":
    st.markdown('<div class="section-title"><h3>🏗️ DPM_FO_23 — Le Registre des Infrastructures de La DPM</h3><span class="section-badge">Date d\'émission : 31/12/25</span></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 Registre & Export Officiel", "➕ Nouvelle Infrastructure", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_infra = pd.read_sql_query("SELECT * FROM fo23_infrastructures", conn)
        edited_infra = st.data_editor(df_infra, use_container_width=True, disabled=["id"], num_rows="fixed", key="ed_fo23")
        c_btn1, c_btn2 = st.columns([1, 2])
        if c_btn1.button("💾 Sauvegarder l'édition rapide (FO_23)", key="save_fast_fo23"):
            for _, r in edited_infra.iterrows():
                c.execute('''UPDATE fo23_infrastructures SET
                    infrastructure=?, besoins_reparation=?, reparations_commentaire=?,
                    reparations_cout=?, criticite=?, date_mise_a_jour=?, observations=? WHERE id=?''',
                    (r['infrastructure'], r['besoins_reparation'], r['reparations_commentaire'], float(r['reparations_cout'] or 0), r['criticite'], str(r['date_mise_a_jour']), r['observations'], int(r['id'])))
            conn.commit()
            st.success("Tableau mis à jour avec succès !")
            st.rerun()
        c_btn2.download_button(
            "📥 Exporter DPM_FO_23 Officiel (.xlsx)",
            data=generate_official_excel_pack("FO_23"),
            file_name=f"DPM_FO_23_Infrastructures_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_fo23"
        )

    with tab2:
        with st.form("add_fo23"):
            c1, c2 = st.columns(2)
            with c1:
                infra = st.text_input("Infrastructure")
                besoins = st.text_area("Besoins de réparation")
                criticite = st.selectbox("Criticité", ["Normal", "Moyen", "Critique - Urgent"])
            with c2:
                rep_comm = st.text_area("Les réparations réalisées — Commentaire")
                rep_cout = st.number_input("Les réparations réalisées — Coût (MAD)", min_value=0.0, step=100.0)
                dt_maj = st.date_input("Date", date.today())
                obs = st.text_input("Observations")
            if st.form_submit_button("➕ Enregistrer dans DPM_FO_23"):
                c.execute('''INSERT INTO fo23_infrastructures (
                    infrastructure, besoins_reparation, reparations_commentaire,
                    reparations_cout, criticite, date_mise_a_jour, observations
                ) VALUES (?,?,?,?,?,?,?)''', (infra, besoins, rep_comm, rep_cout, criticite, str(dt_maj), obs))
                conn.commit()
                st.success("Infrastructure enregistrée !")
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
                    u_comm = st.text_area("Les réparations réalisées — Commentaire", value=str(row['reparations_commentaire']))
                    u_cout = st.number_input("Les réparations réalisées — Coût (MAD)", min_value=0.0, value=float(row['reparations_cout']))
                    u_dt = st.date_input("Date", value=parse_date_safe(row['date_mise_a_jour']))
                    u_obs = st.text_input("Observations", value=str(row['observations']))
                b1, b2 = st.columns(2)
                if b1.form_submit_button("💾 Enregistrer toutes les modifications"):
                    c.execute('''UPDATE fo23_infrastructures SET
                        infrastructure=?, besoins_reparation=?, reparations_commentaire=?,
                        reparations_cout=?, criticite=?, date_mise_a_jour=?, observations=? WHERE id=?''',
                        (u_infra, u_besoins, u_comm, u_cout, u_crit, str(u_dt), u_obs, id_sel))
                    conn.commit()
                    st.success("Mis à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo23_infrastructures WHERE id=?", (id_sel,))
                    conn.commit()
                    st.warning("Supprimé.")
                    st.rerun()
        else:
            st.info("Aucune infrastructure enregistrée.")

# ==============================================================================
# MODULE 3 : ÉQUIPEMENTS, VIGIE, AMEUBLEMENT & VHF (DPM_FO_24 / DPM_FO_25)
# ==============================================================================
elif menu == "📡 Équipements, Vigie & VHF (FO_24/25)":
    st.markdown('<div class="section-title"><h3>📡 DPM_FO_24 & DPM_FO_25 — Registre des Équipements de La DPM (Vigie, Ameublement, VHF...)</h3><span class="section-badge">DMP_PR_02</span></div>', unsafe_allow_html=True)
    classes_pr02 = [
        "Radios Portatifs VHF",
        "Équipements de la Vigie (DPM_FO_25)",
        "Équipements d'Ameublement (DPM_FO_24)",
        "PPUs (Portable Pilot Units)",
        "Simulateur de La DPM",
        "Parc des Voitures de Service",
        "Parc des Pilotines"
    ]
    etats_list = ["Bon", "Moyen", "À réparer", "Hors service"]

    tab1, tab2, tab3 = st.tabs(["📋 Registre & Exports Officiels", "➕ Nouvel Équipement", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_eq = pd.read_sql_query("SELECT * FROM fo24_25_equipements", conn)
        f1, f2 = st.columns([2, 1])
        filtre_classe = f1.multiselect("Filtrer par Classe (`DMP_PR_02`)", options=classes_pr02, default=classes_pr02)
        search_q = f2.text_input("🔍 Rechercher (Numéro de série, Article...)", "")

        df_filtered = df_eq[df_eq['classe'].isin(filtre_classe)] if not df_eq.empty else df_eq
        if search_q.strip() and not df_filtered.empty:
            mask = df_filtered.astype(str).apply(lambda x: x.str.contains(search_q, case=False, na=False)).any(axis=1)
            df_filtered = df_filtered[mask]

        edited_eq = st.data_editor(df_filtered, use_container_width=True, disabled=["id"], num_rows="fixed", key="ed_fo24_25")

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
            st.success("Modifications enregistrées !")
            st.rerun()

        st.markdown("##### 📥 Téléchargements Officiels Nador West Med")
        ex1, ex2, ex3 = st.columns(3)
        ex1.download_button(
            "📥 Exporter DPM_FO_24 (Ameublement)",
            data=generate_official_excel_pack("FO_24"),
            file_name=f"DPM_FO_24_Ameublement_{date.today()}.xlsx",
            use_container_width=True,
            key="dl_fo24"
        )
        ex2.download_button(
            "📥 Exporter DPM_FO_25 (Vigie)",
            data=generate_official_excel_pack("FO_25"),
            file_name=f"DPM_FO_25_Vigie_{date.today()}.xlsx",
            use_container_width=True,
            key="dl_fo25"
        )
        ex3.download_button(
            "📥 Exporter Registre Complet (VHF & Toutes Classes)",
            data=generate_official_excel_pack("FO_24_25_ALL"),
            file_name=f"DPM_Registre_Equipements_Complet_{date.today()}.xlsx",
            use_container_width=True,
            key="dl_fo24_25_all"
        )

    with tab2:
        with st.form("add_fo24_25"):
            c1, c2, c3 = st.columns(3)
            with c1:
                classe = st.selectbox("Classe (`DMP_PR_02`)", classes_pr02)
                article = st.text_input("Article")
                ref_serie = st.text_input("Numéro de Série / Référence")
                cout_est = st.number_input("Coût Estimé (MAD)", min_value=0.0, step=100.0)
            with c2:
                st.markdown("**En utilisation**")
                u_etat = st.selectbox("Etat (En utilisation)", etats_list)
                u_qte = st.number_input("Quantité (En utilisation)", min_value=0, value=1)
                u_emp = st.text_input("Emplacement", value="La DPM")
                st.markdown("**En Stock**")
                s_qte = st.number_input("Quantité (En stock)", min_value=0, value=0)
                s_loc = st.text_input("Localisation", value="Magasin DPM")
            with c3:
                st.markdown("**Besoins & Garantie**")
                b_achat = st.text_input("Besoins — Achat", value="Non")
                b_repa = st.text_input("Besoins — Réparation", value="Non")
                dt_rec = st.date_input("Date de Réception", date.today())
                dt_gar = st.date_input("Échéance Garantie", date.today() + timedelta(days=730))
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
                    st.success("Tous les paramètres ont été mis à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
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
    st.markdown('<div class="section-title"><h3>📦 DPM_FO_26 & DPM_FO_27 — L\'Etat des Consommations Générales & Pharmaceutiques de La DPM</h3><span class="section-badge">FO_26 / FO_27</span></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 États & Exports Officiels", "➕ Nouvel Article", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

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
                st.success("Tableau mis à jour !")
                st.rerun()

            df_calc = df_c.copy()
            df_calc['Coût Début'] = df_calc['debut_qte'] * df_calc['debut_prix_unit']
            df_calc['Coût Livré'] = df_calc['livre_qte'] * df_calc['livre_prix_unit']
            df_calc['Coût Fin'] = df_calc['fin_qte'] * df_calc['fin_prix_unit']
            df_calc['Cout des Consommations'] = (df_calc['Coût Début'] + df_calc['Coût Livré']) - df_calc['Coût Fin']
            st.metric("Le Coût des Consommations de la période", f"{df_calc['Cout des Consommations'].sum():,.2f} MAD")
        else:
            st.info("Aucun article enregistré.")

        ex1, ex2 = st.columns(2)
        ex1.download_button(
            "📥 Exporter DPM_FO_26 Officiel (.xlsx)",
            data=generate_official_excel_pack("FO_26"),
            file_name=f"DPM_FO_26_Consommations_Generales_{date.today()}.xlsx",
            use_container_width=True,
            key="dl_fo26"
        )
        ex2.download_button(
            "📥 Exporter DPM_FO_27 Officiel (.xlsx)",
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
                emp = st.text_input("Emplacement", value="La DPM")
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
                    st.success("Mis à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo26_27_consommables WHERE id=?", (id_sel,))
                    conn.commit()
                    st.warning("Supprimé.")
                    st.rerun()
        else:
            st.info("Aucun article à modifier.")

# ==============================================================================
# MODULE 5 : REGISTRE DE LA CONSOMMATION DE LA PILOTINE (DPM_FO_28)
# ==============================================================================
elif menu == "🚤 Consommation Pilotine (DPM_FO_28)":
    st.markdown('<div class="section-title"><h3>🚤 DPM_FO_28 — Le Registre de La Consommation de la Pilotine</h3><span class="section-badge">FO_28</span></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 Registre & Export Officiel FO_28", "➕ Nouveau Relevé", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

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
            "📥 Exporter DPM_FO_28 Officiel (.xlsx)",
            data=generate_official_excel_pack("FO_28"),
            file_name=f"DPM_FO_28_Consommation_Pilotine_{date.today()}.xlsx",
            key="dl_fo28"
        )

    with tab2:
        with st.form("add_fo28"):
            nom_pil = st.text_input("Identification de la Pilotine", value="Pilotine")
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
                    st.success("Mis à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo28_pilotine WHERE id=?", (id_sel,))
                    conn.commit()
                    st.warning("Supprimé.")
                    st.rerun()
        else:
            st.info("Aucun relevé disponible.")

# ==============================================================================
# MODULE 6 : REGISTRE DES EPIs (DPM_FO_29)
# ==============================================================================
elif menu == "🦺 Registre des EPIs (DPM_FO_29)":
    st.markdown('<div class="section-title"><h3>🦺 DPM_FO_29 — Le Registre des EPIs</h3><span class="section-badge">FO_29</span></div>', unsafe_allow_html=True)
    etats_epi = ["Neuf", "Bon", "Moyen", "À remplacer"]
    tab1, tab2, tab3 = st.tabs(["📋 Registre & Export Officiel FO_29", "➕ Nouvel EPI", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        df_e = pd.read_sql_query("SELECT * FROM fo29_epis", conn)
        if not df_e.empty:
            edited_e = st.data_editor(df_e, use_container_width=True, disabled=["id"], num_rows="fixed", key="ed_fo29")
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
                st.success("Registre EPI mis à jour !")
                st.rerun()
        else:
            st.info("Aucun EPI enregistré.")

        st.download_button(
            "📥 Exporter DPM_FO_29 Officiel (.xlsx)",
            data=generate_official_excel_pack("FO_29"),
            file_name=f"DPM_FO_29_Registre_EPIs_{date.today()}.xlsx",
            key="dl_fo29"
        )

    with tab2:
        with st.form("add_fo29"):
            art = st.text_input("Article")
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
elif menu == "✅ Checklists Achats & Maint. (CL_06/07)":
    st.markdown('<div class="section-title"><h3>✅ DPM_CL_06 (Spécifications d\'Achat) & DPM_CL_07 (Utilisation et Maintenance)</h3><span class="section-badge">CL_06 / CL_07</span></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 Checklists & Export Officiel", "➕ Nouvelle Fiche", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

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
                st.success("Checklists mises à jour !")
                st.rerun()
        else:
            st.info("Aucune checklist enregistrée.")

        st.download_button(
            "📥 Exporter DPM_CL_06 & DPM_CL_07 Officiels (.xlsx)",
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
                    st.success("Fiche mise à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM cl06_07_checklists WHERE id=?", (id_sel,))
                    conn.commit()
                    st.warning("Fiche supprimée.")
                    st.rerun()
        else:
            st.info("Aucune fiche checklist enregistrée.")

# ==============================================================================
# MODULE 8 : FORMULAIRE DE PRÉPARATION DU BUDGET (DPM_FO_30)
# ==============================================================================
elif menu == "💰 Préparation du Budget (DPM_FO_30)":
    st.markdown('<div class="section-title"><h3>💰 DPM_FO_30 — Le Formulaire de Préparation du Budget de La DPM</h3><span class="section-badge">FO_30</span></div>', unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📊 Formulaire Officiel & Export FO_30", "➕ Ajouter une Ligne Budgétaire", "✏️ Modifier (Tous les paramètres) / 🗑️ Supprimer"])

    with tab1:
        if st.button("🔄 Synchroniser automatiquement les coûts depuis les registres d'équipements", key="btn_sync_budget"):
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
            st.success("Synchronisation budgétaire effectuée !")
            st.rerun()

        df_b = pd.read_sql_query("SELECT * FROM fo30_budget_lignes", conn)
        if not df_b.empty:
            df_b['Variation Budget (MAD)'] = df_b['cout_estime_n'] - df_b['cout_annee_prec']
            df_conso_b = df_b[df_b['type_ligne'] == 'Consommation (Générale / Pharmacie)']
            df_invest_b = df_b[df_b['type_ligne'] == 'Investissement']

            st.markdown("##### 1. Consommations Générale / Consommation Pharmacie")
            st.dataframe(df_conso_b[['id', 'classe_rubrique', 'article_investissement', 'prix_unitaire_estime', 'besoin_unites_estime', 'cout_estime_n', 'qte_annee_prec', 'cout_annee_prec', 'Variation Budget (MAD)', 'observations']], use_container_width=True, hide_index=True)

            st.markdown("##### 2. Partie Investissements : Formations / EPIs / Tenue / Peinture / Construction / Vigie / PCs / Etc.")
            st.dataframe(df_invest_b[['id', 'classe_rubrique', 'article_investissement', 'justification', 'cout_estime_n', 'cout_annee_prec', 'Variation Budget (MAD)', 'observations']], use_container_width=True, hide_index=True)

            tot_n = df_b['cout_estime_n'].sum()
            tot_prec = df_b['cout_annee_prec'].sum()
            k1, k2, k3 = st.columns(3)
            k1.metric("Budget année précédente", f"{tot_prec:,.2f} MAD")
            k2.metric("Budget année en objet", f"{tot_n:,.2f} MAD")
            k3.metric("Variation Budget", f"{tot_n - tot_prec:+,.2f} MAD")
        else:
            st.info("Aucune ligne budgétaire enregistrée.")

        st.download_button(
            "📥 Exporter DPM_FO_30 Officiel (.xlsx)",
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
                    st.success("Ligne budgétaire mise à jour !")
                    st.rerun()
                if b2.form_submit_button("🗑️ Supprimer définitivement"):
                    c.execute("DELETE FROM fo30_budget_lignes WHERE id=?", (id_sel,))
                    conn.commit()
                    st.warning("Ligne budgétaire supprimée.")
                    st.rerun()
        else:
            st.info("Aucune ligne budgétaire enregistrée.")

# ==============================================================================
# 6. PIED DE PAGE OFFICIEL DE L'APPLICATION
# ==============================================================================
st.markdown("""
<div class="nwm-footer">
    <strong>NADOR WEST MED — La DPM</strong> • Système de Management ISPO • Gestion des Ressources Matérielles<br>
    Référentiel : DMP_PR_02 | DPM_FI_02 | Formulaires DPM_FO_23 à DPM_FO_30 | Checklists DPM_CL_06 & DPM_CL_07
</div>
""", unsafe_allow_html=True)

# === FIN DU SCRIPT APP.PY ===
