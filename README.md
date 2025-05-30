# Uni-ai
Simple self-bot with gemini api. (Plus, patched gemini _api_client.py for folks that are not in USA!)

## Requirements
```
pip install google-genai
pip install discord.py
pip install discord.py-self
```
<sup>Also, if the discord.py-self doesnt work, build it from source.</sup>

## Notes!!
Replace the dummy values in bot.py (and keep in mind, you need a burner discord acc token, and a gemini api key)

Also, if you arent in USA, place the `_api_client.py` in C:\\Users\\(user)\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\google\\genai

Also, the `_api_client.py` uses 'https://funiapi.vercel.app/proxy/'.
