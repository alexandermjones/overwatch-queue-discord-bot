# Overwatch Queue Discord Bot
A Discord bot for managing a queue of Overwatch players.

## Description

A Discord bot created for a group of friends that play 
Overwatch together, but often have more than the team 
limit of six.
The bot allows a user to create a queue, which players can join.
When a game ends, the queue can be updated to see who is 
playing in the next game.
The queue cycles through players two at a time, so all players
get a chance to play games with minimal fuss.

This bot and repository are currently in beta.
## Installation

Create a .env file in your local version of this folder with the structure:
```
# .env
DISCORD_TOKEN=your-discord-token
DISCORD_GUILD=your-server-name
```
The details for getting these tokens and setting up a Discord bot are [here](https://realpython.com/how-to-make-a-discord-bot-python/).
Once done, just install the necessary dependencies:
```
pip3 install -r requirements.txt
```

## Usage

Run the python file discord_bot.py and type `!help` in your Discord
server to see available commands.
```
python3 discord_bot.py
```
If you use [just](https://github.com/casey/just) then you can just run.

```
just run
```

or, for development
```
just watch
```

## Contributing
Contributions are welcome, but please get in touch with me first
to discuss.

## License
[MIT](https://choosealicense.com/licenses/mit/)