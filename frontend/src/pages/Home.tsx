import { useState } from 'react';
import { useApp } from '../utils/AppContext';
import BottomNav from '../components/BottomNav';
import { BANNER_CARDS, GENRE_FILTERS } from '../data';

export default function Home() {
  const {
    openDrawer,
    openDrawerForRecommendation,
    playSong,
    popularSongs,
    recommendedSongs,
    fetchPopularSongs,
    fetchRecommendations,
    activeSong,
    loadingPopular,
    loadingRecs
  } = useApp();
  const [activeFilter, setActiveFilter] = useState('All');

  const handleFilterChange = (genre: string) => {
    setActiveFilter(genre);
    fetchPopularSongs(genre);
  };

  const getDynamicEyebrow = () => {
    const now = new Date();
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const day = days[now.getDay()];
    
    const hour = now.getHours();
    let timeOfDay = 'night';
    if (hour >= 5 && hour < 12) {
      timeOfDay = 'morning';
    } else if (hour >= 12 && hour < 17) {
      timeOfDay = 'afternoon';
    } else if (hour >= 17 && hour < 21) {
      timeOfDay = 'evening';
    }
    
    return `${day} ${timeOfDay} picks`;
  };

  const handleBannerClick = (cardId: string) => {
    if (cardId === 'alte-soul') {
      handleFilterChange('Alte');
    } else if (cardId === 'city-of-gods') {
      handleFilterChange('Amapiano');
    } else if (cardId === 'work-of-art') {
      handleFilterChange('Afrobeats');
    } else if (cardId === 'midnight') {
      handleFilterChange('All');
    }
  };

  return (
    <div>
      <div className={`scroll-area no-scrollbar${activeSong ? ' has-player' : ''}`}>
        {/* Header */}
        <div className="phead">
          <div>
            <div className="phead-eyebrow">{getDynamicEyebrow()}</div>
            <div className="phead-title">For You</div>
          </div>
        </div>

        {/* Genre pill rail */}
        <div className="pill-rail-container">
          <div className="pill-rail no-scrollbar" role="radiogroup" aria-label="Genre filter rail">
            {GENRE_FILTERS.map(g => (
              <span
                key={g}
                className={`pill${activeFilter === g ? ' on' : ''}`}
                onClick={() => handleFilterChange(g)}
                role="radio"
                aria-pressed={activeFilter === g}
                tabIndex={0}
              >
                {g}
              </span>
            ))}
          </div>
          <div className="pill-rail-fade" />
        </div>

        {/* Banner rail */}
        <div className="banner-rail no-scrollbar">
          {BANNER_CARDS.map(card => (
            <div key={card.id} className="banner-card" style={{ background: card.bg }} onClick={() => handleBannerClick(card.id)}>
              {card.hasAccentOverlay && (
                <div className="banner-accent-overlay" />
              )}
              {card.emoji && <div style={card.emojiStyle as React.CSSProperties}>{card.emoji}</div>}
              <div className="banner-overlay" style={card.overlayStyle as React.CSSProperties}>
                <div
                  className="banner-title"
                  style={card.textColor ? { color: card.textColor, textShadow: card.textShadow, fontSize: 22, lineHeight: 1.05 } : undefined}
                >
                  {card.title.split('\n').map((line, i, arr) => (
                    <span key={i}>{line}{i < arr.length - 1 && <br />}</span>
                  ))}
                </div>
                <div
                  className="banner-sub"
                  style={card.textColor ? { color: 'rgba(0,0,0,.6)' } : undefined}
                >
                  {card.sub}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Popular Today */}
        <div className="sec-row">
          <div className="sec-title">Popular Today</div>
          <div className="sec-link" onClick={() => fetchPopularSongs(activeFilter)}>Refresh</div>
        </div>
        {loadingPopular ? (
          <div className="grid2">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="grid-card skeleton">
                <div className="grid-art skeleton-art"></div>
                <div className="skeleton-line title"></div>
                <div className="skeleton-line artist"></div>
              </div>
            ))}
          </div>
        ) : popularSongs.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📭</div>
            <div className="empty-state-text">Nothing here yet</div>
          </div>
        ) : (
          <div className="grid2">
            {popularSongs.slice(0, 4).map(song => (
              <div key={song.id} className="grid-card" onClick={() => openDrawer({
                title: song.title,
                artist: song.artist,
                genre: song.genre,
                reason: `This song is popular with listeners on PLUGD.`,
                factors: [
                  { emoji: '🔥', label: 'Trending', value: 'High popularity', boost: `+${song.matchPct}%` }
                ],
                matchPct: song.matchPct
              })}>
                <div className="grid-art" style={{ background: song.bg }}>
                  {song.imgUrl ? (
                    <img src={song.imgUrl} alt={song.title} loading="lazy" />
                  ) : (
                    <span>{song.emoji}</span>
                  )}
                  <button className="grid-play" aria-label={`Play ${song.title}`} onClick={e => { e.stopPropagation(); playSong(song); }}>
                    <svg viewBox="0 0 24 24" fill="#111" stroke="none">
                      <polygon points="5 3 19 12 5 21 5 3" />
                    </svg>
                  </button>
                </div>
                <div className="grid-song-title">{song.title}</div>
                <div className="grid-song-artist">{song.artist}</div>
              </div>
            ))}
          </div>
        )}

        {/* Recommended */}
        <div className="sec-row">
          <div className="sec-title">Recommended</div>
          <div className="sec-link" onClick={() => fetchRecommendations()}>Refresh</div>
        </div>
        {loadingRecs ? (
          <div>
            {[1, 2, 3].map(i => (
              <div key={i} className="song-row skeleton" style={{ display: 'flex', alignItems: 'center', padding: '12px 20px' }}>
                <div className="song-row-art skeleton-art" style={{ width: '48px', height: '48px', borderRadius: '8px' }}></div>
                <div className="song-row-info" style={{ flex: 1, marginLeft: '12px' }}>
                  <div className="skeleton-line title" style={{ width: '60%', height: '14px', marginTop: 0 }}></div>
                  <div className="skeleton-line artist" style={{ width: '40%', height: '12px', marginTop: '6px' }}></div>
                </div>
                <div className="skeleton-line pct" style={{ width: '30px', height: '14px', marginLeft: 'auto' }}></div>
              </div>
            ))}
          </div>
        ) : recommendedSongs.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📭</div>
            <div className="empty-state-text">Nothing here yet</div>
          </div>
        ) : (
          recommendedSongs.map(song => (
            <div key={song.id} className="song-row" onClick={() => song.recommendationId ? openDrawerForRecommendation(song.recommendationId, song) : openDrawer()}>
              <div className="song-row-art" style={{ background: song.bg }}>
                {song.imgUrl ? (
                  <img src={song.imgUrl} alt={song.title} loading="lazy" />
                ) : (
                  song.emoji
                )}
              </div>
              <div className="song-row-info">
                <div className="song-row-title">{song.title}</div>
                <div className="song-row-artist">{song.artist} · {song.genre}</div>
              </div>
              <div className="conf-mini-wrap">
                <div className="conf-mini-pct">{song.matchPct}% match</div>
                <div className="conf-mini-bar">
                  <div className="conf-mini-fill" style={{ width: `${song.matchPct}%` }} />
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <BottomNav active="home" />
    </div>
  );
}
