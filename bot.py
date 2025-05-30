import discord,asyncio,datetime,io
import requests,random,traceback
from PIL import Image
from discord.ext import commands
from google import genai
from google.genai import types
client = genai.Client(
    api_key="********************",  # Replace with your actual API key
)
discord_token = "********************" # Replace with your actual Discord token
# Note: Do not share your API key or Discord token publicly.
# Note: Use a burner account!
ownerid = 879374229286580324  # Replace with your actual main discord acc ID.
generate_content_config = types.GenerateContentConfig(
    thinking_config = types.ThinkingConfig(
        thinking_budget=0,
    ),
    response_mime_type="text/plain",
    system_instruction=open("sys.txt", "r", encoding="utf-8").read()
)
model = "gemini-2.5-flash-preview-05-20"  # Default model
chat = client.aio.chats.create(
    model=model,
    config=generate_content_config)
mem = open("memory.txt", "a+", encoding="utf-8")
bot = commands.Bot(command_prefix='k!', self_bot=True)
stop = False
processing = False
avgwpm = 75  # Average words per minute for typing speed

def estimate_typing_time(text: str, wpm: float) -> float:
    if wpm <= 0:
        raise ValueError("wpm must be greater than 0")
    word_count = len(text.split())
    minutes = word_count / wpm
    seconds = minutes * 60
    return seconds


@bot.event
async def on_message(msg):
    global stop, processing,model, chat, avgwpm
    if msg.author == bot.user:
        return
    try:
        user_name = (msg.guild.get_member(msg.author.id) or msg.author).display_name or msg.author.name
    except:
        user_name = msg.author.display_name or msg.author.name
    content = msg.content
    if "uni" in content.lower():
        # if the message contains "uni", we will react with a cat (40% chance)
        if random.random() < 0.05:
            try:
                await msg.add_reaction("🇺")
                await msg.add_reaction("🇳")
                await msg.add_reaction("🇮")
                await msg.add_reaction("💜")
            except discord.Forbidden:
                print("Cannot add reaction, missing permissions.")
        elif random.random() < 0.4:
            try:
                await msg.add_reaction("🐱")
            except discord.Forbidden:
                print("Cannot add reaction, missing permissions.")
    for i in msg.embeds:
        if i.title is not None:
            content = i.description
    for mention in msg.mentions:
        content = content.replace(mention.mention, f"@{mention.display_name or mention.name}")
    referenced_message = await msg.channel.fetch_message(msg.reference.message_id) if msg.reference else None
    referenced_user_name = (referenced_message.guild.get_member(referenced_message.author.id) or referenced_message.author).display_name or referenced_message.author.name if referenced_message else None
    referenced_content = referenced_message.content if referenced_message else None
    isdms = msg.channel.type == discord.ChannelType.private
    message = f"(Replying to: {referenced_user_name}: {referenced_content})\n(Time: {msg.created_at.strftime("%H:%M")}) ({user_name}): {content}" if referenced_message else f"{user_name}: {content}"
    if isdms:
        message = "(DMS) "+message
    else:
        message = f"(#{msg.channel.name}, guild name: {msg.guild.name}) "+message

    # Now, 'message' contains the formatted text
    #print(message)

    if msg.content.startswith("uni!stop") and msg.author.id == ownerid:
        stop = True
        await msg.channel.send("bye", delete_after=2)
    if msg.content.startswith("uni!resume") and msg.author.id == ownerid:
        stop = False
        await msg.channel.send("hello", delete_after=2)
    if msg.content.startswith("uni!meow"):
        await msg.channel.send("meow!!")
    if msg.content.startswith("uni!change_model") and msg.author.id == ownerid:
        model = msg.content.split(" ")[1] if len(msg.content.split(" ")) > 1 else "llama-3.3-70b-versatile"
        chat = client.aio.chats.create(
            model=model,
            config=generate_content_config)
        await msg.channel.send(f"Model changed to {model}", delete_after=2)
    if msg.content.startswith("uni!clear_history") and msg.author.id == ownerid:
        chat = client.aio.chats.create(
            model=model,
            config=generate_content_config)
        await msg.channel.send("History cleared.", delete_after=2)
    if msg.content.startswith("uni!info"):
        await msg.channel.send(
            f"""
**Hello, Im uni!**
I am a selfbot that uses the Google Gemini API to chat with you.
Model: `{model}`
Average WPM: `{avgwpm}`
Creator: <@879374229286580324> (funicat)
And lord thank you `https://dns.comss.one/dns-query` for fixing the ai api.
And... fuck you google for being angry i am not in USA.
            """, silent=True
        )
    if msg.content.startswith("uni!set_wpm") and msg.author.id == ownerid:
        try:
            avgwpm = int(msg.content.split(" ")[1])
            await msg.channel.send(f"Average WPM set to {avgwpm}", delete_after=2)
        except (ValueError, IndexError):
            await msg.channel.send("Please provide a valid number for WPM.", delete_after=2)
    if msg.content.startswith("uni!source"):
        await msg.channel.send(
            f"""
My source code: https://github.com/simpleuserdontwatch/Uni-ai/tree/main
            """, silent=True
        )
    if (bot.user.mentioned_in(msg) or isdms) and not stop:
        # find any attachments we can use for img
        img = None
        for attachment in msg.attachments:
            if attachment.content_type.startswith("image"):
                img = attachment.url
                # yet, we need a PIL image. so fetch!
                img_req = requests.get(img)
                img_data = img_req.content
                img = Image.open(io.BytesIO(img_data))
        print(msg)
        if processing:
            while processing:
                await asyncio.sleep(0.05)
        processing = True
        if img is not None:
            status = False
            while not status:
                try:
                    response = await chat.send_message(
                        [
                            message, img
                        ]
                    )
                    status = True
                except:
                    print("Failed.")
                    traceback.print_exc()
                    await asyncio.sleep(2)
                    
        else:
            status = False
            while not status:
                try:
                    response = await chat.send_message(
                        [
                            message
                        ]
                    )
                    status = True
                except:
                    print("Failed.")
                    traceback.print_exc()
                    await asyncio.sleep(2)

        print(response.text)
        mem.write(message+"\n(Uni): "+response.text+"\n-------------------\n")
        async with msg.channel.typing():
            
            if not "<ignore>" in response.text:
                await asyncio.sleep(estimate_typing_time(response.text, wpm=avgwpm))  # Simulate typing time
                try:
                    if not isdms:
                        await msg.channel.send(response.text.replace("Uni:","").replace("uni:",""),reference=msg)
                    else:
                        await msg.channel.send(response.text.replace("Uni:","").replace("uni:",""))
                except:
                    if not isdms:
                        await msg.channel.send(response.text.replace("Uni:","").replace("uni:",""),reference=msg)
                    else:
                        await msg.channel.send(response.text.replace("Uni:","").replace("uni:",""))

        await asyncio.sleep(0.125)  # To prevent rate limiting
        processing = False

bot.run(discord_token)
