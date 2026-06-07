'use client';

import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import type { JobStatus } from '@/lib/api';

interface ProgressPanelProps {
  status: JobStatus | null;
}

const STATUS_LABELS: Record<string, string> = {
  queued:  'Queued',
  running: 'Processing',
  done:    'Complete',
  error:   'Failed',
};

function classifyLog(line: string) {
  if (line.includes('✅') || line.includes('Complete') || line.includes('Done')) return 'success';
  if (line.includes('❌') || line.includes('Error') || line.includes('Failed')) return 'error';
  if (line.includes('🎙') || line.includes('🤖') || line.includes('🎬') || line.includes('🖼') || line.includes('🎞') || line.includes('⏳')) return 'info';
  return '';
}

export default function ProgressPanel({ status }: ProgressPanelProps) {
  const logRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new log lines arrive
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [status?.logs]);

  if (!status) return null;

  const progress = status.progress ?? 0;
  const statusKey = status.status as string;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{ fontWeight: 700, fontSize: 15 }}>Generation Progress</div>
        <span className={`status-badge ${statusKey}`}>
          {statusKey === 'running' && (
            <span
              style={{
                display: 'inline-block',
                width: 8, height: 8,
                borderRadius: '50%',
                background: 'var(--cyan)',
                marginRight: 4,
                animation: 'pulse-glow 1.5s ease-in-out infinite',
              }}
            />
          )}
          {STATUS_LABELS[statusKey] ?? statusKey}
        </span>
      </div>

      {/* Progress bar */}
      <div className="progress-bar" style={{ marginBottom: 6 }}>
        <motion.div
          className="progress-fill"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
      <div style={{ textAlign: 'right', fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
        {progress}%
      </div>

      {/* Log console */}
      <div className="section-label">Live Log</div>
      <div className="log-console" ref={logRef}>
        {(status.logs ?? []).map((line, i) => (
          <div key={i} className={`log-line ${classifyLog(line)}`}>
            {line}
          </div>
        ))}
        {statusKey === 'running' && (
          <div className="log-line info" style={{ opacity: 0.6 }}>▌</div>
        )}
      </div>

      {/* Error detail */}
      {statusKey === 'error' && status.error && (
        <div
          style={{
            marginTop: 12,
            padding: '12px 16px',
            background: 'rgba(239,68,68,0.08)',
            border: '1px solid rgba(239,68,68,0.25)',
            borderRadius: 10,
            fontSize: 13,
            color: 'var(--red)',
          }}
        >
          <strong>Error:</strong> {status.error}
        </div>
      )}
    </motion.div>
  );
}
