import discord
import os
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from delegation import Delegator
from agents.intent_agent import IntentAgent
import asyncio
from memory import get_operational_memory, write_bot_response, write_user_message
from context_flow import get_context_types, load_context
import time
import random
from pprint import pprint
from datetime import timedelta


load_dotenv()
DISCORD_BOT_TOKEN = str(os.getenv("DISCORD_BOT_TOKEN"))
OWNER_DISCORD_ID = int(os.getenv("OWNER_DISCORD_ID"))
GEMINI_API_KEY = str(os.getenv("GEMINI_API_KEY"))


# setting clients up
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
active_poll_message = None

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
# MODEL = "gemini-3.1-flash-lite-preview"
MODEL = "gemma-4-31b-it"
# MODEL = "qwen3.5:4b"

get_random_value = lambda: random.randint(1, 3)

# chuck this shit through to the intent agent
# based on intent chuck it to the new appropriate agent
# respond back with the appropriate agent
intent_agent = IntentAgent(gemini_client, MODEL)
delegator = Delegator(gemini_client, MODEL)
def respond(user_message: str) -> str:
    write_user_message(user_message)
    operational_state = get_operational_memory()

    max_retries=5
    for attempt in range(max_retries):
        try:
            router_started = time.perf_counter()
            intent = intent_agent.respond(user_message, operational_state=operational_state)
            router_elapsed_ms = (time.perf_counter() - router_started) * 1000
            router_prompt_chars = len(user_message) + len(intent_agent.prompt_intent)
            print(
                f"router metrics: prompt_chars~{router_prompt_chars}, "
                f"latency_ms={router_elapsed_ms:.1f}"
            )
            # rate limiting
            time.sleep(2)
            break
        except errors.ServerError as e:
            # Gemini 503 high demand / unavailable
            if server_error_handling(attempt, max_retries):
                return f"Gemini servers are cooked. Write your message again"
            # rate limiting
            time.sleep(get_random_value())
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {e}")

    for attempt in range(max_retries):
        try:
            context_types = get_context_types(intent, user_message)
            context = load_context(context_types)
            agent = delegator.delegate(intent, context)
            response = agent.respond(user_message, context)
            break
        except errors.ServerError as e:
            # Gemini 503 high demand / unavailable
            if server_error_handling(attempt, max_retries):
                return f"Gemini servers are cooked. Write your message again"
            # rate limiting
            time.sleep(get_random_value())
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {e}")

    # BUG this could be a problem if response is a poll type
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
    print(f"Logged in as {client.user}")


@client.event
async def on_raw_poll_vote_add(payload):
    if active_poll_message is None:
        return

    if payload.message_id != active_poll_message.id:
        return

    refreshed_message = await active_poll_message.fetch()
    answer = refreshed_message.poll.get_answer(payload.answer_id)

    print(f"User {payload.user_id} selected: {answer.text}")
    await print_poll_results()


@client.event
async def on_raw_poll_vote_remove(payload):
    if active_poll_message is None:
        return

    if payload.message_id != active_poll_message.id:
        return

    refreshed_message = await active_poll_message.fetch()
    answer = refreshed_message.poll.get_answer(payload.answer_id)

    print(f"User {payload.user_id} removed their vote from: {answer.text}")
    

async def print_poll_results():
    refreshed_message = await active_poll_message.fetch()

    for answer in refreshed_message.poll.answers:
        async for voter in answer.voters():
            print(f"{voter} selected: {answer.text}")


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

    # response can be a string or a poll
    response = await asyncio.to_thread(respond, user_message)

    global active_poll_message
    
    # don't know a better way to do this
    if isinstance(response, discord.Poll):
      active_poll_message = await message.channel.send(poll=response)
    else:
        await message.channel.send(f"{response}")

client.run(DISCORD_BOT_TOKEN)
