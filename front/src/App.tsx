import React, { useState } from 'react';
import './App.scss';
import Header from './components/Header/Header';
import SearchBar from './components/SearchBar/SearchBar';
import Section from './components/Section/Section';
import NavBar from './components/NavBar/NavBar';
import LiveEventsList from './components/LiveEventsList/LiveEventsList';
import PlayerSection from './components/PlayerSection/PlayerSection';
import FooterDisclaimer from './components/FooterDisclaimer/FooterDisclaimer';

const App: React.FC = () => {
  
  const [playerName, setPlayerName] = useState<string>(''); 

  const handleSearch = (name: string) => {
    setPlayerName(name); 
  };
  
  return (
    <div className="App">
      <NavBar></NavBar>
      <Section id="home" className='section-one'>
        <Header />
      </Section>
      {/* <Section id="search" className='section-two'>
        <PlayerSection/>
      </Section> */}
      <Section id="eventsList" className='section-three'>
        <SearchBar onSearch={handleSearch} />
        <LiveEventsList playerName={playerName} />
      </Section>
      <FooterDisclaimer />
    </div>
  );
};

export default App;
