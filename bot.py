import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from views.verification_view import VerificationView
from services.join_rate_limiter import JoinRateLimiter


load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class MyBot(commands.Bot):
    async def setup_hook(self):

        self.join_limiter = JoinRateLimiter()
        # Dummy registration for persistence routing
        self.add_view(VerificationView())

        # Load cogs here
        await self.load_extension("cogs.verification_commands")
        await self.load_extension("cogs.member_events")
        await self.load_extension("cogs.quests")

        # Sync slash commands
        await self.tree.sync()


bot = MyBot(command_prefix=None, intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")


import time

while True:
    try:
        bot.run(os.getenv("DISCORD_TOKEN"))
    except Exception as e:
        print("Bot crashed:", e)
        time.sleep(60)  # wait 60 seconds before retry
