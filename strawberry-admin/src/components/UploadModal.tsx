import React, { useState } from 'react';
import { Upload, X, Check, FileCode, Hash, AlertCircle } from 'lucide-react';
import type { Experiment, ExperimentVersion } from '../types';
import { calculateSHA256 } from '../lib/crypto';
import { supabase, isSupabaseConfigured } from '../lib/supabase';

interface UploadModalProps {
  experiment: Experiment;
  onClose: () => void;
  onUploadSuccess: (version: ExperimentVersion) => void;
}

export const UploadModal: React.FC<UploadModalProps> = ({
  experiment,
  onClose,
  onUploadSuccess,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>('');
  const [sha256, setSha256] = useState<string>('');
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (selectedFile: File) => {
    setError(null);
    setFile(selectedFile);

    // Calculate SHA-256
    try {
      const hash = await calculateSHA256(selectedFile);
      setSha256(hash);
    } catch (err) {
      setError('Failed to compute SHA-256 hash');
    }

    // Read text preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview((e.target?.result as string) || '');
    };
    reader.readAsText(selectedFile);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handlePublish = async () => {
    if (!file || !sha256) return;
    setIsUploading(true);
    setError(null);

    try {
      if (isSupabaseConfigured && supabase) {
        // 1. Upload to Supabase Storage bucket 'programs'
        const storagePath = `programs/${experiment.id}/${file.name}`;
        const { error: storageError } = await supabase.storage
          .from('programs')
          .upload(storagePath, file, { upsert: true });

        if (storageError) throw storageError;

        // 2. Insert into experiment_versions table
        const nextVersion = (experiment.current_version?.version_number || 0) + 1;
        const { data: versionData, error: dbError } = await supabase
          .from('experiment_versions')
          .insert({
            experiment_id: experiment.id,
            version_number: nextVersion,
            storage_path: storagePath,
            filename: file.name,
            sha256: sha256,
          })
          .select()
          .single();

        if (dbError) throw dbError;

        onUploadSuccess(versionData);
      } else {
        // Demo mode fallback
        const mockVersion: ExperimentVersion = {
          id: `demo-ver-${Date.now()}`,
          experiment_id: experiment.id,
          version_number: (experiment.current_version?.version_number || 0) + 1,
          storage_path: `programs/${file.name}`,
          filename: file.name,
          sha256: sha256,
          created_at: new Date().toISOString(),
        };
        onUploadSuccess(mockVersion);
      }
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to publish version');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-xl w-full max-w-2xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
          <div>
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Upload className="w-4 h-4 text-rose-400" />
              Upload Source Code
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Experiment {experiment.experiment_number}: {experiment.title}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-md transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-5">
          {error && (
            <div className="flex items-center gap-2 p-3 text-xs text-rose-300 bg-rose-500/10 border border-rose-500/20 rounded-lg">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Drag & Drop Zone */}
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
              file
                ? 'border-emerald-500/50 bg-emerald-500/5'
                : 'border-slate-700 hover:border-slate-600 bg-slate-800/40'
            }`}
          >
            <input
              type="file"
              id="fileInput"
              className="hidden"
              onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
            />
            <label htmlFor="fileInput" className="cursor-pointer flex flex-col items-center">
              <FileCode className={`w-10 h-10 mb-3 ${file ? 'text-emerald-400' : 'text-slate-400'}`} />
              <p className="text-sm font-medium text-white mb-1">
                {file ? file.name : 'Click to select or drag and drop source file'}
              </p>
              <p className="text-xs text-slate-400">
                Supports .py, .java, .c, .cpp, .sql, .js, .txt (max 5MB)
              </p>
            </label>
          </div>

          {/* SHA-256 Checksum Card */}
          {sha256 && (
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center gap-1.5 font-medium text-slate-300">
                  <Hash className="w-3.5 h-3.5 text-rose-400" />
                  Calculated SHA-256 Checksum
                </span>
                <span className="text-emerald-400 flex items-center gap-1 font-mono">
                  <Check className="w-3.5 h-3.5" /> Verified
                </span>
              </div>
              <p className="font-mono text-xs text-slate-200 bg-slate-900 p-2 rounded border border-slate-800 break-all select-all">
                {sha256}
              </p>
            </div>
          )}

          {/* Code Preview */}
          {preview && (
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-300">Source Code Preview</label>
              <pre className="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs font-mono text-slate-300 max-h-48 overflow-y-auto whitespace-pre">
                {preview}
              </pre>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-slate-800 bg-slate-950/40 flex items-center justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handlePublish}
            disabled={!file || !sha256 || isUploading}
            className="px-4 py-2 text-xs font-medium bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white rounded-lg transition-colors flex items-center gap-2"
          >
            {isUploading ? (
              <span>Publishing...</span>
            ) : (
              <>
                <Check className="w-4 h-4" />
                <span>Publish Version</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
