import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv

# تحميل التوكن من ملف .env
load_dotenv()
TOKEN = os.getenv('TOKEN')

# إعدادات البوت والـ Intents
intents = discord.Intents.default()
intents.message_content = True  # ضروري لقراءة الأوامر
intents.voice_states = True    # ضروري للتعامل مع القنوات الصوتية

# تغيير الـ Prefix إلى '
bot = commands.Bot(command_prefix="'", intents=intents)

# ملف حفظ بيانات القنوات (24/7)
DATA_FILE = "shady_247_data.json"

def save_voice_data(guild_id, channel_id):
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    
    data[str(guild_id)] = channel_id
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_voice_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

@bot.event
async def on_ready():
    # استخدام الهوية الخاصة بك في رسالة التشغيل
    print(f'🚀 Shady (/3nvy) is Online (24/7 Mode Only)')
    
    # محاولة إعادة الاتصال بالقنوات المحفوظة تلقائياً
    voice_data = load_voice_data()
    for guild_id, channel_id in voice_data.items():
        guild = bot.get_guild(int(guild_id))
        if guild:
            channel = guild.get_channel(int(channel_id))
            if channel:
                try:
                    await channel.connect()
                    print(f"✅ Reconnected to voice in: {guild.name}")
                except Exception as e:
                    print(f"❌ Failed to reconnect in {guild.name}: {e}")

@bot.command(name='24/7')
async def stay_247(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        try:
            await channel.connect()
            save_voice_data(ctx.guild.id, channel.id)
            await ctx.send(f"✅ **24/7 Mode Activated!** I will stay in: `{channel.name}`")
        except discord.ClientException:
            await ctx.send("I'm already in a voice channel!")
    else:
        await ctx.send("❌ You must be in a voice channel first!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        # مسح القناة من الذاكرة لتعطيل الـ 24/7 في هذا السيرفر
        data = load_voice_data()
        if str(ctx.guild.id) in data:
            del data[str(ctx.guild.id)]
            with open(DATA_FILE, "w") as f:
                json.dump(data, f)
        
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the voice channel and disabled 24/7.")
    else:
        await ctx.send("I'm not in a voice channel.")

# تشغيل البوت
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Error: No TOKEN found in .env file!")