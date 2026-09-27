import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Lock, Mail, ArrowRight } from 'lucide-react';
import { Logo } from '../components/Logo';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const res = await fetch("http://127.0.0.1:5000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });
      
      const data = await res.json();
      if (!res.ok) {
        alert(data.error || "Login failed");
        return;
      }

      localStorage.setItem('auth_token', data.token);
      if (data.user && data.user.name) {
        localStorage.setItem('auth_name', data.user.name);
      } else {
        localStorage.setItem('auth_name', email.split('@')[0]);
      }
      navigate('/');
    } catch (err) {
      alert("Error connecting to server");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <Logo className="w-12 h-12 text-primary mx-auto mb-6" />
          <h2 className="text-2xl font-semibold tracking-tight text-textPrimary">Welcome back</h2>
          <p className="mt-3 text-sm text-textSecondary">Sign in to DeepCodeX.</p>
        </div>

        <div className="bg-secondaryBg p-8 rounded-2xl border border-borderSubtle shadow-premium">
          <form className="space-y-6" onSubmit={handleLogin}>
            <div>
              <label className="block text-sm font-medium text-textPrimary mb-2">Email address</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-textMuted stroke-[1.5px]" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 bg-background border border-borderSubtle rounded-lg focus:ring-1 focus:ring-primary/50 focus:border-primary/50 text-textPrimary placeholder:text-textMuted sm:text-sm transition-colors outline-none"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-textPrimary mb-2">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-textMuted stroke-[1.5px]" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 bg-background border border-borderSubtle rounded-lg focus:ring-1 focus:ring-primary/50 focus:border-primary/50 text-textPrimary placeholder:text-textMuted sm:text-sm transition-colors outline-none"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full flex items-center justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-background bg-primary hover:bg-primarySubtle focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary focus:ring-offset-background transition-colors"
            >
              Sign In <ArrowRight className="ml-2 w-4 h-4 stroke-[2px]" />
            </button>
          </form>

          <div className="mt-6 text-center text-sm">
            <span className="text-textSecondary">Don't have an account? </span>
            <Link to="/register" className="font-medium text-primary hover:text-primarySubtle transition-colors">
              Register now
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
