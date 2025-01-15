import { useEffect } from 'react';
import axios from 'axios';

const useKeepAlive = () => {
  const apiUrl = process.env.REACT_APP_API_URL;
  const pingInterval = 10 * 60 * 1000;

  useEffect(() => {

    const pingBackend = async () => {
      try {
        const response = await axios.get(apiUrl+'keep-alive'); 
        if (response.status === 200) {
          console.log("Backend is awake!");
        } else {
          console.error("Failed to ping the backend.");
        }
      } catch (err) {
        console.error("Failed to ping the backend.");
      } 
    };
    const interval = setInterval(pingBackend, pingInterval);
    return () => clearInterval(interval);
  }, []);
};

export default useKeepAlive;
