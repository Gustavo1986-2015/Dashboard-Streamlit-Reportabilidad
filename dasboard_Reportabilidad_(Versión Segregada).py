import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import locale

# --- CONFIGURACIÓN DE LA PÁGINA ---
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'Spanish')
    
st.set_page_config(page_title="Dashboard de Reportabilidad SIMON IV Truper - Sistech & Solusof",
                   page_icon="📊",
                   layout="wide")

# --- ESTILOS VISUALES ---
st.markdown("""
<style>
    body, .stApp, .stMarkdown, .stMetricLabel, .stMetricValue, .stButton>button, .stSubheader, .stDataFrame, div[data-testid="stDataFrame"] table {
        color: black !important;
        font-weight: bold !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: black !important;
        font-weight: bold !important;
    }
    div[data-testid="stDataFrame"] tbody tr td, div[data-testid="stDataFrame"] thead tr th {
        color: black !important;
        font-weight: bold !important;
    }
    .stMetric {
        border-radius: 10px;
        background-color: #F0F2F6;
        padding: 15px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    }
    @media print {
        [data-testid="stSidebar"], [data-testid="stToolbar"] { display: none; }
        [data-testid="stAppViewContainer"] { padding: 0 !important; }
        .main .block-container { padding: 1rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES AUXILIARES ---
def get_provider_inputs(section_key):
    """Crea los campos de entrada para un proveedor en la barra lateral."""
    providers = {"solusof": "AC_avl_Solusof", "sistech": "AC_avl_Sistech"}
    inputs = {}
    
    # Valores por defecto tomados de la imagen para una mejor experiencia inicial
    defaults = {
        "avl_hub": {
            "solusof": {"prom": ["00:01:04", "00:02:33", "00:06:55", "00:59:43"], "cant": [20965, 5317, 159, 351]},
            "sistech": {"prom": ["00:00:40", "00:03:09", "00:06:34", "01:23:24"], "cant": [34765, 3767, 100, 78]}
        },
        "hub_simon": {
            "solusof": {"prom": ["00:00:19", "00:00:00", "00:00:00", "00:00:00"], "cant": [26792, 0, 0, 0]},
            "sistech": {"prom": ["00:00:19", "00:00:00", "00:00:00", "00:00:00"], "cant": [38711, 0, 0, 0]}
        },
        "avl_simon": {
            "solusof": {"prom": ["00:01:15", "00:02:40", "00:06:49", "00:59:52"], "cant": [18216, 8027, 197, 352]},
            "sistech": {"prom": ["00:00:55", "00:03:09", "00:06:13", "01:03:35"], "cant": [33353, 5118, 158, 82]}
        }
    }

    for key, name in providers.items():
        st.subheader(name)
        c1, c2 = st.columns(2)
        promedios = []
        cantidades = []
        for i, rango in enumerate(['<2 min', '2-5 min', '5-10 min', '≥10 min']):
            col = c1 if i % 2 == 0 else c2
            with col:
                promedios.append(st.text_input(f"Prom. {rango}", value=defaults[section_key][key]["prom"][i], key=f"{section_key}_{key}_prom_{i}"))
                cantidades.append(st.number_input(f"Cant. {rango}", min_value=0, value=defaults[section_key][key]["cant"][i], key=f"{section_key}_{key}_cant_{i}"))
        inputs[name] = {"promedios": promedios, "cantidades": cantidades}
    return inputs

def create_section_dashboard(title, section_data):
    """Genera el dashboard para una sección específica (AVL a HUB, etc.)."""
    st.title(f"📊 Análisis: {title}")
    
    # --- Procesamiento de Datos para la Sección ---
    rangos = ['<2 min', '2-5 min', '5-10 min', '≥10 min']
    all_data = []
    for provider, data in section_data.items():
        for i, rango in enumerate(rangos):
            all_data.append({
                'Prestador': provider,
                'Rango': rango,
                'Promedio': data['promedios'][i],
                'Cantidad': data['cantidades'][i]
            })
    df = pd.DataFrame(all_data)
    
    total_placas_section = df['Cantidad'].sum()
    if total_placas_section > 0:
        df['Porcentaje'] = (df['Cantidad'] / total_placas_section) * 100
    else:
        df['Porcentaje'] = 0

    # --- KPIs de la Sección ---
    total_solusof = df[df['Prestador'] == 'AC_avl_Solusof']['Cantidad'].sum()
    total_sistech = df[df['Prestador'] == 'AC_avl_Sistech']['Cantidad'].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Placas en Sección", f"{total_placas_section:,}")
    col2.metric("Total Solusof", f"{total_solusof:,}")
    col3.metric("Total Sistech", f"{total_sistech:,}")
    st.markdown("---")

    # --- Gráficos de la Sección ---
    st.subheader("Comparativa de Cantidad de Placas por Rango")
    fig_cant = px.bar(df, x="Rango", y="Cantidad", color="Prestador", barmode="group", text_auto=True,
                      color_discrete_map={'AC_avl_Solusof': '#0083B8', 'AC_avl_Sistech': '#FF4B4B'})
    fig_cant.update_layout(height=400, plot_bgcolor="rgba(0,0,0,0)", xaxis={'categoryorder':'array', 'categoryarray':rangos},
                           font=dict(color="black", family="Arial Black"), yaxis_title="Nº de Placas")
    st.plotly_chart(fig_cant, use_container_width=True)

    st.subheader("Distribución Porcentual por Rango")
    fig_perc = px.bar(df, x="Rango", y="Porcentaje", color="Prestador", barmode="group", text_auto='.1f',
                      color_discrete_map={'AC_avl_Solusof': '#0083B8', 'AC_avl_Sistech': '#FF4B4B'})
    fig_perc.update_layout(height=400, plot_bgcolor="rgba(0,0,0,0)", xaxis={'categoryorder':'array', 'categoryarray':rangos},
                           yaxis=dict(ticksuffix="%"), font=dict(color="black", family="Arial Black"), yaxis_title="% del Total de la Sección")
    fig_perc.update_traces(texttemplate='%{y:.1f}%')
    st.plotly_chart(fig_perc, use_container_width=True)

    # --- Tabla de Resumen ---
    st.subheader("Tabla de Datos Resumen")
    df_display = df.copy()
    df_display['Porcentaje'] = df_display['Porcentaje'].map('{:.1f}%'.format)
    df_pivot = df_display.pivot(index='Prestador', columns='Rango', values=['Promedio', 'Cantidad', 'Porcentaje']).fillna(0)
    df_pivot = df_pivot.reindex(columns=rangos, level=1)
    st.dataframe(df_pivot, use_container_width=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

# --- BARRA LATERAL (CENTRO DE CONTROL) ---
with st.sidebar:
    st.header("Centro de Control ⚙️")
    fecha_analisis = st.date_input("Fecha del Análisis:", date.today())
    
    with st.expander("AVL a HUB", expanded=True):
        avl_hub_data = get_provider_inputs("avl_hub")
    
    with st.expander("HUB a SIMON"):
        hub_simon_data = get_provider_inputs("hub_simon")
        
    with st.expander("AVL a SIMON"):
        avl_simon_data = get_provider_inputs("avl_simon")

# --- PÁGINA PRINCIPAL (DASHBOARD) ---
st.header(f"Reportabilidad SIMON IV Truper - {fecha_analisis.strftime('%d de %B, %Y')}")
st.markdown("---")

create_section_dashboard("AVL a HUB", avl_hub_data)
create_section_dashboard("HUB a SIMON", hub_simon_data)
create_section_dashboard("AVL a SIMON", avl_simon_data)