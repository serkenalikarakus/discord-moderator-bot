import discord
from discord.ext import commands
import yt_dlp
import asyncio
import logging
from discord import FFmpegPCMAudio


logger = logging.getLogger('bot')

# YoutubeDL configuration
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class Music(commands.Cog):
    """Voice commands for playing music"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_clients = {}

    @commands.command(
        brief="Join a voice channel",
        help="Joins the voice channel you are currently in."
    )
    async def join(self, ctx: commands.Context):
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel first!")
            return
            
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            try:
                await channel.connect()
                logger.info(f'Joined voice channel: {channel.name}')
            except Exception as e:
                logger.error(f'Error joining voice channel: {e}')
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

        async def play_audio(url):
            try:
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
                
                if 'entries' in data:
                    data = data['entries'][0]

                filename = data['url']
                source = await discord.FFmpegOpusAudio.from_probe(filename, **ffmpeg_options)
                ctx.voice_client.play(source)
                
                embed = discord.Embed(
                    title="Now Playing",
                    description=f"🎵 {data['title']}",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
                logger.info(f'Playing audio: {data["title"]}')
                
            except Exception as e:
                logger.error(f'Error playing audio: {e}')
                await ctx.send("An error occurred while trying to play the audio.")

        await play_audio(url)

    @commands.command(
        brief="Leave voice channel",
        help="Disconnects the bot from the current voice channel."
    )
    async def leave(self, ctx: commands.Context):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            logger.info('Left voice channel')
            await ctx.send("👋 Left the voice channel!")
        else:
            await ctx.send("I'm not in a voice channel!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
