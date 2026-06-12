import BottomNav from '../components/BottomNav';
import { STAT_CARDS, GENRE_BARS, TOP_ARTISTS } from '../data';
import { useApp } from '../utils/AppContext';

export default function Insights() {
  const { activeSong, recommendedSongs } = useApp();

  const getDynamicWeekLabel = () => {
    const now = new Date();
    const day = now.getDay();
    const diff = now.getDate() - day + (day === 0 ? -6 : 1); // Monday
    const monday = new Date(now.setDate(diff));
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `Week of ${months[monday.getMonth()]} ${monday.getDate()}`;
  };

  const getInitials = (name: string) => {
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  const getArtistColor = (name: string) => {
    const colors = [
      '#FF6B6B', '#4D96FF', '#6BCB77', '#FFD93D', '#F473B9', 
      '#9B5DE5', '#F15BB5', '#00F5D4', '#00BBF9'
    ];
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    const index = Math.abs(hash) % colors.length;
    return colors[index];
  };

  const topSong = recommendedSongs[0] || {
    title: 'Lonely At The Top',
    artist: 'Asake',
    bg: 'linear-gradient(135deg,#1a0800,#3a1500)',
    emoji: '🎵',
    matchPct: 94
  };

  return (
    <div>
      <div className={`scroll-area no-scrollbar${activeSong ? ' has-player' : ''}`}>
        <div className="phead">
          <div>
            <div className="phead-eyebrow">Your music DNA</div>
            <div className="phead-title">Insights</div>
          </div>
        </div>

        {/* Weekly summary */}
        <div className="insights-section">
          <div className="weekly-card">
            <div className="weekly-label">{getDynamicWeekLabel()}</div>
            <div className="weekly-title">Your top pick this week</div>
            <div className="weekly-song-row">
              <div className="weekly-art" style={{ background: topSong.bg }}>{topSong.emoji}</div>
              <div>
                <div className="weekly-song-title">{topSong.title}</div>
                <div className="weekly-song-artist">{topSong.artist} · {topSong.matchPct}% match</div>
              </div>
            </div>
          </div>
        </div>

        {/* Stat grid */}
        <div className="stat-grid">
          {STAT_CARDS.map(s => (
            <div key={s.eyebrow} className="stat-card">
              <div className="stat-eyebrow">{s.eyebrow}</div>
              <div className="stat-val">{s.value}</div>
              <div className="stat-sub">{s.sub}</div>
            </div>
          ))}
        </div>

        {/* Genre breakdown */}
        <div className="insights-section">
          <div className="divider divider-insights-top" />
          <div className="sec-title sec-title-standalone">Genre breakdown</div>
          <div className="bar-list">
            {GENRE_BARS.map(bar => (
              <div key={bar.name} className="bar-item">
                <div className="bar-item-head">
                  <span className="bar-item-name">{bar.name}</span>
                  <span className="bar-item-pct">{bar.pct}%</span>
                </div>
                <div className="conf-track">
                  <div className="conf-fill" style={{ width: `${bar.pct}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top artists */}
        <div className="insights-section-bottom">
          <div className="divider" />
          <div className="sec-title sec-title-standalone">Top artists this week</div>
        </div>
        <div className="artist-strip no-scrollbar">
          {TOP_ARTISTS.map(a => (
            <div key={a.name}>
              <div 
                className="artist-avatar initials-avatar" 
                style={{ 
                  background: getArtistColor(a.name), 
                  color: '#fff', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  fontWeight: 'bold', 
                  fontSize: '14px' 
                }}
              >
                {getInitials(a.name)}
              </div>
              <div className="artist-name">{a.name}</div>
            </div>
          ))}
        </div>
      </div>

      <BottomNav active="insights" />
    </div>
  );
}
