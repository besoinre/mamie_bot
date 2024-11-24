import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import App from "./App";
import TermsAndConditions from "./components/TermsAndConditions/TermsAndConditions";
import PrivacyPolicy from "./components/PrivacyPolicy/PrivacyPolicy";

const AppRoutes = () => {
  return (
    <Router>
        <Routes>
          <Route path="/" element={<App />} /> 
          <Route path="/terms-and-conditions" element={<TermsAndConditions />} /> 
          <Route path="/privacy-policy" element={<PrivacyPolicy />} /> 
        </Routes>
    </Router>
  );
};

export default AppRoutes;
