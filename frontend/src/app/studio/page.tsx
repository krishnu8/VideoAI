'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';

import AudioDropzone from '@/components/AudioDropzone';
import SettingsToggle from '@/components/SettingsToggle';
import ProgressPanel from '@/components/ProgressPanel';
import VideoPlayer from '@/components/VideoPlayer';

import { startJob, getStatus } from '@/lib/api';
import type { BackgroundMode, JobStatus, Orientation } from '@/lib/api';

type Stage = 'idle' | 'uploading' | 'processing' | 'done' | 'error';

const POLL_INTERVAL_MS = 3000;

export default function StudioPage() {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [mode, setMode] = useState<BackgroundMode>('video');
  const [orientation, setOrientation] = useState<Orientation>('portrait');
  const [captionsEnabled, setCaptionsEnabled] = useState<boolean>(true);

  const [stage, setStage] = useState<Stage>('idle');
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ── Polling ──────────────────────────────────────────────────────
  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const startPolling = useCallback(
    (id: string) => {
      stopPolling();
      pollRef.current = setInterval(async () => {
        try {
          const status = await getStatus(id);
          setJobStatus(status);

          if (status.status === 'done') {
            setStage('done');
            stopPolling();
          } else if (status.status === 'error') {
            setStage('error');
            stopPolling();
          }
        } catch (e) {
          console.error('Polling error:', e);
        }
      }, POLL_INTERVAL_MS);
    },
    [stopPolling]
  );

  useEffect(() => () => stopPolling(), [stopPolling]);

  // ── Submit ───────────────────────────────────────────────────────
  async function handleGenerate() {
    if (!audioFile) return;

    setUploadError(null);
    setStage('uploading');
    setJobStatus(null);

    try {
      const id = await startJob(audioFile, mode, orientation, captionsEnabled);
      setJobId(id);
      setStage('processing');
      startPolling(id);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Upload failed';
      setUploadError(msg);
      setStage('error');
    }
  }

  const isDisabled = stage === 'uploading' || stage === 'processing';
  const canGenerate = !!audioFile && !isDisabled;

  // ── Render ───────────────────────────────────────────────────────
  return (
    <>
      {/* Nav */}
      <nav className="nav">
        <Link href="/" className="nav-logo gradient-text" style={{ textDecoration: 'none' }}>
          VideoAI Studio
        </Link>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {jobStatus && (
            <span className={`status-badge ${jobStatus.status}`}>
              {jobStatus.status}
            </span>
          )}
        </div>
      </nav>

      <main className="studio-layout">
        <div className="studio-header">
          <h1>
            Video <span className="gradient-text">Studio</span>
          </h1>
          <p>Upload your audio, pick a style, and let AI do the rest.</p>
        </div>

        {/* ── Step 1: Audio Upload ── */}
        <div className="studio-card">
          <div className="section-label">Step 1 — Upload Audio</div>
          <AudioDropzone onFile={setAudioFile} file={audioFile} />
        </div>

        {/* ── Step 2: Settings ── */}
        <div className="studio-card">
          <div className="section-label">Step 2 — Choose Style</div>
          <SettingsToggle
            mode={mode}
            orientation={orientation}
            captionsEnabled={captionsEnabled}
            onMode={setMode}
            onOrientation={setOrientation}
            onCaptionsEnabled={setCaptionsEnabled}
            disabled={isDisabled}
          />
        </div>

        {/* ── Error banner ── */}
        <AnimatePresence>
          {uploadError && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              style={{
                padding: '14px 18px',
                background: 'rgba(239,68,68,0.08)',
                border: '1px solid rgba(239,68,68,0.3)',
                borderRadius: 12,
                color: 'var(--red)',
                fontSize: 14,
                marginBottom: 16,
              }}
            >
              ❌ {uploadError}
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Generate Button ── */}
        {stage !== 'done' && (
          <button
            id="generate-btn"
            className="btn-primary"
            onClick={handleGenerate}
            disabled={!canGenerate}
            style={{ width: '100%', justifyContent: 'center', padding: '16px', fontSize: 16, marginBottom: 24 }}
          >
            {stage === 'uploading' && (
              <>
                <span className="spin" style={{ display: 'inline-block', width: 18, height: 18, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%' }} />
                Uploading...
              </>
            )}
            {stage === 'processing' && (
              <>
                <span className="spin" style={{ display: 'inline-block', width: 18, height: 18, border: '2px solid rgba(255,255,255,0.3)', borderTopColor: '#fff', borderRadius: '50%' }} />
                Generating Video...
              </>
            )}
            {(stage === 'idle' || stage === 'error') && '🎬 Generate Video'}
          </button>
        )}

        {/* ── Progress Panel ── */}
        <AnimatePresence>
          {jobStatus && stage !== 'done' && (
            <motion.div
              key="progress"
              className="studio-card"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              style={{ marginBottom: 24 }}
            >
              <ProgressPanel status={jobStatus} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Video Player ── */}
        <AnimatePresence>
          {stage === 'done' && jobId && (
            <motion.div
              key="player"
              className="studio-card"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="section-label">Your Video</div>
              <VideoPlayer jobId={jobId} orientation={orientation} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </>
  );
}
