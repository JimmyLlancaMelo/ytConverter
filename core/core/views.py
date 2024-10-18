from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import messages

from .toolConverter import toolVideo
import os, threading
from django.http import FileResponse

class HomeView(View):
    def get(self, request, *args, **kwargs):

        return render(request,'pages/home.html')

    def post(self, request, *args, **kwargs):
        urlVideo = request.POST.get('urlVideo')
        toolvideo = toolVideo(urlVideo)
        toolvideo.Quality()
        
        qVideo = toolvideo.listaVideo
        qAudio = toolvideo.listaAudio
        Info = toolvideo.Info()
        context={
            'url':urlVideo,
            'qualityVideo':qVideo,
            'qualityAudio':qAudio,
            'title':Info['title'],
            'iframe':Info['iframe']
        }        
        
        return render(request, 'pages/download.html',context)

class HomeDownload(View):
    
    def post(self, request, *args, **kwargs):
        urlVideo = request.POST.get('getUrl')
        Quality = request.POST.get('getQuality')
        formato = request.POST.get('getFormat')

        toolvideo = toolVideo(urlVideo)
        self.Info = toolvideo.Info()
        toolvideo.Quality()
        toolvideo.Download(formato,Quality)

        file_path = f"media/fileYoutube/{self.Info['nameFile']}.{formato}"
        
        response = FileResponse(open(file_path, 'rb'), as_attachment=True) # Busca el archivo.mp4 y el as_attachment lo trata como descarga
        response['Content-Disposition'] = f'attachment; filename="{self.Info["title"]}.{formato}"' # Indicamos que se debe descargar y asignamos un titulo

        # Usar un hilo para eliminar el archivo después de que la respuesta se envíe
        def delete_file():
            threading.Event().wait(5) # Esperar  para asegurarse de que se haya enviado el archivo
            os.remove(file_path)

        # Iniciar el hilo para eliminar el archivo
        threading.Thread(target=delete_file).start()

        return response

def contact(request):
    if request.method == "POST":
        name = request.POST.get("nombre")
        subject = request.POST.get("asunto")
        email = request.POST.get("email")
        message = request.POST.get("mensaje")
        context = {
            'name':name,
            'email':email,
            'message':message
        }
        template = render_to_string("pages/email_template.html", context)
        email = EmailMessage(
            subject,
            template,
            settings.EMAIL_HOST_USER,
            ["windowsrevolutions501@gmail.com"]
            
        )
        email.fail_silently = False
        email.send()

        messages.success(request,"Se ha enviado un correo")
    else:
        print("F ALGO SALIO MAL :( ")
    
    return redirect("home")