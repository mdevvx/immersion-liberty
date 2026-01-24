import random
from discord import Guild, Role
from config.settings import GROUP_ROLE_IDS


class RoleBalancer:
    def __init__(self, guild: Guild):
        self.guild = guild

    def select_group_role(self) -> Role | None:
        roles = [
            self.guild.get_role(role_id)
            for role_id in GROUP_ROLE_IDS
            if self.guild.get_role(role_id)
        ]

        if not roles:
            return None

        role_counts = {role: len(role.members) for role in roles}
        min_count = min(role_counts.values())

        least_populated = [
            role for role, count in role_counts.items() if count == min_count
        ]

        return random.choice(least_populated)
