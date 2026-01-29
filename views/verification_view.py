import discord
from services.role_balancer import RoleBalancer
from services.google_sheets import save_user
from config.settings import VERIFIED_ROLE_ID
from config.settings import GROUP_ROLE_IDS


class VerificationModal(discord.ui.Modal, title="Verification"):
    first_name = discord.ui.TextInput(label="First Name")
    last_name = discord.ui.TextInput(label="Last Name")
    email = discord.ui.TextInput(label="Email", placeholder="name@email.com")

    async def on_submit(self, interaction: discord.Interaction):
        # await interaction.response.defer(ephemeral=True)

        await interaction.response.send_message(
            "⏳ Traitement de votre vérification…", ephemeral=True
        )

        try:
            member = interaction.user
            guild = interaction.guild

            # Save to Google Sheets
            # save_user(
            #     member,
            #     self.first_name.value.strip(),
            #     self.last_name.value.strip(),
            #     self.email.value.strip(),
            # )
            import asyncio

            await asyncio.to_thread(
                save_user,
                member,
                self.first_name.value.strip(),
                self.last_name.value.strip(),
                self.email.value.strip(),
            )

            # Add verified role
            visionnaires = guild.get_role(VERIFIED_ROLE_ID)
            if visionnaires:
                await member.add_roles(visionnaires, reason="Verified")

            # Enforce exactly ONE group role
            # if interaction.client.join_limiter.record_join():
            #     balancer = RoleBalancer(guild)
            #     group_role = balancer.select_group_role()

            #     if group_role:
            #         existing_groups = [
            #             role for role in member.roles if role.id in GROUP_ROLE_IDS
            #         ]

            #         if existing_groups:
            #             await member.remove_roles(
            #                 *existing_groups, reason="Ensuring single group role"
            #             )

            #         await member.add_roles(
            #             group_role, reason="Balanced group assignment"
            #         )

        except Exception as e:
            print("DEPLOY ERROR:", repr(e))
            import traceback

            traceback.print_exc()
            await interaction.followup.send(
                "❌ La vérification a échoué. Veuillez contacter un administrateur.",
                ephemeral=True,
            )
            raise

        await interaction.followup.send(
            "✅ Vérification terminée. Bienvenue dans la communauté.",
            ephemeral=True,
        )


class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        # label="Clique ici !",
        label=" 👉 Clique ici pour démarrer",
        style=discord.ButtonStyle.success,
        custom_id="verify_modal_button",
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        guild = interaction.guild

        verified_role = guild.get_role(VERIFIED_ROLE_ID)
        if not verified_role:
            await interaction.response.send_message(
                "❌ Le rôle de vérification n'est pas configuré. Veuillez contacter un administrateur.",
                ephemeral=True,
            )
            return

        # ✅ Already verified → block modal
        if verified_role in member.roles:
            await interaction.response.send_message(
                "✅ Votre compte est déjà vérifié. Aucune autre action n'est requise.",
                ephemeral=True,
            )
            return

        # ❌ Not verified → open modal
        await interaction.response.send_modal(VerificationModal())
