import { useEffect, useState } from 'react';
import './NavBar.scss';

const NavBar = () => {
    const [active, setActive] = useState<string>('home');

    const handleScroll = () => {
        const sections = document.querySelectorAll('section');
        let currentSection = '';

        sections.forEach((section) => {
            const sectionTop = section.getBoundingClientRect().top;
            const sectionHeight = section.clientHeight;

            if (sectionTop <= 0 && sectionTop + sectionHeight > 0) {
                currentSection = section.getAttribute('id') || '';
            }
        });

        if (currentSection) {
            setActive(currentSection);
        }
    };

    useEffect(() => {
        window.addEventListener('scroll', handleScroll);
        return () => {
            window.removeEventListener('scroll', handleScroll);
        };
    }, []);

    return (
        <nav className="sticky-navbar">
            <ul>
                <li>
                    <a 
                        href="#home" 
                        className={active === 'home' ? 'active' : ''}
                    >
                        Home
                    </a>
                </li>
                {/* <li>
                    <a 
                        href="#search" 
                        className={active === 'search' ? 'active' : ''}
                    >
                        Search
                    </a>
                </li> */}
                <li>
                    <a 
                        href="#eventsList" 
                        className={active === 'eventsList' ? 'active' : ''}
                    >
                        Live
                    </a>
                </li>
            </ul>
        </nav>
    );
};

export default NavBar;
