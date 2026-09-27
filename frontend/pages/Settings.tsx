import React, { useState, useEffect } from 'react';
import { User, Lock, Save, CheckCircle2 } from 'lucide-react';

export const Settings: React.FC = () => {
  const [userName, setUserName] = useState('');
  const [tempName, setTempName] = useState('');
  const [activeTab, setActiveTab] = useState('Profile');
  const [showSuccess, setShowSuccess] = useState(false);
  
  useEffect(() => {
    const name = localStorage.getItem('auth_name') || 'User';
    setUserName(name);
    setTempName(name);
  }, []);

  const handleSaveProfile = () => {
    setUserName(tempName);
    localStorage.setItem('auth_name', tempName);
    
    // Dispatch a custom event so Layout.tsx can instantly update the avatar letter
    window.dispatchEvent(new Event('auth_name_updated'));
    
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  const handleSavePassword = () => {
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  const tabs = [
    { icon: User, label: 'Profile' },
    { icon: Lock, label: 'Security' },
  ];

  return (
    <div className="max-w-4xl mx-auto p-6 md:p-8 space-y-8 animate-fade-in pb-20">
      
      <div className="mb-8 relative">
        <h1 className="text-3xl font-bold text-textPrimary tracking-tight">Settings</h1>
        <p className="text-textSecondary mt-2">Manage your profile and security settings.</p>
        
        {/* Success Toast */}
        <div className={`absolute top-0 right-0 flex items-center gap-2 bg-success/10 border border-success/30 text-success px-4 py-2 rounded-lg transition-all duration-300 ${showSuccess ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4 pointer-events-none'}`}>
          <CheckCircle2 className="w-4 h-4" />
          <span className="text-sm font-medium">Settings saved successfully!</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* Settings Sidebar */}
        <div className="md:col-span-1 space-y-1">
          {tabs.map((item, i) => (
            <button 
              key={i}
              onClick={() => setActiveTab(item.label)}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === item.label
                  ? 'bg-primary/10 text-primary border border-primary/20' 
                  : 'text-textSecondary hover:bg-surface hover:text-textPrimary'
              }`}
            >
              <item.icon className="w-4 h-4 stroke-[2px]" />
              {item.label}
            </button>
          ))}
        </div>

        {/* Settings Content */}
        <div className="md:col-span-3 space-y-6">
          
          {activeTab === 'Profile' && (
            <div className="bg-surface border border-borderSubtle rounded-2xl p-6 animate-fade-in">
              <h2 className="text-lg font-bold text-textPrimary mb-6">Profile Information</h2>
              
              <div className="flex items-center gap-6 mb-8">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white text-3xl font-bold shadow-glow">
                  {userName.charAt(0).toUpperCase()}
                </div>
              </div>

              <div className="space-y-4 max-w-lg">
                <div>
                  <label className="block text-sm font-medium text-textPrimary mb-1.5">Display Name</label>
                  <input 
                    type="text" 
                    value={tempName}
                    onChange={(e) => setTempName(e.target.value)}
                    className="w-full bg-background border border-borderSubtle rounded-lg px-4 py-2 text-sm text-textPrimary focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-textPrimary mb-1.5">Email Address</label>
                  <input 
                    type="email" 
                    defaultValue="user@example.com"
                    className="w-full bg-background border border-borderSubtle rounded-lg px-4 py-2 text-sm text-textSecondary cursor-not-allowed border-dashed transition-all opacity-70"
                    disabled
                  />
                </div>
              </div>
              
              <div className="mt-8 pt-6 border-t border-borderSubtle flex justify-end">
                <button 
                  onClick={handleSaveProfile}
                  className="flex items-center gap-2 bg-primary hover:bg-primarySubtle text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors shadow-glow"
                >
                  <Save className="w-4 h-4" /> Save Changes
                </button>
              </div>
            </div>
          )}

          {activeTab === 'Security' && (
            <div className="bg-surface border border-borderSubtle rounded-2xl p-6 animate-fade-in">
              <h2 className="text-lg font-bold text-textPrimary mb-6">Security Settings</h2>
              <div className="space-y-4 max-w-lg">
                <div>
                  <label className="block text-sm font-medium text-textPrimary mb-1.5">Current Password</label>
                  <input type="password" placeholder="••••••••" className="w-full bg-background border border-borderSubtle rounded-lg px-4 py-2 text-sm text-textPrimary focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-textPrimary mb-1.5">New Password</label>
                  <input type="password" placeholder="••••••••" className="w-full bg-background border border-borderSubtle rounded-lg px-4 py-2 text-sm text-textPrimary focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all" />
                </div>
                <div className="pt-4 flex justify-end border-t border-borderSubtle mt-6">
                  <button 
                    onClick={handleSavePassword} 
                    className="flex items-center gap-2 bg-primary hover:bg-primarySubtle text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors shadow-glow"
                  >
                    <Save className="w-4 h-4" /> Update Password
                  </button>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};
