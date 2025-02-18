import discord
import os
from discord.ext import commands
import yt_dlp
import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get ffmpeg path from .env
ffmpeg_path = os.getenv("FFMPEG_PATH")

# Add ffmpeg path to the system PATH
if ffmpeg_path:
    os.environ["PATH"] += os.pathsep + ffmpeg_path
else:
    print("⚠️ FFMPEG_PATH not found in .env file. Make sure it's set correctly.")

logger = logging.getLogger("bot")

# Discord bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# YouTubeDL configuration
ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'auto',
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class Music(commands.Cog):
    """Voice commands for playing music"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        brief="Join a voice channel",
        help="Joins the voice channel you are currently in."
    )
    async def join(self, ctx: commands.Context):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("You need to be in a voice channel first!")
            return
            
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            try:
                await channel.connect()
                logger.info(f"Joined voice channel: {channel.name}")
            except Exception as e:
                logger.error(f"Error joining voice channel: {e}")
                await ctx.send("Couldn't join the voice channel.")

    @commands.command(
        brief="Play audio from URL",
        help="Plays audio from a given URL (YouTube, etc.). Usage: !play <url>"
    )
    async def play(self, ctx: commands.Context, *, url: str):
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        if not ctx.voice_client:
            return

        await ctx.send("🔍 Fetching audio...")

        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

            if 'entries' in data:
                data = data['entries'][0]  # Get first result if it's a playlist

            audio_url = data['url']
            source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
            ctx.voice_client.stop()  # Stop any currently playing audio
            ctx.voice_client.play(source, after=lambda e: logger.error(f"Player error: {e}") if e else None)

            embed = discord.Embed(
                title="Now Playing 🎶",
                description=f"[{data['title']}]({url})",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=data.get("thumbnail", ""))
            await ctx.send(embed=embed)

        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            await ctx.send("❌ An error occurred while trying to play the audio.")

    @commands.command(
        brief="Leave voice channel",
        help="Disconnects the bot from the current voice channel."
    )
    async def leave(self, ctx: commands.Context):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            logger.info("Left voice channel")
            await ctx.send("👋 Left the voice channel!")
        else:
            await ctx.send("I'm not in a voice channel!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
