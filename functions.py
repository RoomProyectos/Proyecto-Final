import re
import time
import threading
import pickle
import requests
import pandas as pd
import numpy as np

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from openai import OpenAI

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob

print(" >> Functions has been loaded")

def get_movies_data():
    '''
    Obtains the movie title, writers and script url of all the movies in imsdb.com
    '''
    BASE_URL = "https://imsdb.com"
    response = requests.get(BASE_URL + "/all-scripts.html")
    soup_all_movies = BeautifulSoup(response.text, 'html.parser')
    aux_movie_list = soup_all_movies.find_all("p")

    movie_list = []

    for index, movie in enumerate(aux_movie_list):        
        print(f"Index {index}: ", end="")

        aux_link = movie.find("a")
        
        title = aux_link.text.strip()
        
        if ", The" in title:
            title = "The " + title.replace(", The", "")

        aux_writers = movie.find("i").text.split("Written by")[1].split(",")
        writers = [writer.strip() for writer in aux_writers]
           
        movie_url = BASE_URL + aux_link["href"].replace(" ", "%20")
        script_url = get_movie_script_url(movie_url)
        
        if script_url == "No script":
            print ("No Script")            
            continue
        else:            
            movie_list.append([title, writers, script_url])
            print (title)

    df_movies = pd.DataFrame(movie_list, columns=["Title", "Writers", "Script URL"])
    df_movies.to_csv("Data/Movies_Data.csv", sep=";", encoding="UTF-8", index=False)

    return df_movies

def get_movie_script_url(movie_url: str) -> str:
    '''
    Obtains the real url of the script from the intermediate movie page
    '''
    BASE_URL = "https://imsdb.com"
    movie_response = requests.get(movie_url)
    movie_soup = BeautifulSoup(movie_response.text, 'html.parser')

    try:
        url_script = BASE_URL + movie_soup.find_all("a")[-7]["href"]        
    except:
        url_script = "No script"

    return url_script

def get_movie_script_soups(movies: pd.DataFrame) -> dict:
    '''
    Retrieves a dictionary with the scripts' HTML page from the movies list and stores them in a Pickle file
    '''    
    movie_soup_dict = {}

    for movie in movies.values:        
        film_title = movie[0]
        print(film_title, end="")
        url = movie[2]
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            movie_soup_dict[film_title] = soup
            print(" - Correcto")
        except:
            print (" - Error")
            continue
        
    # Save the dictionary in a pickle file
    with open("Data/Movie_Script_Soups.pkl", 'wb+') as f:
        pickle.dump(movie_soup_dict, f)

    return movie_soup_dict

def get_min_indent (script: list) -> int:
    ''' 
    Returns the minimum indentation of an script splitted in a list of lines
    '''   

    min_indent = 0
    base_indent = get_avg_indent(script)

    for line in script:
        if re.search(r"\S", line):
            indent = len(line) - len(line.lstrip())
            if indent < base_indent:
                min_indent = indent
    
    return min_indent

def get_avg_indent(script: list) -> int:
    ''' 
    Returns the average indentation of an script splitted in a list of lines
    '''
    indent = 0
    num_lines = 0  

    for line in script:        
        if re.search(r"\S", line):
            num_lines += 1
            indent += len(line) - len(line.lstrip())

    if num_lines != 0:
        average_indent = indent//num_lines
    else:
        average_indent = 50

    return average_indent

def preprocess_script(script: str) -> list:
    '''
    Preprocess an script deleting parentheses and text between them and returning it split into a list of lines
    '''
    # Pattern for deleting text between parentheses (included)
    pattern = re.compile(r'\(.*?\)', re.DOTALL)
    preprocessed_script = pattern.sub("", script)
    script_lines = preprocessed_script.split('\n')

    return script_lines

def get_dialogs(script_lines: list) -> list:
    '''
    Returns a list with the dialogs per character of a movie script based on indentation
    '''
    dialogs_list = []
    aux_dialog_list = list()
    aux_dict = dict()
    min_indent = get_min_indent(script_lines[10:])

    for line in script_lines[10:]:
        # Skip the line if it contains the text of a transition                        
        if re.search(r"(FADE IN|FADE OUT|CUT TO|EXT.|INT.|EXTERIOR|INTERIOR|SEQUENCE|TITLE|DISSOLVE|CLOSE UP|PAN TO|ANGLE ON|CUT FROM BLACK|FLASHBACK|VIEW|MONTAGE|BACK TO|FLASH CUT|FREEZE FRAME|IRIS IN|IRIS OUT|MATCH|SMASH CUT|TIME CUT|WIPE)", line):
            continue        
        
        # Calculate the indentation of the current line
        line_indent = len(line) - len(line.lstrip())

        if line_indent > min_indent:            
            if line.strip().isupper():
                if aux_dialog_list:
                    aux_dict["Lines"] = " ".join(aux_dialog_list)
                    dialogs_list.append(aux_dict)
                aux_dict = dict()
                aux_dialog_list = []
                aux_dict["Character"] = line.strip()
            else:
                try:
                    if aux_dict["Character"]:
                        dialog_line = line.replace("--","").strip()
                        dialog_line = re.sub(r"\d+\.", "", dialog_line)
                        if dialog_line:
                            aux_dialog_list.append(dialog_line)
                except:
                    continue
        
    if aux_dialog_list:
        aux_dict["Lines"] = " ".join(aux_dialog_list)
        dialogs_list.append(aux_dict)

    return dialogs_list

def show_elapsed_time(start_time, message):
    '''
    Show the elapsed time since a given start time
    '''
    while not stop_thread:
        elapsed_time = time.time() - start_time
        print(f"\r{message}: {int(elapsed_time)} s", end="")
        time.sleep(1)

def load_pickle(filename, message):
    '''
    Load a pickle file showing the elapsed time and provided message.
    '''
    global stop_thread
    start_time = time.time()
    stop_thread = False
    
    thread = threading.Thread(target=show_elapsed_time, args=(start_time,message))
    thread.start()

    try:        
        with open(filename, 'rb') as file:
            data = pickle.load(file)
    except KeyboardInterrupt:
        print("\nInterruption detected. Stopping file load...")
        stop_thread = True
        thread.join()
        raise
    finally:
        stop_thread = True
        thread.join() 

    elapsed_time = time.time() - start_time  # Calcular el tiempo transcurrido total
    print(f"\n Total time elapsed: {int(elapsed_time)} seconds")
    return data

def find_imdbid(movie: str, writers: list, movie_meta_data):
    '''
    Returns de IMDB Id in the metadata dataframe for a given movie and writers
    '''
    for writer in writers:        
        try:
            # Using just the surname to find a match
            writer = writer.strip().split(" ")[1]
            
            filter_movie = movie_meta_data['title'] == movie
            filter_writer = movie_meta_data['writers'].str.contains(writer, case=False, na=False, regex=False)
            
            aux_id = movie_meta_data[(filter_movie) & (filter_writer)]['imdbid'].values
            
            if len(aux_id) > 1:                
                continue
            else:
                aux_id = str(aux_id[0])
            
            if len(aux_id) >= 7:
                return aux_id
            else:
                longitud = 7 - len(aux_id)                
                return "0"*longitud + aux_id
        except:            
            continue
    
    return "0"

def get_movies_info(films_ids:list):
    '''
    Get movie information and "Cast and Characters" from IMDB for a given IMDB Id. list
    '''
    options = Options()
    
    chrome_prefs = {
        "profile.managed_default_content_settings.javascript": 2,
        "intl.accept_languages": "en,en_US"
    }
    
    options.add_experimental_option("prefs", chrome_prefs)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    browser = webdriver.Chrome(options=options)

    list_aux = list()
    num_ids = len (films_ids)

    for index, id in enumerate(films_ids):
        if id == "0":
            continue

        print("                                 \r", end="")
        print(f" Processing... {index+1}/{num_ids}", end="")

        aux_movie_dict = dict()

        # IMDB ID
        aux_movie_dict["IMDB ID"] = id

        # Access the movie URL with current ID
        browser.get(f"https://www.imdb.com/title/tt{id}")
        movie_soup = BeautifulSoup(browser.page_source, "html.parser")
        
        # Year
        try:            
            aux_movie_dict["Year"] = movie_soup.find_all("ul", class_ = "ipc-inline-list")[1].find("li", role="presentation", class_="ipc-inline-list__item").text                                                                        
        except:
            aux_movie_dict["Year"] = np.nan

        # IMDB Rating
        try:            
            aux_movie_dict["Rating"] = movie_soup.find("span", class_ = "sc-bde20123-1 cMEQkK").text.replace(",",".")
        except:
            aux_movie_dict["Rating"] = np.nan

        # Genres
        try:
            aux_movie_dict["Genres"] = [genre.text for genre in movie_soup.find_all("span", class_="ipc-chip__text")[:-1]]
        except:
            aux_movie_dict["Genres"] = np.nan

        # Director
        try:
            aux_movie_dict["Director"] = movie_soup.find("a", class_ = "ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link").text
        except:
            aux_movie_dict["Director"] = np.nan
    
        aux_movie_dict["Cast and Characters"] = pd.DataFrame(get_movie_cast(browser, id))
        
        list_aux.append(aux_movie_dict)
    
    browser.close()
    return list_aux

def get_movie_cast(browser: webdriver, id: str):
    '''
    Obtains the full Cast and Character list of a movie from IMDB providing
     an instance of a WebDriver object and the IMDB ID (without "tt")

    Notes
    -----

    Returns a list with rows for all the actors, containing a dictionary with 
     Actor/Actress name and a list of the roles
    '''
    cast_and_characters = list()

    # Get the full credits page
    try:
        browser.get(f"https://www.imdb.com/title/tt{id}/fullcredits")
        cast_soup = BeautifulSoup(browser.page_source, "html.parser")

        for item in cast_soup.find_all("tr", class_=["odd", "even"]):
            aux_cast_dict = dict()            
            cast_links = item.find_all('td')

            try:
                aux_cast_dict["Actor/Actress"] = cast_links[1].text.strip()
            except: 
                aux_cast_dict["Actor/Actress"] = np.nan

            try:
                aux_cast_dict["Characters"] = [character.text for character in cast_links[3].find_all("a")]
            except:
                aux_cast_dict["Characters"] = np.nan

            cast_and_characters.append(aux_cast_dict)
    except:
        pass
    
    return cast_and_characters

def get_full_actors_list(movie_database: pd.DataFrame):
    '''   
    Returns a sorted list of all the unique actors in our movie database.
    
    '''
    aux_actors_list = []
    actors_list = []
    movies = movie_database[movie_database["Cast and Characters"].notna()]

    for index, movie in movies.iterrows():
        movie_cast = movie["Cast and Characters"]

        if isinstance(movie_cast, pd.DataFrame) and not movie_cast.empty:
            aux_actors_list.extend(movie_cast["Actor/Actress"])

    actors_list = sorted(set(str(actor) for actor in aux_actors_list if actor is not None))

    return actors_list

def ChatGPT_get_actors_sex(actors_list:list, api_key:str, gap:int) -> pd.DataFrame:
    '''
    Connects to the OpenAI API and requests the sex for a provided actor list
    '''
    # Initialize the OpenAI Client
    client = OpenAI(api_key=api_key)

    df_actor_list = pd.DataFrame(actors_list).rename(columns={0: "Actor/Actress"})
    # Loop for splitting the queries to ChatGPT API 
    aux_actors_sex_list = []
    index = 0
    for _ in range(len(df_actor_list) // 25):
        actor_list = df_actor_list.iloc[index:index+25]['Actor/Actress'].tolist()

        completion = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = [{
                "role": "user", 
                "content": f"I need to know if these actors are male or female: {actor_list}. Please provide the answer in a csv format, writing the actors name and 'M' instead of 'male' and 'F' instead of 'female'."
            }]
        )

        aux_actors_sex_list.extend([x.split(",") for x in completion.choices[0].message.content.split("\n")])
        index += 25
       
    actors_sex = pd.DataFrame(aux_actors_sex_list)[[0, 1]].rename(columns={0: 'Actor/Actress', 1: 'Sex'})

    actors_sex = process_ChatGPT_result(actors_sex, gap)
    return actors_sex

def ChatGPT_get_missing_characters_sex(missing_characters:dict, api_key:str) -> dict:
    '''
    Connects to the OpenAI API and requests the sex for a provided characters of a movie
    '''
    # Initialize the OpenAI Client
    client = OpenAI(api_key=api_key)

    # Loop the movies and request the character sex
    aux_dict = {}
    for film in missing_characters.keys():
        characters = missing_characters[film]

        completion = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = [{
                "role": "user", 
                "content": f"I need to know if these characters from a film are male or female. This is the film {film} and these are the characters {characters}. Please provide the answer in a csv format, writing the character name and 'M' instead of 'male' and 'F' instead of 'female'."
            }]
        )
        
        aux_dict[film] = [x for x in completion.choices[0].message.content.split("\n")]
    
    return aux_dict

def change_sex_literal(sex_initial):
    if "M" in sex_initial:
        return "Male"
    elif "F" in sex_initial:
        return "Female"
    
def clean_actor_name(name):
    name = name.replace("[","").replace("]","").replace('"', "").strip("'")
    return name

def clean_character_name(name):
    name = name.replace("[","").replace("]","").replace('"', "").strip().strip("'")
    return name

def process_ChatGPT_result(actors_sex: pd.DataFrame, gap: int) -> pd.DataFrame :
    actors_sex["Sex"] = actors_sex["Sex"].apply(change_sex_literal)

    for index in range(gap,len(actors_sex)):
        actors_sex.at[index,"Actor"] = clean_actor_name(actors_sex.loc[index,"Actor"])

    return actors_sex

def merge_lines_per_character(film_dialogues):
    agg_function = {'Lines' : lambda x: ' '.join(x)}
    return film_dialogues.groupby('Character').agg(agg_function).reset_index()

def get_character_sex(character, cast):
    try:
        for index, actor in cast.iterrows():
            for role in actor['Characters']:
                if character.capitalize() in role:
                    return actor['Sex']
                else:
                    pass
    except:
        return np.nan

def get_actor_movies(actor_name:str, movie_database: pd.DataFrame) -> list:
    '''   
    Find all the movies in our movie database in which an actor appears.

    Notes
    ------
    Works with partcial matches.
    '''
    
    actor_movie_list = []
    movie_database = movie_database[movie_database["Cast and Characters"].notna()]

    for index, movie in movie_database.iterrows():
        movie_cast = movie["Cast and Characters"]

        if isinstance(movie_cast, pd.DataFrame) and not movie_cast.empty:
            actors = movie_cast[movie_cast["Actor/Actress"].notna()]
            matching_actors = actors[actors["Actor/Actress"].str.contains(actor_name, case=False, na=False, regex=False)]
            if not matching_actors.empty:
                for actor in matching_actors["Actor/Actress"]:
                    actor_movie_list.append([movie["IMDB ID"], movie["Title"], actor])

    if actor_movie_list:
        print (f"Coincidencias encontradas: {len(actor_movie_list)}")
        return actor_movie_list
    else:
        print ("No se ha encontrado coincidencias")

def sentiment_analysis(text):
    # Use the SentimentIntensityAnalyzer to compute the sentiment scores 
    sentiment = SentimentIntensityAnalyzer().polarity_scores(text)    

    return sentiment["compound"]

def get_subjectivity(text):
    aux_text = TextBlob(text)
    subjectivity = aux_text.subjectivity
	
    return subjectivity

def obtain_data_aux(df):
    # Create the dataframe
    movies = list()
    years = list()
    ratings = list()
    genres = list()
    directors = list()
    female_characters = list()
    male_characters = list()
    female_polarities = list()
    male_polarities = list()
    female_subjectivities = list()
    male_subjectivities = list()
    female_wcounts_mean = list()
    male_wcounts_mean = list()
    female_wcounts_total = list()
    male_wcounts_total = list()

    data_dict = dict()

    # Add a column for the word count of each character in each movie
    for _, movie_row in df.iterrows():
        dialogue = movie_row['Merged Dialogues']
        dialogue['Word Count'] = dialogue['Lines'].apply(lambda x: len(x.split()))

        movie = movie_row['Movie'] # Get the movie name
        year = movie_row['Year'] # Get the year of the movie
        rating = movie_row['Rating'] # Get the rating of the movie
        genre = movie_row['Genres'] # Get the genres of the movie
        director = movie_row['Director'] # Get the director of the movie
        dialogue = movie_row['Merged Dialogues'] # Get the dialogue subdataframe

        # Group the data
        groupby_sex = dialogue.groupby('Sex', as_index=False).agg(
            characters = ('Sex', 'count'),
            mean_polarity = ('Polarity', 'mean'), 
            mean_subjectivity = ('Subjectivity', 'mean'), 
            mean_word_count = ('Word Count', 'mean'), 
            total_word_count = ('Word Count', 'sum'))

        # Access the specific values for polarity, subjectivity and word count
        for sex_index, sex_row in groupby_sex.iterrows():
            if len(groupby_sex) == 2: # Check if the two sexes are present in the movie
                if sex_row['Sex'] == 'Female':
                    female_character = groupby_sex.loc[sex_index, 'characters']
                    female_polarity = groupby_sex.loc[sex_index, 'mean_polarity']
                    female_subjectivity = groupby_sex.loc[sex_index, 'mean_subjectivity']
                    female_wcount_mean = groupby_sex.loc[sex_index, 'mean_word_count']
                    female_wcount_total = groupby_sex.loc[sex_index, 'total_word_count']
                elif sex_row['Sex'] == 'Male':
                    male_character = groupby_sex.loc[sex_index, 'characters']
                    male_polarity = groupby_sex.loc[sex_index, 'mean_polarity']
                    male_subjectivity = groupby_sex.loc[sex_index, 'mean_subjectivity']
                    male_wcount_mean = groupby_sex.loc[sex_index, 'mean_word_count']
                    male_wcount_total = groupby_sex.loc[sex_index, 'total_word_count']
            
            elif len(groupby_sex) == 1: # Otherwise check which of the sexes is present, and assign 0 to the other sex
                if sex_row['Sex'] == 'Female':
                    female_character = groupby_sex.loc[sex_index, 'characters']
                    female_polarity = groupby_sex.loc[sex_index, 'mean_polarity']
                    female_subjectivity = groupby_sex.loc[sex_index, 'mean_subjectivity']
                    female_wcount_mean = groupby_sex.loc[sex_index, 'mean_word_count']
                    female_wcount_total = groupby_sex.loc[sex_index, 'total_word_count']

                    female_character = 0
                    male_polarity = 0
                    male_subjectivity = 0
                    male_wcount_mean = 0
                    male_wcount_total = 0
                
                elif sex_row['Sex'] == 'Male':
                    male_character = groupby_sex.loc[sex_index, 'characters']
                    male_polarity = groupby_sex.loc[sex_index, 'mean_polarity']
                    male_subjectivity = groupby_sex.loc[sex_index, 'mean_subjectivity']
                    male_wcount_mean = groupby_sex.loc[sex_index, 'mean_word_count']
                    male_wcount_total = groupby_sex.loc[sex_index, 'total_word_count']

                    female_character = 0
                    female_polarity = 0
                    female_subjectivity = 0
                    female_wcount_mean = 0
                    female_wcount_total = 0

                
        # Append the values to the lists
        movies.append(movie)
        years.append(year)
        ratings.append(rating)
        directors.append(director)
        genres.append(genre)
        female_characters.append(female_character)
        male_characters.append(male_character)
        female_polarities.append(female_polarity)
        male_polarities.append(male_polarity)
        female_subjectivities.append(female_subjectivity)
        male_subjectivities.append(male_subjectivity)
        female_wcounts_mean.append(female_wcount_mean)
        male_wcounts_mean.append(male_wcount_mean)
        female_wcounts_total.append(female_wcount_total)
        male_wcounts_total.append(male_wcount_total)

    # Populate the dictionary with the data
    data_dict['Movie'] = movies
    data_dict['Year'] = years
    data_dict['Rating'] = ratings
    data_dict['Genre'] = genres
    data_dict['Director'] = directors
    data_dict['Female Characters'] = female_characters
    data_dict['Male Characters'] = male_characters
    data_dict['Female Polarity'] = female_polarities
    data_dict['Male Polarity'] = male_polarities
    data_dict['Female Subjectivity'] = female_subjectivities
    data_dict['Male Subjectivity'] = male_subjectivities
    data_dict['Female Mean Word Count'] = female_wcounts_mean
    data_dict['Male Mean Word Count'] = male_wcounts_mean
    data_dict['Female Total Word Count'] = female_wcounts_total
    data_dict['Male Total Word Count'] = male_wcounts_total

    return pd.DataFrame(data_dict)