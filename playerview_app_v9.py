import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

# ── CONFIGURAZIONE PAGINA ──────────────────────────────────────────────────
st.set_page_config(
    page_title="PlayerView — Alcione Milano",
    page_icon="🟠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS PREMIUM ALCIONE ───────────────────────────────────────────────────
LOGO_PATH = "Logo_ALCIONE_Nuova_Stagione.svg"

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* BASE */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #050507;
        color: #ffffff;
    }
    .stApp { background-color: #050507; }
    
    /* BOTTONI */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B00, #ff8c00);
        color: white;
        border: none;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        border-radius: 2px;
        padding: 12px 28px;
        font-size: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255,107,0,0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #cc5500, #FF6B00);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255,107,0,0.4);
    }
    
    /* SELECTBOX */
    .stSelectbox > div > div {
        background: #0d0d12;
        border: 1px solid #1e1e2a;
        color: #ffffff;
        border-radius: 2px;
        font-family: 'Inter', sans-serif;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        border-bottom: 1px solid #1e1e2a;
        gap: 0;
    }
    .stTabs [data-baseweb="tab"] {
        color: #555;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        font-size: 11px;
        padding: 16px 28px;
        border-bottom: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] {
        color: #FF6B00 !important;
        border-bottom: 2px solid #FF6B00 !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #ffffff !important;
        background: rgba(255,255,255,0.03) !important;
    }
    
    /* INPUT */
    .stTextInput > div > div > input {
        background: #0d0d12;
        border: 1px solid #1e1e2a;
        border-radius: 2px;
        color: #ffffff;
        padding: 14px 18px;
        font-size: 14px;
        font-family: 'Inter', sans-serif;
        transition: border-color 0.2s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #FF6B00 !important;
        box-shadow: 0 0 0 1px rgba(255,107,0,0.2) !important;
    }
    .stTextInput label {
        color: #666 !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
    }
    
    /* DATAFRAME */
    div[data-testid="stDataFrame"] {
        background: #0d0d12;
        border: 1px solid #1e1e2a;
        border-radius: 2px;
    }
    
    /* METRICHE */
    div[data-testid="metric-container"] {
        background: #0d0d12;
        border: 1px solid #1e1e2a;
        border-radius: 2px;
        padding: 20px;
    }
    
    /* EXPANDER */
    .streamlit-expanderHeader {
        background: #0d0d12 !important;
        border: 1px solid #1e1e2a !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        border-radius: 2px !important;
    }
    
    /* SCROLLBAR */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #050507; }
    ::-webkit-scrollbar-thumb { background: #FF6B00; border-radius: 2px; }
    
    /* DIVIDER */
    hr { border-color: #1e1e2a; margin: 28px 0; }
    
    /* HIDE STREAMLIT */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* SECTION TITLES */
    h5 { 
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        font-size: 11px !important;
        letter-spacing: 3px !important;
        text-transform: uppercase !important;
        color: #555 !important;
        margin-bottom: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# ── BENCHMARK PER RUOLO ────────────────────────────────────────────────────
# Soglie minime di efficacia per ogni principio di gioco, divise per ruolo
BENCHMARK = {
    "DC": {
        "Passaggi Tot, Passaggi Sbagliati": ("Passaggi", 75),
        "Duelli Difensivi Tot, Duelli Difensivi Persi": ("Duelli Difensivi", 65),
        "Duelli Aerei Tot, Duelli Aerei Persi": ("Duelli Aerei", 60),
        "Intercetti Tot, Intercetti Sbagliati": ("Intercetti", 60),
    },
    "AS": {
        "Passaggi Tot, Passaggi Sbagliati": ("Passaggi", 70),
        "Tiri Tot, Tiri Fuori": ("Tiri", 55),
        "Dribbling Tot, Dribbling sbagliati": ("Dribbling", 60),
        "Tagli a partita": ("Tagli", None),  # dato assoluto, nessun benchmark %
    }
}

# ── ANAGRAFICA GIOCATORI ──────────────────────────────────────────────────
ANAGRAFICA = {
    "demaria": {
        "data_nascita": "14/02/2011",
        "nazionalita": "🇮🇹 Italiana",
        "piede": "Destro",
        "altezza": "172 cm",
        "peso": "62 kg",
    },
    "fortin": {
        "data_nascita": "22/06/2011",
        "nazionalita": "🇮🇹 Italiana",
        "piede": "Destro",
        "altezza": "168 cm",
        "peso": "58 kg",
    },
}

# ── CREDENZIALI ────────────────────────────────────────────────────────────
CREDENZIALI = {
    "demaria": {"password": "1234", "ruolo": "player", "nome": "Demaria"},
    "fortin":  {"password": "1234", "ruolo": "player", "nome": "Fortin"},
    "coach":   {"password": "admin", "ruolo": "coach",  "nome": "Staff"},
}

# ── LETTURA EXCEL ──────────────────────────────────────────────────────────

def carica_dati_excel(percorso_file):
    """
    Legge il file Excel del progetto tesi e restituisce
    un dizionario con i dati di ogni giocatore.
    
    Il file Excel ha due sezioni separate:
    - Riga 1: intestazioni DC (Demaria)
    - Riga 2: dati DC
    - Riga 8: intestazioni AS (Fortin)  
    - Riga 9: dati AS
    """
    try:
        df = pd.read_excel(percorso_file, header=None)
        
        giocatori = {}
        
        # Trova le righe che contengono dati (hanno "Anno" nella prima colonna)
        # e le righe immediatamente successive che contengono i valori
        intestazione_rows = []
        for i, row in df.iterrows():
            if str(row[0]).strip() == "Anno":
                intestazione_rows.append(i)
        
        for idx_header in intestazione_rows:
            # Prendi le intestazioni
            headers = [str(df.iloc[idx_header, c]).strip() for c in range(len(df.columns))]
            
            # Prendi la riga dati subito dopo
            idx_data = idx_header + 1
            if idx_data >= len(df):
                continue
            
            # Estrai i valori base
            giocatore_nome = str(df.iloc[idx_data, 1]).strip()
            ruolo = str(df.iloc[idx_data, 2]).strip()
            partita = str(df.iloc[idx_data, 3]).strip()
            
            # Gestisci la data
            data_raw = df.iloc[idx_data, 4]
            if pd.notna(data_raw):
                if isinstance(data_raw, datetime):
                    data_str = data_raw.strftime("%d/%m/%Y")
                else:
                    try:
                        data_str = pd.to_datetime(data_raw).strftime("%d/%m/%Y")
                    except:
                        data_str = str(data_raw)
            else:
                data_str = "N/D"
            
            # Estrai i KPI e le clip (colonne dalla 5 in poi)
            kpi_data = {}
            clip_data = {}
            for col_idx in range(5, len(headers)):
                col_name = headers[col_idx]
                if col_name in ("nan", "", "NaN"):
                    continue
                valore = df.iloc[idx_data, col_idx]
                if pd.isna(valore):
                    continue
                val_str = str(valore).strip()
                # Colonne clip iniziano con Clip1_ o Clip2_
                if col_name.startswith("Clip1_") or col_name.startswith("Clip2_"):
                    if val_str and val_str.lower() != "x" and val_str.lower() != "nan":
                        principio = col_name.replace("Clip1_", "").replace("Clip2_", "")
                        if principio not in clip_data:
                            clip_data[principio] = []
                        clip_data[principio].append(val_str)
                else:
                    kpi_data[col_name] = val_str
            
            # Salva nel dizionario
            key = giocatore_nome.lower()
            if key not in giocatori:
                giocatori[key] = []
            
            giocatori[key].append({
                "nome": giocatore_nome,
                "ruolo": ruolo,
                "partita": partita,
                "data": data_str,
                "kpi_raw": kpi_data,
                "clips": clip_data
            })
        
        return giocatori
    
    except Exception as e:
        st.error(f"Errore nella lettura del file Excel: {e}")
        return {}

def parse_kpi(kpi_raw, ruolo):
    """
    Converte i valori grezzi dell'Excel in dati strutturati con percentuali.
    Es: "21, 5" → tot=21, sbagliati=5, ok=16, pct=76%
    """
    bench = BENCHMARK.get(ruolo, {})
    kpi_elaborati = []
    
    for col_name, valore in kpi_raw.items():
        # Trova il nome leggibile e il benchmark
        info_bench = bench.get(col_name)
        if info_bench is None:
            # Prova a trovare una corrispondenza parziale
            for k in bench:
                if any(part in col_name for part in k.split(",")):
                    info_bench = bench[k]
                    break
        
        if info_bench is None:
            nome_kpi = col_name
            soglia = None
        else:
            nome_kpi, soglia = info_bench
        
        # Parsa il valore
        if "," in str(valore):
            # Formato "tot, sbagliati"
            parti = str(valore).split(",")
            try:
                tot = int(parti[0].strip())
                sbagliati = int(parti[1].strip())
                ok = tot - sbagliati
                pct = round((ok / tot) * 100) if tot > 0 else 0
                kpi_elaborati.append({
                    "nome": nome_kpi,
                    "col_name": col_name,
                    "tot": tot,
                    "sbagliati": sbagliati,
                    "ok": ok,
                    "pct": pct,
                    "soglia": soglia,
                    "tipo": "percentuale"
                })
            except:
                pass
        else:
            # Dato assoluto (es. tagli) — verrà calcolata la media per partita
            try:
                val = int(float(str(valore).strip()))
                kpi_elaborati.append({
                    "nome": nome_kpi,
                    "col_name": col_name,
                    "tot": val,
                    "sbagliati": 0,
                    "ok": val,
                    "pct": None,
                    "soglia": None,
                    "tipo": "media_partita"
                })
            except:
                pass
    
    return kpi_elaborati

def calcola_rating(kpi_list):
    """Calcola il rating della partita basandosi sulla media degli esiti positivi."""
    percentuali = [k["pct"] for k in kpi_list if k["tipo"] == "percentuale" and k["pct"] is not None]
    if not percentuali:
        return 0.0
    media = sum(percentuali) / len(percentuali)
    rating = 1 + (media / 100) * 9
    return round(rating, 1)

def get_colore(pct, soglia):
    """Restituisce il colore semaforo."""
    if soglia is None or pct is None:
        return "yellow"
    if pct >= soglia:
        if abs(pct - soglia) <= 5:
            return "yellow"
        return "green"
    return "red"

def get_emoji(colore):
    return {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(colore, "⚪")

# ── GRAFICI ────────────────────────────────────────────────────────────────

def grafico_kpi(kpi_list, key_suffix=""):
    """Grafico a barre orizzontali con i KPI."""
    nomi, pcts, soglie, colori_hex = [], [], [], []
    
    color_map = {"green": "#00e676", "yellow": "#ffea00", "red": "#ff1744"}
    
    for k in kpi_list:
        if k["tipo"] != "percentuale":
            continue
        colore = get_colore(k["pct"], k["soglia"])
        nomi.append(k["nome"])
        pcts.append(k["pct"])
        soglie.append(k["soglia"])
        colori_hex.append(color_map[colore])
    
    if not nomi:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=pcts, y=nomi, orientation='h',
        marker_color=colori_hex,
        text=[f'{p}%' for p in pcts],
        textposition='outside',
        textfont=dict(color='#f0f0f0', size=14, family='Barlow Condensed'),
        name='% Esiti Positivi',
    ))
    
    # Linee benchmark
    for i, s in enumerate(soglie):
        if s is not None:
            fig.add_shape(type="line", x0=s, x1=s, y0=i-0.4, y1=i+0.4,
                         line=dict(color="#FF6B00", width=2, dash="dash"))
    
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines',
                             line=dict(color='#FF6B00', width=2, dash='dash'),
                             name='Benchmark ruolo'))
    
    fig.update_layout(
        plot_bgcolor='#0d0d12', paper_bgcolor='#050507',
        font=dict(color='#ffffff', family='Inter'),
        xaxis=dict(
            range=[0, 120],
            showgrid=True,
            gridcolor='#1e1e2a',
            gridwidth=1,
            ticksuffix='%',
            tickfont=dict(color='#555', size=11),
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(color='#ffffff', size=12, family='Inter'),
        ),
        legend=dict(
            bgcolor='#0d0d12',
            bordercolor='#1e1e2a',
            borderwidth=1,
            font=dict(color='#888', size=11),
        ),
        margin=dict(l=20, r=70, t=20, b=20),
        height=280,
        bargap=0.3,
    )
    return fig

def grafico_torta(kpi_list, key_suffix=""):
    """Grafico a torta distribuzione positivi/negativi."""
    tot_pos = sum(k["ok"] for k in kpi_list if k["tipo"] == "percentuale")
    tot_neg = sum(k["sbagliati"] for k in kpi_list if k["tipo"] == "percentuale")
    
    if tot_pos + tot_neg == 0:
        return None
    
    pct_pos = round(tot_pos / (tot_pos + tot_neg) * 100)
    
    fig = go.Figure(go.Pie(
        labels=['Positivi (P)', 'Negativi (N)'],
        values=[tot_pos, tot_neg],
        marker_colors=['#00e676', '#ff1744'],
        hole=0.6,
        textfont=dict(color='white', size=13),
        hovertemplate='%{label}: %{value} (%{percent})<extra></extra>',
    ))
    fig.update_layout(
        plot_bgcolor='#0d0d12', paper_bgcolor='#0d0d12',
        font=dict(color='#ffffff', family='Inter'),
        legend=dict(
            bgcolor='#0d0d12',
            font=dict(color='#888', size=11),
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        height=200,
        annotations=[dict(
            text=f'{pct_pos}%',
            font=dict(size=24, color='#00e676', family='Inter'),
            showarrow=False
        )]
    )
    return fig

# ── LOGIN ──────────────────────────────────────────────────────────────────

def mostra_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        c1, c2, c3 = st.columns([1.5, 1, 1.5])
        with c2:
            st.image(LOGO_PATH, use_container_width=True)
        st.markdown("""
        <div style="text-align:center; margin-top:16px; margin-bottom:32px;">
            <div style="font-size:10px; font-weight:700; letter-spacing:5px; text-transform:uppercase; color:#FF6B00;">ALCIONE MILANO · STAGIONE 2025/26</div>
            <div style="font-size:48px; font-weight:900; letter-spacing:4px; text-transform:uppercase; color:#ffffff; line-height:1; margin-top:8px;">PLAYER<span style="color:#FF6B00">VIEW</span></div>
            <div style="font-size:11px; letter-spacing:3px; text-transform:uppercase; color:#444; margin-top:8px;">Piattaforma individuale di analisi video</div>
            <div style="width:40px; height:2px; background:#FF6B00; margin:20px auto;"></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        username = st.text_input("Username", placeholder="es. demaria")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        if st.button("ENTRA →", use_container_width=True):
            u = username.lower().strip()
            if u in CREDENZIALI and CREDENZIALI[u]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = u
                st.session_state["ruolo_utente"] = CREDENZIALI[u]["ruolo"]
                st.rerun()
            else:
                st.error("Credenziali non valide.")
        st.markdown("""
        <div style="text-align:center; margin-top:20px; font-size:11px; color:#555; line-height:2; border-top:1px solid #2a2a2a; padding-top:16px;">
            <span style="letter-spacing:1px; text-transform:uppercase;">Demo access</span><br>
            Giocatori: <span style="color:#FF6B00">demaria / 1234</span> · 
            <span style="color:#FF6B00">fortin / 1234</span><br>
            Staff: <span style="color:#FF6B00">coach / admin</span>
        </div>
        """, unsafe_allow_html=True)


def mostra_giocatore(username, dati_excel, key_prefix=""):
    """Dashboard individuale del giocatore."""
    
    nome_cercato = CREDENZIALI[username]["nome"]
    partite = dati_excel.get(username, [])
    
    if not partite:
        st.warning(f"Nessun dato trovato per {nome_cercato} nel file Excel.")
        st.info("Assicurati che il file Excel sia nella stessa cartella dell'app.")
        return
    
    # Selezione partita
    opzioni_partite = [f"{p['partita']} — {p['data']}" for p in partite]
    
    if len(partite) > 1:
        scelta = st.selectbox("📅 Seleziona partita", opzioni_partite,
                              key=f"sel_partita_{key_prefix}_{username}")
        idx_partita = opzioni_partite.index(scelta)
    else:
        idx_partita = 0
        st.markdown(f"""
        <div style="background:#1a1a1a; border-left:3px solid #FF6B00; padding:12px 20px; margin-bottom:16px;">
            <span style="color:#888; font-size:11px; text-transform:uppercase; letter-spacing:2px;">
                Partita: <strong style="color:#FF6B00">{partite[0]['partita']}</strong> &nbsp;|&nbsp;
                Data: <strong style="color:#FF6B00">{partite[0]['data']}</strong> &nbsp;|&nbsp;
                Campionato: <strong style="color:#FF6B00">Nazionale U15</strong>
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    partita = partite[idx_partita]
    ruolo = partita["ruolo"]
    kpi_list = parse_kpi(partita["kpi_raw"], ruolo)
    rating = calcola_rating(kpi_list)
    rating_color = "#00e676" if rating >= 7 else ("#ffea00" if rating >= 6 else "#ff1744")
    
    # Header giocatore premium
    col_logo_h, col_info_h = st.columns([1, 7])
    with col_logo_h:
        st.image(LOGO_PATH, width=80)
    with col_info_h:
        st.markdown(f"""
        <div style="padding-top:8px;">
            <div style="font-size:44px; font-weight:900; text-transform:uppercase; letter-spacing:3px; color:#ffffff; line-height:1;">{partita['nome'].upper()}</div>
            <div style="font-size:11px; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:#555; margin-top:8px;">
                <span style="color:#FF6B00">{ruolo}</span> &nbsp;·&nbsp; Alcione Milano &nbsp;·&nbsp; U15 Nazionale &nbsp;·&nbsp; Stagione 2025/26
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

    # Dati anagrafici
    ana = ANAGRAFICA.get(username, {})
    if ana:
        st.markdown("""
        <div style="font-size:10px; font-weight:700; letter-spacing:3px; text-transform:uppercase; color:#555; margin-bottom:10px;">Scheda Anagrafica</div>
        """, unsafe_allow_html=True)
        col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns(5)
        items = [
            ("Data di Nascita", ana.get("data_nascita", "-")),
            ("Nazionalità", ana.get("nazionalita", "-")),
            ("Piede", ana.get("piede", "-")),
            ("Altezza", ana.get("altezza", "-")),
            ("Peso", ana.get("peso", "-")),
        ]
        for col, (label, value) in zip([col_a1, col_a2, col_a3, col_a4, col_a5], items):
            with col:
                st.markdown(f"""
                <div style="background:#0d0d12; border:1px solid #1e1e2a; border-top:2px solid #FF6B00; padding:14px 16px;">
                    <div style="font-size:9px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:#555; margin-bottom:6px;">{label}</div>
                    <div style="font-size:15px; font-weight:600; color:#ffffff;">{value}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # Rating
    col_r, col_p, col_c = st.columns(3)
    with col_r:
        st.markdown(f"""
        <div style="background:#1a1a1a; border-top:3px solid {rating_color}; padding:20px 24px; margin-bottom:16px;">
            <div style="font-size:10px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:#888; margin-bottom:8px;">Rating Partita</div>
            <div style="font-family:'Barlow Condensed',sans-serif; font-weight:900; font-size:44px; color:{rating_color}; line-height:1;">{rating}</div>
            <div style="font-size:12px; color:#888; margin-top:4px;">Basato su esiti P/N</div>
        </div>
        """, unsafe_allow_html=True)
    with col_p:
        st.markdown(f"""
        <div style="background:#1a1a1a; border-top:3px solid #FF6B00; padding:20px 24px; margin-bottom:16px;">
            <div style="font-size:10px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:#888; margin-bottom:8px;">Partita</div>
            <div style="font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:22px; color:#FF6B00; line-height:1; margin-top:6px;">{partita['partita']}</div>
            <div style="font-size:12px; color:#888; margin-top:4px;">Stagione 2025/26</div>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown(f"""
        <div style="background:#1a1a1a; border-top:3px solid #FF6B00; padding:20px 24px; margin-bottom:16px;">
            <div style="font-size:10px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:#888; margin-bottom:8px;">Data</div>
            <div style="font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:22px; color:#FF6B00; line-height:1; margin-top:6px;">{partita['data']}</div>
            <div style="font-size:12px; color:#888; margin-top:4px;">Campionato Nazionale U15</div>
        </div>
        """, unsafe_allow_html=True)
    
    # KPI cards
    st.markdown("##### 📊 Key Performance Indicators")
    cols_kpi = st.columns(len(kpi_list))
    
    color_map = {"green": "#00e676", "yellow": "#ffea00", "red": "#ff1744"}
    
    for i, k in enumerate(kpi_list):
        with cols_kpi[i]:
            if k["tipo"] == "percentuale":
                colore = get_colore(k["pct"], k["soglia"])
                c = color_map[colore]
                emoji = get_emoji(colore)
                pct_display = f"{k['pct']}%"
                nums = f"{k['ok']} su {k['tot']}"
                bar_w = k["pct"]
                if k["soglia"]:
                    diff = k["pct"] - k["soglia"]
                    if colore == "green":
                        bench_text = f"✓ Sopra benchmark ({k['soglia']}%)"
                    elif colore == "yellow":
                        bench_text = f"⚠ Vicino al benchmark ({k['soglia']}%)"
                    else:
                        bench_text = f"✗ Sotto benchmark ({k['soglia']}%)"
                else:
                    bench_text = ""
            else:
                tutti_i_tagli = []
                for p in partite:
                    kpi_temp = parse_kpi(p["kpi_raw"], ruolo)
                    for kt in kpi_temp:
                        if kt["nome"] == k["nome"] and kt["tipo"] == "media_partita":
                            tutti_i_tagli.append(kt["tot"])
                if len(tutti_i_tagli) > 1:
                    media = round(sum(tutti_i_tagli) / len(tutti_i_tagli), 1)
                    pct_display = str(media)
                    nums = f"Media su {len(tutti_i_tagli)} partite"
                    bench_text = f"Questa partita: {k['tot']} tagli"
                else:
                    pct_display = str(k["tot"])
                    nums = "1 partita disponibile"
                    bench_text = "Media disponibile con piu partite"
                c = "#ffea00"
                emoji = "🟡"
                bar_w = 50
            
            st.markdown(f"""
            <div style="background:#1a1a1a; border-top:3px solid {c}; padding:18px 20px; margin-bottom:8px; position:relative;">
                <div style="font-size:10px; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; color:#888; margin-bottom:10px;">
                    {emoji} {k['nome']}
                </div>
                <div style="font-family:'Barlow Condensed',sans-serif; font-weight:900; font-size:42px; color:{c}; line-height:1; margin-bottom:10px;">
                    {pct_display}
                </div>
                <div style="height:4px; background:#2a2a2a; border-radius:2px; margin-bottom:8px;">
                    <div style="height:100%; width:{bar_w}%; background:{c}; border-radius:2px;"></div>
                </div>
                <div style="font-size:11px; color:#888; margin-bottom:6px;">{nums}</div>
                <div style="font-size:10px; color:#888;">{bench_text}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Grafici
    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        st.markdown("##### 📈 Performance per Principio di Gioco")
        fig_kpi = grafico_kpi(kpi_list, key_suffix=f"{key_prefix}_{username}_{idx_partita}")
        if fig_kpi:
            st.plotly_chart(fig_kpi, use_container_width=True,
                           key=f"kpi_chart_{key_prefix}_{username}_{idx_partita}")
    
    with col_g2:
        st.markdown("##### 🔵 Distribuzione Esiti")
        fig_torta = grafico_torta(kpi_list)
        if fig_torta:
            st.plotly_chart(fig_torta, use_container_width=True,
                           key=f"torta_chart_{key_prefix}_{username}_{idx_partita}")
        tot_pos = sum(k["ok"] for k in kpi_list if k["tipo"] == "percentuale")
        tot_neg = sum(k["sbagliati"] for k in kpi_list if k["tipo"] == "percentuale")
        st.markdown(f"""
        <div style="background:#1a1a1a; padding:10px; text-align:center; font-size:12px; color:#888;">
            Totale: <strong style="color:#f0f0f0">{tot_pos+tot_neg}</strong> &nbsp;|&nbsp;
            <span style="color:#00e676">✓ {tot_pos}</span> &nbsp;·&nbsp;
            <span style="color:#ff1744">✗ {tot_neg}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabella riepilogo
    st.markdown("##### 📋 Riepilogo Statistico")
    rows = []
    for k in kpi_list:
        if k["tipo"] == "percentuale":
            colore = get_colore(k["pct"], k["soglia"])
            emoji = get_emoji(colore)
            stato = f"{emoji} {'Sopra' if colore=='green' else ('Vicino a' if colore=='yellow' else 'Sotto')} benchmark"
            rows.append({
                "Principio": k["nome"],
                "Totale": k["tot"],
                "Positivi": k["ok"],
                "Negativi": k["sbagliati"],
                "% Efficacia": f"{k['pct']}%",
                "Benchmark": f"{k['soglia']}%" if k["soglia"] else "-",
                "Stato": stato
            })
        else:
            tutti = [kt["tot"] for p in partite for kt in parse_kpi(p["kpi_raw"], ruolo) if kt["nome"] == k["nome"] and kt["tipo"] == "media_partita"]
            media_str = str(round(sum(tutti)/len(tutti), 1)) if len(tutti) > 1 else str(k["tot"])
            rows.append({
                "Principio": k["nome"],
                "Totale": k["tot"],
                "Positivi": k["tot"],
                "Negativi": 0,
                "% Efficacia": f"{media_str} (media/partita)",
                "Benchmark": "-",
                "Stato": "🟡 Media per partita"
            })
    
    df_table = pd.DataFrame(rows)
    st.dataframe(df_table, use_container_width=True, hide_index=True)

    # ── ARCHIVIO CLIP ──
    st.markdown("---")
    st.markdown("##### 🎬 Archivio Clip")
    clips = partita.get("clips", {})
    if clips:
        st.markdown("""
        <div style="font-size:11px; color:#555; margin-bottom:16px; font-style:italic;">
            Clip selezionate per principio di gioco. In produzione i link puntano a Google Drive.
        </div>
        """, unsafe_allow_html=True)
        import os
        for principio, clip_list in clips.items():
            if clip_list:
                with st.expander(f"📹 {principio} — {len(clip_list)} clip disponibili"):
                    for clip_path in clip_list:
                        esito_color = "#00e676" if "_P_" in clip_path else "#ff1744"
                        esito_label = "P" if "_P_" in clip_path else "N"
                        nome_clip = os.path.basename(clip_path).replace(".mp4", "").replace("_", " ")
                        st.markdown(f"""
                        <div style="background:#0d0d12; border-left:3px solid {esito_color}; padding:10px 14px; margin-bottom:8px;">
                            <span style="font-size:13px; color:#ffffff;">{nome_clip}</span>
                            <span style="background:rgba(255,255,255,0.05); color:{esito_color}; padding:2px 8px; font-size:10px; font-weight:700; margin-left:8px;">{esito_label}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        if os.path.exists(clip_path):
                            st.video(clip_path)
                        else:
                            st.caption(f"⚠ File non trovato: {clip_path}")
    else:
        st.info("Nessuna clip disponibile per questa partita.")

# ── VISTA STAFF ────────────────────────────────────────────────────────────

def mostra_staff(dati_excel):
    """Dashboard staff con tutti i giocatori."""
    col_logo_c, col_info_c = st.columns([1, 7])
    with col_logo_c:
        st.image(LOGO_PATH, width=64)
    with col_info_c:
        st.markdown("""
        <div style="padding-top:4px;">
            <div style="font-size:38px; font-weight:900; text-transform:uppercase; letter-spacing:2px; color:#ffffff; line-height:1;">Dashboard <span style="color:#FF6B00">Staff</span></div>
            <div style="font-size:11px; letter-spacing:2px; text-transform:uppercase; color:#555; margin-top:6px;">Alcione Milano · U15 Nazionale · Stagione 2025/26</div>
        </div>
        <div style="height:2px; background:linear-gradient(90deg, #FF6B00, transparent); margin-top:16px; margin-bottom:8px;"></div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Costruisci tabella riassuntiva da Excel
    rows_coach = []
    alerts = []
    
    for username, cred in CREDENZIALI.items():
        if cred["ruolo"] != "player":
            continue
        
        partite = dati_excel.get(username, [])
        if not partite:
            continue
        
        # Ultima partita
        ultima = partite[-1]
        ruolo = ultima["ruolo"]
        kpi_list = parse_kpi(ultima["kpi_raw"], ruolo)
        rating = calcola_rating(kpi_list)
        
        row = {
            "Giocatore": ultima["nome"],
            "Ruolo": ruolo,
            "Ultima Partita": ultima["partita"],
            "Data": ultima["data"],
            "Rating": rating,
        }
        
        alert_count = 0
        for k in kpi_list:
            if k["tipo"] != "percentuale":
                continue
            colore = get_colore(k["pct"], k["soglia"])
            emoji = get_emoji(colore)
            row[k["nome"]] = f"{emoji} {k['pct']}%"
            if colore == "red":
                alert_count += 1
                alerts.append(f"**{ultima['nome']}** — {k['nome']} sotto soglia ({k['pct']}% vs benchmark {k['soglia']}%)")
        
        row["Stato"] = "🔴 ALERT" if alert_count > 0 else ("🟡 ATTENZIONE" if any(
            get_colore(k["pct"], k["soglia"]) == "yellow"
            for k in kpi_list if k["tipo"] == "percentuale"
        ) else "🟢 OK")
        
        rows_coach.append(row)
    
    # Alert banner
    if alerts:
        alert_text = " &nbsp;|&nbsp; ".join(alerts)
        st.markdown(f"""
        <div style="background:rgba(255,23,68,.08); border:1px solid rgba(255,23,68,.2); border-left:4px solid #ff1744; padding:14px 20px; margin-bottom:24px;">
            🔴 <strong style="color:#ff1744">ALERT:</strong> {alert_text}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("##### 📊 Monitoraggio Giocatori — Ultima Partita")
    
    if rows_coach:
        df_coach = pd.DataFrame(rows_coach)
        st.dataframe(df_coach, use_container_width=True, hide_index=True)
    else:
        st.info("Nessun dato disponibile nel file Excel.")
    
    st.markdown("---")
    
    # Dettaglio espandibile per ogni giocatore
    st.markdown("##### 🔍 Dettaglio per Giocatore")
    for username, cred in CREDENZIALI.items():
        if cred["ruolo"] != "player":
            continue
        partite = dati_excel.get(username, [])
        if not partite:
            continue
        ultima = partite[-1]
        kpi_list = parse_kpi(ultima["kpi_raw"], ultima["ruolo"])
        rating = calcola_rating(kpi_list)
        
        with st.expander(f"📋 {ultima['nome']} — {ultima['ruolo']} | Rating: {rating} | {ultima['partita']} ({ultima['data']})"):
            fig = grafico_kpi(kpi_list, key_suffix=f"coach_{username}")
            if fig:
                st.plotly_chart(fig, use_container_width=True,
                               key=f"coach_kpi_{username}")
            
            cols = st.columns(len(kpi_list))
            for i, k in enumerate(kpi_list):
                with cols[i]:
                    if k["tipo"] == "percentuale" and k["soglia"]:
                        delta = k["pct"] - k["soglia"]
                        st.metric(k["nome"], f"{k['pct']}%",
                                 delta=f"{delta:+d}% vs benchmark",
                                 delta_color="normal")
                    elif k["tipo"] == "percentuale":
                        st.metric(k["nome"], f"{k['pct']}%")
                    else:
                        st.metric(k["nome"], f"{k['tot']}")

# ── MAIN ───────────────────────────────────────────────────────────────────

def main():
    # Inizializza session state
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    if not st.session_state["logged_in"]:
        mostra_login()
        return
    
    # Cerca il file Excel
    # Prova prima nella stessa cartella dello script, poi sul Desktop/Scrivania
    possibili_percorsi = [
        "Progetto_Tesi.xlsx",
        os.path.join(os.path.dirname(__file__), "Progetto_Tesi.xlsx"),
        os.path.expanduser("~/Desktop/Progetto_Tesi.xlsx"),
        os.path.expanduser("~/Scrivania/Progetto_Tesi.xlsx"),
    ]
    
    file_excel = None
    for percorso in possibili_percorsi:
        if os.path.exists(percorso):
            file_excel = percorso
            break
    
    if file_excel is None:
        st.error("⚠️ File 'Progetto_Tesi.xlsx' non trovato. Mettilo nella stessa cartella di playerview_app.py")
        if st.button("Esci"):
            st.session_state["logged_in"] = False
            st.rerun()
        return
    
    # Carica dati
    dati_excel = carica_dati_excel(file_excel)
    
    # Header
    username = st.session_state["username"]
    ruolo_utente = st.session_state["ruolo_utente"]
    
    # Top bar premium
    col_logo, col_info, col_logout = st.columns([1, 7, 1])
    col_logo, col_info, col_logout = st.columns([2, 6, 2])
    with col_logo:
        st.image(LOGO_PATH, width=48)
    with col_info:
        nome = CREDENZIALI[username]["nome"]
        ruolo_label = "Analyst · U15" if ruolo_utente == "coach" else "U15 Nazionale"
        st.markdown(f"<span style='color:#888; font-size:13px;'><strong style='color:#f0f0f0'>{nome}</strong> — {ruolo_label}</span>",
                   unsafe_allow_html=True)
    with col_logout:
        if st.button("Esci"):
            st.session_state["logged_in"] = False
            st.rerun()
    
    st.markdown("---")
    
    # Vista in base al ruolo — giocatore vede solo se stesso, staff vede tutto
    if ruolo_utente == "player":
        mostra_giocatore(username, dati_excel, key_prefix="player")
    else:
        tab1, tab2 = st.tabs(["👥 Dashboard Staff", "👤 Vista Giocatore"])
        with tab1:
            mostra_staff(dati_excel)
        with tab2:
            scelta = st.selectbox("Seleziona giocatore",
                                 [u for u, c in CREDENZIALI.items() if c["ruolo"] == "player"],
                                 format_func=lambda x: CREDENZIALI[x]["nome"])
            mostra_giocatore(scelta, dati_excel, key_prefix="coach_detail")

if __name__ == "__main__":
    main()
