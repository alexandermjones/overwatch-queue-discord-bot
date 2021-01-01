watch:
    watchmedo auto-restart -p "*.py" -R python3 -- discord_bot.py
run:
    python3 discord_bot.py
env:
    @echo source {{justfile_directory()}}/.venv/bin/activate