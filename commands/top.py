import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from utils.settings_logic import load_settings
from utils.formatters import format_time, format_number

class TopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="top", description="عرض قوائم المتصدرين في التفاعل (كتابي/صوتي)")
    @app_commands.choices(type=[
        app_commands.Choice(name="رسائل (كتابي)", value="msg"),
        app_commands.Choice(name="ساعات (صوتي)", value="voice")
    ], period=[
        app_commands.Choice(name="اليوم", value="today"),
        app_commands.Choice(name="الأسبوع", value="week"),
        app_commands.Choice(name="الشهر", value="month"),
        app_commands.Choice(name="كلي (منذ البداية)", value="all")
    ])
    async def top(self, interaction: discord.Interaction, type: str, period: str):
        # 1. التحقق من لوحة التحكم
        settings = load_settings()
        if not settings.get("profile", {}).get("enabled", True):
            return await interaction.response.send_message("❌ هذا النظام معطل حالياً.", ephemeral=True)

        await interaction.response.defer()
        
        guild = interaction.guild
        leaderboard = []
        today_date = datetime.now().strftime("%Y-%m-%d")

        # 2. تجميع البيانات ومعالجتها
        for uid, servers in self.bot.users_data.items():
            if str(guild.id) in servers:
                stats = servers[str(guild.id)]
                value = 0
                
                if period == "all":
                    value = stats.get("msg_count" if type == "msg" else "voice_seconds", 0)
                else:
                    # حساب الفترة الزمنية (يوم، أسبوع، شهر)
                    activity_dict = stats.get("daily_activity" if type == "msg" else "daily_voice", {})
                    days_to_check = 1 if period == "today" else (7 if period == "week" else 30)
                    
                    for i in range(days_to_check):
                        date_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                        value += activity_dict.get(date_str, 0)

                if value > 0:
                    member = guild.get_member(int(uid))
                    name = member.display_name if member else f"مستخدم غادر ({uid})"
                    leaderboard.append((name, value, int(uid)))

        # 3. فرز المتصدرين (من الأعلى للأقل)
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        top_10 = leaderboard[:10]

        # 4. بناء الإيمبد
        title_type = "الرسائل 💬" if type == "msg" else "الوقت الصوتي 🎙️"
        title_period = {"today": "اليوم", "week": "هذا الأسبوع", "month": "هذا الشهر", "all": "الكل"}[period]
        
        embed = discord.Embed(
            title=f"🏆 متصدري {title_type} - {title_period}",
            color=0xff0000,
            timestamp=discord.utils.utcnow()
        )

        description = ""
        user_rank = "غير مدرج"
        
        for index, (name, val, uid) in enumerate(leaderboard):
            formatted_val = format_number(val) if type == "msg" else format_time(val)
            
            # عرض أول 10 فقط في القائمة
            if index < 10:
                medal = "🥇" if index == 0 else ("🥈" if index == 1 else ("🥉" if index == 2 else f"`#{index+1}`"))
                description += f"{medal} **{name}** — {formatted_val}\n"
            
            # معرفة ترتيب الشخص الذي استدعى الأمر
            if uid == interaction.user.id:
                user_rank = f"#{index + 1}"

        embed.description = description if description else "لا توجد بيانات لهذه الفترة بعد."
        embed.set_footer(text=f"ترتيبك الحالي: {user_rank} | سيرفر {guild.name}")
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(TopCog(bot))
