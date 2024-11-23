import React, { useState } from 'react';
import './SearchBar.scss';

interface SearchBarProps {
  onSearch: (query: string) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [query, setQuery] = useState<string>('');

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSearch(query);
    document.getElementById('eventsList')?.scrollIntoView({
      behavior: 'smooth'
    });
  };

  return (
    <div className="search-bar">
      <h2>Search player</h2>
      <form className="search-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter TFT player name..."
        />
        <button type="submit">Search</button>
      </form>
    </div>
  );
};

export default SearchBar; 
