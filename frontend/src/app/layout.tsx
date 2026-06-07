import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'VideoAI Studio — Turn Audio Into Stunning Videos',
  description:
    'Upload your audio narration and let AI generate a cinematic B-roll video with Pexels stock footage or images. Free to try — no credit card required.',
  keywords: ['AI video generator', 'text to video', 'B-roll generator', 'audio to video', 'Pexels AI'],
  openGraph: {
    title: 'VideoAI Studio',
    description: 'Transform audio narrations into stunning videos powered by AI.',
    type: 'website',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="noise">
        {/* Ambient background blobs */}
        <div className="blob blob-1" aria-hidden="true" />
        <div className="blob blob-2" aria-hidden="true" />
        <div style={{ position: 'relative', zIndex: 1 }}>{children}</div>
      </body>
    </html>
  );
}
