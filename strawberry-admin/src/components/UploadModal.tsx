import React, { useState, useEffect } from 'react';
import type { Experiment, ExperimentVersion } from '../types';
import { calculateSHA256 } from '../lib/crypto';
import { supabase, isSupabaseConfigured, formatSupabaseError } from '../lib/supabase';
import { STARTER_TEMPLATES } from '../lib/codeTemplates';
import { VscWorkbenchModal } from './VscWorkbenchModal';

interface UploadModalProps {
  experiment: Experiment;
  subjectCode?: string;
  onClose: () => void;
  onUploadSuccess: (version: ExperimentVersion) => void;
}

const DEFAULT_BLANK_CODE =
  STARTER_TEMPLATES.find((t) => t.key === 'blank')?.code ||
  '# Write your source code below:\n';

export const UploadModal: React.FC<UploadModalProps> = ({
  experiment,
  subjectCode,
  onClose,
  onUploadSuccess,
}) => {
  const [code, setCode] = useState<string>('');
  const [filename, setFilename] = useState<string>(() => {
    if (experiment.current_version?.filename) {
      return experiment.current_version.filename;
    }
    const cleanTitle = experiment.title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');
    return `${cleanTitle || 'experiment'}.py`;
  });
  const [sha256, setSha256] = useState<string>('');
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isLoadingExisting, setIsLoadingExisting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Download latest published file into editor buffer when editing an existing program
  useEffect(() => {
    let isCancelled = false;

    const loadInitialCode = async () => {
      if (experiment.current_version?.storage_path && isSupabaseConfigured && supabase) {
        setIsLoadingExisting(true);
        try {
          const { data, error: dlError } = await supabase.storage
            .from('programs')
            .download(experiment.current_version.storage_path);
          if (dlError) throw dlError;
          if (data && !isCancelled) {
            const text = await data.text();
            setCode(text.replace(/\r\n/g, '\n').replace(/\r/g, '\n'));
            return;
          }
        } catch {
          // Fall back to starter template if initial storage download fails
        } finally {
          if (!isCancelled) setIsLoadingExisting(false);
        }
      }

      if (!isCancelled) {
        setCode((prev) => prev || DEFAULT_BLANK_CODE);
      }
    };

    loadInitialCode();
    return () => {
      isCancelled = true;
    };
  }, [experiment]);

  // Re-calculate SHA-256 live as user edits buffer
  useEffect(() => {
    let isCancelled = false;
    const compute = async () => {
      if (!code.trim()) {
        setSha256('');
        return;
      }
      try {
        const hash = await calculateSHA256(code);
        if (!isCancelled) setSha256(hash);
      } catch {
        if (!isCancelled) setError('Failed to compute SHA-256 digest');
      }
    };
    compute();
    return () => {
      isCancelled = true;
    };
  }, [code]);

  const handlePublish = async () => {
    if (!code.trim()) {
      setError('Cannot publish empty program code. Please write source code in the editor.');
      return;
    }

    const cleanFilename = filename.trim() || 'program.py';
    setIsUploading(true);
    setError(null);

    try {
      const computedSha = await calculateSHA256(code);
      setSha256(computedSha);
      const codeBlob = new Blob([code], { type: 'text/plain;charset=utf-8' });

      if (!isSupabaseConfigured || !supabase) {
        setError('Supabase is not configured. Connect your Supabase project before publishing.');
        return;
      }

      const storagePath = `programs/${experiment.id}/${cleanFilename}`;
      const { error: storageError } = await supabase.storage
        .from('programs')
        .upload(storagePath, codeBlob, {
          upsert: true,
          contentType: 'text/plain;charset=utf-8',
        });

      if (storageError) throw storageError;

      const nextVersion = (experiment.current_version?.version_number || 0) + 1;
      const { data: versionData, error: dbError } = await supabase
        .from('experiment_versions')
        .insert({
          experiment_id: experiment.id,
          version_number: nextVersion,
          storage_path: storagePath,
          filename: cleanFilename,
          sha256: computedSha,
        })
        .select()
        .single();

      if (dbError) throw dbError;
      onUploadSuccess(versionData);
      onClose();
    } catch (err: unknown) {
      setError(formatSupabaseError(err, 'Failed to publish code version to storage'));
    } finally {
      setIsUploading(false);
    }
  };

  const nextVerLabel = experiment.current_version
    ? `v${experiment.current_version.version_number + 1}.0`
    : 'v1.0';

  return (
    <VscWorkbenchModal
      mode="edit"
      windowTitle={`Strawberry IDE — ${experiment.title}`}
      submitLabel={`Publish ${nextVerLabel}`}
      isSubmitting={isUploading}
      isLoadingInitialCode={isLoadingExisting}
      error={error}
      programTitle={experiment.title}
      subjectCodeLabel={subjectCode}
      filename={filename}
      onFilenameChange={setFilename}
      code={code}
      onCodeChange={setCode}
      sha256={sha256}
      versionLabel={nextVerLabel}
      onClose={onClose}
      onSubmit={handlePublish}
    />
  );
};
