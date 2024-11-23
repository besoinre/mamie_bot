import { useState } from 'react';
import axios from 'axios';

const useCreatePlayer = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const createPlayer = async (playerName: string, puuid: string) => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await axios.post('http://127.0.0.1:5000/players', {
        playerName,
        puuid,
      });
      if (response.status === 201) {
        setSuccess(true);
      } else {
        setError('Failed to create player');
      }
    } catch (err) {
      console.log(err)
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return { createPlayer, loading, error, success };
};

export default useCreatePlayer;
