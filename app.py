import os
import uuid
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from enum import Enum

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()

from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.video.background_image_generator import generate_image_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Text-To-Video AI API",
    description="Upload audio and generate AI B-roll videos using Pexels footage.",
    version="2.0.0",
)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
allow_creds = "*" not in CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=4)

# In-memory job store: job_id -> job dict
jobs: dict[str, dict] = {}
jobs_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BackgroundMode(str, Enum):
    video = "video"
    image = "image"
    mix = "mix"

class VideoOrientation(str, Enum):
    portrait = "portrait"
    landscape = "landscape"


# ---------------------------------------------------------------------------
# Helper: update job state
# ---------------------------------------------------------------------------

def _update_job(job_id: str, **kwargs):
    with jobs_lock:
        if job_id in jobs:
            jobs[job_id].update(kwargs)


def _log(job_id: str, message: str, progress: Optional[int] = None):
    with jobs_lock:
        if job_id in jobs:
            jobs[job_id]["logs"].append(message)
            if progress is not None:
                jobs[job_id]["progress"] = progress
    print(f"[{job_id[:8]}] {message}")


# ---------------------------------------------------------------------------
# Core pipeline (runs in background thread)
# ---------------------------------------------------------------------------

def _run_pipeline(
    job_id: str,
    audio_path: str,
    mode: BackgroundMode,
    orientation: VideoOrientation,
    output_path: str,
    captions_enabled: bool,
):
    try:
        _update_job(job_id, status="running")
        orientation_landscape = orientation == VideoOrientation.landscape

        # Step 1 — Transcribe
        _log(job_id, "🎙️ Transcribing audio with Whisper...", progress=10)
        timed_captions = generate_timed_captions(audio_path)
        transcript_text = " ".join(text for (_, _), text in timed_captions)
        _log(job_id, f"✅ Transcription complete — {len(timed_captions)} segments.", progress=25)

        # Step 2 — Generate search queries
        _log(job_id, "🤖 Generating B-roll search queries with AI...", progress=30)
        search_terms = getVideoSearchQueriesTimed(transcript_text, timed_captions)
        if not search_terms:
            raise RuntimeError("AI failed to generate search queries.")
        _log(job_id, f"✅ {len(search_terms)} search queries generated.", progress=45)

        # Step 3 — Fetch background media
        background_data = None

        if mode == BackgroundMode.video:
            _log(job_id, "🎬 Fetching video B-roll from Pexels...", progress=50)
            raw = generate_video_url(search_terms, "pexel", orientation_landscape=orientation_landscape)
            background_data = merge_empty_intervals(raw)
            _log(job_id, f"✅ {len(background_data)} video segments fetched.", progress=65)

        elif mode == BackgroundMode.image:
            _log(job_id, "🖼️ Fetching stock images from Pexels...", progress=50)
            raw = generate_image_url(search_terms, orientation_landscape=orientation_landscape)
            background_data = merge_empty_intervals(raw)
            _log(job_id, f"✅ {len(background_data)} images fetched.", progress=65)

        elif mode == BackgroundMode.mix:
            _log(job_id, "🎞️ Fetching mixed media (images + video) from Pexels...", progress=50)
            video_raw = generate_video_url(search_terms, "pexel", orientation_landscape=orientation_landscape)
            image_raw = generate_image_url(search_terms, orientation_landscape=orientation_landscape)

            # Alternate: even index → video, odd index → image
            mixed = []
            for i, (interval, _) in enumerate(video_raw):
                if i % 2 == 0 and video_raw[i][1]:
                    mixed.append(video_raw[i])
                elif image_raw[i][1]:
                    mixed.append(image_raw[i])
                elif video_raw[i][1]:
                    mixed.append(video_raw[i])
                else:
                    mixed.append(image_raw[i])

            background_data = merge_empty_intervals(mixed)
            _log(job_id, f"✅ {len(background_data)} mixed media segments ready.", progress=65)

        if not background_data:
            raise RuntimeError("No background media available.")

        # Step 4 — Render
        _log(job_id, "🎥 Rendering final video (this takes a moment)...", progress=70)

        def progress_cb(step: str, pct: int):
            _log(job_id, step, progress=70 + int(pct * 0.28))

        result_path = get_output_media(
            audio_path,
            timed_captions,
            background_data,
            "pexel",
            output_path=output_path,
            mode=mode.value,
            progress_callback=progress_cb,
            orientation_landscape=orientation_landscape,
            captions_enabled=captions_enabled,
        )

        _log(job_id, "✅ Video rendered successfully!", progress=100)
        _update_job(job_id, status="done", output_path=result_path)

    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        print(f"[{job_id[:8]}] Exception Traceback:\n{trace}")
        _log(job_id, f"❌ Error: {str(e)}")
        _update_job(job_id, status="error", error=str(e))
    finally:
        # Clean up temp audio upload
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@app.post("/api/generate")
async def generate(
    audio: UploadFile = File(...),
    mode: BackgroundMode = Form(BackgroundMode.video),
    orientation: VideoOrientation = Form(VideoOrientation.portrait),
    captions_enabled: bool = Form(True),
):
    """Upload an audio file and start a video generation job."""
    ext = os.path.splitext(audio.filename or "")[1].lower()
    if ext not in (".mp3", ".wav"):
        raise HTTPException(status_code=400, detail="Only .mp3 and .wav files are supported.")

    # Save uploaded audio to temp file
    tmp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    content = await audio.read()
    tmp_audio.write(content)
    tmp_audio.close()

    # Prepare output path
    job_id = str(uuid.uuid4())
    output_dir = tempfile.gettempdir()
    output_path = os.path.join(output_dir, f"video_{job_id}.mp4")

    # Register job
    with jobs_lock:
        jobs[job_id] = {
            "id": job_id,
            "status": "queued",
            "progress": 0,
            "logs": ["⏳ Job queued, starting soon..."],
            "output_path": None,
            "error": None,
            "mode": mode.value,
            "orientation": orientation.value,
        }

    # Submit to background thread
    executor.submit(_run_pipeline, job_id, tmp_audio.name, mode, orientation, output_path, captions_enabled)

    return JSONResponse({"job_id": job_id, "status": "queued"})


@app.get("/api/status/{job_id}")
def get_status(job_id: str):
    """Poll for job status, progress, and logs."""
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "logs": job["logs"],
        "error": job.get("error"),
    }


@app.get("/api/download/{job_id}")
def download_video(job_id: str):
    """Download the rendered video once the job is done."""
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job["status"] != "done":
        raise HTTPException(status_code=400, detail=f"Job is not complete yet (status: {job['status']}).")

    output_path = job.get("output_path")
    if not output_path or not os.path.exists(output_path):
        raise HTTPException(status_code=404, detail="Output file not found.")

    return FileResponse(
        output_path,
        media_type="video/mp4",
        filename=f"generated_video_{job_id[:8]}.mp4",
    )


@app.get("/api/jobs")
def list_jobs():
    """List all jobs (for debugging)."""
    with jobs_lock:
        return [
            {"job_id": jid, "status": j["status"], "progress": j["progress"]}
            for jid, j in jobs.items()
        ]
