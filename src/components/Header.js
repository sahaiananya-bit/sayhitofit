import React from 'react';
import Navigation from './Navigation';
import './Header.css'; // Assuming you have a CSS file for header styles

const Header = () => {
    return (
        <header>
            <div className="logo">
                <h1>SAYHITOFIT</h1>
            </div>
            <Navigation />
        </header>
    );
};

export default Header;