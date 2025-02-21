from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
import requests
import json
from datetime import datetime

class FormularioChofer(BoxLayout):
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Actualizar la fecha actual automáticamente
        Clock.schedule_once(self.set_fecha_actual)

    def set_fecha_actual(self, dt):
        self.fecha_input.text = datetime.now().strftime("%Y-%m-%d")

    def validar_campos(self):
        """Validar que los campos obligatorios estén llenos y sean válidos."""
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
        
        # Validar formato de hora (HH:MM)
        try:
            datetime.strptime(self.hora_salida_input.text, "%H:%M")
            datetime.strptime(self.hora_llegada_input.text, "%H:%M")
        except ValueError:
            self.mostrar_popup_error("Las horas deben estar en formato HH:MM (ej. 14:30).")
            return False
        
        # Validar kilometraje (números positivos)
        try:
            km_inicial = float(self.km_inicial_input.text)
            km_final = float(self.km_final_input.text)
            if km_inicial < 0 or km_final < 0 or km_final < km_inicial:
                self.mostrar_popup_error("El kilometraje debe ser positivo y el final mayor o igual al inicial.")
                return False
        except ValueError:
            self.mostrar_popup_error("El kilometraje debe ser un número válido.")
            return False
        
        return True

    def enviar_datos(self):
        """Enviar los datos al servidor Flask si pasan las validaciones."""
        if not self.validar_campos():
            return

        datos = {
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

        url = "http://tu_servidor_flask.com/api/recibir_datos"  # Reemplaza con tu URL real
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(url, data=json.dumps(datos), headers=headers, timeout=10)
            if response.status_code == 200:
                self.mostrar_popup_exito("Datos enviados exitosamente.")
                self.limpiar_formulario()
            else:
                self.mostrar_popup_error(f"Error del servidor: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.mostrar_popup_error(f"Error de conexión: {str(e)}")

    def limpiar_formulario(self):
        """Limpiar todos los campos después de un envío exitoso."""
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

    def mostrar_popup_exito(self, mensaje):
        popup = Popup(title='Éxito', content=Label(text=mensaje), size_hint=(0.8, 0.4))
        popup.open()

    def mostrar_popup_error(self, mensaje):
        popup = Popup(title='Error', content=Label(text=mensaje), size_hint=(0.8, 0.4))
        popup.open()

class FormularioApp(App):
    def build(self):
        return FormularioChofer()

if __name__ == '__main__':
    FormularioApp().run()