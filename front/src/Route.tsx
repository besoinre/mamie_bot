import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import App from "./App";
import TermsAndConditions from "./components/TermsAndConditions/TermsAndConditions";
import PrivacyPolicy from "./components/PrivacyPolicy/PrivacyPolicy";
import RedirectToRiotTxt from "./components/RedirectRiotFile/RedirectRiotFile";
import { useEffect } from "react";

const AppRoutes = () => {

  useEffect(() => {
    const handleHash = () => {
      const hash = window.location.hash;
      if (hash === '#eventsList/riot.txt') {
        window.location.replace('/riot.txt');
      }
    };

    // Run once on mount
    handleHash();

    // Also listen for hash changes
    window.addEventListener('hashchange', handleHash);

    return () => {
      window.removeEventListener('hashchange', handleHash);
    };
  }, []);
  return (
    <Router>
        <Routes>
          <Route path="/" element={<App />} /> 
          <Route path="/terms-and-conditions" element={<TermsAndConditions />} /> 
          <Route path="/privacy-policy" element={<PrivacyPolicy />} /> 
          <Route path="/eventsList/riot.txt" element={<RedirectToRiotTxt/>} />
        </Routes>
    </Router>
  );
};

export default AppRoutes;
