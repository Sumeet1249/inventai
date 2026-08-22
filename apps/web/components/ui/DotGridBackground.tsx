'use client';

export default function DotGridBackground() {
  return (
    <>
      <style>{`
        .dot-grid-background {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
          z-index: 0;
          background-image: 
            radial-gradient(circle, rgba(255, 255, 255, 0.4) 1.5px, transparent 1.5px);
          background-size: 40px 40px;
          background-position: 0 0;
          animation: dotGridMove 30s linear infinite;
          overflow: hidden;
        }

        @keyframes dotGridMove {
          0% {
            background-position: 0 0;
          }
          100% {
            background-position: 40px 40px;
          }
        }

        .dot-grid-overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: linear-gradient(135deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.2) 100%);
          pointer-events: none;
          z-index: 1;
        }
      `}</style>

      <div className="dot-grid-background" />
      <div className="dot-grid-overlay" />
    </>
  );
}
