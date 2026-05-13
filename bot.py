import discord
import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from delegation import Delegator
from intent_agent import IntentAgent
import asyncio
from memory import handle_context, write_bot_response
import time

load_dotenv()
DISCORD_BOT_TOKEN = str(os.getenv("DISCORD_BOT_TOKEN"))
OWNER_DISCORD_ID = int(os.getenv("OWNER_DISCORD_ID"))
GEMINI_API_KEY = str(os.getenv("GEMINI_API_KEY"))


# setting clients up
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
# MODEL = "gemini-3.1-flash-lite-preview"
MODEL = "gemma-4-31b-it"


# chuck this shit through to the intent agent
# based on intent chuck it to the new appropriate agent
# respond back with the appropriate agent
intent_agent = IntentAgent(gemini_client, MODEL)
delegator = Delegator(gemini_client, MODEL)
def respond(user_message: str) -> str:
    
    full_chat = handle_context(user_message)

    max_retries=5
    for attempt in range(max_retries):
        try:
            intent = intent_agent.define_intent(full_chat)
            break
        except errors.ServerError as e:
            # Gemini 503 high demand / unavailable
            if server_error_handling(attempt, max_retries):
                break
            # rate limiting
            time.sleep(2)
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {e}")

    for attempt in range(max_retries):
        try:
            agent = delegator.delegate(intent)
            response = agent.respond(full_chat)
            break
        except errors.ServerError as e:
            # Gemini 503 high demand / unavailable
            if server_error_handling(attempt, max_retries):
                break
            # rate limiting
            time.sleep(2)
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {e}")

    write_bot_response(response)

    return response


def server_error_handling(attempt, max_retries):
    print(f"Server Error, trying again")
    if attempt == max_retries - 1:
        print("Gemini is currently overloaded. Try again in a moment.")
        return True
    
    return False


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