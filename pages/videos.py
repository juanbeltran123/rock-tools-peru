from yt_dlp import YoutubeDL
import os

def descargar_video_completo(url, calidad='1080p', carpeta='./descargas'):
    """
    Descarga video de YouTube en MP4 con video y audio combinados
    
    Args:
        url: URL del video de YouTube
        calidad: '1080p', '720p', '480p', '360p' 
        carpeta: Carpeta donde guardar el video
    """
    
    # Crear carpeta si no existe
    os.makedirs(carpeta, exist_ok=True)
    
    # Opciones para garantizar MP4 con video+audio
    ydl_opts = {
        # Formato de salida: nombre del archivo
        'outtmpl': f'{carpeta}/%(title)s_%(height)sp.%(ext)s',
        
        # 🔥 CLAVE: Forzar a buscar video MP4 + audio y combinarlos
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        
        # Formato final de salida
        'merge_output_format': 'mp4',
        
        # Usar FFmpeg para combinar video y audio
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        
        # Forzar a mantener archivos temporales para combinar
        'keepvideo': True,
        
        # Silenciar algunas advertencias
        'quiet': False,
        'no_warnings': False,
        
        # Configuración de red (por si hay problemas)
        'retries': 10,
        'fragment_retries': 10,
    }
    
    try:
        print(f"🎬 Iniciando descarga: {url}")
        print(f"📹 Calidad: {calidad}")
        
        with YoutubeDL(ydl_opts) as ydl:
            # Descargar y combinar
            info = ydl.extract_info(url, download=True)
            
            # Obtener nombre del archivo final
            titulo = info.get('title', 'video')
            extension = 'mp4'
            nombre_archivo = f"{carpeta}/{titulo}_{calidad}.{extension}"
            
            print(f"\n✅ ¡DESCARGA COMPLETADA!")
            print(f"📁 Archivo: {nombre_archivo}")
            print(f"📏 Tamaño: {info.get('filesize_approx', 'Desconocido')} bytes")
            return nombre_archivo
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# 🎯 EJEMPLO DE USO
if __name__ == "__main__":
    url = input("🔗 Ingresa la URL del video: ")
    print("\nCalidades disponibles: 1080p, 720p, 480p, 360p")
    calidad = input("📺 Elige calidad (presiona Enter para 720p): ") or "720p"
    
    descargar_video_completo(url, calidad)