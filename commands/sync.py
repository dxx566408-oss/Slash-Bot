import discord
from discord import app_commands
from discord.ext import commands
from utils.database_utils import get_stats
from utils.settings_logic import DEVELOPER_ID

class SyncCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sync_server", description="تحديث قاعدة البيانات وجرد أعضاء السيرفر الحالي")
    async def sync_server(self, interaction: discord.Interaction):
        # التحقق من أن المستخدم هو المطور أو لديه صلاحية إدارة السيرفر
        if interaction.user.id != DEVELOPER_ID and not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("❌ هذا الأمر مخصص للإدارة أو المطور فقط.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        new_users = 0
        existing_users = 0

        # جرد جميع الأعضاء
        async for member in guild.fetch_members(limit=None):
            if member.bot:
                continue
            
            uid = str(member.id)
            gid = str(guild.id)
            
            # إذا كان العضو غير موجود في الذاكرة، سيتم إنشاؤه بواسطة get_stats
            if uid not in self.bot.users_data or gid not in self.bot.users_data[uid]:
                get_stats(self.bot.users_data, uid, gid)
                new_users += 1
            else:
                existing_users += 1
        
        # حفظ البيانات بعد الجرد
        self.bot.save_data()
        
        embed = discord.Embed(
            title="🔄 عملية المزامنة",
            description=f"تم فحص أعضاء سيرفر: **{guild.name}**",
            color=0x00ff00
        )
        embed.add_field(name="✅ أعضاء جدد تم تسجيلهم", value=f"`{new_users}`", inline=True)
        embed.add_field(name="📊 أعضاء مسجلين مسبقاً", value=f"`{existing_users}`", inline=True)
        embed.set_footer(text="ملاحظة: البيانات الصوتية والرسائل تبدأ بالحساب من لحظة التواجد.")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SyncCog(bot))
