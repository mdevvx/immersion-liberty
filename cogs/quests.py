import discord
from discord.ext import commands
from services.quest_service import get_quest, save_quest, can_claim, award_points


def build_claim_warning(quest: dict) -> str:
    if quest["tag"] == "obligatoire":
        return "⛔ Vous avez déjà terminé cette quête."
    if quest["tag"] == "journaliere":
        return "⏳ Vous avez déjà terminé cette quête aujourd'hui. Revenez demain !"
    return "⛔ Vous ne pouvez pas accepter cette quête pour le moment."


class Quests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ADMIN COMMAND
    @discord.app_commands.command(
        name="configure_quest",
        description="Configure a quest for this forum post (points, images & reward message)",
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def configure_quest(
        self, interaction, points: int, images_required: int, reward_message: str
    ):
        await interaction.response.send_message("⏳ Configuring quest…", ephemeral=True)

        thread = interaction.channel

        if not isinstance(thread, discord.Thread):
            return await interaction.followup.send(
                "❌ This command must be used inside a quest thread.", ephemeral=True
            )

        if not thread.applied_tags:
            return await interaction.followup.send(
                "❌ Quest must have a tag (Obligatoire or Journaliere).", ephemeral=True
            )

        tag = thread.applied_tags[0].name.lower()
        if tag not in ("obligatoire", "journaliere"):
            return await interaction.followup.send(
                "❌ Invalid quest tag.", ephemeral=True
            )

        save_quest(
            thread.id, thread.parent_id, tag, points, images_required, reward_message
        )

        await interaction.followup.send(
            "✅ Quest configured successfully.", ephemeral=True
        )

    @discord.app_commands.command(name="score", description="Visualisez vos points")
    async def score(self, interaction):
        from services.quest_service import get_user_points

        points = get_user_points(str(interaction.user.id))

        if not points:
            return await interaction.response.send_message(
                "Aucun point pour l'instant.", ephemeral=True
            )

        await interaction.response.send_message(
            f"🏆 **Vos points:** {points}", ephemeral=True
        )

    @discord.app_commands.command(
        name="leaderboard", description="Les 10 meilleurs utilisateurs par points"
    )
    async def leaderboard(self, interaction):
        from services.quest_service import get_leaderboard

        data = get_leaderboard()

        if not data:
            return await interaction.response.send_message(
                "Aucune donnée pour l'instant.", ephemeral=True
            )

        lines = []
        # for i, row in enumerate(data, start=1):
        #     user = interaction.guild.get_member(int(row["discord_id"]))
        #     name = user.display_name if user else "Unknown"
        #     lines.append(f"**{i}.** {name} — {row['points']} pts")

        for i, row in enumerate(data, 1):
            mention = f"<@{row['discord_id']}>"
            lines.append(f"**{i}.** {mention} — {row['points']} pts")

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

        # if not can_claim(str(message.author.id), quest):
        #     await message.add_reaction("⛔")
        #     return

        if not can_claim(str(message.author.id), quest):
            warning_text = build_claim_warning(quest)

            await message.add_reaction("⛔")

            warn_msg = await message.channel.send(
                warning_text, reference=message, mention_author=False
            )

            # Auto-delete warning after 10 seconds (prevents spam)
            await warn_msg.delete(delay=10)
            return

        if len(images) >= quest["images_required"]:
            award_points(str(message.author.id), quest)

            reward_text = (
                quest["reward_message"]
                .replace("{points}", str(quest["points"]))
                .replace("{user}", message.author.mention)
                .replace("{quest}", message.channel.name)
            )

            await message.add_reaction("✅")

            await message.channel.send(
                reward_text, reference=message, mention_author=False
            )

        else:
            await message.add_reaction("📸")


async def setup(bot):
    await bot.add_cog(Quests(bot))
