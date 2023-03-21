import json, os
from discord.ext import commands
import discord
from discord.ext.commands import has_permissions
import yt_dlp as youtube_dl
import asyncio
import shutil

class Crear_Respuesta():
    def __init__(self,title,content):
        self.title = title
        self.content = content
        self.respuesta = discord.Embed(
            title = self.title,
            description = self.content,
            colour = int("DC75FF", 16)
        )
    @property
    def enviar(self):
        return self.respuesta

def main():
    if os.path.exists('config.json'):
        with open('config.json') as f:
            config_data = json.load(f)
    else:
        template = {'prefix':'!', 'token': "", 'palabrasbaneadas': []}
        with open('config.json','w') as f:
            json.dump(template, f)

    palabrasbaneadas = config_data["palabrasbaneadas"]
    prefix = config_data["prefix"]
    token = config_data["token"]
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix = prefix, intents = intents, description = "Bot musica y drogas")
    #Comandos
    
    #musica
    queue = []
    
    # Función para eliminar los archivos mp3 de la ubicación del bot
    async def eliminar_archivos_mp3():
        folder = "./" # Ruta de la carpeta donde se encuentran los archivos mp3
        for filename in os.listdir(folder):
            if filename.endswith(".mp3"):
                file_path = os.path.join(folder, filename)
                try:
                    os.remove(file_path)
                except PermissionError:
                    shutil.rmtree(file_path, ignore_errors=True)
    
    @bot.command(name="play", help="reproduce una canción de YouTube")
    async def play(ctx, url):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            # Si ya está conectado, agrega la canción a la cola y sal del comando
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'outtmpl': '%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }]
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                title = info['title']
                queue.append(f"{title}.mp3")
                await ctx.send(f"{title} agregue tu webada, ya estas feliz? 🙄")
                if len(queue) == 1:
                    voice.play(discord.FFmpegPCMAudio(queue[0]), after=lambda x=None: check_queue(ctx))
            return

        voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='General')
        await voiceChannel.connect()
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info['title']
            queue.append(f"{title}.mp3")
            await ctx.send(f"{title} agregue tu webada, ya estas feliz? 🙄")
            if len(queue) == 1:
                voice.play(discord.FFmpegPCMAudio(queue[0]), after=lambda x=None: asyncio.run(check_queue(ctx)))

    async def check_queue(ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if len(queue) > 0:
            queue.pop(0)
        if len(queue) > 0:
            voice.play(discord.FFmpegPCMAudio(queue[0]), after=lambda x=None: asyncio.run(check_queue(ctx)))
        else:
            await voice.disconnect()
            await eliminar_archivos_mp3() # Eliminar los archivos mp3 de la ubicación del bot

    @bot.command(name="skip", help="salta la canción actual y reproduce la siguiente en la cola")
    async def skip(ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            voice.stop()
            await ctx.send("Salte tu cancion mano, quieres que te llene la cola? ... de musica 🥴")
        else:
            await ctx.send("jsjs no hay nada, parece tus mensajes con ella 🤣")
            await eliminar_archivos_mp3() # Eliminar los archivos mp3 de la ubicación del bot
            
    @bot.command(name="queue", help="musica queue")
    async def queue_command(ctx):
        if len(queue) == 0:
            respuesta = Crear_Respuesta("Lista Pedorra", "No te llene la cola 😩").enviar
        else:
            queue_list = ""
            for i, song in enumerate(queue):
                queue_list += f"{i+1}. {song}\n"
            respuesta = Crear_Respuesta("Lista Pedorra", queue_list).enviar
        await ctx.send(embed=respuesta)


    @bot.command(name="stop", help="musica stop")
    async def stop(ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected() and voice.is_playing():
            voice.stop()
            await voice.disconnect()
            await eliminar_archivos_mp3() # Eliminar los archivos mp3 de la ubicación del bot
    
    @bot.command(name="pause", help="Pausa la música actual")
    async def pause(ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_playing():
            voice.pause()
        else:
            respuesta = Crear_Respuesta("Pause", "que pauseas kgada si no hay nada 🤏👈")
            await ctx.send(embed=respuesta.enviar)

    @bot.command(name="resume", help="Reanuda la música pausada")
    async def resume(ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_paused():
            voice.resume()
        else:
            respuesta = Crear_Respuesta("Resume", "que resumes kgada si no hay nada 🤏👈")
            await ctx.send(embed=respuesta.enviar)
    
    @bot.command(name="nowplaying", help="musica ahora sonando")
    async def nowplaying_command(ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            respuesta = Crear_Respuesta("Now Playing", f"Sonando ahora: {queue[0]['title']}\nDuración: {queue[0]['duration']} 🥳")
            await ctx.send(embed=respuesta.enviar)
        else:
            respuesta = Crear_Respuesta("Now Playing", "jsjs no hay nada, parece tus mensajes con ella 🤣")
            await ctx.send(embed=respuesta.enviar)

    #saludo
    @bot.command(name="saludar", help="El bot te saludara")
    async def saludar(ctx):
        respuesta = Crear_Respuesta(f'Agg, wacala!, no saludo a marrones como tu {ctx.author} 🤢', None)
        await ctx.reply(embed = respuesta.enviar)
        
    #insulto
    @bot.command(name="insultar", help="El bot insulta alguien")
    async def insultar(ctx, *, usuario: discord.Member = None):
        # Si el usuario no se encuentra en la lista, se notifica al usuario
        if usuario is None:
            respuesta = Crear_Respuesta("Me tienes que decir a quien insultar, pe webon 😒.", None)
            await ctx.reply(embed=respuesta.enviar)
            return
        # Si el usuario se encuentra en la lista, se menciona en el mensaje
        respuesta = Crear_Respuesta(f"Ese {usuario} le encanta comer vergas 🤮", None)
        await ctx.reply(embed=respuesta.enviar)
        
    #suma
    @bot.command(name="sumar", help="Se sumar prro")
    async def sumar(ctx, num1:int, num2:int):
        suma = num1 + num2
        respuesta = Crear_Respuesta(f'Se sumar no como tu webon, la respuesta es {suma} 😏', None)
        await ctx.reply(embed = respuesta.enviar)

    

    #permisos
    #banear palabras
    @has_permissions(administrator=True)
    @bot.command(help='Banear palabra del servidor')
    async def banword(ctx, palabra):
        if palabra.lower() in palabrasbaneadas:
            await ctx.send(embed = Crear_Respuesta('Ya esta baneado eso idiota 😡',None).enviar)
        else:
            palabrasbaneadas.append(palabra.lower())
            with open('config.json', 'r+') as f:
                datos = json.load(f)
                datos['palabrasbaneadas'] = palabrasbaneadas
                f.seek(0)
                f.write(json.dumps(datos))
                f.truncate()
            respuesta = Crear_Respuesta('Ya papi nadie lo va a decir 🥶', None)
            await ctx.send(embed = respuesta.enviar)

    #desbanear palabras
    @has_permissions(administrator=True)
    @bot.command(help='Quitar ban a palabra del servidor')
    async def unbanword(ctx, palabra):
        if palabra.lower() in palabrasbaneadas:
            palabrasbaneadas.remove(palabra.lower())
            with open('config.json', 'r+') as f:
                datos = json.load(f)
                datos['palabrasbaneadas'] = palabrasbaneadas
                f.seek(0)
                f.write(json.dumps(datos))
                f.truncate()
            respuesta = Crear_Respuesta('Decidete ps papi no que no querias esta palabra? 🙄', None)
            await ctx.send(embed = respuesta.enviar)
        else:
            respuesta = Crear_Respuesta('Error:', 'No quiero pe ctmr 🤬, na es broma no la veo en mi lista mongolon 🥱')
            await ctx.send(embed = respuesta.enviar)


    #Eventos
    #revisar mensajes general
    @bot.event
    async def on_message(message):
        message_content = message.content.lower()
        message_content = message_content.split(' ')
        for palabrabaneada in palabrasbaneadas:
            if palabrabaneada in message_content:
                respuesta = Crear_Respuesta('Habla bonito mrda o te enfrio! 🩸🗡😠',None)
                await message.reply(embed = respuesta.enviar)
                await message.delete()
                break
        await bot.process_commands(message)
        
    # Evento para recibir a los nuevos miembros
    @bot.event
    async def on_member_join(member):
        # Crea un mensaje de bienvenida para el nuevo miembro
        respuesta = Crear_Respuesta(f'Bienvenido {member.name} a la sala! ... otro pendejo aca 🙄', None)
        canal = bot.get_channel(730200402108088325)
        await canal.send(embed=respuesta.enviar)

    #Estado bot
    @bot.event
    async def on_ready():
        await bot.change_presence(activity=discord.Game(name="Ilusionar a RAMCES"))

    bot.run(token)


if __name__ == '__main__':
    main()
        