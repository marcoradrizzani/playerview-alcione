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

    /* ── MOBILE RESPONSIVE ── */
    @media (max-width: 768px) {
        /* Logo login più piccolo */
        .login-logo img { max-width: 80px !important; }

        /* Titolo PlayerView più piccolo */
        .playerview-title { font-size: 32px !important; }

        /* Header giocatore */
        .player-name { font-size: 28px !important; }

        /* KPI cards: 2 per riga su mobile */
        div[data-testid="column"] {
            min-width: 45% !important;
            flex: 1 1 45% !important;
        }

        /* Font più leggibili */
        div[style*="font-size:44px"] { font-size: 32px !important; }
        div[style*="font-size:42px"] { font-size: 30px !important; }
        div[style*="font-size:38px"] { font-size: 26px !important; }

        /* Padding ridotto */
        .main .block-container {
            padding-left: 12px !important;
            padding-right: 12px !important;
            padding-top: 16px !important;
        }

        /* Iframe clip più basso */
        iframe { height: 200px !important; }
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
    Legge il file Excel con due fogli separati:
    - Foglio 'Demaria' per il DC
    - Foglio 'Fortin' per l'AS
    Riga 1 = titolo, Riga 2 = intestazioni, Riga 3+ = dati partite
    """
    try:
        giocatori = {}
        all_sheets = pd.read_excel(percorso_file, sheet_name=None, header=None)
        
        for sheet_name, df in all_sheets.items():
            username = sheet_name.lower().strip()
            
            # Riga 2 (indice 1) = intestazioni, Riga 3+ (indice 2+) = dati
            if len(df) < 3:
                continue
            
            headers = [str(df.iloc[1, c]).strip() for c in range(len(df.columns))]
            
            for row_idx in range(2, len(df)):
                # Salta righe vuote
                if pd.isna(df.iloc[row_idx, 1]) or str(df.iloc[row_idx, 1]).strip() in ('', 'nan'):
                    continue
                
                giocatore_nome = str(df.iloc[row_idx, 1]).strip()
                ruolo = str(df.iloc[row_idx, 2]).strip()
                partita = str(df.iloc[row_idx, 3]).strip()
                
                # Data
                data_raw = df.iloc[row_idx, 4]
                if pd.notna(data_raw):
                    try:
                        data_str = pd.to_datetime(data_raw).strftime("%d/%m/%Y")
                    except:
                        data_str = str(data_raw)
                else:
                    data_str = "N/D"
                
                # KPI e clip
                kpi_data = {}
                clip_data = {}
                
                for col_idx in range(5, len(headers)):
                    col_name = headers[col_idx]
                    if col_name in ("nan", "", "NaN"):
                        continue
                    valore = df.iloc[row_idx, col_idx]
                    if pd.isna(valore):
                        continue
                    val_str = str(valore).strip()
                    if not val_str or val_str.lower() in ('nan', 'x', ''):
                        continue
                    
                    if col_name.startswith("Clip1_") or col_name.startswith("Clip2_"):
                        esito = "P" if col_name.startswith("Clip1_") else "N"
                        principio = col_name.replace("Clip1_", "").replace("Clip2_", "")
                        if principio not in clip_data:
                            clip_data[principio] = []
                        clip_data[principio].append({"url": val_str, "esito": esito})
                    else:
                        kpi_data[col_name] = val_str
                
                if username not in giocatori:
                    giocatori[username] = []
                
                giocatori[username].append({
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

def calcola_medie_stagionali(partite, ruolo):
    """Calcola le medie stagionali per ogni KPI su tutte le partite disponibili."""
    totali = {}
    conteggi = {}
    for p in partite:
        kpi_list = parse_kpi(p["kpi_raw"], ruolo)
        for k in kpi_list:
            if k["tipo"] == "percentuale" and k["pct"] is not None:
                nome = k["nome"]
                totali[nome] = totali.get(nome, 0) + k["pct"]
                conteggi[nome] = conteggi.get(nome, 0) + 1
    return {nome: round(totali[nome] / conteggi[nome]) for nome in totali}

def grafico_trend(partite, ruolo, key_suffix=""):
    """Grafico a linee: andamento KPI partita per partita con media stagionale."""
    if len(partite) < 2:
        return None

    # Raccoglie dati per ogni partita
    labels = [f"{p['partita']}\n{p['data']}" for p in partite]
    kpi_nomi = []
    # Prende i nomi KPI dalla prima partita
    for k in parse_kpi(partite[0]["kpi_raw"], ruolo):
        if k["tipo"] == "percentuale":
            kpi_nomi.append(k["nome"])

    colori_linee = ["#FF6B00", "#00e676", "#00bcd4", "#ffea00", "#e040fb"]
    medie = calcola_medie_stagionali(partite, ruolo)

    fig = go.Figure()

    for i, nome_kpi in enumerate(kpi_nomi):
        valori = []
        for p in partite:
            kpi_list = parse_kpi(p["kpi_raw"], ruolo)
            val = next((k["pct"] for k in kpi_list if k["nome"] == nome_kpi and k["tipo"] == "percentuale"), None)
            valori.append(val)

        colore = colori_linee[i % len(colori_linee)]

        fig.add_trace(go.Scatter(
            x=labels, y=valori,
            mode='lines+markers',
            name=nome_kpi,
            line=dict(color=colore, width=2),
            marker=dict(size=8, color=colore),
            connectgaps=True,
        ))

        # Linea media stagionale tratteggiata
        media = medie.get(nome_kpi)
        if media is not None:
            fig.add_shape(type="line",
                x0=labels[0], x1=labels[-1], y0=media, y1=media,
                line=dict(color=colore, width=1, dash="dot"),
                xref="x", yref="y"
            )

    fig.update_layout(
        plot_bgcolor='#0d0d12', paper_bgcolor='#050507',
        font=dict(color='#ffffff', family='Inter'),
        xaxis=dict(showgrid=False, tickfont=dict(color='#888', size=10)),
        yaxis=dict(
            range=[0, 110], ticksuffix='%',
            showgrid=True, gridcolor='#1e1e2a',
            tickfont=dict(color='#555', size=11),
        ),
        legend=dict(bgcolor='#0d0d12', bordercolor='#1e1e2a', borderwidth=1,
                    font=dict(color='#888', size=11)),
        margin=dict(l=20, r=20, t=20, b=40),
        height=300,
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
    st.markdown("<br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        c1, c2, c3 = st.columns([2, 1, 2])
        with c2:
            st.image(LOGO_PATH, width=90)
        st.markdown("""
        <div style="text-align:center; margin-top:8px; margin-bottom:24px;">
            <div style="font-size:10px; font-weight:700; letter-spacing:4px; text-transform:uppercase; color:#FF6B00;">ALCIONE MILANO · 2025/26</div>
            <div style="font-size:40px; font-weight:900; letter-spacing:3px; text-transform:uppercase; color:#ffffff; line-height:1; margin-top:6px;">PLAYER<span style="color:#FF6B00">VIEW</span></div>
            <div style="font-size:10px; letter-spacing:2px; text-transform:uppercase; color:#444; margin-top:6px;">Analisi video individuale</div>
            <div style="width:40px; height:2px; background:#FF6B00; margin:16px auto;"></div>
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

    # ── STAGIONALE ──
    if len(partite) > 1:
        st.markdown("---")
        st.markdown("##### 📅 Medie Stagionali")

        medie_stagionali = calcola_medie_stagionali(partite, ruolo)

        cols_stag = st.columns(len(medie_stagionali))
        bench = BENCHMARK.get(ruolo, {})
        soglie_map = {info[0]: info[1] for info in bench.values() if info[1] is not None}

        for i, (nome_kpi, media_pct) in enumerate(medie_stagionali.items()):
            with cols_stag[i]:
                soglia = soglie_map.get(nome_kpi)
                colore = get_colore(media_pct, soglia)
                color_map2 = {"green": "#00e676", "yellow": "#ffea00", "red": "#ff1744"}
                c = color_map2[colore]
                emoji = get_emoji(colore)
                bench_text = f"Benchmark: {soglia}%" if soglia else ""
                st.markdown(f"""
                <div style="background:#1a1a1a; border-top:3px solid {c}; padding:18px 20px; margin-bottom:8px;">
                    <div style="font-size:10px; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; color:#888; margin-bottom:10px;">
                        {emoji} {nome_kpi}<br>
                        <span style="color:#555; font-size:9px;">MEDIA STAGIONALE</span>
                    </div>
                    <div style="font-family:'Barlow Condensed',sans-serif; font-weight:900; font-size:42px; color:{c}; line-height:1; margin-bottom:10px;">
                        {media_pct}%
                    </div>
                    <div style="height:4px; background:#2a2a2a; border-radius:2px; margin-bottom:8px;">
                        <div style="height:100%; width:{media_pct}%; background:{c}; border-radius:2px;"></div>
                    </div>
                    <div style="font-size:10px; color:#888;">{bench_text} &nbsp;·&nbsp; {len(partite)} partite</div>
                </div>
                """, unsafe_allow_html=True)

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
                    for clip_item in clip_list:
                        # Supporta sia il nuovo formato {"url":..., "esito":...} che il vecchio stringa
                        if isinstance(clip_item, dict):
                            clip_path = clip_item["url"]
                            esito_label = clip_item.get("esito", "P")
                        else:
                            clip_path = clip_item
                            esito_label = "P"  # fallback
                        
                        esito_color = "#00e676" if esito_label == "P" else "#ff1744"
                        nome_clip = f"{principio} — Esito {esito_label}"
                        
                        st.markdown(f"""
                        <div style="background:#0d0d12; border-left:3px solid {esito_color}; padding:10px 14px; margin-bottom:8px;">
                            <span style="font-size:13px; color:#ffffff;">{nome_clip}</span>
                            <span style="background:rgba(255,255,255,0.05); color:{esito_color}; padding:2px 8px; font-size:10px; font-weight:700; margin-left:8px;">{esito_label}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if clip_path.startswith("http"):
                            # Converti in URL preview per iframe
                            preview_url = clip_path
                            if "drive.google.com" in clip_path:
                                if "id=" in clip_path:
                                    file_id = clip_path.split("id=")[-1].split("&")[0].strip()
                                    preview_url = f"https://drive.google.com/file/d/{file_id}/preview"
                                elif "/file/d/" in clip_path:
                                    file_id = clip_path.split("/file/d/")[1].split("/")[0]
                                    preview_url = f"https://drive.google.com/file/d/{file_id}/preview"
                            
                            st.markdown(f"""
                            <div style="border:1px solid #1e1e2a; border-radius:2px; overflow:hidden; margin-top:8px; margin-bottom:4px; background:#000;">
                                <iframe 
                                    src="{preview_url}" 
                                    width="100%" 
                                    height="320"
                                    frameborder="0"
                                    allow="autoplay"
                                    allowfullscreen
                                    style="display:block;"
                                ></iframe>
                            </div>
                            <div style="text-align:right; margin-bottom:12px;">
                                <a href="{clip_path}" target="_blank" style="
                                    color:#FF6B00; font-size:10px; font-weight:700;
                                    letter-spacing:1px; text-transform:uppercase; text-decoration:none;
                                ">↗ Apri in Drive</a>
                            </div>
                            """, unsafe_allow_html=True)
                        elif os.path.exists(clip_path):
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
        
        # Medie stagionali invece dell'ultima partita
        ruolo = partite[-1]["ruolo"]
        nome = partite[-1]["nome"]
        medie = calcola_medie_stagionali(partite, ruolo)
        bench = BENCHMARK.get(ruolo, {})
        soglie_map = {info[0]: info[1] for info in bench.values() if info[1] is not None}

        row = {
            "Giocatore": nome,
            "Ruolo": ruolo,
            "Partite": len(partite),
        }

        alert_count = 0
        for nome_kpi, media_pct in medie.items():
            soglia = soglie_map.get(nome_kpi)
            colore = get_colore(media_pct, soglia)
            emoji = get_emoji(colore)
            row[nome_kpi] = f"{emoji} {media_pct}%"
            if colore == "red":
                alert_count += 1
                alerts.append(f"**{nome}** — {nome_kpi} sotto soglia ({media_pct}% vs benchmark {soglia}%)")

        row["Stato"] = "🔴 ALERT" if alert_count > 0 else ("🟡 ATTENZIONE" if any(
            get_colore(m, soglie_map.get(n)) == "yellow"
            for n, m in medie.items()
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
    
    st.markdown("##### 📊 Monitoraggio Giocatori — Medie Stagionali")
    
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
    
    # ── GESTIONE FILE EXCEL ──────────────────────────────────────────────
    # Il file Excel viene scaricato da Google Drive al primo accesso
    # oppure quando si preme il tasto "Aggiorna Dati"

    username = st.session_state["username"]
    ruolo_utente = st.session_state["ruolo_utente"]

    DRIVE_FILE_ID = "12qRBYLlnNRvL7QitKLZ8vZSc68sD1od9"
    DRIVE_DOWNLOAD_URL = f"https://docs.google.com/spreadsheets/d/{DRIVE_FILE_ID}/export?format=xlsx"

    def scarica_da_drive():
        import requests
        import io
        try:
            r = requests.get(DRIVE_DOWNLOAD_URL, timeout=15)
            if r.status_code == 200:
                st.session_state["excel_bytes"] = r.content
                st.session_state["excel_ultimo_aggiornamento"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                return True
            else:
                return False
        except Exception as e:
            st.error(f"Errore nel download: {e}")
            return False

    # Scarica automaticamente al primo accesso
    if "excel_bytes" not in st.session_state:
        with st.spinner("Caricamento dati in corso..."):
            scarica_da_drive()

    # Tasto aggiorna nella sidebar (visibile a tutti)
    with st.sidebar:
        st.markdown("### 🔄 Dati")
        ultimo = st.session_state.get("excel_ultimo_aggiornamento", "—")
        st.markdown(f"<div style='font-size:11px; color:#888; margin-bottom:12px;'>Ultimo aggiornamento:<br><strong style='color:#FF6B00'>{ultimo}</strong></div>", unsafe_allow_html=True)
        if st.button("🔄 Aggiorna Dati", use_container_width=True):
            with st.spinner("Scaricamento in corso..."):
                if scarica_da_drive():
                    st.success("✅ Dati aggiornati!")
                    st.rerun()
                else:
                    st.error("❌ Errore nel download. Riprova.")

    # Carica dati da session state o fallback locale
    import io
    if "excel_bytes" in st.session_state:
        dati_excel = carica_dati_excel(io.BytesIO(st.session_state["excel_bytes"]))
    else:
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
            st.warning("⚠️ Dati non disponibili. Premi 'Aggiorna Dati' nel pannello laterale.")
            if st.button("Esci"):
                st.session_state["logged_in"] = False
                st.rerun()
            return

        dati_excel = carica_dati_excel(file_excel)
    
    # Top bar premium
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
