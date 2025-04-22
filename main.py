# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy import platform
import requests
import json
from datetime import datetime
from plyer import filechooser
import os
import logging
from kivy.uix.dropdown import DropDown
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen
from PIL import Image as PilImage
import io

# URLs del servidor
url_conductores = "http://34.67.103.132:5000/api/conductores"
url_vehiculos = "http://34.67.103.132:5000/api/vehiculos_info"

# Solicitar permisos en Android
if platform == "android":
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE,
                             Permission.WRITE_EXTERNAL_STORAGE])
    except ImportError:
        pass

def comprimir_imagen(path, quality=70, max_size=(1280, 960)):
    """Intenta comprimir la imagen y devuelve un buffer con la imagen comprimida.
    Si hay un error, devuelve None para usar la imagen original."""
    try:
        # Abrir la imagen
        img = PilImage.open(path)
        
        # Obtener el tamaño original
        original_width, original_height = img.size
        target_width, target_height = max_size
        
        # Verificar si la imagen necesita redimensionarse
        if original_width > target_width or original_height > target_height:
            # Calcular el nuevo tamaño manteniendo la relación de aspecto
            aspect_ratio = original_width / original_height
            if aspect_ratio > 1:  # Imagen más ancha que alta
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            else:  # Imagen más alta que ancha
                new_height = target_height
                new_width = int(target_height * aspect_ratio)
            img = img.resize((new_width, new_height), PilImage.Resampling.LANCZOS)
        
        # Crear un buffer para la imagen comprimida
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)  # Comprimir con calidad 70
        buffer.seek(0)  # Reiniciar el puntero del buffer
        return buffer
    except Exception as e:
        logging.error(f"Error al comprimir la imagen {path}: {e}")
        return None  # En caso de error, devolvemos None

# Pantalla principal
class MainScreen(Screen):
    """Pantalla principal con opciones de formulario."""

    def go_to_salida_form(self, *args):
        """Navega al formulario de datos de salida."""
        self.manager.current = 'salida_form'

    def go_to_llegada_form(self, *args):
        """Navega al formulario de datos de llegada."""
        self.manager.current = 'llegada_form'

# Formulario de Salida
class FormularioSalida(BoxLayout, Screen):
    """Formulario para ingresar datos de salida del chofer."""
    nombre_input = ObjectProperty(None)
    vehiculo_input = ObjectProperty(None)
    placa_input = ObjectProperty(None)
    fecha_salida_input = ObjectProperty(None)
    hora_salida_input = ObjectProperty(None)
    ubicacion_inicial_input = ObjectProperty(None)
    km_inicial_input = ObjectProperty(None)
    observaciones_salida_input = ObjectProperty(None)
    file_list_layout_inicio = ObjectProperty(None)  # Layout para la lista de archivos de inicio

    fotos_inicio_paths = ListProperty([""] * 4)  # Hasta 4 fotos

    btn_km_inicial_color = ListProperty([0, 0.5, 0.8, 1])

    dropdown_chofer = ObjectProperty(None)
    selected_chofer = StringProperty("")
    dropdown_vehiculo = ObjectProperty(None)
    selected_vehiculo = StringProperty("")

    enviar_btn_disabled = BooleanProperty(False)

    def __init__(self, conductores, vehiculos, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 30
        self.spacing = 40
        self.original_y = 0
        self.conductores = conductores
        self.vehiculos = vehiculos
        Clock.schedule_once(self.store_original_position, 0)
        Clock.schedule_once(self.set_fecha_actual)
        Clock.schedule_once(self.setup_dropdowns)
        Clock.schedule_once(self.setup_observaciones)

    def store_original_position(self, dt):
        """Guarda la posición original del formulario."""
        self.original_y = self.y

    def set_fecha_actual(self, dt):
        """Establece la fecha actual en el campo correspondiente."""
        self.fecha_salida_input.text = datetime.now().strftime("%Y-%m-%d")

    def setup_dropdowns(self, dt):
        """Configura los dropdowns para choferes y vehículos."""
        self.dropdown_chofer = DropDown(auto_width=False, width=dp(300), max_height=dp(200))
        self.dropdown_vehiculo = DropDown(auto_width=False, width=dp(300), max_height=dp(200))

        self.nombre_input.bind(text=self.on_nombre_text)
        self.vehiculo_input.bind(text=self.on_vehiculo_text)

    def setup_observaciones(self, dt):
        """Configura el comportamiento del campo de observaciones."""
        self.observaciones_salida_input.bind(focus=self.on_observaciones_focus)

    def on_observaciones_focus(self, instance, value):
        """Anima el formulario al enfocar/desenfocar el campo de observaciones."""
        offset = dp(50)
        if value:
            Animation(y=self.y + offset, d=0.3).start(self)
        else:
            Animation(y=self.original_y, d=0.3).start(self)

    def on_nombre_text(self, instance, value):
        """Filtra y muestra el dropdown de conductores."""
        self.dropdown_chofer.clear_widgets()
        if value.strip():
            filtered_conductores = [
                conductor for conductor in self.conductores
                if value.lower() in conductor.lower()
            ]
            if filtered_conductores:
                for conductor in filtered_conductores:
                    btn = Button(
                        text=conductor,
                        size_hint_y=None,
                        height=dp(44),
                        background_normal='',
                        background_color=(0.2, 0.2, 0.2, 1)
                    )
                    btn.bind(on_release=lambda btn: self.seleccionar_conductor(btn.text))
                    self.dropdown_chofer.add_widget(btn)
                if not self.dropdown_chofer.attach_to:
                    self.dropdown_chofer.open(instance)
            else:
                self.dropdown_chofer.dismiss()
        else:
            self.dropdown_chofer.dismiss()

    def on_vehiculo_text(self, instance, value):
        """Filtra y muestra el dropdown de vehículos."""
        self.dropdown_vehiculo.clear_widgets()
        if value.strip():
            filtered_vehiculos = [
                vehiculo for vehiculo in self.vehiculos
                if value.lower() in f"{vehiculo['tipo_vehiculo']} | {vehiculo['placa']}".lower()
            ]
            if filtered_vehiculos:
                for vehiculo in filtered_vehiculos:
                    texto_combinado = f"{vehiculo['tipo_vehiculo']} | {vehiculo['placa']}"
                    btn = Button(
                        text=texto_combinado,
                        size_hint_y=None,
                        height=dp(44),
                        background_normal='',
                        background_color=(0.2, 0.2, 0.2, 1)
                    )
                    btn.bind(on_release=lambda btn, v=vehiculo: self.seleccionar_vehiculo(v))
                    self.dropdown_vehiculo.add_widget(btn)
                if not self.dropdown_vehiculo.attach_to:
                    self.dropdown_vehiculo.open(instance)
            else:
                self.dropdown_vehiculo.dismiss()
        else:
            self.dropdown_vehiculo.dismiss()
            self.placa_input.text = ""

    def seleccionar_conductor(self, conductor):
        """Establece el conductor seleccionado."""
        self.nombre_input.text = conductor
        self.selected_chofer = conductor
        self.dropdown_chofer.dismiss()

    def seleccionar_vehiculo(self, vehiculo_data):
        """Establece el vehículo y placa seleccionados."""
        self.vehiculo_input.text = vehiculo_data['tipo_vehiculo']
        self.placa_input.text = vehiculo_data['placa']
        self.selected_vehiculo = vehiculo_data['tipo_vehiculo']
        self.dropdown_vehiculo.dismiss()

    def validar_campos(self):
        """Valida que los campos obligatorios estén completos."""
        campos = {
            "Fecha": self.fecha_salida_input.text,
            "Nombre del Chofer": self.nombre_input.text,
            "Vehículo": self.vehiculo_input.text,
            "Placa": self.placa_input.text,
            "Ubicación Inicial": self.ubicacion_inicial_input.text,
            "Hora de Salida": self.hora_salida_input.text,
            "Kilometraje Inicial": self.km_inicial_input.text,
        }

        for nombre, valor in campos.items():
            if not valor.strip():
                self.mostrar_popup_error(f"El campo '{nombre}' es obligatorio.")
                return False

        try:
            datetime.strptime(self.hora_salida_input.text, "%H:%M")
        except ValueError:
            self.mostrar_popup_error("La hora debe estar en formato HH:MM.")
            return False

        try:
            float(self.km_inicial_input.text)
        except ValueError:
            self.mostrar_popup_error("El kilometraje debe ser un número válido.")
            return False

        return True

    def seleccionar_foto_km_inicial(self):
        """Abre el selector de archivos para elegir hasta 4 fotos del km inicial."""
        self.fotos_inicio_paths = [""] * 4
        def on_selection(selection):
            if selection:
                self.fotos_inicio_paths = selection[:4]
                self.btn_km_inicial_color = [0, 0.8, 0, 1]
                Clock.schedule_once(lambda dt: self.mostrar_popup_fotos_seleccionadas(self.fotos_inicio_paths), 2.5)
            else:
                self.fotos_inicio_paths = [""] * 4
                self.btn_km_inicial_color = [0, 0.5, 0.8, 1]

        filechooser.open_file(
            on_selection=on_selection,
            title="Seleccionar Fotos km Inicial",
            filters=[("Image Files", "*.jpg;*.jpeg;*.png")],
            multiple=True
        )

    def mostrar_popup_fotos_seleccionadas(self, paths):
        """Muestra un popup con la lista de fotos seleccionadas."""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        titulo = Label(
            text="Fotos seleccionadas:",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40),
            color=(0, 0.5, 0.8, 1)
        )
        content.add_widget(titulo)
        
        for path in paths:
            if path:
                filename = os.path.basename(path)
                label = Label(
                    text=f"• {filename}",
                    font_size=dp(16),
                    size_hint_y=None,
                    height=dp(30),
                    halign='left',
                    color=(1, 1, 1, 1)
                )
                label.bind(size=label.setter('text_size'))
                content.add_widget(label)
        
        btn = Button(
            text="Aceptar",
            size_hint=(None, None),
            size=(dp(150), dp(50)),
            pos_hint={'center_x': 0.5},
            background_color=(0, 0.5, 0.8, 1)
        )
        
        popup = Popup(
            title='Fotos Seleccionadas',
            content=content,
            size_hint=(0.9, None),
            height=dp(400),
            auto_dismiss=True
        )
        
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def actualizar_lista_fotos_inicio(self):
        """Actualiza la lista de nombres de archivos de fotos de inicio en la UI."""
        self.file_list_layout_inicio.clear_widgets()
        if self.fotos_inicio_paths and any(self.fotos_inicio_paths):
            for path in self.fotos_inicio_paths:
                if path:
                    filename = os.path.basename(path)
                    label = Label(text=filename, font_size=dp(20), color=(0, 0, 0, 1), halign='left')
                    self.file_list_layout_inicio.add_widget(label)
        else:
            label = Label(text="Ninguna foto seleccionada", font_size=dp(20), color=(0.5, 0.5, 0.5, 1), halign='left')
            self.file_list_layout_inicio.add_widget(label)

    def enviar_datos_salida(self):
        """Envía los datos del formulario de salida al servidor, usando fotos comprimidas si es posible."""
        if not self.validar_campos():  # Validación de campos
            return

        # Preparar los datos del formulario
        payload = {
            "tipo_formulario": "salida",
            "nombre_chofer": self.nombre_input.text,
            "vehiculo": self.vehiculo_input.text,
            "placa": self.placa_input.text,
            "fecha_salida": self.fecha_salida_input.text,
            "hora_salida": self.hora_salida_input.text,
            "ubicacion_inicial": self.ubicacion_inicial_input.text,
            "km_inicial": self.km_inicial_input.text,
            "observaciones_salida": self.observaciones_salida_input.text
        }

        # Preparar las imágenes para el envío
        files = {}
        for i, path in enumerate(self.fotos_inicio_paths, start=1):
            if path:
                # Intentar comprimir la imagen
                compressed_image = comprimir_imagen(path)
                if compressed_image:
                    # Si la compresión es exitosa, usar la imagen comprimida
                    files[f"foto_km_inicial_{i}"] = (
                        os.path.basename(path),  # Nombre del archivo
                        compressed_image,        # Buffer con la imagen comprimida
                        "image/jpeg"             # Tipo MIME
                    )
                else:
                    # Si falla la compresión, usar la imagen original
                    with open(path, 'rb') as original_file:
                        files[f"foto_km_inicial_{i}"] = (
                            os.path.basename(path),  # Nombre del archivo
                            original_file.read(),    # Contenido original
                            "image/jpeg"             # Tipo MIME
                        )

        # Enviar los datos al servidor
        url = "http://34.67.103.132:5000/api/recibir_datos_choferes"
        # url = "http://127.0.0.1:5000/api/recibir_datos_choferes"
        try:
            response = requests.post(url, data=payload, files=files, timeout=30)
            response.raise_for_status()
            self.mostrar_popup_exito("Datos de Salida enviados exitosamente.")
            self.enviar_btn_disabled = True
        except requests.exceptions.RequestException as e:
            self.mostrar_popup_error(f"Error de conexión: {e}")
        finally:
            # Cerrar los buffers si se usaron
            for _, file_info in files.items():
                if isinstance(file_info[1], io.BytesIO):
                    file_info[1].close()

    def limpiar_formulario(self):
        """Limpia los campos del formulario de salida."""
        self.fecha_salida_input.text = datetime.now().strftime("%Y-%m-%d")
        self.nombre_input.text = ""
        self.vehiculo_input.text = ""
        self.placa_input.text = ""
        self.ubicacion_inicial_input.text = ""
        self.hora_salida_input.text = ""
        self.km_inicial_input.text = ""
        self.observaciones_salida_input.text = ""
        self.fotos_inicio_paths = [""] * 4
        self.btn_km_inicial_color = [0, 0.5, 0.8, 1]
        self.actualizar_lista_fotos_inicio()
        self.enviar_btn_disabled = False

    def mostrar_popup_exito(self, mensaje):
        """Muestra un popup de éxito."""
        popup = Popup(title='Éxito', content=Label(text=mensaje, font_size=dp(20)), size_hint=(0.8, 0.4))
        popup.open()

    def mostrar_popup_error(self, mensaje):
        """Muestra un popup de error."""
        popup = Popup(title='Error', content=Label(text=mensaje, font_size=dp(20)), size_hint=(0.8, 0.4))
        popup.open()

# Formulario de Llegada
class FormularioLlegada(BoxLayout, Screen):
    """Formulario para ingresar datos de llegada del chofer."""
    nombre_input = ObjectProperty(None)
    vehiculo_input = ObjectProperty(None)
    placa_input = ObjectProperty(None)
    fecha_llegada_input = ObjectProperty(None)
    hora_retorno_input = ObjectProperty(None)
    ubicacion_final_input = ObjectProperty(None)
    km_final_input = ObjectProperty(None)
    observaciones_llegada_input = ObjectProperty(None)
    file_list_layout_fin = ObjectProperty(None)  # Layout para la lista de archivos de fin

    fotos_fin_paths = ListProperty([""] * 4)  # Hasta 4 fotos

    btn_km_final_color = ListProperty([0, 0.5, 0.8, 1])

    dropdown_chofer = ObjectProperty(None)
    selected_chofer = StringProperty("")
    dropdown_vehiculo = ObjectProperty(None)
    selected_vehiculo = StringProperty("")

    enviar_btn_disabled = BooleanProperty(False)

    def __init__(self, conductores, vehiculos, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 30
        self.spacing = 40
        self.original_y = 0
        self.conductores = conductores
        self.vehiculos = vehiculos
        Clock.schedule_once(self.store_original_position, 0)
        Clock.schedule_once(self.set_fecha_actual)
        Clock.schedule_once(self.setup_dropdowns)
        Clock.schedule_once(self.setup_observaciones)

    def store_original_position(self, dt):
        """Guarda la posición original del formulario."""
        self.original_y = self.y

    def set_fecha_actual(self, dt):
        """Establece la fecha actual en el campo de llegada."""
        self.fecha_llegada_input.text = datetime.now().strftime("%Y-%m-%d")

    def setup_dropdowns(self, dt):
        """Configura los dropdowns para choferes y vehículos."""
        self.dropdown_chofer = DropDown(auto_width=False, width=dp(300), max_height=dp(200))
        self.dropdown_vehiculo = DropDown(auto_width=False, width=dp(300), max_height=dp(200))

        self.nombre_input.bind(text=self.on_nombre_text)
        self.vehiculo_input.bind(text=self.on_vehiculo_text)

    def setup_observaciones(self, dt):
        """Configura el comportamiento del campo de observaciones."""
        self.observaciones_llegada_input.bind(focus=self.on_observaciones_focus)

    def on_observaciones_focus(self, instance, value):
        """Anima el formulario al enfocar/desenfocar el campo de observaciones."""
        offset = dp(50)
        if value:
            Animation(y=self.y + offset, d=0.3).start(self)
        else:
            Animation(y=self.original_y, d=0.3).start(self)

    def on_nombre_text(self, instance, value):
        """Filtra y muestra el dropdown de conductores."""
        self.dropdown_chofer.clear_widgets()
        if value.strip():
            filtered_conductores = [
                conductor for conductor in self.conductores
                if value.lower() in conductor.lower()
            ]
            if filtered_conductores:
                for conductor in filtered_conductores:
                    btn = Button(
                        text=conductor,
                        size_hint_y=None,
                        height=dp(44),
                        background_normal='',
                        background_color=(0.2, 0.2, 0.2, 1)
                    )
                    btn.bind(on_release=lambda btn: self.seleccionar_conductor(btn.text))
                    self.dropdown_chofer.add_widget(btn)
                if not self.dropdown_chofer.attach_to:
                    self.dropdown_chofer.open(instance)
            else:
                self.dropdown_chofer.dismiss()
        else:
            self.dropdown_chofer.dismiss()

    def on_vehiculo_text(self, instance, value):
        """Filtra y muestra el dropdown de vehículos."""
        self.dropdown_vehiculo.clear_widgets()
        if value.strip():
            filtered_vehiculos = [
                vehiculo for vehiculo in self.vehiculos
                if value.lower() in f"{vehiculo['tipo_vehiculo']} | {vehiculo['placa']}".lower()
            ]
            if filtered_vehiculos:
                for vehiculo in filtered_vehiculos:
                    texto_combinado = f"{vehiculo['tipo_vehiculo']} | {vehiculo['placa']}"
                    btn = Button(
                        text=texto_combinado,
                        size_hint_y=None,
                        height=dp(44),
                        background_normal='',
                        background_color=(0.2, 0.2, 0.2, 1)
                    )
                    btn.bind(on_release=lambda btn, v=vehiculo: self.seleccionar_vehiculo(v))
                    self.dropdown_vehiculo.add_widget(btn)
                if not self.dropdown_vehiculo.attach_to:
                    self.dropdown_vehiculo.open(instance)
            else:
                self.dropdown_vehiculo.dismiss()
        else:
            self.dropdown_vehiculo.dismiss()
            self.placa_input.text = ""

    def seleccionar_conductor(self, conductor):
        """Establece el conductor seleccionado."""
        self.nombre_input.text = conductor
        self.selected_chofer = conductor
        self.dropdown_chofer.dismiss()

    def seleccionar_vehiculo(self, vehiculo_data):
        """Establece el vehículo y placa seleccionados."""
        self.vehiculo_input.text = vehiculo_data['tipo_vehiculo']
        self.placa_input.text = vehiculo_data['placa']
        self.selected_vehiculo = vehiculo_data['tipo_vehiculo']
        self.dropdown_vehiculo.dismiss()

    def validar_campos_llegada(self):
        """Valida que los campos obligatorios de llegada estén completos."""
        campos = {
            "Fecha de Llegada": self.fecha_llegada_input.text,
            "Nombre del Chofer": self.nombre_input.text,
            "Vehículo": self.vehiculo_input.text,
            "Placa": self.placa_input.text,
            "Ubicación Final": self.ubicacion_final_input.text,
            "Hora de Retorno": self.hora_retorno_input.text,
            "Kilometraje Final": self.km_final_input.text,
        }

        for nombre, valor in campos.items():
            if not valor.strip():
                self.mostrar_popup_error(f"El campo '{nombre}' es obligatorio.")
                return False

        try:
            datetime.strptime(self.hora_retorno_input.text, "%H:%M")
        except ValueError:
            self.mostrar_popup_error("La hora debe estar en formato HH:MM.")
            return False

        try:
            float(self.km_final_input.text)
        except ValueError:
            self.mostrar_popup_error("El kilometraje debe ser un número válido.")
            return False

        return True

    def seleccionar_foto_km_final(self):
        """Abre el selector de archivos para elegir hasta 4 fotos del km final."""
        self.fotos_fin_paths = [""] * 4
        def on_selection(selection):
            if selection:
                self.fotos_fin_paths = selection[:4]
                self.btn_km_final_color = [0, 0.8, 0, 1]
                Clock.schedule_once(lambda dt: self.mostrar_popup_fotos_seleccionadas(self.fotos_fin_paths), 2.5)
            else:
                self.fotos_fin_paths = [""] * 4
                self.btn_km_final_color = [0, 0.5, 0.8, 1]

        filechooser.open_file(
            on_selection=on_selection,
            title="Seleccionar Fotos km Final",
            filters=[("Image Files", "*.jpg;*.jpeg;*.png")],
            multiple=True
        )

    def mostrar_popup_fotos_seleccionadas(self, paths):
        """Muestra un popup con la lista de fotos seleccionadas."""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        titulo = Label(
            text="Fotos seleccionadas:",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40),
            color=(0, 0.5, 0.8, 1)
        )
        content.add_widget(titulo)
        
        for path in paths:
            if path:
                filename = os.path.basename(path)
                label = Label(
                    text=f"• {filename}",
                    font_size=dp(16),
                    size_hint_y=None,
                    height=dp(30),
                    halign='left',
                    color=(1, 1, 1, 1)
                )
                label.bind(size=label.setter('text_size'))
                content.add_widget(label)
        
        btn = Button(
            text="Aceptar",
            size_hint=(None, None),
            size=(dp(150), dp(50)),
            pos_hint={'center_x': 0.5},
            background_color=(0, 0.5, 0.8, 1)
        )
        
        popup = Popup(
            title='Fotos Seleccionadas',
            content=content,
            size_hint=(0.9, None),
            height=dp(400),
            auto_dismiss=True
        )
        
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)
        popup.open()

    def actualizar_lista_fotos_fin(self):
        """Actualiza la lista de nombres de archivos de fotos de fin en la UI."""
        self.file_list_layout_fin.clear_widgets()
        if self.fotos_fin_paths and any(self.fotos_fin_paths):
            for path in self.fotos_fin_paths:
                if path:
                    filename = os.path.basename(path)
                    label = Label(text=filename, font_size=dp(20), color=(0, 0, 0, 1), halign='left')
                    self.file_list_layout_fin.add_widget(label)
        else:
            label = Label(text="Ninguna foto seleccionada", font_size=dp(20), color=(0.5, 0.5, 0.5, 1), halign='left')
            self.file_list_layout_fin.add_widget(label)

    def enviar_datos_llegada(self):
        """Envía los datos del formulario de llegada al servidor, usando fotos comprimidas si es posible."""
        if not self.validar_campos_llegada():  # Validación de campos
            return

        # Preparar los datos del formulario
        payload = {
            "tipo_formulario": "llegada",
            "nombre_chofer": self.nombre_input.text,
            "vehiculo": self.vehiculo_input.text,
            "placa": self.placa_input.text,
            "fecha_llegada": self.fecha_llegada_input.text,
            "hora_retorno": self.hora_retorno_input.text,
            "ubicacion_final": self.ubicacion_final_input.text,
            "km_final": self.km_final_input.text,
            "observaciones_llegada": self.observaciones_llegada_input.text
        }

        # Preparar las imágenes para el envío
        files = {}
        for i, path in enumerate(self.fotos_fin_paths, start=1):
            if path:
                # Intentar comprimir la imagen
                compressed_image = comprimir_imagen(path)
                if compressed_image:
                    # Si la compresión es exitosa, usar la imagen comprimida
                    files[f"foto_km_final_{i}"] = (
                        os.path.basename(path),  # Nombre del archivo
                        compressed_image,        # Buffer con la imagen comprimida
                        "image/jpeg"             # Tipo MIME
                    )
                else:
                    # Si falla la compresión, usar la imagen original
                    with open(path, 'rb') as original_file:
                        files[f"foto_km_final_{i}"] = (
                            os.path.basename(path),  # Nombre del archivo
                            original_file.read(),    # Contenido original
                            "image/jpeg"             # Tipo MIME
                        )

        # Enviar los datos al servidor
        url = "http://34.67.103.132:5000/api/recibir_datos_choferes"
        # url = "http://127.0.0.1:5000/api/recibir_datos_choferes"
        
        try:
            response = requests.post(url, data=payload, files=files, timeout=30)
            response.raise_for_status()
            self.mostrar_popup_exito("Datos de Llegada enviados exitosamente.")
            self.enviar_btn_disabled = True
        except requests.exceptions.RequestException as e:
            self.mostrar_popup_error(f"Error de conexión: {e}")
        finally:
            # Cerrar los buffers si se usaron
            for _, file_info in files.items():
                if isinstance(file_info[1], io.BytesIO):
                    file_info[1].close()

    def limpiar_formulario(self):
        """Limpia los campos del formulario de llegada."""
        self.fecha_llegada_input.text = datetime.now().strftime("%Y-%m-%d")
        self.nombre_input.text = ""
        self.vehiculo_input.text = ""
        self.placa_input.text = ""
        self.ubicacion_final_input.text = ""
        self.hora_retorno_input.text = ""
        self.km_final_input.text = ""
        self.observaciones_llegada_input.text = ""
        self.fotos_fin_paths = [""] * 4
        self.btn_km_final_color = [0, 0.5, 0.8, 1]
        self.actualizar_lista_fotos_fin()
        self.enviar_btn_disabled = False

    def mostrar_popup_exito(self, mensaje):
        """Muestra un popup de éxito."""
        popup = Popup(title='Éxito', content=Label(text=mensaje, font_size=dp(20)), size_hint=(0.8, 0.4))
        popup.open()

    def mostrar_popup_error(self, mensaje):
        """Muestra un popup de error."""
        popup = Popup(title='Error', content=Label(text=mensaje, font_size=dp(20)), size_hint=(0.8, 0.4))
        popup.open()

# Aplicación Principal
class FormularioApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conductores = []
        self.vehiculos = []

    def build(self):
        self.cargar_conductores()
        self.cargar_vehiculos()

        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main_screen'))
        sm.add_widget(FormularioSalida(conductores=self.conductores, vehiculos=self.vehiculos, name='salida_form'))
        sm.add_widget(FormularioLlegada(conductores=self.conductores, vehiculos=self.vehiculos, name='llegada_form'))
        Clock.schedule_once(lambda dt: setattr(sm, 'current', 'main_screen'), 5.0)
        return sm

    def cargar_conductores(self):
        """Carga la lista de conductores desde el servidor."""
        try:
            response = requests.get(url_conductores, timeout=10)
            response.raise_for_status()
            self.conductores = response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al cargar conductores: {e}")
        except ValueError as e:
            logging.error(f"Error al procesar respuesta (conductores): {e}")

    def cargar_vehiculos(self):
        """Carga la lista de vehículos desde el servidor."""
        try:
            response = requests.get(url_vehiculos, timeout=10)
            response.raise_for_status()
            self.vehiculos = response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error al cargar vehículos: {e}")
        except ValueError as e:
            logging.error(f"Error al procesar respuesta (vehículos): {e}")

if __name__ == '__main__':
    FormularioApp().run()