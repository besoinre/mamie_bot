import { useState } from "react";
import PlayerForm from "../PlayerForm/PlayerForm";
import PlayerList from "../PlayerList/PlayerList";

const PlayerSection = () => {
  const [refresh, setRefresh] = useState(false);

  const handlePlayerAdded = () => {
    setRefresh(!refresh); 
  };

  return (
    <>
      <PlayerForm onPlayerAdded={handlePlayerAdded} />
      <PlayerList key={refresh.toString()} /> 
    </>
  );
};

export default PlayerSection;
