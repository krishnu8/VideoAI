const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export type BackgroundMode = 'video' | 'image' | 'mix';
export type Orientation = 'portrait' | 'landscape';

export interface JobStatus {
  job_id: string;
  status: 'queued' | 'running' | 'done' | 'error';
  progress: number;
  logs: string[];
  error?: string;
}

/**
 * Upload audio and start a video generation job.
 * Returns the job_id to poll with getStatus().
 */
export async function startJob(
  audioFile: File,
  mode: BackgroundMode,
  orientation: Orientation,
  captionsEnabled: boolean
): Promise<string> {
  const formData = new FormData();
  formData.append('audio', audioFile);
  formData.append('mode', mode);
  formData.append('orientation', orientation);
  formData.append('captions_enabled', String(captionsEnabled));

  const res = await fetch(`${API_BASE}/api/generate`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  const data = await res.json();
  return data.job_id as string;
}

/** Poll job status. */
export async function getStatus(jobId: string): Promise<JobStatus> {
  const res = await fetch(`${API_BASE}/api/status/${jobId}`);
  if (!res.ok) throw new Error(`Status fetch failed: HTTP ${res.status}`);
  return res.json();
}

/** Returns the download URL for a completed job. */
export function getDownloadUrl(jobId: string): string {
  return `${API_BASE}/api/download/${jobId}`;
}
