import React from 'react';
import './Section.scss';

interface SectionProps {
    children: React.ReactNode; 
    id: string;
    className?: string;
}

const Section: React.FC<SectionProps> = ({children, id, className}) => {

    return (
        <section id={id} className={`section ${className ?? ''}`}>
            {children}
        </section>
    );
};

export default Section;