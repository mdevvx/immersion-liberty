# import discord
# from discord.ext import commands
# from views.verification_view import VerificationView
# from services.rebalancer import rebalance_guild


# class VerificationCommands(commands.Cog):
#     def __init__(self, bot: commands.Bot):
#         self.bot = bot

#     @discord.app_commands.command(
#         name="send_verification",
#         description="Send a verification button in this channel",
#     )
#     @discord.app_commands.checks.has_permissions(administrator=True)
#     async def send_verification(self, interaction: discord.Interaction):
#         await interaction.channel.send(content="", view=VerificationView())

#         await interaction.response.send_message(
#             "Verification button sent.", ephemeral=True
#         )

#     @discord.app_commands.command(
#         name="rebalance", description="Rebalance group roles for all verified members"
#     )
#     @discord.app_commands.checks.has_permissions(administrator=True)
#     async def rebalance(self, interaction: discord.Interaction):
#         await interaction.response.defer(ephemeral=True)

#         count = await rebalance_guild(interaction.guild)

#         await interaction.followup.send(
#             f"Rebalance complete. {count} members reassigned.", ephemeral=True
#         )


# async def setup(bot):
#     await bot.add_cog(VerificationCommands(bot))


# import discord
# from discord.ext import commands
# from views.verification_view import VerificationView


# class VerificationCommands(commands.Cog):
#     def __init__(self, bot: commands.Bot):
#         self.bot = bot

#     @discord.app_commands.command(
#         name="send_verification", description="Send a customizable verification button"
#     )
#     @discord.app_commands.checks.has_permissions(administrator=True)
#     async def send_verification(
#         self,
#         interaction: discord.Interaction,
#         channel: discord.TextChannel,
#         verified_role: discord.Role,
#         button_label: str = "Verify",
#     ):
#         view = VerificationView(
#             verified_role_id=verified_role.id, button_label=button_label
#         )

#         await channel.send(
#             content="",
#             view=view,
#         )

#         await interaction.response.send_message(
#             f"Verification button sent to {channel.mention}.", ephemeral=True
#         )


# async def setup(bot):
#     await bot.add_cog(VerificationCommands(bot))


# Cliquez sur le bouton ci-dessous pour vérifier votre compte :

import discord
from discord.ext import commands
from views.verification_view import VerificationView


class VerificationCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(
        name="send_verification", description="Send verification button to a channel"
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def send_verification(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        await channel.send("", view=VerificationView())
        await interaction.response.send_message(
            "Verification button sent.", ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(VerificationCommands(bot))
