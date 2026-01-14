import discord
from discord import app_commands
from discord.ext import commands
from utils.database_utils import get_stats

class LevelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # دالة الحسبة (المحرك الرياضي)
    def calculate_stats(self, ms, vs):
        # --- الحسبة الكتابية ---
        t_xp = ms // 25
        t_ms_prog = ms % 25
        t_lvl = t_xp // 20
        t_xp_prog = t_xp % 20

        # --- الحسبة الصوتية ---
        vm_total = vs // 60
        v_xp = vm_total // 5
        v_vm_prog = vm_total % 5
        v_lvl = v_xp // 20
        v_xp_prog = v_xp % 20
        
        # تحويل الثواني للعرض النصي vt total
        h = vs // 3600
        m = (vs % 3600) // 60
        s = vs % 60
        vt_display = f"{h} ساعة و {m} دقيقة و {s} ثانية"

        # --- الحسبة العامة ---
        total_xp = t_xp + v_xp
        gen_lvl = total_xp // 20
        gen_xp_prog = total_xp % 20

        return {
            "text": {"lvl": t_lvl, "xp_0_20": t_xp_prog, "xp_total": t_xp, "ms_0_25": t_ms_prog, "ms_total": ms},
            "voice": {"lvl": v_lvl, "xp_0_20": v_xp_prog, "xp_total": v_xp, "vm_0_5": v_vm_prog, "vt_total": vt_display},
            "gen": {"lvl": gen_lvl, "xp_0_20": gen_xp_prog, "xp_total": total_xp}
        }

    @app_commands.command(name="level", description="عرض مستوياتك (عام، كتابي، صوتي)")
    @app_commands.describe(member="العضو المراد رؤية مستواه")
    async def level(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        gid = str(interaction.guild.id)
        
        # جلب البيانات من الداتابيز (العقل)
        stats_data = get_stats(self.bot.users_data, target.id, gid)
        
        # تنفيذ الحسبة
        res = self.calculate_stats(stats_data.get("ms", 0), stats_data.get("vs", 0))
        
        # إنشاء الإمبيد
        embed = discord.Embed(title=f"📊 إحصائيات المستوى: {target.display_name}", color=0x3498db)
        
        # 1. قسم لفل الكتابي
        t = res["text"]
        embed.add_field(name="📝 Level Text", value=(
            f"**lvl:** `{t['lvl']}`\n"
            f"**xp:** `{t['xp_0_20']}/20`\n"
            f"**xp total:** `{t['xp_total']}`\n"
            f"**ms:** `{t['ms_0_25']}/25`\n"
            f"**ms total:** `{t['ms_total']}`"
        ), inline=True)

        # 2. قسم لفل الصوتي
        v = res["voice"]
        embed.add_field(name="🎙️ Level Voice", value=(
            f"**lvl:** `{v['lvl']}`\n"
            f"**xp:** `{v['xp_0_20']}/20`\n"
            f"**xp total:** `{v['xp_total']}`\n"
            f"**vm:** `{v['vm_0_5']}/5`\n"
            f"**vt total:** `{v['vt_total']}`"
        ), inline=True)

        # 3. قسم اللفل العام (General)
        g = res["gen"]
        embed.add_field(name="🌟 Level General", value=(
            f"**lvl:** `{g['lvl']}`\n"
            f"**xp:** `{g['xp_0_20']}/20`\n"
            f"**xp total:** `{g['xp_total']}`"
        ), inline=False)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LevelCog(bot))
