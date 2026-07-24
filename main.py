import csv
from datetime import datetime
from io import StringIO
from fastapi import Depends, FastAPI, Form, Query, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import OrdenDB, SessionLocal, init_db

init_db()

app = FastAPI(title="Sistema FSM - MASTERFIX")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request, q: str = Query(None), db: Session = Depends(get_db)
):
    query = db.query(OrdenDB)

    if q:
        if q.isdigit():
            query = query.filter(
                (OrdenDB.id == int(q)) | (OrdenDB.cliente_celular.contains(q))
            )
        else:
            query = query.filter(
                (OrdenDB.cliente_nombre.contains(q))
                | (OrdenDB.marca.contains(q))
                | (OrdenDB.modelo.contains(q))
            )

    ordenes = query.order_by(OrdenDB.id.desc()).all()
    return templates.TemplateResponse(
        request, "index.html", {"ordenes": ordenes, "q": q or ""}
    )


@app.get("/nuevo", response_class=HTMLResponse)
def form_nuevo(request: Request):
    return templates.TemplateResponse(request, "nuevo.html", {})


@app.post("/crear-orden")
def crear_orden(
    nombre: str = Form(...),
    celular: str = Form(...),
    identidad: str = Form(...),
    marca: str = Form(...),
    modelo: str = Form(...),
    color: str = Form(...),
    imei: str = Form(...),
    credenciales: str = Form(...),
    observaciones: str = Form(...),
    db: Session = Depends(get_db),
):
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
    nueva_orden = OrdenDB(
        cliente_nombre=nombre,
        cliente_celular=celular,
        cliente_identidad=identidad,
        marca=marca,
        modelo=modelo,
        color=color,
        imei=imei,
        credenciales=credenciales,
        observaciones=observaciones,
        estado="Revision",
        fecha=fecha_actual,
    )
    db.add(nueva_orden)
    db.commit()
    db.refresh(nueva_orden)
    
    # Abre el ticket en una pestaña nueva y devuelve la pestaña actual al menú principal de inmediato
    return HTMLResponse(f"""
        <script>
            window.open('/ticket/{nueva_orden.id}', '_blank');
            window.location.href = '/';
        </script>
    """)


@app.get("/editar/{orden_id}", response_class=HTMLResponse)
def form_editar(orden_id: int, request: Request, db: Session = Depends(get_db)):
    orden = db.query(OrdenDB).filter(OrdenDB.id == orden_id).first()
    if not orden:
        return "Orden no encontrada"
    return templates.TemplateResponse(request, "editar.html", {"orden": orden})


@app.post("/actualizar-orden/{orden_id}")
def actualizar_orden(
    orden_id: int,
    nombre: str = Form(...),
    celular: str = Form(...),
    identidad: str = Form(...),
    marca: str = Form(...),
    modelo: str = Form(...),
    color: str = Form(...),
    imei: str = Form(...),
    credenciales: str = Form(...),
    observaciones: str = Form(...),
    estado: str = Form(...),
    db: Session = Depends(get_db),
):
    orden = db.query(OrdenDB).filter(OrdenDB.id == orden_id).first()
    if orden:
        orden.cliente_nombre = nombre
        orden.cliente_celular = celular
        orden.cliente_identidad = identidad
        orden.marca = marca
        orden.modelo = modelo
        orden.color = color
        orden.imei = imei
        orden.credenciales = credenciales
        orden.observaciones = observaciones
        orden.estado = estado
        db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/cambiar-estado/{orden_id}/{nuevo_estado}")
def cambiar_estado(
    orden_id: int, nuevo_estado: str, db: Session = Depends(get_db)
):
    orden = db.query(OrdenDB).filter(OrdenDB.id == orden_id).first()
    if orden:
        orden.estado = nuevo_estado
        db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/eliminar/{orden_id}")
def eliminar_orden(orden_id: int, db: Session = Depends(get_db)):
    orden = db.query(OrdenDB).filter(OrdenDB.id == orden_id).first()
    if orden:
        db.delete(orden)
        db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/exportar-excel")
def exportar_excel(db: Session = Depends(get_db)):
    ordenes = db.query(OrdenDB).order_by(OrdenDB.id.desc()).all()

    output = StringIO()
    writer = csv.writer(output, delimiter=";")

    writer.writerow([
        "ID Orden",
        "Fecha",
        "Cliente",
        "Celular",
        "Identidad",
        "Marca",
        "Modelo",
        "Color",
        "IMEI",
        "Credenciales/Patrón",
        "Observaciones",
        "Estado",
    ])

    for o in ordenes:
        writer.writerow([
            o.id,
            o.fecha,
            o.cliente_nombre,
            str(o.cliente_celular),
            f'="{o.cliente_identidad}"',
            o.marca,
            o.modelo,
            o.color,
            f'="{o.imei}"',
            o.credenciales,
            o.observaciones,
            o.estado,
        ])

    response = Response("\ufeff" + output.getvalue())
    response.headers["Content-Disposition"] = (
        "attachment; filename=respaldo_taller_fsm.csv"
    )
    response.headers["Content-Type"] = "text/csv; charset=utf-8"

    return response


@app.get("/ticket/{orden_id}", response_class=HTMLResponse)
def ver_ticket(request: Request, orden_id: int, db: Session = Depends(get_db)):
    o = db.query(OrdenDB).filter(OrdenDB.id == orden_id).first()
    if not o:
        return "Orden no encontrada"
    return templates.TemplateResponse(request, "ticket.html", {"o": o})