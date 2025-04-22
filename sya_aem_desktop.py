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

def obtener_lista_carpetas_servidor():
    url_servidor = "http://34.67.103.132:5000/api/listar-carpetas-fotos"  # Ajusta la URL si es necesario
    try:
        respuesta = requests.get(url_servidor)
        respuesta.raise_for_status()
        return respuesta.json()  # Devuelve {nombre: num_fotos}
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"No se pudo conectar al servidor:\n{e}")
        return {}

def contar_fotos_local(carpeta_path):
    """Cuenta el número de fotos en una carpeta local."""
    if not os.path.exists(carpeta_path):
        return 0
    return len([f for f in os.listdir(carpeta_path) if os.path.isfile(os.path.join(carpeta_path, f))])

def obtener_carpetas_a_descargar():
    ruta_descargas = "descargas"  # Ajusta esta ruta
    ruta_fotos_local = os.path.join(ruta_descargas, "fotos_vehiculos")
    if not os.path.exists(ruta_fotos_local):
        os.makedirs(ruta_fotos_local)
    
    carpetas_servidor = obtener_lista_carpetas_servidor()  # {nombre: num_fotos}
    carpetas_a_descargar = []
    
    for nombre, num_fotos_servidor in carpetas_servidor.items():
        carpeta_local_path = os.path.join(ruta_fotos_local, nombre)
        num_fotos_local = contar_fotos_local(carpeta_local_path)
        if num_fotos_local < num_fotos_servidor:
            carpetas_a_descargar.append(nombre)
    
    return carpetas_a_descargar

def descargar_archivo(url, nombre_archivo):
    try:
        respuesta = requests.get(url, stream=True)
        respuesta.raise_for_status()

        ruta_descargas = crear_carpeta_descargas()
        nombre_archivo_completo = os.path.join(ruta_descargas, nombre_archivo)

        with open(nombre_archivo_completo, 'wb') as archivo:
            for chunk in respuesta.iter_content(chunk_size=8192):
                archivo.write(chunk)

        return nombre_archivo_completo  # Retorna la ruta del archivo descargado
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error de descarga", f"Error al descargar el archivo:\n{e}")
        return None

def descomprimir_archivo(ruta_archivo, carpeta_destino):
    try:
        with zipfile.ZipFile(ruta_archivo, 'r') as zip_ref:
            zip_ref.extractall(carpeta_destino)
        os.remove(ruta_archivo)  # Elimina el archivo ZIP después de descomprimirlo
        return True
    except zipfile.BadZipFile:
        messagebox.showerror("Error", "El archivo descargado no es un archivo ZIP válido.")
        return False
    except Exception as e:
        messagebox.showerror("Error", f"Error al descomprimir el archivo:\n{e}")
        return False

def on_descargar_rutas():
    url_servidor = "http://34.67.103.132:5000/descargar-registro-rutas"
    nombre_archivo = "registros_choferes.xlsx"
    ruta_archivo = descargar_archivo(url_servidor, nombre_archivo)
    if ruta_archivo:
        messagebox.showinfo("Descarga completada", "Registro Excel descargado correctamente.")

def on_descargar_fotos():
    carpetas_a_descargar = obtener_carpetas_a_descargar()
    if not carpetas_a_descargar:
        messagebox.showinfo("Información", "No hay nuevas imágenes para descargar.")
        return
    
    ruta_descargas = crear_carpeta_descargas()
    ruta_fotos_local = os.path.join(ruta_descargas, "fotos_vehiculos")
    
    todas_descargadas = True  # Bandera para verificar si todo fue exitoso
    
    for carpeta in carpetas_a_descargar:
        url_servidor = f"http://34.67.103.132:5000/descargar-carpeta-fotos/{carpeta}"
        nombre_archivo = f"{carpeta}.zip"
        ruta_zip = descargar_archivo(url_servidor, nombre_archivo)
        if ruta_zip:
            if not descomprimir_archivo(ruta_zip, ruta_fotos_local):
                todas_descargadas = False
        else:
            todas_descargadas = False
    
    if todas_descargadas:
        messagebox.showinfo("Descarga completada", "Imágenes descargadas correctamente.")
    else:
        messagebox.showwarning("Advertencia", "Algunas imágenes no se pudieron descargar o descomprimir correctamente.")

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
