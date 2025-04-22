# Aplicación Móvil de Gestión de Rutas - SMONT y ARAGÓN

## Descripción General

La aplicación móvil de Gestión de Rutas es una herramienta diseñada específicamente para SMONT y ARAGÓN que permite a los conductores registrar información detallada sobre sus rutas, incluyendo datos de salida, llegada y documentación fotográfica de los vehículos. Esta aplicación facilita el seguimiento y control de la flota vehicular, mejorando la gestión logística y el mantenimiento de registros.

## Pantalla Principal, Formulario de Salida y Formulario de Llegada
![image](https://github.com/user-attachments/assets/c384764f-65a4-4f49-8cf8-ed824367d296)

## Funcionalidades Principales

### 1. Pantalla Principal
- Interfaz intuitiva con dos opciones principales: "DATOS DE SALIDA" y "DATOS DE LLEGADA"
- Diseño optimizado para dispositivos móviles con botones grandes y fáciles de usar

### 2. Formulario de Datos de Salida
- Registro completo de información al inicio de una ruta:
  - Nombre del conductor (con búsqueda y autocompletado)
  - Vehículo y placa (con selección asistida)
  - Fecha y hora de salida
  - Ubicación inicial
  - Kilometraje inicial
  - Observaciones adicionales
- Captura de hasta 4 fotografías del vehículo al inicio del recorrido
- Compresión automática de imágenes para optimizar el envío
- Validación de campos para asegurar información completa y correcta

### 3. Formulario de Datos de Llegada
- Registro detallado al finalizar una ruta:
  - Nombre del conductor
  - Vehículo y placa
  - Fecha y hora de llegada
  - Ubicación final
  - Kilometraje final
  - Observaciones sobre el recorrido o el estado del vehículo
- Captura de hasta 4 fotografías del vehículo al finalizar el recorrido
- Compresión automática de imágenes para optimizar el envío
- Validación de campos para asegurar información completa y correcta

### 4. Gestión de Fotografías
- Selección de imágenes desde la galería del dispositivo
- Visualización previa de las fotos seleccionadas
- Compresión inteligente que mantiene la calidad visual mientras reduce el tamaño del archivo
- Soporte para diferentes resoluciones de cámara

### 5. Sincronización con Servidor
- Envío de datos e imágenes al servidor central
- Indicador visual de progreso durante la transmisión
- Notificaciones claras sobre el éxito o fallo del envío
- Procesamiento de datos en segundo plano mientras se usa la aplicación.

## Guía de Uso

### Para Registrar Salida de Vehículo:
1. Abra la aplicación y seleccione "DATOS DE SALIDA"
2. Complete todos los campos requeridos
3. Tome o seleccione fotografías del vehículo (odómetro, estado general, etc.)
4. Presione "Enviar Salida"
5. Espere la confirmación de envío exitoso

### Para Registrar Llegada de Vehículo:
1. Abra la aplicación y seleccione "DATOS DE LLEGADA"
2. Complete todos los campos requeridos
3. Tome o seleccione fotografías del vehículo al final del recorrido
4. Presione "Enviar Llegada"
5. Espere la confirmación de envío exitoso

## Características Técnicas

- Interfaz responsiva adaptada a diferentes tamaños de pantalla
- Procesamiento eficiente de imágenes para reducir el consumo de datos
- Operaciones de red en hilos separados para mantener la fluidez de la aplicación
- Validación de datos para prevenir errores de registro
- Compatibilidad con múltiples versiones de Android
- Manejo de errores robusto con mensajes claros para el usuario

## Requisitos del Sistema

- Android 7.0 (Nougat) o superior
- Permisos de cámara y almacenamiento
- Conexión a Internet para sincronización de datos
- Espacio mínimo recomendado: 75MB

## Formato de los campos

A continuación, se detalla el formato esperado para cada uno de los campos del formulario.

**Nombre del Chofer:** ingresar texto y seleccionar de la lista desplegable.

**Vehículo:** ingresar texto y seleccionar de la lista desplegable.

**Placa:** se rellena automáticamente.

**Fecha de Salida / Fecha de Llegada:** fecha del día actual predefinido, pero se puede ingresar texto. Formato: `año-mes-dia` | Ejemplo: `2025-12-31`

**Hora de Salida / Hora de Retorno:** ingresar texto. Formato: `hh:mm` | Ejemplo: `23:59`

**Ubicación Inicial / Ubicación Final:** ingresar texto.

**Kilometraje Inicial / Kilometraje Final:** ingresar números enteros.

**Fotos de Inicio / Fotos de Fin:** Subir imágenes con el botón Subir Imagen.

**Observ. Salida / Observ. Llegada:** ingresar texto. Permite multilínea, es decir crea una nueva línea dando ENTER.

## Soporte y Contacto

Para soporte técnico o consultas sobre la aplicación, contacte al departamento de TI de SMONT y ARAGÓN o al desarrollador responsable.

---
