import { useEffect } from 'react';

const RedirectToRiotTxt = () => {
  useEffect(() => {
    window.location.replace('/riot.txt');
  }, []);

  return <div>Redirecting...</div>;
}

export default RedirectToRiotTxt;
