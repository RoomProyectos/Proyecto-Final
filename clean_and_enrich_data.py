from functions import load_pickle, sentiment_analysis, get_subjectivity, obtain_data_aux
import pandas as pd
import os

movie_dialogues_raw = load_pickle('Data/all_movies_final_data.pkl', " >> Loading movies dialogues file").drop("Dialogues", axis=1).reset_index(drop=True)

sum_nan_dialogues = 0
sum_nan_cast = 0
agg_function = {'Lines' : lambda x: ' '.join(x), 'Sex' : 'first'}

for index, movie in movie_dialogues_raw.iterrows():
    dialogues = movie["Merged Dialogues"]
    cast = movie["Cast and Characters"]
    nan_dialogues = dialogues.isna().sum()
    nan_cast = cast.isna().sum()
    
    if nan_dialogues.sum() > 0:
        sum_nan_dialogues += 1
        dialogues = dialogues.dropna()
        movie_dialogues_raw.at[index,"Merged Dialogues"] = dialogues.reset_index(drop=True)
    
    movie_dialogues_raw.at[index,"Merged Dialogues"] = dialogues.groupby('Character').agg(agg_function).reset_index()

    if nan_cast.sum() > 0:
        sum_nan_cast += 1
        cast = cast.dropna()
        movie_dialogues_raw.at[index,"Cast and Characters"] = cast.reset_index(drop=True)

if sum_nan_dialogues > 0:
    print (f"Movies with Nans in dialogues cleaned: {sum_nan_dialogues}")

if sum_nan_cast > 0:
    print (f"Movies with Nans in cast cleaned: {sum_nan_cast}")

for index, movie in movie_dialogues_raw.iterrows():
    dialogues = movie["Merged Dialogues"]
    if isinstance(dialogues, pd.DataFrame) and not dialogues.empty:
        dialogues["Polarity"] = dialogues["Lines"].apply(sentiment_analysis)
        dialogues["Subjectivity"] = dialogues["Lines"].apply(get_subjectivity)

movies_final_aux = obtain_data_aux(movie_dialogues_raw)
movies_final_aux.to_pickle("Data/movies_final_aux.pkl")