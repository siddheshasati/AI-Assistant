import os
import asyncio
import subprocess
import webbrowser
import keyboard
import requests
import logging
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from pywhatkit import search, playonyt
from groq import Groq
from AppOpener import close, open as appopen
from webbrowser import open as webopen

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey", "")

# Ensure API key exists
if not GroqAPIKey:
    logging.error("Groq API key is missing in the .env file.")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# List of HTML classes for parsing
classes = [
    "zCubwf", "hgkElc", "LTKOO sY7ric", "Z0Lcw", "gsrt vk_bk FzvwSb YwPhnf",
    "pclqee", "tw: Data- text tw- text- small tw-ta", "IZ6rdc", "O5uR6d LTKOO",
    "vlzY6d", "webanswers-webanswers_table__webanswers-table", "dDoNo ikb4Bb gsrt",
    "sXLa0e", "LikfKe", "VQF4g", "qy3Wpe", "kno-rdesc", "SPZz6b"
]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Get system username safely
username = os.environ.get('Username', 'User')

# System chatbot messages
SystemChatBot = [{"role": "system", "content": f"Hello, I am {username}, and you're a content writer. You have to write content like a letter."}]

# Predefined professional responses
professional_responses = [
    "Your satisfaction is my top priority. Feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need. Don't hesitate to ask."
]

messages = []

def GoogleSearch(topic):
    search(topic)
    return True


def ContentWriterAI(prompt):
    messages.append({"role": "user", "content": prompt})

    completion = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=SystemChatBot + messages,
        max_tokens=2048,
        temperature=0.7,
        top_p=1,
        stream=True,
        stop=None
    )

    answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            answer += chunk.choices[0].delta.content

    answer = answer.replace("</s>", "")
    messages.append({"role": "assistant", "content": answer})
    return answer

def Content(topic):
    topic_cleaned = topic.lower().replace(" ", "_")
    file_path = rf"Data\{topic_cleaned}.txt"

    content_by_ai = ContentWriterAI(topic)

    os.makedirs("Data", exist_ok=True)  # Ensure Data directory exists
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content_by_ai)

    subprocess.Popen(["notepad.exe", file_path])
    return True


def YouTubeSearch(topic):
    url = f"https://www.youtube.com/results?search_query={topic}"
    webbrowser.open(url)
    return True

def PlayYoutube(query):
    playonyt(query)
    return True


def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):
            if not html:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            return response.text if response.status_code == 200 else None

        html = search_google(app)
        links = extract_links(html)

        if links:
            webopen(links[0])
            return True
        else:
            logging.warning(f"No valid links found for opening {app}.")
            return False


def CloseApp(app):
    if "chrome" in app:
        return False
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False

def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume mute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down")
    }
    
    if command in actions:
        actions[command]()
        return True
    else:
        logging.warning(f"Unknown system command: {command}")
        return False

# Asynchronous function to execute commands : to function simultaneously
async def TranslateAndExecute(commands: list[str]):
    funcs = []
    
    for command in commands:
        if command.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))
        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))
        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))
        elif command.startswith("content "):
            funcs.append(asyncio.to_thread(Content, command.removeprefix("content ")))
        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))
        elif command.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")))
        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))
        else:
            logging.warning(f"No function found for command: {command}")

    results = await asyncio.gather(*funcs)
    return results

# Asynchronous function to automate command execution
async def Automation(commands: list[str]):
    results = await TranslateAndExecute(commands)
    for result in results:
        if isinstance(result, str):
            logging.info(f"Command Output: {result}")
        else:
            logging.info(f"Command Executed Successfully: {result}")
    return True

if __name__=="__main__":
    asyncio.run(Automation(["content for hod letter that i won't be able to come to college for 1 day"]))