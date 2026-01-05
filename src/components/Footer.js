import React from 'react';

const Footer = () => {
    return (
        <footer>
            <div className="footer-content">
                <p>&copy; {new Date().getFullYear()} SAYHITOFIT. All rights reserved.</p>
                <ul className="footer-links">
                    <li><a href="/about">About</a></li>
                    <li><a href="/contact">Contact</a></li>
                    <li><a href="/blog">Blog</a></li>
                    <li><a href="/programs">Programs</a></li>
                </ul>
            </div>
        </footer>
    );
};

export default Footer;