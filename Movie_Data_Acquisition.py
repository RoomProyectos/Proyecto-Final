from functions import get_movies_data, find_imdbid, get_movies_info
import pandas as pd
import os

print("------------------------")
print(" Movie Data Acquisition")
print("------------------------")

# Path to Movies Data file
movie_data_path = "Data/Movies_Data.csv"

# Path to Movies Data file with IMDB ID
movie_data_ID_path = "Data/Movies_Data_IMDBID.csv"

# Check whether the files exist. If not, generate them
if os.path.exists(movie_data_ID_path):
    print(" >> Loading movie data with IMDB ID")
    df_all_movies = pd.read_csv(movie_data_ID_path, sep=";", encoding="UTF-8", dtype={'IMDB ID': str})   
    df_all_movies["Writers"] = df_all_movies["Writers"].apply(lambda x: [a.strip() for a in x.replace("[","").replace("]", "").replace("'","").split(",")])
else:    
    # Check whether the files exists 
    if os.path.exists(movie_data_path):
        print(" >> Loading movie data")
        df_all_movies = pd.read_csv(movie_data_path, sep=";", encoding="UTF-8")        
    else:
        print(" >> Obtaining movies data from imsdb.com")
        df_all_movies = get_movies_data()
    
    df_corpus = pd.read_csv("Data/Corpus_movie_meta_data.csv")
    df_corpus = df_corpus[["title", "writers", "imdbid"]]
    print(" >> Obtaining IMDB ID")
    df_all_movies["IMDB ID"] = df_all_movies.apply(lambda row: find_imdbid(row["Title"], row["Writers"], df_corpus), axis=1)
    df_all_movies.to_csv("Data/Movies_Data_IMDBID.csv", sep=";", encoding="utf-8", index=False)

print(" >> Obtaining movie metadata from IMDB")
all_movies_info = pd.DataFrame(get_movies_info(df_all_movies["IMDB ID"].values))

df_all_movies_with_info = df_all_movies.merge(all_movies_info, how='left')
df_all_movies_with_info.to_pickle("Data/All_movies_with_info.pkl")

print(" >> Completed. All movies saved to All_movies_with_info.pkl in Data folder.")