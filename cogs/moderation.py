from typing import Optional
import discord
from discord.ext import commands
from utils.permissions import has_permission
import logging

logger = logging.getLogger('bot')

class Moderation(commands.Cog):
    """Commands for server moderation"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        brief="Kick a member from the server",
        help="Kicks the specified member from the server. Requires kick permissions."
    )
    @commands.has_permissions(kick_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
        if member.top_role >= ctx.author.top_role:
            await ctx.send("You can't kick someone with a higher or equal role!")
            return

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="Member Kicked",
                description=f"{member.mention} was kicked by {ctx.author.mention}",
                color=discord.Color.red()
            )
            if reason:
                embed.add_field(name="Reason", value=reason)
            await ctx.send(embed=embed)
            logger.info(f'Member {member} was kicked by {ctx.author} for reason: {reason}')
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick this member!")
        except Exception as e:
            logger.error(f'Error kicking member: {e}')
            await ctx.send("An error occurred while trying to kick the member.")

    @commands.command(
        brief="Ban a member from the server",
        help="Bans the specified member from the server. Requires ban permissions."
    )
    @commands.has_permissions(ban_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = None):
        if member.top_role >= ctx.author.top_role:
            await ctx.send("You can't ban someone with a higher or equal role!")
            return

        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="Member Banned",
                description=f"{member.mention} was banned by {ctx.author.mention}",
                color=discord.Color.dark_red()
            )
            if reason:
                embed.add_field(name="Reason", value=reason)
            await ctx.send(embed=embed)
            logger.info(f'Member {member} was banned by {ctx.author} for reason: {reason}')
        except discord.Forbidden:
            await ctx.send("I don't have permission to ban this member!")
        except Exception as e:
            logger.error(f'Error banning member: {e}')
            await ctx.send("An error occurred while trying to ban the member.")

    @commands.command(
        brief="Add a role to a member",
        help="Adds the specified role to the specified member. Requires manage roles permission."
    )
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def addrole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        if role >= ctx.author.top_role:
            await ctx.send("You can't add a role that is higher or equal to your highest role!")
            return

        try:
            await member.add_roles(role)
            embed = discord.Embed(
                title="Role Added",
                description=f"Added {role.mention} to {member.mention}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            logger.info(f'Role {role} added to {member} by {ctx.author}')
        except discord.Forbidden:
            await ctx.send("I don't have permission to manage roles!")
        except Exception as e:
            logger.error(f'Error adding role: {e}')
            await ctx.send("An error occurred while trying to add the role.")

    @commands.command(
        brief="Remove a role from a member",
        help="Removes the specified role from the specified member. Requires manage roles permission."
    )
    @commands.has_permissions(manage_roles=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def removerole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        if role >= ctx.author.top_role:
            await ctx.send("You can't remove a role that is higher or equal to your highest role!")
            return

        try:
            await member.remove_roles(role)
            embed = discord.Embed(
                title="Role Removed",
                description=f"Removed {role.mention} from {member.mention}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            logger.info(f'Role {role} removed from {member} by {ctx.author}')
        except discord.Forbidden:
            await ctx.send("I don't have permission to manage roles!")
        except Exception as e:
            logger.error(f'Error removing role: {e}')
            await ctx.send("An error occurred while trying to remove the role.")

    @commands.command(
        brief="Change a member's nickname",
        help="Changes the specified member's nickname. Requires manage nicknames permission."
    )
    @commands.has_permissions(manage_nicknames=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def nickname(self, ctx: commands.Context, member: discord.Member, *, new_nickname: Optional[str] = None):
        if member.top_role >= ctx.author.top_role:
            await ctx.send("You can't change the nickname of someone with a higher or equal role!")
            return

        try:
            await member.edit(nick=new_nickname)
            embed = discord.Embed(
                title="Nickname Changed",
                description=f"Changed {member.mention}'s nickname to: {new_nickname if new_nickname else 'Default'}",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            logger.info(f'Nickname for {member} was changed to {new_nickname} by {ctx.author}')
        except discord.Forbidden:
            await ctx.send("I don't have permission to change nicknames!")
        except Exception as e:
            logger.error(f'Error changing nickname: {e}')
            await ctx.send("An error occurred while trying to change the nickname.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))