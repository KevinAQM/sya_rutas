import os
import sys
import requests
import webbrowser
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, ttk
import zipfile


def resource_path(relative_path):
    """
    Obtiene la ruta absoluta a los recursos, tanto para desarrollo como para ejecutables generados con PyInstaller.
    """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def obtener_ruta_aplicacion():
    """
    Obtiene la ruta del directorio en el que se encuentra el ejecutable o el script.
    """
    if getattr(sys, 'frozen', False):
        # En modo ejecutable (PyInstaller)
        return os.path.dirname(sys.executable)
    else:
        # En modo desarrollo
        return os.path.dirname(os.path.abspath(__file__))

def crear_carpeta_descargas():
    """
    Crea la carpeta 'descargas' en la misma ruta que el ejecutable, si no existe.
    """
    ruta_app = obtener_ruta_aplicacion()
    ruta_descargas = os.path.join(ruta_app, "descargas")
    if not os.path.exists(ruta_descargas):
        try:
            os.makedirs(ruta_descargas)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la carpeta 'descargas':\n{e}")
    return ruta_descargas

def descargar_archivo(url, nombre_archivo):
    """
    Función para descargar un archivo desde una URL y guardarlo en la carpeta 'descargas'.
    Maneja archivos zip y otros.
    """
    try:
        respuesta = requests.get(url, stream=True)
        respuesta.raise_for_status()  # Lanza una excepción si la solicitud falla

        ruta_descargas = crear_carpeta_descargas()
        nombre_archivo_completo = os.path.join(ruta_descargas, nombre_archivo)

        with open(nombre_archivo_completo, 'wb') as archivo:
            for chunk in respuesta.iter_content(chunk_size=8192):
                archivo.write(chunk)

        messagebox.showinfo("Descarga completada", f"Archivo '{nombre_archivo}' descargado exitosamente en:\n{nombre_archivo_completo}")
        return nombre_archivo_completo # Retorna la ruta completa

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error de descarga", f"Error al descargar el archivo:\n{e}")
        return None

def descomprimir_archivo(ruta_archivo, carpeta_destino):
    """Descomprime un archivo zip en la carpeta de destino."""
    try:
        with zipfile.ZipFile(ruta_archivo, 'r') as zip_ref:
            zip_ref.extractall(carpeta_destino)
        messagebox.showinfo("Descompresión completada", f"Carpeta descomprimida en: {carpeta_destino}")

    except zipfile.BadZipFile:
        messagebox.showerror("Error", "El archivo descargado no es un archivo ZIP válido.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al descomprimir el archivo:\n{e}")

def on_descargar_rutas():
    """
    Evento del botón 'Descargar Registro Rutas'.
    """
    url_servidor = "http://34.67.103.132:5000/descargar-registro-rutas"
    nombre_archivo = "registros_choferes.xlsx"
    descargar_archivo(url_servidor, nombre_archivo)

def on_descargar_fotos():
    """
    Evento del botón 'Descargar Carpeta Fotos'.
    """
    url_servidor = "http://34.67.103.132:5000/descargar-carpeta-fotos"
    nombre_archivo = "fotos_km.zip"
    ruta_zip = descargar_archivo(url_servidor, nombre_archivo)
    if ruta_zip:
        # Descomprimir el archivo
        ruta_descargas = crear_carpeta_descargas()
        descomprimir_archivo(ruta_zip, ruta_descargas)
        # Opcional:  Borrar el zip después de descomprimir
        # os.remove(ruta_zip)


# Crear la ventana principal
root = tk.Tk()
root.title("S&A - Area de Equipos y Maquinarias")
root.geometry("450x520")  # Ajustado el tamaño
root.resizable(True, True)
root.configure(bg='#f0f0f0')

# Establecer el ícono de la ventana
try:
    root.iconbitmap(resource_path("images/smontyaragon.ico"))
except Exception:
    pass

# Estilo moderno
style = ttk.Style(root)
style.theme_use('clam')

# Estilo para el título
style.configure("Title.TLabel", font=("Helvetica", 16, "bold"), foreground="#333", background='#f0f0f0')

# Estilo base para los botones
style.configure("Base.TButton", font=("Helvetica", 14), padding=(15, 12), relief="flat", background="#e0e0e0", foreground="#333")
style.map("Base.TButton",
    background=[("active", "#f0f0f0")],
    relief=[("active", "raised")]
)

# Estilo específico para botones de descarga (azul claro)
style.configure("Descargar.TButton", parent="Base.TButton", background="#cce0ff", foreground="#003366")
style.map("Descargar.TButton",
    background=[("active", "#b3d1ff")],
    foreground=[("active", "#003366")]
)

# Estilo para la imagen
style.configure("ImageLabel.TLabel", background='#f0f0f0')

# Etiqueta de título
titulo = ttk.Label(root, text="S&A - Descarga de Rutas y Fotos", style="Title.TLabel") # Texto actualizado
titulo.pack(pady=20)

# Cargar la imagen
try:
    image = Image.open(resource_path("images/smontyaragon.png"))
    photo = ImageTk.PhotoImage(image)
    label_imagen = ttk.Label(root, image=photo, style="ImageLabel.TLabel")
    label_imagen.image = photo
    label_imagen.pack(pady=15)
except Exception:
    pass

# Crear la carpeta 'descargas' al inicio
crear_carpeta_descargas()

# Contenedor de botones
frame_botones = ttk.Frame(root)
frame_botones.pack(pady=20)

# Botón para descargar el archivo Excel de registros de choferes
btn_descargar_rutas = ttk.Button(frame_botones, text="Descargar Registro Rutas", command=on_descargar_rutas, style="Descargar.TButton")
btn_descargar_rutas.pack(pady=10) # Usar pack en lugar de grid

# Botón para descargar la carpeta de fotos
btn_descargar_fotos = ttk.Button(frame_botones, text="Descargar Carpeta Fotos", command=on_descargar_fotos, style="Descargar.TButton")
btn_descargar_fotos.pack(pady=10)


# Mostrar la ventana
root.mainloop()