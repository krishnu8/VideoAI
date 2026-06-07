'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';

interface AudioDropzoneProps {
  onFile: (file: File) => void;
  file: File | null;
}

export default function AudioDropzone({ onFile, file }: AudioDropzoneProps) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted[0]) onFile(accepted[0]);
    },
    [onFile]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'audio/mpeg': ['.mp3'], 'audio/wav': ['.wav'] },
    maxFiles: 1,
    multiple: false,
  });

  const formatSize = (bytes: number) => {
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  };

  return (
    <div
      {...getRootProps()}
      className={`dropzone ${isDragActive ? 'active' : ''} ${file ? 'has-file' : ''}`}
      id="audio-dropzone"
    >
      <input {...getInputProps()} id="audio-input" />

      <AnimatePresence mode="wait">
        {file ? (
          <motion.div
            key="has-file"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
          >
            <div style={{ fontSize: 36, marginBottom: 12 }}>✅</div>
            <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4, color: '#10b981' }}>
              {file.name}
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              {formatSize(file.size)} · Click or drag to replace
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="no-file"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div style={{ fontSize: 48, marginBottom: 16 }}>
              {isDragActive ? '🎯' : '🎙️'}
            </div>
            <div style={{ fontWeight: 700, fontSize: 17, marginBottom: 8 }}>
              {isDragActive ? 'Drop your audio here' : 'Upload your audio narration'}
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              Drag & drop or click to browse · MP3 and WAV supported
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
