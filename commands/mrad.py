import discord
from discord import app_commands
from discord.ext import commands
from utils.database_utils import get_stats
from utils.settings_logic import load_settings, DEVELOPER_ID
from utils.formatters import format_number
import math
from utils.captcha import generate_captcha
import asyncio

class MradCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # تعريف مجموعة الأوامر
    mrad_group = app_commands.Group(name="mrad", description="نظام عملة مراد الكامل")

    # --- الأمر الفرعي الأول: الرصيد والتحويل ---
    @mrad_group.command(name="balance", description="عرض الرصيد أو التحويل لعضو")
    @app_commands.describe(member="العضو", amount="المبلغ للتحويل")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None, amount: int = None):
        settings = load_settings()
        if not settings.get("mrad", {}).get("enabled", True):
            return await interaction.response.send_message("❌ نظام مراد معطل حالياً.", ephemeral=True)

        gid = str(interaction.guild.id)

        # 1. إذا كان هناك مبلغ (عملية تحويل)
        if amount is not None:
            if not member:
                return await interaction.response.send_message("❌ يرجى تحديد العضو للتحويل له.", ephemeral=True)
            
            # استثناء المطور (أنت)
            if interaction.user.id == DEVELOPER_ID:
                receiver_stats = get_stats(self.bot.users_data, member.id, gid)
                receiver_stats["mrad"] = receiver_stats.get("mrad", 0) + amount
                self.bot.save_data()
                return await interaction.response.send_message(f"✅ (أمر المطور) تم منح `${format_number(amount)}` إلى {member.name}")

            # قيود المستخدم العادي
            if member.id == interaction.user.id:
                return await interaction.response.send_message("❌ لا يمكنك التحويل لنفسك.", ephemeral=True)
            
            sender_stats = get_stats(self.bot.users_data, interaction.user.id, gid)
            if sender_stats.get("mrad", 0) < amount:
                return await interaction.response.send_message("❌ ليس لديك رصيد كافٍ.", ephemeral=True)

            # نظام الكابتشا
            captcha_text, captcha_file = generate_captcha()
            embed = discord.Embed(title="🛡️ تحقق أمان", description="اكتب الأرقام التي في الصورة لإتمام التحويل:", color=0x2b2d31)
            embed.set_image(url="attachment://captcha.png")
            await interaction.response.send_message(embed=embed, file=captcha_file, ephemeral=True)

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=40.0)
                if msg.content == captcha_text:
                    receiver_stats = get_stats(self.bot.users_data, member.id, gid)
                    sender_stats["mrad"] -= amount
                    receiver_stats["mrad"] = receiver_stats.get("mrad", 0) + amount
                    self.bot.save_data()
                    try: await msg.delete() 
                    except: pass
                    return await interaction.followup.send(f"✅ تم تحويل `${format_number(amount)}` إلى {member.mention} بنجاح!", ephemeral=True)
                else:
                    return await interaction.followup.send("❌ الكود خاطئ. تم إلغاء العملية.", ephemeral=True)
            except asyncio.TimeoutError:
                return await interaction.followup.send("⏳ انتهى الوقت. حاول مجدداً.", ephemeral=True)

        # 2. إذا لم يكن هناك مبلغ (عرض الرصيد فقط)
        target = member or interaction.user
        stats = get_stats(self.bot.users_data, target.id, gid)
        bal = format_number(stats.get("mrad", 0))
        
        if target.id == interaction.user.id:
            msg = f"**ـ {target.name}, رصيد حسابك هو `${bal}`.** | :bank:"
        else:
            msg = f"** رصيد {target.name} هو `${bal}`.** :credit_card:"
        await interaction.response.send_message(content=msg)

    # --- الأمر الفرعي الثاني: المتصدرين ---
    @mrad_group.command(name="top", description="عرض قائمة الأغنياء أو مركز معين")
    @app_commands.describe(rank="عرض مركز معين")
    async def top(self, interaction: discord.Interaction, rank: int = None):
        gid = str(interaction.guild.id)
        
        # إذا طلب مركز محدد
        if rank is not None:
            if rank <= 0: return await interaction.response.send_message("❌ مركز خاطئ.", ephemeral=True)
            all_users = []
            for uid, servers in self.bot.users_data.items():
                if gid in servers and servers[gid].get("mrad", 0) > 0:
                    all_users.append({"id": uid, "balance": servers[gid]["mrad"]})
            all_users.sort(key=lambda x: x["balance"], reverse=True)
            
            if rank > len(all_users):
                return await interaction.response.send_message(f"⚠️ لا يوجد أحد في المركز #{rank}.", ephemeral=True)
            
            user_data = all_users[rank-1]
            embed = discord.Embed(title=f"🏆 المركز #{rank}", color=0xffd700)
            embed.description = f"العضو: <@{user_data['id']}>\n**الرصيد:** `{format_number(user_data['balance'])}` مراد"
            return await interaction.response.send_message(embed=embed)

        # عرض القائمة الكاملة (الصفحة الأولى)
        await self.send_top_page(interaction, 1)

    # دالة مساعدة لإرسال الصفحات
    async def send_top_page(self, interaction, page):
        gid = str(interaction.guild.id)
        all_users = []
        for uid, servers in self.bot.users_data.items():
            if gid in servers and servers[gid].get("mrad", 0) > 0:
                all_users.append((uid, servers[gid]["mrad"]))
        
        all_users.sort(key=lambda x: x[1], reverse=True)
        total_users = len(all_users)
        pages_count = math.ceil(total_users / 10)
        
        start = (page - 1) * 10
        current_list = all_users[start:start+10]

        embed = discord.Embed(title="💰 قائمة أغنياء السيرفر", color=0xff0000)
        desc = "\n".join([f"#{i} | <@{u[0]}> — `{format_number(u[1])}` مراد" for i, u in enumerate(current_list, start=start+1)])
        embed.description = desc or "القائمة فارغة."
        embed.set_footer(text=f"صفحة {page} من {pages_count}")

        view = TopView(self, page, pages_count) if total_users > 10 else None
        
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed, view=view)

# كلاس الأزرار (خارج الكوج)
class TopView(discord.ui.View):
    def __init__(self, cog, current_page, total_pages):
        super().__init__(timeout=60)
        self.cog = cog
        self.current_page = current_page
        self.total_pages = total_pages

    @discord.ui.button(label="الصفحة التالية 🟢", style=discord.ButtonStyle.success)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        next_pg = 1 if self.current_page >= self.total_pages else self.current_page + 1
        await self.cog.send_top_page(interaction, next_pg)

async def setup(bot):
    await bot.add_cog(MradCog(bot))
