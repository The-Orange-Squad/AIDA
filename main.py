from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from API_CALLER import chatWithCohere

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name)
    print("ID: " + str(bot.user.id))

user_conversations = {}

@bot.slash_command(name="chat", description="Have a conversation with Cohere's Coral!")
async def chat(ctx, message: Option(str, description="Type Your Message Here")):
    user_id = ctx.author.id
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    emoji = discord.utils.get(ctx.guild.emojis, id=1155521991445594152)
    
    # Store the user message
    user_conversations[user_id].append({
        "user_name": "User",
        "message": message
    })

    embed = discord.Embed(
        title=f"Hold on, {ctx.author.name}!",
        description="Your message is being generated...",
        color=discord.Color.blue()
    )
    messageTemp = await ctx.respond(ctx.author.mention, embed=embed, delete_after=0)
    messageTemp = await ctx.channel.send(ctx.author.mention, embed=embed)
    await messageTemp.add_reaction(emoji)

    
    # Get the chatbot response
    messageResponse = chatWithCohere(COHERE_API_KEY, message, user_conversations[user_id])

    print(user_conversations[user_id])    
    # Store the chatbot message
    user_conversations[user_id].append({
        "user_name": "Chatbot",
        "message": messageResponse
    })

    embedResponse = discord.Embed(
        title="Coral says...",
        description=messageResponse,
        color=discord.Color.random()
    )

    await messageTemp.edit(embed=embedResponse)
    await messageTemp.clear_reactions()
bot.run(DISCORD_TOKEN)
