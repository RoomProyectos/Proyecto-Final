import pandas as pd
import streamlit as st

def get_navigation():
    inicio = st.Page("streamlit_app.py", title="Sinopsis", icon="🎬", default=True)
    analisis_general = st.Page("pages/analisis_general.py", title="Plano General", icon="🎥", default=False)
    analisis_pelicula = st.Page("pages/analisis_pelicula.py", title="Primer Plano", icon="🍿", default=False)
    
    
    lista_paginas = [inicio, analisis_general, analisis_pelicula]

    navegacion = st.columns(len(lista_paginas))
    for nav_col, page in zip (navegacion, lista_paginas):
        with nav_col:
            st.page_link(page._page, label=page.title, icon=page.icon)


def get_unique_genres(df):
    
    aux_genre_list = []
    for _, row in df[["Genres"]].iterrows():
        aux_genre_list.extend(row["Genres"])

    genre_list = sorted(set(aux_genre_list))
    return genre_list

def get_genres_count(df):
    dict_genres = {genre : 0 for genre in get_unique_genres(df)}

    for _, row in df[["Genres"]].iterrows():
        genres = row["Genres"]
        for genre in genres:
            dict_genres[genre] += 1

    genres_df = pd.DataFrame (list(dict_genres.items()), columns=['Genre', 'Count']).sort_values("Count", ascending=False).reset_index(drop=True)
    return genres_df
