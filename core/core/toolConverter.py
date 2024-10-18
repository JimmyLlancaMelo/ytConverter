import yt_dlp
import re, os, uuid

class toolVideo:
    
    def __init__(self, url):
        self.url = url
        self.listaVideo = []
        self.listaAudio = []
        self.nameFile = ""

    def Quality(self):
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(self.url, download=False) # SE OBTIENE LA INFORMACION EN UN DICCIONARIO

            for i in info['formats']: # SE OBTIENEN VARIOS FORMATOS - formad_id, url, ext, acodec, vcodec, filesize, abr, etc

                self.listaVideo.append(i.get("height","desconocido")) # OPTENER CALIDAD DE 1080p 720p 480p 360p 240p
                self.listaAudio.append(i.get("abr","desconocido")) # OBTENER CALIDAD DE 320kbs 192kbs 128kbs
                
            # QUITAR DUPLICADOS
            self.listaVideo = list(set(self.listaVideo))
            self.listaAudio = list(set(self.listaAudio))

            # DEJAR NUMEROS Y DECIMALES
            self.listaVideo = list(i for i in self.listaVideo if isinstance(i,int))
            self.listaAudio = list(i for i in self.listaAudio if isinstance(i,float))
            
            # ORDENAR
            self.listaVideo.sort(reverse=True) # DE MAYOR A MENOR
            self.listaAudio.sort(reverse=True)
            
            # FILTRAR
            self.listaVideo = [i for i in self.listaVideo if i > 100] # ELIMINAMOS ELEMENTOS MENORES A 100
            del self.listaAudio[3:len(self.listaAudio)] # ELIMINAMOS ELEMENTOS A PARTIR DEL INDICE 3 EN ADELANTE
            self.listaAudio[:3] = [320,192,128] # REEMPLAZAMOS LOS ELEMENTOS
            
            print(self.listaVideo)
            print(self.listaAudio)

    def Download(self, formato, quality, progress_callback=None):
        ruta_base = os.path.dirname(os.path.abspath(__file__))
        ruta_ffmpeg = os.path.join(ruta_base, '..', 'bin', 'ffmpeg', 'bin', 'ffmpeg.exe')

        ydl_opts = {
            'outtmpl': f'media/fileYoutube/{self.nameFile}.%(ext)s',
            'ffmpeg_location': ruta_ffmpeg,
            'progress_hooks': [progress_callback] if progress_callback else [],
        }

        if formato == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': f'{self.listaAudio[int(quality)]}',
                }],
                'extractaudio': True,
            })
        else:
            ydl_opts.update({
                'format': f'bestvideo[height<={self.listaVideo[int(quality)]}]+bestaudio/best',
                'merge_output_format': 'mp4',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
                'postprocessor_args': [
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-b:a', '320k'
                ],
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

    
    def Info(self):
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(self.url, download=False)
    
        title = info['title']
        self.nameFile = f"%(title)s_{uuid.uuid1()}"
        match = re.search(r'(?:v=|\/|shorts\/|embed\/)([a-zA-Z0-9_-]{11})', self.url)
        video_id = match.group(1)
        iframe_code = f'<iframe class="p-0 m-0" width="100%" height="100%" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'

        
        detail = {
            'title':title,
            'iframe':iframe_code,
            'nameFile':title + self.nameFile.replace(f"%(title)s","")
        }
        
        return detail

    