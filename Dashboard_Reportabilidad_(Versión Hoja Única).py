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

def parse_table_from_sheet(uploaded_file, sheet_name, start_row):
    """Lee una tabla específica desde una hoja de Excel, comenzando en la fila indicada."""
    try:
        # El usuario proporciona el número de fila (1-based) de Excel donde aparece "Prestadores".
        # El encabezado de niveles múltiples se encuentra en esa fila y la anterior.
        header_indices = [start_row - 2, start_row - 1]
        
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=header_indices, 
                           index_col=0, engine='openpyxl')
        
        # Nos quedamos solo con las primeras 3 filas de datos leídos (2 proveedores + fila de total)
        df = df.head(3)
        
        df.columns = ['_'.join(map(str, col)).strip() for col in df.columns.values]
        df.index.name = 'Prestador'
        df = df.reset_index()

        providers_of_interest = ["AC_avl_Solusof", "AC_avl_Sistech", "AC_avl_truper"]
        df = df[df['Prestador'].isin(providers_of_interest)]
        df['Prestador'] = df['Prestador'].replace('AC_avl_truper', 'AC_avl_Sistech')

        data = {}
        rangos_cols = {
            '<2 min': ('<2 min_Promedio de Diferencia', '<2 min_Cuenta de Placas'),
            '2-5 min': ('2-5 min_Promedio de Diferencia', '2-5 min_Cuenta de Placas'),
            '5-10 min': ('5-10 min_Promedio de Diferencia', '5-10 min_Cuenta de Placas'),
            '≥10 min': ('≥10 min_Promedio de Diferencia', '≥10 min_Cuenta de Placas')
        }
        
        for provider_name in ["AC_avl_Solusof", "AC_avl_Sistech"]:
            provider_row = df[df['Prestador'] == provider_name]
            if not provider_row.empty:
                promedios, cantidades = [], []
                for rango_key, (prom_col_base, cant_col_base) in rangos_cols.items():
                    actual_prom_col = next((c for c in df.columns if prom_col_base in c), None)
                    actual_cant_col = next((c for c in df.columns if cant_col_base in c), None)
                    
                    prom = str(provider_row[actual_prom_col].iloc[0]) if actual_prom_col and not pd.isna(provider_row[actual_prom_col].iloc[0]) else "00:00:00"
                    cant = int(provider_row[actual_cant_col].iloc[0]) if actual_cant_col and not pd.isna(provider_row[actual_cant_col].iloc[0]) else 0
                    promedios.append(prom)
                    cantidades.append(cant)
                data[provider_name] = {"promedios": promedios, "cantidades": cantidades}
            else:
                data[provider_name] = {"promedios": ["00:00:00"]*4, "cantidades": [0]*4}
        return data
    except Exception as e:
        st.sidebar.error(f"Error al leer la tabla en la fila {start_row} de la hoja '{sheet_name}': {e}")
        return None

def create_section_dashboard(title, section_data):
    """Genera el dashboard para una sección específica."""
    st.title(f"📊 Análisis: {title}")
    
    rangos = ['<2 min', '2-5 min', '5-10 min', '≥10 min']
    all_data = [{'Prestador': p, 'Rango': r, 'Promedio': d['promedios'][i], 'Cantidad': d['cantidades'][i]}
                for p, d in section_data.items() for i, r in enumerate(rangos)]
    df = pd.DataFrame(all_data)
    
    total_placas_section = df['Cantidad'].sum()
    df['Porcentaje'] = (df['Cantidad'] / total_placas_section) * 100 if total_placas_section > 0 else 0

    total_solusof = df[df['Prestador'] == 'AC_avl_Solusof']['Cantidad'].sum()
    total_sistech = df[df['Prestador'] == 'AC_avl_Sistech']['Cantidad'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Placas en Sección", f"{total_placas_section:,}")
    c2.metric("Total Solusof", f"{total_solusof:,}")
    c3.metric("Total Sistech", f"{total_sistech:,}")
    st.markdown("---")

    st.subheader("Comparativa de Cantidad de Placas por Rango")
    fig_cant = px.bar(df, x="Rango", y="Cantidad", color="Prestador", barmode="group", text_auto=True, color_discrete_map={'AC_avl_Solusof': '#0083B8', 'AC_avl_Sistech': '#FF4B4B'})
    fig_cant.update_layout(height=400, plot_bgcolor="rgba(0,0,0,0)", xaxis={'categoryorder':'array', 'categoryarray':rangos}, font=dict(color="black", family="Arial Black"), yaxis_title="Nº de Placas")
    st.plotly_chart(fig_cant, use_container_width=True)

    st.subheader("Distribución Porcentual por Rango")
    fig_perc = px.bar(df, x="Rango", y="Porcentaje", color="Prestador", barmode="group", text_auto='.1f', color_discrete_map={'AC_avl_Solusof': '#0083B8', 'AC_avl_Sistech': '#FF4B4B'})
    fig_perc.update_layout(height=400, plot_bgcolor="rgba(0,0,0,0)", xaxis={'categoryorder':'array', 'categoryarray':rangos}, yaxis=dict(ticksuffix="%"), font=dict(color="black", family="Arial Black"), yaxis_title="% del Total de la Sección")
    fig_perc.update_traces(texttemplate='%{y:.1f}%')
    st.plotly_chart(fig_perc, use_container_width=True)

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
    
    uploaded_file = st.file_uploader("Sube tu archivo Excel de análisis", type=["xlsx"])
    
    avl_hub_data, hub_simon_data, avl_simon_data = None, None, None

    if uploaded_file is not None:
        try:
            xls = pd.ExcelFile(uploaded_file)
            sheet_options = xls.sheet_names
            
            selected_sheet = st.selectbox("Selecciona la hoja con las tablas:", sheet_options)
            
            st.markdown("---")
            st.markdown("Indica la fila donde aparece la palabra **'Prestadores'** para cada tabla:")
            
            # El número de fila que se ve en Excel.
            start_row_avl_hub = st.number_input("Fila con 'Prestadores' para 'AVL a HUB'", min_value=1, value=5)
            start_row_hub_simon = st.number_input("Fila con 'Prestadores' para 'HUB a SIMON'", min_value=1, value=18)
            start_row_avl_simon = st.number_input("Fila con 'Prestadores' para 'AVL a SIMON'", min_value=1, value=30)

            if st.button("Procesar Archivo", use_container_width=True, type="primary"):
                avl_hub_data = parse_table_from_sheet(uploaded_file, selected_sheet, start_row_avl_hub)
                hub_simon_data = parse_table_from_sheet(uploaded_file, selected_sheet, start_row_hub_simon)
                avl_simon_data = parse_table_from_sheet(uploaded_file, selected_sheet, start_row_avl_simon)
        except Exception as e:
            st.error(f"No se pudo leer el archivo Excel. Error: {e}")
    else:
        st.info("Esperando archivo Excel para generar el reporte.")

# --- PÁGINA PRINCIPAL (DASHBOARD) ---
st.header(f"Reportabilidad SIMON IV Truper - {fecha_analisis.strftime('%d de %B, %Y')}")
st.markdown("---")

if avl_hub_data and hub_simon_data and avl_simon_data:
    create_section_dashboard("AVL a HUB", avl_hub_data)
    create_section_dashboard("HUB a SIMON", hub_simon_data)
    create_section_dashboard("AVL a SIMON", avl_simon_data)
else:
    st.warning("Por favor, sube un archivo Excel y presiona 'Procesar Archivo' para ver el reporte.")