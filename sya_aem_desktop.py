import os
import sys
import requests
import webbrowser
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox, ttk
import zipfile

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def obtener_ruta_aplicacion():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def crear_carpeta_descargas():
    ruta_app = obtener_ruta_aplicacion()
    ruta_descargas = os.path.join(ruta_app, "descargas")
    if not os.path.exists(ruta_descargas):
        try:
            os.makedirs(ruta_descargas)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la carpeta 'descargas':\n{e}")
    return ruta_descargas

def descargar_archivo(url, nombre_archivo):
    try:
        respuesta = requests.get(url, stream=True)
        respuesta.raise_for_status()

        ruta_descargas = crear_carpeta_descargas()
        nombre_archivo_completo = os.path.join(ruta_descargas, nombre_archivo)

        with open(nombre_archivo_completo, 'wb') as archivo:
            for chunk in respuesta.iter_content(chunk_size=8192):
                archivo.write(chunk)

        messagebox.showinfo("Descarga completada", f"Archivo '{nombre_archivo}' descargado exitosamente en:\n{nombre_archivo_completo}")
        return nombre_archivo_completo
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error de descarga", f"Error al descargar el archivo:\n{e}")
        return None

def descomprimir_archivo(ruta_archivo, carpeta_destino):
    try:
        with zipfile.ZipFile(ruta_archivo, 'r') as zip_ref:
            zip_ref.extractall(carpeta_destino)
        messagebox.showinfo("Descompresión completada", f"Carpeta descomprimida en: {carpeta_destino}")
    except zipfile.BadZipFile:
        messagebox.showerror("Error", "El archivo descargado no es un archivo ZIP válido.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al descomprimir el archivo:\n{e}")

def on_descargar_rutas():
    url_servidor = "http://34.67.103.132:5000/descargar-registro-rutas"
    # url_servidor = "http://127.0.0.1:5000/descargar-registro-rutas"
    nombre_archivo = "registros_choferes.xlsx"
    ruta_registros = descargar_archivo(url_servidor, nombre_archivo)

def on_descargar_fotos():
    url_servidor = "http://34.67.103.132:5000/descargar-carpeta-fotos"
    # url_servidor = "http://127.0.0.1:5000/descargar-carpeta-fotos"
    nombre_archivo = "fotos_vehiculos.zip"
    ruta_zip = descargar_archivo(url_servidor, nombre_archivo)
    if ruta_zip:
        ruta_descargas = crear_carpeta_descargas()
        descomprimir_archivo(ruta_zip, ruta_descargas)

def abrir_archivo(ruta_archivo):
    if os.path.exists(ruta_archivo):
        webbrowser.open(ruta_archivo)
    else:
        messagebox.showerror("Error", "El archivo no existe.")

def on_abrir_rutas():
    ruta_app = obtener_ruta_aplicacion()
    ruta_registros = os.path.join(ruta_app, "descargas", "registros_choferes.xlsx")
    abrir_archivo(ruta_registros)


def on_abrir_fotos():
    ruta_app = obtener_ruta_aplicacion()
    ruta_fotos = os.path.join(ruta_app, "descargas", "fotos_vehiculos")
    abrir_archivo(ruta_fotos)


root = tk.Tk()
root.title("S&A - Area de Equipos y Maquinarias")
root.geometry("450x520")
root.resizable(True, True)
root.configure(bg='#f0f0f0')

try:
    root.iconbitmap(resource_path("images/smontyaragon.ico"))
except Exception:
    pass

style = ttk.Style(root)
style.theme_use('clam')

style.configure("Title.TLabel", font=("Helvetica", 16, "bold"), foreground="#333", background='#f0f0f0')

style.configure("Base.TButton", font=("Helvetica", 14), padding=(15, 12), relief="flat", background="#e0e0e0", foreground="#333")
style.map("Base.TButton",
          background=[("active", "#f0f0f0")],
          relief=[("active", "raised")]
          )

style.configure("Descargar.TButton", parent="Base.TButton", background="#cce0ff", foreground="#003366")
style.map("Descargar.TButton",
          background=[("active", "#b3d1ff")],
          foreground=[("active", "#003366")]
          )

style.configure("Abrir.TButton", parent="Base.TButton", background="#90EE90", foreground="#006400") # Verde claro
style.map("Abrir.TButton",
          background=[("active", "#7FFFD4")], # Acuamarine
          foreground=[("active", "#006400")]
          )

titulo = ttk.Label(root, text="S&A - Rutas de Vehículos", style="Title.TLabel")
titulo.pack(pady=20)

try:
    image = Image.open(resource_path("images/smontyaragon.png"))
    photo = ImageTk.PhotoImage(image)
    label_imagen = ttk.Label(root, image=photo)
    label_imagen.image = photo
    label_imagen.pack(pady=15)
except Exception:
    pass

crear_carpeta_descargas()

frame_botones = ttk.Frame(root)
frame_botones.pack(pady=20)

frame_rutas_botones = ttk.Frame(frame_botones)
frame_rutas_botones.pack(pady=5)

btn_descargar_rutas = ttk.Button(frame_rutas_botones, text="Descargar Registro Rutas", command=on_descargar_rutas, style="Descargar.TButton")
btn_descargar_rutas.pack(side='left', padx=10)

btn_abrir_rutas = ttk.Button(frame_rutas_botones, text="Abrir Registro Rutas", command=on_abrir_rutas, style="Abrir.TButton")
btn_abrir_rutas.pack(side='left', padx=10)

frame_fotos_botones = ttk.Frame(frame_botones)
frame_fotos_botones.pack(pady=5)

btn_descargar_fotos = ttk.Button(frame_fotos_botones, text="Descargar Carpeta Fotos", command=on_descargar_fotos, style="Descargar.TButton")
btn_descargar_fotos.pack(side='left', padx=10)

btn_abrir_fotos = ttk.Button(frame_fotos_botones, text="Abrir Carpeta Fotos", command=on_abrir_fotos, style="Abrir.TButton")
btn_abrir_fotos.pack(side='left', padx=10)


root.mainloop()
