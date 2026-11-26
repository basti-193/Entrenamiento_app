import random
import re
from datetime import date, timedelta

import streamlit as st

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
EQUIPO = ["barra", "paralelas", "trx", "mancuernas", "kettlebell", "maquina", "bandas", "cajon", "rueda", "cancha", "ancla", "agarre_neutro"]
ORDEN = ["tiron", "empuje", "pierna"]  # en empate gana el primero: tracción es la prioridad
TIPO_MAP = {"tiron": "tiron", "habilidades_empuje": "empuje", "piernas_velocidad": "pierna"}
CASA = {"mancuernas", "bandas", "cajon", "cancha", "trx", "rueda", "maquina", "kettlebell", "ancla"}
PLAZA = {"barra", "paralelas", "bandas", "agarre_neutro"}
EQ_TIPO = {"pierna": CASA, "empuje": PLAZA, "tiron": PLAZA}  # pierna en casa; empuje y tirón en la plaza
GYM = {"maquina", "mancuernas", "bandas", "rueda", "cajon"}
ZONAS = {"Tren superior": {"empuje", "tiron", "hombro", "habilidad"}, "Piernas": {"piernas", "velocidad"}, "Core": {"core"}}
INF = ("sentadilla profunda", "tobillo", "estocada", "isquio", "apertura", "hip cars", "ankle cars", "90/90", "cossack hold", "tibial", "pancake")
SUP = ("escapular", "rotacion", "bear", "shoulder cars", "muneca")
POST = ("peso muerto", "puente", "curl femoral", "hip thrust", "buenos dias", "bisagra", "isquios", "nordic curl")
QUAD = ("sissy", "atg", "shrimp", "step down", "skater", "hindu", "wall sit", "sentadilla en pared", "cossack", "curl nordico inverso")
# Cadenas de progresión: cada ejercicio es una variante más difícil del anterior
CADENAS = {
    "dominada": ["Dominada negativa", "Dominada estricta", "Dominada pecho a barra", "Dominada explosiva", "Transicion muscle-up", "Muscle-up"],
    "fondo": ["Fondos entre sillas", "Fondo en paralelas", "Fondo en barra recta"],
    "flexion": ["Flexion", "Flexion declinada", "Flexion diamante", "Flexion pseudo planche", "Flexion arquero", "Flexion explosiva"],
    "lsit": ["Elevacion de piernas sentado", "L-sit con rodillas flexionadas", "L-sit", "L-sit a tuck planche"],
    "unilateral": ["Step down con cajon", "ATG split squat", "Sentadilla bulgara con mancuernas", "Pistol asistida en TRX", "Pistol squat", "Shrimp squat"],
    "bisagra": ["Buenos dias", "Puente de gluteo a una pierna", "Peso muerto rumano a una pierna", "Caminata de isquios (walkouts)", "Nordic curl"],
}
INICIO = {"dominada": "Dominada estricta", "fondo": "Fondo en paralelas", "flexion": "Flexion declinada",
          "lsit": "L-sit con rodillas flexionadas", "unilateral": "Sentadilla bulgara con mancuernas", "bisagra": "Puente de gluteo a una pierna"}
FUERZA = {"dominada", "fondo", "unilateral"}  # se tratan como ejercicio pesado: solo, 4 series, 90-120 s
FAM_DE = {n: f for f, ns in CADENAS.items() for n in ns}
PLANTILLAS = {
    # pierna (en casa, poco espacio): pliometría, velocidad estática por tiempo, pesado, extensión y cadena posterior siempre
    "pierna": [("piernas", None, 2, ("salto",)), ("velocidad", None, 1, ("en el lugar",)), ("@unilateral",),
               ("piernas", None, 1, ("extension",)), ("core", None, 1, None),
               ("@bisagra",), ("core", None, 1, None),
               ("piernas", False, 1, QUAD), ("movilidad", None, 1, INF)],
    "empuje": [("@fondo",), ("tiron", True, 1, ("dominada estricta",)),
               ("@flexion",), ("piernas", None, 1, ("sentadilla",)),
               ("empuje", False, 1, None), ("piernas", None, 1, ("sentadilla",)),
               ("core", None, 1, None), ("@lsit",), ("movilidad", None, 1, SUP)],
    "tiron": [("habilidad", None, 1, ("muscle", "transicion")), ("@dominada",),
              ("tiron", None, 1, ("remo",)), ("piernas", None, 1, ("sentadilla",)),
              ("tiron", False, 1, ("chin-up", "agarre")), ("piernas", None, 1, ("sentadilla",)),
              ("core", None, 1, None), ("movilidad", None, 1, SUP)],
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
    if e.get("_plio") or e.get("_liviana"):
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
    if e["categoria"] == "velocidad" and seg:
        return f"{m} s"
    if e.get("_liviana"):
        return "3-4 reps (deja 2 en reserva)"
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
    if e.get("_liviana"):
        return "60-90 s"
    if e["categoria"] == "habilidad":
        return "30-60 s"
    if e["es_fijo"]:
        return "90-120 s"
    return f"{e['seg_descanso']} s"


def minutos(e):
    d = 45 if e["categoria"] == "habilidad" else e["seg_descanso"]
    return series_de(e) * (e["seg_trabajo"] + d) / 60


def linea(i, e, s):
    meta = f"\n   Meta: 3 o más series de {techo(e)} en dos sesiones seguidas y pasas a {e['_sig']}" if e.get("_sig") else ""
    return f"{i}) {e['nombre']}: {presc(e, s)} · descanso {descanso(e)}\n   Técnica: {e['notas_tecnicas']}{meta}"


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


def techo(e):
    """Tope del rango de repeticiones o segundos del ejercicio (lo que hay que lograr para subir de nivel)."""
    return int(re.findall(r"\d+", rango(e))[-1])


def actual(fam, ej, eq, dom):
    """Ejercicio en el que estás en esa cadena: parte del inicio y sube cuando dominas el actual."""
    por = {e["nombre"]: e for e in ej}
    cad = [por[n] for n in CADENAS[fam] if n in por]
    if not cad:
        return None
    idx = next((i for i, e in enumerate(cad) if e["nombre"] == INICIO[fam]), 0)
    while idx + 1 < len(cad) and cad[idx]["nombre"] in dom:
        idx += 1
    while idx > 0 and not set(cad[idx]["equipo"]) <= eq:
        idx -= 1
    if not set(cad[idx]["equipo"]) <= eq:
        return None
    e = dict(cad[idx], es_fijo=True) if fam in FUERZA else dict(cad[idx])
    if idx + 1 < len(cad):
        e["_sig"] = cad[idx + 1]["nombre"]
    return e


def dominados(logs, ej):
    """Ejercicios dominados: en sus dos últimas sesiones, 3 o más series, todas en el tope del rango."""
    por_id = {e["id"]: e for e in ej}
    ses = {}
    for r in logs:
        v = r["segundos"] if r["segundos"] is not None else r["reps"]
        if v is not None:
            ses.setdefault(r["ejercicio_id"], {}).setdefault(r["sesion_id"], []).append(v)
    dom = set()
    for eid, por_ses in ses.items():
        e = por_id.get(eid)
        if not e or e["nombre"] not in FAM_DE:
            continue
        t = techo(dict(e, es_fijo=True) if FAM_DE[e["nombre"]] in FUERZA else e)
        ult = sorted(por_ses, reverse=True)[:2]
        if len(ult) == 2 and all(len(por_ses[x]) >= 3 and min(por_ses[x]) >= t for x in ult):
            dom.add(e["nombre"])
    return dom


@st.cache_data(ttl=60)
def cargar_logs(_cli, hoy):
    try:
        return _cli.table("series_log").select("ejercicio_id,reps,segundos,sesion_id").order("sesion_id", desc=True).limit(1500).execute().data
    except Exception:
        return []


def tiempo(lista):
    """Minutos reales de la sesión: 5 de calentamiento + bloques, con el descanso compartido en las biseries."""
    plio = [e for e in lista if e.get("_plio")]
    movs = [e for e in lista if e["categoria"] == "movilidad" and not e.get("_plio")]
    cuerpo = [e for e in lista if not e.get("_plio") and e["categoria"] != "movilidad"]
    t = 5 + sum(minutos(e) for e in plio + movs)
    i = 0
    while i < len(cuerpo):
        e = cuerpo[i]
        sig = cuerpo[i + 1] if i + 1 < len(cuerpo) else None
        if sig and puede_par(e) and puede_par(sig):
            t += min(series_de(e), series_de(sig)) * (e["seg_trabajo"] + sig["seg_trabajo"] + 60) / 60
            i += 2
        else:
            t += minutos(e)
            i += 1
    return t


CALENT = {
    "pierna": "Calentamiento (5 min): sentadilla profunda sostenida 1 min · movilidad de tobillo 10 por lado · Cossack squat 8 por lado · saltos suaves 30 s · balanceo de piernas 10 por lado",
    "empuje": "Calentamiento (5 min): rotaciones de hombros x10 · flexiones escapulares x10 · escapulares colgado en la barra x8 · colgarse 20 s",
    "tiron": "Calentamiento (5 min): rotaciones de hombros x10 · flexiones escapulares x10 · escapulares colgado en la barra x8 · colgarse 20 s",
}


def armar_dia(ej, tipo, equipo, nmax, rng, tope, dom=frozenset()):
    eq = set(equipo) & EQ_TIPO.get(tipo, set(EQUIPO))
    usados, lista = set(), []
    for slot in PLANTILLAS[tipo]:
        if slot[0].startswith("@"):
            e = actual(slot[0][1:], ej, eq, dom)
            if e and e["nombre"] not in usados:
                usados.add(e["nombre"])
                lista.append(e)
            continue
        plio = tipo == "pierna" and bool(slot[3]) and "salto" in slot[3]
        liviana = tipo == "empuje" and slot[0] == "tiron"
        for e in elegir(ej, slot, eq, nmax, rng, usados, True):
            usados.add(e["nombre"])
            lista.append(dict(e, _plio=plio) if plio else (dict(e, _liviana=True) if liviana else e))
    def intocable(e):  # lo que no se recorta: fuerza principal, extensión de cuádriceps y, con tiempo, pliometría y habilidades
        return e["es_fijo"] or "extension" in e["nombre"].lower() or (tipo == "pierna" and e["categoria"] == "piernas" and any(k in e["nombre"].lower() for k in POST)) or (tope >= 30 and (e.get("_plio") or e["categoria"] in ("habilidad", "movilidad")))

    while tiempo(lista) > tope and len(lista) > 2:
        cand = [e for e in lista if not intocable(e)]
        if not cand:
            break
        lista.remove(cand[-1])
    return lista, round(tiempo(lista))


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


def generar_plan(ej, fechas, hist, equipo, nmax, semilla, tope=40, dom=frozenset()):
    rng = random.Random(semilla)
    bloques = []
    for f, (tipo, dias) in asignar(fechas, hist).items():
        lista, total = armar_dia(ej, tipo, equipo, nmax, rng, tope, dom)
        nota = f"· hace {dias} días que no lo trabajas" if dias < 99 else "· sin registros recientes de este día"
        t = texto_dia(f"{DIAS[f.weekday()].upper()} {f.strftime('%d/%m')} · {TITULOS[tipo]}", tipo, lista, total, nota)
        if tipo != "pierna" and tope - total >= 3:
            t += f"\nCancha: al terminar, corre en la cancha unos {tope - total} min (trote continuo o piques) hasta completar {tope} min."
        bloques.append(t)
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


def recomendar(ej, mins, energia, dolor, zonas, hist, equipo, hoy, modo="auto"):
    rng, usados = random.Random(), set()
    excl = set().union(*[ZONAS[z] for z in zonas]) if zonas else set()
    base = [e for e in ej if e["categoria"] not in excl and set(e["equipo"]) <= set(equipo) and e["nivel"] <= 2]
    if modo == "pino":
        por = {e["nombre"]: e for e in base}
        lista = [por[n] for n in ("Shoulder taps en plancha", "Wall walk", "Handstand en pared") if n in por]
        if not lista:
            return "No encontré ejercicios de parada de manos compatibles con tu equipo y tus molestias."
        cuerpo = ["Calentamiento (3 min): círculos de muñecas, apoyos de palma, hombros y flexiones escapulares x10",
                  "Necesitas una pared libre. Si pierdes la técnica, termina el bloque."]
        cuerpo += [linea(i, e, 4) for i, e in enumerate(lista, 1)]
        return "ADICIONAL PARADA DE MANOS · ≈ 15 min (en casa, junto a una pared)\n" + "\n".join(cuerpo)
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


def velocidad_100(semana):
    acel, vmax = {1: ("3 x 30 m", "3 x 50 m"), 2: ("3 x 30 m", "3 x 50 m"), 3: ("3 x 30 m", "3 x 60 m"), 4: ("2 x 30 m", "2 x 40 m")}[semana]
    nota = " (semana de descarga)" if semana == 4 else ""
    return "\n".join([
        f"ADICIONAL VELOCIDAD 100 m · semana {semana} de 4{nota} · en la cancha, 35-45 min, intensidad 90-95%",
        "1) Calentamiento (10 min): trote suave 3 min · movilidad de tobillos 10 por lado · movilidad de cadera 10 por lado · balanceo de piernas 10 por lado · skipping A 2 x 20 m · talones al glúteo 2 x 20 m",
        "2) Técnica de carrera (5 min): salidas inclinadas 3 x 10 m · desplazamientos laterales 2 x 15 m · descanso 30-45 s",
        f"3) Aceleración: {acel} · descanso 2 min · potencia en los primeros metros",
        f"4) Velocidad máxima: {vmax} · descanso 3 min · frecuencia, coordinación y zancada",
        "5) Potencia de piernas (biserie, 3 rondas, descanso 60-90 s): saltos horizontales x4 + sentadilla búlgara con salto 5 por pierna",
        "6) Vuelta a la calma (3 min): caminata suave, flexores de cadera, tobillos, isquios y gemelos",
        "Máximo 1 vez por semana. Si vienes cargado de piernas, mejor déjalo para otro día."])


def semana_ciclo(cli):
    try:
        n = cli.table("sesiones").select("id", count="exact").eq("tipo_dia", "velocidad_100m").execute().count or 0
    except Exception:
        n = 0
    return n % 4 + 1


def flow(ej, equipo):
    rng = random.Random()
    loco = [e for e in ej if e["categoria"] == "locomocion" and e["nivel"] <= 2]
    mov = [e for e in ej if e["categoria"] == "movilidad" and e["nivel"] <= 2 and e["tipo_medida"] != "metros" and set(e["equipo"]) <= set(equipo)]
    if len(loco) < 4:
        return "No hay suficientes ejercicios de locomoción en el catálogo."
    out = ["ADICIONAL MOVIMIENTO · ≈ 15-20 min (en casa, bastan 2-3 m: en el lugar o ida y vuelta)",
           "Calentamiento (3 min): círculos lentos de muñecas, hombros y cadera",
           "Flow: 3 rondas encadenando estos 4 movimientos, 30 s cada uno, descanso 1 min entre rondas:"]
    out += [f"- {e['nombre']}: {e['notas_tecnicas']}" for e in rng.sample(loco, 4)]
    out.append("Movilidad final (3 min):")
    out += [f"- {e['nombre']}: {presc(e, 2)} · {e['notas_tecnicas']}" for e in rng.sample(mov, min(2, len(mov)))]
    return "\n".join(out)


# ---------- pantalla ----------
def cargar_plan(cli, lunes):
    try:
        r = cli.table("planes").select("texto,dias").eq("semana_inicio", str(lunes)).execute().data
        return r[0] if r else None
    except Exception:
        return None


def tab_planificar(ejercicios, cli):
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    hist = cargar_hist(cli, hoy)
    guardado = cargar_plan(cli, lunes)
    dom = dominados(cargar_logs(cli, hoy), ejercicios)

    with st.expander("Duración, equipo y dificultad"):
        tope = st.select_slider("Duración por sesión (min)", options=[20, 30, 40], value=40, key="tope")
        equipo = st.multiselect("Equipo disponible esta semana", EQUIPO, default=[e for e in EQUIPO if e not in ("ancla", "agarre_neutro")], help="Marca \"ancla\" si tienes dónde enganchar los pies (Nordic curl) y \"agarre_neutro\" si la barra tiene agarres paralelos")
        nmax = st.slider("Dificultad máxima de ejercicios", 1, 6, 2, help="Empieza en 2 y súbela cuando domines los ejercicios")

    st.subheader(f"Semana del {lunes.strftime('%d/%m')}")
    if guardado and not st.session_state.get("rehacer"):
        st.caption("Plan guardado de esta semana")
        st.code(guardado["texto"], language=None)
        if st.button("Rehacer plan"):
            st.session_state["rehacer"] = True
            st.session_state["variante"] = st.session_state.get("variante", 0) + 1
            st.rerun()
    else:
        st.caption("Marca los días que puedes entrenar (máximo 3).")
        fechas = []
        for i, col in enumerate(st.columns(7)):
            f = lunes + timedelta(days=i)
            if col.checkbox(f"{DIAS[i][:3]} {f.day}", key=f"dia_{f}", disabled=f < hoy):
                fechas.append(f)
        if len(fechas) > 3:
            st.warning("Marca máximo 3 días.")
        elif st.button("Planificar semana", type="primary", disabled=not fechas):
            iso = lunes.isocalendar()
            semilla = int(f"{iso.year}{iso.week:02d}") + st.session_state.get("variante", 0)
            texto = generar_plan(ejercicios, fechas, hist, equipo, nmax, semilla, tope, dom)
            try:
                cli.table("planes").upsert({"semana_inicio": str(lunes), "dias": [str(f) for f in fechas], "texto": texto}).execute()
                st.session_state["rehacer"] = False
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo guardar el plan: {e}")
                st.code(texto, language=None)
        if guardado and st.button("Cancelar y volver al plan guardado"):
            st.session_state["rehacer"] = False
            st.rerun()

    try:
        ant = cli.table("planes").select("semana_inicio,texto").lt("semana_inicio", str(lunes)).order("semana_inicio", desc=True).limit(12).execute().data
    except Exception:
        ant = []
    if ant:
        with st.expander("Planes anteriores"):
            sel = st.selectbox("Semana", [x["semana_inicio"] for x in ant], key="plan_ant")
            st.code(next(x["texto"] for x in ant if x["semana_inicio"] == sel), language=None)

    with st.expander("Tu progresión"):
        for fam in CADENAS:
            e = actual(fam, ejercicios, set(equipo), dom)
            if e:
                st.write(f"**{fam.capitalize()}**: {e['nombre']} → " + (f"siguiente: {e['_sig']}" if e.get("_sig") else "último nivel de la cadena"))

    st.divider()
    st.subheader("Adicional de hoy")
    c1, c2, c3 = st.columns(3)
    mins = c1.select_slider("Tiempo (min)", options=[10, 15, 20, 25, 30, 40, 50, 60], value=20, key="adic_mins")
    energia = c2.slider("Energía hoy", 1, 5, 3, key="adic_energia")
    dolor = c3.slider("Dolor muscular", 1, 5, 2, key="adic_dolor")
    zonas = st.multiselect("Zona con molestia (opcional)", list(ZONAS), key="adic_zonas")
    modo = st.radio("Tipo", ["Recomendado", "Parada de manos (casa)", "Velocidad 100 m (cancha)", "Movimiento / flow (casa)"], horizontal=True, key="adic_modo")
    semana = 1
    if modo.startswith("Velocidad"):
        semana = st.selectbox("Semana del ciclo", [1, 2, 3, 4], index=semana_ciclo(cli) - 1, key="vel_sem", help="Se calcula según tus sesiones registradas como velocidad_100m; puedes cambiarla")
    if st.button("Recomendar adicional"):
        if modo.startswith("Velocidad"):
            st.session_state["adicional"] = velocidad_100(semana)
        elif modo.startswith("Movimiento"):
            st.session_state["adicional"] = flow(ejercicios, equipo)
        else:
            st.session_state["adicional"] = recomendar(ejercicios, mins, energia, dolor, zonas, hist, equipo, hoy, "pino" if modo.startswith("Parada") else "auto")
    if st.session_state.get("adicional"):
        st.code(st.session_state["adicional"], language=None)
