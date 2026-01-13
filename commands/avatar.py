import discord
from discord import app_commands
from discord.ext import commands

class AvatarCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="عرض الصورة الشخصية لك أو لعضو آخر")
    @app_commands.describe(member="العضو الذي تريد رؤية صورته")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        # إذا لم يتم اختيار عضو، نعرض صورة الشخص الذي استخدم الأمر
        target = member or interaction.user
        
        # إنشاء الـ Embed لعرض الصورة بشكل احترافي
        embed = discord.Embed(
            title=f"🖼️ صورة {target.display_name}",
            color=0xff0000 # اللون الأحمر الذي تفضله
        )
        
        # وضع رابط الصورة في الـ Embed
        embed.set_image(url=target.display_avatar.url)
        
        # إضافة روابط لتحميل الصورة بجودات مختلفة (اختياري)
        embed.description = f"[رابط مباشر للتحميل]({target.display_avatar.url})"
        
        await interaction.response.send_message(embed=embed)

# دالة الربط مع الملف الأساسي
async def setup(bot):
    await bot.add_cog(AvatarCog(bot))
