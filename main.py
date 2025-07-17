import threading
import time
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn

from integrated_system import IntegratedSystem
from config import Config

app = FastAPI()
system = None

@app.on_event("startup")
def startup_event():
    global system
    config = Config()
    system = IntegratedSystem(config)
    system.start()

@app.on_event("shutdown")
def shutdown_event():
    if system:
        system.stop()

@app.get("/report", response_class=HTMLResponse)
def report():
    # On suppose que system.data_integrator existe et a get_last_report()
    report = system.data_integrator.get_last_report()
    if not report:
        return HTMLResponse("<h2>Aucune donnée disponible</h2>")
    html = f"""
    <h2>Rapport de session</h2>
    <ul>
      <li><b>Score global :</b> {report['overall_score']:.1f}%</li>
      <li><b>Attention :</b> {report['attention']}</li>
      <li><b>Audio :</b> {report['audio']}</li>
      <li><b>Environnement :</b> {report['environment']}</li>
      <li><b>Horodatage :</b> {report['timestamp']}</li>
    </ul>
    """
    return HTMLResponse(html)

@app.get("/export/attention")
def export_attention():
    # On suppose que system.data_integrator existe et a export_attention_csv()
    csv_path = system.data_integrator.export_attention_csv()
    return FileResponse(csv_path, media_type="text/csv", filename="attention_scores.csv")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)