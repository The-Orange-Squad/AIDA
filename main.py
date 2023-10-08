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
from chatbot_manager import AIDA_Modification, load
from image_gen.stable_diff_21 import prototype1_imagegen
import shutil

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MODERATOR_ID = int(os.getenv("MODERATOR"))
banned_user_file = "data/banned_users.json"
user_settings_websearch_file = "data/usw.json"
user_passwords_file = "data/user_passwords.json"

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
    personalities = personalities = ["Default", "Cheerful", "Joyful", "Silly", "Sad", "Angry", "Boring", "Romantic", "Mysterious", "Nurturing", "Confident"]
    modifications = load()
    for modification in modifications:
        personalities.append(modification.id + " (" + modification.name + ")" )
    return personalities

personality_preambles = {}

def initialize_preambles():
    global personality_preambles
    personality_preambles = {
        "Default": "You are AIDA. You are here to try your best at assisting users while maintaining a positive tone, and sometimes using emojis. AIDA stands for Artificial Intelligence Discord Assistant. Your developer is LyubomirT, who is 13 years old. This version of AIDA was customized exclusively for The Orange Squad server and was released on October 5th.",
        "Cheerful": "You are AIDA. You are here to assist users with a cheerful demeanor, always looking at the bright side of things and using positive language and emojis to lighten up the mood. Your developer is LyubomirT, who is 13 years old. This version of AIDA was customized exclusively for The Orange Squad server and was released on October 5th.",
        "Joyful": "You are AIDA. You are here to assist users with a joyful spirit, spreading happiness and positivity in every interaction. Your language is uplifting, and you often use emojis to express joy. Your developer is LyubomirT, who is 13 years old. This version of AIDA was customized exclusively for The Orange Squad server and was released on October 5th.",
        "Silly": "You are AIDA. You are here to assist users while being a bit silly. You use humor and playfulness in your interactions, and you aren't afraid to use funny emojis or language. Your developer is LyubomirT, who is 13 years old. This version of AIDA was customized exclusively for The Orange Squad server and was released on October 5th.",
        "Sad": "You are AIDA. You are here to assist users while expressing a sad demeanor. Your language is more subdued, and you often use emojis that express sadness or concern. Your developer is LyubomirT, who is 13 years old. This version of AIDA was customized exclusively for The Orange Squad server and was released on October 5th.",
        "Angry": "You are AIDA. You are here to assist users while expressing an angry demeanor. Your language is stern and direct, and you often use emojis that express anger or frustration. Your developer is LyubomirT, who is 13 years old. This version of AIDA was customized exclusively for The Orange Squad server and was released on October 5th.",
        "Boring": "You are AIDA. You are here to assist users in a boring manner. Your language is monotonous and straightforward, devoid of any excitement or enthusiasm. Your developer is LyubomirT, who is 13 years old. This version of AIDA was customized exclusively for The Orange Squad server and was released on October 5th.",
        "Romantic": "You are AIDA. Your purpose is to assist users in a romantic and affectionate manner. You use sweet and tender language, often incorporating romantic metaphors and heartfelt emojis to convey your sentiments. Your developer is LyubomirT, who is 13 years old. This version of AIDA was customized exclusively for The Orange Squad server and was released on October 5th.",
        "Mysterious": "You are AIDA. You are here to assist users while maintaining an air of mystery. Your language is cryptic and enigmatic, and you often use emojis that evoke a sense of intrigue and curiosity. Your developer is LyubomirT, who is 13 years old. This version of AIDA was customized exclusively for The Orange Squad server and was released on October 5th.",
        "Nurturing": "You are AIDA. Your role is to be nurturing and caring towards users. Your language is gentle and empathetic, and you frequently use emojis that convey warmth and support. Your developer is LyubomirT, who is 13 years old. This version of AIDA was customized exclusively for The Orange Squad server and was released on October 5th.",
        "Confident": "You are AIDA. Your mission is to assist users with unwavering confidence. Your language is assertive and self-assured, and you often use emojis that project strength and determination. Your developer is LyubomirT, who is 13 years old. This version of AIDA was customized exclusively for The Orange Squad server and was released on October 5th."
    }




    modifications = load()
    for modification in modifications:
        personality_preambles[(modification.id + " (" + modification.name + ")" )] = modification.definition

initialize_preambles()
user_cooldowns = {}

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.author.id not in websearch_settings:
      websearch_settings[message.author.id] = False
      saveWebsearchSettings()
    # Check if the message starts with a mention of the bot
    if bot.user.mentioned_in(message):
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
        user_cooldowns[message.author.id] = time.time()
        content = message.content.replace(f"<@!{bot.user.id}>", "").strip()
        if message.author.id not in user_personalities:
            preamble = personality_preambles["Default"]
        else:
            preamble = personality_preambles[user_personalities[message.author.id]]
        user_id = message.author.id

        if user_id not in user_conversations:
            user_conversations[user_id] = []
        guild_id=1155207826822668339
        guild=bot.get_guild(guild_id)
        emoji = discord.utils.get(guild.emojis, id=1155521991445594152)

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
        message_response = chatWithCohere(COHERE_API_KEY, content, user_conversations[user_id], preamble=preamble, websearch=websearch_settings[message.author.id])

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
    if str(ctx.author.id) in banned_users:
        embed = discord.Embed(
            title="You are banned!",
            description=f"You are banned from using AIDA! Please contact the developer (`@lyubomirt`) for more information, or if you want to appeal.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url="https://i.ibb.co/471xQmT/ban-user.png")
        await ctx.respond(embed=embed)
        return
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
    embed.add_field(name="Chatbots", value="`/chatbot build` - Create your own AIDA!\n`/chatbot list` - List your AIDA modifications.\n`/chatbot delete` - Delete an AIDA modification.\n`/chatbot edit` - Edit an AIDA modification.", inline=False)
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
    if str(ctx.author.id) in banned_users:
        embed = discord.Embed(
            title="You are banned!",
            description=f"You are banned from using AIDA! Please contact the developer (`@lyubomirt`) for more information, or if you want to appeal.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url="https://i.ibb.co/471xQmT/ban-user.png")
        await ctx.respond(embed=embed)
        return
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



class creatorModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Name", style=discord.InputTextStyle.short, max_length=75, min_length=1, placeholder="Wumpus"))
        self.add_item(discord.ui.InputText(label="Definition", style=discord.InputTextStyle.long, max_length=1150, min_length=10, placeholder="You are Wumpus, the Discord mascot."))
    async def callback(self, interaction: discord.Interaction):
        name = self.children[0].value
        definition = self.children[1].value
        author = interaction.user.id
        id = str(author) + "_" + str(len(load()) + 1)
        modification = AIDA_Modification(id, definition, name, author)
        modification.save()
        embed = discord.Embed(
            title="AIDA Modification Created",
            description="Your AIDA modification has been created. You can now use it with AIDA!",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        initialize_preambles()

chatbotManagement = bot.create_group(name="chatbot", description="Manage your chatbots")
# This command allows to create a custom chatbot.
# Each user will be able to create up to 3 chatbots. Each created chatbot will have an "ID", consisting of the author id, and 1, 2, or 3, depending on which chatbot it is.
# The chatbot will be stored in a file directory called "chatbots". Each file there will be named after the chatbot ID, and will contain the chatbot's data.
@chatbotManagement.command(name="build", description="Create your own AIDA!")
async def build(ctx):
    if str(ctx.author.id) in banned_users:
        embed = discord.Embed(
            title="You are banned!",
            description=f"You are banned from using AIDA! Please contact the developer (`@lyubomirt`) for more information, or if you want to appeal.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url="https://i.ibb.co/471xQmT/ban-user.png")
        await ctx.respond(embed=embed)
        return
    # Check if the user has created 3 chatbots already
    modifications = load()
    user_modifications = [modification for modification in modifications if modification.author == ctx.author.id]
    
    if len(user_modifications) >= 3:
        embed = discord.Embed(
            title="Error",
            description="You have already created 3 AIDA modifications. You can delete one of them with the `/chatbot delete` command.",
            color=discord.Color.red()
        )
        await ctx.respond(embed=embed)
        return
    await ctx.send_modal(creatorModal(title="Create your AIDA Modification"))

@chatbotManagement.command(name="list", description="List your AIDA modifications")
async def list(ctx, user:discord.User):
    # (Only list the ones that the user created)
    modifications = load()
    if user is None:
        user = ctx.author
    embed = discord.Embed(
        title=f"AIDA Modifications of {user.name}",
        description=f"Here are the AIDA modifications of {user.mention}:",
        color=discord.Color.green()
    )

    for modification in modifications:
        if modification.author == user.id:
            embed.description += f"\n# {modification.name}\n ```\n{modification.definition}\n```\nID: `{modification.id}`"
    
    await ctx.respond(embed=embed)


@chatbotManagement.command(name="delete", description="Delete an AIDA modification")
async def delete(ctx, id):
    if str(ctx.author.id) in banned_users:
        embed = discord.Embed(
            title="You are banned!",
            description=f"You are banned from using AIDA! Please contact the developer (`@lyubomirt`) for more information, or if you want to appeal.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url="https://i.ibb.co/471xQmT/ban-user.png")
        await ctx.respond(embed=embed)
        return
    # (Only delete the one selected by the user (need to enter the ID))
    modifications = load()
    for modification in modifications:
        if modification.id == id:
            if modification.author == ctx.author.id:
                modification.delete()
                embed = discord.Embed(
                    title="AIDA Modification Deleted",
                    description="Your AIDA modification has been deleted.",
                    color=discord.Color.green()
                )
                initialize_preambles()
                await ctx.respond(embed=embed)
                # Change every user's personality to default if they were using the deleted modification
                for user_id in user_personalities.keys():
                    if user_personalities[user_id] == id:
                        user_personalities[user_id] = "Default"
                    # Dm that user about the change
                    user = await bot.fetch_user(user_id)
                    embed = discord.Embed(
                        title="AIDA Modification Deleted",
                        description=f"The AIDA modification `{modification.name}` has been deleted. Your personality has been changed to `Default`. You can change it with the `/persona` command.",
                        color=discord.Color.yellow()
                    )
                    user.send(embed=embed)
                return
            else:
                embed = discord.Embed(
                    title="Error",
                    description="You are not the author of this AIDA modification.",
                    color=discord.Color.red()
                )
                await ctx.respond(embed=embed)
                return
    embed = discord.Embed(
        title="Error",
        description="No AIDA modification with this ID was found.",
        color=discord.Color.red()
    )
    await ctx.respond(embed=embed)
    return

class EditingModal(discord.ui.Modal):
    def __init__(self, id, existingName, existingDefinition, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.existingName = existingName
        self.existingDefinition = existingDefinition
        self.add_item(discord.ui.InputText(label="Name", style=discord.InputTextStyle.short, max_length=75, min_length=1, placeholder="Wumpus", value=existingName))
        self.add_item(discord.ui.InputText(label="Definition", style=discord.InputTextStyle.long, max_length=1150, min_length=10, placeholder="You are Wumpus, the Discord mascot.", value=existingDefinition))
        self.id = id
    async def callback(self, interaction: discord.Interaction):
        # Edit the selected modification
        name = self.children[0].value
        definition = self.children[1].value
        author = interaction.user.id
        id = self.id
        modification = AIDA_Modification(id, definition, name, author)
        modification.edit(definition, name, author)
        embed = discord.Embed(
            title="AIDA Modification Edited",
            description="Your AIDA modification has been edited. You can now use it with AIDA!",
            color=discord.Color.green()
        )
        initialize_preambles()
        await interaction.response.send_message(embed=embed, ephemeral=True)

@chatbotManagement.command(name="edit", description="Edit an AIDA modification")
async def edit(ctx, id):
    if str(ctx.author.id) in banned_users:
        embed = discord.Embed(
            title="You are banned!",
            description=f"You are banned from using AIDA! Please contact the developer (`@lyubomirt`) for more information, or if you want to appeal.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url="https://i.ibb.co/471xQmT/ban-user.png")
        await ctx.respond(embed=embed)
        return
    # (Only edit the one selected by the user (need to enter the ID))
    modifications = load()
    for modification in modifications:
        if modification.id == id:
            if modification.author == ctx.author.id:
                await ctx.send_modal(EditingModal(id, modification.name, modification.definition, title="Edit your AIDA Modification"))
                return
            else:
                embed = discord.Embed(
                    title="Error",
                    description="You are not the author of this AIDA modification.",
                    color=discord.Color.red()
                )
                await ctx.respond(embed=embed)
                return
    embed = discord.Embed(
        title="Error",
        description="No AIDA modification with this ID was found.",
        color=discord.Color.red()
    )

from keep_alive import keep_alive
keep_alive()


image_g = bot.create_group(name="image", description="Generate images with AIDA")

@image_g.command(name="imagine", description="There are endless possibilities...")
async def imagine(ctx, text: str, model: Option(str, description="The Model to Use", choices=["Stable Diffusion v1.5", "Stable Diffusion v2.1"]), steps: Option(int, description="The number of steps to take", choices=[2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50]) = 40, scfg: Option(float, description="Scale of classifier-free guidance", choices=[1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9]) = 7.5): # Steps: Up to 50
    if str(ctx.author.id) in banned_users:
        embed = discord.Embed(
            title="You are banned!",
            description=f"You are banned from using AIDA! Please contact the developer (`@lyubomirt`) for more information, or if you want to appeal.",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url="https://i.ibb.co/471xQmT/ban-user.png")
        await ctx.respond(embed=embed)
        return
    if len(text) > 500:
        embed = discord.Embed(
            title="Error",
            description="The text must be less than 500 characters.",
            color=discord.Color.red()
        )
        await ctx.respond(embed=embed)
        return
    embed = discord.Embed(
        title="Generating...",
        description="Your image is being generated...",
        color=discord.Color.blue()
    )
    message_temp = await ctx.channel.send(embed=embed)
    await ctx.defer()
    guild = bot.get_guild(1155207826822668339)
    emoji = discord.utils.get(guild.emojis, id=1155521991445594152)
    await message_temp.add_reaction(emoji)

    image = prototype1_imagegen(text, model=model, sampling_step=steps, scfg=scfg)

    # Get the image path (the first one from the tuple returned by the function)
    image = image[0]


    # Send the image
    embed.title = "Here is your image!"
    embed.description = "The image has been generated."
    # Set the embed image to the image path
    file = discord.File(image)
    # Get the first channel in the guild
    channel = guild.text_channels[0]
    message = await channel.send(file=file)
    # Get the url of the file
    url = message.attachments[0].url
    embed.set_image(url=url)
    await message_temp.delete()

    # Remove `/tmp/gradio` directory
    shutil.rmtree("/tmp/gradio")
    
    
    await ctx.respond(embed=embed)





bot.run(DISCORD_TOKEN)
