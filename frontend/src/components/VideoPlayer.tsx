'use client';

import { motion } from 'framer-motion';
import { getDownloadUrl } from '@/lib/api';
import type { Orientation } from '@/lib/api';

interface VideoPlayerProps {
  jobId: string;
  orientation: Orientation;
}

export default function VideoPlayer({ jobId, orientation }: VideoPlayerProps) {
  const downloadUrl = getDownloadUrl(jobId);
  const isPortrait = orientation === 'portrait';

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Success banner */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: '12px 16px',
          background: 'rgba(16,185,129,0.1)',
          border: '1px solid rgba(16,185,129,0.3)',
          borderRadius: 12,
          marginBottom: 20,
          fontSize: 14,
          color: '#10b981',
          fontWeight: 600,
        }}
      >
        <span style={{ fontSize: 20 }}>🎉</span>
        Your video is ready! Preview below or download it.
      </div>

      {/* Video preview */}
      <div
        className={`video-wrapper ${isPortrait ? '' : 'landscape'}`}
        style={{ marginBottom: 20 }}
      >
        <video
          id="video-preview"
          controls
          autoPlay
          loop
          playsInline
          src={downloadUrl}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        />
      </div>

      {/* Action buttons */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <a
          id="download-btn"
          href={downloadUrl}
          download={`video_${jobId.slice(0, 8)}.mp4`}
          className="btn-primary"
          style={{ flex: 1, justifyContent: 'center' }}
        >
          ⬇️ Download MP4
        </a>
        <button
          id="new-video-btn"
          className="btn-ghost"
          onClick={() => window.location.reload()}
          style={{ flex: 1, justifyContent: 'center' }}
        >
          ✨ Make Another
        </button>
      </div>

      <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 12, textAlign: 'center' }}>
        Video available until server redeploy. Download now to save it permanently.
      </p>
    </motion.div>
  );
}
