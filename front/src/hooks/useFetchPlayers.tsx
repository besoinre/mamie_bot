import { useState, useEffect } from 'react';
import axios from 'axios';

const useFetchPlayers = () => {
  const [players, setPlayers] = useState<any[]>([]); 
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null); 
  const apiUrl = process.env.REACT_APP_API_URL;

  useEffect(() => {
    const fetchPlayers = async () => {
      setLoading(true); 
      setError(null); 
      try {
        const response = await axios.get(apiUrl+'players'); 
        if (response.status === 200) {
          setPlayers(response.data); 
        } else {
          setError('Failed to fetch players');
        }
      } catch (err) {
        setError('An error occurred while fetching players');
      } finally {
        setLoading(false); 
      }
    };

    fetchPlayers(); 

  }, []);

  return { players, loading, error };
};

export default useFetchPlayers;
