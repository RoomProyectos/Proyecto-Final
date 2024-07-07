import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_functions import *

################# CARGA DE ESTILOS Y NAVEGACIÓN ###############
with open("styles.css") as css_file:
    css_content = css_file.read()

with open("scripts.js") as js_file:
    js_content = js_file.read()
    
st.markdown(f"""<style>{css_content}</style>""", unsafe_allow_html=True)
get_navigation()
################# CARGA DE ESTILOS Y NAVEGACIÓN ###############


################# CARGAR EL DATASET ###############

# Función para cargar y procesar el dataset
def load_and_process_data(file_path):
    data = pd.read_pickle(file_path)
    merged_dialogues = data['Merged Dialogues']
    
    if isinstance(merged_dialogues.iloc[0], pd.DataFrame):
        merged_dialogues_combined = pd.concat(merged_dialogues.values.tolist(), ignore_index=True)
    else:
        raise ValueError("'Merged Dialogues' does not contain DataFrames")
    
    return merged_dialogues_combined

# Función para contar personajes por género y graficar los resultados con Plotly
def plot_sex_counts_pie_plotly(df):
    sex_counts = df['Sex'].value_counts().reset_index()
    sex_counts.columns = ['Sex', 'Count']
    fig = px.pie(sex_counts, names='Sex', values='Count', title='Número de personajes por género', 
                 color='Sex', color_discrete_map={'Male': '#2297E6', 'Female': '#28E2E5'})
    return fig

# Título de la aplicación
st.title("Análisis de Género en Diálogos de Películas")

# Ruta del archivo
file_path = 'Data/movies_final.pkl'

# Cargar y procesar el dataset
df = load_and_process_data(file_path)

################# GRAFICAR EL DATASET ######################

# Graficar los resultados
fig = plot_sex_counts_pie_plotly(df)
st.plotly_chart(fig)

# Mostrar conteos
sex_counts = df['Sex'].value_counts()


############### 2 COLUMNAS CON NÚMERO DE SEXOS #####################

st.subheader("La gran mayoría de los personajes son masculinos")
st.markdown("""Según los datos sacados de los guiones de las películas, de los 7386 personajes, 5631 son masculinos, o sea, el 75%. 
            `De cada 4 personajes`, `3 son hombres` y solamente `1 es mujer`. Con un ratio de 3 por 1, las probabilidades de triunfar en 
            Hollywood es mucho menor para las mujeres.""")

# Mostrar los datos en formato de métricas
col1, col2 = st.columns(2)

col1.metric("Número de personajes masculinos", sex_counts.get('Male', 0))
col2.metric("Número de personajes femeninos", sex_counts.get('Female', 0))


