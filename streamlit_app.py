import streamlit as st

import plotly.express as px
import pandas as pd
# from streamlit_option_menu import option_menu
# import altair as alt
from streamlit_functions import *
import os

from PIL import Image


################ CONFIGURACIÓN DE LA PÁGINA ##############################
def main():    
    # Configuración de la página y pestaña
    st.set_page_config(page_title = "Cine y Ciencia de Datos",
                    page_icon = ":panda_face:",
                    # layout = "wide",                    
                    # initial_sidebar_state = ""
                    ) #optional

    ################# CARGA DE ESTILOS Y NAVEGACIÓN ###############
    with open("styles.css") as css_file:
        css_content = css_file.read()

    with open("scripts.js") as js_file:
        js_content = js_file.read()
        
    st.markdown(f"""<style>{css_content}</style>""", unsafe_allow_html=True)
    get_navigation()
    ################# CARGA DE ESTILOS Y NAVEGACIÓN ###############
    
    st.title("El guion cuenta una historia, los datos cuentan otra.", anchor=None)
    
    
    # image = Image.open("Data/film.jpg")
    # st.image(image = image)
    
    # st.markdown("""
    # <h1 style='text-align:right; color:red'>
    #     ... los datos cuentan otra.
    # </h1>
    # """, unsafe_allow_html=True)
    # st.title("... los datos cuentan otra.", anchor=None)

    st.markdown("""En este espacio, te invitamos a explorar el fascinante mundo del análisis de datos aplicado a 
    la industria cinematográfica. """, unsafe_allow_html=True)
    
    st.markdown("""Nuestro proyecto se centra en dos vertientes fundamentales:""", unsafe_allow_html=True)
    
    st.markdown(""" - `Análisis de los metadatos de películas` """, unsafe_allow_html=True)
    
    st.markdown(""" - `Procesamiento del lenguaje natural (NLP) de sus guiones`""", unsafe_allow_html=True)
    
    st.markdown("""A través de estas dos perspectivas, buscamos revelar las historias ocultas detrás de la narrativa y los números.
    """, unsafe_allow_html=True)

    st.markdown("""Nuestro objetivo es proporcionar una visión integral de cómo los datos pueden complementar y 
    enriquecer nuestra comprensión de las historias que vemos en la pantalla grande. Al combinar análisis de metadatos 
    con técnicas avanzadas de NLP, no solo revelamos patrones interesantes, sino que también planteamos nuevas preguntas 
    y perspectivas sobre la creación y recepción de películas.""")

    st.markdown("""Esperamos que disfrutes explorando los diversos análisis y visualizaciones que hemos preparado. 
    ¡Gracias por visitarnos y sumergirte en el apasionante cruce entre el cine y la ciencia de datos!""")

    ################ CARGAR DATASETS ##############################

    # Cargar el dataset de películas
    df = pd.read_pickle("Data/movies_final.pkl")
    # Crear el conteo de géneros
    genre_count = get_genres_count(df)

    ################ 60% DE LAS PELÍCULAS.... ####################
    top_genres_pct = genre_count["Count"].head().sum()/genre_count["Count"].sum() * 100
    
    st.markdown(f"""
    <h2>
        El {top_genres_pct:.2f} % de las películas se encaja en 5 categorías
    </h2>
    """, unsafe_allow_html=True)

    # st.subheader(f"{top_genres_pct:.2f} % de las películas se encajan en 5 categorías")
    st.markdown("""Una obra audiovisual puede pertenecer a diferentes géneros.""")
    st.markdown("""Teniendo esto en cuenta, si identificamos cada uno de los géneros de cada película y lo agrupamos, obtenemos lo siguientes datos:""")

    columns = st.columns(5)
              
    for col, genre in zip(columns, genre_count.loc[0:5].values):            
        with col:          
            st.metric(label=genre[0], value=(f"{(genre[1]/genre_count["Count"].sum() * 100):.1f} %"))            

    st.markdown(f"""
    <h2 class="Total">
        Número total de películas: {len(df)}
    </h2>
    """, unsafe_allow_html=True)

    fig = px.histogram(data_frame=genre_count,
                        title="Número de películas con cierto género",
                        x="Genre",
                        y="Count",
                        color="Genre",
                        labels={"Genre":"Género cinematográfico"}
                        )

    fig.update_layout(
        xaxis_title='',
        yaxis_title=''        
    )

    st.plotly_chart(fig)

    # Crear el gráfico de torta
    fig = px.pie(genre_count, values='Count', names='Genre', title='Porcentaje sobre el total de géneros', hole = 0.5)

    # Añadir información adicional al pasar el ratón
    # bottom_genres = ', '.join(bottom_values['genres'])
    fig.update_traces(
        hoverinfo='label+percent+value'
        # hovertemplate='<b>Otros Géneros</b>: %{value} películas<br>(%{percent})<br>Géneros agrupados:<br>' + bottom_genres
    )
    fig.update_layout(
        width=1000,  # Ancho del gráfico
        height=600  # Altura del gráfico
    )
    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)


    ################ SLIDER POR AÑO ####################

    if not df['Year'].dropna().empty:
        min_year = df['Year'].min()
        max_year = df['Year'].max()

        if min_year != max_year:
            # Crear el slider para seleccionar el año
            selected_year = st.slider('Selecciona el año', min_year, max_year, [1995, 2001])            
            # Filtrar las películas del año seleccionado            
            filtered_movies = df[df['Year'].between(selected_year[0],selected_year[1])].drop(["Merged Dialogues", "IMDB ID", "Cast and Characters"], axis=1)
            
            # Mostrar el DataFrame filtrado
            st.write(f"Películas del año {selected_year}:")
            st.dataframe(filtered_movies)
        else:
            st.write(f"Todas las películas en el dataset son del año {min_year}.")
    else:
        st.write("No hay datos válidos en la columna 'release_date'.")    

if __name__ == "__main__":
    main()