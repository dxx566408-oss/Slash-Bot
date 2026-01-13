import discord
from discord import app_commands
from discord.ext import commands
from utils.settings_logic import load_settings # للربط بلوحة التحكم

class IdCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="id", description="عرض معرف الحساب (ID) ومعلومات سريعة")
    @app_commands.describe(member="العضو الذي تريد معرفة الآيدي الخاص به")
    async def id_info(self, interaction: discord.Interaction, member: discord.Member = None):
        # 1. التحقق من حالة الأمر في لوحة التحكم (اختياري لكن يفضل لتوحيد النظام)
        settings = load_settings()
        if not settings.get("user", {}).get("enabled", True): # نستخدم مفتاح 'user' الموجود في الإعدادات الافتراضية
            return await interaction.response.send_message("❌ هذا الأمر معطل حالياً من لوحة التحكم.", ephemeral=True)

        target = member or interaction.user
        
        # 2. بناء الإيمبد بتصميم أنيق
        embed = discord.Embed(
            title="🆔 بطاقة تعريف المستخدم", 
            color=0xff0000,
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # معلومات الحساب
        embed.add_field(name="👤 الاسم المستعار", value=target.mention, inline=True)
        embed.add_field(name="🔢 المعرف (ID)", value=f"`{target.id}`", inline=True)
        
        # تواريخ مهمة
        created_at = target.created_at.strftime("%Y/%m/%d")
        joined_at = target.joined_at.strftime("%Y/%m/%d") if target.joined_at else "غير متاح"
        
        embed.add_field(name="🗓️ إنشاء الحساب", value=f"`{created_at}`", inline=True)
        embed.add_field(name="📥 انضم للسيرفر", value=f"`{joined_at}`", inline=True)
        
        # تذييل الإيمبد
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(IdCog(bot))
