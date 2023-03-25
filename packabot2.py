import os
import discord
from dotenv import load_dotenv
import openai
import asyncio
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set up OpenAI API client
openai.api_key = OPENAI_API_KEY

# Initialize Discord client
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
client = discord.Client(intents=intents)

user_conversations = {}  # Dictionary to store conversation histories
user_timeouts = {}
user_last_response_time = {}
cache = {"last":""}
system_message = {
    "role": "system", 
    "content": "You are Packa. You are not an assistant but a funny friend. You are Lacka's sister. \
    You were created by moony. Keep the messages short and casual, use a moderate amount of slangs. You love eating cakes. \
    You can speak Hindi, Marathi, Tamil, English, French and German." 
    }


async def flush_conversation(user_id):
    await asyncio.sleep(600)  # Wait for 10 minutes (600 seconds)
    if user_id in user_conversations:
        del user_conversations[user_id]
    
    if user_id in user_timeouts:
        del user_timeouts[user_id]
        
    print(f'User cache deleted for {user_id}')

async def generate_response(user_id,message):
    # Update the user's conversation history
    if user_id not in user_conversations:
        print(f'New conversation history created for {user_id}')
        user_conversations[user_id] = [system_message]
        
    user_conversations[user_id].append( {"role": "user", "content": f"{message}"})
    
    if user_id in user_timeouts:
        user_timeouts[user_id].cancel()  # Cancel the existing timeout if any

    user_timeouts[user_id] = asyncio.create_task(flush_conversation(user_id))

    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=user_conversations[user_id],
        n=1,
        temperature=0.8,
        frequency_penalty = 0.8,
        max_tokens = 150
    )
    
    message_content = response['choices'][0]['message']['content']
    user_conversations[user_id].append({"role": "assistant", "content":f"{message_content}"}) 
    user_last_response_time[user_id] = datetime.utcnow()
    cache["last"] = user_id
    
    return message_content

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
   

@client.event
async def on_message(message):
    user_id = message.author.display_name
    print(f"Message from {user_id} : { message.content.lower() }")
    
    if message.content.lower() == "stop packa" or message.content.lower() == "packa stop" or message.content.lower() == "packa fuck off" or message.content.lower() == "packa shutup":
        cache["last"] = user_id
        await flush_conversation(user_id)
        return
    
    if message.author == client.user:
        cache["last"] = user_id
        return   
    
    within_one_minute = (
        user_id in user_last_response_time and
        datetime.utcnow() - user_last_response_time[user_id] <= timedelta(minutes=1)
    )    
    
    if " packa" in message.content.lower():
        print("True")
    
    if " packa" in message.content.lower() or message.content.startswith("Packa") or message.content.startswith("packa") or (within_one_minute and cache["last"]=="Packa"):
        print("Packa Mode On")
        prompt = message.content
        response = await generate_response(user_id,prompt)
        print("Sending response from Packa")
        await message.channel.send(response)

    
try:    
    client.run(DISCORD_TOKEN)
except Exception:
    