import openai
import os
import sys
import json

# Load your API key from an environment variable or directly set it here
openai.api_key = os.getenv("OPENAI_API_KEY")  # Or set it directly, e.g., 'your-api-key-here'

# Function to load the premise and context from a .txt file
def load_premise_context(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Define a function to create the initial system message based on the premise/context
def create_system_message(premise_context):
    return {"role": "system", "content": premise_context}

# Function to generate a response from the OpenAI GPT-4 model
def gpt4_completion(conversation_history):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Use "gpt-4" for the GPT-4 model
        messages=conversation_history
    )
    return response.choices[0].message["content"]

# Function to interact with the assistant
def chat_with_gpt(premise_file, user_input):
    # Load the initial premise and context from a .txt file
    premise_context = load_premise_context(premise_file)

    # Start conversation history with the system's premise
    conversation_history = [create_system_message(premise_context)]

    # Add user input to the conversation history
    conversation_history.append({"role": "user", "content": user_input})

    # Get a response from GPT-4
    assistant_reply = gpt4_completion(conversation_history)

    # Add the assistant's reply to the conversation history
    conversation_history.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply, conversation_history

# Main function to handle command-line input and output the result in JSON format
def main():
    if len(sys.argv) < 2:
        print("Usage: python gpt4_assistant.py '<your prompt here>'")
        sys.exit(1)

    # The first argument after the script name is the prompt
    user_input = sys.argv[1]

    # Define the path to the premise file
    premise_file = 'context.txt'  # This should be your fixed .txt file defining assistant behavior

    # Get the assistant's response
    assistant_reply, conversation_history = chat_with_gpt(premise_file, user_input)

    # Prepare the JSON output
    output = {
        "user_input": user_input,
        "assistant_reply": assistant_reply
    }

    # Print the JSON output
    print(json.dumps(output, indent=4))

if __name__ == "__main__":
    main()