


# PUNTO 1. IMPORTACIONES Y CONFIGURACIÓN GENERAL

import os #Permite interactuar con el sistema operativo, gestionar archivos, carpetas y rutas.
import random
import sqlite3#Permite crear, conectar, consultar y administrar bases de datos SQLite.
import time
import datetime as dt
from contextlib import closing#Permite cerrar automáticamente conexiones y recursos después de utilizarlos.
import altair as alt#Permite crear gráficos estadísticos interactivos para visualizar y analizar datos.
import pandas as pd
import streamlit as st

DB = "limpieza.db"  # archivo SQLite donde se guarda todo

FAMILIA = "Equipo Ruballos Aceituno"  # título del dashboard 

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"] #Dias de la semana

st.set_page_config(page_title=FAMILIA, page_icon=" ", layout="centered") #Titulo centrado


# PUNTO 2. BASE DE DATOS (SQLite)
# members =las personas y su color
# tasks =tareas; kind='diaria' (todos los días) o 'especial' (solo ruleta)
# done = quién hizo cada tarea diaria cada día
# specials = a quién le tocó cada tarea especial (resultado de la ruleta)
# rewards / spent = premios y puntos gastados

def run(sql, args=(), fetch=False):
    """Ejecuta una consulta SQL; devuelve filas si fetch=True."""
    with closing(sqlite3.connect(DB)) as c:
        cur = c.execute(sql, args)
        c.commit()
        return cur.fetchall() if fetch else None


def init_db():
    run("CREATE TABLE IF NOT EXISTS members(id INTEGER PRIMARY KEY, name TEXT, color TEXT, emoji TEXT)")

    run("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, name TEXT, kind TEXT, pts INT, orden INT)")
    run("CREATE TABLE IF NOT EXISTS done(day TEXT, task_id INT, member_id INT, PRIMARY KEY(day, task_id))")
    run("CREATE TABLE IF NOT EXISTS specials(day TEXT, task_id INT, member_id INT, done INT DEFAULT 0, PRIMARY KEY(day, task_id))")
    run("CREATE TABLE IF NOT EXISTS rewards(id INTEGER PRIMARY KEY, name TEXT, cost INT)")
    run("CREATE TABLE IF NOT EXISTS spent(id INTEGER PRIMARY KEY, member_id INT, reward TEXT, cost INT)")

    if not run("SELECT 1 FROM members", fetch=True):

        #######################################
        # Personas y colores del boceto:
        for n, c, e in [("Sofi", "#000fe6", " "), ("Selene", "#ff33e4", " "), ("Mami", "#8720b0", " "), ("Papi", "#333333", " ")]:
            run("INSERT INTO members(name, color, emoji) VALUES(?,?,?)", (n, c, e))
        ########################################

        ##################################################################################
        # Tareas de TODOS LOS DÍAS (orden cronológico) -> (nombre, tipo, puntos, orden)
        diarias = [("Ordenar camas", 2), ("Barrer la casa", 2), ("Lavar los trastes (desayuno)", 2),
                   ("Trapear", 3), ("Lavar los trastes (almuerzo)", 2)]
        for i, (n, p) in enumerate(diarias):
            run("INSERT INTO tasks(name, kind, pts, orden) VALUES(?,?,?,?)", (n, "diaria", p, i))
        ####################################################################################

        #########################################################################
        # DÍAS ESPECIALES: solo aparecen como extra cuando la ruleta los asigna
        especiales = [("Lavar ropa en la lavadora", 4), ("Barrer el segundo piso", 3),
                      ("Tender la ropa", 2), ("Limpiar el baño", 5), ("Sacar la basura", 3)]
        for i, (n, p) in enumerate(especiales):
            run("INSERT INTO tasks(name, kind, pts, orden) VALUES(?,?,?,?)", (n, "especial", p, i))

        for n, c in [("Elegir la película del domingo", 15), ("Postre especial", 20),
                     ("No hacer ninguna tarea en el dia", 25), ("Salida en familia", 50)]:
            run("INSERT INTO rewards(name, cost) VALUES(?,?)", (n, c))
        ################################################################################



# PUNTO 3. FUNCIONES DE APOYO (leer datos, puntos, fechas)

def members():
    return run("SELECT id, name, color, emoji FROM members ORDER BY id", fetch=True)


def tasks(kind):
    return run("SELECT id, name, pts FROM tasks WHERE kind=? ORDER BY orden, id", (kind,), fetch=True)


def lunes_de(d):
    return d - dt.timedelta(days=d.weekday())


def puntos(desde="0000-01-01"):
    """Puntos ganados por persona desde una fecha: diarias hechas + especiales cumplidas."""
    sql = """SELECT member_id, SUM(pts) FROM (
        SELECT d.member_id, t.pts FROM done d JOIN tasks t ON t.id = d.task_id WHERE d.day >= ?
        UNION ALL
        SELECT s.member_id, t.pts FROM specials s JOIN tasks t ON t.id = s.task_id WHERE s.done = 1 AND s.day >= ?
    ) GROUP BY member_id"""
    got = {r[0]: r[1] for r in run(sql, (desde, desde), fetch=True)}
    return {m[0]: got.get(m[0], 0) for m in members()}


def saldo():
    """Puntos disponibles = ganados - gastados en premios."""
    gan = puntos()
    gas = {r[0]: r[1] for r in run("SELECT member_id, SUM(cost) FROM spent GROUP BY member_id", fetch=True)}
    return {i: gan[i] - (gas.get(i) or 0) for i in gan}



# PUNTO 4. CALLBACKS (se ejecutan al tocar un control)

def marcar_diaria(day, task_id, key):
    """Guarda quién hizo la tarea diaria (0 = pendiente)."""
    quien = st.session_state[key]
    if quien == 0:
        run("DELETE FROM done WHERE day=? AND task_id=?", (day, task_id))
    else:
        run("INSERT OR REPLACE INTO done VALUES(?,?,?)", (day, task_id, quien))


def marcar_extra(day, task_id, key):
    """Marca una tarea especial como cumplida o no."""
    run("UPDATE specials SET done=? WHERE day=? AND task_id=?", (int(st.session_state[key]), day, task_id))



# PUNTO 5. ENCABEZADO Y PESTAÑAS (Hoy | Semana | Ruleta | Reporte | Premios)

init_db()
mem = members()
ids = [m[0] for m in mem]
nombre = {m[0]: f"{m[3]} {m[1]}" for m in mem}
hoy = dt.date.today()
hoy_s = hoy.isoformat()
st.title(f"¡¡{FAMILIA}!!")
t_hoy, t_sem, t_rul, t_rep, t_pre = st.tabs(["Hoy", "Semana", "Ruleta", "Reporte", "Premios"])


# PUNTO 5. ENCABEZADO Y PESTAÑAS (Hoy | Semana | Ruleta | Reporte | Premios)

with t_hoy:
    st.subheader("¡¡Hola FAMILIAAAA!!")
    st.caption("¡Nosotros podemos, YUPIII! ")

    st.image("IMAGEHAPPY.jpg", use_container_width=True)


    diarias = tasks("diaria")
    hechas = {r[0]: r[1] for r in run("SELECT task_id, member_id FROM done WHERE day=?", (hoy_s,), fetch=True)}
    n_ok = sum(1 for t in diarias if t[0] in hechas)
    st.progress(n_ok / max(1, len(diarias)), text=f"{n_ok}/{len(diarias)} tareas completadas")

    st.markdown("#### Tareas de hoy:")
    for t in diarias:
        c1, c2 = st.columns([3, 2])
        c1.markdown(f"{' ' if t[0] in hechas else ' '} **{t[1]}** \n<small>+{t[2]} pts</small>", unsafe_allow_html=True)
        key = f"q_{hoy_s}_{t[0]}"
        c2.selectbox(
            "¿Quién lo hizo?",
            [0] + ids,
            index=([0] + ids).index(hechas.get(t[0], 0)),
            format_func=lambda i: "¿Quién lo hizo?" if i == 0 else nombre[i],
            key=key,
            label_visibility="collapsed",
            on_change=marcar_diaria,
            args=(hoy_s, t[0], key)
        )

    # Extras: tareas especiales que la ruleta asignó HOY (no son parte de las diarias)
    extras = run("""SELECT s.task_id, t.name, t.pts, s.member_id, s.done FROM specials s
                   JOIN tasks t ON t.id = s.task_id WHERE s.day=?""", (hoy_s,), fetch=True)
    if extras:
        st.markdown("#### Extras de hoy (ruleta)")
        for tid, tn, tp, mid, dn in extras:
            key = f"x_{hoy_s}_{tid}"
            st.checkbox(f"{tn} → {nombre[mid]} (+{tp} pts)", value=bool(dn), key=key,
                        on_change=marcar_extra, args=(hoy_s, tid, key))


# ============================================================
# PUNTO 7. PESTAÑA "SEMANA": quién hizo qué cada día
# ============================================================
with t_sem:
    st.subheader("Resumen de la semana")
    lunes = lunes_de(hoy)
    dias = [lunes + dt.timedelta(days=i) for i in range(7)]
    cols = [f"{DIAS[d.weekday()][:3]} {d.day}" for d in dias]

    feitas = {(r[0], r[1]): r[2] for r in run("SELECT day, task_id, member_id FROM done WHERE day>=?",
                                             (lunes.isoformat(),), fetch=True)}
    filas = {}
    for t in tasks("diaria"):
        filas[t[1]] = [nombre[feitas[(d.isoformat(), t[0])]].split()[0] if (d.isoformat(), t[0]) in feitas else "·" for d in dias]

    st.dataframe(pd.DataFrame(filas, index=cols).T, use_container_width=True)

    st.markdown("**Extras de la ruleta esta semana**")
    ex = run("""SELECT s.day, t.name, s.member_id, s.done FROM specials s JOIN tasks t ON t.id = s.task_id
                WHERE s.day>=? ORDER BY s.day""", (lunes.isoformat(),), fetch=True)
    if ex:
        st.dataframe(pd.DataFrame([{"Día": dt.date.fromisoformat(d).strftime("%d/%m"), "Actividad": n,
                                   "Le tocó a": nombre[m], "Hecha": " " if f else " "} for d, n, m, f in ex]),
                     hide_index=True, use_container_width=True)
    else:
        st.caption("Todavía no se ha girado la ruleta esta semana.")


# ============================================================
# PUNTO 8. PESTAÑA "RULETA": decide quién hace cada actividad especial
# ============================================================
with t_rul:
    st.subheader(" Ruleta de actividades especiales")
    st.caption("Las actividades especiales no van todos los días: la ruleta decide a quién le toca.")

    esp = tasks("especial")
    tarea = st.selectbox("Actividad especial", esp, format_func=lambda t: f"{t[1]} (+{t[2]} pts)")
    ausentes = st.multiselect("¿Quién no participa hoy?", ids, format_func=lambda i: nombre[i])
    justa = st.toggle("Ruleta justa: más probabilidad a quien ha hecho menos extras esta semana", True)
    if st.button(" ¡Girar la ruleta!", type="primary", use_container_width=True):
        candidatos = [i for i in ids if i not in ausentes]
        if not candidatos:
            st.warning("Necesitas al menos una persona participando.")
        else:
            # Cuántos extras lleva cada quien esta semana -> menos extras = más probabilidad
            cuenta = {r[0]: r[1] for r in run("SELECT member_id, COUNT(*) FROM specials WHERE day>=? GROUP BY member_id",
                                              (lunes_de(hoy).isoformat(),), fetch=True)}
            pesos = [1 / (1 + cuenta.get(i, 0)) if justa else 1 for i in candidatos]
            ganador = random.choices(candidatos, weights=pesos)[0]
            pantalla = st.empty()
            for n in range(18):  # animación: los nombres pasan cada vez más lento
                pantalla.markdown(f"### {nombre[random.choice(candidatos)]}")
                time.sleep(0.06 + n * 0.012)
            pantalla.markdown(f"### {nombre[ganador]} hará: **{tarea[1]}**")
            run("INSERT OR REPLACE INTO specials VALUES(?,?,?,0)", (hoy_s, tarea[0], ganador))
            st.balloons()

    asignadas = run("""SELECT s.task_id, t.name, s.member_id FROM specials s JOIN tasks t ON t.id = s.task_id
                       WHERE s.day=?""", (hoy_s,), fetch=True)

    if asignadas:
        st.markdown("**Asignadas hoy**")
        for tid, tn, mid in asignadas:
            c1, c2 = st.columns([5, 1])
            c1.write(f"{tn} → {nombre[mid]}")
            if c2.button(" ", key=f"undo{tid}", help="Quitar y volver a girar"):
                run("DELETE FROM specials WHERE day=? AND task_id=?", (hoy_s, tid))
                st.experimental_rerun()


# ============================================================
# PUNTO 9. PESTAÑA "REPORTE": el dashboard con métricas y gráficas
# ============================================================
with t_rep:
    st.subheader("Reporte")
    periodo = st.radio("Periodo", ["Esta semana", "Todo el tiempo"], horizontal=True)
    desde = lunes_de(hoy).isoformat() if periodo == "Esta semana" else "0000-01-01"

    pts = puntos(desde)
    total_d = run("SELECT COUNT(*) FROM done WHERE day>=?", (desde,), fetch=True)[0][0]
    total_e = run("SELECT COUNT(*) FROM specials WHERE done=1 AND day>=?", (desde,), fetch=True)[0][0]

    m1, m2 = st.columns(2)
    m1.metric("Tareas diarias hechas", total_d)
    m2.metric("Extras cumplidos", total_e)

    df = pd.DataFrame({
        "Persona": [m[1] for m in mem],
        "Puntos": [pts[m[0]] for m in mem],
        "Color": [m[2] for m in mem]
    })

    st.altair_chart(alt.Chart(df).mark_bar().encode(
        x="Persona",
        y="Puntos",
        color=alt.Color("Persona", scale=alt.Scale(domain=list(df.Persona), range=list(df.Color)), legend=None)
    ), use_container_width=True)

    if df.Puntos.sum() > 0:
        lider = df.loc[df.Puntos.idxmax()]
        st.success(f" Va liderando: {lider.Persona} con {int(lider.Puntos)} puntos")

    st.markdown("**Tareas completadas por día (esta semana)**")
    lunes = lunes_de(hoy)
    por_dia = {r[0]: r[1] for r in run("SELECT day, COUNT(*) FROM done WHERE day>=? GROUP BY day", (lunes.isoformat(),), fetch=True)}

    st.bar_chart(pd.DataFrame({"Tareas": [por_dia.get((lunes + dt.timedelta(days=i)).isoformat(), 0) for i in range(7)]},
                             index=[d[:3] for d in DIAS]))


# ============================================================
# PUNTO 10. PESTAÑA "PREMIOS": canjear puntos
# ============================================================
with t_pre:
    st.subheader("Premios")
    bal = saldo()
    premios = run("SELECT id, name, cost FROM rewards ORDER BY cost", fetch=True)

    for mid in ids:
        with st.container():
            st.markdown(f"**{nombre[mid]}** &nbsp; {bal[mid]} puntos")
            for rid, rn, rc in premios:
                c1, c2 = st.columns([4, 2])
                c1.write(rn)
                if c2.button(f"{rc} ", key=f"b{mid}_{rid}", disabled=bal[mid] < rc):
                    run("INSERT INTO spent(member_id, reward, cost) VALUES(?,?,?)", (mid, rn, rc))
                    st.experimental_rerun()

    with st.form("nuevo_premio", clear_on_submit=True):
        st.write("**Nuevo premio**")
        rn = st.text_input("Premio", placeholder="Ej: Noche de juegos")
        rc = st.number_input("Costo en puntos", 1, 500, 20)
        if st.form_submit_button("Agregar premio") and rn.strip():
            run("INSERT INTO rewards(name, cost) VALUES(?,?)", (rn.strip(), rc))
            st.experimental_rerun()
