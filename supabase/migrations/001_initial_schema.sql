-- 🍓 Strawberry Schema Migration: Academic Catalog & Storage Policies
-- Version: 1.0.0

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Academic Years
CREATE TABLE IF NOT EXISTS public.years (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    year_number INT NOT NULL UNIQUE, -- 2, 3, 4
    display_name TEXT NOT NULL,       -- "2nd Year", "3rd Year", "4th Year"
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Semesters
CREATE TABLE IF NOT EXISTS public.semesters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    year_id UUID NOT NULL REFERENCES public.years(id) ON DELETE CASCADE,
    semester_number INT NOT NULL,     -- 3, 4, 5, 6, 7, 8
    display_name TEXT NOT NULL,       -- "Semester 3", etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(year_id, semester_number)
);

-- 3. Subjects
CREATE TABLE IF NOT EXISTS public.subjects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    semester_id UUID NOT NULL REFERENCES public.semesters(id) ON DELETE CASCADE,
    subject_code TEXT NOT NULL UNIQUE, -- e.g. "CS301"
    subject_name TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Experiments
CREATE TABLE IF NOT EXISTS public.experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_id UUID NOT NULL REFERENCES public.subjects(id) ON DELETE CASCADE,
    experiment_number INT NOT NULL,   -- 1, 2, 3...
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(subject_id, experiment_number)
);

-- 5. Experiment Versions
CREATE TABLE IF NOT EXISTS public.experiment_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES public.experiments(id) ON DELETE CASCADE,
    version_number INT NOT NULL DEFAULT 1,
    storage_path TEXT NOT NULL,       -- e.g. "programs/CS301_01_v1.java"
    filename TEXT NOT NULL,           -- e.g. "SocketServer.java"
    sha256 TEXT NOT NULL,             -- SHA-256 integrity hash
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(experiment_id, version_number)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE public.years ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.semesters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.experiment_versions ENABLE ROW LEVEL SECURITY;

-- Anonymous (Public / Student CLI) Read-Only Policies
CREATE POLICY "Public Read Years" ON public.years FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public Read Semesters" ON public.semesters FOR SELECT TO anon, authenticated USING (true);
CREATE POLICY "Public Read Subjects" ON public.subjects FOR SELECT TO anon, authenticated USING (is_active = true);
CREATE POLICY "Public Read Experiments" ON public.experiments FOR SELECT TO anon, authenticated USING (is_published = true);
CREATE POLICY "Public Read Versions" ON public.experiment_versions FOR SELECT TO anon, authenticated USING (true);

-- Authenticated (Admin / Faculty) Write Policies
CREATE POLICY "Admin All Years" ON public.years FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Admin All Semesters" ON public.semesters FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Admin All Subjects" ON public.subjects FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Admin All Experiments" ON public.experiments FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "Admin All Versions" ON public.experiment_versions FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- ─────────────────────────────────────────────────────────────────────────────
-- STORAGE BUCKET CONFIGURATION
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO storage.buckets (id, name, public) 
VALUES ('programs', 'programs', true)
ON CONFLICT (id) DO NOTHING;

-- Storage RLS: Public read, Authenticated write
CREATE POLICY "Public Read Storage Programs"
ON storage.objects FOR SELECT TO anon, authenticated
USING (bucket_id = 'programs');

CREATE POLICY "Admin Write Storage Programs"
ON storage.objects FOR INSERT TO authenticated
WITH CHECK (bucket_id = 'programs');

CREATE POLICY "Admin Update Storage Programs"
ON storage.objects FOR UPDATE TO authenticated
USING (bucket_id = 'programs');

CREATE POLICY "Admin Delete Storage Programs"
ON storage.objects FOR DELETE TO authenticated
USING (bucket_id = 'programs');
