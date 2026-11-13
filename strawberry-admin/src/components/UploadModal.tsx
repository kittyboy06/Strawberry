import React, { useState, useEffect, useRef } from 'react';
import {
  X,
  Check,
  FileCode,
  Hash,
  AlertCircle,
  Edit3,
  UploadCloud,
  Copy,
  Sparkles,
  RotateCcw,
  Code2,
} from 'lucide-react';
import type { Experiment, ExperimentVersion } from '../types';
import { calculateSHA256 } from '../lib/crypto';
import { supabase, isSupabaseConfigured } from '../lib/supabase';

interface UploadModalProps {
  experiment: Experiment;
  onClose: () => void;
  onUploadSuccess: (version: ExperimentVersion) => void;
}

const STARTER_TEMPLATES: Record<string, { label: string; filename: string; code: string }> = {
  python_socket: {
    label: 'Python • Socket Server',
    filename: 'socket_server.py',
    code: `# TCP Echo Server - Socket Programming
import socket

HOST = '127.0.0.1'
PORT = 65432

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Server listening on {HOST}:{PORT}...")
        conn, addr = s.accept()
        with conn:
            print(f"[+] Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f"[>] Received: {data.decode().strip()}")
                conn.sendall(data)

if __name__ == '__main__':
    start_server()
`,
  },
  c_tcp: {
    label: 'C • TCP Client',
    filename: 'tcp_client.c',
    code: `// TCP Echo Client in C
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 65432
#define BUFFER_SIZE 1024

int main() {
    int sock = 0;
    struct sockaddr_in serv_addr;
    char buffer[BUFFER_SIZE] = {0};
    const char *hello = "Hello from Strawberry Lab Client!";

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        perror("Socket creation failed");
        return -1;
    }

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(PORT);

    if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0) {
        perror("Invalid address");
        return -1;
    }

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("Connection Failed");
        return -1;
    }

    send(sock, hello, strlen(hello), 0);
    printf("[+] Message sent to server\\n");
    read(sock, buffer, BUFFER_SIZE - 1);
    printf("[>] Server echo: %s\\n", buffer);

    close(sock);
    return 0;
}
`,
  },
  sql_schema: {
    label: 'SQL • Laboratory Schema',
    filename: 'laboratory_schema.sql',
    code: `-- University Laboratory Management Schema
CREATE TABLE IF NOT EXISTS students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    roll_number VARCHAR(20) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lab_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    program_title VARCHAR(100) NOT NULL,
    sha256_digest VARCHAR(64) NOT NULL,
    status VARCHAR(20) DEFAULT 'VERIFIED',
    submitted_at TIMESTAMPTZ DEFAULT NOW()
);

-- Query recent verified submissions
SELECT s.roll_number, s.full_name, sub.program_title, sub.sha256_digest
FROM students s
JOIN lab_submissions sub ON s.id = sub.student_id
ORDER BY sub.submitted_at DESC;
`,
  },
  blank: {
    label: 'Blank Script',
    filename: 'main.py',
    code: `# Laboratory Program Implementation
# Write or paste your source code directly below:

def execute_experiment():
    print("Program executed successfully.")

if __name__ == '__main__':
    execute_experiment()
`,
  },
};

export const UploadModal: React.FC<UploadModalProps> = ({
  experiment,
  onClose,
  onUploadSuccess,
}) => {
  // Mode: 'write' (in-webpage code editor) or 'import' (file upload/drop)
  const [mode, setMode] = useState<'write' | 'import'>('write');

  // Code editor states
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
  const [copiedSha, setCopiedSha] = useState<boolean>(false);
  const [copiedCode, setCopiedCode] = useState<boolean>(false);

  // File import state
  const [importedFile, setImportedFile] = useState<File | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // If the experiment already has an existing version, load its code into the web editor
  useEffect(() => {
    let isCancelled = false;

    const loadInitialCode = async () => {
      if (experiment.current_version?.storage_path && isSupabaseConfigured && supabase) {
        setIsLoadingExisting(true);
        try {
          const { data, error } = await supabase.storage
            .from('programs')
            .download(experiment.current_version.storage_path);
          if (error) throw error;
          if (data && !isCancelled) {
            const text = await data.text();
            setCode(text);
            return;
          }
        } catch {
          // If storage download fails, fall back to blank template
        } finally {
          if (!isCancelled) setIsLoadingExisting(false);
        }
      }

      // Default initial template if no existing version
      if (!isCancelled) {
        setCode((prev) => prev || STARTER_TEMPLATES.blank.code);
      }
    };

    loadInitialCode();
    return () => {
      isCancelled = true;
    };
  }, [experiment]);

  // Re-calculate SHA-256 whenever code changes
  useEffect(() => {
    let isCancelled = false;
    const compute = async () => {
      if (!code.trim()) {
        setSha256('');
        return;
      }
      try {
        const hash = await calculateSHA256(code);
        if (!isCancelled) {
          setSha256(hash);
        }
      } catch {
        if (!isCancelled) setError('Failed to calculate SHA-256 digest');
      }
    };
    compute();
    return () => {
      isCancelled = true;
    };
  }, [code]);

  // Support Tab key indentation inside textarea
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const target = e.currentTarget;
      const start = target.selectionStart;
      const end = target.selectionEnd;
      const spaces = '    ';
      const newCode = code.substring(0, start) + spaces + code.substring(end);
      setCode(newCode);
      setTimeout(() => {
        target.selectionStart = target.selectionEnd = start + spaces.length;
      }, 0);
    }
  };

  // Load a starter template
  const handleSelectTemplate = (templateKey: string) => {
    const tpl = STARTER_TEMPLATES[templateKey];
    if (!tpl) return;
    if (code.trim() && !window.confirm('Replace current editor code with template?')) {
      return;
    }
    setCode(tpl.code);
    setFilename(tpl.filename);
  };

  // Extension quick-selector
  const handleSetExtension = (ext: string) => {
    const dotIndex = filename.lastIndexOf('.');
    const base = dotIndex !== -1 ? filename.substring(0, dotIndex) : filename;
    setFilename(`${base || 'program'}${ext}`);
  };

  // Handle file import into editor
  const handleFileImport = (selectedFile: File) => {
    setError(null);
    setImportedFile(selectedFile);
    setFilename(selectedFile.name);

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = (e.target?.result as string) || '';
      setCode(content);
      setMode('write'); // Switch straight to write mode so user can see and edit the code directly
    };
    reader.onerror = () => {
      setError('Could not read file from disk');
    };
    reader.readAsText(selectedFile);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileImport(e.dataTransfer.files[0]);
    }
  };

  // Publish to Supabase Storage & Database
  const handlePublish = async () => {
    if (!code.trim()) {
      setError('Cannot publish empty program code. Please write your program below.');
      return;
    }

    const cleanFilename = filename.trim() || 'program.py';
    setIsUploading(true);
    setError(null);

    try {
      const computedSha = await calculateSHA256(code);
      setSha256(computedSha);

      // Create a Blob from the direct code text
      const codeBlob = new Blob([code], { type: 'text/plain;charset=utf-8' });

      if (isSupabaseConfigured && supabase) {
        // 1. Upload to Supabase Storage bucket 'programs'
        const storagePath = `programs/${experiment.id}/${cleanFilename}`;
        const { error: storageError } = await supabase.storage
          .from('programs')
          .upload(storagePath, codeBlob, {
            upsert: true,
            contentType: 'text/plain;charset=utf-8',
          });

        if (storageError) throw storageError;

        // 2. Insert into experiment_versions table
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
      } else {
        // Local Standalone Mode
        const mockVersion: ExperimentVersion = {
          id: `local-ver-${Date.now()}`,
          experiment_id: experiment.id,
          version_number: (experiment.current_version?.version_number || 0) + 1,
          storage_path: `programs/${cleanFilename}`,
          filename: cleanFilename,
          sha256: computedSha,
          created_at: new Date().toISOString(),
        };
        onUploadSuccess(mockVersion);
      }
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to publish code version to storage');
    } finally {
      setIsUploading(false);
    }
  };

  const lineCount = code.split('\n').length;
  const byteSize = new TextEncoder().encode(code).length;

  return (
    <div className="fixed inset-0 z-50 bg-[#2E1E24]/50 backdrop-blur-xs flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
      <div className="bg-[#FFFFFF] border border-[#F5E8EB] rounded-2xl w-full max-w-4xl overflow-hidden shadow-2xl flex flex-col max-h-[92vh] my-auto">
        {/* Header */}
        <div className="px-6 py-4 border-b border-[#F5E8EB] flex items-center justify-between bg-[#FFF9FA]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-[#FDE8EC] text-[#BE123C] flex items-center justify-center border border-[#FDE2E7]">
              <Code2 className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-serif font-bold text-[#2E1E24]">
                  In-Browser Code Authoring
                </h2>
                <span className="bg-[#FFF0F3] text-[#BE123C] border border-[#FDE2E7] text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">
                  {experiment.current_version ? `v${experiment.current_version.version_number + 1}.0` : 'v1.0'}
                </span>
              </div>
              <p className="text-xs text-[#8C6D76]">
                Target Experiment: <span className="font-semibold text-[#2E1E24]">{experiment.title}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Mode Switch Tabs */}
            <div className="flex items-center bg-[#FAF3F5] border border-[#F2DEE3] p-0.5 rounded-xl text-xs font-medium">
              <button
                type="button"
                onClick={() => setMode('write')}
                className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all cursor-pointer ${
                  mode === 'write'
                    ? 'bg-[#BE123C] text-white shadow-xs font-semibold'
                    : 'text-[#4B3840] hover:text-[#BE123C]'
                }`}
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span>Write Code Directly</span>
              </button>
              <button
                type="button"
                onClick={() => setMode('import')}
                className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-all cursor-pointer ${
                  mode === 'import'
                    ? 'bg-[#BE123C] text-white shadow-xs font-semibold'
                    : 'text-[#4B3840] hover:text-[#BE123C]'
                }`}
              >
                <UploadCloud className="w-3.5 h-3.5" />
                <span>Import File</span>
              </button>
            </div>

            <button
              onClick={onClose}
              className="text-[#8C6D76] hover:text-[#2E1E24] p-1.5 rounded-full hover:bg-[#FDF0F3] transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-5 sm:p-6 overflow-y-auto space-y-4 flex-1">
          {/* Error Message */}
          {error && (
            <div className="p-3 bg-[#FEF2F2] border border-[#FCA5A5] rounded-xl text-xs text-[#991B1B] flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* MODE 1: WRITE CODE DIRECTLY IN WEBPAGE */}
          {mode === 'write' && (
            <div className="space-y-4">
              {/* Filename & Quick Extensions & Template Bar */}
              <div className="bg-[#FAF3F5] border border-[#F2DEE3] p-3.5 rounded-xl space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex-1 flex items-center gap-2">
                    <span className="text-xs font-medium text-[#4B3840] whitespace-nowrap">File Name:</span>
                    <input
                      type="text"
                      value={filename}
                      onChange={(e) => setFilename(e.target.value)}
                      placeholder="e.g. socket_server.py"
                      className="w-full sm:max-w-xs bg-white border border-[#E5D5DA] rounded-lg px-2.5 py-1.5 text-xs font-mono text-[#2E1E24] focus:outline-none focus:border-[#BE123C]"
                    />
                    {/* Quick Extensions */}
                    <div className="hidden sm:flex items-center gap-1">
                      {['.py', '.c', '.cpp', '.java', '.sql'].map((ext) => (
                        <button
                          key={ext}
                          type="button"
                          onClick={() => handleSetExtension(ext)}
                          className={`text-[10px] font-mono px-2 py-1 rounded-md border transition-colors cursor-pointer ${
                            filename.endsWith(ext)
                              ? 'bg-[#BE123C] text-white border-[#BE123C]'
                              : 'bg-white text-[#4B3840] border-[#E5D5DA] hover:border-[#BE123C]'
                          }`}
                        >
                          {ext}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Starter Templates */}
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-[#BE123C]" />
                    <span className="text-xs font-medium text-[#4B3840] whitespace-nowrap">Load Template:</span>
                    <select
                      onChange={(e) => handleSelectTemplate(e.target.value)}
                      defaultValue=""
                      className="bg-white border border-[#E5D5DA] rounded-lg px-2.5 py-1.5 text-xs text-[#2E1E24] focus:outline-none focus:border-[#BE123C] cursor-pointer"
                    >
                      <option value="" disabled>Choose boilerplate...</option>
                      {Object.entries(STARTER_TEMPLATES).map(([key, tpl]) => (
                        <option key={key} value={key}>
                          {tpl.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Code Editor Container */}
              <div className="relative border border-[#3E2B33] rounded-2xl overflow-hidden bg-[#181216] shadow-inner">
                {/* Editor Top Bar */}
                <div className="bg-[#241A21] px-4 py-2 border-b border-[#3E2B33] flex items-center justify-between text-xs font-mono text-[#C9BAC2]">
                  <div className="flex items-center gap-2">
                    <FileCode className="w-3.5 h-3.5 text-[#BE123C]" />
                    <span className="text-white font-semibold">{filename}</span>
                    <span className="text-[10px] text-[#93818C]">
                      ({lineCount} lines • {(byteSize / 1024).toFixed(2)} KB)
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        navigator.clipboard.writeText(code);
                        setCopiedCode(true);
                        setTimeout(() => setCopiedCode(false), 2000);
                      }}
                      className="hover:text-white flex items-center gap-1 text-[11px] cursor-pointer transition-colors"
                      title="Copy code to clipboard"
                    >
                      {copiedCode ? <Check className="w-3.5 h-3.5 text-[#10B981]" /> : <Copy className="w-3.5 h-3.5" />}
                      <span>{copiedCode ? 'Copied' : 'Copy'}</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => setCode('')}
                      className="hover:text-[#F87171] flex items-center gap-1 text-[11px] cursor-pointer transition-colors"
                      title="Clear editor"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                      <span>Clear</span>
                    </button>
                  </div>
                </div>

                {/* Editor Body with Line Numbers */}
                <div className="flex font-mono text-xs leading-relaxed max-h-[380px] min-h-[260px] overflow-hidden">
                  {/* Line Numbers Gutter */}
                  <div className="w-12 py-3 bg-[#1F171D] text-[#7A6773] select-none text-right pr-3 border-r border-[#33222B] overflow-hidden shrink-0">
                    {Array.from({ length: Math.max(lineCount, 12) }).map((_, i) => (
                      <div key={i} className="leading-6">
                        {i + 1}
                      </div>
                    ))}
                  </div>

                  {/* Textarea Code Input */}
                  <div className="relative flex-1 overflow-auto">
                    <textarea
                      ref={textareaRef}
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="# Write your program directly in this editor...&#10;# (Press Tab to indent 4 spaces)"
                      spellCheck={false}
                      className="w-full h-full min-h-[260px] py-3 px-4 bg-transparent text-[#FDEBED] resize-none focus:outline-none font-mono text-xs leading-6 selection:bg-[#BE123C]/50"
                    />
                  </div>
                </div>
              </div>

              {/* Real-time Cryptographic Digest */}
              <div className="bg-[#FFF9FA] border border-[#F5E8EB] p-3.5 rounded-xl space-y-1.5 font-mono">
                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5 text-xs text-[#2E1E24] font-sans font-medium">
                    <Hash className="w-3.5 h-3.5 text-[#BE123C]" />
                    <span>Real-time SHA-256 Digest (Hardware Verified)</span>
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-[#059669] flex items-center gap-1 font-sans font-semibold text-xs">
                      <Check className="w-3 h-3" /> Live Synced
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        if (sha256) {
                          navigator.clipboard.writeText(sha256);
                          setCopiedSha(true);
                          setTimeout(() => setCopiedSha(false), 2000);
                        }
                      }}
                      className="text-[#BE123C] hover:underline text-[11px] font-sans font-medium cursor-pointer"
                    >
                      {copiedSha ? 'Copied!' : 'Copy Hash'}
                    </button>
                  </div>
                </div>
                <div className="text-xs text-[#BE123C] break-all select-all bg-[#FFFFFF] p-2.5 rounded-lg border border-[#F5E8EB]">
                  {sha256 || 'Type code in editor above to compute instant SHA-256 hash...'}
                </div>
              </div>
            </div>
          )}

          {/* MODE 2: IMPORT EXISTING FILE */}
          {mode === 'import' && (
            <div className="space-y-4">
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
                  importedFile
                    ? 'border-[#BE123C] bg-[#FFF0F3]'
                    : 'border-[#F5D5DC] hover:border-[#BE123C] bg-[#FFF9FA] hover:bg-[#FFF0F3]'
                }`}
                onClick={() => document.getElementById('modal-file-upload')?.click()}
              >
                <input
                  id="modal-file-upload"
                  type="file"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleFileImport(e.target.files[0]);
                    }
                  }}
                />
                <div className="flex flex-col items-center justify-center space-y-3">
                  <div className="w-12 h-12 rounded-full bg-[#FFE4E8] flex items-center justify-center text-[#BE123C]">
                    <UploadCloud className="w-6 h-6" />
                  </div>
                  <div className="text-sm font-medium text-[#2E1E24]">
                    {importedFile ? (
                      <span className="text-[#BE123C] font-semibold">{importedFile.name}</span>
                    ) : (
                      'Click to select a file or drag & drop here'
                    )}
                  </div>
                  <p className="text-xs text-[#8C6D76]">
                    Supported extensions: .py, .c, .cpp, .java, .sql, .js, .ts
                  </p>
                  <p className="text-[11px] text-[#BE123C] font-medium">
                    Selecting a file will immediately load its text into the in-webpage editor!
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-[#F5E8EB] bg-[#FFF9FA] flex items-center justify-between">
          <div className="text-xs text-[#8C6D76]">
            {isLoadingExisting ? (
              <span className="italic">Loading existing version source...</span>
            ) : (
              <span>Changes sync immediately to campus workstations via <code className="font-mono text-[#BE123C]">strawberry pull</code></span>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium text-[#6B7280] hover:text-[#2E1E24] hover:bg-[#F5E8EB] transition-colors cursor-pointer"
              disabled={isUploading}
            >
              Cancel
            </button>
            <button
              onClick={handlePublish}
              disabled={!code.trim() || !sha256 || isUploading}
              className={`px-5 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all ${
                !code.trim() || !sha256 || isUploading
                  ? 'bg-[#F5E8EB] text-[#A89CA0] cursor-not-allowed'
                  : 'bg-[#BE123C] hover:bg-[#9F1239] text-white shadow-sm cursor-pointer'
              }`}
            >
              {isUploading ? (
                <span>Publishing to Storage...</span>
              ) : (
                <>
                  <Check className="w-4 h-4" />
                  <span>Publish Version ({experiment.current_version ? `v${experiment.current_version.version_number + 1}.0` : 'v1.0'})</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
