import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { UploadModal } from './components/UploadModal';
import type { Year, Subject, Experiment, ExperimentVersion } from './types';
import { supabase, isSupabaseConfigured } from './lib/supabase';
import { 
  BookOpen, 
  Upload, 
  Plus, 
  CheckCircle2, 
  FileCode2, 
  Clock, 
  ChevronRight,
  Sparkles
} from 'lucide-react';

// Default demo data for offline testing
const INITIAL_YEARS: Year[] = [
  { id: 'yr-2', year_number: 2, display_name: '2nd Year' },
  { id: 'yr-3', year_number: 3, display_name: '3rd Year' },
  { id: 'yr-4', year_number: 4, display_name: '4th Year' },
];

const INITIAL_SUBJECTS: Subject[] = [
  { id: 'sub-cn', semester_id: 'sem-3', subject_code: 'CS301', subject_name: 'Computer Networks', is_active: true, semester_label: 'Semester 3' },
  { id: 'sub-dbms', semester_id: 'sem-3', subject_code: 'CS302', subject_name: 'Database Management Systems', is_active: true, semester_label: 'Semester 3' },
  { id: 'sub-java', semester_id: 'sem-3', subject_code: 'CS303', subject_name: 'Java Programming', is_active: true, semester_label: 'Semester 3' },
  { id: 'sub-os', semester_id: 'sem-4', subject_code: 'CS401', subject_name: 'Operating Systems', is_active: true, semester_label: 'Semester 4' },
];

const INITIAL_EXPERIMENTS: Experiment[] = [
  {
    id: 'exp-cn-1',
    subject_id: 'sub-cn',
    experiment_number: 1,
    title: 'Socket Programming',
    description: 'TCP client-server socket communication',
    is_published: true,
    current_version: {
      id: 'v1',
      experiment_id: 'exp-cn-1',
      version_number: 1,
      storage_path: 'programs/socket_server.py',
      filename: 'socket_server.py',
      sha256: '9b2c34a2e5d7990beea9e4210d7c71d64388414adbf68e8e7b1a50428d0cb0d7',
      created_at: new Date().toISOString()
    }
  },
  {
    id: 'exp-cn-2',
    subject_id: 'sub-cn',
    experiment_number: 2,
    title: 'TCP Client Server',
    description: 'TCP client connection to echo server',
    is_published: true,
    current_version: {
      id: 'v2',
      experiment_id: 'exp-cn-2',
      version_number: 1,
      storage_path: 'programs/tcp_client.py',
      filename: 'tcp_client.py',
      sha256: '68e8e7b1a50428d0cb0d79b2c34a2e5d7990beea9e4210d7c71d64388414adbf',
      created_at: new Date().toISOString()
    }
  }
];

export const App: React.FC = () => {
  const [years] = useState<Year[]>(INITIAL_YEARS);
  const [selectedYear, setSelectedYear] = useState<number>(2);
  const [subjects, setSubjects] = useState<Subject[]>(INITIAL_SUBJECTS);
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(INITIAL_SUBJECTS[0]);
  const [experiments, setExperiments] = useState<Experiment[]>(INITIAL_EXPERIMENTS);
  const [uploadModalExp, setUploadModalExp] = useState<Experiment | null>(null);

  // New experiment form state
  const [isAddingExp, setIsAddingExp] = useState(false);
  const [newExpTitle, setNewExpTitle] = useState('');
  const [newExpDesc, setNewExpDesc] = useState('');

  // Fetch from Supabase if configured
  useEffect(() => {
    const client = supabase;
    if (!isSupabaseConfigured || !client) return;

    const fetchRemoteData = async () => {
      try {
        const { data: subData } = await client
          .from('subjects')
          .select('*, semesters(display_name)')
          .eq('is_active', true);

        if (subData) {
          const mapped: Subject[] = subData.map((s: any) => ({
            id: s.id,
            semester_id: s.semester_id,
            subject_code: s.subject_code,
            subject_name: s.subject_name,
            is_active: s.is_active,
            semester_label: s.semesters?.display_name || '',
          }));
          setSubjects(mapped);
          if (mapped.length > 0) setSelectedSubject(mapped[0]);
        }
      } catch (e) {
        console.error('Failed to load from Supabase:', e);
      }
    };

    fetchRemoteData();
  }, []);

  const handleUploadSuccess = (version: ExperimentVersion) => {
    setExperiments((prev) =>
      prev.map((exp) =>
        exp.id === version.experiment_id
          ? { ...exp, current_version: version }
          : exp
      )
    );
  };

  const handleCreateExperiment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSubject || !newExpTitle.trim()) return;

    const nextIndex = experiments.length + 1;
    const newExp: Experiment = {
      id: `exp-${Date.now()}`,
      subject_id: selectedSubject.id,
      experiment_number: nextIndex,
      title: newExpTitle.trim(),
      description: newExpDesc.trim(),
      is_published: true,
      current_version: null,
    };

    const client = supabase;
    if (isSupabaseConfigured && client) {
      try {
        const { data, error } = await client
          .from('experiments')
          .insert({
            subject_id: selectedSubject.id,
            experiment_number: nextIndex,
            title: newExp.title,
            description: newExp.description,
          })
          .select()
          .single();

        if (error) throw error;
        setExperiments((prev) => [...prev, data]);
      } catch (err: any) {
        alert(`Failed to create experiment: ${err.message}`);
        return;
      }
    } else {
      setExperiments((prev) => [...prev, newExp]);
    }

    setNewExpTitle('');
    setNewExpDesc('');
    setIsAddingExp(false);
  };

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Year Tabs */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2">
            {years.map((yr) => (
              <button
                key={yr.id}
                onClick={() => setSelectedYear(yr.year_number)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  selectedYear === yr.year_number
                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/40'
                }`}
              >
                {yr.display_name}
              </button>
            ))}
          </div>

          <div className="text-xs text-slate-400 flex items-center gap-1.5 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg">
            <Sparkles className="w-3.5 h-3.5 text-rose-400" />
            <span>Changes sync automatically to student CLI clients</span>
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          {/* Subjects Sidebar */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-rose-400" />
                Subjects ({selectedYear}nd/rd/th Year)
              </h2>
            </div>

            <div className="space-y-2">
              {subjects.map((sub) => {
                const isSelected = selectedSubject?.id === sub.id;
                return (
                  <div
                    key={sub.id}
                    onClick={() => setSelectedSubject(sub)}
                    className={`p-3 rounded-lg border cursor-pointer transition-all flex items-center justify-between ${
                      isSelected
                        ? 'bg-rose-500/10 border-rose-500/30 text-white'
                        : 'bg-slate-950/40 border-slate-800/60 text-slate-300 hover:border-slate-700'
                    }`}
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-semibold text-rose-400">
                          {sub.subject_code}
                        </span>
                        <span className="text-xs bg-slate-800 px-2 py-0.5 rounded text-slate-400">
                          {sub.semester_label || 'Sem 3'}
                        </span>
                      </div>
                      <p className="text-sm font-medium mt-1">{sub.subject_name}</p>
                    </div>
                    <ChevronRight className={`w-4 h-4 ${isSelected ? 'text-rose-400' : 'text-slate-600'}`} />
                  </div>
                );
              })}
            </div>
          </div>

          {/* Experiments & Files Panel */}
          <div className="lg:col-span-2 space-y-5">
            {selectedSubject ? (
              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-6">
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded">
                        {selectedSubject.subject_code}
                      </span>
                      <h2 className="text-lg font-bold text-white">
                        {selectedSubject.subject_name}
                      </h2>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      Manage laboratory programs and upload verified source files.
                    </p>
                  </div>

                  <button
                    onClick={() => setIsAddingExp(true)}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-rose-600 hover:bg-rose-500 text-white rounded-lg transition-colors shadow-sm"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Add Experiment</span>
                  </button>
                </div>

                {/* Add Experiment Inline Form */}
                {isAddingExp && (
                  <form onSubmit={handleCreateExperiment} className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
                    <h3 className="text-xs font-semibold text-slate-200">New Laboratory Experiment</h3>
                    <input
                      type="text"
                      placeholder="Experiment Title (e.g., DNS Resolution)"
                      value={newExpTitle}
                      onChange={(e) => setNewExpTitle(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-rose-500"
                      required
                    />
                    <input
                      type="text"
                      placeholder="Brief Description or Algorithm details"
                      value={newExpDesc}
                      onChange={(e) => setNewExpDesc(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-rose-500"
                    />
                    <div className="flex justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => setIsAddingExp(false)}
                        className="px-3 py-1.5 text-xs text-slate-400 hover:text-white"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="px-3 py-1.5 text-xs bg-rose-600 text-white rounded-lg font-medium"
                      >
                        Save Experiment
                      </button>
                    </div>
                  </form>
                )}

                {/* Experiment Cards */}
                <div className="space-y-4">
                  {experiments.map((exp) => (
                    <div
                      key={exp.id}
                      className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-5 hover:border-slate-700 transition-all space-y-4"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-3">
                          <span className="font-mono text-xs font-bold bg-slate-900 border border-slate-800 text-slate-300 w-8 h-8 rounded-lg flex items-center justify-center shrink-0">
                            {exp.experiment_number.toString().padStart(2, '0')}
                          </span>
                          <div>
                            <h3 className="text-sm font-semibold text-white">{exp.title}</h3>
                            <p className="text-xs text-slate-400 mt-0.5">{exp.description}</p>
                          </div>
                        </div>

                        <button
                          onClick={() => setUploadModalExp(exp)}
                          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors border border-slate-700"
                        >
                          <Upload className="w-3.5 h-3.5 text-rose-400" />
                          <span>{exp.current_version ? 'Update Code' : 'Upload Code'}</span>
                        </button>
                      </div>

                      {/* Version status card */}
                      {exp.current_version ? (
                        <div className="bg-slate-900/80 rounded-lg p-3 border border-slate-800/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                          <div className="flex items-center gap-2">
                            <FileCode2 className="w-4 h-4 text-emerald-400" />
                            <span className="font-mono font-medium text-slate-200">
                              {exp.current_version.filename}
                            </span>
                            <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded text-[11px] font-mono">
                              v{exp.current_version.version_number}
                            </span>
                          </div>

                          <div className="flex items-center gap-2 text-slate-400 text-[11px]">
                            <span className="font-mono bg-slate-950 px-2 py-1 rounded border border-slate-800 text-slate-400 truncate max-w-xs">
                              SHA: {exp.current_version.sha256.slice(0, 16)}...
                            </span>
                            <span className="flex items-center gap-1 text-emerald-400">
                              <CheckCircle2 className="w-3.5 h-3.5" /> Published
                            </span>
                          </div>
                        </div>
                      ) : (
                        <div className="bg-amber-500/5 border border-amber-500/20 rounded-lg p-3 text-xs text-amber-300 flex items-center gap-2">
                          <Clock className="w-4 h-4 shrink-0" />
                          <span>No program uploaded yet. Click "Upload Code" to publish source code for students.</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="p-12 text-center text-slate-500 bg-slate-900/30 rounded-xl border border-slate-800">
                Select a subject to view and manage laboratory programs.
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Upload Modal */}
      {uploadModalExp && (
        <UploadModal
          experiment={uploadModalExp}
          onClose={() => setUploadModalExp(null)}
          onUploadSuccess={handleUploadSuccess}
        />
      )}
    </div>
  );
};

export default App;
