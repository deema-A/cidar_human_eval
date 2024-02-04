import gradio as gr
import pandas as pd
import random
from collections import defaultdict
import json

css = """
.rtl{
    text-align: right;
}
.selectize-dropdown, .selectize-input {
    direction: rtl !important;
}
"""
# Assuming 'data.json' is your JSON file
cidar = 'output/cidar.json'
chat = 'output/chat.json'
alpagasus = 'output/alpagasus.json'

# Open the JSON file and load its content into a Python object
with open(cidar, mode='r', encoding='utf-8') as file:
    cidar_data = json.load(file)
    cidar_df = pd.DataFrame(cidar_data)

with open(chat, mode='r', encoding='utf-8') as file:
    chat_data = json.load(file)
    chat_df = pd.DataFrame(chat_data)
    
with open(alpagasus, mode='r', encoding='utf-8') as file:
    alpagasus_data = json.load(file)
    alpagasus_df = pd.DataFrame(alpagasus_data)

# Select and rename the columns in 'alpagasus_df'
alpagasus_df = alpagasus_df[['Sentence', 'Response']].rename(columns={'Sentence': 'instruction', 'Response': 'alpagasus_output'})
cidar_df.rename(columns={'model_output': 'cidar_output'}, inplace=True)
chat_df.rename(columns={'model_output': 'chat_output'}, inplace=True)

# Merge 'chat_df' and 'alpagasus_df' first
merged_df = pd.merge(chat_df, alpagasus_df, on='instruction', how='inner')

# Then merge the result with 'cidar_df'
df = pd.merge(merged_df, cidar_df, on='instruction', how='inner')

# that keeps track of how many times each question has been used
question_count = {index: 0 for index in df.index}
model_rankings = defaultdict(lambda: {'1st': 0, '2nd': 0, '3rd': 0})


def get_rank_suffix(rank):
    if 11 <= rank <= 13:
        return 'th'
    else:
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        return suffixes.get(rank % 10, 'th')


def process_rankings(user_rankings):
    print("Processing Rankings:", user_rankings)  # Debugging print
    for answer_id, rank in user_rankings:
        model = answer_id.split('_')[0]  # Extracting the model name from the answer_id
        rank_suffix = get_rank_suffix(rank)
        model_rankings[model][f'{rank}{rank_suffix}'] += 1  # Using the correct suffix based on the rank

    file_path = 'users_ranking.txt'
    with open(file_path, 'a') as file:
        model_rankings_dict = dict(model_rankings)
        json.dump(model_rankings_dict, file)
        file.write('\n')  # Add a newline to separate entries
    print("Updated Model Rankings:", model_rankings)  # Debugging print
    return


def get_questions_and_answers():
    available_questions = [index for index, count in question_count.items() if count < 3]
    selected_indexes = random.sample(available_questions, min(4, len(available_questions)))
    for index in selected_indexes:
        question_count[index] += 1

    questions_and_answers = []
    for index in selected_indexes:
        question = df.loc[index, 'instruction']
        answers_with_models = [
            (df.loc[index, 'cidar_output'], 'CIDAR'),
            (df.loc[index, 'chat_output'], 'CHAT'),
            (df.loc[index, 'alpagasus_output'], 'ALPAGASUS')
        ]
        random.shuffle(answers_with_models)  # Shuffle answers with their IDs
        questions_and_answers.append((question, answers_with_models))

    return questions_and_answers


def rank_interface():
    questions = get_questions_and_answers()
    
    # Create three dropdowns for each question for 1st, 2nd, and 3rd choices
    inputs = []

    for question, answers in questions:
        # Use an HTML component to display the question
        inputs.append(gr.Markdown(rtl=True, value= question))
        
        answers_text = [answer for answer, _ in answers]

        # Append three dropdowns for rankings without repeating the question
        inputs.append(gr.Dropdown(elem_classes="rtl", choices=["...اختر"] + answers_text, label="الاختيار الأول"))
        inputs.append(gr.Dropdown(elem_classes="rtl", choices=["...اختر"] + answers_text, label="الاختيار الثاني"))
        inputs.append(gr.Dropdown(elem_classes="rtl", choices=["...اختر"] + answers_text, label="الاختيار الثالث"))

    outputs = gr.Textbox(elem_id="rtl_text")
 

    def rank_fluency(*dropdown_selections):
        user_rankings = []
        for i in range(0, len(dropdown_selections), 4):  # Process each set of 3 dropdowns for a question
            selections = dropdown_selections[i+1:i+4]
            # Check for duplicate selections within the same question
            unique_selections = set(tuple(selection) for selection in selections)

            # Now you can safely check if all sublists were unique
            if len(selections) != len(unique_selections):
                return "تأكد من عدم تكرار الإجابة لنفس السؤال"

            question_index = i // 4
            _, model_answers = questions[question_index]
            for j, chosen_answer in enumerate(selections, start=1):
                if chosen_answer == "...اختر":  # Skip unselected dropdowns
                    continue
                for model_answer, model in model_answers:
                    if model_answer == chosen_answer:
                        user_rankings.append((model, j))  # j is the rank (1, 2, or 3)
                        break
        process_rankings(user_rankings)
        return "سجلنا ردك، ما قصرت =)"

    return gr.Interface(fn=rank_fluency, inputs=inputs, outputs=outputs, title="ترتيب فصاحة النماذج",
                            description=".لديك مجموعة من الأسئلة، الرجاء ترتيب إجابات كل سؤال حسب جودة و فصاحة الإجابة", css=css)

iface = rank_interface()
iface.launch()
