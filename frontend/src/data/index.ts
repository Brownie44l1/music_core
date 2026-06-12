import type { Song, BannerCard, GenreTile, StatCard, GenreBar, DrawerSong } from '../types';

export const BANNER_CARDS: BannerCard[] = [
  {
    id: 'work-of-art',
    title: 'WORK OF ART',
    sub: 'Asake · Afrobeats',
    bg: '#292524',
    emoji: '🎨',
    emojiStyle: { position: 'absolute', top: 10, right: 12, fontSize: '3.5rem', opacity: 0.25 },
    overlayStyle: { background: 'none', flexDirection: 'column', justifyContent: 'flex-end' }
  },
  {
    id: 'city-of-gods',
    title: 'CITY OF\nGODS',
    sub: 'Burna Boy · 8 songs',
    bg: '#1c1917',
    emoji: '🏙️',
    emojiStyle: { position: 'absolute', top: -10, right: -10, fontSize: '5rem', opacity: 0.2, transform: 'rotate(15deg)' },
    overlayStyle: { background: 'none', padding: 14, flexDirection: 'column', justifyContent: 'flex-end', alignItems: 'flex-start' }
  },
  {
    id: 'alte-soul',
    title: 'ALTE SOUL',
    sub: 'Lady Donli, Cruel Santino',
    bg: '#1c1917',
    emoji: '🎸',
    emojiStyle: { position: 'absolute', top: 10, right: 14, fontSize: '3rem', opacity: 0.25 },
    overlayStyle: { background: 'none', flexDirection: 'column', justifyContent: 'flex-end' }
  },
  {
    id: 'midnight',
    title: 'MIDNIGHT\nPLAYLIST',
    sub: 'Late night · 12 songs',
    bg: '#0c0a09',
    overlayStyle: { background: 'none', flexDirection: 'column', justifyContent: 'flex-end' }
  },
];

export const GENRE_FILTERS = ['All', 'Afrobeats', 'Amapiano', 'Alte', 'Afro-fusion', 'Street-hop'];

export const GRID_SONGS: Song[] = [
  { id: 'gs1', title: 'Lonely At The Top', artist: 'Asake', genre: 'Afrobeats', emoji: '🎵', bg: '#292524', matchPct: 94 },
  { id: 'gs2', title: 'Calm Down', artist: 'Rema', genre: 'Afrobeats', emoji: '🎶', bg: '#292524', matchPct: 88 },
  { id: 'gs3', title: 'Essence', artist: 'Wizkid', genre: 'Afro-fusion', emoji: '🎤', bg: '#292524', matchPct: 91 },
  { id: 'gs4', title: 'Terminator', artist: 'Burna Boy', genre: 'Afrobeats', emoji: '🥁', bg: '#292524', matchPct: 83 },
];

export const LIST_SONGS: Song[] = [
  { id: 'ls1', title: 'Lonely At The Top', artist: 'Asake', genre: 'Afrobeats', emoji: '🎵', bg: '#292524', matchPct: 94 },
  { id: 'ls2', title: 'Ke Star (Remix)', artist: 'Focalistic', genre: 'Amapiano', emoji: '🎧', bg: '#292524', matchPct: 87 },
  { id: 'ls3', title: 'Bad Vibes Forever', artist: 'Lady Donli', genre: 'Alte', emoji: '🎤', bg: '#292524', matchPct: 78 },
  { id: 'ls4', title: 'Essence', artist: 'Wizkid', genre: 'Afro-fusion', emoji: '🎙️', bg: '#292524', matchPct: 91 },
  { id: 'ls5', title: 'Terminator', artist: 'Burna Boy', genre: 'Afrobeats', emoji: '🥁', bg: '#292524', matchPct: 83 },
];

export const GENRE_TILES: GenreTile[] = [
  { id: 'afrobeats', name: 'Afrobeats', count: '1,240 songs', emoji: '🥁', bg: '#F5F500' },
  { id: 'amapiano', name: 'Amapiano', count: '830 songs', emoji: '🎹', bg: '#E8F5E8' },
  { id: 'alte', name: 'Alte', count: '415 songs', emoji: '🎸', bg: '#F0E8FF' },
  { id: 'afrofusion', name: 'Afro-fusion', count: '620 songs', emoji: '✨', bg: '#FFF3E0' },
  { id: 'naijarb', name: 'Naija R&B', count: '370 songs', emoji: '🎙️', bg: '#E0F4FF' },
  { id: 'streethop', name: 'Street-hop', count: '290 songs', emoji: '🎤', bg: '#FFE8EC' },
  { id: 'highlife', name: 'Highlife', count: '155 songs', emoji: '🪘', bg: '#ECFFE8' },
  { id: 'fujifusion', name: 'Fuji-fusion', count: '88 songs', emoji: '🎺', bg: '#FFF8E0' },
];

export const STAT_CARDS: StatCard[] = [
  { eyebrow: 'Top genre', value: 'Afrobeats', sub: '68% of picks' },
  { eyebrow: 'Avg match', value: '89%', sub: 'Last 30 recs' },
  { eyebrow: 'Songs liked', value: '47', sub: 'This month' },
  { eyebrow: 'Avg BPM', value: '119', sub: 'Afrobeats pace' },
  { eyebrow: 'Energy level', value: 'High (0.82)', sub: 'Vibe profile' },
  { eyebrow: 'BPM range', value: '112–128 BPM', sub: 'Peak range' },
  { eyebrow: 'Listen time', value: '10pm–2am', sub: 'Peak late night' },
];

export const GENRE_BARS: GenreBar[] = [
  { name: 'Afrobeats', pct: 68 },
  { name: 'Amapiano', pct: 18 },
  { name: 'Alte', pct: 9 },
  { name: 'Other', pct: 5 },
];

export const TOP_ARTISTS = [
  { emoji: '🎤', name: 'Asake' },
  { emoji: '🎧', name: 'Burna Boy' },
  { emoji: '🎵', name: 'Tems' },
  { emoji: '🎼', name: 'Rema' },
  { emoji: '🎙️', name: 'Wizkid' },
];

export const DRAWER_SONG: DrawerSong = {
  title: 'Lonely At The Top',
  artist: 'Asake',
  genre: 'Afrobeats',
  reason: 'You consistently pick Afrobeats at 115–125 BPM. This track sits at exactly 120 BPM and shares a percussive triplet groove with 3 songs you\'ve liked this week.',
  factors: [
    { emoji: '🎤', label: 'Vocal style', value: 'Similar to Asake, Seun Kuti', boost: '+31%' },
    { emoji: '🥁', label: 'Rhythm pattern', value: 'Afrobeats triplet groove', boost: '+28%' },
    { emoji: '🌙', label: 'Time of day match', value: 'You listen late — this tracks', boost: '+18%' },
    { emoji: '📈', label: 'Trending in Lagos', value: 'Top 10 this week', boost: '+17%' },
  ],
  matchPct: 94,
};

export const OB_GENRES = ['Afrobeats', 'Amapiano', 'Alte', 'Afro-pop', 'Street-hop', 'Naija R&B', 'Afro-fusion', 'Highlife', 'Afro-drill', 'Fuji-fusion'];

export const OB_ARTISTS = ['Asake', 'Burna Boy', 'Wizkid', 'Tems', 'Davido', 'Rema', 'Ayra Starr', 'Omah Lay'];

export const OB_MOODS = [
  { emoji: '🔥', name: 'Turn Up', desc: 'High energy bangers' },
  { emoji: '🌙', name: 'Late Night', desc: 'Smooth & lowkey' },
  { emoji: '😤', name: 'Grind Mode', desc: 'Focus & motivation' },
  { emoji: '💃', name: 'Dance Floor', desc: "Can't sit still" },
];

export const MARQUEE_TAGS = ['Afrobeats', 'Amapiano', 'Alte', 'Afro-fusion', 'Street-hop', 'Naija R&B', 'Highlife'];
