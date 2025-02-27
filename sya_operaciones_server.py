import os
import logging
from datetime import datetime
import pandas as pd
import openpyxl
from flask import Flask, request, jsonify, send_file, send_from_directory
import zipfile

app = Flask(__name__)

# Usar una ruta absoluta para el archivo Excel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE = os.path.join(BASE_DIR, "registros_trabajo.xlsx")
REQUERIMIENTOS_EXCEL_FILE = os.path.join(BASE_DIR, "requerimientos_obra.xlsx")
MATERIALES_CSV_PATH = os.path.join(BASE_DIR, "operaciones_materiales.csv")
EQUIPOS_CSV_PATH = os.path.join(BASE_DIR, "operaciones_equipos.csv")
VEHICULOS_CSV_PATH = os.path.join(BASE_DIR, "operaciones_vehiculos.csv")
PERSONAL_CSV_PATH = os.path.join(BASE_DIR, "operaciones_personal.csv")

# --- Archivo Excel y directorio para registros de choferes ---
REGISTROS_CHOFERES_EXCEL = os.path.join(BASE_DIR, "registros_choferes.xlsx")
FOTOS_KM_DIR = os.path.join(BASE_DIR, "fotos_km")

# --- Ruta al archivo CSV de conductores y vehiculos---
CONDUCTORES_CSV_PATH = os.path.join(BASE_DIR, "aem_conductores.csv")
VEHICULOS_INFO_CSV_PATH = os.path.join(BASE_DIR, "aem_vehiculos.csv")

# Configuración de logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def inicializar_excel():
    # Inicializar Excel de Reporte Diario (código existente, sin cambios)
    if not os.path.exists(EXCEL_FILE):
        logging.info(f"Creando archivo Excel de reporte diario en: {EXCEL_FILE}")
        wb = openpyxl.Workbook()
        ws1 = wb.active
        ws1.title = "Reporte Principal"
        headers_reporte = [
            "Fecha", "Código Obra", "Nombre Ingeniero",
            "Nombre Supervisor", "Actividad Principal",
            "Supervisor Presente", "Avance Diario",
            "Incidentes", "Plan Siguiente Día", "Observaciones"
        ]
        ws1.append(headers_reporte)
        ws2 = wb.create_sheet(title="Materiales Usados")
        headers_materiales = ["Fecha", "Código Obra", "Nombre Ingeniero"]
        ws2.append(headers_materiales)
        ws3 = wb.create_sheet(title="Equipos Usados")
        headers_equipos = ["Fecha", "Código Obra", "Nombre Ingeniero"]
        ws3.append(headers_equipos)
        ws4 = wb.create_sheet(title="Vehículos Usados")
        headers_vehiculos = ["Fecha", "Código Obra", "Nombre Ingeniero"]
        ws4.append(headers_vehiculos)
        ws5 = wb.create_sheet(title="Personal de Campo")
        headers_personal = ["Fecha", "Código Obra", "Nombre Ingeniero"]
        ws5.append(headers_personal)
        wb.save(EXCEL_FILE)
    else:
        logging.info(f"El archivo Excel de reporte diario ya existe en: {EXCEL_FILE}")

    # Inicializar Excel de Requerimientos (código existente, sin cambios)
    if not os.path.exists(REQUERIMIENTOS_EXCEL_FILE):
        logging.info(f"Creando archivo Excel de requerimientos en: {REQUERIMIENTOS_EXCEL_FILE}")
        wb_req = openpyxl.Workbook()
        ws_req = wb_req.active
        ws_req.title = "Requerimientos"
        headers_requerimientos_inicial = ["Fecha", "Código Obra", "Nombre Ingeniero"]
        ws_req.append(headers_requerimientos_inicial)
        wb_req.save(REQUERIMIENTOS_EXCEL_FILE)
    else:
        logging.info(f"El archivo Excel de requerimientos ya existe en: {REQUERIMIENTOS_EXCEL_FILE}")

    # --- Inicializar Excel de Registros de Choferes ---
    if not os.path.exists(REGISTROS_CHOFERES_EXCEL):
        logging.info(f"Creando archivo Excel de registros de choferes en: {REGISTROS_CHOFERES_EXCEL}")
        wb_choferes = openpyxl.Workbook()
        ws_choferes = wb_choferes.active
        ws_choferes.title = "Registros"
        headers_choferes = ["Nombre del Chofer", "Vehículo", "Placa", "Fecha de Salida", "Hora de Salida", 
            "Ubicación Inicial", "Kilometraje Inicial", "Fotos de Inicio", "Observaciones"]
        ws_choferes.append(headers_choferes)
        wb_choferes.save(REGISTROS_CHOFERES_EXCEL)
    else:
        logging.info(f"El archivo Excel de registros de choferes ya existe en: {REGISTROS_CHOFERES_EXCEL}")

    # --- Crear directorio de fotos si no existe ---
    if not os.path.exists(FOTOS_KM_DIR):
        os.makedirs(FOTOS_KM_DIR)
        logging.info(f"Directorio de fotos creado: {FOTOS_KM_DIR}")

def actualizar_cabeceras_materiales(ws, num_materiales):
    headers = list(ws.rows)[0] # Correct way to get headers in openpyxl
    num_headers_actuales = len(headers)

    ultimo_material = 0
    for header in headers:
        header_value = header.value
        if header_value and header_value.startswith("Material"):
            try:
                numero = int(header_value.split(" ")[1])
                ultimo_material = max(ultimo_material, numero)
            except ValueError:
                pass

    if ultimo_material >= num_materiales:
        return

    for i in range(ultimo_material + 1, num_materiales + 1):
        ws.cell(row=1, column=num_headers_actuales + 1, value=f"Material {i}")
        ws.cell(row=1, column=num_headers_actuales + 2, value=f"Unidad {i}")
        ws.cell(row=1, column=num_headers_actuales + 3, value=f"Cantidad {i}")
        num_headers_actuales += 3

def actualizar_cabeceras_equipos(ws, num_equipos):
    headers = list(ws.rows)[0] # Correct way to get headers in openpyxl
    num_headers_actuales = len(headers)

    ultimo_equipo = 0
    for header in headers:
        header_value = header.value
        if header_value and header_value.startswith("Equipo"):
            try:
                numero = int(header_value.split(" ")[1])
                ultimo_equipo = max(ultimo_equipo, numero)
            except ValueError:
                pass

    if ultimo_equipo >= num_equipos:
        return

    for i in range(ultimo_equipo + 1, num_equipos + 1):
        ws.cell(row=1, column=num_headers_actuales + 1, value=f"Equipo {i}")
        ws.cell(row=1, column=num_headers_actuales + 2, value=f"Cantidad {i}")
        ws.cell(row=1, column=num_headers_actuales + 3, value=f"Propiedad {i}")
        num_headers_actuales += 3

def actualizar_cabeceras_vehiculos(ws, num_vehiculos):
    headers = list(ws.rows)[0] # Correct way to get headers in openpyxl
    num_headers_actuales = len(headers)

    ultimo_vehiculo = 0
    for header in headers:
        header_value = header.value
        if header_value and header_value.startswith("Vehículo"):
            try:
                numero = int(header_value.split(" ")[1])
                ultimo_vehiculo = max(ultimo_vehiculo, numero)
            except ValueError:
                pass

    if ultimo_vehiculo >= num_vehiculos:
        return

    for i in range(ultimo_vehiculo + 1, num_vehiculos + 1):
        ws.cell(row=1, column=num_headers_actuales + 1, value=f"Vehículo {i}")
        ws.cell(row=1, column=num_headers_actuales + 2, value=f"Placa {i}")
        ws.cell(row=1, column=num_headers_actuales + 3, value=f"Propiedad {i}")
        num_headers_actuales += 3

def actualizar_cabeceras_personal(ws, num_personal):
    headers = list(ws.rows)[0] # Correct way to get headers in openpyxl
    num_headers_actuales = len(headers)

    ultimo_personal = 0
    for header in headers:
        header_value = header.value
        if header_value and header_value.startswith("Personal"):
            try:
                numero = int(header_value.split(" ")[1])
                ultimo_personal = max(ultimo_personal, numero)
            except ValueError:
                pass

    if ultimo_personal >= num_personal:
        return

    for i in range(ultimo_personal + 1, num_personal + 1):
        ws.cell(row=1, column=num_headers_actuales + 1, value=f"Personal {i}")
        ws.cell(row=1, column=num_headers_actuales + 2, value=f"Categoría {i}")
        ws.cell(row=1, column=num_headers_actuales + 3, value=f"Horas extras {i}")
        num_headers_actuales += 3

def actualizar_cabeceras_requerimientos(ws, num_items):
    headers = list(ws.rows)[0] # Correct way to get headers in openpyxl
    num_headers_actuales = len(headers)

    ultimo_item = 0
    for header in headers:
        header_value = header.value
        if header_value and header_value.startswith("Artículo"):
            try:
                numero = int(header_value.split(" ")[1])
                ultimo_item = max(ultimo_item, numero)
            except ValueError:
                pass

    if ultimo_item >= num_items:
        return

    for i in range(ultimo_item + 1, num_items + 1):
        ws.cell(row=1, column=num_headers_actuales + 1, value=f"Artículo {i}")
        ws.cell(row=1, column=num_headers_actuales + 2, value=f"Unidad {i}")
        ws.cell(row=1, column=num_headers_actuales + 3, value=f"Cantidad {i}")
        num_headers_actuales += 3


def procesar_datos(datos):
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE)
        ws_reporte = wb["Reporte Principal"]
        ws_materiales = wb["Materiales Usados"]
        ws_equipos = wb["Equipos Usados"]
        ws_vehiculos = wb["Vehículos Usados"]
        ws_personal = wb["Personal de Campo"]


        # Preparar fila de datos para "Reporte Principal"
        fila_reporte = [
            # Formatear la fecha como DATE en "Reporte Principal"
            datetime.strptime(datos.get('fecha', ''), '%d/%m/%Y').date(),  # Fecha como date
            datos.get('codigo_obra', ''),
            datos.get('nombre_ingeniero', ''),
            datos.get('nombre_supervisor', ''),
            datos.get('actividad_principal', ''),
            'Sí' if datos.get('supervisor_presente', False) else 'No',
            datos.get('avance_diario', ''),
            datos.get('incidentes', ''),
            datos.get('siguiente_dia', ''),
            datos.get('observaciones', '')
        ]
        ws_reporte.append(fila_reporte)

        # Procesar materiales usados para "Materiales Usados"
        materiales = datos.get('materiales_usados', [])
        actualizar_cabeceras_materiales(ws_materiales, len(materiales))
        fila_materiales = [
            datetime.strptime(datos.get('fecha', ''), '%d/%m/%Y').date(),
            datos.get('codigo_obra', ''),
            datos.get('nombre_ingeniero', '')
        ]
        for material in materiales:
            fila_materiales.extend([material['nombre'], material['unidad'], material['cantidad']])
        ws_materiales.append(fila_materiales)

        # Procesar equipos usados
        equipos = datos.get('equipos_usados', [])
        actualizar_cabeceras_equipos(ws_equipos, len(equipos))
        fila_equipos = [
            datetime.strptime(datos.get('fecha', ''), '%d/%m/%Y').date(),
            datos.get('codigo_obra', ''),
            datos.get('nombre_ingeniero', '')
        ]
        for equipo in equipos:
            fila_equipos.extend([equipo['nombre'], equipo['cantidad'], equipo['propiedad']])
        ws_equipos.append(fila_equipos)

        # Procesar vehículos usados
        vehiculos = datos.get('vehiculos_usados', [])
        actualizar_cabeceras_vehiculos(ws_vehiculos, len(vehiculos))
        fila_vehiculos = [
            datetime.strptime(datos.get('fecha', ''), '%d/%m/%Y').date(),
            datos.get('codigo_obra', ''),
            datos.get('nombre_ingeniero', '')
        ]
        for vehiculo in vehiculos:
            fila_vehiculos.extend([vehiculo['nombre'], vehiculo['placa'], vehiculo['propiedad']])
        ws_vehiculos.append(fila_vehiculos)

        # Procesar personal de campo
        personal_campo = datos.get('personal_de_campo', [])
        actualizar_cabeceras_personal(ws_personal, len(personal_campo))
        fila_personal = [
            datetime.strptime(datos.get('fecha', ''), '%d/%m/%Y').date(),
            datos.get('codigo_obra', ''),
            datos.get('nombre_ingeniero', '')
        ]
        for personal in personal_campo:
            fila_personal.extend([personal['nombre_completo'], personal['categoria'], personal['horas_extras']])
        ws_personal.append(fila_personal)


        wb.save(EXCEL_FILE)
        logging.info(f"Datos recibidos de {datos.get('nombre_ingeniero', 'Unknown')} procesados exitosamente")

    except Exception as e:
        logging.error(f"Error al procesar datos: {str(e)}")

def procesar_requerimientos(datos):
    logging.info("Datos de requerimientos recibidos:")
    logging.info(datos)  # Log the received data for debugging
    try:
        wb_req = openpyxl.load_workbook(REQUERIMIENTOS_EXCEL_FILE)
        ws_requerimientos = wb_req["Requerimientos"]

        requerimientos = datos.get('requerimientos', [])
        actualizar_cabeceras_requerimientos(ws_requerimientos, len(requerimientos))

        fila_requerimientos = [
            datetime.strptime(datos.get('fecha', ''), '%d/%m/%Y').date(), # Fecha actual si no viene
            datos.get('codigo_obra', ''),
            datos.get('nombre_ingeniero', '')
        ]
        for req in requerimientos:
            fila_requerimientos.extend([req['nombre'], req['unidad'], req['cantidad']])
        ws_requerimientos.append(fila_requerimientos)

        wb_req.save(REQUERIMIENTOS_EXCEL_FILE)
        logging.info(f"Requerimientos recibidos de {datos.get('nombre_ingeniero', 'Unknown')} procesados exitosamente")

    except Exception as e:
        logging.exception(f"Error al procesar requerimientos: {str(e)}") # Log exception details


def descargar_excel_flask():
    try:
        logging.info(f"Intentando enviar archivo: {EXCEL_FILE}")
        return send_file(EXCEL_FILE, as_attachment=True)
    except Exception as e:
        logging.error(f"Error al generar descarga de Excel: {str(e)}")
        return str(e), 500

def descargar_requerimientos_excel_flask():
    try:
        logging.info(f"Intentando enviar archivo de requerimientos: {REQUERIMIENTOS_EXCEL_FILE}")
        return send_file(REQUERIMIENTOS_EXCEL_FILE, as_attachment=True, download_name='requerimientos_obra.xlsx')
    except Exception as e:
        logging.error(f"Error al generar descarga de Excel de requerimientos: {str(e)}")
        return str(e), 500


def agregar_nuevo_material_csv(nombre_material, unidad):
    try:
        df = pd.read_csv(MATERIALES_CSV_PATH)
        nuevo_material = pd.DataFrame([{'nombre_material': nombre_material, 'unidad': unidad}])
        df = pd.concat([df, nuevo_material], ignore_index=True)
        df.to_csv(MATERIALES_CSV_PATH, index=False)
        logging.info(f"Nuevo material '{nombre_material}' agregado a {MATERIALES_CSV_PATH}")
        return True
    except Exception as e:
        logging.error(f"Error al agregar nuevo material a CSV: {str(e)}")
        return False

def agregar_nuevo_equipo_csv(nombre_equipo, propiedad):
    try:
        df = pd.read_csv(EQUIPOS_CSV_PATH)
        nuevo_equipo = pd.DataFrame([{'nombre_equipo': nombre_equipo, 'propiedad': propiedad}])
        df = pd.concat([df, nuevo_equipo], ignore_index=True)
        df.to_csv(EQUIPOS_CSV_PATH, index=False)
        logging.info(f"Nuevo equipo '{nombre_equipo}' agregado a {EQUIPOS_CSV_PATH}")
        return True
    except Exception as e:
        logging.error(f"Error al agregar nuevo equipo a CSV: {str(e)}")
        return False

def agregar_nuevo_vehiculo_csv(nombre_vehiculo, placa, propiedad):
    try:
        df = pd.read_csv(VEHICULOS_CSV_PATH)
        nuevo_vehiculo = pd.DataFrame([{'nombre_vehiculo': nombre_vehiculo, 'placa': placa, 'propiedad': propiedad}])
        df = pd.concat([df, nuevo_vehiculo], ignore_index=True)
        df.to_csv(VEHICULOS_CSV_PATH, index=False)
        logging.info(f"Nuevo vehículo '{nombre_vehiculo}' agregado a {VEHICULOS_CSV_PATH}")
        return True
    except Exception as e:
        logging.error(f"Error al agregar nuevo vehículo a CSV: {str(e)}")
        return False

def agregar_nuevo_personal_csv(apellido_paterno, apellido_materno, nombres, categoria):
    try:
        df = pd.read_csv(PERSONAL_CSV_PATH)
        nuevo_personal = pd.DataFrame([{
            'AP. PATERNO': apellido_paterno,
            'AP. MATERNO': apellido_materno,
            'NOMBRES': nombres,
            'CATEGORIA': categoria
        }])
        df = pd.concat([df, nuevo_personal], ignore_index=True)
        df.to_csv(PERSONAL_CSV_PATH, index=False)
        logging.info(f"Nuevo personal '{nombres} {apellido_paterno}' agregado a {PERSONAL_CSV_PATH}")
        return True
    except Exception as e:
        logging.error(f"Error al agregar nuevo personal a CSV: {str(e)}")
        return False


# Inicializar Excel al inicio
inicializar_excel()

#----------------- Existing routes ----------------
@app.route('/api/materiales', methods=['GET'])
def get_materiales():
    try:
        df = pd.read_csv(MATERIALES_CSV_PATH)
        materiales = df.to_dict(orient='records')
        return jsonify(materiales)
    except FileNotFoundError:
        return jsonify({"error": f"No se encontró el archivo de materiales en {MATERIALES_CSV_PATH}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/equipos', methods=['GET'])
def get_equipos():
    try:
        df = pd.read_csv(EQUIPOS_CSV_PATH)
        equipos = df.to_dict(orient='records')
        return jsonify(equipos)
    except FileNotFoundError:
        return jsonify({"error": f"No se encontró el archivo de equipos en {EQUIPOS_CSV_PATH}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/vehiculos', methods=['GET'])
def get_vehiculos():
    try:
        df = pd.read_csv(VEHICULOS_CSV_PATH)
        vehiculos = df.to_dict(orient='records')
        return jsonify(vehiculos)
    except FileNotFoundError:
        return jsonify({"error": f"No se encontró el archivo de vehículos en {VEHICULOS_CSV_PATH}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/personal', methods=['GET'])
def get_personal():
    try:
        df = pd.read_csv(PERSONAL_CSV_PATH)
        personal = df.to_dict(orient='records')
        return jsonify(personal)
    except FileNotFoundError:
        return jsonify({"error": f"No se encontró el archivo de personal en {PERSONAL_CSV_PATH}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/materiales/new', methods=['POST'])
def new_material():
    data = request.json
    if not data or 'nombre_material' not in data or 'unidad' not in data:
        return jsonify({"error": "Nombre de material y unidad son requeridos"}), 400
    if agregar_nuevo_material_csv(data['nombre_material'], data['unidad']):
        return jsonify({"status": "success"}), 201
    else:
        return jsonify({"error": "Error al agregar nuevo material"}), 500

@app.route('/api/equipos/new', methods=['POST'])
def new_equipo():
    data = request.json
    if not data or 'nombre_equipo' not in data or 'propiedad' not in data:
        return jsonify({"error": "Nombre de equipo y propiedad son requeridos"}), 400
    if agregar_nuevo_equipo_csv(data['nombre_equipo'], data['propiedad']):
        return jsonify({"status": "success"}), 201
    else:
        return jsonify({"error": "Error al agregar nuevo equipo"}), 500

@app.route('/api/vehiculos/new', methods=['POST'])
def new_vehiculo():
    data = request.json
    if not data or 'nombre_vehiculo' not in data or 'placa' not in data or 'propiedad' not in data:
        return jsonify({"error": "Nombre de vehículo, placa y propiedad son requeridos"}), 400
    if agregar_nuevo_vehiculo_csv(data['nombre_vehiculo'], data['placa'], data['propiedad']):
        return jsonify({"status": "success"}), 201
    else:
        return jsonify({"error": "Error al agregar nuevo vehículo"}), 500

@app.route('/api/personal/new', methods=['POST'])
def new_personal():
    data = request.json
    if not data or 'nombre_completo' not in data or 'categoria' not in data:
        return jsonify({"error": "Nombre completo y categoría de personal son requeridos"}), 400

    nombre_completo = data['nombre_completo']
    partes_nombre = nombre_completo.split(',')
    if len(partes_nombre) != 2:
        return jsonify({"error": "Formato de nombre incorrecto. Debe ser 'apellido_paterno apellido_materno, nombres'"}), 400

    apellidos_str, nombres = partes_nombre
    apellidos_partes = apellidos_str.strip().split()
    if not apellidos_partes:
        return jsonify({"error": "Apellido paterno requerido"}), 400
    apellido_paterno = apellidos_partes[0]
    apellido_materno = apellidos_partes[1] if len(apellidos_partes) > 1 else ''

    if agregar_nuevo_personal_csv(apellido_paterno, apellido_materno, nombres.strip(), data['categoria']):
        return jsonify({"status": "success"}), 201
    else:
        return jsonify({"error": "Error al agregar nuevo personal"}), 500


@app.route('/recibir-datos', methods=['POST'])
def recibir_datos():
    datos = request.json
    procesar_datos(datos)
    return jsonify({"status": "success"})

@app.route('/recibir-requerimientos', methods=['POST'])
def recibir_requerimientos_route(): # Corrected route name
    datos = request.json
    print("Datos recibidos en /recibir-requerimientos:", datos) # Log received data
    procesar_requerimientos(datos)
    return jsonify({"status": "success"})

@app.route('/descargar-excel', methods=['GET'])
def descargar_excel_route():
    return descargar_excel_flask()

@app.route('/descargar-requerimientos-excel', methods=['GET'])
def descargar_requerimientos_excel_route():
    return descargar_requerimientos_excel_flask()
#----------------------------------------------------


# --- Función para procesar datos de choferes ---
def procesar_datos_choferes(data, files):
    try:
        wb_choferes = openpyxl.load_workbook(REGISTROS_CHOFERES_EXCEL)
        ws_choferes = wb_choferes.active

        # Nuevo orden de los campos:
        fila = [
            data.get("nombre_chofer"),
            data.get("vehiculo"),
            data.get("placa"),
            data.get("fecha_salida"),       # antes era "fecha"
            data.get("hora_salida"),
            data.get("ubicacion_inicial"),
            data.get("km_inicial"),
            data.get("observaciones")       # antes era "comentarios"
        ]
        ws_choferes.append(fila)
        wb_choferes.save(REGISTROS_CHOFERES_EXCEL)

        # --- Procesar la imagen de Fotos de Inicio ---
        if not os.path.exists(FOTOS_KM_DIR):
            os.makedirs(FOTOS_KM_DIR)

        # Ahora la imagen se recibe con el nombre "fotos_inicio"
        foto_inicio = files.get("fotos_inicio")
        if foto_inicio:
            path_inicio = os.path.join(FOTOS_KM_DIR, foto_inicio.filename)
            foto_inicio.save(path_inicio)
            # Aquí podrías actualizar el Excel con el nombre del archivo si lo requieres

        logging.info("Datos de choferes recibidos y guardados correctamente.")
        return True

    except Exception as e:
        logging.error(f"Error al procesar datos de choferes: {str(e)}")
        return False


# --- Ruta para recibir datos de choferes ---
@app.route('/api/recibir_datos_choferes', methods=['POST'])
def recibir_datos_choferes():
    if procesar_datos_choferes(request.form, request.files):
        return jsonify({"status": "success", "message": "Datos de choferes recibidos y guardados"}), 200
    else:
        return jsonify({"status": "error", "message": "Error al guardar datos de choferes"}), 500

# --- Ruta para obtener la lista de conductores ---
@app.route('/api/conductores', methods=['GET'])
def get_conductores():
    try:
        df = pd.read_csv(CONDUCTORES_CSV_PATH)
        # Asegurarse de que la columna 'conductor' exista y convertir los valores a string
        if 'conductor' in df.columns:
            conductores = df['conductor'].dropna().astype(str).tolist()
        else:
            conductores = []  # O devolver un error si la columna es esencial
            logging.warning(f"La columna 'conductor' no se encontró en {CONDUCTORES_CSV_PATH}")

        return jsonify(conductores)
    except FileNotFoundError:
        logging.error(f"No se encontró el archivo {CONDUCTORES_CSV_PATH}")
        return jsonify({"error": f"No se encontró el archivo de conductores"}), 404
    except Exception as e:
        logging.error(f"Error al leer el archivo de conductores: {str(e)}")
        return jsonify({"error": str(e)}), 500

# --- Ruta para obtener información de vehículos (tipo y placa) ---
@app.route('/api/vehiculos_info', methods=['GET'])
def get_vehiculos_info():
    try:
        df = pd.read_csv(VEHICULOS_INFO_CSV_PATH)
        # Asegurarse de que las columnas necesarias existan
        if 'tipo_vehiculo' in df.columns and 'placa' in df.columns:
            # Convertir a un diccionario con la estructura deseada
            vehiculos = df[['tipo_vehiculo', 'placa']].dropna().astype(str).to_dict('records')
            return jsonify(vehiculos)
        else:
            missing_cols = []
            if 'tipo_vehiculo' not in df.columns:
                missing_cols.append('tipo_vehiculo')
            if 'placa' not in df.columns:
                missing_cols.append('placa')

            logging.warning(f"Faltan columnas en {VEHICULOS_INFO_CSV_PATH}: {', '.join(missing_cols)}")
            return jsonify({"error": f"Faltan columnas: {', '.join(missing_cols)}"}), 400 # Bad Request

    except FileNotFoundError:
        logging.error(f"No se encontró el archivo {VEHICULOS_INFO_CSV_PATH}")
        return jsonify({"error": f"No se encontró el archivo de vehículos"}), 404
    except Exception as e:
        logging.error(f"Error al leer el archivo de vehículos: {str(e)}")
        return jsonify({"error": str(e)}), 500

# --- NUEVAS RUTAS PARA LA APP DE ESCRITORIO ---
@app.route('/descargar-registro-rutas', methods=['GET'])
def descargar_registro_rutas():
    """Descarga el archivo Excel de registros de choferes."""
    try:
        logging.info(f"Intentando enviar archivo de registro de rutas: {REGISTROS_CHOFERES_EXCEL}")
        return send_file(REGISTROS_CHOFERES_EXCEL, as_attachment=True, download_name='registros_choferes.xlsx')
    except Exception as e:
        logging.error(f"Error al generar descarga de Excel de registros de choferes: {str(e)}")
        return str(e), 500

@app.route('/descargar-carpeta-fotos', methods=['GET'])
def descargar_carpeta_fotos():
    """Comprime y descarga la carpeta de fotos de kilometraje."""
    try:
        # Comprimir la carpeta
        zip_file_path = os.path.join(BASE_DIR, "fotos_km.zip")
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(FOTOS_KM_DIR):
                for file in files:
                    zipf.write(os.path.join(root, file),
                               os.path.relpath(os.path.join(root, file),
                                               os.path.join(FOTOS_KM_DIR, '..')))

        logging.info(f"Intentando enviar carpeta de fotos comprimida: {zip_file_path}")
        return send_file(zip_file_path, as_attachment=True, download_name='fotos_km.zip')
    except Exception as e:
        logging.error(f"Error al comprimir o descargar la carpeta de fotos: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)