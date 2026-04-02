import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
st.set_page_config(page_title="Contador S&S", page_icon="🎴", layout="centered")
st.logo("https://www.sanitsolutions.com.mx/templates/rt_akuatik/custom/images/FB-04%20(1).png")

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def init_connection():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # st.secrets lee automáticamente la carpeta .streamlit/secrets.toml
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes
    )
    return gspread.authorize(creds)

# Intentamos conectar, si hay error lo mostramos en pantalla
try:
    client = init_connection()
    # Abre el archivo (debe llamarse exactamente "Sistema_Sanit")
    sheet = client.open("Sistema_Sanit").sheet1
except Exception as e:
    st.error(f"Error de conexión con Google Sheets: {e}")
    st.stop()

# Obtenemos todos los datos de la hoja
datos_hoja = sheet.get_all_records()

# Convertimos los datos para usarlos: {'Ezequiel': 100, 'Kevin': 100}
fichas = {str(fila['Empleado']): int(fila['Fichas']) for fila in datos_hoja}

# --- FUNCIÓN PARA ACTUALIZAR DATOS EN LA NUBE ---
def actualizar_en_nube(empleado, cambio):
    celda_empleado = sheet.find(empleado)
    fila = celda_empleado.row
    columna_fichas = celda_empleado.col + 1 
    
    fichas_actuales = fichas[empleado]
    nuevas_fichas = fichas_actuales + cambio
    
    sheet.update_cell(fila, columna_fichas, nuevas_fichas)
    return nuevas_fichas

# --- INTERFAZ ---
st.title("Contador S&S 🎴")

nombres_empleados = list(fichas.keys())
opciones_menu = ["Elige una opción...", "Admin (Sergio)"] + nombres_empleados

usuario = st.selectbox("Selecciona tu perfil:", opciones_menu)
st.divider()

# VISTA ADMINISTRADOR
if usuario == "Admin (Sergio)":
    password = st.text_input("Ingresa tu PIN de Administrador:", type="password")
    
    if password == "caradehuevo2026": 
        st.success("Acceso concedido")
        st.subheader("Panel de Control")
        
        for empleado, puntos in fichas.items():
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{empleado}**\n{puntos} fichas")
            with col2:
                if st.button("➕ 5", key=f"sumar_{empleado}") and puntos <= 95:
                    actualizar_en_nube(empleado, 5)
                    st.rerun()
            with col3:
                if st.button("➖ 5", key=f"restar_{empleado}") and puntos >= 5:
                    actualizar_en_nube(empleado, -5)
                    st.rerun()
            st.write("---")
            
    elif password != "":
        st.error("PIN incorrecto. Acceso denegado.")

# VISTA COLABORADOR
elif usuario in fichas:
    st.subheader(f"Hola, {usuario} 👋")
    puntos_actuales = fichas[usuario]
    
    st.metric(label="Tus Fichas Actuales", value=puntos_actuales)
    
    if puntos_actuales >= 80:
        st.success("Nivel: Colaborador confiable ⭐")
    elif puntos_actuales >= 50:
        st.warning("Nivel: En observación 👀")
    else:
        st.error("Nivel: Riesgo ⚠️")
