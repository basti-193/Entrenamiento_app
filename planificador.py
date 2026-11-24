import random
from datetime import date, timedelta

import streamlit as st

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
EQUIPO = ["barra", "paralelas", "trx", "mancuernas", "kettlebell", "maquina", "bandas", "cajon", "rueda", "cancha"]
ORDEN = ["pierna", "empuje", "tiron"]
FOCOS = {"core": "Core", "pecho_triceps": "Pecho y tríceps", "espalda_biceps": "Espalda y bíceps"}
# (categoria, fijo: True/False/None, cantidad, palabras clave opcionales)
PLANTILLAS = {
    "pierna": [("velocidad", None, 1, None), ("piernas", True, 1, None), ("piernas", False, 2, None), ("core", None, 1, None), ("movilidad", None, 1, None)],
    "empuje": [("habilidad", None, 1, ("handstand", "wall", "planche", "l-sit", "shoulder", "sentado")), ("empuje", True, 1, None), ("empuje", False, 2, None), ("core", None, 1, None)],
    "tiron": [("habilidad", None, 1, ("muscle", "transicion")), ("tiron", True, 1, None), ("tiron", False, 2, None), ("core", None, 1, None)],
    "core": [("core", None, 4, None), ("movilidad", None, 1, None)],
    "pecho_triceps": [("empuje", None, 4, None), ("hombro", None, 1, None)],
    "espalda_biceps": [("tiron", None, 4, None), ("hombro", None, 1, None)],
}
TITULOS = {"pierna": "PIERNA + VELOCIDAD", "empuje": "EMPUJE + HABILIDADES", "tiron": "TIRÓN + HABILIDADES",
           "core": "EXTRA GIMNASIO: CORE", "pecho_triceps": "EXTRA GIMNASIO: PECHO Y TRÍCEPS", "espalda_biceps": "EXTRA GIMNASIO: ESPALDA Y BÍCEPS"}


def elegir(ej, slot, equipo, nmax, rng, usados):
    cat, fijo, n, kw = slot
    c = [e for e in ej if e["categoria"] == cat and set(e["equipo"]) <= equipo
         and e["nivel"] <= nmax and e["nombre"] not in usados]
    if fijo is not None:
        c = [e for e in c if e["es_fijo"] == fijo]
    if kw:
        c = [e for e in c if any(k in e["nombre"].lower() for k in kw)]
    rng.shuffle(c)
    return c[:n]


def series_de(e):
    if e["categoria"] == "velocidad":
        return 4
    return 4 if e["es_fijo"] else (2 if e["categoria"] == "movilidad" else 3)


def presc(e, s):
    m = e["objetivo_max"] or 10
    if e["tipo_medida"] == "reps":
        return f"{s} x {max(m - 3, 3)}-{m} reps"
    if e["tipo_medida"] == "segundos":
        return f"{s} x {max(m - 10, 10)}-{m} s"
    return f"{s} x {m} m"


def minutos(e):
    return series_de(e) * (e["seg_trabajo"] + e["seg_descanso"]) / 60


def armar_dia(ej, tipo, equipo, nmax, rng):
    usados, lista = set(), []
    for slot in PLANTILLAS[tipo]:
        for e in elegir(ej, slot, equipo, nmax, rng, usados):
            usados.add(e["nombre"])
            lista.append(e)
    total = 8 + sum(minutos(e) for e in lista)  # 6 min calentamiento + 2 cierre
    while total > 45 and len(lista) > 3:
        total -= minutos(lista.pop())
    return lista, round(total)


def texto_dia(nombre_dia, tipo, lista, total):
    out = [f"{nombre_dia.upper()} · {TITULOS[tipo]} (≈ {total} min)", "Calentamiento (6 min): movilidad de hombros, tobillos y cadera + 2 series suaves del primer ejercicio"]
    i, n = 0, 1
    while i < len(lista):
        e = lista[i]
        sig = lista[i + 1] if i + 1 < len(lista) else None
        if sig and e["seg_descanso"] <= 60 and sig["seg_descanso"] <= 60:
            s = min(series_de(e), series_de(sig))
            out.append(f"{n}) Biserie x{s}: {e['nombre']} ({presc(e, s).split(' x ')[1]}) + {sig['nombre']} ({presc(sig, s).split(' x ')[1]}) · descanso 60 s")
            out.append(f"   Técnica: {e['notas_tecnicas']} / {sig['notas_tecnicas']}")
            i += 2
        else:
            out.append(f"{n}) {e['nombre']}: {presc(e, series_de(e))} · descanso {e['seg_descanso']} s")
            out.append(f"   Técnica: {e['notas_tecnicas']}")
            i += 1
        n += 1
    out.append("Cierre (2 min): respiración y estiramiento suave")
    return "\n".join(out)


def generar_plan(ej, dias, extra, equipo, nmax, semilla):
    rng = random.Random(semilla)
    asignados = {d: ORDEN[i % 3] for i, d in enumerate(sorted(dias, key=DIAS.index))}
    if extra:
        asignados[extra[0]] = extra[1]
    bloques = []
    for d in sorted(asignados, key=DIAS.index):
        lista, total = armar_dia(ej, asignados[d], set(equipo), nmax, rng)
        bloques.append(texto_dia(d, asignados[d], lista, total))
    return "\n\n".join(bloques)


def tab_planificar(ejercicios, cli):
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    st.subheader(f"Semana del {lunes.strftime('%d/%m')}")
    dias = st.multiselect("Días de entrenamiento (3)", DIAS, default=["Lunes", "Miércoles", "Viernes"], max_selections=3)
    extra = None
    if st.checkbox("Agregar día extra de gimnasio"):
        libres = [d for d in DIAS if d not in dias]
        c1, c2 = st.columns(2)
        dia_x = c1.selectbox("Día extra", libres)
        foco = c2.selectbox("Qué trabajar", list(FOCOS), format_func=FOCOS.get)
        extra = (dia_x, foco)
    equipo = st.multiselect("Equipo disponible esta semana", EQUIPO, default=EQUIPO)
    nmax = st.slider("Dificultad máxima de ejercicios", 1, 6, 3, help="Súbela a medida que progreses")
    if st.button("Planificar semana", type="primary") and len(dias) == 3:
        semilla = int(f"{lunes.isocalendar().year}{lunes.isocalendar().week:02d}")
        st.session_state["plan"] = generar_plan(ejercicios, dias, extra, equipo, nmax, semilla)
    if len(dias) != 3:
        st.info("Marca exactamente 3 días.")
    plan = st.session_state.get("plan")
    if plan:
        st.code(plan, language=None)
        if st.button("Guardar plan de la semana"):
            cli.table("planes").upsert({"semana_inicio": str(lunes), "dias": dias, "texto": plan}).execute()
            st.success("Plan guardado")
