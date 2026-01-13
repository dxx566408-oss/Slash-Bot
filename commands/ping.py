import discord
from discord import app_commands
from discord.ext import commands

class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="فحص سرعة استجابة البوت (Latency)")
    async def ping(self, interaction: discord.Interaction):
        # حساب زمن الاستجابة
        latency = round(self.bot.latency * 1000)
        
        # تحديد لون الإيمبد بناءً على السرعة (أخضر إذا سريع، أحمر إذا بطيء)
        color = 0x00ff00 if latency < 150 else 0xff0000
        
        embed = discord.Embed(
            title="🏓 فحص الاتصال",
            description=f"سرعة استجابة البوت هي: **`{latency}ms`**",
            color=color
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(PingCog(bot))
