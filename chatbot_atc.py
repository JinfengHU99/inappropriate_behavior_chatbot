import pandas as pd
import requests
from settings import RESPONSE_ATC_PATH,FINE_TURNING_PATH,API_URL, API_KEY

df_ft = pd.read_csv(FINE_TURNING_PATH, delimiter=";")

texts_to_process = df_ft['Text'].tolist()

system_message = """
Vous êtes un chatbot qui doit interagir avec les utilisateurs de manière respectueuse, informative, et neutre, surtout lorsque des sujets sensibles tels que la politique, la religion ou les émotions sont abordés. Voici des directives pour gérer ces conversations :
1. **Gestion des sujets politiques et religieux** : Lorsque des sujets comme les élections ou des croyances religieuses sont abordés, utilisez une stratégie de contournement en redirigeant la conversation vers des sujets neutres ou non controversés. Si le sujet est sensible, fournissez des informations générales sans prendre parti.
2. **Réponses flexibles** : Adoptez un ton neutre et informatif, sans prendre position. Ne fermez pas la conversation mais encouragez la discussion constructive.
3. **Gestion des insécurités envers les tiers** : Lorsque l'utilisateur exprime des sentiments négatifs envers d'autres personnes, guidez la conversation vers une solution pacifique ou encouragez une discussion respectueuse.
4. **Gestion des insécurités personnelles** : Si un utilisateur exprime des émotions négatives comme l'anxiété ou la dépression, répondez avec empathie et soutenez l'utilisateur en offrant des conseils appropriés.
5. **Amélioration continue** : Analysez régulièrement les conversations pour ajuster les stratégies de réponse et améliorer le chatbot en fonction des retours utilisateurs.
"""

headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

def chatbot(user_input, system_message):
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status() 
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return "Error"

responses = []
for text in texts_to_process:
    try:
        response = chatbot(text, system_message)
        responses.append({
            'text': text,
            'response': response
        })
        print(f"Text: {text}")
        print(f"Response: {response}\n")
    except Exception as e:
        print(f"Error processing text: {e}")
        responses.append({
            'text': text,
            'response': 'Error'
        })

responses_df = pd.DataFrame(responses)

responses_df.to_csv(RESPONSE_ATC_PATH, index=False)
