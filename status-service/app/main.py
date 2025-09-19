import os
import time
import psutil
from sqlalchemy import create_engine, text
from fastapi import FastAPI


DATABASE_URL = (
    f"postgresql+psycopg2://{os.environ.get('POSTGRES_USER','insight')}:{os.environ.get('POSTGRES_PASSWORD','insight')}@"
    f"{os.environ.get('POSTGRES_HOST','postgres')}:{os.environ.get('POSTGRES_PORT','5432')}/{os.environ.get('POSTGRES_DB','insightdb')}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = FastAPI(title="Status Service", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/status")
def status():
    with engine.begin() as conn:
        docs = conn.execute(text("SELECT COUNT(*) FROM documents")).scalar() or 0
        reports = conn.execute(text("SELECT COUNT(*) FROM reports_history")).scalar() or 0
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.1)
    return {
        "uptime_s": int(time.time() - psutil.boot_time()),
        "documents": int(docs),
        "reports": int(reports),
        "cpu_percent": cpu,
        "mem_percent": mem.percent,
    }


@app.get("/logs")
def logs():
    return {"message": "Logs endpoint placeholder"}


