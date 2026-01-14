import discord
from discord import app_commands
from discord.ext import commands
from utils.database_utils import get_stats
from utils.settings_logic import load_settings, DEVELOPER_ID
from utils.formatters import format_number
import math

class MradCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mrad", description="نظام عملة مراد: عرض الرصيد، التحويل، أو المتصدرين")
    @app_commands.describe(
        member="العضو المراد رؤية رصيده أو التحويل له",
        amount="المبلغ المراد تحويله (اتركه فارغاً لرؤية الرصيد فقط)",
        top="عرض قائمة أغنى 10 أعضاء في السيرفر",
        rank="عرض من يحتل مركزاً معيناً (مثلاً: 7)"
    )
    async def mrad(self, interaction: discord.Interaction, 
                   member: discord.Member = None, 
                   amount: int = None, 
                   top: bool = False, 
                   rank: int = None):
        
        settings = load_settings()
        if not settings.get("mrad", {}).get("enabled", True):
            return await interaction.response.send_message("❌ نظام مراد معطل حالياً.", ephemeral=True)

        gid = str(interaction.guild.id)
        
        # --- الحالة الأولى: خيار المركز المحدّد (Rank #) ---
        if rank is not None:
            if rank <= 0: return await interaction.response.send_message("❌ يرجى إدخال مركز صحيح (1 أو أكثر).", ephemeral=True)
            
            # جرد الأعضاء وترتيبهم
            all_users = []
            for uid, servers in self.bot.users_data.items():
                if gid in servers and servers[gid].get("mrad", 0) > 0:
                    all_users.append({"id": uid, "balance": servers[gid]["mrad"]})
            
            all_users.sort(key=lambda x: x["balance"], reverse=True)
            
            # منطق تجميع المراكز (حساب التساوي)
            ranks_map = {}
            current_rank = 0
            last_balance = -1
            
            for user in all_users:
                if user["balance"] != last_balance:
                    current_rank += 1
                last_balance = user["balance"]
                
                if current_rank not in ranks_map: ranks_map[current_rank] = []
                ranks_map[current_rank].append(user)
            
            if rank not in ranks_map:
                return await interaction.response.send_message(f"⚠️ لا يوجد أحد في المركز #{rank} حالياً.", ephemeral=True)
            
            users_in_rank = ranks_map[rank]
            mentions = [f"<@{u['id']}>" for u in users_in_rank]
            balance = format_number(users_in_rank[0]["balance"])
            
            embed = discord.Embed(title=f"🏆 المركز #{rank}", color=0xffd700)
            embed.description = f"الأعضاء في هذا المركز:\n" + "\n".join(mentions) + f"\n\n**الرصيد:** `{balance}` مراد"
            return await interaction.response.send_message(embed=embed)

        # --- الحالة الثانية: خيار قائمة الأغنياء (Top) ---
        if top:
            return await self.send_top_page(interaction, 1)

        # --- الحالة الثالثة: التحويل (Amount) ---
        if amount is not None:
            if not member: return await interaction.response.send_message("❌ يرجى تحديد العضو المراد التحويل له.", ephemeral=True)
            if member.bot: return await interaction.response.send_message("❌ لا يمكنك التحويل للبوتات.", ephemeral=True)
            if member.id == interaction.user.id: return await interaction.response.send_message("❌ لا يمكنك التحويل لنفسك.", ephemeral=True)
            if amount <= 0: return await interaction.response.send_message("❌ المبلغ يجب أن يكون أكبر من 0.", ephemeral=True)

            sender_stats = get_stats(self.bot.users_data, interaction.user.id, gid)
            receiver_stats = get_stats(self.bot.users_data, member.id, gid)

            # استثناء المطور
            if interaction.user.id != DEVELOPER_ID:
                if sender_stats["mrad"] < amount:
                    return await interaction.response.send_message("❌ ليس لديك رصيد كافٍ من مراد.", ephemeral=True)
                
                # هنا سيتم استدعاء الكابتشا لاحقاً
                # حالياً سننفذ العملية مباشرة
                sender_stats["mrad"] -= amount

            receiver_stats["mrad"] += receiver_stats.get("mrad", 0) + amount
            self.bot.save_data()
            
            embed = discord.Embed(description=f"✅ تم تحويل `{format_number(amount)}` مراد إلى {member.mention}", color=0x00ff00)
            return await interaction.response.send_message(embed=embed)

        # --- الحالة الرابعة: رؤية الرصيد (Member) ---
        target = member or interaction.user
        stats = get_stats(self.bot.users_data, target.id, gid)
        balance = format_number(stats.get("mrad", 0))
        
        embed = discord.Embed(color=0xff0000)
        embed.set_author(name=f"رصيد {target.display_name}", icon_url=target.display_avatar.url)
        embed.description = f"💰 لديه: **{balance}** مراد"
        await interaction.response.send_message(embed=embed)

    # دالة مساعدة لإرسال قائمة التوب مع الأزرار
    async def send_top_page(self, interaction, page):
        gid = str(interaction.guild.id)
        all_users = []
        for uid, servers in self.bot.users_data.items():
            if gid in servers and servers[gid].get("mrad", 0) > 0:
                all_users.append((uid, servers[gid]["mrad"]))
        
        all_users.sort(key=lambda x: x[1], reverse=True)
        pages_count = math.ceil(len(all_users) / 10)
        
        start = (page - 1) * 10
        end = start + 10
        current_list = all_users[start:end]

        embed = discord.Embed(title="💰 قائمة أغنياء السيرفر", color=0xff0000)
        desc = ""
        for i, (uid, bal) in enumerate(current_list, start=start+1):
            desc += f"#{i} | <@{uid}> — `{format_number(bal)}` مراد\n"
        
        embed.description = desc if desc else "القائمة فارغة."
        embed.set_footer(text=f"صفحة {page} من {pages_count}")

        # إضافة الزر الأخضر (تقليب الصفحات)
        view = TopView(self, page, pages_count)
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed, view=view)

# كلاس الأزرار لتقليب الصفحات
class TopView(discord.ui.View):
    def __init__(self, cog, current_page, total_pages):
        super().__init__(timeout=60)
        self.cog = cog
        self.current_page = current_page
        self.total_pages = total_pages

    @discord.ui.button(label="الصفحة التالية 🟢", style=discord.ButtonStyle.success)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        next_pg = self.current_page + 1
        if next_pg > self.total_pages: next_pg = 1 # العودة للصفحة الأولى
        await self.cog.send_top_page(interaction, next_pg)

async def setup(bot):
    await bot.add_cog(MradCog(bot))
