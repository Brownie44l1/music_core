export type Screen = 'landing' | 'onboarding' | 'home' | 'insights';

export interface Song {
  id: string;
  title: string;
  artist: string;
  genre: string;
  emoji: string;
  bg: string;
  matchPct: number;
  imgUrl?: string;
  recommendationId?: string;
  previewUrl?: string;
}

export interface BannerCard {
  id: string;
  title: string;
  sub: string;
  bg: string;
  emoji?: string;
  emojiStyle?: React.CSSProperties;
  textColor?: string;
  textShadow?: string;
  hasAccentOverlay?: boolean;
  overlayStyle?: React.CSSProperties;
}

export interface GenreTile {
  id: string;
  name: string;
  count: string;
  emoji: string;
  bg: string;
}

export interface StatCard {
  eyebrow: string;
  value: string;
  sub: string;
}

export interface GenreBar {
  name: string;
  pct: number;
}

export interface Insight {
  emoji: string;
  label: string;
  value: string;
}

export interface DrawerSong {
  title: string;
  artist: string;
  genre: string;
  reason: string;
  factors: { emoji: string; label: string; value: string; boost: string }[];
  matchPct: number;
}
