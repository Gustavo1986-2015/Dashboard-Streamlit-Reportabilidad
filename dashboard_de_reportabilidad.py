import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import locale

# --- CONFIGURACIÓN DE LA PÁGINA ---
# Se establece el idioma a español para las fechas
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'Spanish')
    
st.set_page_config(page_title="Dashboard de Reportabilidad SIMON IV Truper - Sistech & Solusof",
                   page_icon="📊",
                   layout="wide")

# --- ESTILOS VISUALES (Inspirado en Power BI) ---
st.markdown("""
<style>
    /* Estilo general para asegurar texto negro y negrita */
    body, .stApp, .stMarkdown, .stMetricLabel, .stMetricValue, .stButton>button, .stSubheader, .stDataFrame, div[data-testid="stDataFrame"] table {
        color: black !important;
        font-weight: bold !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: black !important;
        font-weight: bold !important;
    }
    /* Estilo específico para el contenido de la tabla */
    div[data-testid="stDataFrame"] tbody tr td, div[data-testid="stDataFrame"] thead tr th {
        color: black !important;
        font-weight: bold !important;
    }

    /* Estilo para las tarjetas de métricas (KPIs) */
    .stMetric {
        border-radius: 10px;
        background-color: #F0F2F6;
        padding: 15px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        transition: 0.3s;
    }
    .stMetric:hover {
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
    }
    
    /* Reglas para la impresión a PDF */
    @media print {
        [data-testid="stSidebar"], [data-testid="stToolbar"] {
            display: none;
        }
        [data-testid="stAppViewContainer"] {
            padding: 0 !important;
        }
        .main .block-container {
            padding: 1rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# --- BARRA LATERAL PARA INGRESO DE DATOS ---
with st.sidebar:
    st.header("Centro de Control ⚙️")
    st.markdown("### Ingresar Cantidad de Placas")

    fecha_analisis = st.date_input("Fecha del Análisis:", date(2025, 8, 18))

    st.markdown("---")
    st.subheader("AC_avl_Solusof")
    s_cant_1 = st.number_input("Cant. <2 min", min_value=0, value=13425, key="s1")
    s_cant_2 = st.number_input("Cant. 2-5 min", min_value=0, value=3358, key="s2")
    s_cant_3 = st.number_input("Cant. 5-10 min", min_value=0, value=102, key="s3")
    s_cant_4 = st.number_input("Cant. ≥10 min", min_value=0, value=214, key="s4")

    st.markdown("---")
    st.subheader("AC_avl_Sistech_truper")
    t_cant_1 = st.number_input("Cant. <2 min", min_value=0, value=44727, key="t1")
    t_cant_2 = st.number_input("Cant. 2-5 min", min_value=0, value=3786, key="t2")
    t_cant_3 = st.number_input("Cant. 5-10 min", min_value=0, value=92, key="t3")
    t_cant_4 = st.number_input("Cant. ≥10 min", min_value=0, value=77, key="t4")


# --- PÁGINA PRINCIPAL / DASHBOARD ---
st.title(f"📊 Reportabilidad SIMON IV Truper")
st.markdown(f"Análisis para el día: **{fecha_analisis.strftime('%d de %B, %Y')}**")
st.markdown("---")

# --- PROCESAMIENTO DE DATOS ---
rangos = ['<2 min', '2-5 min', '5-10 min', '≥10 min']
cantidades = [s_cant_1, s_cant_2, s_cant_3, s_cant_4, t_cant_1, t_cant_2, t_cant_3, t_cant_4]
total_placas_calculado = sum(cantidades)

if total_placas_calculado == 0:
    porcentajes = [0] * 8
else:
    porcentajes = [(c / total_placas_calculado) * 100 for c in cantidades]

datos = {
    'Prestador': ['AC_avl_Solusof'] * 4 + ['AC_avl_Sistech_truper'] * 4,
    'Rango': rangos * 2,
    'Cantidad': cantidades,
    'Porcentaje': porcentajes
}
df = pd.DataFrame(datos)
df['Porcentaje_decimal'] = df['Porcentaje'] / 100.0

# --- KPIs (Indicadores Clave de Rendimiento) ---
total_solusof = df[df['Prestador'] == 'AC_avl_Solusof']['Cantidad'].sum()
total_sistech = df[df['Prestador'] == 'AC_avl_Sistech_truper']['Cantidad'].sum()

col1, col2, col3 = st.columns(3)
col1.metric(label="Total Placas Reportadas", value=f"{total_placas_calculado:,}")
col2.metric(label="Total Placas Solusof", value=f"{total_solusof:,}")
col3.metric(label="Total Placas Sistech", value=f"{total_sistech:,}")

st.markdown("---")

# --- GRÁFICOS Y TABLAS ---
st.subheader("Visión General: Comparativa de Cantidad de Placas por Rango")
fig_cantidades = px.bar(df, x="Rango", y="Cantidad", color="Prestador", barmode="group", text_auto=True,
                        title="<b>Volumen de Placas Reportadas</b>",
                        color_discrete_map={'AC_avl_Solusof': '#0083B8', 'AC_avl_Sistech_truper': '#FF4B4B'},
                        labels={"Cantidad": "Nº de Placas", "Rango": "Rango de Reportabilidad"})
fig_cantidades.update_layout(
    height=500,
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis={'categoryorder':'array', 'categoryarray':rangos},
    yaxis=(dict(showgrid=False)),
    legend_title_text='',
    font=dict(color="black", family="Arial Black, sans-serif", size=14),
    title_font_weight="bold",
    xaxis_title_font_weight="bold",
    yaxis_title_font_weight="bold"
)
fig_cantidades.update_traces(textfont=dict(color='black', size=12, family='Arial Black, sans-serif'))
st.plotly_chart(fig_cantidades, use_container_width=True)

st.markdown("---")

st.subheader("Análisis de Eficiencia por Rango (%)")
df_s = df[df['Prestador'] == 'AC_avl_Solusof']
df_t = df[df['Prestador'] == 'AC_avl_Sistech_truper']
fig_eficiencia = go.Figure()
fig_eficiencia.add_trace(go.Bar(x=df_s['Rango'], y=df_s['Porcentaje_decimal'], name='Solusof (%)', marker_color='#0083B8', text=df_s['Porcentaje'].apply(lambda x: f'{x:.1f}%'), textposition='auto'))
fig_eficiencia.add_trace(go.Bar(x=df_t['Rango'], y=df_t['Porcentaje_decimal'], name='Sistech (%)', marker_color='#FF4B4B', text=df_t['Porcentaje'].apply(lambda x: f'{x:.1f}%'), textposition='auto'))
fig_eficiencia.add_trace(go.Scatter(x=df_s['Rango'], y=df_s['Porcentaje_decimal'], name='Tendencia Solusof', mode='lines+markers', line=dict(color='#005f87', width=3)))
fig_eficiencia.add_trace(go.Scatter(x=df_t['Rango'], y=df_t['Porcentaje_decimal'], name='Tendencia Sistech', mode='lines+markers', line=dict(color='#c43232', width=3)))
fig_eficiencia.update_layout(
    height=500,
    title_text="<b>Curva de Eficiencia por Prestador</b>",
    xaxis_title="Rango de Reportabilidad",
    yaxis_title="Porcentaje del Total de Placas",
    yaxis_tickformat='.0%',
    barmode='group',
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis={'categoryorder':'array', 'categoryarray':rangos},
    legend_title_text='',
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    font=dict(color="black", family="Arial Black, sans-serif", size=14),
    title_font_weight="bold",
    xaxis_title_font_weight="bold",
    yaxis_title_font_weight="bold"
)
fig_eficiencia.update_traces(textfont=dict(color='black', size=12, family='Arial Black, sans-serif'))
st.plotly_chart(fig_eficiencia, use_container_width=True)

st.markdown("---")

st.subheader("Tabla de Datos Resumen")
df_display = df.copy()
df_display['Porcentaje'] = df_display['Porcentaje'].map('{:.1f}%'.format)
df_pivot = df_display.pivot(index='Prestador', columns='Rango', values=['Cantidad', 'Porcentaje']).fillna(0)
# --- AJUSTE FINAL: Reordenar las columnas de la tabla pivote ---
df_pivot = df_pivot.reindex(columns=rangos, level=1)
st.dataframe(df_pivot, use_container_width=True)

st.markdown("---")

# --- Indicadores de Eficiencia Clave (al final) ---
st.subheader("Indicadores de Eficiencia Clave")
st.markdown("*Este indicador muestra el porcentaje de reportes recibidos en cada rango de eficiencia y el total combinado (< 5 min).*")

# Cálculos para Solusof
eficiencia_s1 = df.loc[(df['Prestador'] == 'AC_avl_Solusof') & (df['Rango'] == '<2 min'), 'Porcentaje'].iloc[0]
eficiencia_s2 = df.loc[(df['Prestador'] == 'AC_avl_Solusof') & (df['Rango'] == '2-5 min'), 'Porcentaje'].iloc[0]
total_s = eficiencia_s1 + eficiencia_s2

# Cálculos para Truper
eficiencia_t1 = df.loc[(df['Prestador'] == 'AC_avl_Sistech_truper') & (df['Rango'] == '<2 min'), 'Porcentaje'].iloc[0]
eficiencia_t2 = df.loc[(df['Prestador'] == 'AC_avl_Sistech_truper') & (df['Rango'] == '2-5 min'), 'Porcentaje'].iloc[0]
total_t = eficiencia_t1 + eficiencia_t2

def get_eficiencia_emoji(valor):
    if valor >= 85: return "🟢"
    if valor >= 70: return "🟡"
    return "🔴"

st.markdown("##### AC_avl_Solusof")
col1, col2, col3 = st.columns(3)
col1.metric(label="Eficiencia <2 min", value=f"{eficiencia_s1:.1f}%")
col2.metric(label="Eficiencia 2-5 min", value=f"{eficiencia_s2:.1f}%")
col3.metric(label=f"Total <5 min {get_eficiencia_emoji(total_s)}", value=f"{total_s:.1f}%")

st.markdown("##### AC_avl_Sistech_truper")
col1, col2, col3 = st.columns(3)
col1.metric(label="Eficiencia <2 min", value=f"{eficiencia_t1:.1f}%")
col2.metric(label="Eficiencia 2-5 min", value=f"{eficiencia_t2:.1f}%")
col3.metric(label=f"Total <5 min {get_eficiencia_emoji(total_t)}", value=f"{total_t:.1f}%")