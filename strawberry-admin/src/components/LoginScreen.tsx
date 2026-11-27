import React, { useState } from 'react';
import { Lock, Mail, Eye, EyeOff, AlertCircle, LogIn, ShieldCheck } from 'lucide-react';
import { supabase } from '../lib/supabase';
import strawberryLogo from '../assets/strawberry-logo.png';

/**
 * Full-portal Supabase Email & Password sign-in gate for Faculty / Lab Coordinators.
 * Enforces the `TO authenticated` RLS write policies configured in Supabase.
 */
export const LoginScreen: React.FC = () => {
  const [email, setEmail] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!supabase) {
      setError('Supabase client is not configured.');
      return;
    }

    const trimmedEmail = email.trim();
    if (!trimmedEmail || !password) {
      setError('Please enter both your faculty email and password.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const { error: authError } = await supabase.auth.signInWithPassword({
        email: trimmedEmail,
        password,
      });

      if (authError) {
        setError(authError.message || 'Invalid faculty credentials.');
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unable to reach Supabase Auth service.';
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 bg-gradient-to-b from-[#FDEBEC] via-[#FDF1F2] to-[#FEF6F5]">
      <div className="w-full max-w-md bg-white/95 border border-[#F5E8EB] rounded-3xl shadow-[0_12px_36px_rgba(190,18,60,0.08)] p-8 space-y-6">
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center space-y-2">
          <div className="w-16 h-16 rounded-2xl bg-[#FFF0F3] border border-[#FDE2E7] flex items-center justify-center p-2 shadow-xs">
            <img src={strawberryLogo} alt="Strawberry" className="w-full h-full object-contain" />
          </div>
          <div className="font-serif italic font-bold text-2xl text-[#881337] tracking-tight pt-1">
            Strawberry
          </div>
          <h1 className="text-xl font-serif font-bold text-[#2E1E24]">Faculty Portal Sign In</h1>
          <p className="text-xs text-[#6B7280] max-w-xs">
            Authenticate with your Supabase faculty account to manage courses, source code, and version releases.
          </p>
        </div>

        {/* Auth Error Banner */}
        {error && (
          <div
            role="alert"
            className="p-3 bg-[#FEF2F2] border border-[#FCA5A5] rounded-xl text-xs text-[#991B1B] flex items-start gap-2"
          >
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="faculty-email" className="block text-xs font-medium text-[#4B3840] mb-1.5">
              Faculty Email
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-[#8C6D76] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                id="faculty-email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="faculty@department.edu"
                className="w-full bg-[#FAF3F5] border border-[#F2DEE3] rounded-xl pl-10 pr-3.5 py-2.5 text-xs text-[#2E1E24] placeholder-[#8C6D76] focus:outline-none focus:border-[#BE123C] transition-colors"
              />
            </div>
          </div>

          <div>
            <label htmlFor="faculty-password" className="block text-xs font-medium text-[#4B3840] mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-[#8C6D76] absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                id="faculty-password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full bg-[#FAF3F5] border border-[#F2DEE3] rounded-xl pl-10 pr-10 py-2.5 text-xs text-[#2E1E24] placeholder-[#8C6D76] focus:outline-none focus:border-[#BE123C] transition-colors"
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[#8C6D76] hover:text-[#2E1E24] cursor-pointer"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full py-2.5 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-sm ${
              isSubmitting
                ? 'bg-[#F5E8EB] text-[#A89CA0] cursor-not-allowed'
                : 'bg-[#BE123C] hover:bg-[#9F1239] text-white cursor-pointer'
            }`}
          >
            <LogIn className="w-4 h-4" />
            <span>{isSubmitting ? 'Signing In...' : 'Sign In to Admin Portal'}</span>
          </button>
        </form>

        {/* RLS Policy Footer Note */}
        <div className="pt-3 border-t border-[#FDF0F3] flex items-start gap-2 text-[11px] text-[#8C6D76]">
          <ShieldCheck className="w-4 h-4 text-[#059669] shrink-0 mt-0.5" />
          <span>
            Protected by PostgreSQL & Storage Row-Level Security. Faculty accounts are managed under Supabase Auth.
          </span>
        </div>
      </div>
    </div>
  );
};
