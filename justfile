watch:
    watchmedo auto-restart -p "*.py" -R python3 -- discord_bot.py --log=INFO
run:
    python3 discord_bot.py
env:
    poetry shell