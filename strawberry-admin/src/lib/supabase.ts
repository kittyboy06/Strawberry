import { createClient } from '@supabase/supabase-js';

let rawUrl =
  (import.meta.env.VITE_SUPABASE_URL as string) ||
  (import.meta.env.STRAWBERRY_SUPABASE_URL as string) ||
  '';

rawUrl = rawUrl.trim().replace(/\/+$/, '');
if (rawUrl.endsWith('/rest/v1')) {
  rawUrl = rawUrl.slice(0, -'/rest/v1'.length).replace(/\/+$/, '');
}

const supabaseUrl = rawUrl;

const supabasePublishableKey =
  (import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY as string) ||
  (import.meta.env.STRAWBERRY_SUPABASE_PUBLISHABLE_KEY as string) ||
  (import.meta.env.VITE_SUPABASE_ANON_KEY as string) ||
  (import.meta.env.STRAWBERRY_SUPABASE_ANON_KEY as string) ||
  '';

export const isSupabaseConfigured = Boolean(supabaseUrl && supabasePublishableKey);

export const supabase = isSupabaseConfigured
  ? createClient(supabaseUrl, supabasePublishableKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: false,
      },
    })
  : null;

/**
 * Formats Supabase PostgREST / Storage / RLS errors with clear re-authentication hints.
 */
export function formatSupabaseError(err: unknown, fallbackMessage: string): string {
  const errObj = err as { code?: string; status?: number; message?: string } | null;
  const code = errObj?.code;
  const status = errObj?.status;
  const msg = errObj?.message || fallbackMessage;

  if (
    code === '42501' ||
    status === 401 ||
    status === 403 ||
    msg.toLowerCase().includes('row-level security') ||
    msg.toLowerCase().includes('jwt expired')
  ) {
    return `${msg} — Please verify your faculty Supabase Auth session is active (try signing out and signing back in).`;
  }
  return msg;
}
