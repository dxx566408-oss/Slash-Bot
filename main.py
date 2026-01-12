import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import time
import random
import io  # ضروري لمعالجة بيانات الصورة في الذاكرة
from PIL import Image, ImageDraw, ImageFont  # ضروري لإنشاء صورة الكابتشا
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

# --- تشغيل السيرفر لإبقاء البوت حياً ---
app = Flask('')
@app.route('/')
def home(): return "Hermenya Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- دالة صنع صورة الكابتشا ---
def create_captcha_image(text):
    # إنشاء خلفية داكنة تناسب ديسكورد
    img = Image.new('RGB', (150, 60), color=(43, 45, 49))
    d = ImageDraw.Draw(img)
    
    # كتابة الأرقام باللون الأحمر الفاقع في منتصف الصورة تقريباً
    d.text((55, 20), text, fill=(255, 0, 0)) 
    
    # إضافة 8 خطوط تشويش عشوائية خلف/فوق النص
    for i in range(8):
        d.line([(random.randint(0,150), random.randint(0,60)), 
                (random.randint(0,150), random.randint(0,60))], 
               fill=(100, 100, 100))
               
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

# --- إعدادات البوت الأساسية ---
class HermenyaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        self.data_file = "database.json"
        self.users_data = self.load_data()
        self.voice_times = {}

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f: return json.load(f)
        return {}

    def save_data(self):
        with open(self.data_file, "w") as f: json.dump(self.users_data, f, indent=4)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ تم مزامنة جميع الأوامر بنجاح")

bot = HermenyaBot()

# --- دالة جلب البيانات ---
# --- أمر البروفايل المحلي (profile) ---
@bot.tree.command(name="profile", description="عرض مستواك في هذا السيرفر فقط")
async def profile(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    stats = get_stats(target.id, interaction.guild.id)
    embed = discord.Embed(title=f"🏠 ملف {target.display_name} المحلي", color=0xff0000)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="المستوى", value=f"⭐ `{stats['level']}`", inline=True)
    embed.add_field(name="الخبرة", value=f"✨ `{stats['xp']}/20`", inline=True)
    embed.add_field(name="الرسائل", value=f"✉️ `{stats['msg_count']}`", inline=False)
    await interaction.response.send_message(embed=embed)

# --- أمر البروفايل العالمي (globalprofile) ---
@bot.tree.command(name="globalprofile", description="عرض مستواك الإجمالي في كل السيرفرات")
async def globalprofile(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    stats = get_stats(target.id) 
    embed = discord.Embed(title=f"🌍 الحساب العالمي: {target.display_name}", color=0xff0000)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="المستوى العالمي", value=f"🏆 `{stats['level']}`", inline=True)
    embed.add_field(name="الخبرة الإجمالية", value=f"✨ `{stats['xp']}/20`", inline=True)
    embed.add_field(name="مجموع الرسائل الكلي", value=f"📧 `{stats['msg_count']}`", inline=False)
    h = stats['voice_seconds'] // 3600
    m = (stats['voice_seconds'] % 3600) // 60
    s = stats['voice_seconds'] % 60
    embed.add_field(name="إجمالي وقت الفويس", value=f"🎙️ `{h}` ساعة و `{m}` دقيقة و `{s}` ثانية", inline=False)
    await interaction.response.send_message(embed=embed)

def get_stats(user_id, guild_id=None):
    uid = str(user_id)
    if uid not in bot.users_data:
        bot.users_data[uid] = {"mrad": 0}
    
    if guild_id:
        gid = str(guild_id)
        if gid not in bot.users_data[uid]:
            bot.users_data[uid][gid] = {"level": 0, "xp": 0, "msg_count": 0, "voice_seconds": 0}
        return bot.users_data[uid][gid]
    else:
        all_stats = {"level": 0, "xp": 0, "msg_count": 0, "voice_seconds": 0, "mrad": bot.users_data[uid].get("mrad", 0)}
        total_xp = 0
        for key, value in bot.users_data[uid].items():
            if isinstance(value, dict):
                all_stats["msg_count"] += value.get("msg_count", 0)
                all_stats["voice_seconds"] += value.get("voice_seconds", 0)
                total_xp += (value.get("level", 0) * 20) + value.get("xp", 0)
        all_stats["level"] = total_xp // 20
        all_stats["xp"] = total_xp % 20
        return all_stats

# --- نظام الحسبة المطور مع دعم التواريخ ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    uid = str(message.author.id)
    gid = str(message.guild.id)
    today = datetime.now().strftime("%Y-%m-%d")
    
    stats = get_stats(uid, gid)
    stats["msg_count"] += 1
    
    # تسجيل النشاط اليومي للترتيب
    if "daily_activity" not in stats: stats["daily_activity"] = {}
    stats["daily_activity"][today] = stats["daily_activity"].get(today, 0) + 1
    
    if stats["msg_count"] % 25 == 0:
        stats["xp"] += 1
        if stats["xp"] >= 20:
            stats["level"] += 1
            stats["xp"] = 0
            
    bot.save_data()
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot or not member.guild: return
    uid = str(member.id)
    gid = str(member.guild.id)
    today = datetime.now().strftime("%Y-%m-%d")
    
    if before.channel is None and after.channel is not None:
        bot.voice_times[member.id] = time.time()
    elif before.channel is not None and after.channel is None:
        if member.id in bot.voice_times:
            duration = int(time.time() - bot.voice_times.pop(member.id))
            stats = get_stats(uid, gid)
            stats["voice_seconds"] += duration 
            
            # تسجيل نشاط الفويس اليومي للترتيب
            if "daily_voice" not in stats: stats["daily_voice"] = {}
            stats["daily_voice"][today] = stats["daily_voice"].get(today, 0) + duration
            
            while stats["voice_seconds"] >= 300:
                stats["xp"] += 1
                stats["voice_seconds"] -= 300
                if stats["xp"] >= 20:
                    stats["level"] += 1
                    stats["xp"] = 0
            bot.save_data()

# --- 1. أمر مراد (أحمر فاقع) ---
@bot.tree.command(name="mrad", description="عرض أو تحويل رصيد مراد")
@app_commands.describe(user="العضو المراد التحويل له", amount="المبلغ المراد تحويله")
async def mrad(interaction: discord.Interaction, user: discord.Member = None, amount: int = None):
    MY_ID = 1371432836946726934 
    
    # 1. حالة عرض الرصيد فقط
    if amount is None:
        target = user or interaction.user
        s = get_stats(target.id)
        embed = discord.Embed(description=f"💰 رصيد **{target.mention}** هو: `{s['mrad']}` مراد", color=0xff0000)
        return await interaction.response.send_message(embed=embed)

    # 2. إعداد البيانات
    sender_id = interaction.user.id
    receiver_id = user.id
    sender_stats = get_stats(sender_id)
    receiver_stats = get_stats(receiver_id)

    # 3. التحقق من الشحن الذاتي للمطور
    if sender_id == receiver_id:
        if sender_id == MY_ID:
            receiver_stats["mrad"] += amount
            bot.save_data()
            return await interaction.response.send_message(f"✅ أهلاً مطورنا، تم إضافة `{amount}` لرصيدك بنجاح!")
        else:
            return await interaction.response.send_message("❌ لا يمكنك التحويل لنفسك!", ephemeral=True)

    # 4. فحص رصيد المستخدم العادي
    if sender_id != MY_ID and sender_stats["mrad"] < amount:
        return await interaction.response.send_message("❌ رصيدك لا يكفي لإتمام هذه العملية!", ephemeral=True)

    if amount <= 0:
        return await interaction.response.send_message("❌ يجب أن يكون المبلغ أكبر من صفر!", ephemeral=True)

    # 5. نظام الكابتشا (الصورة) للتحويل بين الأشخاص
    captcha_text = str(random.randint(1111, 9999))
    captcha_file = discord.File(create_captcha_image(captcha_text), filename="captcha.png")

    embed_captcha = discord.Embed(
        title="🛡️ تحقق الأمان", 
        description=f"اكتب الأرقام الظاهرة في الصورة للتأكيد:\nلتحويل `{amount}` إلى {user.mention}", 
        color=0xff0000
    )
    embed_captcha.set_image(url="attachment://captcha.png")

    await interaction.response.send_message(file=captcha_file, embed=embed_captcha)

    def check(m): 
        return m.author == interaction.user and m.channel == interaction.channel
        
    try:
        msg_res = await bot.wait_for('message', check=check, timeout=30.0)
        if msg_res.content == captcha_text:
            await msg_res.delete()
            await interaction.delete_original_response()
            
            # تنفيذ العملية (المطور لا ينقص رصيده)
            if sender_id != MY_ID:
                sender_stats["mrad"] -= amount
            
            receiver_stats["mrad"] += amount
            bot.save_data()
            
            await interaction.followup.send(f"✅ تم تحويل `{amount}` إلى {user.mention} بنجاح.")
        else:
            await msg_res.delete()
            await interaction.followup.send("❌ الرقم غير صحيح، تم إلغاء العملية.", ephemeral=True)
            
    except TimeoutError:
        await interaction.followup.send("⚠️ انتهى الوقت، تم إلغاء عملية التحويل.")

# --- 3. أمر الأفاتار (أحمر فاقع) ---
@bot.tree.command(name="avatar", description="عرض صورة الحساب")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    avatar_url = target.display_avatar.with_size(1024).url
    embed = discord.Embed(title=f"صورة {target.name}", url=avatar_url, color=0xff0000)
    embed.set_image(url=avatar_url)
    await interaction.response.send_message(embed=embed)

# --- 4. أمر الآيدي (أحمر فاقع) ---
@bot.tree.command(name="id", description="عرض الآيدي")
async def id_info(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    embed = discord.Embed(title="🆔 معرف العضو", color=0xff0000)
    embed.add_field(name="العضو", value=target.mention, inline=True)
    embed.add_field(name="الآيدي", value=f"`{target.id}`", inline=True)
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# --- 5. أمر السيرفر (أحمر فاقع) ---
@bot.tree.command(name="server", description="عرض معلومات السيرفر بالتفصيل")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild
    
    # حساب الإحصائيات
    total_members = guild.member_count
    bot_count = len([m for m in guild.members if m.bot])
    human_count = total_members - bot_count
    
    # تاريخ إنشاء السيرفر
    created_ts = int(guild.created_at.timestamp())
    
    # إنشاء الإيمبد بتنسيق يشبه الصورة
    embed = discord.Embed(color=0x2b2d31) # لون داكن رسمي
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    # السطر الأول: المالك وتاريخ الإنشاء والآيدي (باستخدام المنشن والأيقونات)
    embed.add_field(
        name="", 
        value=f"👑 **مملوك بواسطة**\n{guild.owner.mention}", 
        inline=True
    )
    embed.add_field(
        name="", 
        value=f"📅 **تاريخ الانشاء**\n<t:{created_ts}:D>\n**<t:{created_ts}:R>**", 
        inline=True
    )
    embed.add_field(
        name="", 
        value=f"🆔 **ايدي السيرفر**\n`{guild.id}`", 
        inline=True
    )

    # السطر الثاني: الأعضاء بالتفصيل
    embed.add_field(
        name="", 
        value=f"👥 **الأعضاء ({total_members})**\nالاعضاء: `{human_count}`\nالبوتات: `{bot_count}`", 
        inline=True
    )

    # السطر الثالث: الرومات (إحصائية إضافية لتعبئة الشكل)
    embed.add_field(
        name="", 
        value=f"💬 **الرومات ({len(guild.channels)})**\nكتابي: `{len(guild.text_channels)}` | صوتي: `{len(guild.voice_channels)}`", 
        inline=True
    )

    # السطر الأخير: تعزيز السيرفر
    embed.add_field(
        name="", 
        value=f"✨ **التعزيزات**\nعدد البوستات: `{guild.premium_subscription_count}`", 
        inline=True
    )

    await interaction.response.send_message(embed=embed)
# --- 6. أمر الأسماء (أحمر فاقع) ---
@bot.tree.command(name="name", description="عرض جميع أسماء العضو بالتفصيل")
@app_commands.describe(member="العضو المراد فحص أسمائه")
async def name_info(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    
    # 1. اليوزر نيم الأصلي (الفريد)
    user_name = target.name
    
    # 2. الاسم العالمي (Global Name) - الاسم الذي يظهر في الملف الشخصي العام
    global_name = target.global_name if target.global_name else "لا يوجد"
    
    # 3. النيك نيم (Server Nickname) - اللقب داخل هذا السيرفر فقط
    server_nick = target.nick if target.nick else "لا يوجد لقب"

    embed = discord.Embed(
        title="🏷️ قائمة الأسماء", 
        description=f"تفاصيل الأسماء لـ: {target.mention}", 
        color=0xff0000
    )
    
    # إضافة الحقول بشكل منفصل وواضح
    embed.add_field(name="Username (الأصلي)", value=f"`{user_name}`", inline=False)
    embed.add_field(name="Display Name (العالمي)", value=f"`{global_name}`", inline=False)
    embed.add_field(name="Server Nickname (اللقب)", value=f"`{server_nick}`", inline=False)
    
    # وضع صورة العضو المصغرة
    embed.set_author(name=target.name, icon_url=target.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

# --- 7. أمر اليوزر (أحمر فاقع) ---
@bot.tree.command(name="user", description="عرض معلومات الحساب")
async def user_info(interaction: discord.Interaction, member: discord.Member = None):
    await interaction.response.defer()
    target = member or interaction.user
    created_ts = int(target.created_at.timestamp())
    joined_ts = int(target.joined_at.timestamp())
    embed = discord.Embed(title=f"👤 معلومات: {target.display_name}", color=0xff0000)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="🗓️ إنشاء الحساب", value=f"<t:{created_ts}:D> (<t:{created_ts}:R>)", inline=False)
    embed.add_field(name="📥 دخول السيرفر", value=f"<t:{joined_ts}:D> (<t:{joined_ts}:R>)", inline=False)
    await interaction.followup.send(embed=embed)

@bot.command()
async def ping(ctx): await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

keep_alive()

# --- أمر الترتيب (TOP 10) المطور ---
@bot.tree.command(name="top", description="عرض ترتيب أفضل 10 أعضاء أو ترتيب عضو معين")
@app_commands.choices(category=[
    app_commands.Choice(name="الرسائل (Text)", value="msg"),
    app_commands.Choice(name="الفويس (Voice)", value="voice")
], timeframe=[
    app_commands.Choice(name="اليوم (Day)", value="day"),
    app_commands.Choice(name="الأسبوع (Week)", value="week"),
    app_commands.Choice(name="الشهر (Month)", value="month"),
    app_commands.Choice(name="الكل (All Time)", value="all")
])
@app_commands.describe(member="العضو الذي تريد رؤية ترتيبه (اختياري)")
async def top(interaction: discord.Interaction, category: str, timeframe: str, member: discord.Member = None):
    await interaction.response.defer()
    gid = str(interaction.guild.id)
    leaderboard = []
    now = datetime.now()

    # 1. تجميع البيانات
    for uid, data in bot.users_data.items():
        if gid in data:
            server_data = data[gid]
            score = 0
            
            if timeframe == "all":
                score = server_data.get("msg_count" if category == "msg" else "voice_seconds", 0)
            else:
                activity_key = "daily_activity" if category == "msg" else "daily_voice"
                if activity_key in server_data:
                    for date_str, val in server_data[activity_key].items():
                        try:
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                            delta_days = (now - date_obj).days
                            if timeframe == "day" and delta_days == 0: score += val
                            elif timeframe == "week" and delta_days <= 7: score += val
                            elif timeframe == "month" and delta_days <= 30: score += val
                        except: continue
            
            if score > 0:
                leaderboard.append({"id": int(uid), "score": score})

    # 2. الترتيب
    leaderboard.sort(key=lambda x: x["score"], reverse=True)

    if not leaderboard:
        return await interaction.followup.send("❌ لا توجد بيانات كافية لهذا التصنيف حالياً.")

    # 3. بناء الإيمبد
    title_map = {"msg": "✉️ تصنيف الرسائل", "voice": "🎙️ تصنيف وقت الفويس"}
    time_map = {"day": "خلال الـ 24 ساعة الماضية", "week": "هذا الأسبوع", "month": "هذا الشهر", "all": "السجل التاريخي الكامل"}
    
    embed = discord.Embed(
        title=title_map[category],
        description=f"📅 الفترة: **{time_map[timeframe]}**",
        color=0xff0000,
        timestamp=datetime.now()
    )

    # حقل ترتيب العضو المختار (إذا تم اختياره)
    if member:
        rank = next((i for i, item in enumerate(leaderboard, 1) if item["id"] == member.id), None)
        if rank:
            s = leaderboard[rank-1]["score"]
            val_text = f"`{s}` رسالة" if category == "msg" else f"`{s//3600}`س و `{(s%3600)//60}`د و `{s%60}`ث"
            embed.add_field(name=f"👤 مركز {member.display_name}", value=f"يحتل المركز **#{rank}** برصيد {val_text}", inline=False)
        else:
            embed.add_field(name=f"👤 مركز {member.display_name}", value="غير متواجد في القائمة لهذه الفترة.", inline=False)

    # قائمة الأعضاء (سواء الـ 10 الأوائل أو سياق العضو)
    description = ""
    for rank, item in display_list:
        # استخدام المنشن المباشر باستخدام ID العضو
        user_mention = f"<@{item['id']}>"
        
        if category == "msg":
            score_text = f"`{item['score']}` رسالة"
        else:
            h, m = item['score'] // 3600, (item['score'] % 3600) // 60
            score_text = f"`{h}`س و `{m}`د"
            
        # تمييز العضو المختار بسهم إذا كان موجوداً
        prefix = "➡️ " if member and item['id'] == member.id else ""
        
        # تنسيق الميداليات للأوائل
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        rank_icon = medals.get(rank, f"`#{rank}`")
        
        # دمج كل المعلومات في سطر واحد باستخدام المنشن
        description += f"{prefix}{rank_icon} {user_mention} — {score_text}\n"

    embed.description = description

    embed.add_field(name="🏆 قائمة الـ 10 الأوائل", value=top_text, inline=False)
    
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)
    
    embed.set_footer(text=f"طلب بواسطة: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
    
    await interaction.followup.send(embed=embed)

# --- أمر مزامنة الرسائل القديمة (للمطور فقط) ---
@bot.tree.command(name="sync_history", description="مزامنة الرسائل القديمة (للمطور فقط)")
@app_commands.describe(limit="عدد الرسائل التي يتم فحصها في كل روم (مثلاً 1000)")
async def sync_history(interaction: discord.Interaction, limit: int = 1000):
    # تحقق أنك المطور فقط من يستخدم الأمر
    if interaction.user.id != 1371432836946726934: 
        return await interaction.response.send_message("❌ هذا الأمر للمطور فقط!", ephemeral=True)

    await interaction.response.defer(ephemeral=True)
    gid = str(interaction.guild.id)
    count = 0

    for channel in interaction.guild.text_channels:
        try:
            async for message in channel.history(limit=limit):
                if message.author.bot: continue
                
                uid = str(message.author.id)
                today = message.created_at.strftime("%Y-%m-%d")
                
                # جلب البيانات وتحديثها
                stats = get_stats(uid, gid)
                stats["msg_count"] += 1
                
                # تحديث النشاط اليومي بناءً على تاريخ الرسالة القديمة
                if "daily_activity" not in stats: stats["daily_activity"] = {}
                stats["daily_activity"][today] = stats["daily_activity"].get(today, 0) + 1
                
                # تحديث الـ XP والمستوى
                if stats["msg_count"] % 25 == 0:
                    stats["xp"] += 1
                    if stats["xp"] >= 20:
                        stats["level"] += 1
                        stats["xp"] = 0
                count += 1
        except Exception as e:
            print(f"تعذر قراءة روم {channel.name}: {e}")

    bot.save_data()
    await interaction.followup.send(f"✅ تمت المزامنة! تم جرد `{count}` رسالة قديمة بنجاح.")

bot.run(os.getenv("DISCORD_TOKEN"))
