import { useState, useEffect, useRef } from 'react';
import { useApp } from '../utils/AppContext';

export default function ExplanationDrawer() {
  const {
    drawerOpen,
    drawerSong,
    drawerSongObj,
    closeDrawer,
    activeSong,
    isPlaying,
    playSong,
    togglePlay,
    submitFeedback,
    audioCurrentTime,
    audioDuration,
    likedSongs,
    toggleLikeSong
  } = useApp();

  const [isAccordionOpen, setIsAccordionOpen] = useState(false);
  const [waveformHeights, setWaveformHeights] = useState<number[]>([]);
  const [showScrollShadow, setShowScrollShadow] = useState(false);
  const drawerRef = useRef<HTMLDivElement>(null);

  // Generate deterministic heights for the waveform bars based on song ID
  const getDeterministicWaveform = (songId: string): number[] => {
    const heights: number[] = [];
    let hash = 0;
    for (let i = 0; i < songId.length; i++) {
      hash = songId.charCodeAt(i) + ((hash << 5) - hash);
    }
    for (let i = 0; i < 40; i++) {
      const pseudoRandom = Math.abs(Math.sin(hash + i) * 20);
      heights.push(Math.floor(pseudoRandom) + 8);
    }
    return heights;
  };

  useEffect(() => {
    if (drawerSongObj) {
      setWaveformHeights(getDeterministicWaveform(drawerSongObj.id));
    }
  }, [drawerSongObj?.id]);

  const handleScroll = () => {
    if (drawerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = drawerRef.current;
      const isScrollable = scrollHeight > clientHeight;
      const isAtBottom = scrollTop + clientHeight >= scrollHeight - 5;
      setShowScrollShadow(isScrollable && !isAtBottom);
    }
  };

  useEffect(() => {
    if (drawerOpen) {
      const handle = setTimeout(handleScroll, 50);
      return () => clearTimeout(handle);
    }
  }, [drawerOpen, isAccordionOpen, drawerSongObj]);

  if (!drawerSongObj) return null;

  const isCurrentActive = activeSong && activeSong.id === drawerSongObj.id;
  const showPlaying = isCurrentActive && isPlaying;
  
  // Audio timing calculations
  const progressPercent = isCurrentActive && audioDuration > 0 ? (audioCurrentTime / audioDuration) : 0;
  const activeBarsCount = Math.floor(progressPercent * 40);

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const handlePlayToggle = () => {
    if (isCurrentActive) {
      togglePlay();
    } else {
      playSong(drawerSongObj);
    }
  };

  return (
    <>
      <div className={`backdrop${drawerOpen ? ' on' : ''}`} onClick={closeDrawer} />
      <div ref={drawerRef} className={`drawer${drawerOpen ? ' on' : ''}`} onScroll={handleScroll}>
        <div className="drawer-handle" />
        <div className="drawer-content-top">
          
          {/* Header section with title and close button */}
          <div className="drawer-header-row">
            <div>
              <div className="drawer-eyebrow">
                {isCurrentActive && isPlaying ? "Now Playing" : "Recommended For You"}
              </div>
            </div>
            <button onClick={closeDrawer} className="drawer-close-btn" aria-label="Close drawer">✕</button>
          </div>

          {/* Large Album Art or Fallback */}
          {drawerSongObj.imgUrl ? (
            <img 
              src={drawerSongObj.imgUrl} 
              className="drawer-img" 
              alt={drawerSongObj.title} 
            />
          ) : (
            <div className="drawer-fallback-art" style={{ background: drawerSongObj.bg }}>
              {drawerSongObj.emoji}
            </div>
          )}

          {/* Metadata */}
          <div className="drawer-meta-row">
            <div>
              <div className="drawer-song-title">{drawerSongObj.title}</div>
              <div className="drawer-song-sub">{drawerSongObj.artist}</div>
            </div>
            <span className="pill on drawer-genre-badge">
              {drawerSongObj.genre}
            </span>
          </div>

          {/* Dynamic Audio Controls & Waveform */}
          <div className="drawer-player-controls">
            <button className="drawer-play-btn" onClick={handlePlayToggle} aria-label={showPlaying ? "Pause" : "Play"}>
              <span className="material-symbols-outlined">
                {showPlaying ? 'pause' : 'play_arrow'}
              </span>
            </button>
            <div className="drawer-waveform-wrap">
              <div className="waveform-container">
                {waveformHeights.map((h, i) => (
                  <div 
                    key={i} 
                    className={`waveform-bar${i < activeBarsCount ? ' active' : ''}`} 
                    style={{ height: `${h}px` }} 
                  />
                ))}
              </div>
              <div className="drawer-time-labels">
                <span>{isCurrentActive ? formatTime(audioCurrentTime) : '0:00'}</span>
                <span>{isCurrentActive && audioDuration ? formatTime(audioDuration) : '0:30'}</span>
              </div>
            </div>
          </div>

          {/* Feedback controls inside bottom sheet */}
          <div className="drawer-feedback-row">
            <button 
              className="drawer-feedback-btn error"
              onClick={() => {
                submitFeedback(drawerSongObj.id, 'dislike');
                closeDrawer();
              }}
              title="Not for me"
              aria-label="Dislike"
            >
              <span className="material-symbols-outlined">heart_broken</span>
            </button>
            <button 
              className={`drawer-feedback-btn success${likedSongs.has(drawerSongObj.id) ? ' liked' : ''}`}
              onClick={() => {
                toggleLikeSong(drawerSongObj.id);
                submitFeedback(drawerSongObj.id, 'like');
              }}
              title="Dey blow"
              aria-label="Like"
              style={likedSongs.has(drawerSongObj.id) ? { color: '#ba1a1a', borderColor: '#ba1a1a' } : undefined}
            >
              <span 
                className="material-symbols-outlined"
                style={likedSongs.has(drawerSongObj.id) ? { fontVariationSettings: '"FILL" 1' } : undefined}
              >
                favorite
              </span>
            </button>
          </div>

          {/* Collapsible Accordion: Why this song? */}
          <div className="drawer-accordion-wrap">
            <button 
              className="accordion-trigger" 
              onClick={() => setIsAccordionOpen(!isAccordionOpen)}
            >
              <span>Why this song?</span>
              <span className="material-symbols-outlined" style={{ transform: isAccordionOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}>
                expand_more
              </span>
            </button>
            <div 
              className="accordion-content" 
              style={{ 
                maxHeight: isAccordionOpen ? '600px' : '0px',
                opacity: isAccordionOpen ? 1 : 0
              }}
            >
              <div className="drawer-accordion-inner">
                <div className="drawer-reason">
                  <p>{drawerSong.reason}</p>
                </div>
                <div className="factor-list">
                  {drawerSong.factors.map((f) => (
                    <div className="factor-row" key={f.label}>
                      <div className="factor-ico">{f.emoji}</div>
                      <div className="factor-info">
                        <div className="factor-label">{f.label}</div>
                        <div className="factor-val">{f.value}</div>
                      </div>
                      <div className="factor-boost">{f.boost}</div>
                    </div>
                  ))}
                </div>
                
                {/* Confidence Bar */}
                <div className="drawer-match-summary">
                  <div className="drawer-match-header">
                    <span className="drawer-eyebrow drawer-eyebrow-nomargin">Overall match</span>
                    <span className="conf-match-pct">{drawerSong.matchPct}% match</span>
                  </div>
                  <div className="conf-track conf-track-thin">
                    <div className="conf-fill" style={{ width: `${drawerSong.matchPct}%` }} />
                  </div>
                </div>

              </div>
            </div>
          </div>

        </div>
        {showScrollShadow && <div className="drawer-scroll-shadow" />}
      </div>
    </>
  );
}
