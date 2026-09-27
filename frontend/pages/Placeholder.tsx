import React from 'react';
import { Construction } from 'lucide-react';

interface PlaceholderProps {
  title: string;
}

export const Placeholder: React.FC<PlaceholderProps> = ({ title }) => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center space-y-6 animate-fade-in p-8">
      <div className="w-24 h-24 rounded-full bg-surface border border-borderSubtle flex items-center justify-center shadow-glow">
        <Construction className="w-10 h-10 text-primary" />
      </div>
      <div>
        <h2 className="text-3xl font-bold text-textPrimary tracking-tight mb-2">{title}</h2>
        <p className="text-textSecondary max-w-md mx-auto">
          This module is currently under development. Check back soon for updates.
        </p>
      </div>
    </div>
  );
};
