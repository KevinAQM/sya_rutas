# main.py (modificado)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy import platform
import requests
import json
from datetime import datetime
from plyer import filechooser
import os
import logging
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.metrics import dp  # Import dp for device-independent pixels


if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE,
                        Permission.WRITE_EXTERNAL_STORAGEclass FormularioChofer(BoxLayout):

    fecha_input = ObjectProperty(None)
    nombre_input = ObjectProperty(None)
    vehiculo_input = ObjectProperty(None)
    placa_input = ObjectProperty(None)
    ubicacion_inicial_input = ObjectProperty(None)
    ubicacion_final_input = ObjectProperty(None)
    hora_salida_input = ObjectProperty(None)
    hora_llegada_input = ObjectProperty(None)
    km_inicial_input = ObjectProperty(None)
    km_final_input = ObjectProperty(None)
    comentarios_input = ObjectProperty(None)

    foto_km_inicial_path = StringProperty("")
    foto_km_final_path = StringProperty("")
    btn_km_inicial_color = ListProperty([0, 0.5, 0.8, 1])
    btn_km_final_color = ListProperty([0, 0.5, 0.8, 1])

    dropdown_chofer = ObjectProperty(None)
    selected_chofer = StringProperty("")
    dropdown_vehiculo = ObjectProperty(None)
    selected_vehiculo = StringProperty("")


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.set_fecha_actual)
        Clock.schedule_once(self.setup_dropdowns)
        self.conductores = []  # Store the full list of conductors
        self.vehiculos = []  # Store the full list of vehicles


    def set_fecha_actual(self, dt):
        self.fecha_input.text = datetime.now().strftime("%Y-%m-%d")

    def setup_dropdowns(self, dt):
        self.dropdown_chofer = DropDown()
        self.dropdown_vehiculo = DropDown()

        self.nombre_input.bind(text=self.on_nombre_text) # Bind to text change instead of focus
        self.vehiculo_input.bind(text=self.on_vehiculo_text)

        self.cargar_conductores()
        self.cargar_vehiculos()

    def on_nombre_text(self, instance, value):
        """Filtra y muestra el dropdown de conductores según el texto ingresado."""
        self.dropdown_chofer.dismiss()  # Asegura que el dropdown esté cerrado
        self.dropdown_chofer.clear_widgets()  # Limpia los botones anteriores
        filtered_conductores = [
            conductor for conductor in self.conductores
            if value.lower() in conductor.lower()
        ]
        if filtered_conductores:
            for conductor in filtered_conductores:
                btn = Button(text=conductor, size_hint_y=None, height=dp(44))
                btn.bind(on_release=lambda btn: self.seleccionar_conductor(btn.text))
                self.dropdown_chofer.add_widget(btn)
            self.dropdown_chofer.open(instance)
        else:
            self.dropdown_chofer.dismiss()

    def on_vehiculo_text(self, instance, value):
        """Filtra y muestra el dropdown de vehículos según el texto ingresado."""
        self.dropdown_vehiculo.dismiss()  # Asegura que el dropdown esté cerrado
        self.dropdown_vehiculo.clear_widgets()  # Limpia los botones anteriores
        filtered_vehiculos = [
            vehiculo for vehiculo in self.vehiculos
            if value.lower() in f"{vehiculo['tipo_vehiculo']} -- {vehiculo['placa']}".lower()
        ]
        if filtered_vehiculos:
            for vehiculo in filtered_vehiculos:
                btn_text = f"{vehiculo['tipo_vehiculo']} -- {vehiculo['placa']}"
                btn = Button(text=btn_text, size_hint_y=None, height=dp(44))
                btn.bind(on_release=lambda btn, v=vehiculo: self.seleccionar_vehiculo(v))
                self.dropdown_vehiculo.add_widget(btn)
            self.dropdown_vehiculo.open(instance)
        else:
            self.dropdown_vehiculo.dismiss()
        
    def show_dropdown_chofer(self, instance, value):
        # This is no longer needed.
        pass

    def show_dropdown_vehiculo(self, instance, value):
        # This is no longer needed
        pass



    def cargar_conductores(self):
        url = "http://34.67.103.132:5000/api/conductores"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            self.conductores = response.json()  # Store the full list
            # No initial population, only on text input
        except requests.exceptions.RequestException as e:
            self.mostrar_popup_error(f"Error al cargar conductores: {e}")
            logging.error(f"Error al cargar conductores: {e}")
        except ValueError as e:
            self.mostrar_popup_error(f"Error al procesar la respuesta del servidor: {e}")
            logging.error(f"Error al procesar respuesta: {e}")

    def seleccionar_conductor(self, conductor):
        self.nombre_input.text = conductor
        self.selected_chofer = conductor
        self.dropdown_chofer.dismiss()

    def cargar_vehiculos(self):
        """Carga la lista de vehículos desde el servidor."""
        url = "http://34.67.103.132:5000/api/vehiculos_info"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            self.vehiculos = response.json()  # Store full list
            # No initial population, only on text change
        except requests.exceptions.RequestException as e:
            self.mostrar_popup_error(f"Error al cargar vehículos: {e}")
            logging.error(f"Error al cargar vehículos: {e}")
        except ValueError as e:
            self.mostrar_popup_error(f"Error al procesar respuesta (vehículos): {e}")
            logging.error(f"Error al procesar respuesta (vehículos): {e}")

    def seleccionar_vehiculo(self, vehiculo_data):
        """Establece el vehículo y placa seleccionados."""
        self.vehiculo_input.text = vehiculo_data['tipo_vehiculo']
        self.placa_input.text = vehiculo_data['placa']
        self.selected_vehiculo = vehiculo_data['tipo_vehiculo']
        self.dropdown_vehiculo.dismiss()


    def validar_campos(self):
        campos = {
            "Fecha": self.fecha_input.text,
            "Nombre del Chofer": self.nombre_input.text,
            "Vehículo": self.vehiculo_input.text,
            "Placa": self.placa_input.text,
            "Ubicación Inicial": self.ubicacion_inicial_input.text,
            "Ubicación Final": self.ubicacion_final_input.text,
            "Hora de Salida": self.hora_salida_input.text,
            "Hora de Llegada": self.hora_llegada_input.text,
            "Kilometraje Inicial": self.km_inicial_input.text,
            "Kilometraje Final": self.km_final_input.text,
        }

        for nombre, valor in campos.items():
            if not valor.strip():
                self.mostrar_popup_error(f"El campo '{nombre}' es obligatorio.")
                return False

        try:
            datetime.strptime(self.hora_salida_input.text, "%H:%M")
            datetime.strptime(self.hora_llegada_input.text, "%H:%M")
        except ValueError:
            self.mostrar_popup_error("Las horas deben estar en formato HH:MM")
            return False

        try:
            km_inicial = float(self.km_inicial_input.text)
            km_final = float(self.km_final_input.text)
            if km_inicial < 0 or km_final < 0 or km_final < km_inicial:
                self.mostrar_popup_error("El kilometraje final debe ser mayor al inicial.")
                return False
        except ValueError:
            self.mostrar_popup_error("El kilometraje debe ser un número válido.")
            return False

        return True

    def seleccionar_foto_km_inicial(self):
        def on_selection(selection):
            if selection:
                self.foto_km_inicial_path = selection[0]
                print(f"Selected image path (inicial): {self.foto_km_inicial_path}")
                self.btn_km_inicial_color = [0, 0.8, 0, 1]
                Clock.schedule_once(lambda dt: self.mostrar_popup_exito_imagen(self.foto_km_inicial_path))

        filechooser.open_file(on_selection=on_selection, title="Seleccionar Foto km Inicial", filters=[("Image Files", "*.jpg;*.jpeg;*.png")])

    def seleccionar_foto_km_final(self):
        def on_selection(selection):
            if selection:
                self.foto_km_final_path = selection[0]
                print(f"Selected image path (final): {self.foto_km_final_path}")
                self.btn_km_final_color = [0, 0.8, 0, 1]
                Clock.schedule_once(lambda dt: self.mostrar_popup_exito_imagen(self.foto_km_final_path))

        filechooser.open_file(on_selection=on_selection, title="Seleccionar Foto km Final", filters=[("Image Files", "*.jpg;*.jpeg;*.png")])

    def enviar_datos(self):
        if not self.validar_campos():
            return
        self.btn_km_inicial_color = [0, 0.5, 0.8, 1]
        self.btn_km_final_color = [0, 0.5, 0.8, 1]

        print(f"foto_km_inicial_path: {self.foto_km_inicial_path}")
        print(f"foto_km_final_path: {self.foto_km_final_path}")

        payload = {
            "fecha": self.fecha_input.text,
            "nombre_chofer": self.nombre_input.text,
            "vehiculo": self.vehiculo_input.text,
            "placa": self.placa_input.text,
            "ubicacion_inicial": self.ubicacion_inicial_input.text,
            "ubicacion_final": self.ubicacion_final_input.text,
            "hora_salida": self.hora_salida_input.text,
            "hora_llegada": self.hora_llegada_input.text,
            "km_inicial": self.km_inicial_input.text,
            "km_final": self.km_final_input.text,
            "comentarios": self.comentarios_input.text
        }

        files = {}
        if self.foto_km_inicial_path:
            if os.path.exists(self.foto_km_inicial_path):
                nombre_sin_espacios = self.nombre_input.text.lower().replace(" ", "")
                filename_inicial = f"{self.fecha_input.text.replace('-', '')}_{self.hora_salida_input.text.replace(':', '')}_{nombre_sin_espacios}_kminicial.jpg"
                try:
                    files["foto_km_inicial"] = (filename_inicial, open(self.foto_km_inicial_path, 'rb'), "image/jpeg")
                except Exception as e:
                    self.mostrar_popup_error(f"No se pudo abrir la imagen de km inicial: {e}")
                    return
            else:
                self.mostrar_popup_error(f"Error: El archivo no existe (inicial): {self.foto_km_inicial_path}")
                return

        if self.foto_km_final_path:
            if os.path.exists(self.foto_km_final_path):
                nombre_sin_espacios = self.nombre_input.text.lower().replace(" ", "")
                filename_final = f"{self.fecha_input.text.replace('-', '')}_{self.hora_salida_input.text.replace(':', '')}_{nombre_sin_espacios}_kmfinal.jpg"
                try:
                    files["foto_km_final"] = (filename_final, open(self.foto_km_final_path, 'rb'), "image/jpeg")
                except Exception as e:
                    self.mostrar_popup_error(f"No se pudo abrir la imagen de km final: {e}")
                    return
            else:
                self.mostrar_popup_error(f"Error: El archivo no existe (final): {self.foto_km_final_path}")
                return

        url = "http://34.67.103.132:5000/api/recibir_datos_choferes"

        try:
            response = requests.post(url, data=payload, files=files, timeout=10)
            for _, fileinfo in files.items():
                fileinfo[1].close()

            if response.status_code == 200:
                self.mostrar_popup_exito("Datos enviados exitosamente.")
                self.limpiar_formulario()
            else:
                self.mostrar_popup_error(f"Error del servidor: {response.status_code}")
                print(f"Respuesta del servidor: {response.text}")
        except requests.exceptions.RequestException as e:
            self.mostrar_popup_error(f"Error de conexión: {e}")

    def limpiar_formulario(self):
        self.fecha_input.text = datetime.now().strftime("%Y-%m-%d")
        self.nombre_input.text = ""
        self.vehiculo_input.text = ""
        self.placa_input.text = ""
        self.ubicacion_inicial_input.text = ""
        self.ubicacion_final_input.text = ""
        self.hora_salida_input.text = ""
        self.hora_llegada_input.text = ""
        self.km_inicial_input.text = ""
        self.km_final_input.text = ""
        self.comentarios_input.text = ""
        self.foto_km_inicial_path = ""
        self.foto_km_final_path = ""


    def mostrar_popup_exito_imagen(self, image_path):
        """Muestra un popup de éxito con la imagen, centrada y con botón de cierre."""
        popup_layout = RelativeLayout()
        try:
            image = Image(source=image_path, size_hint=(None, None), allow_stretch=True, keep_ratio=True)
            def set_image_size(*args):
                popup_width = popup.width * 0.8
                popup_height = popup.height * 0.8
                image_ratio = image.texture_size[0] / image.texture_size[1] if image.texture_size[1] else 1

                if popup_width / image_ratio < popup_height:
                    image.width = popup_width
                    image.height = popup_width / image_ratio
                else:
                    image.height = popup_height
                    image.width = popup_height * image_ratio

            image.bind(texture_size=set_image_size)
            image.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
            popup_layout.add_widget(image)

        except Exception as e:
            error_label = Label(text=f"Error al cargar la imagen: {e}", font_size=20, color=(1, 0, 0, 1))
            popup_layout.add_widget(error_label)

        close_button = Button(
            text='x',
            size_hint=(None, None),
            size=(100, 100),
            background_color=(0, 1, 0, 1),
            pos_hint={'top': 1, 'right': 1}
        )
        close_button.bind(on_release=lambda btn: popup.dismiss())
        popup_layout.add_widget(close_button)
        popup = Popup(title='Éxito al cargar la imagen', content=popup_layout, size_hint=(0.8, 0.5))
        popup.bind(size=set_image_size)
        popup.open()

    def mostrar_popup_error(self, mensaje):
        popup = Popup(title='Error', content=Label(text=mensaje, font_size=40), size_hint=(0.8, 0.4))
        popup.open()

    def mostrar_popup_exito(self, mensaje):
        popup = Popup(title='Exito', content=Label(text=mensaje, font_size=40), size_hint=(0.8, 0.4))
        popup.open()

class FormularioApp(App):
    def build(self):
        return FormularioChofer()

if __name__ == '__main__':
    FormularioApp().run()