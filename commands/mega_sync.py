import discord
from discord import app_commands
from discord.ext import commands
from utils.database_utils import get_stats

class MegaSync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sync_all_history", description="جرد تاريخ رسائل السيرفر بالكامل (منذ الإنشاء)")
    @app_commands.checks.has_permissions(administrator=True)
    async def sync_all_history(self, interaction: discord.Interaction):
        # الرد الأولي لأن العملية ستأخذ وقتاً
        await interaction.response.send_message("⚙️ بدأت عملية الجرد الشامل للسيرفر.. قد يستغرق هذا وقتاً طويلاً، سأعلمك عند الانتهاء.")
        
        total_messages = 0
        guild = interaction.guild
        
        # المرور على كل قناة نصية في السيرفر
        for channel in guild.text_channels:
            # التأكد أن البوت يملك صلاحية قراءة الرسائل في القناة
            permissions = channel.permissions_for(guild.me)
            if not permissions.read_message_history or not permissions.read_messages:
                continue
            
            try:
                # قراءة كل الرسائل (limit=None تعني جلب كل شيء)
                async for message in channel.history(limit=None):
                    if not message.author.bot:
                        uid, gid = str(message.author.id), str(guild.id)
                        
                        # جلب بيانات العضو وتحديث الـ ms
                        stats = get_stats(self.bot.users_data, uid, gid)
                        stats["ms"] = stats.get("ms", 0) + 1
                        total_messages += 1
                        
                        # حفظ تلقائي كل 500 رسالة لضمان عدم ضياع البيانات إذا توقف البوت
                        if total_messages % 500 == 0:
                            self.bot.save_data()
                            
            except Exception as e:
                print(f"Error in channel {channel.name}: {e}")
                continue

        # حفظ نهائي
        self.bot.save_data()
        
        # إرسال رسالة نهائية في الشات (ليست ephemeral ليراها الجميع)
        await interaction.channel.send(f"✅ **انتهى الجرد الشامل!**\nتمت قراءة وتوثيق `{total_messages}` رسالة من تاريخ السيرفر وإضافتها لنظام المستويات.")

async def setup(bot):
    await bot.add_cog(MegaSync(bot))
