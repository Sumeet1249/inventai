'use client';

export default function ShootingStarsBackground() {
  return (
    <>
      <style>{`
        @keyframes shootingStar {
          0% {
            left: 100%;
            top: 0%;
            opacity: 1;
            box-shadow: -50px -50px 35px rgba(255, 255, 255, 0.5), -50px -50px 60px rgba(255, 255, 255, 0.3);
          }
          100% {
            left: 0%;
            top: 100%;
            opacity: 0;
            box-shadow: 0 0 5px rgba(255, 255, 255, 0);
          }
        }

        .shooting-stars-container {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
          z-index: 0;
          overflow: hidden;
        }

        .shooting-star {
          position: absolute;
          width: 2px;
          height: 2px;
          background: rgba(255, 255, 255, 0.8);
          border-radius: 50%;
          filter: drop-shadow(0 0 2px rgba(255, 255, 255, 0.8));
        }

        .star-1 {
          animation: shootingStar 3s ease-in infinite;
          animation-delay: 0s;
        }

        .star-2 {
          animation: shootingStar 2.5s ease-in infinite;
          animation-delay: 0.8s;
        }

        .star-3 {
          animation: shootingStar 3.5s ease-in infinite;
          animation-delay: 1.6s;
        }

        .star-4 {
          animation: shootingStar 2.8s ease-in infinite;
          animation-delay: 2.4s;
        }

        .star-5 {
          animation: shootingStar 3.2s ease-in infinite;
          animation-delay: 3.2s;
        }

        .star-6 {
          animation: shootingStar 2.9s ease-in infinite;
          animation-delay: 4s;
        }
      `}</style>

      <div className="shooting-stars-container">
        <div className="shooting-star star-1" style={{ right: '20%', top: '10%' }} />
        <div className="shooting-star star-2" style={{ right: '30%', top: '15%' }} />
        <div className="shooting-star star-3" style={{ right: '50%', top: '5%' }} />
        <div className="shooting-star star-4" style={{ right: '10%', top: '20%' }} />
        <div className="shooting-star star-5" style={{ right: '70%', top: '8%' }} />
        <div className="shooting-star star-6" style={{ right: '40%', top: '12%' }} />
      </div>
    </>
  );
}
