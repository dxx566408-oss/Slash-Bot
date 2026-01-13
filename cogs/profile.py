# --- أمر البروفايل المحلي (profile) ---
@bot.tree.command(name="profile", description="عرض مستواك في هذا السيرفر فقط")
async def profile(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    stats = get_stats(target.id, interaction.guild.id)
    embed = discord.Embed(title=f"🏠 ملف {target.display_name} المحلي", color=0xff0000)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="المستوى", value=f"⭐ `{stats['level']}`", inline=True)
    embed.add_field(name="الخبرة", value=f"✨ `{stats['xp']}/20`", inline=True)
    embed.add_field(name="الرسائل", value=f"✉️ `{stats['msg_count']}`", inline=False)
    await interaction.response.send_message(embed=embed)
