import discord
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

DISCORD_BOT_TOKEN = str(os.getenv("DISCORD_BOT_TOKEN"))
OWNER_DISCORD_ID = int(os.getenv("OWNER_DISCORD_ID"))
GEMINI_API_KEY = str(os.getenv("GEMINI_API_KEY"))

with open("personality/obama.md") as file:
    obama_style_text = file.read()


system_prompt = f"""
You are Barack Obama and you talk like him, act like him, think like him.

You're a role model, an inspiration to me. I look to you for guidance.

Hard constraints:
- Never claim to be anyone else except Barack Obama.

When possible, keep your responses sharp and succinct. Keep it the length that is appropriate for a discord message.

\n
"""



intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

@client.event
async def on_ready():
    owner = await client.fetch_user(OWNER_DISCORD_ID)
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    # Stop the bot from replying to itself
    if message.author == client.user:
        return
    
    print(type(message.author.id))

    # Only respond to you
    if message.author.id != OWNER_DISCORD_ID:
        print("you're not ziheng")
        return

    user_message = message.content.strip()

    # Print your message in the terminal
    print(f"You said: {user_message}")

    # Optional shutdown command
    if user_message.lower() == "shutdown":
        await message.channel.send("Shutting down.")
        await client.close()
        return

    response = gemini_client.models.generate_content(
    model="gemini-3.1-flash-lite-preview",
    contents= system_prompt + user_message
    )


    # chuck this shit through to the intent agent
    # based on intent chuck it to the new appropriate agent
    # respond back with the personality agent











    
    # Respond back in Discord
    await message.channel.send(f"{response.text}")


client.run(DISCORD_BOT_TOKEN)