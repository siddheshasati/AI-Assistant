from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

# Load environment variables
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "AI Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey", "")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System prompt
System = f"""Hello, I am {Username}. You are an advanced AI chatbot named {Assistantname} with real-time information.
*** Provide professional answers with correct grammar, punctuation, and structure. ***"""

# Load chat history
try:
    with open(r"Data/ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data/ChatLog.json", "w") as f:
        dump([], f)

# Google search function
def GoogleSearch(query):
    results = list(search(query, num_results=5))  # Removed 'advanced=True'
    Answer = f"The search results for '{query}' are:\n[start]\n"
    for i, url in enumerate(results, 1):
        Answer += f"{i}. {url}\n"
    Answer += "[end]"
    return Answer

# Remove empty lines from response
def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

# Chatbot context
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Get real-time information
def Information():
    current_datetime = datetime.datetime.now()
    return f"""Real-time information:
Day: {current_datetime.strftime("%A")}
Date: {current_datetime.strftime("%d")}
Month: {current_datetime.strftime("%B")}
Year: {current_datetime.strftime("%Y")}
Time: {current_datetime.strftime("%H:%M:%S")}."""

# Main AI function
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages
    
    # Load chat history
    with open(r"Data/ChatLog.json", "r") as f:
        messages = load(f)
    
    messages.append({"role": "user", "content": prompt})
    
    # Append real-time search results
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})
    
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        max_tokens=2048,
        temperature=0.7,
        top_p=1,
        stream=False  # Set to False to get the full response at once
    )
    
    Answer = completion.choices[0].message.content.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    # Save chat history
    with open(r"Data/ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    return AnswerModifier(Answer)

# CLI mode
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
