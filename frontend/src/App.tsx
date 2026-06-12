import { AppProvider, useApp } from './utils/AppContext';
import ExplanationDrawer from './components/ExplanationDrawer';
import MiniPlayer from './components/MiniPlayer';
import Landing from './pages/Landing';
import Onboarding from './pages/Onboarding';
import Home from './pages/Home';
import Insights from './pages/Insights';

function AppInner() {
  const { screen } = useApp();
  const showPlayer = screen !== 'landing' && screen !== 'onboarding';

  return (
    <div id="app-root">
      {screen === 'landing' && <Landing />}
      {screen === 'onboarding' && <Onboarding />}
      {screen === 'home' && <Home />}
      {screen === 'insights' && <Insights />}
      <ExplanationDrawer />
      {showPlayer && <MiniPlayer />}
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <AppInner />
    </AppProvider>
  );
}
