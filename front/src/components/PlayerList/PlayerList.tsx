import useFetchPlayers from "../../hooks/useFetchPlayers";
import PlayerItem from "../PlayerItem/PlayerItem";
import './PlayerList.scss';

const PlayerList = () => {
  const { players, loading, error } = useFetchPlayers();

  if (loading) {
    return <p>Loading players...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  return (
    <ul className="player-list">
      {players.map((player, index) => (
        <PlayerItem key={player._id} _id={player._id} playerName={player.playerName} puuid={player.puuid} />
      ))}
    </ul>
  );
};

export default PlayerList;
