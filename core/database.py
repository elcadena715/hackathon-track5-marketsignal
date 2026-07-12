import os
import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# Configuración de Supabase
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))

# Cliente de Supabase
@st.cache_resource
def get_supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️ SUPABASE_URL o SUPABASE_KEY no configuradas. Usando modo fallback SQLite.")
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"⚠️ Error conectando a Supabase: {e}. Usando modo fallback SQLite.")
        return None

# Fallback a SQLite local para desarrollo
import sqlite3
DB_PATH = os.path.join("data", "marketsignal.db")

def init_db():
    """Inicializa la base de datos (Supabase o SQLite fallback)"""
    supabase = get_supabase_client()
    
    if supabase:
        # Crear tabla en Supabase si no existe
        try:
            supabase.table("reviews").select("*").limit(1).execute()
            print("✅ Tabla 'reviews' existe en Supabase")
        except:
            print("⚠️ No se pudo verificar tabla en Supabase. Asegurate de crearla manualmente.")
    else:
        # Fallback: SQLite local
        os.makedirs("data", exist_ok=True)
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    justification TEXT NOT NULL,
                    reviewer TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)
            conn.commit()
            print("✅ Base de datos SQLite local inicializada")

def guardar_revision(signal_id, status, justification, reviewer="Analista de Turno"):
    """Guarda una revisión en Supabase o SQLite"""
    supabase = get_supabase_client()
    
    timestamp = datetime.now().isoformat()
    
    if supabase:
        try:
            supabase.table("reviews").insert({
                "signal_id": signal_id,
                "status": status,
                "justification": justification,
                "reviewer": reviewer,
                "created_at": timestamp
            }).execute()
            print(f"✅ Revisión guardada en Supabase: {signal_id}")
        except Exception as e:
            print(f"❌ Error guardando en Supabase: {e}. Guardando localmente.")
            _guardar_revision_sqlite(signal_id, status, justification, reviewer, timestamp)
    else:
        _guardar_revision_sqlite(signal_id, status, justification, reviewer, timestamp)

def _guardar_revision_sqlite(signal_id, status, justification, reviewer, timestamp):
    """Helper para guardar en SQLite"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO reviews (signal_id, status, justification, reviewer, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (signal_id, status, justification, reviewer, timestamp))
        conn.commit()

def obtener_revisiones():
    """Obtiene todas las revisiones de Supabase o SQLite"""
    supabase = get_supabase_client()
    
    if supabase:
        try:
            response = supabase.table("reviews").select("signal_id, status, justification, reviewer, created_at").execute()
            rows = response.data
            return {row["signal_id"]: {
                "status": row["status"],
                "justification": row["justification"],
                "reviewer": row["reviewer"],
                "date": row["created_at"]
            } for row in rows}
        except Exception as e:
            print(f"⚠️ Error leyendo desde Supabase: {e}. Usando SQLite local.")
            return _obtener_revisiones_sqlite()
    else:
        return _obtener_revisiones_sqlite()

def _obtener_revisiones_sqlite():
    """Helper para leer de SQLite"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT signal_id, status, justification, reviewer, created_at FROM reviews")
            rows = cursor.fetchall()
            return {row[0]: {"status": row[1], "justification": row[2], "reviewer": row[3], "date": row[4]} for row in rows}
    except:
        return {}