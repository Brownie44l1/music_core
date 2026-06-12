import { useState } from 'react';
import { useApp } from '../utils/AppContext';
import { OB_MOODS, OB_ARTISTS } from '../data';

export default function Onboarding() {
  const { completeOnboarding } = useApp();
  const [step, setStep] = useState(1);
  const [selectedMood, setSelectedMood] = useState('Turn Up');
  const [artistInput, setArtistInput] = useState('');
  const [selectedArtist, setSelectedArtist] = useState('');
  const [isFinishing, setIsFinishing] = useState(false);

  const pickArtist = (a: string) => {
    setSelectedArtist(a);
    setArtistInput(a);
  };

  const handleFinish = async () => {
    setIsFinishing(true);
    await completeOnboarding(new Set<string>(), selectedArtist || artistInput);
    setIsFinishing(false);
  };

  return (
    <div className="ob-wrap">
      <div className="ob-progress">
        {[1, 2].map(i => (
          <div key={i} className={`ob-prog-seg${i < step ? ' done' : ''}${i === step ? ' active' : ''}`} />
        ))}
      </div>

      {/* Step 1 — Artist */}
      {step === 1 && (
        <div className="ob-step">
          <div className="ob-q">Who is your top artist?</div>
          <div className="ob-input-container" style={{ marginTop: '12px' }}>
            <div className="pill-grid" style={{ marginTop: '12px' }}>
              {OB_ARTISTS.map(a => (
                <span
                  key={a}
                  className={`pg-pill${selectedArtist === a ? ' on' : ''}`}
                  onClick={() => pickArtist(a)}
                >
                  {a}
                </span>
              ))}
            </div>
          </div>

          <div className="ob-btns">
            <button
              className="btn-primary"
              onClick={() => setStep(2)}
              disabled={!(selectedArtist || artistInput.trim())}
              style={{ width: '100%' }}
            >
              Continue
            </button>
          </div>
        </div>
      )}

      {/* Step 2 — Mood */}
      {step === 2 && (
        <div className="ob-step">
          <div className="ob-q">Pick your current mood</div>
          <div className="mood-grid">
            {OB_MOODS.map(m => (
              <div
                key={m.name}
                className={`mood-card${selectedMood === m.name ? ' on' : ''}`}
                onClick={() => setSelectedMood(m.name)}
              >
                <div className="mood-emoji">
                  <span>{m.emoji}</span>
                </div>
                <div className="mood-name">{m.name}</div>
                <div className="mood-desc">{m.desc}</div>
              </div>
            ))}
          </div>
          <div className="ob-btns">
            <button className="btn-primary" onClick={handleFinish} disabled={isFinishing}>
              {isFinishing ? 'Plugging In...' : "Plugged In"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
