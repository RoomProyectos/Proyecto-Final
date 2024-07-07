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

st.title("Mirando con lupa... 🔍")
st.write(f"""En esta página analizaremos cada película por separado. Te invitamos a explorarlas de manera individual 
         seleccionando una película específica de nuestro dataset y ver detalles representativos 
         sobre la relación entre hombres y mujeres en el cine. """)

st.write("""Hemos organizado la información para que puedas sumergirte en los aspectos más interesantes 
         de cada una y a través de esta funcionalidad, ofrecemos una mirada más profunda de cómo se distribuyen el 
         número de personajes, los diálogos por sexo, la distribución de los roles o la polaridad vs subjetividad.""")

st.subheader("""¡¡A explorar!!""")

# Cargar el dataset
file_path = 'Data/movies_final_aux.pkl'
data = pd.read_pickle(file_path)

file_path_dialogues = 'Data/movies_final.pkl'
data_dialogues = pd.read_pickle(file_path_dialogues)

# Mostrar las películas disponibles en la barra lateral
selected_movie = st.selectbox(":point_down: Seleccione una película a continuación. :point_down:", data['Movie'].unique())

filtered_data = data[data["Movie"] == selected_movie]

index_filtered_dialogues = data_dialogues[data_dialogues["Movie"] == selected_movie].index[0]
filtered_dialogues = data_dialogues[data_dialogues["Movie"] == selected_movie].loc[index_filtered_dialogues,"Merged Dialogues"]

############## IMPRIMIR LOS GRÁFICOS Y LAS 2 COLUMNAS ##################
st.subheader('Un dato vale más que mil palabras')

# Mostrar estadísticas en dos columnas
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Personajes Masculinos", value=filtered_data["Male Characters"])
    st.metric(label="Personajes Femeninos", value=filtered_data["Female Characters"])
with col2:
    st.metric(label="Palabras Masculinas", value=filtered_data["Male Total Word Count"])
    st.metric(label="Palabras Femeninas", value=filtered_data["Female Total Word Count"])
with col3:
    st.metric(label="Media de Palabras Masculinas", value=int(filtered_data["Male Mean Word Count"]))
    st.metric(label="Media de Palabras Femeninas", value=int(filtered_data["Female Mean Word Count"]))

################# PIE CHARTS ####################
color_discrete_map = {
    'Femenino': '#FFC000', 
    'Masculino': '#E7E6E6'
}

# Crear el gráfico de torta Total de personajes por sexo
fig_total_personajes = px.pie(values=[filtered_data["Male Characters"].values[0], filtered_data["Female Characters"].values[0]],
                                names=['Masculino', 'Femenino'], title='Total de personajes por sexo', hole = 0.4,
                                color = ['Masculino', 'Femenino'],
                                color_discrete_map = color_discrete_map)

# Añadir información adicional al pasar el ratón
fig_total_personajes.update_traces(hoverinfo='label+percent+value', textinfo='value+percent', textposition='inside')

# Crear gráfico de torta en Plotly - Total palabras por sexo
fig_word_count = px.pie(values=[filtered_data["Male Total Word Count"].values[0], filtered_data["Female Total Word Count"].values[0]],
                        labels={'Sex': 'Sexo', 'Word Count': 'Número de Palabras'},
                        names=['Masculino', 'Femenino'], title='Total de palabras por sexo', hole = 0.4,
                        color = ['Masculino', 'Femenino'],
                        color_discrete_map = color_discrete_map)

fig_word_count.update_traces(hoverinfo='label+percent+value', textinfo='value+percent', textposition='inside')

col1, col2 = st.columns(2, vertical_alignment= "center")
with col1:
    st.plotly_chart(fig_total_personajes)
with col2:
    st.plotly_chart(fig_word_count)    

dict_sex = {"Female": "Femenino","Male" : "Masculino"}

filtered_dialogues['Word Count'] = filtered_dialogues['Lines'].apply(lambda x: len(str(x).split()))
filtered_dialogues["Sex"] = filtered_dialogues["Sex"].replace(dict_sex)
main_characters = filtered_dialogues.sort_values("Word Count", ascending=False).head(10)

# main_characters["Sex"] = main_characters["Sex"].replace(dict_sex)

# st.subheader(f"{}")
st.subheader(f""" Quién se come el pastel en {selected_movie}""")

st.write(""" Al seleccionar los diez personajes con más diálogos en cada película, los hombres, siguiendo la tónica general, suelen dominar la lista. 
         Ese mayor peso de personajes masculinos influye en la narrativa, dando más espacio y profundidad 
         a las voces masculinas mientras que las femeninas son menos representadas.""")

fig_main_characters = px.sunburst(main_characters, path=["Sex", "Character"], values="Word Count",                                  
                                  title='Reparto de personajes principales',
                                  color = "Sex",
                                  color_discrete_map = color_discrete_map)
fig_main_characters.update_layout(
    
    height=650  # Altura del gráfico
)

st.plotly_chart(fig_main_characters)


################# BUBBLE CHARTS ####################          ##################################################################################
       
# Bubble Chart - Sentimiento por personaje (segregado por sexo)
fig_sentiment_scatter_by_sex = px.scatter(data_frame = filtered_dialogues,
                        x            = "Polarity",
                        y            = "Subjectivity",
                        color        = "Sex",
                        hover_name   = "Character",                   
                        color_discrete_map = color_discrete_map,
                        size       = "Word Count",
                        title      = "Polaridad vs subjetividad media por personaje (segregado por sexo)")
fig_sentiment_scatter_by_sex.update_layout(
    xaxis_title='Polaridad',
    yaxis_title='Subjetividad'
)
fig_sentiment_scatter_by_sex.update_layout(
    
    height=600  # Altura del gráfico
)

st.plotly_chart(fig_sentiment_scatter_by_sex)
            # Cambiar las etiquetas de 'Male' y 'Female' ????(si da tiempo)?????????????????????????????????????????????????????????????????????????????????????????????????


# Bubble Chart - Sentimiento por personaje 
fig_sentiment_scatter = px.scatter(data_frame = filtered_dialogues,
                        x            = "Polarity",
                        y            = "Subjectivity",
                        color        = "Character",
                        hover_name   = "Character",                   
                        # color_discrete_map = {"Male" : "#E7E6E6", "Female" : "#FFC000"},
                        size       = "Word Count",
                        title      = "Polaridad vs subjetividad media por personaje")

fig_sentiment_scatter.update_layout(
    xaxis_title='Polaridad',
    yaxis_title='Subjetividad'
)

fig_sentiment_scatter.update_layout(
    
    height=600  # Altura del gráfico
)

st.plotly_chart(fig_sentiment_scatter)
            # Cambiar las etiquetas de 'Male' y 'Female' ????(si da tiempo)?????????????????????????????????????????????????????????????????????????????????????????????????