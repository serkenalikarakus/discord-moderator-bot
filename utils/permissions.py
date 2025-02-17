from typing import Callable, Any
from discord.ext import commands

def has_permission(permission: str) -> Callable[[commands.Context], bool]:
    """Check if user has the required permission"""
    async def predicate(ctx: commands.Context) -> bool:
        return getattr(ctx.author.guild_permissions, permission, False)
    return commands.check(predicate)