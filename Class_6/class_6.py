
import streamlit as st
import time



# 1. ELEMENTOS BÁSICOS DE STREAMLIT


st.title("Mi página")

st.checkbox("Checkbox")

st.radio(
    "Selecciona un color:",
    ["Azul", "Rojo", "Verde"]
)

st.button("Presiona")

st.selectbox(
    "Selecciona otro color:",
    ["Verde", "Azul", "Rojo"]
)



# 2. REGISTRO DE INFORMACIÓN PERSONAL


st.title("Registro de información personal")

st.write("Complete el siguiente formulario")



# 3. CREACIÓN DEL FORMULARIO

with st.form("formulario_registro"):

    st.header("Datos personales")

    # Columnas
    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Ingrese su nombre")

    with col2:
        apellido = st.text_input("Ingrese su apellido")

    # Área de texto
    descripcion = st.text_area("Escriba una descripción")

    # Fecha y hora
    fecha = st.date_input("Seleccione una fecha")

    hora = st.time_input("Seleccione una hora")

    # Cargar archivo
    archivo = st.file_uploader(
        "Seleccione un archivo",
        type=["txt", "pdf", "jpg", "png"]
    )

    # Botón para enviar
    enviar = st.form_submit_button("Registrar")



# 4. PROCESAMIENTO DE LA INFORMACIÓN


if enviar:

    st.success("Información registrada correctamente")

    st.subheader("Datos ingresados")

    # Mostrar datos
    st.write("Nombre:", nombre)
    st.write("Apellido:", apellido)
    st.write("Descripción:", descripcion)
    st.write("Fecha:", fecha)
    st.write("Hora:", hora)

    # Dividir descripción en palabras
    palabras = descripcion.split()

    st.write("Palabras de la descripción:", palabras)
    st.write("Cantidad de palabras:", len(palabras))

    # Mostrar archivo
    if archivo is not None:
        st.write("Archivo cargado:", archivo.name)
    else:
        st.warning("No se seleccionó ningún archivo")


    
    # 5. BARRA DE PROGRESO
 

    mensaje = st.empty()

    progreso = st.progress(0)

    for porcentaje in range(101):

        progreso.progress(porcentaje)

        mensaje.text(
            f"Procesando... {porcentaje}%"
        )

        time.sleep(0.03)

    # Limpiar mensaje
    mensaje.empty()

    st.success("¡Proceso terminado correctamente!")
