import requests
import uuid
import sys
import json 

def get_available_models(base_url, headers):
    models_url = f"{base_url}/api/models"
    try:
        response = requests.get(models_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching available models: {e}")
        return None

def select_model(available_models):
    print("Available models:")
    for i, model in enumerate(available_models['data'], 1):
        print(f"{i}. {model['id']}")
    
    choice = input("Select a model (number): ")
    return available_models['data'][int(choice)-1]['id']

def get_full_response(base_url, headers, model, messages):
    chat_payload = {
        "model": model,
        "messages": messages,
        "session_id": str(uuid.uuid4()),
        "chat_id": "",
        "id": str(uuid.uuid4())
    }

    try:
        # Send the request and get the entire response at once
        response = requests.post(f"{base_url}/api/chat/completions", json=chat_payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()

        # Extract the assistant's response from the 'choices' key
        if 'choices' in response_data and response_data['choices']:
            return response_data['choices'][0].get('message', {}).get('content', '')
        else:
            return "No valid response from AI."
    except requests.RequestException as e:
        print(f"Error: {e}")
        return None

def interactive_chat(base_url, headers, model):
    print(f"Starting interactive chat with model: {model}")
    print("Type 'exit' to end the conversation.")
    
    session_id = str(uuid.uuid4())
    messages = []

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        messages.append({"role": "user", "content": user_input})
        
        print("AI: ", end='', flush=True)
        ai_response = get_full_response(base_url, headers, model, messages)
        
        if ai_response:
            print(ai_response)
            messages.append({"role": "assistant", "content": ai_response})

def main():
    # Step 1: Authenticate and get the token
    base_url = "http://ip.address:8080"
    auth_url = f"{base_url}/api/v1/auths/signin"
    auth_payload = {
        "email": "openwebui@example.com",
        "password": "password"
    }
    try:
        auth_response = requests.post(auth_url, json=auth_payload)
        auth_response.raise_for_status()
        token = auth_response.json().get("token")
        if not token:
            raise ValueError("Token not found in response")
        print("Authentication successful")
    except requests.RequestException as e:
        print(f"Authentication request failed: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Authentication failed: {e}")
        sys.exit(1)

    # Define headers after getting the token
    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Step 2: Fetch available models
    available_models = get_available_models(base_url, headers)
    if not available_models:
        print("Unable to fetch available models. Exiting.")
        sys.exit(1)

    # Step 3: Select model
    model_name = select_model(available_models)

    # Step 4: Start interactive chat
    interactive_chat(base_url, headers, model_name)

if __name__ == "__main__":
    main()
