import { Link } from "react-router-dom";
import "./TermsAndConditions.scss"; 

const TermsAndConditions = () => {
  return (
    <div className="terms-and-conditions">
      <h1>Terms and Conditions</h1>
      <p><strong>Effective Date:</strong> 11/24/2024</p>

      <section>
        <h2>1. Acceptance of Terms</h2>
        <p>
          By accessing or using the Site or Services, you agree to abide by these Terms and our <Link to="/privacy-policy">Privacy Policy</Link>. These Terms apply to all visitors, users, and others who access or use the Services.
        </p>
      </section>

      <section>
        <h2>2. Disclaimer About Riot Games</h2>
        <p>
          Mamie Bot is <strong>not endorsed by Riot Games</strong> and does not reflect the views or opinions of Riot Games or anyone officially involved in producing or managing Riot Games properties. Riot Games and all associated properties are trademarks or registered trademarks of <strong>Riot Games, Inc.</strong>.
        </p>
      </section>

      <section>
        <h2>3. Use of the Services</h2>
        <p>You agree to use the Services only for lawful purposes and in accordance with these Terms. You will not:</p>
        <ul>
          <li>Violate any applicable laws or regulations.</li>
          <li>Attempt to gain unauthorized access to the Site, Services, or related systems.</li>
          <li>Use the Services in a manner that could harm, disable, overburden, or impair the Site.</li>
        </ul>
      </section>

      <section>
        <h2>4. Intellectual Property</h2>
        <p>
          All content on this Site, including text, graphics, logos, and software, is the property of Mamie Bot or its content suppliers and is protected by copyright, trademark, and other intellectual property laws. You may not reproduce, distribute, or create derivative works of our content without prior written consent.
        </p>
      </section>

      <section>
        <h2>5. Third-Party Services</h2>
        <p>
          Our Services may include links to third-party websites or services that are not owned or controlled by Mamie Bot. We are not responsible for the content, privacy policies, or practices of third-party sites or services. Use them at your own risk.
        </p>
      </section>

      <section>
        <h2>6. Limitation of Liability</h2>
        <p>
          To the fullest extent permitted by law, Mamie Bot and its owners, operators, employees, or affiliates will not be liable for any direct, indirect, incidental, special, or consequential damages arising from:
        </p>
        <ul>
          <li>Your use of or inability to use the Services.</li>
          <li>Errors or inaccuracies in the Site.</li>
          <li>Unauthorized access to or use of our systems and any personal information stored within.</li>
        </ul>
      </section>

      <section>
        <h2>7. Indemnification</h2>
        <p>
          You agree to indemnify, defend, and hold harmless Mamie Bot and its affiliates, employees, and agents from any claims, liabilities, damages, or expenses, including reasonable attorneys’ fees, arising from your use of the Site or violation of these Terms.
        </p>
      </section>

      <section>
        <h2>8. Privacy</h2>
        <p>
          We value your privacy. Please review our <a href="/privacy-policy">Privacy Policy</a> for details on how we collect, use, and disclose your information.
        </p>
      </section>

      <section>
        <h2>9. Modification of Terms</h2>
        <p>
          We reserve the right to modify these Terms at any time. Any changes will be effective immediately upon posting to the Site. Your continued use of the Services constitutes your acceptance of the updated Terms.
        </p>
      </section>

      <section>
        <h2>10. Termination</h2>
        <p>
          We may terminate or suspend your access to our Services immediately, without prior notice or liability, for any reason, including if you breach these Terms.
        </p>
      </section>

      <section>
        <h2>11. Governing Law</h2>
        <p>
          These Terms are governed by and construed in accordance with the laws of France. Any disputes arising from these Terms will be subject to the exclusive jurisdiction of the courts in France.
        </p>
      </section>

      <section>
        <h2>12. Contact Information</h2>
        <p>
          If you have any questions or concerns about these Terms, please contact us at:
        </p>
        <ul>
          <li>Email: oscarsaadate@gmail.com</li>
        </ul>
      </section>
    </div>
  );
};

export default TermsAndConditions;
