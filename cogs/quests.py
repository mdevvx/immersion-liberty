import discord
from discord.ext import commands
from services.quest_service import get_quest, save_quest, can_claim, award_points


class Quests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ADMIN COMMAND
    @discord.app_commands.command(name="configure_quest")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def configure_quest(
        self, interaction, points: int, images_required: int, reward_message: str
    ):
        thread = interaction.channel

        if not isinstance(thread, discord.Thread):
            return await interaction.response.send_message(
                "❌ Use this inside a quest thread.", ephemeral=True
            )

        if not thread.applied_tags:
            return await interaction.response.send_message(
                "❌ Quest must have a tag.", ephemeral=True
            )

        tag = thread.applied_tags[0].name.lower()
        if tag not in ("obligatoire", "journaliere"):
            return await interaction.response.send_message(
                "❌ Invalid quest tag.", ephemeral=True
            )

        save_quest(
            thread.id, thread.parent_id, tag, points, images_required, reward_message
        )

        await interaction.response.send_message(
            "✅ Quest configured successfully.", ephemeral=True
        )

    @discord.app_commands.command(name="points", description="View your points")
    async def points(self, interaction):
        from services.quest_service import get_user_points

        points = get_user_points(str(interaction.user.id))

        await interaction.response.send_message(
            f"🏆 **Your Points:** {points}", ephemeral=True
        )

    @discord.app_commands.command(
        name="leaderboard", description="Top 10 users by points"
    )
    async def leaderboard(self, interaction):
        from services.quest_service import get_leaderboard

        data = get_leaderboard()

        if not data:
            return await interaction.response.send_message(
                "No data yet.", ephemeral=True
            )

        lines = []
        for i, row in enumerate(data, start=1):
            user = interaction.guild.get_member(int(row["discord_id"]))
            name = user.display_name if user else "Unknown"
            lines.append(f"**{i}.** {name} — {row['points']} pts")

        embed = discord.Embed(
            title="🏆 Leaderboard",
            description="\n".join(lines),
            color=discord.Color.gold(),
        )

        await interaction.response.send_message(embed=embed)

    # USER IMAGE LISTENER
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not isinstance(message.channel, discord.Thread):
            return

        quest = get_quest(message.channel.id)
        if not quest:
            return

        images = [
            a
            for a in message.attachments
            if a.content_type and a.content_type.startswith("image/")
        ]

        if not images:
            return

        if not can_claim(str(message.author.id), quest):
            await message.add_reaction("⛔")
            return

        if len(images) >= quest["images_required"]:
            award_points(str(message.author.id), quest)
            await message.add_reaction("✅")
            reward_text = (
                quest["reward_message"]
                .replace("{points}", str(quest["points"]))
                .replace("{user}", message.author.mention)
                .replace("{quest}", message.channel.name)
            )

            await message.reply(reward_text, mention_author=False)

        else:
            await message.add_reaction("📸")


async def setup(bot):
    await bot.add_cog(Quests(bot))
