import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { Screen, Song, DrawerSong } from '../types';
import { DRAWER_SONG } from '../data';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api';

async function apiFetch(url: string, options: RequestInit = {}) {
  const headers = new Headers(options.headers || {});
  headers.append('ngrok-skip-browser-warning', 'true');
  return fetch(url, { ...options, headers });
}

// Helper to generate or retrieve a stable, random session ID
function getOrCreateSessionId(): string {
  let sid = localStorage.getItem('plugd_session_id');
  if (!sid) {
    sid = 'sess_' + Math.random().toString(36).substring(2, 15);
    localStorage.setItem('plugd_session_id', sid);
  }
  return sid;
}

// Helper to map genre to visual background and emoji (visually matching solid colors)
export function getGenreVisuals(genre: string) {
  const g = genre.toLowerCase();
  let emoji = '🎧';
  let bg = '#292524';
  
  if (g.includes('afrobeat')) {
    emoji = '🔥';
    bg = '#e65c00';
  } else if (g.includes('amapiano')) {
    emoji = '⚡';
    bg = '#006622';
  } else if (g.includes('alte')) {
    emoji = '🎨';
    bg = '#990099';
  } else if (g.includes('fusion') || g.includes('pop')) {
    emoji = '🌟';
    bg = '#005c99';
  } else if (g.includes('r&b') || g.includes('soul')) {
    emoji = '🍿';
    bg = '#cc0000';
  } else if (g.includes('street')) {
    emoji = '👑';
    bg = '#4d2600';
  }
  return { emoji, bg };
}

interface AppContextType {
  screen: Screen;
  go: (s: Screen) => void;
  drawerOpen: boolean;
  drawerSong: DrawerSong;
  drawerSongObj: Song | null;
  openDrawer: (song?: DrawerSong, songObj?: Song) => void;
  openDrawerForRecommendation: (recommendationId: string, songObj: Song) => Promise<void>;
  closeDrawer: () => void;
  activeSong: Song | null;
  isPlaying: boolean;
  playSong: (song: Song) => void;
  togglePlay: () => void;
  
  // API States & Actions
  sessionId: string;
  recommendedSongs: Song[];
  popularSongs: Song[];
  loadingRecs: boolean;
  loadingPopular: boolean;
  fetchRecommendations: () => Promise<void>;
  fetchPopularSongs: (genre?: string) => Promise<void>;
  submitFeedback: (songId: string, feedbackType: 'like' | 'dislike' | 'skip') => Promise<void>;
  completeOnboarding: (genres: Set<string>, artist: string) => Promise<void>;

  // Audio Playback progress
  audioCurrentTime: number;
  audioDuration: number;

  likedSongs: Set<string>;
  toggleLikeSong: (songId: string) => void;
}

const AppContext = createContext<AppContextType | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [screen, setScreen] = useState<Screen>('landing');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerSong, setDrawerSong] = useState<DrawerSong>(DRAWER_SONG);
  const [drawerSongObj, setDrawerSongObj] = useState<Song | null>(null);
  const [activeSong, setActiveSong] = useState<Song | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  // API Integration States
  const [sessionId] = useState<string>(getOrCreateSessionId);
  const [recommendedSongs, setRecommendedSongs] = useState<Song[]>([]);
  const [popularSongs, setPopularSongs] = useState<Song[]>([]);
  const [loadingRecs, setLoadingRecs] = useState(false);
  const [loadingPopular, setLoadingPopular] = useState(false);

  // Debouncing to ensure rate-limiting safety (idempotent buttons)
  const [submittingFeedback, setSubmittingFeedback] = useState<Record<string, boolean>>({});

  const [likedSongs, setLikedSongs] = useState<Set<string>>(new Set());

  const toggleLikeSong = (songId: string) => {
    setLikedSongs(prev => {
      const next = new Set(prev);
      if (next.has(songId)) {
        next.delete(songId);
      } else {
        next.add(songId);
      }
      return next;
    });
  };

  // HTML5 Audio Element State
  const [audio] = useState(() => new Audio());
  const [audioCurrentTime, setAudioCurrentTime] = useState(0);
  const [audioDuration, setAudioDuration] = useState(0);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationTime, setSimulationTime] = useState(0);

  const go = (s: Screen) => {
    setScreen(s);
    window.scrollTo(0, 0);
  };

  const openDrawer = (song?: DrawerSong, songObj?: Song) => {
    if (song) setDrawerSong(song);
    if (songObj) setDrawerSongObj(songObj);
    else if (song) {
      setDrawerSongObj({
        id: 'drawer-fake',
        title: song.title,
        artist: song.artist,
        genre: song.genre,
        emoji: '🎵',
        bg: 'linear-gradient(135deg,#1c1917,#0c0a09)',
        matchPct: song.matchPct
      });
    }
    setDrawerOpen(true);
  };

  const openDrawerForRecommendation = async (recommendationId: string, songObj: Song) => {
    setDrawerSongObj(songObj);
    try {
      const res = await apiFetch(`${API_BASE}/explain?recommendation_id=${recommendationId}`);
      if (!res.ok) throw new Error('Failed to fetch explanation');
      const data = await res.json();
      
      const explainData = data.explanation;
      const confidencePct = Math.round(explainData.confidence * 100);
      
      const mappedDrawerSong: DrawerSong = {
        title: data.title,
        artist: data.artist,
        genre: explainData.matched_features.genre || songObj.genre,
        reason: `Your top-matched genre is ${explainData.matched_features.genre}. This track matches your taste profile: tempo is ${explainData.matched_features.tempo || 'Medium'} and energy is ${Math.round(explainData.matched_features.energy_level * 100)}%.`,
        factors: [
          { emoji: '🥁', label: 'Tempo Match', value: explainData.matched_features.tempo || 'Medium', boost: `+${Math.round(explainData.confidence * 30)}%` },
          { emoji: '⚡', label: 'Energy Match', value: `${Math.round(explainData.matched_features.energy_level * 100)}%`, boost: `+${Math.round(explainData.confidence * 25)}%` },
          { emoji: '👥', label: 'Taste Similarities', value: `${explainData.similar_users.length} similar listeners`, boost: `+18%` }
        ],
        matchPct: confidencePct || songObj.matchPct
      };
      
      setDrawerSong(mappedDrawerSong);
      setDrawerOpen(true);
    } catch (err) {
      console.error(err);
      // Fallback
      setDrawerSong({
        title: songObj.title,
        artist: songObj.artist,
        genre: songObj.genre,
        reason: `Recommended based on your recent activity with a ${songObj.matchPct}% match score.`,
        factors: [
          { emoji: '🎵', label: 'Genre Match', value: songObj.genre, boost: `+25%` },
          { emoji: '📈', label: 'Popularity Boost', value: 'High affinity', boost: `+15%` }
        ],
        matchPct: songObj.matchPct
      });
      setDrawerOpen(true);
    }
  };

  const closeDrawer = () => setDrawerOpen(false);

  const playSong = (song: Song) => {
    setActiveSong(song);
    setIsPlaying(true);
  };

  const togglePlay = () => {
    setIsPlaying(prev => !prev);
  };

  const fetchRecommendations = async () => {
    setLoadingRecs(true);
    try {
      const res = await apiFetch(`${API_BASE}/recommendations?session_id=${sessionId}&limit=6`);
      if (!res.ok) throw new Error('Failed to fetch recommendations');
      const data = await res.json();
      
      const mapped = data.recommendations.map((r: any) => {
        const visuals = getGenreVisuals(r.genre);
        return {
          id: r.song_id, // e.g. "ng_..."
          recommendationId: r.recommendation_id,
          title: r.title,
          artist: r.artist,
          genre: r.genre,
          emoji: visuals.emoji,
          bg: visuals.bg,
          matchPct: Math.round(r.score * 100),
          imgUrl: r.album_art_url,
          previewUrl: r.preview_url
        };
      });
      setRecommendedSongs(mapped);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingRecs(false);
    }
  };

  const fetchPopularSongs = async (genre?: string) => {
    setLoadingPopular(true);
    try {
      const genreParam = genre && genre !== 'All' ? `?genre=${encodeURIComponent(genre)}` : '';
      const res = await apiFetch(`${API_BASE}/songs${genreParam}`);
      if (!res.ok) throw new Error('Failed to fetch songs');
      const data = await res.json();
      
      const mapped = data.songs.map((s: any) => {
        const visuals = getGenreVisuals(s.genre);
        return {
          id: s.id,
          title: s.title,
          artist: s.artist,
          genre: s.genre,
          emoji: visuals.emoji,
          bg: visuals.bg,
          matchPct: Math.round(s.popularity_score * 100),
          imgUrl: s.album_art_url,
          previewUrl: s.preview_url
        };
      });
      setPopularSongs(mapped);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingPopular(false);
    }
  };

  const submitFeedback = async (songId: string, feedbackType: 'like' | 'dislike' | 'skip') => {
    const key = `${songId}-${feedbackType}`;
    if (submittingFeedback[key]) return; // Deduplicate ongoing identical request

    setSubmittingFeedback(prev => ({ ...prev, [key]: true }));
    try {
      const res = await apiFetch(`${API_BASE}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          song_id: songId,
          feedback_type: feedbackType
        })
      });
      if (!res.ok) throw new Error('Failed to submit feedback');
      
      // Refresh recommendations since the user profile changed and cache is invalidated
      await fetchRecommendations();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmittingFeedback(prev => ({ ...prev, [key]: false }));
    }
  };

  const completeOnboarding = async (genres: Set<string>, artist: string) => {
    try {
      // Find up to 50 popular songs first
      const res = await apiFetch(`${API_BASE}/songs?page_size=50`);
      if (res.ok) {
        const data = await res.json();
        const candidateSongs = data.songs;
        
        // Find matching songs based on selected artist and genres
        const matches = candidateSongs.filter((s: any) => 
          (artist && s.artist.toLowerCase().includes(artist.toLowerCase())) || 
          genres.has(s.genre)
        ).slice(0, 5);

        // Submit "like" feedback for these matches
        for (const s of matches) {
          await apiFetch(`${API_BASE}/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              session_id: sessionId,
              song_id: s.id,
              feedback_type: 'like'
            })
          });
        }
      }
    } catch (err) {
      console.error('Failed to seed onboarding preferences:', err);
    }
    
    // Refresh recommendations to reflect the likes immediately
    await fetchRecommendations();
    go('home');
  };

  // Sync Audio playback
  useEffect(() => {
    if (!activeSong || !activeSong.previewUrl) {
      audio.pause();
      setIsSimulating(false);
      setSimulationTime(0);
      return;
    }

    if (audio.src !== activeSong.previewUrl) {
      audio.src = activeSong.previewUrl;
      audio.load();
      setIsSimulating(false);
      setSimulationTime(0);
    }

    if (isPlaying) {
      audio.play().then(() => {
        setIsSimulating(false);
      }).catch(err => {
        console.warn("Audio playback failed (possible CORS or expired CDN). Falling back to simulation.", err);
        setIsSimulating(true);
      });
    } else {
      audio.pause();
    }
  }, [activeSong, isPlaying, audio]);

  // Simulation timer for progress bar and waveform
  useEffect(() => {
    let interval: any = null;
    if (isPlaying && isSimulating) {
      interval = setInterval(() => {
        setSimulationTime(prev => {
          if (prev >= 30) {
            setIsPlaying(false);
            setIsSimulating(false);
            return 0;
          }
          return prev + 0.1;
        });
      }, 100);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPlaying, isSimulating]);

  // Web Audio API Synthesizer loop to generate audible chords when Deezer preview streams fail
  useEffect(() => {
    let audioCtx: AudioContext | null = null;
    let timer: any = null;

    if (isPlaying && isSimulating) {
      try {
        const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
        audioCtx = new AudioContextClass();
        
        // Melodic chord progression in F major key
        const notes = [
          [349.23, 440.00, 523.25], // F Maj
          [349.23, 440.00, 523.25], // F Maj
          [392.00, 493.88, 587.33], // G Maj
          [261.63, 329.63, 392.00], // C Maj
        ];
        let step = 0;

        timer = setInterval(() => {
          if (!audioCtx) return;
          if (audioCtx.state === 'suspended') {
            audioCtx.resume();
          }

          const now = audioCtx.currentTime;
          const chord = notes[step % notes.length];
          
          chord.forEach(freq => {
            const osc = audioCtx!.createOscillator();
            const gainNode = audioCtx!.createGain();
            
            osc.type = 'triangle'; // Smooth electric piano-like tone
            osc.frequency.value = freq;
            
            gainNode.gain.setValueAtTime(0.06, now);
            gainNode.gain.exponentialRampToValueAtTime(0.0001, now + 0.5);
            
            osc.connect(gainNode);
            gainNode.connect(audioCtx!.destination);
            
            osc.start(now);
            osc.stop(now + 0.5);
          });
          
          step++;
        }, 600); // 100 BPM rhythmic pulse
      } catch (err) {
        console.warn("Web Audio API not supported or blocked:", err);
      }
    }

    return () => {
      if (timer) clearInterval(timer);
      if (audioCtx) {
        audioCtx.close();
      }
    };
  }, [isPlaying, isSimulating]);

  // Audio events for duration and progress tracking
  useEffect(() => {
    const handleTimeUpdate = () => setAudioCurrentTime(audio.currentTime);
    const handleDurationChange = () => setAudioDuration(audio.duration || 0);
    const handleEnded = () => setIsPlaying(false);

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('durationchange', handleDurationChange);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('durationchange', handleDurationChange);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [audio]);

  // Fetch initial popular songs and recommendations on mount
  useEffect(() => {
    fetchPopularSongs();
    fetchRecommendations();
  }, []);

  return (
    <AppContext.Provider value={{
      screen,
      go,
      drawerOpen,
      drawerSong,
      drawerSongObj,
      openDrawer,
      openDrawerForRecommendation,
      closeDrawer,
      activeSong,
      isPlaying,
      playSong,
      togglePlay,
      sessionId,
      recommendedSongs,
      popularSongs,
      loadingRecs,
      loadingPopular,
      fetchRecommendations,
      fetchPopularSongs,
      submitFeedback,
      completeOnboarding,
      audioCurrentTime: isSimulating ? simulationTime : audioCurrentTime,
      audioDuration: isSimulating || audioDuration === 0 ? 30 : audioDuration,
      likedSongs,
      toggleLikeSong
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}


