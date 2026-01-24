# import discord
# from services.role_balancer import RoleBalancer
# from config.settings import VERIFIED_ROLE_ID


# class VerificationView(discord.ui.View):
#     def __init__(self):
#         super().__init__(timeout=None)

#     @discord.ui.button(
#         label="Clique ici !",
#         style=discord.ButtonStyle.success,
#         custom_id="verify_button",
#     )
#     async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
#         member = interaction.user
#         guild = interaction.guild

#         verified_role = guild.get_role(VERIFIED_ROLE_ID)
#         if not verified_role:
#             await interaction.response.send_message(
#                 "Verification role not found", ephemeral=True
#             )
#             return

#         if verified_role in member.roles:
#             await interaction.response.send_message(
#                 "You are already verified", ephemeral=True
#             )
#             return

#         await member.add_roles(verified_role, reason="User verified")

#         # Rate-limit protection
#         if interaction.client.join_limiter.record_join():
#             balancer = RoleBalancer(guild)
#             group_role = balancer.select_group_role()

#             if group_role:
#                 await member.add_roles(group_role, reason="Balanced group assignment")

#             await interaction.response.send_message(
#                 "You are verified and assigned to a group.",
#                 ephemeral=True,
#             )
#         else:
#             await interaction.response.send_message(
#                 "You are verified. Group assignment will be completed shortly.",
#                 ephemeral=True,
#             )


# import discord
# from services.role_balancer import RoleBalancer
# from services.google_sheets import save_user


# class VerificationView(discord.ui.View):
#     def __init__(self, verified_role_id: int, button_label: str):
#         super().__init__(timeout=None)
#         self.verified_role_id = verified_role_id

#         self.add_item(
#             VerificationButton(verified_role_id=verified_role_id, label=button_label)
#         )


# class VerificationButton(discord.ui.Button):
#     def __init__(self, verified_role_id: int, label: str):
#         super().__init__(
#             label=label,
#             style=discord.ButtonStyle.success,
#             custom_id=f"verify:{verified_role_id}",
#         )
#         self.verified_role_id = verified_role_id

#     async def callback(self, interaction: discord.Interaction):
#         member = interaction.user
#         guild = interaction.guild

#         verified_role = guild.get_role(self.verified_role_id)
#         if not verified_role:
#             await interaction.response.send_message(
#                 "Rôle de vérification introuvable.", ephemeral=True
#             )
#             return

#         if verified_role in member.roles:
#             await interaction.response.send_message(
#                 "Vous êtes déjà vérifié.", ephemeral=True
#             )
#             return

#         await member.add_roles(verified_role, reason="User verified")

#         # Balanced group assignment (rate-limited)
#         if interaction.client.join_limiter.record_join():
#             balancer = RoleBalancer(guild)
#             group_role = balancer.select_group_role()
#             if group_role:
#                 await member.add_roles(group_role, reason="Balanced group assignment")

#             await interaction.response.send_message(
#                 "Votre compte a été vérifié et vous avez été affecté à un groupe.",
#                 ephemeral=True,
#             )
#         else:
#             await interaction.response.send_message(
#                 "Votre inscription est validée. "
#                 "L'affectation au groupe sera effectuée sous peu.",
#                 ephemeral=True,
#             )

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
            "⏳ Processing your verification…", ephemeral=True
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
                "❌ Verification failed. Please contact an administrator.",
                ephemeral=True,
            )
            raise

        await interaction.followup.send(
            "✅ Verification complete. Welcome to the community.",
            ephemeral=True,
        )


class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Verify Here !",
        style=discord.ButtonStyle.success,
        custom_id="verify_modal_button",
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        guild = interaction.guild

        verified_role = guild.get_role(VERIFIED_ROLE_ID)
        if not verified_role:
            await interaction.response.send_message(
                "❌ Verification role is not configured. Please contact an administrator.",
                ephemeral=True,
            )
            return

        # ✅ Already verified → block modal
        if verified_role in member.roles:
            await interaction.response.send_message(
                "✅ You are already verified. No further action is required.",
                ephemeral=True,
            )
            return

        # ❌ Not verified → open modal
        await interaction.response.send_modal(VerificationModal())
