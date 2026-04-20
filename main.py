from todus.client import ToDusClient
from pathlib import Path
from pyrogram.client import Client
from pyrogram.filters import command, private, video, document, photo, audio
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os

load_dotenv(Path(".env"))

tclient = ToDusClient()

bot: Client = Client(
    name="todus-bot",
    api_id=os.getenv("API_ID"),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

@bot.on_message(command("start") & private)
async def start(client: Client, message: Message):
    
    await message.reply(f"hola {message.from_user.mention}")

@bot.on_message(command("token") & private)
async def create_login(client: Client, message: Message):

    if len(message.command) < 2:
        return
    
    if len(message.command) > 2:
        return

    if os.path.exists("./token.txt"):
        await message.reply("Ya existe un token, esta seguro que desea cambiarlo?", 
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [InlineKeyboardButton("Si", callback_data="answer_yes")]
                                ]
                            ))
        
        return

    with open("token.txt", "w", encoding="utf-8") as file:
        file.write(message.command[-1])

    await message.reply("token annadido")

@bot.on_message(video | document | photo | audio & (private))
async def dl_up(client: Client, message: Message):
    
    if not os.path.exists("./token.txt", encoding="utf-8"):
        await message.reply("no hay token, ponga uno")
        return

    with open("./token.txt", "r", encoding="utf-8") as file:
        token = file.read().strip()

    await message.reply("descargando...")

    filename = await message.download()

    await message.reply("subiendo a todus")
    url = tclient.upload_file(token, Path(filename), max_retry=20)

    real_filename = filename.split("/")[-1]
    txt = f"./{real_filename}.txt"

    content = f"{url}\t{real_filename}"
    
    with open(txt, "w", encoding="utf-8") as file:
        file.write(content)


    await message.reply_document(txt)
    os.remove(txt)

@bot.on_callback_query()
async def manage_querys(client: Client, query: CallbackQuery):

    if query.data == "answer_yes":
        
        with open("token.txt", "w", encoding="utf-8") as file:
            file.write(query.message.reply_to_message.text.split(" ")[-1])

        await query.message.reply("token annadido")

if __name__ == "__main__":
    print("bot running")
    bot.run()