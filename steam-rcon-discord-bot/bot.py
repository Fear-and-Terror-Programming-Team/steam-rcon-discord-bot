#!/usr/bin/env python3

import asyncio
import config
import discord
from srcds.rcon import RconConnection
from discord.ext import commands


bot = commands.Bot(command_prefix=config.BOT_CMD_PREFIX)


class PermissionDeniedError(commands.CommandError):
    pass


def rcon_command(*args, **kwargs):
    '''
    Decorator handling @bot.command, role checks and channel checks.

    Use it as you would use @bot.command.
    '''
    discord_wrapper = bot.command(*args, **kwargs)
    def decorator(func):
        func = discord_wrapper(func)
        def wrapper(ctx, *args, **kwargs):
            if ctx.channel.id != config.RCON_CHANNEL:
                return
            if config.ADMIN_ROLE not in [r.id for r in ctx.author.roles]:
                raise PermissionDeniedError

            return func(ctx, *args, **kwargs)
        return wrapper
    return decorator


@bot.event
async def on_ready():
    config.init_config(bot)
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


async def execute_command(ctx, command):
    conn = RconConnection(config.HOST,
            port=config.PORT, password=config.PASSWORD)
    response = conn.exec_command(command)
    if len(response) == 0:
        response = "(no output)"
    await ctx.send(f""
            f"**Command executed**\n"
            f"{ctx.author.mention}\n"
            f"> {command}\n"
            f"```\n"
            f"{response}"
            f"```")


@rcon_command(aliases=["r"])
async def rcon(ctx, *, command):
    await execute_command(ctx, command)


@rcon_command(aliases=["aldp"])
async def adminlistdisconnectedplayers(ctx):
    await execute_command(ctx, "AdminListDisconnectedPlayers")


# TODO error handling
# - permission denied error
# - server is down / unresponsive (probably via timeouts)


if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
