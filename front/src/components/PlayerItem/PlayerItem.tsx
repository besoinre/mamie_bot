import useDeletePlayer from '../../hooks/useDeletePlayer';
import './PlayerItem.scss';

interface PlayerItemProps {
  _id: string;
  playerName: string;
  puuid: string;
}

const PlayerItem: React.FC<PlayerItemProps> = ({ _id, playerName, puuid }) => {
  const { deletePlayer, loading, error, success } = useDeletePlayer();

  const handleDelete = async (playerId: string) => {
    await deletePlayer(playerId);
  };

  return (
    <li key={_id} className="player-item">
      <span className="player-name">{playerName}</span>
      <span className="player-puuid">{puuid}</span>
      <button 
        className="delete-button" 
        onClick={() => handleDelete(_id)} 
        disabled={loading} 
      >
        Delete
      </button>
    </li>
  );
};

export default PlayerItem;
