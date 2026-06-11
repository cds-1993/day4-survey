import json
import logging
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse


BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML = BASE_DIR / "index.html"
NAME_LIST = BASE_DIR / "list.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("day3-backend")

app = FastAPI(title="DAY3 Survey Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def log_payload(label: str, payload: dict) -> None:
    logger.info("%s: %s", label, json.dumps(payload, ensure_ascii=False))


def load_allowed_names() -> set[str]:
    if not NAME_LIST.exists():
        logger.warning("名单文件不存在: %s", NAME_LIST)
        return set()

    return {
        line.strip()
        for line in NAME_LIST.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def build_scope_error(name: str) -> dict:
    return {
        "success": False,
        "message": "不在调查范围内",
        "data": {
            "name": name,
            "allowed": False,
        },
    }


def is_name_allowed(name: str) -> bool:
    return name.strip() in load_allowed_names()


@app.get("/")
async def home() -> FileResponse:
    return FileResponse(INDEX_HTML)


@app.post("/api/validate-name")
async def validate_name(payload: dict, request: Request) -> JSONResponse:
    name = str(payload.get("name", "")).strip()
    received_params = {
        "body": payload,
        "client": request.client.host if request.client else None,
    }
    log_payload("接收到的参数", received_params)

    if not is_name_allowed(name):
        returned_params = build_scope_error(name)
        log_payload("返回的参数", returned_params)
        return JSONResponse(returned_params, status_code=403)

    returned_params = {
        "success": True,
        "message": "姓名校验通过",
        "data": {
            "name": name,
            "allowed": True,
        },
    }
    log_payload("返回的参数", returned_params)

    return JSONResponse(returned_params)


@app.post("/submit")
async def submit_survey(
    request: Request,
    name: str = Form(...),
    gender: str = Form(...),
    country: str = Form(...),
    frequency: str = Form(...),
    fill_time: str = Form(""),
) -> JSONResponse:
    name = name.strip()
    received_params = {
        "name": name,
        "gender": gender,
        "country": country,
        "frequency": frequency,
        "fill_time": fill_time,
        "client": request.client.host if request.client else None,
    }
    log_payload("接收到的参数", received_params)

    if not is_name_allowed(name):
        returned_params = build_scope_error(name)
        log_payload("返回的参数", returned_params)
        return JSONResponse(returned_params, status_code=403)

    returned_params = {
        "success": True,
        "message": "提交成功",
        "data": {
            "name": name,
            "name_char_count": len(name),
            "gender": gender,
            "country": country,
            "frequency": frequency,
            "fill_time": fill_time,
        },
    }
    log_payload("返回的参数", returned_params)

    return JSONResponse(returned_params)


@app.post("/api/name-count")
async def count_name_characters(payload: dict, request: Request) -> JSONResponse:
    name = str(payload.get("name", "")).strip()
    fill_time = str(payload.get("fill_time", ""))
    received_params = {
        "body": payload,
        "client": request.client.host if request.client else None,
    }
    log_payload("接收到的参数", received_params)

    if not is_name_allowed(name):
        returned_params = build_scope_error(name)
        log_payload("返回的参数", returned_params)
        return JSONResponse(returned_params, status_code=403)

    returned_params = {
        "success": True,
        "data": {
            "name": name,
            "name_char_count": len(name),
            "fill_time": fill_time,
        },
    }
    log_payload("返回的参数", returned_params)

    return JSONResponse(returned_params)
