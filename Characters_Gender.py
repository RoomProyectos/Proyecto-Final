from functions import load_pickle, get_full_actors_list, ChatGPT_get_actors_sex
import pandas as pd
import os

CHAT_GPT_KEY = os.getenv('chatgpt_key')

df_all_movies_with_info = load_pickle("Data/All_movies_with_info.pkl", " >> Loading file")

actors_list = get_full_actors_list(df_all_movies_with_info)

actors_sex = ChatGPT_get_actors_sex(actors_list, api_key=CHAT_GPT_KEY, gap=13)

for index, movie in df_all_movies_with_info.iterrows():
    movie_cast = movie["Cast and Characters"]
    if isinstance(movie_cast, pd.DataFrame) and not movie_cast.empty:            
        cast_with_sex = movie_cast.merge(actors_sex, on="Actor/Actress", how="left")
        df_all_movies_with_info.at[index,"Cast and Characters"] = cast_with_sex

df_all_movies_with_info.to_pickle("Data/All_movies_with_Gender.pkl")