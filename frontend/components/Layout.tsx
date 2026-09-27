import React, { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, Code2, History, Settings, Search, Bell, LogOut, CheckCircle, FileText, Menu, X } from 'lucide-react';
import { Logo } from './Logo';

export const Layout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [userName, setUserName] = useState<string>('U');
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const updateName = () => {
      const name = localStorage.getItem('auth_name');
      if (name) {
        setUserName(name.charAt(0).toUpperCase());
      }
    };

    updateName();
    window.addEventListener('auth_name_updated', updateName);
    return () => window.removeEventListener('auth_name_updated', updateName);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_name');
    navigate('/login');
  };

  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Home' },
    { to: '/analyze', icon: Code2, label: 'Code Analysis' },
    { to: '/history', icon: History, label: 'History' },
    { to: '/settings', icon: Settings, label: 'Settings' },
  ];

  const topNavItems = [
    { to: '/', icon: LayoutDashboard, label: 'Home' },
    { to: '/analyze', icon: Search, label: 'Analyze' },
    { to: '/history', icon: History, label: 'History' },
    { to: '/docs', icon: FileText, label: 'Docs' },
  ];

  return (
    <div className="flex h-screen bg-background text-textPrimary overflow-hidden font-sans">
      
      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 md:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-[260px] bg-secondaryBg/95 backdrop-blur-xl border-r border-borderSubtle flex-col transform transition-transform duration-300 md:relative md:translate-x-0 md:flex shrink-0 ${isMobileMenuOpen ? 'translate-x-0 flex' : '-translate-x-full hidden'}`}>
        
        {/* Mobile close button */}
        <button 
          className="md:hidden absolute top-6 right-4 text-textSecondary hover:text-textPrimary"
          onClick={() => setIsMobileMenuOpen(false)}
        >
          <X className="w-5 h-5" />
        </button>

        {/* Logo Area */}
        <div className="p-6 pb-8">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white shadow-glow">
              <Code2 className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-wide">DeepCodeX</h1>
              <p className="text-[10px] text-textSecondary uppercase tracking-wider font-medium">AI Code Complexity Analyzer</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 space-y-1.5 overflow-y-auto mb-4">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 font-medium text-sm group ${
                  isActive
                    ? 'bg-gradient-to-r from-primary/20 to-primary/5 text-primarySubtle border border-primary/20 shadow-[0_0_15px_rgba(99,91,255,0.1)]'
                    : 'text-textSecondary hover:bg-surface hover:text-textPrimary'
                }`
              }
            >
              <item.icon className="w-5 h-5 stroke-[1.5px]" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        
        {/* Bottom Bar */}
        <div className="p-4 border-t border-borderSubtle flex items-center justify-between">
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-sm text-textSecondary hover:text-danger transition-colors w-full px-2"
          >
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden flex flex-col bg-background/95 relative">
        {/* Background glow effects for the main content */}
        <div className="absolute top-0 left-1/4 w-[500px] h-[300px] bg-primary/10 blur-[120px] rounded-full pointer-events-none z-0"></div>
        <div className="absolute top-1/4 right-0 w-[400px] h-[400px] bg-accent/5 blur-[120px] rounded-full pointer-events-none z-0"></div>

        {/* Top Header */}
        <header className="h-[72px] px-4 md:px-8 flex items-center justify-between shrink-0 relative z-20">
          
          <div className="md:hidden flex items-center gap-3">
             <button onClick={() => setIsMobileMenuOpen(true)} className="text-textSecondary hover:text-textPrimary transition-colors">
               <Menu className="w-6 h-6" />
             </button>
             <Code2 className="w-6 h-6 text-primary" />
          </div>

          {/* Center Pill Nav */}
          <div className="hidden md:flex items-center gap-1 bg-surface border border-borderSubtle p-1 rounded-full relative z-20">
            {topNavItems.map((item) => {
              const isActive = location.pathname === item.to;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={`flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-medium transition-all ${
                    isActive 
                      ? 'bg-primary text-white shadow-glow' 
                      : 'text-textSecondary hover:text-textPrimary hover:bg-surfaceElevated'
                  }`}
                >
                  <item.icon className="w-3.5 h-3.5" />
                  {item.label}
                </NavLink>
              )
            })}
          </div>
          
          <div className="flex items-center gap-4 relative z-20">
            <div className="hidden lg:flex items-center relative group">
              <Search className="w-4 h-4 text-textMuted absolute left-3 transition-colors group-focus-within:text-primary" />
              <input 
                type="text" 
                placeholder="Search files, analyses..." 
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setShowSearchDropdown(e.target.value.length > 0);
                }}
                onFocus={() => {
                  if (searchQuery.length > 0) setShowSearchDropdown(true);
                }}
                onBlur={() => setTimeout(() => setShowSearchDropdown(false), 200)}
                className="bg-surface border border-borderSubtle rounded-full pl-9 pr-16 py-2 text-xs text-textPrimary placeholder:text-textMuted focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 w-[240px] transition-all"
              />
              <div className="absolute right-2 flex items-center">
                <kbd className="bg-surfaceElevated border border-borderSubtle rounded px-1.5 py-0.5 text-[9px] text-textMuted font-mono">Ctrl K</kbd>
              </div>

              {/* Search Dropdown */}
              {showSearchDropdown && (
                <div className="absolute top-full mt-2 w-[300px] right-0 md:right-auto md:left-0 bg-surfaceElevated border border-borderSubtle rounded-xl shadow-2xl p-2 z-50">
                  <div className="text-[10px] uppercase tracking-wider text-textMuted font-semibold px-2 py-1 mb-1">Results</div>
                  <button onClick={() => {navigate('/history'); setShowSearchDropdown(false);}} className="w-full text-left px-3 py-2 text-sm text-textPrimary hover:bg-surface rounded-lg flex items-center gap-3">
                    <FileText className="w-4 h-4 text-textSecondary" />
                    <span>Search history for "<span className="text-primary">{searchQuery}</span>"</span>
                  </button>
                  <button onClick={() => {navigate('/analyze'); setShowSearchDropdown(false);}} className="w-full text-left px-3 py-2 text-sm text-textPrimary hover:bg-surface rounded-lg flex items-center gap-3">
                    <Code2 className="w-4 h-4 text-textSecondary" />
                    <span>New analysis</span>
                  </button>
                </div>
              )}
            </div>
            
            <div className="relative">
              <button 
                onClick={() => setShowNotifications(!showNotifications)}
                className="w-9 h-9 rounded-full bg-surface border border-borderSubtle flex items-center justify-center text-textSecondary hover:bg-surfaceElevated hover:text-textPrimary transition-colors relative"
              >
                <Bell className="w-4 h-4 stroke-[1.5px]" />
                <span className="absolute top-2 right-2 w-1.5 h-1.5 bg-danger rounded-full border border-surface"></span>
              </button>

              {/* Notifications Dropdown */}
              {showNotifications && (
                <div className="absolute top-full mt-2 right-0 w-64 bg-surfaceElevated border border-borderSubtle rounded-xl shadow-2xl p-3 z-50">
                  <h4 className="text-sm font-semibold text-textPrimary mb-3 px-1">Notifications</h4>
                  <div className="space-y-2">
                    <div className="p-3 bg-surface border border-borderSubtle rounded-lg flex items-start gap-3">
                      <CheckCircle className="w-4 h-4 text-success mt-0.5" />
                      <div>
                        <p className="text-xs text-textPrimary font-medium">Analysis Complete</p>
                        <p className="text-[10px] text-textSecondary mt-0.5">Your file `example.js` has been analyzed.</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            
            <div className="relative group">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary to-accent border border-borderSubtle flex items-center justify-center text-white text-sm font-semibold cursor-pointer shadow-sm">
                {userName}
              </div>
              
              {/* Profile Dropdown */}
              <div className="absolute top-full mt-2 right-0 w-48 bg-surfaceElevated border border-borderSubtle rounded-xl shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50 overflow-hidden">
                <button onClick={() => navigate('/settings')} className="w-full text-left px-4 py-3 text-sm text-textPrimary hover:bg-surface flex items-center gap-2">
                  <Settings className="w-4 h-4 text-textSecondary" /> Settings
                </button>
                <button onClick={handleLogout} className="w-full text-left px-4 py-3 text-sm text-danger hover:bg-surface flex items-center gap-2 border-t border-borderSubtle">
                  <LogOut className="w-4 h-4" /> Sign Out
                </button>
              </div>
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-auto relative scroll-smooth z-10 w-full">
          <Outlet />
        </div>
      </main>
    </div>
  );
};