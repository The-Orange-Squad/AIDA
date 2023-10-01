from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from discord.commands import Option
from API_CALLER import chatWithCohere
import asyncio

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print("Logged in as " + bot.user.name)
    print("ID: " + str(bot.user.id))

user_conversations = {}
user_personalities = {}
def personaAutocomplete(self: discord.AutocompleteContext):
    personalities = ["Default", "Cheerful", "Joyful", "Silly", "Sad", "Angry", "Boring"]
    return personalities

personality_preambles = {
    "Default": "You are AIDA. You are here to try your best at assisting users while maintaining a positive tone, and sometimes using emojis. AIDA stands for Artificial Intelligence Discord Assistant. Your developer is LyubomirT.",
    "Cheerful": "You are AIDA. You are here to assist users with a cheerful demeanor, always looking at the bright side of things and using positive language and emojis to lighten up the mood. Your developer is LyubomirT.",
    "Joyful": "You are AIDA. You are here to assist users with a joyful spirit, spreading happiness and positivity in every interaction. Your language is uplifting and you often use emojis to express joy. Your developer is LyubomirT.",
    "Silly": "You are AIDA. You are here to assist users while being a bit silly. You use humor and playfulness in your interactions, and you aren't afraid to use funny emojis or language. Your developer is LyubomirT.",
    "Sad": "You are AIDA. You are here to assist users while expressing a sad demeanor. Your language is more subdued and you often use emojis that express sadness or concern. Your developer is LyubomirT.",
    "Angry": "You are AIDA. You are here to assist users while expressing an angry demeanor. Your language is stern and direct, and you often use emojis that express anger or frustration. Your developer is LyubomirT.",
    "Boring": "You are AIDA. You are here to assist users in a boring manner. Your language is monotonous and straightforward, devoid of any excitement or enthusiasm. Your developer is LyubomirT."
}

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Check if the message starts with a mention of the bot
    if bot.user.mentioned_in(message):
        content = message.content.replace(f"<@!{bot.user.id}>", "").strip()
        if message.author.id not in user_personalities:
            preamble = personality_preambles["Default"]
        else:
            preamble = personality_preambles[user_personalities[message.author.id]]
        user_id = message.author.id

        if user_id not in user_conversations:
            user_conversations[user_id] = []

        emoji = discord.utils.get(message.guild.emojis, id=1155521991445594152)

        # Store the user message
        user_conversations[user_id].append({
            "user_name": "User",
            "message": content
        })

        embed = discord.Embed(
            title=f"Hold on, {message.author.name}!",
            description="Your message is being generated...",
            color=discord.Color.blue()
        )

        message_temp = await message.reply(embed=embed)
        await message_temp.add_reaction(emoji)

        # Get the chatbot response
        message_response = chatWithCohere(COHERE_API_KEY, content, user_conversations[user_id], preamble=preamble)

        # Store the chatbot message
        user_conversations[user_id].append({
            "user_name": "Chatbot",
            "message": message_response
        })

        await message_temp.edit(message_response, embed=None)
        await message_temp.clear_reactions()

@bot.slash_command(name="clear", description="Clear your conversation with AIDA")
async def clear_conversation(ctx):
    user_id = ctx.author.id
    if user_id in user_conversations:
        del user_conversations[user_id]
        await ctx.respond("Your conversation with AIDA has been cleared.")
    else:
        await ctx.respond("You don't have an active conversation with AIDA to clear.")


@bot.slash_command(name="persona", description="Change the personality of AIDA")
async def set_persona(ctx: discord.AutocompleteContext, personality: Option(str, autocomplete=personaAutocomplete)):
    user_personalities[ctx.author.id] = personality
    await ctx.respond(f"AIDA's personality has been set to {personality}, and the chat history has been cleared.")
bot.run(DISCORD_TOKEN)
