#cargamos las librerias necesarias para todo el proyecto 
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import scipy.stats as stats
import matplotlib.pyplot as plt
from statsmodels.graphics.gofplots import qqplot
import os
from pathlib import Path
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
def cargar_archivos_excel_automatico():
    """
    Carga automáticamente todos los archivos Excel de las carpetas especificadas
    y los organiza en un diccionario jerárquico para fácil acceso.
    
    Returns:
        dict: Diccionario organizado como {carpeta: {archivo: dataframe}}
    """
    
    # Definir las rutas de las carpetas
    rutas = {
        "H_I": "datos/H-I-CORREGIDOS",
        "I_M_I": "datos/I-M-I CORREGIDOS", 
        "I_R": "datos/I-R"
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
    


class Metricas:
    """Se calculan las diferentes métricas para cada una de las pruebas de laboratorio."""
    
    def __init__(self, datos, archivo, prueba, columna="resultado", acceder_func=None,
                 controles=None, archivo_control=None, prueba_control=None, columna_control="resultado"):
        self.datos = datos  # conjunto completo de datos
        self.archivo = archivo  # por ejemplo 'H_I'
        self.prueba = prueba  # por ejemplo 'colesterol total'
        self.columna = columna  # por ejemplo 'resultado'
        self.acceder_func = acceder_func if acceder_func else self._acceso_directo
        self.controles = controles  # diccionario de controles
        self.archivo_control = archivo_control
        self.prueba_control = prueba_control
        self.columna_control = columna_control


    def _acceso_directo(self, datos, archivo, prueba, columna):
        return datos[archivo][prueba][columna]

    def obtener_columna(self):
        return self.acceder_func(self.datos, self.archivo, self.prueba, self.columna)

    def obtener_columna_control(self):
        if self.controles is not None and self.archivo_control is not None and self.prueba_control is not None:
            # Si se especifican controles, archivo_control y prueba_control, usar esos datos
            return self.acceder_func(self.datos, self.archivo_control, self.prueba_control, self.columna_control)
        elif all(v is not None for v in [self.archivo_control, self.prueba_control]):
            # Si solo se especifican archivo_control y prueba_control sin diccionario de controles
            return self.acceder_func(self.datos, self.archivo_control, self.prueba_control, self.columna_control)
        return None

    def Calculo_Atipicos(self):
        # Usando la nueva estructura de acceso a datos
        datos_columna = self.obtener_columna()
        
        n = len(datos_columna)
        q1 = datos_columna.quantile(0.25)
        q2 = datos_columna.quantile(0.50)
        q3 = datos_columna.quantile(0.75)
        iqr = q3 - q1
        lim_inf = q1 - 1.5 * iqr
        lim_sup = q3 + 1.5 * iqr
        
        # Crear DataFrame para plotly
        df_temp = pd.DataFrame({self.columna: datos_columna})
        atipicos = df_temp[(datos_columna < lim_inf) | (datos_columna > lim_sup)]
        cantidad_atipicos = len(atipicos)
        
        fig = px.box(df_temp, x=self.columna, title=None, template="simple_white")
        fig.update_traces(marker=dict(size=8, color="red", symbol="circle"))
        fig.update_layout(
            xaxis=dict(
                showline=True,
                showticklabels=True,
                linecolor='black',
                linewidth=1,
            ),
            yaxis=dict(
                showline=False,
                showticklabels=False,
                showgrid=False,
                zeroline=False
            ))
        return fig, n, q1, q2, q3,iqr, lim_inf, lim_sup, cantidad_atipicos
    
    def Calculo_Descriptivas(self):
        # Usando la nueva estructura de acceso a datos
        datos_columna = self.obtener_columna()
        n = len(datos_columna)
        media = datos_columna.mean()
        mediana = datos_columna.median()
        moda = datos_columna.mode()[0]
        rango = datos_columna.max() - datos_columna.min()
        varianza = datos_columna.var()
        desviacion_estandar = datos_columna.std()

        # Crear DataFrame para plotly
        df_temp = pd.DataFrame({self.columna: datos_columna})
        fig = px.histogram(df_temp, x=self.columna, title=None, template="simple_white")
        fig.update_layout(
            xaxis=dict(
                showline=True,
                showticklabels=True,
                linecolor='black',
                linewidth=1,
            ),
            yaxis=dict(
                showline=False,
                showticklabels=True,
                showgrid=True,
                zeroline=False
            ))
        fig.add_vline(x=media, line_dash="dash", line_color="red", annotation_text="Media", annotation_position="top",line_width=3,annotation_bgcolor="red",annotation_font_color="white",annotation_font_size=15) 
        return fig, n, media, mediana, moda, rango, varianza, desviacion_estandar

    def Calculo_Normalidad(self):
        # Usando la nueva estructura de acceso a datos
        datos = self.obtener_columna()
        
        shapiro_stat, shapiro_p = stats.shapiro(datos)

        mean_norm = np.mean(datos)
        std_norm = np.std(datos, ddof=1)
        stat_ks_norm, kolmogorov_p = stats.kstest(datos, 'norm', args=(mean_norm, std_norm))

        fig_qq = qqplot(datos, line='s')
        plt.close()

        ax = fig_qq.gca()
        puntos = ax.lines[0]
        linea_ref = ax.lines[1]

        x_data = puntos.get_xdata()
        y_data = puntos.get_ydata()
        x_line = linea_ref.get_xdata()
        y_line = linea_ref.get_ydata()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='markers',
            marker=dict(color='#ff5648'),
            name='Datos'
        ))

        fig.add_trace(go.Scatter(
            x=x_line,
            y=y_line,
            mode='lines',
            line=dict(color="#00ff00", dash='dash'),
            name='Línea de referencia'
        ))

        fig.update_layout(template="simple_white",
            showlegend=False,
            xaxis=dict(title='Cuantiles teóricos',
                showline=True,
                showticklabels=True,
                linecolor='black',
                linewidth=1,
            ),
            yaxis=dict(title='Cuantiles muestrales',
                showline=False,
                showticklabels=True,
                showgrid=True,
                zeroline=False
            )              
        )
        return fig, shapiro_p, kolmogorov_p

    def Calculos_Control(self):
        # Obtener los datos observados
        y = self.obtener_columna()
        x = list(range(len(y)))
        
        # Calcular estadísticas observadas
        media_observada = y.mean()
        std_observada = y.std()
        mas2 = media_observada + 2 * std_observada
        menos2 = media_observada - 2 * std_observada
        
        # Datos de control I-R hardcodeados
        controles_ir = {
            'colesterol': {'maximo': 165, 'minimo': 138, 'promedio': 152},
            'glucosa': {'maximo': 120, 'minimo': 68.2, 'promedio': 94},
            'trigliceridos': {'maximo': 98.7, 'minimo': 77.6, 'promedio': 88.2},
            'colesterol hdl': {'maximo': 98.4, 'minimo': 74.8, 'promedio': 86.6},
            'creatina': {'maximo': 1.01, 'minimo': 0.79, 'promedio': 0.9},
            # Controles patológicos
            'colesterol patologico': {'maximo': 275, 'minimo': 207, 'promedio': 241},
            'glucosa patologico': {'maximo': 269, 'minimo': 195, 'promedio': 232},
            'trigliceridos patologico': {'maximo': 276, 'minimo': 192, 'promedio': 234},
            'colesterol hdl patologico': {'maximo': 221, 'minimo': 147, 'promedio': 184},
            'creatina patologico': {'maximo': 5.33, 'minimo': 3.41, 'promedio': 4.37}
        }
        
        # Verificar si tenemos datos de control
        # Primero intentamos con los datos pasados como parámetro
        tiene_control_param = (
            self.controles is not None and 
            self.archivo_control is not None and 
            self.prueba_control is not None and
            self.archivo_control in self.controles and
            self.prueba_control in self.controles[self.archivo_control]
        )
        
        # Luego verificamos con los controles hardcodeados I-R
        # Normalizamos el nombre de la prueba para la comparación
        prueba_normalizada = self.prueba.lower().strip() if hasattr(self, 'prueba') and self.prueba else None
        tiene_control_hardcoded = prueba_normalizada in controles_ir
        
        # Determinar cuál usar
        if tiene_control_param:
            # Usar controles de parámetros
            control_info = self.controles[self.archivo_control][self.prueba_control]
            tiene_control = True
            fuente_control = "parametros"
        elif tiene_control_hardcoded:
            # Usar controles hardcodeados I-R
            control_info = controles_ir[prueba_normalizada]
            tiene_control = True
            fuente_control = "I-R"
        else:
            # Sin controles
            tiene_control = False
            fuente_control = None
        
        if tiene_control:
            # Caso con datos de control
            media_control = control_info['promedio']
            li = control_info['minimo']  # límite inferior
            ls = control_info['maximo']  # límite superior
            
            # Contar puntos fuera de control
            fuera_control_inf = (y < li).sum()
            fuera_control_sup = (y > ls).sum()
            total_fuera_control = fuera_control_inf + fuera_control_sup
            
            # Colorear puntos según criterios de control y 2σ
            colores = []
            for valor in y:
                if valor < menos2 or valor > mas2:
                    colores.append("red")
                elif valor < li or valor > ls:
                    colores.append("red")
                else:
                    colores.append("orange")
        else:
            # Caso sin datos de control - solo observados
            media_control = None
            li = None
            ls = None
            fuera_control_inf = 0
            fuera_control_sup = 0
            total_fuera_control = 0
            
            # Colorear solo según 2σ observadas
            colores = []
            for valor in y:
                if valor < menos2 or valor > mas2:
                    colores.append("red")
                else:
                    colores.append("orange")
        
        # Contar puntos fuera de 2σ observadas
        fuera_2sigma = ((y < menos2) | (y > mas2)).sum()
        
        # Crear la gráfica
        fig = go.Figure()
        
        # Agregar datos principales
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode="lines+markers",
            name="Datos",
            marker=dict(color=colores, size=6),
            line=dict(color="blue")
        ))
        
        # Agregar media observada (siempre presente)
        fig.add_trace(go.Scatter(
            x=x, y=[media_observada]*len(x),
            mode="lines",
            name="Media observada",
            line=dict(color="red", dash="dash")
        ))
        
        # Agregar límites 2σ observadas (siempre presentes)
        fig.add_trace(go.Scatter(
            x=x, y=[mas2]*len(x),
            mode="lines",
            name="+2σ observada",
            line=dict(color="orange", dash="dash")
        ))
        
        fig.add_trace(go.Scatter(
            x=x, y=[menos2]*len(x),
            mode="lines",
            name="−2σ observada",
            line=dict(color="orange", dash="dash")
        ))
        
        # Agregar elementos de control solo si están disponibles
        if tiene_control:
            fig.add_trace(go.Scatter(
                x=x, y=[media_control]*len(x),
                mode="lines",
                name="Media de control I-R" if fuente_control == "I-R" else "Media de control",
                line=dict(color="purple", dash="dot")
            ))
            
            fig.add_trace(go.Scatter(
                x=x, y=[ls]*len(x),
                mode="lines",
                name="Límite superior control",
                line=dict(color="green", dash="dot")
            ))
            
            fig.add_trace(go.Scatter(
                x=x, y=[li]*len(x),
                mode="lines",
                name="Límite inferior control",
                line=dict(color="green", dash="dot")
            ))
        
        # Título con información sobre el tipo de control usado
        titulo_base = "Gráfico de Control"
        if not tiene_control:
            titulo = titulo_base + " (Solo datos observados)"
        elif fuente_control == "I-R":
            titulo = titulo_base + f" (Control I-R: {prueba_normalizada})"
        else:
            titulo = titulo_base
        
        # Configurar layout
        fig.update_layout(
            showlegend=True,
            template="simple_white",
            title=titulo,
            xaxis=dict(
                title="Índice de muestra",
                showline=True,
                showticklabels=True,
                linecolor='black',
                linewidth=1
            ),
            yaxis=dict(
                title=self.columna,
                showline=False,
                showticklabels=True,
                showgrid=True,
                zeroline=False
            )
        )
        
        return fig, media_control, li, ls, media_observada, std_observada, mas2, menos2, fuera_2sigma, total_fuera_control, fuera_control_inf, fuera_control_sup
    def Calculos_Incertidumbre(self):
        # Usando la nueva estructura de acceso a datos
        y = self.obtener_columna()
        x = list(range(len(y)))

        media_observada = y.mean()
        std_observada = y.std()
        error_estandar = std_observada / np.sqrt(len(y))

        df_grafica = pd.DataFrame({
            "Índice de muestra": x,
            "Valor": y,
            "Error estándar": [error_estandar] * len(x)
        })

        fig = px.line(df_grafica, x="Índice de muestra", y="Valor", title=None, template="simple_white",error_y="Error estándar",error_y_minus="Error estándar")
        fig.update_layout(
            xaxis=dict(
                title="Índice de muestra",
                showline=True,
                showticklabels=True,
                linecolor='black',
                linewidth=1
            ),
            yaxis=dict(
                title=self.columna,
                showline=False,
                showticklabels=True,
                showgrid=True,
                zeroline=False
            )
        )
        return fig, media_observada, std_observada, error_estandar
datos = cargar_archivos_excel_automatico() # cargamos los datos de los archivos 

""" 
ejemplo para cargar metricas y figuras especificas de la clase }
metricas = Metricas(
    datos=datos,
    archivo='I_R',
    prueba='colesterol',
    controles=controles,
    archivo_control='I-R',
    prueba_control='colesterol',
)
"""

