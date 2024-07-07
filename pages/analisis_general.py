import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_functions import *


def main():    
    # Configuración de la página y pestaña
    st.set_page_config(page_title = "Cine y Ciencia de Datos",
                    page_icon = ":panda_face:"
                    ) 

    ################# CARGA DE ESTILOS Y NAVEGACIÓN ###############
    with open("styles.css") as css_file:
        css_content = css_file.read()

    with open("scripts.js") as js_file:
        js_content = js_file.read()
        
    st.markdown(f"""<style>{css_content}</style>""", unsafe_allow_html=True)
    get_navigation()
    ################# CARGA DE ESTILOS Y NAVEGACIÓN ###############
    # Ruta del archivo
    file_path = 'Data/movies_final_aux.pkl'

    # Cargar y procesar el dataset
    movies_df = pd.read_pickle(file_path)

    ################ INTRO ####################

    # Crear la aplicación de Streamlit
    st.title('Cómo está repartido el pastel :pie:')
    st.markdown("""Los guiones de las películas son más que simples narrativas; 
                son reflejos de la sociedad y de cómo se representan diferentes voces en la gran pantalla. 
                Al examinar estos aspectos, buscamos desentrañar patrones y tendencias que pueden revelar sesgos, 
                estereotipos o incluso cambios progresivos en la industria cinematográfica. Más especificamente desde el punto
                de vista de sexos.""")

    st.subheader('Personajes por sexo y género')
    st.markdown("""Utilizamos técnicas de procesamiento del lenguaje natural (NLP) para analizar los guiones y extraer 
                datos relevantes sobre el número de palabras y personajes. Esta metodología nos permite obtener una visión 
                general de las dinámicas de género en la narrativa cinematográfica. Para poder explorar dichos datos, por favor, 
                seleccione los géneros que le pueda interesar así como un rango temporal.""")

    ############# MULTISELECT POR GÉNERO #################

    #obtención de la lista de géneros
    genres = set()
    for item in movies_df['Genre']:
        for genre in item:
            genres.add(genre)

    selected_genres = st.multiselect(label= "Selecciona uno o más géneros:", options = genres, default = genres)

    if len(selected_genres) == 0:
        st.error("Por favor, selecciona al menos un género.", icon="🚨")
    else:
        # Filtrado del dataframe con los géneros seleccionados
        index_set = set()
        for selected_genre in selected_genres:
            for index, row in movies_df.iterrows():
                if selected_genre in row['Genre']:
                    index_set.add(index)
                else:
                    pass
        index_set = list(index_set)

        filtered_movies_genres = movies_df.loc[index_set].sort_values(by='Movie', ascending=True)

        ################ SLIDER POR AÑO ####################

        min_year = filtered_movies_genres['Year'].min()
        max_year = filtered_movies_genres['Year'].max()

        
        # Crear el slider para seleccionar el año
        selected_year = st.slider('Selecciona el año', min_year, max_year, value=[min_year, max_year])            
        # Filtrar las películas del año seleccionado            
        filtered_movies_years = filtered_movies_genres[filtered_movies_genres['Year'].between(selected_year[0],selected_year[1])]
        
        if len(filtered_movies_years) == 0:
            st.error("No hay películas que mostrar. Por favor, añade más géneros o amplía el rango de años.", icon="🚨")
        else: 
            st.write(f"Películas entre el año **{selected_year[0]}** y el **{selected_year[1]}** | Total de películas analizadas: **{len(filtered_movies_years)}**")
                    
            # Calcular totales y medias
            total_personajes_femenino = filtered_movies_years['Female Characters'].sum().round(2)
            total_personajes_masculino = filtered_movies_years['Male Characters'].sum().round(2)
            
            media_personajes_femenino = filtered_movies_years['Female Characters'].mean().round(2)
            media_personajes_masculino = filtered_movies_years['Male Characters'].mean().round(2)
            
            total_palabras_femenino = filtered_movies_years['Female Total Word Count'].sum().round(2)
            total_palabras_masculino = filtered_movies_years['Male Total Word Count'].sum().round(2)

            media_palabras_femenino = filtered_movies_years['Female Mean Word Count'].mean().round(2)
            media_palabras_masculino = filtered_movies_years['Male Mean Word Count'].mean().round(2)

            color_discrete_map = {
                'Femenino': '#FFC000', 
                'Masculino': '#E7E6E6'
            }
            # Crear el gráfico de torta Total de personajes por sexo
            fig_total_personajes = px.pie(values=[total_personajes_femenino, total_personajes_masculino],
                                        names=['Femenino', 'Masculino'], title='Personajes por sexo', hole = 0.4,
                                        color = ['Femenino', 'Masculino'],
                                        color_discrete_map = color_discrete_map)
                                        #   color_discrete_sequence="Masculino":"#E7E6E6", "Femenino":"#FFC000"])
            # Añadir información adicional al pasar el ratón
            fig_total_personajes.update_traces(hoverinfo='label+percent+value', textinfo='value+percent', textposition='inside')
            
            # Crear el gráfico de torta Total de palabras por sexo
            fig_total_palabras = px.pie(values=[total_palabras_femenino, total_palabras_masculino],
                                        names=['Femenino', 'Masculino'], title='Palabras por sexo', hole = 0.4,
                                        color = ['Femenino', 'Masculino'],
                                        color_discrete_map = color_discrete_map)
            # Añadir información adicional al pasar el ratón
            fig_total_palabras.update_traces(hoverinfo='label+percent+value', textinfo='value+percent', textposition='inside')
            
            # Crear el gráfico de torta Media de palabras por sexo por película
            fig_media_palabras_pelicula = px.pie(values=[media_palabras_femenino, media_palabras_masculino], 
                                                names=['Femenino', 'Masculino'], title='Media de palabras por sexo y película', 
                                                color = ['Femenino', 'Masculino'],
                                                    color_discrete_map = color_discrete_map, hole = 0.4)
            fig_media_palabras_pelicula.update_traces(hoverinfo='label+percent+value', textinfo='value+percent', textposition='inside')


            ############## IMPRIMIR LOS GRÁFICOS Y LAS 2 COLUMNAS ##################

            st.subheader('De media, solamente 1 de cada 4 personajes es mujer')
            st.markdown("""Analizamos la proporción de personajes masculinos y femeninos en una amplia gama de películas, 
                        cubriendo diferentes géneros y épocas. Este análisis nos permite identificar patrones 
                        y tendencias en la representación de sexo a lo largo del tiempo. Exploramos cómo varía la representación 
                        de personajes masculinos y femeninos según el género cinematográfico. Por ejemplo, ¿los dramas tienden 
                        a tener más personajes femeninos que las películas de acción? ¿Qué géneros presentan una mayor equidad 
                        de sexo en sus personajes? """)
            col1, col2 = st.columns(2, vertical_alignment= "center")
            with col1:
                st.plotly_chart(fig_total_personajes)
            with col2:
                st.write("**Independientemente del género...**")
                st.write("""...observamos un patrón persistente en la industria cinematográfica: 
                        casi siempre hay más personajes masculinos que femeninos. Esta tendencia se observa 
                        tanto en géneros tradicionalmente dominados por hombres, como la acción y la ciencia ficción, como en géneros donde 
                        se esperaría una representación más equilibrada, como el drama y la comedia.""")
                st.metric(label="Media de personajes masculinos por película", value=media_personajes_masculino.astype(int))
                st.metric(label="Media de personajes femeninos por película", value=media_personajes_femenino.astype(int))
                

            st.subheader('Más palabras para los hombres')
            st.markdown("""Analizamos los guiones cinematográficos para extraer dos datos clave: el total de palabras 
                        destinadas a los personajes masculinos y a los personajes femeninos. En la mayoría de los casos, 
                        los personajes masculinos tienen significativamente más palabras que los personajes femeninos. 
                        A pesar de que el total de palabras favorece a los personajes masculinos, observamos que la media de 
                        palabras por personaje de cada sexo es más equilibrada. Sin embargo, esta aparente paridad en la media de 
                        palabras se da porque hay muchos menos personajes femeninos en comparación con los masculinos.""")
            col3, col4 = st.columns(2)
            with col3:
                st.plotly_chart(fig_total_palabras)
            with col4:
                st.plotly_chart(fig_media_palabras_pelicula)

            # ################ BUBBLE CHARTS ####################
            
            # Bubble Chart media de polaridad por sexo
            # Cáculo de datos
            media_polaridad_femenino = filtered_movies_years['Female Polarity'].mean().round(2)
            media_polaridad_masculino = filtered_movies_years['Male Polarity'].mean().round(2)
            media_subjetividad_femenino = filtered_movies_years['Female Subjectivity'].mean().round(2)
            media_subjetividad_masculino = filtered_movies_years['Male Subjectivity'].mean().round(2)
            
            bubble_data1 = {'Gender': ['Femenino', 'Masculino'],
                    'Polarity': [media_polaridad_femenino, media_polaridad_masculino],
                    'Subjectivity': [media_subjetividad_femenino, media_subjetividad_masculino],
                    'Total Characters': [total_personajes_femenino, total_personajes_masculino]}
            
            st.subheader("Análisis de la polaridad vs subjetividad")

            st.write("""Los gráficos a continuación nos ayuda a comprender cómo se expresan los 
                    personajes masculinos y femeninos en términos de emociones y opiniones. """)
            
            st.write("""La polaridad mide el tono emocional del texto, desde negativo a positivo. Una 
                    polaridad alta indica un tono más positivo, mientras que una polaridad baja 
                    sugiere un tono más negativo.""")

            st.write("""La subjetividad refleja el grado en que el texto 
                    es personal y subjetivo, en lugar de objetivo y basado en hechos. Un valor 
                    alto de subjetividad indica que el texto está cargado de opiniones personales.""")

            # Bubble Chart
            fig_scatter1 = px.scatter(data_frame = bubble_data1,
                                    x          = "Polarity",
                                    y          = "Subjectivity",
                                    color      = "Gender",
                                    color_discrete_map = {'Masculino': '#E7E6E6', 'Femenino': '#FFC000'},
                                    size       = "Total Characters",
                                    title      = "Polaridad vs Subjetividad media por sexo")
            
            fig_scatter1.update_layout(
                xaxis_title='Polaridad',
                yaxis_title='Subjetividad'
            )

            st.plotly_chart(fig_scatter1)
            
            st.write("""En general, podemos observar que los diálogos de las mujeres son más positivos y emocionales,
                    mientras que el de los hombres tiende a ser más neutro. """)

            # Bubble Chart sentimiento todas las películas(femenino)
            fig_scatter2 = px.scatter(data_frame = filtered_movies_years,
                                    x          = "Female Polarity",
                                    y          = "Female Subjectivity",
                                    size       = "Female Characters",
                                    hover_name = "Movie",
                                    title      = "Polaridad vs Subjetividad de todas las películas (Femenino)")
            
            fig_scatter2.update_layout(
                xaxis_title='Polaridad Femenina',
                yaxis_title='Subjetividad Femenina'
            )

            fig_scatter2.update_traces(marker=dict(color = "#FFC000", line=dict(width=0.7, color='white')))
            
            st.plotly_chart(fig_scatter2)

            # Bubble Chart sentimiento todas las películas(masculino)

            fig_scatter3 = px.scatter(data_frame = filtered_movies_years,
                                    x          = "Male Polarity",
                                    y          = "Male Subjectivity",
                                    size       = "Male Characters",
                                    hover_name = "Movie",
                                    title      = "Polaridad vs Subjetividad de todas las películas (Masculino)")
            fig_scatter3.update_layout(
                xaxis_title='Polaridad Masculina',
                yaxis_title='Subjetividad Masculina'
            )
            fig_scatter3.update_traces(marker=dict(color = "#E7E6E6", line=dict(width=0.5, color='black')))
            st.plotly_chart(fig_scatter3)
            

            # ################ SCATTER CHART ####################
            
            st.subheader("Paridad vs Rating de las películas")

            st.write("""El gráfico a continuación explora la relación entre la paridad en los personajes 
                    de las películas y sus ratings. La paridad se refiere al equilibro entre personajes femeninos y masculinos.
                    Se calcula un ratio de personajes femeninos entre los masculinos, donde un valor de 1 equivaldría a que hay
                    1 mujer por cada hombre.""")
            
            st.write("""Se puede observar en este gráfico que la mayoría de películas tiene una paridad inferior a 1,
                    lo cual demuestra que hay un desequilibro entre sexos, habiendo incluso el doble de personajes
                    masculinos que femeninos en la gran mayoría de películas.""")
            
            
            st.write("""Aunque no existe una correlación directa entre la paridad de género y el rating de una película, 
                    ¿qué sugiere el siguiente gráfico? ¿Podemos ver películas con alta paridad y que tengan alto rating?
                    ¿Será la paridad influyente en la popularidad y rating de las películas?""")

            sex_ratio = filtered_movies_years['Female Characters'] / filtered_movies_years['Male Characters']

            fig_scatter4 = px.scatter(data_frame = filtered_movies_years,
                                    x          = sex_ratio,
                                    y          = "Rating",
                                    color      = "Movie",  
                                    hover_name = "Movie")
            
            fig_scatter4.add_vline(x=1, line_width=2, line_color="#FFC000")


            fig_scatter4.add_shape(type="line", x0=-0.2, y0=5,x1=3.5, y1=5, line=dict(color="#FFC000", width=2))

            fig_scatter4.update_layout(
                xaxis_title='Paridad',
                yaxis_title='Rating'
            )

            fig_scatter4.update_layout(
        
                height=500  # Altura del gráfico
            )

            st.plotly_chart(fig_scatter4)
        

            # ################ LINE CHART ####################
            # Data
            filtered_movies_years_sorted = filtered_movies_years.sort_values(by='Year')

            graph_options = filtered_movies_years.iloc[:, 5:13].columns

            func_dictionary = {"Female Characters" : "Personajes Femeninos",
                                "Male Characters" : "Personajes Masculinos",
                                "Female Polarity" : "Polaridad Femenina",
                                "Male Polarity" : "Polaridad Masculina",
                                "Female Subjectivity" : "Subjetividad Femenina",
                                "Male Subjectivity" : "Subjetividad Masculina",
                                "Female Mean Word Count" : "Palabras Femeninas (Media)",
                                "Male Mean Word Count" : "Palabras Masculinas (Media)"}

            st.subheader("Cómo ha cambiado el cine a lo largo de los años")

            selected_columns = st.multiselect(label = "Selecciona uno o más datos para mostrar", 
                                            options = graph_options,
                                            format_func=lambda x: func_dictionary[x])
            
            graph_df_sorted = filtered_movies_years.groupby("Year", as_index = False).mean("Female Characters").sort_values(by='Year', ascending=True)
            graph_years = graph_df_sorted["Year"].values

            if len(selected_columns) == 0:            
                pass
            else:
                fig_line = go.Figure()

                for column in selected_columns:
                
                    fig_line.add_trace(go.Scatter(
                                            x          = graph_years,
                                            y          = graph_df_sorted[column].values,
                                            mode       = "lines",
                                            name       = func_dictionary[column]
                                            )
                    )
                st.plotly_chart(fig_line)

if __name__ == "__main__":
    main()