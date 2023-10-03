
# AIDA Discord Bot

## Table of Contents

- [Introduction](#introduction)
- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
  - [Basic Interaction](#basic-interaction)
  - [Changing AIDA's Personality](#changing-aidas-personality)
  - [Banning and Unbanning Users](#banning-and-unbanning-users)
  - [Sending Feedback](#sending-feedback)
  - [Web Search Settings](#web-search-settings)  <!-- Added this section -->
- [Contributing](#contributing)
- [License](#license)

## Introduction

AIDA (Artificial Intelligence Discord Assistant) is a Discord bot designed to provide conversational interactions with users. It uses the Cohere API for natural language processing and can be configured with different personalities to suit the tone of interactions.

## Setup

### Prerequisites

Before setting up the AIDA Discord Bot (self-hosted), ensure you have the following:

1. A Discord Bot Token: Create a Discord Bot and obtain its token. You can do this by creating a new bot on the [Discord Developer Portal](https://discord.com/developers/applications).

2. Cohere API Key: Sign up for the Cohere API and obtain an API key from [Cohere Technologies](https://cohere.ai/).

3. Python Environment: Ensure you have Python 3.7 or higher installed.

### Installation

1. Clone the AIDA Discord Bot repository:

   ```bash
   git clone https://github.com/The-Orange-Squad/AIDA.git
   cd AIDA
   ```

2. Install the required Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. Create a `.env` file in the project directory and add the following environment variables:

   ```
   COHERE_API_KEY=your_cohere_api_key
   DISCORD_TOKEN=your_discord_bot_token
   MODERATOR=your_discord_user_id
   ```

   Replace `your_cohere_api_key` with your Cohere API key, `your_discord_bot_token` with your Discord bot token, and `your_discord_user_id` with your Discord user ID (used for moderation).

2. Customize `personality_preambles` in the code to define different personalities for AIDA. You can add or modify personality descriptions to suit your preferences.

## Usage

### Basic Interaction

To interact with AIDA, follow these steps:

1. Invite the bot to your Discord server using the bot's OAuth2 link.

2. Mention the bot by using `@bot-name` in your message to initiate a conversation with AIDA.

3. AIDA will respond to your message based on the configured personality and the content of your message.

### Changing AIDA's Personality

You can change AIDA's personality using the `/persona` command. Here's how:

1. Type `/persona` in a text channel.

2. Choose a personality from the autocomplete menu provided by the bot.

3. AIDA's personality will be updated, and the chat history will be cleared.

### Banning and Unbanning Users

Moderators can use the `/ban` and `/unban` commands to manage user access to AIDA:

- `/ban @user`: Ban a user from using AIDA.
- `/unban @user`: Unban a user who was previously banned.

Note: You must have the moderator permission to use these commands.

### Sending Feedback

Users can provide feedback to the bot developer using the `/feedback` command:

1. Type `/feedback` in a text channel.

2. A modal dialog will appear, allowing you to enter your feedback.

3. After submitting feedback, it will be sent to the developer for review.

### Web Search Settings

Users can toggle web search settings using the `/settings` command:

1. Type `/settings` in a text channel.

2. Choose the option to enable or disable web search results from AIDA.

3. A confirmation message will be provided, and your web search settings will be updated accordingly.

## Contributing

If you would like to contribute to the development of AIDA Discord Bot, please fork the repository, make your changes, and submit a pull request. Your contributions are welcome!

## License

This project is licensed under the [BSD 3-Clause License](LICENSE). Feel free to use, modify, and distribute it according to the terms of the license.