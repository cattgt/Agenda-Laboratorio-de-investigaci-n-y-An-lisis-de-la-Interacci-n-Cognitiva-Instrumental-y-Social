import streamlit as st
import datetime as dt
from clabcalendar import GoogleCalendarManager

# Mostrar logotipo al inicio
st.image("logo_11.png", width=150)  # Puedes ajustar el ancho según prefieras

# Inicializa el manejador de calendario
calendar_manager = GoogleCalendarManager()

# Estilos y título
st.markdown(
    """
    <style>
        .title {
            font-size: 36px;
            color: #00BFFF;
            text-align: center;
        }
        .available {
            background-color: #98FB98;
            color: black;
            font-weight: bold;
            padding: 5px;
            margin: 2px;
            border-radius: 5px;
        }
        .occupied {
            background-color: #FF6347;
            color: white;
            font-weight: bold;
            padding: 5px;
            margin: 2px;
            border-radius: 5px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title">AGENDA LABORATORIO DE INVESTIGACION Y ANALISIS DE LA INTERACCION COGNITIVA, INSTRUMENTAL Y SOCIAL</div>', unsafe_allow_html=True)

# --- 1. Ver horas disponibles ---
st.header("🕒 Ver horas disponibles")
fecha_seleccionada = st.date_input("Selecciona una fecha", dt.date.today())

# Bloques fijos definidos
bloques_fijos = {
    "08:30 - 09:30": dt.time(8, 30),
    "09:40 - 10:40": dt.time(9, 40),
    "10:50 - 11:50": dt.time(10, 50),
    "12:00 - 13:00": dt.time(12, 00),
    "14:30 - 15:30": dt.time(14, 30),
    "15:40 - 16:40": dt.time(15, 40),
    "16:50 - 17:50": dt.time(16, 50)
}

def obtener_eventos_del_dia(fecha):
    eventos = calendar_manager.list_upcoming_events(50)
    ocupados = []
    for evento in eventos:
        inicio = evento["start"].get("dateTime")
        if inicio:
            start_dt = dt.datetime.fromisoformat(inicio)
            if start_dt.date() == fecha:
                ocupados.append(start_dt.time())
    return ocupados

ocupados = obtener_eventos_del_dia(fecha_seleccionada)

for bloque, hora in bloques_fijos.items():
    estado = "⛔ Ocupado" if hora in ocupados else "✅ Disponible"
    clase = "occupied" if hora in ocupados else "available"
    st.markdown(f'<div class="{clase}">{bloque} - {estado}</div>', unsafe_allow_html=True)

# --- 3. Crear evento ---
st.header("📌 Reserva una hora")
nombre = st.text_input("Tu nombre completo")
correo = st.text_input("Ingrese Correo electrónico")
nombre_responsable = st.text_input("Ingrese nombre de profesor/a o persona responsable")
correo_responsable = st.text_input("Ingrese Correo electrónico de profesor/a o persona responsable")
motivo = st.text_input("Motivo de uso del laboratorio")
fecha = st.date_input("Fecha de reserva", dt.date.today())
bloques_disponibles = {
    "08:30 - 09:30": (dt.time(8, 30), 60),
    "09:40 - 10:40": (dt.time(9, 40), 60),
    "10:50 - 11:50": (dt.time(10, 50), 60),
    "12:00 - 13:00": (dt.time(12, 00), 60),
    "14:30 - 15:30": (dt.time(14, 30), 60),
    "15:40 - 16:40": (dt.time(15, 40), 60),
    "16:50 - 17:50": (dt.time(16, 50), 60)
}
bloque_seleccionado = st.selectbox("Selecciona un bloque horario", list(bloques_disponibles.keys()))
hora, duracion = bloques_disponibles[bloque_seleccionado]

# Verificación robusta de tipos
if isinstance(fecha, str):
    fecha = dt.datetime.strptime(fecha, "%Y-%m-%d").date()
if isinstance(hora, str):
    hora = dt.datetime.strptime(hora, "%H:%M:%S").time()

# --- Documentos éticos (opcional) ---
st.header("📄 Documentos éticos (opcional)")
st.caption("Sube el protocolo aprobado por el CEC si aplica.")
archivo = st.file_uploader("Sube tu protocolo (PDF, Word, etc.)", type=["pdf", "docx", "doc"])
archivo_nombre = archivo.name if archivo else "No se subió archivo"

if archivo:
    st.success(f"Archivo '{archivo.name}' cargado correctamente.")

# --- Validación antes de agendar ---
if not nombre or not correo:
    st.warning("Por favor, ingresa tu nombre y correo antes de agendar.")
else:
    if st.button("Agendar hora"):
        inicio = dt.datetime.combine(fecha, hora).isoformat()
        fin = (dt.datetime.combine(fecha, hora) + dt.timedelta(minutes=duracion)).isoformat()
        resumen = f"{nombre} - {motivo}"
        descripcion = (
            f"Correo: {correo}\n"
            f"Responsable: {nombre_responsable} ({correo_responsable})\n"
            f"Motivo: {motivo}"
        )

        link = calendar_manager.create_event(
            summary=resumen,
            description=descripcion,
            start_time=inicio,
            end_time=fin
        )

        if link and link.startswith("http"):
            # ✅ Registro en Google Sheets
            calendar_manager.append_to_sheet([
                dt.datetime.now().isoformat(),
                nombre,
                correo,
                nombre_responsable,
                correo_responsable,
                motivo,
                fecha.strftime("%Y-%m-%d"),
                hora.strftime("%H:%M"),
                f"{duracion} minutos",
                archivo_nombre,
                link
            ])

            st.success("✅ Reserva realizada correctamente!")
            st.balloons()
        else:
            st.error(link)
