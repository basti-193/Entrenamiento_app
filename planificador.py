import random
from datetime import date, timedelta

import streamlit as st

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
EQUIPO = ["barra", "paralelas", "trx", "mancuernas", "kettlebell", "maquina", "bandas", "cajon", "rueda", "cancha"]
ORDEN = ["pierna", "empuje", "tiron"]
TIPO_MAP = {"tiron": "tiron", "habilidades_empuje": "empuje", "piernas_velocidad": "pierna"}
CASA = {"mancuernas", "bandas", "cajon", "cancha", "trx", "rueda", "maquina", "kettlebell"}
PLAZA = {"barra", "paralelas", "bandas"}
EQ_TIPO = {"pierna": CASA, "empuje": PLAZA, "tiron": PLAZA}  # pierna en casa; empuje y tirón en la plaza
GYM = {"maquina", "mancuernas", "bandas", "rueda", "cajon"}
ZONAS = {"Tren superior": {"empuje", "tiron", "hombro", "habilidad"}, "Piernas": {"piernas", "velocidad"}, "Core": {"core"}}
PLANTILLAS = {
    # pierna: pliometría de activación, luego pesado y biseries (la extensión de cuádriceps va siempre)
    "pierna": [("piernas", None, 2, ("salto",)), ("velocidad", None, 1, None), ("piernas", True, 1, None),
               ("piernas", None, 1, ("extension",)), ("core", None, 1, None),
               ("piernas", False, 1, None), ("core", None, 1, None), ("movilidad", None, 1, ("sentadilla profunda", "tobillo", "estocada", "isquio", "apertura"))],
    # empuje y tirón: ejercicio pesado solo y biseries con sentadillas entre series
    "empuje": [("habilidad", None, 1, ("handstand", "wall")), ("empuje", True, 1, None),
               ("empuje", False, 1, None), ("piernas", None, 1, ("sentadilla",)),
               ("empuje", False, 1, None), ("piernas", None, 1, ("sentadilla",)), ("habilidad", None, 1, ("l-sit", "sentado")), ("movilidad", None, 1, ("escapular", "rotacion", "bear"))],
    "tiron": [("habilidad", None, 1, ("muscle", "transicion")), ("tiron", True, 1, None),
              ("tiron", False, 1, None), ("piernas", None, 1, ("sentadilla",)),
              ("tiron", False, 1, None), ("piernas", None, 1, ("sentadilla",)), ("core", None, 1, None), ("movilidad", None, 1, ("escapular", "rotacion", "bear"))],
}
TITULOS = {"pierna": "PIERNA + VELOCIDAD (en casa)", "empuje": "EMPUJE + HABILIDADES (plaza)", "tiron": "TRACCIÓN + HABILIDADES (plaza)"}


# ---------- utilidades ----------
def elegir(ej, slot, equipo, nmax, rng, usados, sin_saltos=False):
    cat, fijo, n, kw = slot
    c = [e for e in ej if e["categoria"] == cat and set(e["equipo"]) <= equipo and e["nivel"] <= nmax and e["nombre"] not in usados]
    if fijo is not None:
        c = [e for e in c if e["es_fijo"] == fijo]
    if kw:
        c = [e for e in c if any(k in e["nombre"].lower() for k in kw)]
    if sin_saltos and not (kw and "salto" in kw):
        c = [e for e in c if "salto" not in e["nombre"].lower()]
    rng.shuffle(c)
    return c[:n]


def series_de(e):
    if e.get("_plio"):
        return 2
    c = e["categoria"]
    if c == "velocidad":
        return 4
    if c == "habilidad":
        return 6
    if c == "movilidad":
        return 2
    return 4 if e["es_fijo"] else 3


def rango(e):
    """Reglas por objetivo: fuerza 4-8 reps, accesorio 8-15, habilidad 20-30 s, movilidad 30-60 s."""
    m = e["objetivo_max"] or 10
    seg = e["tipo_medida"] == "segundos"
    if e["tipo_medida"] == "metros":
        return f"{m} m"
    if e.get("_plio"):
        return f"{max(m - 2, 3)}-{m} reps"
    if e["categoria"] == "habilidad":
        if seg:
            hi = min(m, 30)
            return f"{max(hi - 10, 10)}-{hi} s"
        return f"{max(m - 2, 1)}-{m} reps"
    if e["categoria"] == "movilidad":
        return f"{max(m - 30, 30)}-{m} s" if seg else f"{m} reps"
    if e["es_fijo"] and not seg:
        hi = min(m, 8)
        return f"{min(4, hi)}-{hi} reps"
    if seg:
        return f"{max(m - 10, 10)}-{m} s"
    return f"8-{min(m, 15)} reps" if m >= 10 else f"{max(m - 3, 3)}-{m} reps"


def presc(e, s):
    if e["categoria"] == "habilidad" and e["tipo_medida"] == "segundos":
        return f"{s} intentos de {rango(e)}"
    return f"{s} x {rango(e)}"


def descanso(e):
    if e["categoria"] == "habilidad":
        return "30-60 s"
    if e["es_fijo"]:
        return "90-120 s"
    return f"{e['seg_descanso']} s"


def minutos(e):
    d = 45 if e["categoria"] == "habilidad" else e["seg_descanso"]
    return series_de(e) * (e["seg_trabajo"] + d) / 60


def linea(i, e, s):
    return f"{i}) {e['nombre']}: {presc(e, s)} · descanso {descanso(e)}\n   Técnica: {e['notas_tecnicas']}"


def ultimos(hist):
    ult = {}
    for h in hist:
        t = TIPO_MAP.get(h["tipo_dia"])
        f = date.fromisoformat(h["fecha"])
        if t and (t not in ult or f > ult[t]):
            ult[t] = f
    return ult


@st.cache_data(ttl=60)
def cargar_hist(_cli, hoy):
    desde = str(hoy - timedelta(days=14))
    return _cli.table("sesiones").select("fecha,tipo_dia").gte("fecha", desde).execute().data


# ---------- semana ----------
def asignar(fechas, hist):
    ult, res = ultimos(hist), {}
    for f in sorted(fechas):
        pri = {t: ((f - ult[t]).days if t in ult else 99) for t in ORDEN}
        t = max(ORDEN, key=lambda x: (pri[x], -ORDEN.index(x)))
        res[f] = (t, pri[t])
        ult[t] = f
    return res


CALENT = {
    "pierna": "Calentamiento (5 min): sentadilla profunda sostenida 1 min · movilidad de tobillo 10 por lado · Cossack squat 8 por lado · saltos suaves 30 s · balanceo de piernas 10 por lado",
    "empuje": "Calentamiento (5 min): rotaciones de hombros x10 · flexiones escapulares x10 · escapulares colgado en la barra x8 · colgarse 20 s",
    "tiron": "Calentamiento (5 min): rotaciones de hombros x10 · flexiones escapulares x10 · escapulares colgado en la barra x8 · colgarse 20 s",
}


def armar_dia(ej, tipo, equipo, nmax, rng, tope):
    eq = set(equipo) & EQ_TIPO.get(tipo, set(EQUIPO))
    usados, lista = set(), []
    for slot in PLANTILLAS[tipo]:
        plio = tipo == "pierna" and bool(slot[3]) and "salto" in slot[3]
        for e in elegir(ej, slot, eq, nmax, rng, usados, tipo == "pierna"):
            usados.add(e["nombre"])
            lista.append(dict(e, _plio=True) if plio else e)
    def intocable(e):  # lo que no se recorta: fuerza principal, extensión de cuádriceps y, con tiempo, pliometría y habilidades
        return e["es_fijo"] or "extension" in e["nombre"].lower() or (tope >= 30 and (e.get("_plio") or e["categoria"] in ("habilidad", "movilidad")))

    total = 5 + sum(minutos(e) for e in lista)  # 5 min de calentamiento
    while total > tope and len(lista) > 2:
        cand = [e for e in lista if not intocable(e)]
        if not cand:
            break
        x = cand[-1]
        lista.remove(x)
        total -= minutos(x)
    return lista, round(total)


def puede_par(e):
    return e["seg_descanso"] <= 60 and e["categoria"] != "habilidad" and not e["es_fijo"]


def texto_dia(titulo, tipo, lista, total, nota):
    out = [f"{titulo} (≈ {total} min) {nota}", CALENT[tipo]]
    plio = [e for e in lista if e.get("_plio")]
    movs = [e for e in lista if e["categoria"] == "movilidad" and not e.get("_plio")]
    lista = [e for e in lista if not e.get("_plio") and e["categoria"] != "movilidad"]
    if plio:
        out.append("Activación pliométrica (antes de lo pesado, máxima intención, sin llegar a cansarte):")
        out += [f"   - {e['nombre']}: {presc(e, 2)} · descanso {descanso(e)} · {e['notas_tecnicas']}" for e in plio]
    i, n = 0, 1
    while i < len(lista):
        e = lista[i]
        sig = lista[i + 1] if i + 1 < len(lista) else None
        if sig and puede_par(e) and puede_par(sig):
            s = min(series_de(e), series_de(sig))
            out.append(f"{n}) Biserie x{s}: {e['nombre']} ({rango(e)}) + {sig['nombre']} ({rango(sig)}) · descanso 60 s")
            out.append(f"   Técnica: {e['notas_tecnicas']} / {sig['notas_tecnicas']}")
            i += 2
        else:
            out.append(linea(n, e, series_de(e)))
            i += 1
        n += 1
    if movs:
        out.append("Movilidad final (3-5 min):")
        out += [f"   - {e['nombre']}: {presc(e, series_de(e))} · {e['notas_tecnicas']}" for e in movs]
    return "\n".join(out)


def generar_plan(ej, fechas, hist, equipo, nmax, semilla, tope=45):
    rng = random.Random(semilla)
    bloques = []
    for f, (tipo, dias) in asignar(fechas, hist).items():
        lista, total = armar_dia(ej, tipo, equipo, nmax, rng, tope)
        nota = f"· hace {dias} días que no lo trabajas" if dias < 99 else "· sin registros recientes de este día"
        bloques.append(texto_dia(f"{DIAS[f.weekday()].upper()} {f.strftime('%d/%m')} · {TITULOS[tipo]}", tipo, lista, total, nota))
    return "\n\n".join(bloques)


# ---------- adicional ----------
def carga_alta(hist, hoy, energia, dolor):
    recientes = [h for h in hist if (hoy - date.fromisoformat(h["fecha"])).days <= 3]
    return energia <= 2 or dolor >= 4 or len(recientes) >= 3


def pick(base, cats, n, rng, usados, solo_reps=False):
    c = [e for e in base if e["categoria"] in cats and e["nombre"] not in usados and (not solo_reps or e["tipo_medida"] == "reps")]
    rng.shuffle(c)
    sel = c[:n]
    usados.update(e["nombre"] for e in sel)
    return sel


def recomendar(ej, mins, energia, dolor, zonas, hist, equipo, hoy):
    rng, usados = random.Random(), set()
    excl = set().union(*[ZONAS[z] for z in zonas]) if zonas else set()
    base = [e for e in ej if e["categoria"] not in excl and set(e["equipo"]) <= set(equipo) and e["nivel"] <= 2]
    if carga_alta(hist, hoy, energia, dolor):
        lista = pick(base, ["movilidad"], 3, rng, usados) + pick(base, ["core"], 1, rng, usados)
        titulo = "ADICIONAL SUAVE · 15 min (tu carga está alta: hoy toca soltar, no sumar)"
        cuerpo = [linea(i, e, 2) for i, e in enumerate(lista, 1)]
    elif mins <= 25:
        lista = pick(base, ["piernas"], 1, rng, usados, True) + pick(base, ["empuje", "tiron"], 1, rng, usados, True) + pick(base, ["core"], 1, rng, usados, True)
        dur = 15 if mins < 20 else 20
        rp = lambda e: max(round((e["objetivo_max"] or 10) * 0.6), 5)
        if rng.random() < 0.5:
            titulo = f"ADICIONAL EMOM · {dur} min"
            cuerpo = ["Cada minuto empiezas una serie; lo que sobre del minuto es descanso."]
            cuerpo += [f"Min {i}: {e['nombre']} x {rp(e)}" for i, e in enumerate(lista, 1)]
            cuerpo.append(f"Repite el ciclo de {len(lista)} minutos hasta completar {dur} min.")
        else:
            titulo = f"ADICIONAL AMRAP · {dur} min"
            cuerpo = [f"Tantas rondas como puedas en {dur} min, sin descanso fijo:"]
            cuerpo += [f"- {e['nombre']} x {rp(e)}" for e in lista]
            cuerpo.append("Anota cuántas rondas hiciste para superarlas la próxima vez.")
        cuerpo += [f"Técnica {e['nombre']}: {e['notas_tecnicas']}" for e in lista]
    else:
        ult = ultimos(hist)
        tipo = max(ORDEN, key=lambda t: ((hoy - ult[t]).days if t in ult else 99, -ORDEN.index(t)))
        focos = {"tiron": (["tiron"], ["hombro"], "espalda y bíceps"), "empuje": (["empuje"], ["hombro"], "pecho y tríceps"), "pierna": (["piernas"], ["core"], "pierna")}
        main, sec, nombre = focos[tipo]
        gbase = [e for e in base if e["equipo"] and set(e["equipo"]) <= GYM]
        lista = pick(gbase, main, 2, rng, usados) + pick(gbase, sec, 1, rng, usados)
        s = 4 if mins >= 40 else 3
        titulo = f"ADICIONAL GIMNASIO · {mins} min · foco: {nombre} (es lo que más tiempo lleva sin trabajarse)"
        cuerpo = [linea(i, e, s) for i, e in enumerate(lista, 1)]
    if not lista:
        return "No encontré ejercicios compatibles con tu equipo y tus molestias."
    return titulo + "\n" + "\n".join(cuerpo)


# ---------- pantalla ----------
def tab_planificar(ejercicios, cli):
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    hist = cargar_hist(cli, hoy)

    st.subheader(f"Semana del {lunes.strftime('%d/%m')}")
    st.caption("Marca los días que puedes entrenar (máximo 3).")
    fechas = []
    for i, col in enumerate(st.columns(7)):
        f = lunes + timedelta(days=i)
        if col.checkbox(f"{DIAS[i][:3]} {f.day}", key=f"dia_{f}", disabled=f < hoy):
            fechas.append(f)
    with st.expander("Duración, equipo y dificultad"):
        tope = st.select_slider("Duración por sesión (min)", options=[20, 30, 45], value=45, key="tope")
        equipo = st.multiselect("Equipo disponible esta semana", EQUIPO, default=EQUIPO)
        nmax = st.slider("Dificultad máxima de ejercicios", 1, 6, 2, help="Empieza en 2 y súbela cuando domines los ejercicios")
    if len(fechas) > 3:
        st.warning("Marca máximo 3 días.")
    elif st.button("Planificar semana", type="primary", disabled=not fechas):
        semilla = int(f"{lunes.isocalendar().year}{lunes.isocalendar().week:02d}")
        st.session_state["plan"] = generar_plan(ejercicios, fechas, hist, equipo, nmax, semilla, tope)
    plan = st.session_state.get("plan")
    if plan:
        st.code(plan, language=None)
        if st.button("Guardar plan de la semana"):
            cli.table("planes").upsert({"semana_inicio": str(lunes), "dias": [str(f) for f in fechas], "texto": plan}).execute()
            st.success("Plan guardado")

    st.divider()
    st.subheader("Adicional de hoy")
    c1, c2, c3 = st.columns(3)
    mins = c1.select_slider("Tiempo (min)", options=[10, 15, 20, 25, 30, 40, 50, 60], value=20, key="adic_mins")
    energia = c2.slider("Energía hoy", 1, 5, 3, key="adic_energia")
    dolor = c3.slider("Dolor muscular", 1, 5, 2, key="adic_dolor")
    zonas = st.multiselect("Zona con molestia (opcional)", list(ZONAS), key="adic_zonas")
    if st.button("Recomendar adicional"):
        st.session_state["adicional"] = recomendar(ejercicios, mins, energia, dolor, zonas, hist, equipo, hoy)
    if st.session_state.get("adicional"):
        st.code(st.session_state["adicional"], language=None)
