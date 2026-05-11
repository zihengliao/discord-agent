import discord

# Read bot token
with open("discord_token.txt", "r") as file:
    TOKEN = file.read().strip()

# Read your Discord user ID
with open("discord_id.txt", "r") as file:
    OWNER_DISCORD_ID = int(file.read().strip())

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")

    owner = await client.fetch_user(OWNER_DISCORD_ID)
    await owner.send("Hey, I'm online. Send me a message.")


@client.event
async def on_message(message):
    # Stop the bot from replying to itself
    if message.author == client.user:
        return

    # Only respond to you
    if message.author.id != OWNER_DISCORD_ID:
        return

    user_message = message.content.strip()

    # Print your message in the terminal
    print(f"You said: {user_message}")

    # Optional shutdown command
    if user_message.lower() == "shutdown":
        await message.channel.send("Shutting down.")
        await client.close()
        return

    # Respond back in Discord
    await message.channel.send(f"I received your message: {user_message}")


client.run(TOKEN)