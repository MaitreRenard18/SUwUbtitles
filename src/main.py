import os
from tempfile import TemporaryFile, _TemporaryFileWrapper

from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse

from subtitles import generate_subtitles
from video import add_subtitles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="upload.html", context={}
    )

@app.post("/upload/")
async def upload(video: UploadFile):
    with TemporaryFile(mode="+bw", suffix=".mp4", delete=False) as base_video:
        base_video.write(await video.read())
        
        subtitles = generate_subtitles(base_video.name)
        
        final_video = TemporaryFile("+bw", delete=False, suffix=".mp4")
        add_subtitles(base_video.name, subtitles.name, final_video.name)
        
        return FileResponse(final_video.name, media_type='application/octet-stream',filename=video.filename)
