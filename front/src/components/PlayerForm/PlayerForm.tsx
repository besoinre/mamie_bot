import React, { useState } from 'react';
import './PlayerForm.scss';
import useCreatePlayer from '../../hooks/useCreatePlayer';

interface PlayerFormProps {
  onPlayerAdded: () => void;
}

const PlayerForm: React.FC<PlayerFormProps> = ({onPlayerAdded}) => {
  const { createPlayer, loading, error, success } = useCreatePlayer();
  const [playerName, setPlayerName] = useState('');
  const [puuid, setPuuid] = useState('');

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!playerName || !puuid) return;
    createPlayer(playerName, puuid);
    setPlayerName("");
    setPuuid("");
    onPlayerAdded();
  };

  return (
    <div className='player-form'>
      <h2>Add player</h2>
      <form className="add-player-form" onSubmit={handleSubmit}>
        <div className="input-group">
          <input
            id='player-name'
            type="text"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            placeholder="Player name + game tag"
          />
          <input
            id='puuid'
            type="text"
            value={puuid}
            onChange={(e) => setPuuid(e.target.value)}
            placeholder="puuid"
          />
        </div>
        <button id='submit' type="submit">Add</button>
      </form>
      {
        error && <p className='result-message error'>Failed to add the player : {error}</p>
      }
      {
        success && <p className='result-message success'>Player added successfully</p>
      }
    </div>
  );
};

export default PlayerForm; 
