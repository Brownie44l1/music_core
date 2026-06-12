import { useApp } from '../utils/AppContext';
import { MARQUEE_TAGS } from '../data';

function StarIcon() {
  return (
    <svg viewBox="0 0 480 512" xmlns="http://www.w3.org/2000/svg" className="landing-star-icon">
      <path d="M471.99 334.43L336.06 256l135.93-78.43c7.66-4.42 10.28-14.2 5.86-21.86l-32.02-55.43c-4.42-7.65-14.21-10.28-21.87-5.86l-135.93 78.43V16c0-8.84-7.17-16-16.01-16h-64.04c-8.84 0-16.01 7.16-16.01 16v156.86L56.04 94.43c-7.66-4.42-17.45-1.79-21.87 5.86L2.15 155.71c-4.42 7.65-1.8 17.44 5.86 21.86L143.94 256 8.01 334.43c-7.66 4.42-10.28 14.21-5.86 21.86l32.02 55.43c4.42 7.65 14.21 10.27 21.87 5.86l135.93-78.43V496c0 8.84 7.17 16 16.01 16h64.04c8.84 0 16.01-7.16 16.01-16V339.14l135.93 78.43c7.66 4.42 17.45 1.8 21.87-5.86l32.02-55.43c4.42-7.65 1.8-17.43-5.86-21.85z" />
    </svg>
  );
}

export default function Landing() {
  const { go } = useApp();
  const doubleTags = [...MARQUEE_TAGS, ...MARQUEE_TAGS];

  return (
    <div className="landing-wrap">
      <div className="landing-hero">
        <div className="landing-noise" />
        <div className="landing-content">
          <div className="landing-top">
            <div className="landing-logo">PLUGD</div>
            <h1 className="landing-h1">
              Music that match your <em>vibe.</em>
            </h1>
          </div>
          <div className="landing-bottom">
            <p className="landing-sub">
              Recommendations built for you, tuned to your taste.
            </p>
            <div className="genre-marquee-strip">
              <div className="marquee-inner">
                {doubleTags.map((tag, i) => (
                  <span key={i}>
                    <span className="mtag">{tag}</span>
                    <span className="mtag-star"><StarIcon /></span>
                  </span>
                ))}
              </div>
            </div>
            <div className="landing-actions">
              <button
                className="btn-primary btn-landing-primary"
                onClick={() => go('onboarding')}
              >
                Get Plugged
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
