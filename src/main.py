import os
from tempfile import TemporaryFile, _TemporaryFileWrapper

from fastapi import FastAPI, Request, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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


async def streamer(file: _TemporaryFileWrapper):
    file.seek(0)
    while chunk := file.read(1024 * 1024):
        yield chunk


@app.post("/upload/")
async def upload(video: UploadFile):
    with TemporaryFile(mode="+bw", suffix=".mp4", delete=False) as base_video:
        base_video.write(await video.read())
        
        subtitles = generate_subtitles(base_video.name)
        
        final_video = TemporaryFile("+bw", delete=False)
        add_subtitles(base_video.name, subtitles, final_video.name)
        os.remove(subtitles)
        
        return StreamingResponse(streamer(final_video))
