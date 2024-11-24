import './FooterDisclaimer.scss';      
import { Link } from "react-router-dom";

const FooterDisclaimer = () => {
  return (
    <footer className="footer-disclaimer">
      <p>
        Mamie Bot isn&apos;t endorsed by Riot Games and doesn&apos;t reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.
      </p>
      <div className='footer-buttons'>
        <Link to="/terms-and-conditions">Terms and Conditions</Link>
        <Link to="/privacy-policy">Privacy Policy</Link>
      </div>
    </footer>
  );
};

export default FooterDisclaimer;