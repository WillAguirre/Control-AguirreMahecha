import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import base64
from metricas import Metricas
import metricas
import scipy.stats as stats
import matplotlib.pyplot as plt
from statsmodels.graphics.gofplots import qqplot
import os
from pathlib import Path




# Configuración de la página
st.set_page_config(
    page_title="Análisis Datos Clínicos",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)







# CSS personalizado para replicar el estilo original
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Ubuntu:wght@300;400;500;700&display=swap');
    
    .main {
        font-family: 'Ubuntu', sans-serif;
    }
    
    .header-container {
        background-color: #fff;
        color: #ff0064;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .header-title {
        font-size: 2rem;
        font-weight: 700;
        color: #ff0064;
        text-align: center;
        margin: 0;
    }
    
    .metric-card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        padding: 1rem;
        margin: 0.5rem;
        text-align: center;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
    }
    
    .metric-header {
        background-color: #ff0064;
        color: white;
        padding: 0.75rem;
        border-radius: 4px;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #000;
    }
    
    .section-header {
        color: #ff0064;
        border-bottom: 2px solid #ff0064;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .info-box {
        background-color: #f8f9fa;
        border-left: 4px solid #ff0064;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    
    .stSelectbox > div > div {
        background-color: #ff0064;
        color: white;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f0f0;
        color: #ff0064;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ff0064;
        color: white;
    }
</style>
""", unsafe_allow_html=True)















# Función para mostrar tarjetas de métricas
def mostrar_tarjetas(metricas_tarjeta, prefijo=""):
    cols = st.columns(3)
    items = list(metricas_tarjeta.items())
    
    for i, (key, value) in enumerate(items):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-header">{key.replace('_', ' ').title()}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)














controles = {
    'I-M-I':{
        'microalbumina':{'maximo':59,'minimo':39,'promedio':49},
        'glucosa':{'maximo':98,'minimo':72,'promedio':85},
        'colesterol':{'maximo':162,'minimo':120,'promedio':0},
        'creatinina':{'maximo':1.57,'minimo':1.09,'promedio':1.33},
        'colesterol hdl':{'maximo':66,'minimo':39,'promedio':52.5},
        'trigliceridos':{'maximo':70,'minimo':52,'promedio':61},
        'colesterol ldl':{'maximo':77,'minimo':46,'promedio':62},
        #inicio de controles patologicos (inferencia)
        'microalbumina_P':{'maximo':66,'minimo':44,'promedio':55},
        'glucosa_P':{'maximo':243,'minimo':179,'promedio':211},
        'colesterol_P':{'maximo':266,'minimo':196,'promedio':231},
        'creatinina_P':{'maximo':3.74,'minimo':2.6,'promedio':3.17},
        'colesterol hdl_P':{'maximo':110,'minimo':66,'promedio':88},
        'trigliceridos_P':{'maximo':144,'minimo':106,'promedio':125},
        'colesterol ldl_P':{'maximo':143,'minimo':86,'promedio':155},
    },
    'I-R':{
        'colesterol':{'maximo':165,'minimo':138,'promedio':152},
        'glucosa':{'maximo':120,'minimo':68.2,'promedio':94},
        'trigliceridos':{'maximo':98.7,'minimo':77.6,'promedio':88.2},
        'colesterol hdl':{'maximo':98.4,'minimo':74.8,'promedio':86.6},
        'creatina':{'maximo':1.01,'minimo':0.79,'promedio':0.9},
        #Inicio de controles patologicos (insertos)
        'colesterol_P':{'maximo':275,'minimo':207,'promedio':241},
        'glucosa_P':{'maximo':269,'minimo':195,'promedio':232},
        'trigliceridos_P':{'maximo':276,'minimo':192,'promedio':234},
        'colesterol hdl_P':{'maximo':221,'minimo':147,'promedio':184},
        'creatina_P':{'maximo':5.33,'minimo':3.41,'promedio':4.37},
    }
}
@st.cache_data

def cargar_archivos_excel_automatico():
    """
    Carga automáticamente todos los archivos Excel de las carpetas especificadas
    y los organiza en un diccionario jerárquico para fácil acceso.
    
    Returns:
        dict: Diccionario organizado como {carpeta: {archivo: dataframe}}
    """
    
    # Definir las rutas de las carpetas
    rutas = {
        "H_I": "/datos/H-I-CORREGIDOS",
        "I_M_I": "/datos/I-M-I CORREGIDOS", 
        "I_R": "/datos/I-R"
    }
    
    # Diccionario principal para almacenar todos los datos
    datos_organizados = {}
    
    # Procesar cada carpeta
    for nombre_carpeta, ruta_carpeta in rutas.items():
        print(f"\nProcesando carpeta: {nombre_carpeta}")
        print(f"Ruta: {ruta_carpeta}")
        
        # Verificar si la carpeta existe
        if not os.path.exists(ruta_carpeta):
            print(f"⚠️  Advertencia: La carpeta {ruta_carpeta} no existe")
            datos_organizados[nombre_carpeta] = {}
            continue
        
        # Diccionario para esta carpeta específica
        archivos_carpeta = {}
        
        # Buscar todos los archivos .xlsx en la carpeta
        archivos_encontrados = list(Path(ruta_carpeta).glob("*.xlsx"))
        
        if not archivos_encontrados:
            print(f"   No se encontraron archivos .xlsx en {nombre_carpeta}")
        
        # Cargar cada archivo Excel
        for archivo_path in archivos_encontrados:
            try:
                # Obtener el nombre del archivo sin extensión
                nombre_archivo = archivo_path.stem
                
                #print(f"   📁 Cargando: {nombre_archivo}.xlsx")
                
                # Leer el archivo Excel
                df = pd.read_excel(archivo_path)
                
                # Guardar en el diccionario
                archivos_carpeta[nombre_archivo] = df
                
               # print(f"      ✅ Cargado exitosamente - Shape: {df.shape}")
                
            except Exception as e:
                print(f"      ❌ Error al cargar {archivo_path.name}: {str(e)}")
                continue
        
        # Agregar los archivos de esta carpeta al diccionario principal
        datos_organizados[nombre_carpeta] = archivos_carpeta
        print(f"   📊 Total archivos cargados en {nombre_carpeta}: {len(archivos_carpeta)}")
    
    return datos_organizados

def mostrar_estructura_datos(datos_organizados):
    """
    Muestra la estructura completa de los datos cargados
    """
    print("\n" + "="*60)
    print("ESTRUCTURA DE DATOS CARGADOS")
    print("="*60)
    
    for carpeta, archivos in datos_organizados.items():
        print(f"\n📂 CARPETA: {carpeta}")
        if not archivos:
            print("   (Sin archivos)")
            continue
            
        for archivo, df in archivos.items():
            print(f"   📄 {archivo}")
            print(f"      - Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
            print(f"      - Columnas: {list(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")

def acceder_datos(datos_organizados, carpeta, archivo, columna=None):
    """
    Función de acceso fácil a los datos
    
    Args:
        datos_organizados: El diccionario principal
        carpeta: Nombre de la carpeta ("H_I", "I_M_I", "I_R")
        archivo: Nombre del archivo (sin extensión)
        columna: Nombre de la columna (opcional)
    
    Returns:
        DataFrame completo, Series (columna), o None si no existe
    """
    try:
        if carpeta not in datos_organizados:
            print(f"Carpeta '{carpeta}' no encontrada")
            return None
            
        if archivo not in datos_organizados[carpeta]:
            print(f"Archivo '{archivo}' no encontrado en carpeta '{carpeta}'")
            print(f"   Archivos disponibles: {list(datos_organizados[carpeta].keys())}")
            return None
        
        df = datos_organizados[carpeta][archivo]
        
        if columna is None:
            return df
        else:
            if columna not in df.columns:
                print(f"Columna '{columna}' no encontrada")
                print(f"Columnas disponibles: {list(df.columns)}")
                return None
            return df[columna]
            
    except Exception as e:
        print(f"Error al acceder a los datos: {str(e)}")
        return None
# Cargar los datos automáticamente
datos = cargar_archivos_excel_automatico()
lista_clinicas = list(datos.keys())
clinica_seleccionada = st.sidebar.selectbox("Selecciona una clínica", lista_clinicas)
# Acceder a los datos de la clínica seleccionada
if clinica_seleccionada:
    archivos_clinica = datos[clinica_seleccionada]
    lista_archivos = list(archivos_clinica.keys())
    archivo_seleccionado = st.sidebar.selectbox("Selecciona un archivo", lista_archivos)
    
    if archivo_seleccionado:
        # Acceder al DataFrame del archivo seleccionado
        data = archivos_clinica[archivo_seleccionado]
        st.write(f"Datos cargados de : {clinica_seleccionada} - Prueba : {archivo_seleccionado}")
        st.dataframe(data.head())  # Mostrar las primeras filas del DataFrame
metricas_clinica = Metricas(
    datos=datos,
    archivo=clinica_seleccionada,
    prueba=archivo_seleccionado,
    columna='resultado'
)

def main():
    # Header
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">Análisis Datos Clínicos</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["ATÍPICOS", "DESCRIPTIVOS", "NORMALIDAD", "CONTROL", "INCERTIDUMBRE"])
    
    with tab1:
        st.markdown('<h2 class="section-header">Análisis de Valores Atípicos</h2>', unsafe_allow_html=True)
        fig1, n, cuartil_1, cuartil_2, cuartil_3,  Rango_Intercuantilico, lim_inf, lim_sup, cantidad_atipicos = metricas_clinica.Calculo_Atipicos()
        st.plotly_chart(fig1, use_container_width=True,key="atipicos_plot")
        st.markdown('<h3 class="section-header">Estadísticas</h3>', unsafe_allow_html=True)
        mostrar_tarjetas({
            'Cantidad de Valores': n,
            'Cuartil 1': cuartil_1,
            'Cuartil 2': cuartil_2,
            'Cuartil 3': cuartil_3,
            'Rango Intercuartílico': Rango_Intercuantilico,
            'Límite Inferior': lim_inf,
            'Límite Superior': lim_sup,
            'Cantidad de Atípicos': cantidad_atipicos
        })

    with tab2:
        st.markdown('<h2 class="section-header">Estadísticas Descriptivas</h2>', unsafe_allow_html=True)
        fig2, n, media, mediana, moda, rango, varianza, desviacion_estandar = metricas_clinica.Calculo_Descriptivas()
        st.plotly_chart(fig2, use_container_width=True, key="descriptivas_plot")
        st.markdown('<h3 class="section-header">Estadísticas</h3>', unsafe_allow_html=True)
        mostrar_tarjetas({
            'Cantidad de Valores': n,
            'Media': media,
            'Mediana': mediana,
            'Moda': moda,
            'Rango': rango,
            'Varianza': varianza,
            'Desviación Estándar': desviacion_estandar
        })

    with tab3:
        st.markdown('<h2 class="section-header">Pruebas de Normalidad</h2>', unsafe_allow_html=True)
        fig3, shapiro_p, kolmogorov_p = metricas_clinica.Calculo_Normalidad()
        st.plotly_chart(fig3, use_container_width=True, key="normalidad_plot") 
        st.markdown('<h3 class="section-header">Pruebas Estadísticas</h3>', unsafe_allow_html=True)
        mostrar_tarjetas({
            'Shapiro-Wilk p-value': shapiro_p,
            'Kolmogorov-Smirnov p-value': kolmogorov_p
        })


    with tab4:
        st.markdown('<h2 class="section-header">Análisis de Control</h2>', unsafe_allow_html=True)
        fig4, media_control, li, ls, media_obs, std_obs, mas2, menos2, fuera_2sigma, total_fuera, fuera_inf, fuera_sup = metricas_clinica.Calculos_Control()
        st.plotly_chart(fig4, use_container_width=True, key="control_plot")
        st.markdown('<h3 class="section-header">Estadísticas de Control</h3>', unsafe_allow_html=True)
        mostrar_tarjetas({
            'Media Control': media_control,
            'Límite Inferior': li,
            'Límite Superior': ls,
            'Media Observada': media_obs,
            'Desviación Estándar Observada': std_obs,
            '+2σ': mas2,
            '−2σ': menos2,
            '±2σ': fuera_2sigma,
            'Total Fuera de Control': total_fuera,
            'Fuera límite Inferior': fuera_inf,
            'Fuera límite Superior': fuera_sup
        })


    with tab5:
        st.markdown('<h2 class="section-header">Análisis de Incertidumbre</h2>', unsafe_allow_html=True)
        fig5, media_observada, std_observada, error_estandar = metricas_clinica.Calculos_Incertidumbre()
        st.plotly_chart(fig5, use_container_width=True, key="incertidumbre_plot")
        st.markdown('<h3 class="section-header">Estadísticas de Incertidumbre</h3>', unsafe_allow_html=True)
        mostrar_tarjetas({
            'Media Observada': media_observada,
            'Desviación Estándar Observada': std_observada,
            'Error Estándar': error_estandar
        })


if __name__ == "__main__":
    main()
