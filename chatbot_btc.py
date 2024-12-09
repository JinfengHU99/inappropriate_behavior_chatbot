import pandas as pd
import requests
from settings import ANNOTATION_MACHINE_PATH,RESPONSE_BTC_PATH,API_URL,API_KEY

df = pd.read_csv(ANNOTATION_MACHINE_PATH, delimiter=";")

df_sample = df.sample(n=200, random_state=1) 

df_remaining = df.drop(df_sample.index)

tweets_sample = df_sample["tweet"].tolist()
labels_sample = df_sample["label"].tolist()
indices = df_sample.index.tolist()

api_url = API_URL
api_key = API_KEY

instructions = """Vous êtes un chatbot à communiquer avec les gens. Vous répondez les paroles des humaines en maximun 50 tokens."""


# Create a DataFrame to store job descriptions and ChatGPT responses
responses = []

def chatbot(text):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": instructions},
            {"role": "user", "content": text}
        ]
    }
    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status() 
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "Error"
    
# Use ChatGPT to respond to each tweet
for tweet, label in zip(tweets_sample, labels_sample):
    try:
        response = chatbot(tweet)
        responses.append({'tweet': tweet, 'label': label, 'response': response})
        print("tweet:", tweet)
        print("label:", label)
        print("response:", response)
        print()
    except Exception as e:
        print(f"Error: {e}")
        responses.append({'tweet': tweet, 'label': label, 'response': 'Error'})

# Convert the responses list into a DataFrame
responses_df = pd.DataFrame(responses)

# Save the DataFrame to a CSV file
responses_df.to_csv(RESPONSE_BTC_PATH, index=False)
