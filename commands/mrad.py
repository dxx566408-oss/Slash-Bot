import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio

# الاستيراد الصحيح من المجلدات التي أنشأناها
from utils.database_utils import get_stats
from utils.captcha import create_captcha_image
from utils.settings_logic import DEVELOPER_ID

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mrad", description="عرض أو تحويل رصيد مراد")
    @app_commands.describe(user="العضو المراد التحويل له أو رؤية رصيده", amount="المبلغ المراد تحويله")
    async def mrad(self, interaction: discord.Interaction, user: discord.Member = None, amount: int = None):
        
        # الحالة 1: عرض الرصيد فقط (إذا لم يتم إدخال مبلغ)
        if amount is None:
            target = user or interaction.user
            stats = get_stats(self.bot.users_data, target.id)
            embed = discord.Embed(
                description=f"💰 رصيد **{target.mention}** هو: `{stats.get('mrad', 0)}` مراد", 
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed)

        # الحالة 2: عملية التحويل
        sender_id = interaction.user.id
        receiver_id = user.id
        
        # جلب بيانات المرسل والمستقبل بشكل صحيح
        sender_stats = get_stats(self.bot.users_data, sender_id)
        receiver_stats = get_stats(self.bot.users_data, receiver_id, interaction.guild.id)

        # --- التحقق من القوانين ---
        if sender_id == receiver_id:
            if sender_id == DEVELOPER_ID: # المطور يشحن لنفسه
                receiver_stats["mrad"] += amount
                self.bot.save_data()
                return await interaction.response.send_message(f"✅ تم إضافة `{amount}` لرصيدك يا مطور!")
            return await interaction.response.send_message("❌ لا يمكنك التحويل لنفسك!", ephemeral=True)

        if sender_id != DEVELOPER_ID and sender_stats.get("mrad", 0) < amount:
            return await interaction.response.send_message("❌ رصيدك لا يكفي لإتمام هذه العملية!", ephemeral=True)

        if amount <= 0:
            return await interaction.response.send_message("❌ عفواً، المبلغ يجب أن يكون أكبر من صفر!", ephemeral=True)

        # --- نظام الكابتشا ---
        captcha_text = str(random.randint(1111, 9999))
        captcha_buffer = create_captcha_image(captcha_text)
        captcha_file = discord.File(captcha_buffer, filename="captcha.png")

        embed_v = discord.Embed(
            title="🛡️ تأكيد التحويل (نظام الحماية)", 
            description=f"لإتمام تحويل `{amount}` إلى {user.mention}، يرجى كتابة الرقم الظاهر في الصورة أدناه:", 
            color=0xff0000
        )
        embed_v.set_image(url="attachment://captcha.png")

        await interaction.response.send_message(file=captcha_file, embed=embed_v)

        # --- انتظار الرد من المستخدم ---
        def check(m): 
            return m.author == interaction.user and m.channel == interaction.channel
        
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            if msg.content == captcha_text:
                try: await msg.delete() # حذف رسالة المستخدم للتنظيف
                except: pass

                # تنفيذ عملية الخصم والإضافة
                if sender_id != DEVELOPER_ID:
                    sender_stats["mrad"] -= amount
                
                receiver_stats["mrad"] += amount
                self.bot.save_data()
                
                await interaction.followup.send(f"✅ تم تحويل `{amount}` إلى {user.mention} بنجاح! \nرصيدك الحالي: `{sender_stats.get('mrad', 0)}`")
            else:
                await interaction.followup.send("❌ رقم الكابتشا خاطئ، تم إلغاء العملية.")
        except asyncio.TimeoutError:
            await interaction.followup.send("⏳ انتهى وقت التحقق (30 ثانية). يرجى المحاولة مرة أخرى.")

async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
