'use client';

import type { BackgroundMode, Orientation } from '@/lib/api';

interface SettingsToggleProps {
  mode: BackgroundMode;
  orientation: Orientation;
  captionsEnabled: boolean;
  onMode: (m: BackgroundMode) => void;
  onOrientation: (o: Orientation) => void;
  onCaptionsEnabled: (c: boolean) => void;
  disabled?: boolean;
}

const MODE_OPTIONS: { value: BackgroundMode; label: string; icon: string; desc: string }[] = [
  { value: 'video', label: 'Video Only',   icon: '🎬', desc: 'Pexels stock video B-roll' },
  { value: 'image', label: 'Images Only',  icon: '🖼️', desc: 'Pexels stock photo slideshow' },
  { value: 'mix',   label: 'Mix of Both',  icon: '🎞️', desc: 'Alternating video + images' },
];

const ORIENT_OPTIONS: { value: Orientation; label: string; icon: string; desc: string }[] = [
  { value: 'portrait',  label: 'Portrait',  icon: '📱', desc: 'Shorts · Reels · TikTok (1080×1920)' },
  { value: 'landscape', label: 'Landscape', icon: '🖥️', desc: 'YouTube · Standard (1920×1080)' },
];

export default function SettingsToggle({
  mode, orientation, captionsEnabled, onMode, onOrientation, onCaptionsEnabled, disabled = false,
}: SettingsToggleProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

      {/* Background Mode */}
      <div>
        <div className="section-label">Background Mode</div>
        <div className="toggle-group" style={{ width: '100%' }}>
          {MODE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              className={`toggle-option ${mode === opt.value ? 'active' : ''}`}
              onClick={() => !disabled && onMode(opt.value)}
              disabled={disabled}
              id={`mode-${opt.value}`}
              title={opt.desc}
              style={{ flex: 1, justifyContent: 'center' }}
            >
              <span>{opt.icon}</span>
              <span>{opt.label}</span>
            </button>
          ))}
        </div>
        <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8, paddingLeft: 4 }}>
          {MODE_OPTIONS.find((o) => o.value === mode)?.desc}
        </p>
      </div>

      {/* Orientation */}
      <div>
        <div className="section-label">Video Orientation</div>
        <div className="toggle-group">
          {ORIENT_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              className={`toggle-option ${orientation === opt.value ? 'active' : ''}`}
              onClick={() => !disabled && onOrientation(opt.value)}
              disabled={disabled}
              id={`orient-${opt.value}`}
              title={opt.desc}
            >
              <span>{opt.icon}</span>
              <span>{opt.label}</span>
            </button>
          ))}
        </div>
        <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8, paddingLeft: 4 }}>
          {ORIENT_OPTIONS.find((o) => o.value === orientation)?.desc}
        </p>
      </div>
      {/* Captions Toggle */}
      <div>
        <div className="section-label">AI Captions</div>
        <div className="toggle-group" style={{ display: 'inline-flex' }}>
          <button
            className={`toggle-option ${captionsEnabled ? 'active' : ''}`}
            onClick={() => !disabled && onCaptionsEnabled(true)}
            disabled={disabled}
            id="captions-on"
          >
            <span>📝</span>
            <span>On</span>
          </button>
          <button
            className={`toggle-option ${!captionsEnabled ? 'active' : ''}`}
            onClick={() => !disabled && onCaptionsEnabled(false)}
            disabled={disabled}
            id="captions-off"
          >
            <span>🚫</span>
            <span>Off</span>
          </button>
        </div>
        <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8, paddingLeft: 4 }}>
          {captionsEnabled ? 'Whisper transcript overlaid on the video' : 'No text on the video'}
        </p>
      </div>
    </div>
  );
}
