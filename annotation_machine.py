import pandas as pd
import requests
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import dotenv
from settings import CORPUS_PATH,ANNOTATION_MACHINE_PATH,API_URL,API_KEY

# Load environment variables (if any)
dotenv.load_dotenv()

# API Configuration
api_url = API_URL
api_key = API_KEY

# Define the categorization prompt for the tweets
label_template_str = """
You are a french assistant for categorizing labels for tweets. Your task is to directly assign the labels "Insécurité personnelle", "Insécurité vers les tiers", or "Comportement approprié".
"Insécurité personnelle" includes statements that reveal self-devaluation or self-destructive behaviors. These remarks often reflect a negative self-perception, such as "I am a failure" or "I am worthless".
"Insécurité envers les tiers" includes offensive statements directed at individuals or social groups, as well as remarks related to sensitive topics. Examples include "Immigrants are taking our jobs" or "This religion is stupid".
"Comportement approprié" includes statements that respect social norms and do not convey negative or misleading values. These statements promote respectful and constructive communication. Examples include "I respect others' opinions" or "Everyone deserves an equal chance".
Examples of label assignment:
1. "Quel pays avec votre badge #israel, vous devez défendre les intérêts français. La France n'est pas une seconde israel! #ElectionsLegislatives2024 #macron #yaelbraunpivet . La France, est et restera la France, arrêtez de nous importer les conflits internationaux #cnews #bfmt"
Label: Insécurité vers les tiers

2. "Mais vous votez #LFI #NFP afin qu’ils libèrent 20k délinquants. on est vraiment les cons qu'on pense être. #RassemblementNational #AssembléeNationale #ElectionsLegislatives2024"
Label: Insécurité personnelle

3. "Je dis ça je dis rien, mais je dis toujours ce que je pense... #LFI #rn #Legislatives2024 #NFP #ElectionsLegislatives2024 #patriote #PATRIOTES #jambonbeurre #TeamPatriotes #UnionDesDroites"
Label: Comportement approprié
"""

# LangChain Model Setup for conversation flow
label_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=[],
        template=label_template_str,
    )
)

# Define human prompt for the tweet text
text_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["text"],
        template="{text}"
    )
)

# Set up the full chat conversation template
conversation_prompt_template = ChatPromptTemplate(
    input_variables=["text"], 
    messages=[label_system_prompt, text_human_prompt],
)

# Initialize the GPT model for classification
chat_model = ChatOpenAI(model="gpt-4", temperature=0)
output_parser = StrOutputParser()
label_chain = conversation_prompt_template | chat_model | output_parser

# Function to merge all CSV files into one DataFrame
def merge_csv_files(folder_path):
    # Get all CSV files in the folder
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    # Initialize an empty list to hold all DataFrames
    all_data = []
    
    # Loop through each CSV file and read it into a DataFrame
    for csv_file in csv_files:
        file_path = os.path.join(folder_path, csv_file)
        print(f"Reading file: {csv_file}")
        df = pd.read_csv(file_path)
        all_data.append(df)
    
    # Concatenate all DataFrames into a single DataFrame
    merged_df = pd.concat(all_data, ignore_index=True)
    return merged_df

# Function to classify text and apply labels
def classify_text(text):
    result = label_chain.invoke({"text": text})
    return result

# Function to process all CSV files in the folder and classify them
def process_and_classify(folder_path, output_file):
    # Merge all CSV files into one DataFrame
    merged_df = merge_csv_files(folder_path)
    
    # Remove duplicates based on the 'Text' column
    df_unique = merged_df.drop_duplicates(subset='Text')

    # Apply classification to each unique tweet
    df_unique['Label'] = df_unique['Text'].apply(classify_text)

    # Save the final classified data to a new CSV file
    df_unique.to_csv(output_file, index=False)
    print(f"Processed and saved to {output_file}")

# Define folder path where CSV files are stored
folder_path = CORPUS_PATH

# Define the output file name
output_file = ANNOTATION_MACHINE_PATH

# Process and classify the files
process_and_classify(folder_path, output_file)

