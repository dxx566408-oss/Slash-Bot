import discord
from discord import app_commands
from discord.ext import commands

class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # تحويله إلى أمر سلاش (Slash Command)
    @app_commands.command(name="ping", description="فحص سرعة استجابة البوت (Latency)")
    async def ping(self, interaction: discord.Interaction):
        # حساب زمن الاستجابة بالميلي ثانية
        latency = round(self.bot.latency * 1000)
        
        # إرسال الاستجابة
        await interaction.response.send_message(f"🏓 Pong! `{latency}ms`")

async def setup(bot):
    await bot.add_cog(PingCog(bot))
