import discord
from discord.ext import commands
from services.role_balancer import RoleBalancer
from config.settings import VERIFIED_ROLE_ID, GROUP_ROLE_IDS


class MemberEvents(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        verified_role = after.guild.get_role(VERIFIED_ROLE_ID)
        if not verified_role:
            return

        # Verified role just added
        if verified_role not in before.roles and verified_role in after.roles:
            # Check if already has a group role
            if any(role.id in GROUP_ROLE_IDS for role in after.roles):
                return

            balancer = RoleBalancer(after.guild)
            group_role = balancer.select_group_role()

            if group_role:
                await after.add_roles(
                    group_role, reason="Auto group assignment after verification"
                )


async def setup(bot):
    await bot.add_cog(MemberEvents(bot))
