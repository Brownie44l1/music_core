import { useApp } from '../utils/AppContext';

export default function MiniPlayer() {
  const { 
    activeSong, 
    isPlaying, 
    togglePlay, 
    openDrawer, 
    openDrawerForRecommendation,
    audioCurrentTime,
    audioDuration,
    likedSongs,
    toggleLikeSong
  } = useApp();

  if (!activeSong) return null;

  const progressPercent = audioDuration > 0 ? (audioCurrentTime / audioDuration) : 0;

  return (
    <div 
      className="mini-player-container"
      onClick={() => {
        if (activeSong.recommendationId) {
          openDrawerForRecommendation(activeSong.recommendationId, activeSong);
        } else {
          openDrawer(undefined, activeSong);
        }
      }}
    >
      <div className="mini-player-pill" style={{ position: 'relative', overflow: 'hidden' }}>
        {activeSong.imgUrl ? (
          <img 
            className="mini-player-img" 
            src={activeSong.imgUrl} 
            alt={activeSong.title} 
          />
        ) : (
          <div className="mini-player-fallback-art" style={{ background: activeSong.bg }}>
            {activeSong.emoji}
          </div>
        )}
        <div className="mini-player-info">
          <h5 className="mini-player-title">{activeSong.title}</h5>
          <p className="mini-player-artist">{activeSong.artist}</p>
        </div>
        <div className="mini-player-actions">
          <button 
            className={`mini-player-btn-fav ${likedSongs.has(activeSong.id) ? 'liked' : ''}`}
            aria-label={likedSongs.has(activeSong.id) ? "Unlike" : "Like"}
            onClick={(e) => {
              e.stopPropagation();
              toggleLikeSong(activeSong.id);
            }}
          >
            <span 
              className="material-symbols-outlined" 
              style={likedSongs.has(activeSong.id) ? { fontVariationSettings: '"FILL" 1' } : undefined}
            >
              favorite
            </span>
          </button>
          <button 
            className="mini-player-btn-play"
            aria-label={isPlaying ? "Pause" : "Play"}
            onClick={(e) => {
              e.stopPropagation();
              togglePlay();
            }}
          >
            <span 
              className="material-symbols-outlined"
            >
              {isPlaying ? 'pause' : 'play_arrow'}
            </span>
          </button>
        </div>
        
        {/* Playback progress line at the bottom of the pill */}
        <div 
          className="mini-player-progress-bar" 
          style={{ width: `${progressPercent * 100}%` }}
        />
      </div>
    </div>
  );
}
