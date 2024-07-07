from functions import load_pickle, merge_lines_per_character, get_character_sex, ChatGPT_get_missing_characters_sex, clean_character_name, change_sex_literal
import pandas as pd
import os

CHAT_GPT_KEY = os.getenv('chatgpt_key')

movie_dialogues = load_pickle('Data/Movie_Dialogs.pkl', " >> Loading movies dialogues file")
movie_dialogues['Merged Dialogues'] = movie_dialogues['Dialogs'].apply(merge_lines_per_character)

movie_info = load_pickle('Data/All_movies_with_Gender.pkl', " >> Loading movies info file")
movie_info = movie_info.drop_duplicates(subset='Title', keep='first')

movie_dialogues_info = movie_dialogues.merge(movie_info, left_on='Movie', right_on='Title', how='left').drop(columns=['CSV Path', 'Title', 'Script URL'], axis = 1)

for index, movie in movie_dialogues_info.iterrows():
    cast = movie['Cast and Characters']
    movie['Merged Dialogues']['Sex'] = movie['Merged Dialogues']['Character'].apply(lambda character: get_character_sex(character, cast))

missing_characters = {}
for index, movie in movie_dialogues_info.iterrows():
    dialogues = movie['Merged Dialogues']
    missing_characters[movie['Movie']] = dialogues[dialogues['Sex'].isna()]['Character'].tolist()

missing_characters_sex = ChatGPT_get_missing_characters_sex(missing_characters, CHAT_GPT_KEY)

characters_sex_dict = {}
aux_movie_list = []
aux_character_list = []

for film in missing_characters_sex.keys():
    aux_movie_list.append(film)
    aux_character_list.append(pd.DataFrame([x.split(',') for x in missing_characters_sex[film]]).iloc[:, :2].rename(columns={0 : 'Character', 1 : 'Sex'}))

characters_sex_dict['Movie'] = aux_movie_list
characters_sex_dict['Characters'] = aux_character_list

character_sex_df = pd.DataFrame.from_dict(characters_sex_dict)

for index, movie in character_sex_df.iterrows():
    movie['Characters'] = movie['Characters'].map(clean_character_name, na_action='ignore')

for index, movie in character_sex_df.iterrows():
    movie['Characters']['Sex'] = movie['Characters']['Sex'].map(change_sex_literal, na_action='ignore')

for movie1, movie2 in zip(movie_dialogues_info.iterrows(), character_sex_df.iterrows()):
    movie_dialogues_info.at[movie1[0], 'Merged Dialogues'] = movie1[1]['Merged Dialogues'].merge(movie2[1]['Characters'], on='Character', how='left')

for index, movie in movie_dialogues_info.iterrows():
    dialogues = movie['Merged Dialogues']
    dialogues['Sex'] = dialogues.apply(lambda x: x['Sex_x'] if not pd.isna(x['Sex_x']) else x['Sex_y'], axis=1)
    dialogues.drop(columns=['Sex_x', 'Sex_y'], axis=1, inplace=True)

pd.to_pickle(movie_dialogues_info, 'Data/all_movies_final_data.pkl')