import discord
from discord import app_commands
from discord.ext import commands
from utils.settings_logic import load_settings # أضفنا هذا السطر للربط باللوحة

class AvatarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="عرض الصورة الشخصية لك أو لعضو آخر")
    @app_commands.describe(member="العضو الذي تريد رؤية صورته")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        # --- التحقق من لوحة التحكم ---
        settings = load_settings()
        if not settings.get("avatar", {}).get("enabled", True):
            return await interaction.response.send_message("❌ هذا الأمر معطل حالياً من قبل الإدارة.", ephemeral=True)
        # ---------------------------

        target = member or interaction.user
        
        embed = discord.Embed(
            title=f"🖼️ صورة {target.display_name}",
            description=f"🔗 [رابط مباشر للتحميل]({target.display_avatar.url})",
            color=0xff0000 
        )
        
        embed.set_image(url=target.display_avatar.url)
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(AvatarCog(bot))
