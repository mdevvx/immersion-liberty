from services.role_balancer import RoleBalancer
from config.settings import VERIFIED_ROLE_ID, GROUP_ROLE_IDS


async def rebalance_guild(guild):
    verified_role = guild.get_role(VERIFIED_ROLE_ID)
    if not verified_role:
        return 0

    balancer = RoleBalancer(guild)
    reassigned = 0

    for member in verified_role.members:
        current_groups = [r for r in member.roles if r.id in GROUP_ROLE_IDS]

        # Remove existing group roles
        if current_groups:
            await member.remove_roles(*current_groups, reason="Rebalancing")

        # Assign new balanced role
        role = balancer.select_group_role()
        if role:
            await member.add_roles(role, reason="Rebalancing")
            reassigned += 1

    return reassigned
