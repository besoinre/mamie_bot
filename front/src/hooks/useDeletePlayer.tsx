import { useState } from 'react';
import axios from 'axios';

const useDeletePlayer = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const apiUrl = process.env.REACT_APP_API_URL;

  const deletePlayer = async (playerId: string) => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      const response = await axios.delete(apiUrl+`players/${playerId}`);

      if (response.status === 200) {
        setSuccess(true);
      } else {
        setError('Failed to delete player');
      }
    } catch (err) {
      setError('An error occurred while deleting the player');
    } finally {
      setLoading(false);
    }
  };

  return { deletePlayer, loading, error, success };
};

export default useDeletePlayer;
