import pandas as pd
import json

cidar = 'output/cidar.json'
chat = 'output/chat.json'
alpagasus = 'output/alpagasus.json'

# Open the JSON file and load its content into a Python object
with open(cidar, mode='r', encoding='utf-8') as file:
    cidar_data = json.load(file)
    cidar_df = pd.DataFrame(cidar_data)
# print("len(cidar_df):", len(cidar_df))

with open(chat, mode='r', encoding='utf-8') as file:
    chat_data = json.load(file)
    chat_df = pd.DataFrame(chat_data)
# print("len(chat_df):", len(chat_df))

with open(alpagasus, mode='r', encoding='utf-8') as file:
    alpagasus_data = json.load(file)
    alpagasus_df = pd.DataFrame(alpagasus_data)
# print("len(alpagasus_df):", len(alpagasus_df))

# Select and rename the columns in 'alpagasus_df'
alpagasus_df = alpagasus_df[['Sentence', 'Response']].rename(columns={'Sentence': 'instruction', 'Response': 'alpagasus_output'})
cidar_df.rename(columns={'model_output': 'cidar_output'}, inplace=True)
chat_df.rename(columns={'model_output': 'chat_output'}, inplace=True)
# print("len(alpagasus_df):", len(alpagasus_df))
# print("len(cidar_df):", len(cidar_df))
# print("len(chat_df):", len(chat_df))
print("chat_df['instruction'].nunique():", chat_df['instruction'].nunique())
print("cidar_df['instruction'].nunique():", cidar_df['instruction'].nunique())
print("alpagasus_df['instruction'].nunique():", alpagasus_df['instruction'].nunique())

# Merge 'chat_df' and 'alpagasus_df' first
merged_df = pd.merge(chat_df, alpagasus_df, on='instruction', how='inner')
merged_df.drop_duplicates(inplace=True)
print("len(merged_df):", len(merged_df))
unique_values = set(merged_df['instruction']) - set(merged_df['instruction'].unique())

print("r:", unique_values)
print("merged_df['instruction'].nunique():", merged_df['instruction'].nunique())

# # Then merge the result with 'cidar_df'
# df = pd.merge(merged_df, cidar_df, on='instruction', how='inner')
