import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import base64

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

# Función para generar datos de ejemplo
@st.cache_data
def generate_sample_data():
    np.random.seed(42)
    return np.random.normal(123.5, 15.2, 100)

# Función para calcular estadísticas de atípicos
def calcular_atipicos(data):
    q1 = np.percentile(data, 25)
    q2 = np.percentile(data, 50)  # mediana
    q3 = np.percentile(data, 75)
    q5 = np.percentile(data, 95)
    iqr = q3 - q1
    lim_inf = q1 - 1.5 * iqr
    lim_sup = q3 + 1.5 * iqr
    atipicos = data[(data < lim_inf) | (data > lim_sup)]
    
    return {
        'n': len(data),
        'q1': round(q1, 2),
        'q2': round(q2, 2),
        'q3': round(q3, 2),
        'q5': round(q5, 2),
        'iqr': round(iqr, 2),
        'lim_inf': round(lim_inf, 2),
        'lim_sup': round(lim_sup, 2),
        'cantidad_atipicos': len(atipicos)
    }

# Función para calcular estadísticas descriptivas
def calcular_descriptivas(data):
    return {
        'n': len(data),
        'media': round(np.mean(data), 2),
        'mediana': round(np.median(data), 2),
        'moda': round(stats.mode(data, keepdims=True)[0][0], 2),
        'rango': round(np.max(data) - np.min(data), 2),
        'varianza': round(np.var(data, ddof=1), 2),
        'desviacion_estandar': round(np.std(data, ddof=1), 2)
    }

# Función para calcular pruebas de normalidad
def calcular_normalidad(data):
    shapiro_stat, shapiro_p = stats.shapiro(data)
    ks_stat, ks_p = stats.kstest(data, 'norm', args=(np.mean(data), np.std(data)))
    
    return {
        'shapiro_p': round(shapiro_p, 6),
        'kolmogorov_p': round(ks_p, 6)
    }

# Función para calcular estadísticas de control
def calcular_control(data, media_control=120, std_control=10):
    media_obs = np.mean(data)
    std_obs = np.std(data, ddof=1)
    
    li = media_control - 2 * std_control
    ls = media_control + 2 * std_control
    
    mas2 = media_control + 2 * std_control
    menos2 = media_control - 2 * std_control
    
    fuera_2sigma = len(data[(data < menos2) | (data > mas2)])
    fuera_control_inf = len(data[data < li])
    fuera_control_sup = len(data[data > ls])
    total_fuera_control = fuera_control_inf + fuera_control_sup
    
    return {
        'media_control': media_control,
        'li': round(li, 2),
        'ls': round(ls, 2),
        'media_observada': round(media_obs, 2),
        'std_observada': round(std_obs, 2),
        'mas2': round(mas2, 2),
        'menos2': round(menos2, 2),
        'fuera_2sigma': fuera_2sigma,
        'total_fuera_control': total_fuera_control,
        'fuera_control_inf': fuera_control_inf,
        'fuera_control_sup': fuera_control_sup
    }

# Función para mostrar tarjetas de métricas
def mostrar_tarjetas(metricas, prefijo=""):
    cols = st.columns(3)
    items = list(metricas.items())
    
    for i, (key, value) in enumerate(items):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-header">{key.replace('_', ' ').title()}</div>
                <div class="metric-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

# Función para crear gráficos
def crear_grafico_atipicos(data, stats_atipicos):
    fig = go.Figure()
    
    # Boxplot
    fig.add_trace(go.Box(
        y=data,
        name="Datos",
        boxpoints="outliers",
        marker_color="#ff0064"
    ))
    
    fig.update_layout(
        title="Análisis de Valores Atípicos",
        yaxis_title="Valores",
        showlegend=False,
        height=400
    )
    
    return fig

def crear_grafico_descriptivos(data):
    fig = go.Figure()
    
    # Histograma
    fig.add_trace(go.Histogram(
        x=data,
        nbinsx=20,
        name="Distribución",
        marker_color="#ff0064",
        opacity=0.7
    ))
    
    # Línea de la media
    fig.add_vline(x=np.mean(data), line_dash="dash", line_color="red", 
                  annotation_text="Media")
    
    fig.update_layout(
        title="Distribución de Datos",
        xaxis_title="Valores",
        yaxis_title="Frecuencia",
        showlegend=False,
        height=400
    )
    
    return fig

def crear_grafico_normalidad(data):
    fig = go.Figure()
    
    # Q-Q plot
    from scipy import stats
    (osm, osr), (slope, intercept, r) = stats.probplot(data, dist="norm", plot=None)
    
    fig.add_trace(go.Scatter(
        x=osm, 
        y=osr,
        mode='markers',
        name='Datos observados',
        marker_color="#ff0064"
    ))
    
    fig.add_trace(go.Scatter(
        x=osm,
        y=slope * osm + intercept,
        mode='lines',
        name='Línea teórica',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        title="Q-Q Plot - Prueba de Normalidad",
        xaxis_title="Cuantiles Teóricos",
        yaxis_title="Cuantiles Observados",
        height=400
    )
    
    return fig

def crear_grafico_control(data, stats_control):
    fig = go.Figure()
    
    # Datos
    fig.add_trace(go.Scatter(
        x=list(range(len(data))),
        y=data,
        mode='lines+markers',
        name='Datos',
        line=dict(color='blue'),
        marker=dict(size=4)
    ))
    
    # Líneas de control
    fig.add_hline(y=stats_control['media_control'], line_dash="solid", 
                  line_color="green", annotation_text="Media Control")
    fig.add_hline(y=stats_control['li'], line_dash="dash", 
                  line_color="red", annotation_text="LI")
    fig.add_hline(y=stats_control['ls'], line_dash="dash", 
                  line_color="red", annotation_text="LS")
    
    fig.update_layout(
        title="Gráfico de Control",
        xaxis_title="Muestra",
        yaxis_title="Valores",
        height=400
    )
    
    return fig

def crear_grafico_incertidumbre(data):
    media = np.mean(data)
    std = np.std(data, ddof=1)
    error_std = std / np.sqrt(len(data))
    
    # Intervalo de confianza 95%
    ci_95 = stats.t.interval(0.95, len(data)-1, loc=media, scale=error_std)
    
    fig = go.Figure()
    
    # Distribución normal
    x = np.linspace(media - 4*std, media + 4*std, 100)
    y = stats.norm.pdf(x, media, std)
    
    fig.add_trace(go.Scatter(
        x=x, y=y,
        mode='lines',
        fill='tozeroy',
        name='Distribución',
        line=dict(color='#ff0064')
    ))
    
    # Intervalo de confianza
    fig.add_vrect(
        x0=ci_95[0], x1=ci_95[1],
        fillcolor="rgba(255,0,100,0.2)",
        annotation_text="IC 95%",
        annotation_position="top left"
    )
    
    fig.update_layout(
        title="Análisis de Incertidumbre",
        xaxis_title="Valores",
        yaxis_title="Densidad",
        height=400
    )
    
    return fig

# Interfaz principal
def main():
    # Header
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">Análisis Datos Clínicos</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Generar datos de ejemplo
    data = generate_sample_data()

    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["ATÍPICOS", "DESCRIPTIVOS", "NORMALIDAD", "CONTROL", "INCERTIDUMBRE"])
    
    with tab1:
        st.markdown('<h2 class="section-header">Análisis de Valores Atípicos</h2>', unsafe_allow_html=True)
        
        
        stats_atipicos = calcular_atipicos(data)
        fig = crear_grafico_atipicos(data, stats_atipicos)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('<h3 class="section-header">Estadísticas</h3>', unsafe_allow_html=True)
        mostrar_tarjetas(stats_atipicos)
    
    with tab2:
        st.markdown('<h2 class="section-header">Estadísticas Descriptivas</h2>', unsafe_allow_html=True)
        fig = crear_grafico_descriptivos(data)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<h3 class="section-header">Estadísticas</h3>', unsafe_allow_html=True)
        stats_descriptivas = calcular_descriptivas(data)
        mostrar_tarjetas(stats_descriptivas)
    
    with tab3:
        st.markdown('<h2 class="section-header">Pruebas de Normalidad</h2>', unsafe_allow_html=True)
        fig = crear_grafico_normalidad(data)
        st.plotly_chart(fig, use_container_width=True) 
        st.markdown('<h3 class="section-header">Pruebas Estadísticas</h3>', unsafe_allow_html=True)
        stats_normalidad = calcular_normalidad(data)
        mostrar_tarjetas(stats_normalidad)
    
    with tab4:
        st.markdown('<h2 class="section-header">Análisis de Control</h2>', unsafe_allow_html=True)
        stats_control = calcular_control(data)
        fig = crear_grafico_control(data, stats_control)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<h3 class="section-header">Estadísticas de Control</h3>', unsafe_allow_html=True)
        mostrar_tarjetas(stats_control)
    with tab5:
        st.markdown('<h2 class="section-header">Análisis de Incertidumbre</h2>', unsafe_allow_html=True)
        fig = crear_grafico_incertidumbre(data)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('<h3 class="section-header">Estadísticas de Incertidumbre</h3>', unsafe_allow_html=True)
        # Cálculos de incertidumbre
        media = np.mean(data)
        std = np.std(data, ddof=1)
        error_std = std / np.sqrt(len(data))
        ci_95 = stats.t.interval(0.95, len(data)-1, loc=media, scale=error_std)
        
        stats_incertidumbre = {
            'error_estandar': round(error_std, 2),
            'intervalo_confianza_95': f"({ci_95[0]:.1f}, {ci_95[1]:.1f})",
            'coeficiente_variacion': round((std/media)*100, 2)
        }
        
        mostrar_tarjetas(stats_incertidumbre)

if __name__ == "__main__":
    main()