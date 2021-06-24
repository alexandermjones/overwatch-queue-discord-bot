# Overwatch Queue Discord Bot
A Discord bot for managing a queue of Overwatch players.

## Description

A Discord bot created for a group of friends that play 
Overwatch together, but often have more players than the team 
limit of six.

The bot allows a user to create a queue, which players can join.
When a game ends, the queue can be updated to see who is 
playing in the next game.
The queue cycles through players two at a time, so all players
get a chance to play games with minimal fuss.

The bot will optionally post patch notes of latest patch notes to the game into
a chosen server by running the command !patchnotes.
The patch scraper class can be used outside of the bot if desired.

## Installation

Create a .env file in your local version of this folder with the structure:
```
# .env
DISCORD_TOKEN=your-discord-token
```
The details for getting this token and setting up a Discord bot are [here](https://realpython.com/how-to-make-a-discord-bot-python/).
Once done, just install the necessary dependencies:
```
pip3 install -r requirements.txt
```

## Usage

Run the bot_code folder with python to start the bot.
```
python3 bot_code
```
Type `!help` in your Discord server to see the available commands:

```
  add            Add a player to the queue.
  delay          Temporarily no longer be counted as a current player
  end            End (empty) the current queue.
  help           Shows this message
  join           Join the Overwatch queue.
  kick           Remove a player from the queue.
  leave          Leave the Overwatch queue.
  link           Link a discord name to a battle net account
  next           Update the queue for the next game.
  patchnotes     The bot will post Overwatch patch notes to this channel.
  queue          Starts an Overwatch queue.
  rejoin         Stop delaying games and be a current player again.
  status         See the status of the queue.
  stoppatchnotes The bot will stop posting Overwatch patch notes to this channel.
  undo           Undo the previous command issued.
  wait           See how long until your next game.
```

## Contributing
Contributions are welcome, but please get in touch with me first
to discuss.

## License
[MIT](https://choosealicense.com/licenses/mit/)