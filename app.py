import streamlit as st
import hashlib
from database.conexion import get_supabase  # ← CAMBIADO

st.set_page_config(
    page_title="Rock Tools Peru - Login",
    page_icon="⛏️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* === FUENTE PROFESIONAL SOBRIA === */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }
    
    /* === OCULTAR ELEMENTOS POR DEFECTO DE STREAMLIT === */
    [data-testid="stSidebar"] {display: none;}
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    header, .stDecoration, .stStatusWidget, .stException {
        display: none !important;
    }
    
    /* === FONDO SOBRIO (GRIS MUY CLARO) === */
    .stApp {
        background: #F0F2F5 !important;
    }
    
    /* === CONTENEDOR CENTRADO === */
    .full-height-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #F0F2F5 0%, #E8ECF1 100%);
        margin: 0;
        padding: 0;
    }
    
    /* === TARJETA PRINCIPAL === */
    .login-card {
        background: white;
        width: 100%;
        max-width: 420px;
        border-radius: 24px;
        padding: 0;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.06), 0 8px 16px rgba(0, 0, 0, 0.04);
        overflow: hidden;
    }
    
    /* === HEADER DE LA TARJETA === */
    .card-header {
        background: #1A2A3A;
        padding: 2rem 2rem 1.5rem;
        text-align: center;
    }
    
    .card-header h1 {
        color: white;
        font-size: 1.8rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .card-header .subtitle {
        color: #8A9BAC;
        font-size: 0.75rem;
        margin-top: 0.5rem;
        letter-spacing: 1px;
        font-weight: 400;
    }
    
    /* === CUERPO DEL FORMULARIO === */
    .card-body {
        padding: 2rem 2rem 1.8rem;
    }
    
    /* === LABELS === */
    .stTextInput > label {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: #2C3E50 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.4rem !important;
    }
    
    /* === INPUTS === */
    .stTextInput > div > div {
        border-radius: 8px !important;
        border: 1px solid #D1D9E6 !important;
        background: white !important;
        padding: 0.6rem 0.8rem !important;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div:focus-within {
        border-color: #2C5F8A !important;
        box-shadow: 0 0 0 3px rgba(44, 95, 138, 0.08) !important;
    }
    
    /* === BOTÓN === */
    .stButton > button {
        background: #2C5F8A !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.7rem !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        color: white !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #1E4668 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(44, 95, 138, 0.2);
    }
    
    /* === CHECKBOX === */
    .stCheckbox > label {
        font-size: 0.75rem !important;
        color: #5A6E7A !important;
    }
    
    /* === LINK OLVIDÉ CONTRASEÑA === */
    .forgot-link {
        color: #7A8D9E !important;
        font-size: 0.7rem !important;
        text-decoration: none;
        transition: color 0.2s;
    }
    
    .forgot-link:hover {
        color: #2C5F8A !important;
    }
    
    /* === FOOTER === */
    .login-footer {
        text-align: center;
        padding: 1rem 2rem;
        border-top: 1px solid #E8ECF0;
        background: #FAFBFD;
    }
    
    .login-footer p {
        color: #8A9BAC;
        font-size: 0.7rem;
        margin: 0;
    }
    
    /* === MENSAJES DE ERROR === */
    .stAlert {
        border-radius: 8px !important;
        font-size: 0.8rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INICIALIZAR ESTADO DE SESIÓN
# ============================================================================
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['usuario'] = None
    st.session_state['nombre_completo'] = None
    st.session_state['rol'] = None

# ============================================================================
# FUNCIÓN VERIFICAR USUARIO (MODIFICADA)
# ============================================================================
def verificar_usuario(usuario, contraseña):
    supabase = get_supabase()  # ← NUEVO
    response = supabase.table("usuarios").select("id, usuario, nombre_completo, rol")\
        .eq("usuario", usuario)\
        .eq("contrasena", contraseña)\
        .eq("activo", 1)\
        .execute()
    
    if response.data:
        return response.data[0]  # Retorna el primer registro como diccionario
    return None

# ============================================================================
# LOGIN
# ============================================================================
if not st.session_state['autenticado']:
    st.markdown('<div class="full-height-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    
    # Header de la tarjeta
    st.markdown("""
    <div class="card-header">
        <h1>ROCK TOOLS PERU</h1>
        <div class="subtitle">SISTEMA DE GESTIÓN</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="card-body">', unsafe_allow_html=True)
    
    usuario = st.text_input("USUARIO", key="login_user")
    contraseña = st.text_input("CONTRASEÑA", type="password", placeholder="••••••••", key="login_pass")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        recordar = st.checkbox("Recordarme")
    with col2:
        st.markdown('<div style="text-align: right;"><a href="#" class="forgot-link">¿Olvidaste tu contraseña?</a></div>', 
                   unsafe_allow_html=True)
    
    if st.button("INGRESAR", use_container_width=True, type="primary"):
        usuario_data = verificar_usuario(usuario, contraseña)
        if usuario_data:
            st.session_state['autenticado'] = True
            st.session_state['usuario'] = usuario_data['usuario']           # ← CAMBIADO
            st.session_state['nombre_completo'] = usuario_data['nombre_completo']  # ← CAMBIADO
            st.session_state['rol'] = usuario_data['rol']                   # ← CAMBIADO
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="login-footer"><p>© 2025 Rock Tools Peru S.A.C.</p></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
else:
    st.switch_page("pages/01_dashboard.py")