# main.py (con bloqueo de botón y persistencia de datos)

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty  # Import BooleanProperty
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout  # No se usa
from kivy.uix.relativelayout import RelativeLayout
from kivy import platform
import requests
import json
from datetime import datetime
from plyer import filechooser
import os
import logging
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput # No se usa
from kivy.metrics import dp
from kivy.core.window import Window  # No se usa
from kivy.animation import Animation


if platform == "android":
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE,
                           Permission.WRITE_EXTERNAL_STORAGE])
    except ImportError:
        pass

class FormularioChofer(BoxLayout):
    """Formulario para ingresar datos del chofer y enviarlos al servidor."""
    nombre_input = ObjectProperty(None)
    vehiculo_input = ObjectProperty(None)
    placa_input = ObjectProperty(None)
    fecha_salida_input = ObjectProperty(None)
    hora_salida_input = ObjectProperty(None)
    ubicacion_inicial_input = ObjectProperty(None)
    km_inicial_input = ObjectProperty(None)
    observaciones_input = ObjectProperty(None)

    fotos_inicio_path = StringProperty("")

    btn_km_inicial_color = ListProperty([0, 0.5, 0.8, 1])

    dropdown_chofer = ObjectProperty(None)
    selected_chofer = StringProperty("")
    dropdown_vehiculo = ObjectProperty(None)
    selected_vehiculo = StringProperty("")

    # Nueva propiedad para controlar el estado del botón Enviar
    enviar_btn_disabled = BooleanProperty(False)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.store_original_position, 0)
        Clock.schedule_once(self.set_fecha_actual)
        Clock.schedule_once(self.setup_dropdowns)
        Clock.schedule_once(self.setup_observaciones)
        self.conductores = []
        self.vehiculos = []

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

        self.cargar_conductores()
        self.cargar_vehiculos()

    def setup_observaciones(self, dt):
        """Configura el comportamiento del campo de observaciones."""
        self.observaciones_input.bind(focus=self.on_observaciones_focus)

    def on_observaciones_focus(self, instance, value):
        """Anima el formulario al enfocar/desenfocar el campo de observaciones."""
        offset = dp(150)
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

    def cargar_conductores(self):
        """Carga la lista de conductores desde el servidor."""
        url = "http://34.67.103.132:5000/api/conductores"  # Cambia a la IP de tu servidor
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            self.conductores = response.json()
        except requests.exceptions.RequestException as e:
            self.mostrar_popup_error(f"Error al cargar conductores: {e}")
            logging.error(f"Error al cargar conductores: {e}")
        except ValueError as e:
            self.mostrar_popup_error(f"Error al procesar respuesta (conductores): {e}")
            logging.error(f"Error al procesar respuesta (conductores): {e}")

    def seleccionar_conductor(self, conductor):
        """Establece el conductor seleccionado."""
        self.nombre_input.text = conductor
        self.selected_chofer = conductor
        self.dropdown_chofer.dismiss()

    def cargar_vehiculos(self):
        """Carga la lista de vehículos desde el servidor."""
        url = "http://34.67.103.132:5000/api/vehiculos_info"  # Cambia a la IP de tu servidor
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            self.vehiculos = response.json()
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
            km_inicial = float(self.km_inicial_input.text)
            # Considera si realmente necesitas restringir a valores positivos.
        except ValueError:
            self.mostrar_popup_error("El kilometraje debe ser un número válido.")
            return False

        return True

    def seleccionar_foto_km_inicial(self):
        """Abre el selector de archivos para elegir la foto del km inicial."""
        def on_selection(selection):
            if selection:
                self.fotos_inicio_path = selection[0]
                self.btn_km_inicial_color = [0, 0.8, 0, 1]  # Verde
                self.mostrar_popup_exito_imagen(self.fotos_inicio_path)
            else:
                self.fotos_inicio_path = ""
                self.btn_km_inicial_color = [0, 0.5, 0.8, 1]

        filechooser.open_file(
            on_selection=on_selection,
            title="Seleccionar Foto km Inicial",
            filters=[("Image Files", "*.jpg;*.jpeg;*.png")]
        )

    def enviar_datos(self):
        """Envía los datos del formulario al servidor."""
        if not self.validar_campos():
            return

        payload = {
            "nombre_chofer": self.nombre_input.text,
            "vehiculo": self.vehiculo_input.text,
            "placa": self.placa_input.text,
            "fecha_salida": self.fecha_salida_input.text,
            "hora_salida": self.hora_salida_input.text,
            "ubicacion_inicial": self.ubicacion_inicial_input.text,
            "km_inicial": self.km_inicial_input.text,
            "observaciones": self.observaciones_input.text
        }

        files = {}
        if self.fotos_inicio_path:
            try:
                files["foto_km_inicial"] = (
                    os.path.basename(self.fotos_inicio_path),
                    open(self.fotos_inicio_path, 'rb'),
                    "image/jpeg"
                )
            except Exception as e:
                self.mostrar_popup_error(f"No se pudo abrir la imagen: {e}")
                return

        url = "http://127.0.0.1:5000/api/recibir_datos_choferes"

        try:
            response = requests.post(url, data=payload, files=files, timeout=30)
            response.raise_for_status()
            self.mostrar_popup_exito("Datos enviados exitosamente.")
            # self.limpiar_formulario()  # NO limpiar el formulario
            self.enviar_btn_disabled = True  # Deshabilitar el botón

        except requests.exceptions.RequestException as e:
            self.mostrar_popup_error(f"Error de conexión: {e}")
        finally:
            for _, file_info in files.items():
                if file_info: # Verifica que file_info no sea None.
                    file_info[1].close()


    def limpiar_formulario(self):
        """Limpia los campos del formulario (ahora solo se usa para reiniciar)."""
        self.fecha_salida_input.text = datetime.now().strftime("%Y-%m-%d")
        self.nombre_input.text = ""
        self.vehiculo_input.text = ""
        self.placa_input.text = ""
        self.ubicacion_inicial_input.text = ""
        self.hora_salida_input.text = ""
        self.km_inicial_input.text = ""
        self.observaciones_input.text = ""
        self.fotos_inicio_path = ""
        self.btn_km_inicial_color = [0, 0.5, 0.8, 1]
        self.enviar_btn_disabled = False  # Habilitar el botón nuevamente


    def mostrar_popup_exito_imagen(self, image_path):
        """Muestra un popup con la imagen seleccionada."""
        popup_layout = RelativeLayout()
        try:
            image = Image(source=image_path, size_hint=(None, None), allow_stretch=True, keep_ratio=True)
            def set_image_size(*args):
                if image.texture_size[0] == 0 or image.texture_size[1] == 0:
                    return
                popup_width = popup.width * 0.8
                popup_height = popup.height * 0.8
                image_ratio = image.texture_size[0] / image.texture_size[1]

                if popup_width / image_ratio < popup_height:
                    image.width = popup_width
                    image.height = popup_width / image_ratio
                else:
                    image.height = popup_height
                    image.width = popup_height * image_ratio

            image.bind(texture_size=set_image_size)
            image.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
            popup_layout.add_widget(image)

            close_button = Button(
                text='x',
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                background_color=(0, 1, 0, 1),
                pos_hint={'top': 1, 'right': 1}
            )
            close_button.bind(on_release=lambda btn: popup.dismiss())
            popup_layout.add_widget(close_button)

            popup = Popup(title='Éxito', content=popup_layout, size_hint=(0.8, 0.5))
            image.bind(on_load=lambda *args: set_image_size())
            popup.bind(size=lambda *args: set_image_size())
            popup.open()

        except Exception as e:
            error_label = Label(text=f"Error al cargar la imagen: {e}", font_size=dp(20), color=(1, 0, 0, 1))
            popup_layout.add_widget(error_label)

    def mostrar_popup_error(self, mensaje):
        """Muestra un popup de error."""
        popup = Popup(title='Error', content=Label(text=mensaje, font_size=dp(20)), size_hint=(0.8, 0.4))
        popup.open()

    def mostrar_popup_exito(self, mensaje):
        """Muestra un popup de éxito."""
        popup = Popup(title='Éxito', content=Label(text=mensaje, font_size=dp(20)), size_hint=(0.8, 0.4))
        popup.open()

class FormularioApp(App):
    """Aplicación principal."""
    def build(self):
        return FormularioChofer()

if __name__ == '__main__':
    FormularioApp().run()