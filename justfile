watch:
    watchmedo auto-restart -p "*.py" -R python3 -- discord_bot.py
run:
    python3 discord_bot.py
update-reqs:
    pip3 freeze > requirements.txt
    git add requirements.txt
    git commit -m "updated requirements file"
env:
    @echo source {{justfile_directory()}}/.venv/bin/activate