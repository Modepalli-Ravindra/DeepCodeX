import React from 'react';

export const Logo: React.FC<{ className?: string }> = ({ className = "w-10 h-10" }) => {
  return (
    <svg viewBox="0 0 200 200" className={className} fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="logo_grad" x1="20" y1="20" x2="180" y2="180" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#6366f1" /> {/* Primary */}
          <stop offset="100%" stopColor="#38bdf8" /> {/* Accent */}
        </linearGradient>
        <linearGradient id="logo_grad_glow" x1="100" y1="0" x2="100" y2="200" gradientUnits="userSpaceOnUse">
           <stop offset="0%" stopColor="#6366f1" stopOpacity="0.2"/>
           <stop offset="100%" stopColor="#38bdf8" stopOpacity="0"/>
        </linearGradient>
      </defs>
      
      {/* Background Glow */}
      <circle cx="100" cy="100" r="90" fill="url(#logo_grad_glow)" />

      {/* Main Hexagon Outline - Tech Frame */}
      <path 
        d="M100 25 L165 62.5 V137.5 L100 175 L35 137.5 V62.5 Z" 
        stroke="url(#logo_grad)" 
        strokeWidth="8" 
        strokeLinecap="round" 
        strokeLinejoin="round"
        strokeOpacity="0.4"
      />

      {/* Stylized 'D' / Code Brackets - Left Side */}
      <path 
        d="M75 75 L55 100 L75 125" 
        stroke="url(#logo_grad)" 
        strokeWidth="14" 
        strokeLinecap="round" 
        strokeLinejoin="round" 
      />
      
      {/* Stylized 'C' / Code Brackets - Right Side */}
      <path 
        d="M125 75 L145 100 L125 125" 
        stroke="url(#logo_grad)" 
        strokeWidth="14" 
        strokeLinecap="round" 
        strokeLinejoin="round" 
      />

      {/* Central Node / Core Intelligence */}
      <path 
        d="M100 70 V130" 
        stroke="url(#logo_grad)" 
        strokeWidth="8" 
        strokeLinecap="round" 
      />
      <circle cx="100" cy="100" r="10" fill="#f8fafc" />
      <circle cx="100" cy="100" r="14" stroke="url(#logo_grad)" strokeWidth="3" />

      {/* Circuit Dots */}
      <circle cx="165" cy="62.5" r="6" fill="#6366f1" />
      <circle cx="35" cy="137.5" r="6" fill="#38bdf8" />
    </svg>
  );
};