import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './components/Home';
import Profile from './components/Profile';
const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/player/:gameName/:tagLine" element={<Profile />} />
        <Route path="/" element={<Home />} />
      </Routes>
    </Router>
  );
};

export default App;