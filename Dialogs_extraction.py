import pandas as pd
from functions import preprocess_script, get_dialogs, load_pickle, get_movie_script_soups
import os

movie_soups_path = "Data/Movie_Script_Soups.pkl"

if os.path.exists(movie_soups_path):
    print(" >> Loading movie script soups file")
    # Load pickle file with the movie scripts dictionary
    movie_soups = load_pickle(movie_soups_path, " >> Loading file")
else:
    print(" >> Obtaining movies scripts from imsdb.com")
    movies = pd.read_csv("Data/Movies_Data.csv", encoding="utf-8", sep=";")
    movie_soups = get_movie_script_soups(movies)

error_movie_list = []
movie_dialogs_list = []
print("-------------------")
print(" Processing movies")
print("-------------------")

for movie in movie_soups.keys():
    print(movie, end="")
    
    try:
        script = movie_soups[movie].find("pre").get_text()        
        if len(script) == 0:
            error_movie_list.append([movie, "No lines"])
            print(" - Error: No lines")
            continue
    except:        
        error_movie_list.append([movie, "No <pre> tag"])
        print(" - Error: No <pre> tag")
        continue
    
    script_lines = preprocess_script(script)
    dialogs_list = get_dialogs(script_lines)        
    df_dialogs = pd.DataFrame(dialogs_list)

    if df_dialogs.shape[1] == 0 or df_dialogs.shape[0] < 200:
        error_movie_list.append([movie, "Insuficient dialogs"])
        print(" - Error: Insuficient dialogs")
        continue    
    
    print (f" - Dialog lines extracted: {df_dialogs.shape[0]}")

    movie_dialogs_list.append([movie,df_dialogs])

SCRIPTS_PATH = "Data/Scripts/"

if not os.path.exists(SCRIPTS_PATH):
    os.makedirs(SCRIPTS_PATH)

df_error_movies = pd.DataFrame(error_movie_list, columns=["Movie", "Error"])
df_error_movies.to_csv("Data/Error_Movie_List.csv", sep=";", encoding="UTF-8")

df_movies_aux = pd.DataFrame(movie_dialogs_list, columns=["Movie", "Dialogs"])
df_movies_aux["CSV Path"] = df_movies_aux["Movie"].apply(lambda x: str(x).replace(":","").replace(" ","_") + ".csv")
df_movies_aux.to_pickle("Data/Movie_Dialogs_List.pkl")

for movie in movie_dialogs_list:
    aux_path = SCRIPTS_PATH + str(movie[0]).replace(":","").replace(" ", "_") + ".csv"
    movie[1].to_csv(aux_path, sep=";", encoding="utf-8")

print("---------------------------")
print(" Process completed")
print(f" Movies processed: {len(movie_soups)}")
print(f" Movies with dialogs: {len(movie_dialogs_list)}")
print(f" Movies with errors: {len(error_movie_list)}")
print("---------------------------")