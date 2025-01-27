import os
from tempfile import TemporaryFile, _TemporaryFileWrapper

from fastapi import FastAPI, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse

from subtitles import SubtitleGenerator
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
async def upload(video: UploadFile, word_level: bool = Form(True)):
    content = await video.read()
    
    subtitles = SubtitleGenerator.generate_str(content, word_level)
    
    final_video = TemporaryFile("+bw", delete=False, suffix=".mp4")
    add_subtitles(content, subtitles, final_video.name)
    
    return FileResponse(final_video.name, media_type='application/octet-stream',filename=video.filename)
