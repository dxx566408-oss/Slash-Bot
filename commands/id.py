import discord
from discord import app_commands
from discord.ext import commands
from utils.settings_logic import load_settings

class IdCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="id", description="عرض معرف الحساب (ID) الخاص بالعضو")
    @app_commands.describe(member="العضو الذي تريد معرفة الآيدي الخاص به")
    async def id_info(self, interaction: discord.Interaction, member: discord.Member = None):
        # 1. التحقق من حالة الأمر (مربوط بمفتاح user في اللوحة)
        settings = load_settings()
        if not settings.get("user", {}).get("enabled", True):
            return await interaction.response.send_message("❌ هذا الأمر معطل حالياً.", ephemeral=True)

        target = member or interaction.user
        
        # 2. بناء إيمبد بسيط وواضح
        embed = discord.Embed(
            description=f"👤 العضو: {target.mention}\n\n🔢 المعرف الخاص به: `{target.id}`",
            color=0xff0000 # اللون الأحمر الخاص ببوتك
        )
        
        # وضع صورة العضو بجانب الآيدي للتوضيح
        embed.set_author(name=f"معلومات معرف: {target.name}", icon_url=target.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(IdCog(bot))
