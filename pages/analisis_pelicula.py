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

st.subheader("Mirando con lupa...")
st.markdown(""":point_down: Seleccione una película a continuación. :point_down:""")


# Función para cargar y procesar el dataset
def load_and_process_data(file_path):
    data = pd.read_pickle(file_path)
    return data

# Cargar el dataset
file_path = 'Data/movies_final.pkl'

# Cargar y procesar el dataset
data = load_and_process_data(file_path)

# Función para obtener estadísticas de una película específica
def get_movie_stats(data, selected_movie):
    movie_data = data[data['Movie'] == selected_movie].iloc[0]
    dialogues_df = pd.DataFrame(movie_data['Merged Dialogues'])
    
    # Contar personajes masculinos y femeninos
    sex_counts = dialogues_df['Sex'].value_counts()
    
    # Contar número total de palabras por sexo
    dialogues_df['Word Count'] = dialogues_df['Lines'].apply(lambda x: len(str(x).split()))
    word_counts = dialogues_df.groupby('Sex')['Word Count'].sum()
    
    return sex_counts, word_counts, dialogues_df

# Mostrar las películas disponibles en la barra lateral
selected_movie = st.selectbox("Películas", data['Movie'].unique())

# Obtener estadísticas para la película seleccionada
sex_counts, word_counts, dialogues_df = get_movie_stats(data, selected_movie)

# Mostrar estadísticas en dos columnas
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Personajes Masculinos", value=sex_counts.get('Male', 0))
    st.metric(label="Personajes Femeninos", value=sex_counts.get('Female', 0))
with col2:
    st.metric(label="Palabras Masculinas", value=word_counts.get('Male', 0))
    st.metric(label="Palabras Femeninas", value=word_counts.get('Female', 0))

# Crear gráfico de histograma en Plotly
def plot_word_count_by_sex(dialogues_df):
    fig = px.histogram(dialogues_df, x='Sex', y='Word Count', histfunc='sum',
                       title=f'Número total de palabras por sexo en "{selected_movie}"',
                       labels={'Sex': 'Sexo', 'Word Count': 'Número de Palabras'},
                       color='Sex',
                       color_discrete_map={'Male': '#2297E6', 'Female': '#28E2E5'})
    return fig

fig = plot_word_count_by_sex(dialogues_df)
st.plotly_chart(fig)

# Mostrar gráfico de histograma de número de personajes por género
fig_sex_hist = px.histogram(dialogues_df, x='Sex', histfunc='count',
                            title=f'Número de personajes por género en "{selected_movie}"',
                            labels={'Sex': 'Género', 'count': 'Número de Personajes'},
                            color='Sex',
                            color_discrete_map={'Male': '#2297E6', 'Female': '#28E2E5'})
fig_sex_hist.update_layout(bargap=0.1)  # Ajuste de espacio entre barras
st.plotly_chart(fig_sex_hist)