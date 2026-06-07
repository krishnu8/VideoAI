'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

const features = [
  {
    icon: '🎙️',
    title: 'Upload Your Audio',
    desc: 'Drop any MP3 or WAV narration file. Our Whisper-powered engine transcribes it instantly.',
  },
  {
    icon: '🤖',
    title: 'AI Picks the Visuals',
    desc: 'The LLM reads your script and generates perfect Pexels search terms for every sentence.',
  },
  {
    icon: '🎬',
    title: 'Three Background Modes',
    desc: 'Choose stock videos, stock images, or a cinematic mix of both — all from Pexels.',
  },
  {
    icon: '⚡',
    title: 'Instant Download',
    desc: 'Renders to 1080p MP4 in minutes. Portrait for Shorts & Reels, landscape for YouTube.',
  },
];

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } },
};
const item = {
  hidden: { opacity: 0, y: 24 },
  show:  { opacity: 1, y: 0,  transition: { duration: 0.5 } },
};

export default function HomePage() {
  return (
    <>
      {/* ── Nav ── */}
      <nav className="nav">
        <span className="nav-logo gradient-text">VideoAI Studio</span>
        <Link href="/studio" className="btn-primary" style={{ padding: '10px 24px', fontSize: 14 }}>
          Open Studio →
        </Link>
      </nav>

      {/* ── Hero ── */}
      <section className="hero">
        <motion.div initial={{ opacity: 0, y: 32 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
          <div
            style={{
              display: 'inline-block',
              padding: '6px 18px',
              borderRadius: 99,
              border: '1px solid rgba(124,58,237,0.4)',
              background: 'rgba(124,58,237,0.1)',
              fontSize: 13,
              fontWeight: 600,
              color: '#a855f7',
              marginBottom: 28,
              letterSpacing: '0.05em',
            }}
          >
            ✦ Powered by Whisper · Ollama · Pexels
          </div>

          <h1>
            Turn Audio Into
            <br />
            <span className="gradient-text">Cinematic Videos</span>
          </h1>

          <p>
            Upload a narration. Our AI transcribes, searches for the perfect B-roll,
            and renders a polished 1080p video — in minutes.
          </p>

          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link href="/studio" className="btn-primary">
              🎬 Start Creating Free
            </Link>
            <a
              href="https://github.com"
              className="btn-ghost"
              target="_blank"
              rel="noopener noreferrer"
            >
              View on GitHub
            </a>
          </div>
        </motion.div>

        {/* Mock video preview */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          style={{ marginTop: 64, position: 'relative' }}
        >
          <div
            className="glass pulse"
            style={{
              padding: '6px',
              borderRadius: 24,
              display: 'inline-block',
            }}
          >
            <div
              style={{
                width: 200,
                height: 356,
                borderRadius: 18,
                background: 'linear-gradient(160deg, #1a0533 0%, #0a1628 50%, #001a1a 100%)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 12,
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <div style={{ fontSize: 40 }}>🎬</div>
              <div style={{ fontSize: 13, color: 'rgba(255,255,255,0.6)', textAlign: 'center', padding: '0 20px' }}>
                Your video renders here
              </div>
              {/* fake captions */}
              <div
                style={{
                  position: 'absolute',
                  bottom: 32,
                  left: 12, right: 12,
                  background: 'rgba(0,0,0,0.7)',
                  borderRadius: 8,
                  padding: '6px 10px',
                  fontSize: 11,
                  fontWeight: 700,
                  color: '#fff',
                  textAlign: 'center',
                }}
              >
                AI-generated captions appear here
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* ── Features ── */}
      <section style={{ paddingBottom: 80 }}>
        <motion.div
          className="feature-grid"
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-80px' }}
        >
          {features.map((f) => (
            <motion.div key={f.title} className="feature-card" variants={item}>
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* CTA banner */}
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          style={{ textAlign: 'center', padding: '0 24px' }}
        >
          <div
            className="glass"
            style={{
              maxWidth: 600,
              margin: '0 auto',
              padding: '48px 40px',
              background: 'linear-gradient(135deg, rgba(124,58,237,0.15) 0%, rgba(6,182,212,0.1) 100%)',
              borderColor: 'rgba(124,58,237,0.3)',
            }}
          >
            <h2 style={{ fontSize: 32, fontWeight: 800, marginBottom: 12, letterSpacing: '-0.03em' }}>
              Ready to go viral?
            </h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 28 }}>
              Create your first AI video in under 5 minutes.
            </p>
            <Link href="/studio" className="btn-primary">
              Open Studio — It&apos;s Free →
            </Link>
          </div>
        </motion.div>
      </section>

      {/* ── Footer ── */}
      <footer
        style={{
          textAlign: 'center',
          padding: '32px 24px',
          borderTop: '1px solid var(--border)',
          color: 'var(--text-muted)',
          fontSize: 13,
        }}
      >
        VideoAI Studio · Powered by Whisper, Ollama & Pexels
      </footer>
    </>
  );
}
