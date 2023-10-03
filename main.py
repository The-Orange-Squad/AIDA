from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from discord.commands import Option
import discord.ui
from API_CALLER import chatWithCohere
import asyncio
import json
import time

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MODERATOR_ID = int(os.getenv("MODERATOR"))
banned_user_file = "data/banned_users.json"
user_settings_websearch_file = "data/usw.json"

bot = commands.Bot(command_prefix="!")

banned_users = {}

def loadBanData():
    if os.path.isfile(banned_user_file):
        with open(banned_user_file, "r") as f:
            global banned_users
            banned_users = json.load(f)

loadBanData()
def saveBanData():
    with open(banned_user_file, "w") as f:
        json.dump(banned_users, f)

websearch_settings = {}

def loadWebsearchSettings():
    if os.path.isfile(user_settings_websearch_file):
        with open(user_settings_websearch_file, "r") as f:
            global websearch_settings
            websearch_settings = json.load(f)
            temp = {}
            for user_id in websearch_settings.keys():
                temp[int(user_id)] = websearch_settings[user_id]
            websearch_settings = temp
            print("Loaded websearch settings.")

loadWebsearchSettings()

def saveWebsearchSettings():
    with open(user_settings_websearch_file, "w") as f:
        json.dump(websearch_settings, f)



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

user_cooldowns = {}

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if str(message.author.id) in banned_users:
        embed = discord.Embed(
            title="You are banned!",
            description=f"You are banned from using AIDA! Please contact the developer (`@lyubomirt`) for more information, or if you want to appeal.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url="https://i.ibb.co/471xQmT/ban-user.png")
        await message.reply(embed=embed)
        return
    # Check if the user is on cooldown
    if message.author.id in user_cooldowns:
        if time.time() - user_cooldowns[message.author.id] < 15:
            embed_cooldown = discord.Embed(
                title="You are on cooldown!",
                description=f"You can only use AIDA once every 15 seconds. Try again in `{round(15 - (time.time() - user_cooldowns[message.author.id]), 2)}` seconds.",
                color=discord.Color.red()
            )
            embed_cooldown.set_thumbnail(url="https://i.ibb.co/bbSB1Kz/timer.png")
            await message.reply(embed=embed_cooldown)
            return
    # Check if the message starts with a mention of the bot
    if bot.user.mentioned_in(message):
        user_cooldowns[message.author.id] = time.time()
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
    if str(ctx.author.id) in banned_users:
        embed = discord.Embed(
            title="You are banned!",
            description=f"You are banned from using AIDA! Please contact the developer (`@lyubomirt`) for more information, or if you want to appeal.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url="https://i.ibb.co/471xQmT/ban-user.png")
        await ctx.respond(embed=embed)
        return
    user_id = ctx.author.id
    if user_id in user_conversations:
        del user_conversations[user_id]
        await ctx.respond("Your conversation with AIDA has been cleared.")
    else:
        await ctx.respond("You don't have an active conversation with AIDA to clear.")


@bot.slash_command(name="persona", description="Change the personality of AIDA")
async def set_persona(ctx: discord.AutocompleteContext, personality: Option(str, autocomplete=personaAutocomplete)):
    if str(ctx.author.id) in banned_users:
        embed = discord.Embed(
            title="You are banned!",
            description=f"You are banned from using AIDA! Please contact the developer (`@lyubomirt`) for more information, or if you want to appeal.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url="https://i.ibb.co/471xQmT/ban-user.png")
        await ctx.respond(embed=embed)
        return
    user_personalities[ctx.author.id] = personality
    user_id = ctx.author.id
    if user_id in user_conversations:
        del user_conversations[user_id]
    await ctx.respond(f"AIDA's personality has been set to {personality}, and the chat history has been cleared.")


@bot.slash_command(name="ban", description="Ban a user from using AIDA", guild_ids=[1155207826822668339])
async def ban(ctx, user:discord.User):
    if ctx.author.id != MODERATOR_ID:
        await ctx.respond("You do not have permission to use this command.")
        return
    try:
        user_id = user.id
        if user is None:
            # Red ANSI code
            ansi_code = r"\033[0;91m"
            print(f"{ansi_code}{user_id} is not a valid user ID.")
            await ctx.respond(f"{user_id} is not a valid user ID.")
            return
        else:
            banned_users[str(user.id)] = True
            saveBanData()
            embed = discord.Embed(
                title=f"{user.name} has been banned from using AIDA!",
                description="Please use the `/unban` command to unban them, if needed.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)
            loadBanData()
    except:
        ansi_code = r"\033[0;91m"
        print(ansi_code + f"Something went wrong while trying to ban {user_id}.")
        await ctx.respond(f"Something went wrong while trying to ban {user_id}.")


@bot.slash_command(name="unban", description="Unban a user from using AIDA", guild_ids=[1155207826822668339])
async def unban(ctx, user:discord.User):
    if ctx.author.id != MODERATOR_ID:
        await ctx.respond("You do not have permission to use this command.")
        return
    try:
        user_id = user.id
        if user is None:
            # Red ANSI code
            ansi_code = r"\033[0;91m"
            print(f"{ansi_code}{user_id} is not a valid user ID.")
            await ctx.respond(f"{user_id} is not a valid user ID.")
            return
        else:
            if str(user_id) in banned_users.keys():
                del banned_users[str(user_id)]
                saveBanData()
                await ctx.respond(f"{user_id} has been unbanned from using AIDA.")
            else:
                await ctx.respond(f"{user_id} is not banned from using AIDA.")
    except:
        ansi_code = r"\033[0;91m"
        print(f"{ansi_code}Something went wrong while trying to unban {user_id}.")
        await ctx.respond(f"Something went wrong while trying to unban {user_id}.")


class FeedbackModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Feedback", style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):
        feedback = self.children[0].value
        user_id = MODERATOR_ID  # your user ID
        user = await bot.fetch_user(user_id)
        embedFeedback = discord.Embed(
            title="Feedback Received",
            description=f"```\n{feedback}\n```",
            color=discord.Color.yellow()
        )
        embedFeedback.set_author(name=user.name, icon_url=user.avatar)
        embedFeedback.set_footer(text="User ID: " + str(user_id) + " | Timestamp: " + str(time.strftime("%m/%d/%Y, %H:%M:%S")))
        embedFeedback.set_thumbnail(url=user.avatar)
        # Get the message history of the user and put it into a separate variable
        try:
            message_history = user_conversations[user_id]
        except:
            message_history = None
        # Put this into a .txt file, if a message history exists
        if message_history:
            with open(f"message_history_{user_id}.txt", "w") as f:
                for message in message_history:
                    f.write(message["user_name"] + ": " + message["message"] + "\n")
        
            # Send the feedback to the developer
            file = discord.File(f"message_history_{user_id}.txt")

        if message_history:
            await user.send(embed=embedFeedback, file=file)
        else:
            await user.send(embed=embedFeedback)
        if message_history:
            os.remove(f"message_history_{user_id}.txt")
        embed = discord.Embed(
            title="Thank you for your feedback!",
            description="Your feedback has been sent to the developer. We will get back to you as soon as possible!",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

@bot.slash_command(name="feedback", description="Send feedback to help us improve AIDA!")
async def feedback(ctx):
    """Shows an example of a modal dialog being invoked from a slash command."""
    modal = FeedbackModal(title="Send Feedback")
    await ctx.send_modal(modal)

class exportButton(discord.ui.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = discord.ButtonStyle.green
        self.label = "Export Conversation"  
        self.emoji = discord.PartialEmoji(name="📥") 
    async def callback(self, interaction):
        # Export the conversation
        user_id = interaction.user.id
        # Using the same method as with the modal
        try:
            message_history = user_conversations[user_id]
        except:
            message_history = None
        # Put this into a .txt file, if a message history exists
        if message_history:
            with open(f"message_history_{user_id}.txt", "w") as f:
                for message in message_history:
                    f.write(message["user_name"] + ": " + message["message"] + "\n==================\n")
        
            # Send the feedback to the developer
            file = discord.File(f"message_history_{user_id}.txt")
            await interaction.response.send_message("Here is your conversation!", file=file)
            os.remove(f"message_history_{user_id}.txt")
        else:
            embed = discord.Embed(
                title="No conversation to export!",
                description="You don't have an active conversation with AIDA to export.",
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=embed)

class exportConvView(discord.ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add a button to export the conversation
        self.add_item(exportButton())


@bot.slash_command(name="conversation", description="Check your active conversation with AIDA.")
async def conversation(ctx):
    if ctx.author.id not in user_conversations:
        embed = discord.Embed(
            title="Error",
            description="You don't have an active conversation with AIDA.",
            color = discord.Color.red()
        )
        await ctx.respond(embed=embed)
        return
    embed=discord.Embed(
        title="Your active conversation with AIDA:",
        color=discord.Color.green(),
        description="\n\n"
    )
    for message in user_conversations[ctx.user.id]:
        embed.description += "**" + message["user_name"] + "**: " + message["message"] + "\n"
    
    if ctx.author.id not in user_personalities:
        user_personalities[ctx.author.id] = "Default"
    embed.set_footer(text="Total messages: " + str(len(user_conversations[ctx.user.id]))  + " | Tone: " + user_personalities[ctx.user.id], icon_url=ctx.author.avatar)
    
    await ctx.respond(embed=embed, view=exportConvView())
    

@bot.slash_command(name="help", description="Get help with using AIDA")
async def help(ctx):
    embed = discord.Embed(
        title="Help",
        description="Here are the commands you can use with AIDA:",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=bot.user.avatar)
    # Add the commands. Split with categories with pages
    embed.add_field(name="Conversation", value="`/conversation` - Check your active conversation with AIDA.\n`/clear` - Clear your conversation with AIDA.\n`/persona` - Change the personality of AIDA.", inline=False)
    embed.add_field(name="Feedback", value="`/feedback` - Send feedback to help us improve AIDA.", inline=False)
    embed.add_field(name="Moderation", value="`/ban` - Ban a user from using AIDA.\n`/unban` - Unban a user from using AIDA.", inline=False)
    embed.add_field(name="Settings", value="`/settings` - Change your settings for AIDA.", inline=False)
    await ctx.respond(embed=embed)

class WebSearchToggleButton(discord.ui.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = discord.ButtonStyle.blurple
        self.label = "Toggle"  
        self.emoji = discord.PartialEmoji(name="🔎") 
    async def callback(self, interaction):
        if interaction.user.id not in websearch_settings:
            websearch_settings[interaction.user.id] = False
        websearch_settings[interaction.user.id] = not websearch_settings[interaction.user.id]
        saveWebsearchSettings()
        if websearch_settings[interaction.user.id]:
            embed = discord.Embed(
                title="Web Search Enabled",
                description="You will now receive web search results from AIDA.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="Web Search Disabled",
                description="You will no longer receive web search results from AIDA.",
                color=discord.Color.red()
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)
class WebSearchToggleView(discord.ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add a button to toggle websearch
        self.add_item(WebSearchToggleButton())
@bot.slash_command(name="settings", description="Change your settings for AIDA")
async def settings(ctx, part: Option(str, choices=["websearch"])):
    if part == "websearch":
        if ctx.author.id not in websearch_settings:
            websearch_settings[ctx.author.id] = False
        if websearch_settings[ctx.author.id]:
            embed = discord.Embed(
                title="Web Search Enabled",
                description="You will receive web search results from AIDA.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="Web Search Disabled",
                description="You will not receive web search results from AIDA.",
                color=discord.Color.red()
            )
        await ctx.respond("Here are your web search settings:", embed=embed, view=WebSearchToggleView(), ephemeral=True)



bot.run(DISCORD_TOKEN)
