import asyncio
import os.path
import time
import socket

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256 as hashc
from tempfile import SpooledTemporaryFile
from fastapi import FastAPI, UploadFile, File, HTTPException
from starlette import status
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist
from uploader.models import *
from uploader.settings import *
from aiofile import async_open
from uploader.datamodels import *

app = FastAPI(root_path=ROOT_PATH)
pool = ThreadPoolExecutor(max_workers=2)

#region Wait for MySQL to initialize
while True:
    try:
        with socket.create_connection((os.getenv("MYSQL_HOST"), int(os.getenv("MYSQL_PORT"))), timeout=5.0):
            break
    except OSError:
        time.sleep(0.125)
#endregion

def calculate_file_hash(file: SpooledTemporaryFile, chunk: int = 1024 * 1024):
    sha = hashc()
    while True:
        data = file.read(chunk)
        if not data:
            break
        sha.update(data)
    file.seek(0)
    return sha.digest(), sha.hexdigest()


@app.on_event("startup")
async def startup():  # pragma: nocoverage
    await Tortoise.init(config=TORTOISE_ORM)


@app.on_event("shutdown")
async def shutdown():  # pragma: nocoverage
    await Tortoise.close_connections()


@app.post("/uploads/")
async def upload(file: UploadFile = File(...)):
    assert len(file.filename) <= 255
    hash, hex = await asyncio.get_running_loop().run_in_executor(pool, calculate_file_hash, file.file)
    url_hash = hashc(hash + file.filename.encode("utf-8")).hexdigest()
    model = await FileModel.get_or_none(hash=hex)
    if model is None:
        size = 0
        async with async_open(os.path.join(DATA_PATH, hex), "wb") as f:
            while True:
                data = await file.read(1024 * 1024)
                if not data:
                    break
                size += len(data)
                await f.write(data)
        model = await FileModel.create(hash=hex, type=file.content_type, size=size)
    try:
        await FilenameModel.get(hash=url_hash)
    except DoesNotExist:
        await FilenameModel.create(hash=url_hash, name=file.filename, file=model)
    return url_hash


@app.get("/uploads/", response_model=List[FileDataModel])
async def get_uploads():
    return [await FileDataModel.of(model) async for model in FileModel.all()]

@app.get("/uploads/{hash}")
async def download_file(hash: str):
    try:
        filename = await FilenameModel.get(hash=hash)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    file = filename.file
    async with async_open(os.path.join(DATA_PATH, file.hash), "wb") as f:
        pass
