# Text-To-Video AI 🎬

A full-stack, market-ready SaaS application that turns audio narrations into cinematic videos using AI. Upload an audio file, and the AI automatically transcribes it, extracts keywords, fetches matching background media (videos, stock images, or a mix of both), and renders a polished 1080p MP4.

[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

---

## Architecture

This project is separated into a backend API and a frontend UI.

- **Backend (Python / FastAPI)**: Handles transcription (Whisper), AI keyword extraction (Ollama), media fetching (Pexels), and video rendering (MoviePy). Ready to be deployed to Railway.
- **Frontend (Next.js / React)**: A premium glassmorphism UI for users to upload audio, tweak settings, watch live generation progress, and download the final video. Ready to be deployed to Vercel.

---

## Features

- **3 Background Modes**: Choose between pure video B-roll, high-quality image slideshows, or a dynamic mix of both.
- **2 Orientations**: Render in Portrait (1080x1920) for Shorts/Reels/TikTok, or Landscape (1920x1080) for YouTube.
- **Live Progress**: Watch the backend's progress in real-time on the frontend via polling.
- **Premium UI**: Beautiful dark mode interface with drag-and-drop file upload.

---

## Deployment Guide

### 1. Deploy the Backend (Railway)

The backend is configured for 1-click deployment on Railway using Nixpacks.

1. Fork or clone this repository to your GitHub account.
2. Go to [Railway](https://railway.app/) and click **New Project** → **Deploy from GitHub repo**.
3. Select this repository. Railway will detect the `railway.toml` and `Procfile`.
4. Go to the **Variables** tab for your new Railway service and add the following:
   - `LLM_PROVIDER`: `ollama`
   - `OLLAMA_BASE_URL`: `https://ollama.com/api` (or your endpoint)
   - `OLLAMA_API_KEY`: Your Ollama Cloud token
   - `OLLAMA_MODEL`: `qwen3.5:cloud`
   - `PEXELS_API_KEY`: Your [Pexels API key](https://www.pexels.com/api/)
   - `CORS_ORIGINS`: `*` (Change to your Vercel URL later for security, e.g., `https://your-frontend.vercel.app`)
5. Railway will automatically build and deploy the FastAPI server. Grab the public domain URL Railway gives you.

### 2. Deploy the Frontend (Vercel)

1. Go to [Vercel](https://vercel.com/) and click **Add New** → **Project**.
2. Select the same repository.
3. In the project setup, set the **Root Directory** to `frontend`.
4. Under **Environment Variables**, add:
   - `NEXT_PUBLIC_API_URL`: The URL you got from Railway in step 1 (e.g., `https://your-api.up.railway.app`).
5. Click **Deploy**.

---

## Local Development

### Backend Setup
1. Open a terminal in the root directory.
2. Create a virtual environment: `python -m venv venv`
3. Activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in your API keys. Make sure `CORS_ORIGINS=http://localhost:3000`.
6. Run the server: `uvicorn app:app --reload`
   - The API will be available at `http://localhost:8000`.

### Frontend Setup
1. Open a second terminal and navigate to the frontend folder: `cd frontend`
2. Install dependencies: `npm install`
3. Create a `.env.local` file inside `frontend/` with:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
4. Run the development server: `npm run dev`
5. Open `http://localhost:3000` in your browser.

---

## Note on Video Storage
By default, rendered videos are stored in the server's temporary directory (`/tmp`) and served directly back to the user for download. Because Railway's filesystem is ephemeral, these files are wiped whenever the server restarts or redeploys. Download your videos immediately after they finish rendering!
