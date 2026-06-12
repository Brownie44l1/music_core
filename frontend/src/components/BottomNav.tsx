import { useApp } from '../utils/AppContext';
import type { Screen } from '../types';

const NAV_ITEMS: { label: string; screen: Screen; icon: string }[] = [
  {
    label: 'Home',
    screen: 'home',
    icon: 'home'
  },
  {
    label: 'My Taste',
    screen: 'insights',
    icon: 'queue_music'
  }
];

export default function BottomNav({ active }: { active: Screen }) {
  const { go } = useApp();

  return (
    <nav className="bottom-nav">
      <div className="bottom-nav-inner">
        {NAV_ITEMS.map((item) => {
          const isOn = item.screen === active;
          return (
            <button
              key={item.label}
              className={`bottom-nav-btn ${isOn ? 'active' : ''}`}
              onClick={() => go(item.screen)}
            >
              <span 
                className="material-symbols-outlined nav-icon" 
                style={isOn ? { fontVariationSettings: '"FILL" 1' } : undefined}
              >
                {item.icon}
              </span>
              <span className="nav-label">{item.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
