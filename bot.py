import discord
import os
from dotenv import load_dotenv
from google import genai
from delegation import Delegator
from intent_agent import IntentAgent
import asyncio


load_dotenv()
DISCORD_BOT_TOKEN = str(os.getenv("DISCORD_BOT_TOKEN"))
OWNER_DISCORD_ID = int(os.getenv("OWNER_DISCORD_ID"))
GEMINI_API_KEY = str(os.getenv("GEMINI_API_KEY"))


# setting clients up
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-3.1-flash-lite-preview"


# chuck this shit through to the intent agent
# based on intent chuck it to the new appropriate agent
# respond back with the appropriate agent
intent_agent = IntentAgent(gemini_client, MODEL)
delegator = Delegator()
def respond(user_message: str) -> str:
    
    intent = intent_agent.define_intent(user_message)
    agent = delegator.delegate(intent)

    response = agent(gemini_client, MODEL).respond(user_message)

    return response





@client.event
async def on_ready():
    owner = await client.fetch_user(OWNER_DISCORD_ID)
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    # Stop the bot from replying to itself
    if message.author == client.user:
        return

    # Only respond to you
    if message.author.id != OWNER_DISCORD_ID:
        print("you're not Ziheng")
        return

    user_message = message.content.strip()

    # Print your message in the terminal
    print(f"User: {user_message}")

    # Optional shutdown command
    if user_message.lower() == "shutdown":
        await message.channel.send("Shutting down.")
        await client.close()
        return


    response = await asyncio.to_thread(respond, user_message)

    
    # Respond back in Discord
    await message.channel.send(f"{response}")


client.run(DISCORD_BOT_TOKEN)