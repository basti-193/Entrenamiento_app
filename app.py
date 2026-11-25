import re
from datetime import date

import pandas as pd
import streamlit as st
from supabase import create_client
from planificador import tab_planificar

st.set_page_config(page_title="Entrenador", page_icon="💪", layout="centered")

TIPOS_DIA = ["tiron", "habilidades_empuje", "piernas_velocidad", "otro"]


# ---------- acceso ----------
def check_password():
    if st.session_state.get("auth"):
        return True
    pw = st.text_input("Contraseña", type="password")
    if pw:
        if pw == st.secrets["APP_PASSWORD"]:
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    return False


@st.cache_resource
def get_client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


@st.cache_data(ttl=300)
def cargar_ejercicios():
    res = get_client().table("ejercicios").select("*").eq("activo", True).order("categoria").order("nombre").execute()
    return res.data


def parsear_numeros(texto):
    """'4,4,3,3' o '4 4 3 3' -> [4, 4, 3, 3]"""
    partes = [p for p in re.split(r"[,\s]+", texto.strip()) if p]
    return [int(float(p.replace(",", "."))) for p in partes]


# ---------- pestaña: registrar ----------
def tab_registrar(ejercicios):
    st.subheader("Datos de la sesión")
    c1, c2 = st.columns(2)
    fecha = c1.date_input("Fecha", value=date.today())
    tipo_dia = c2.selectbox("Tipo de día", TIPOS_DIA)
    c3, c4, c5 = st.columns(3)
    energia = c3.slider("Energía antes", 1, 5, 3)
    dolor = c4.slider("Dolor muscular", 1, 5, 2)
    sensacion = c5.slider("Cómo quedé", 1, 5, 3)
    notas = st.text_area("Notas (opcional)", height=70)

    st.subheader("Agregar ejercicio")
    por_nombre = {e["nombre"]: e for e in ejercicios}
    if "pendientes" not in st.session_state:
        st.session_state["pendientes"] = []

    with st.form("agregar", clear_on_submit=True):
        nombre = st.selectbox("Ejercicio", list(por_nombre.keys()))
        valores = st.text_input("Series (ej: 4,4,3,3)", help="Reps, segundos o metros de cada serie, separados por coma")
        lastre = st.number_input("Lastre (kg)", min_value=0.0, step=0.5, value=0.0)
        costo = st.slider("Qué tanto me costó (1 fácil, 5 al límite)", 1, 5, 3)
        agregar = st.form_submit_button("Agregar")

    if agregar:
        try:
            nums = parsear_numeros(valores)
            if not nums:
                raise ValueError
            st.session_state["pendientes"].append(
                {"nombre": nombre, "valores": nums, "lastre": lastre, "costo": costo}
            )
            st.rerun()
        except ValueError:
            st.error("Escribe las series como números, por ejemplo 4,4,3,3")

    pend = st.session_state["pendientes"]
    if pend:
        st.subheader("Para guardar")
        for p in pend:
            extra = f" (+{p['lastre']} kg)" if p["lastre"] else ""
            st.write(f"**{p['nombre']}**: {', '.join(map(str, p['valores']))}{extra} · costo {p['costo']}/5")
        b1, b2 = st.columns(2)
        if b1.button("Quitar el último"):
            pend.pop()
            st.rerun()
        if b2.button("Guardar sesión", type="primary"):
            guardar_sesion(fecha, tipo_dia, energia, dolor, sensacion, notas, pend, por_nombre)


def guardar_sesion(fecha, tipo_dia, energia, dolor, sensacion, notas, pend, por_nombre):
    cli = get_client()
    try:
        ses = cli.table("sesiones").insert({
            "fecha": str(fecha), "tipo_dia": tipo_dia, "energia": energia,
            "dolor_muscular": dolor, "sensacion_final": sensacion, "notas": notas or None,
        }).execute()
        sesion_id = ses.data[0]["id"]

        filas = []
        for p in pend:
            ej = por_nombre[p["nombre"]]
            for i, v in enumerate(p["valores"], start=1):
                fila = {"sesion_id": sesion_id, "ejercicio_id": ej["id"], "serie_n": i,
                        "lastre_kg": p["lastre"], "costo": p["costo"]}
                if ej["tipo_medida"] == "segundos":
                    fila["segundos"] = v
                else:  # reps y metros van en reps
                    fila["reps"] = v
                filas.append(fila)
        cli.table("series_log").insert(filas).execute()

        st.session_state["pendientes"] = []
        st.success("Sesión guardada")
    except Exception as e:
        st.error(f"No se pudo guardar: {e}")


# ---------- pestaña: historial ----------
def tab_historial(ejercicios):
    cli = get_client()

    st.subheader("Últimas sesiones")
    ses = cli.table("sesiones").select("*").order("fecha", desc=True).order("id", desc=True).limit(10).execute().data
    if not ses:
        st.info("Aún no hay sesiones registradas.")
    for s in ses:
        with st.expander(f"{s['fecha']} · {s['tipo_dia']} · energía {s['energia']}/5 · quedé {s['sensacion_final']}/5"):
            filas = cli.table("series_log").select("serie_n,reps,segundos,lastre_kg,costo,ejercicios(nombre)") \
                .eq("sesion_id", s["id"]).order("serie_n").execute().data
            agrupado = {}
            for f in filas:
                n = f["ejercicios"]["nombre"]
                valor = f["segundos"] if f["segundos"] is not None else f["reps"]
                agrupado.setdefault(n, {"vals": [], "lastre": f["lastre_kg"], "costo": f["costo"]})
                agrupado[n]["vals"].append(valor)
            for n, d in agrupado.items():
                extra = f" (+{d['lastre']} kg)" if d["lastre"] and float(d["lastre"]) > 0 else ""
                st.write(f"**{n}**: {', '.join(map(str, d['vals']))}{extra} · costo {d['costo']}/5")
            if s["notas"]:
                st.caption(s["notas"])

    st.subheader("Progreso por ejercicio")
    nombres = {e["nombre"]: e for e in ejercicios}
    elegido = st.selectbox("Ejercicio", list(nombres.keys()), key="prog")
    ej = nombres[elegido]
    datos = cli.table("series_log").select("reps,segundos,sesiones(fecha)").eq("ejercicio_id", ej["id"]).execute().data
    if not datos:
        st.info("Todavía no hay registros de este ejercicio.")
        return
    campo = "segundos" if ej["tipo_medida"] == "segundos" else "reps"
    df = pd.DataFrame([{"fecha": d["sesiones"]["fecha"], "valor": d[campo]} for d in datos if d[campo] is not None])
    mejor = df.groupby("fecha")["valor"].max()
    st.line_chart(mejor)
    st.caption(f"Mejor serie por sesión ({'segundos' if campo == 'segundos' else 'reps/metros'}).")


# ---------- main ----------
st.title("💪 Entrenador")
if check_password():
    try:
        ejercicios = cargar_ejercicios()
    except Exception as e:
        st.error("Error al leer la base de datos")
        st.code(repr(e.args))
        st.stop()
    t1, t2, t3 = st.tabs(["Planificar", "Registrar sesión", "Historial"])
    with t1:
        tab_planificar(ejercicios, get_client())
    with t2:
        tab_registrar(ejercicios)
    with t3:
        tab_historial(ejercicios)