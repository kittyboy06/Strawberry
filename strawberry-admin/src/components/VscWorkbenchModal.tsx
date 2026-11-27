import React, { useState, useRef, useMemo } from 'react';
import {
  X,
  Check,
  Copy,
  Files,
  Sparkles,
  ShieldCheck,
  ChevronDown,
  ChevronRight,
  Maximize2,
  Minimize2,
  UploadCloud,
  RotateCcw,
  PanelLeft,
  AlertCircle,
  Hash,
  FileCode2,
} from 'lucide-react';
import type { Subject } from '../types';
import {
  STARTER_TEMPLATES,
  detectLanguageMeta,
  highlightLineTokens,
} from '../lib/codeTemplates';

interface VscWorkbenchModalProps {
  mode: 'create' | 'edit';
  windowTitle: string;
  submitLabel: string;
  isSubmitting: boolean;
  isLoadingInitialCode?: boolean;
  error: string | null;

  // Program Metadata (editable in 'create' mode, displayed readonly in 'edit' mode)
  subjects?: Subject[];
  subjectId?: string;
  onSubjectIdChange?: (val: string) => void;
  programTitle: string;
  onProgramTitleChange?: (val: string) => void;
  programDescription?: string;
  onProgramDescriptionChange?: (val: string) => void;
  subjectCodeLabel?: string;

  // Code Authoring Control
  includeCode?: boolean;
  onIncludeCodeChange?: (val: boolean) => void;
  filename: string;
  onFilenameChange: (val: string) => void;
  code: string;
  onCodeChange: (val: string) => void;
  sha256: string;
  versionLabel: string;

  onClose: () => void;
  onSubmit: () => void | Promise<void>;
}

const CODE_FONT_STYLE: React.CSSProperties = {
  fontFamily: "'Cascadia Code', 'Fira Code', Consolas, 'Courier New', monospace",
  fontSize: '13.5px',
  lineHeight: '22px',
  letterSpacing: '0px',
  fontVariantLigatures: 'none',
  fontFeatureSettings: '"liga" 0, "calt" 0',
  tabSize: 4,
};

const LINE_HEIGHT_PX = 22;

export const VscWorkbenchModal: React.FC<VscWorkbenchModalProps> = ({
  mode,
  windowTitle,
  submitLabel,
  isSubmitting,
  isLoadingInitialCode = false,
  error,
  subjects = [],
  subjectId = '',
  onSubjectIdChange,
  programTitle,
  onProgramTitleChange,
  programDescription = '',
  onProgramDescriptionChange,
  subjectCodeLabel,
  includeCode = true,
  onIncludeCodeChange,
  filename,
  onFilenameChange,
  code,
  onCodeChange,
  sha256,
  versionLabel,
  onClose,
  onSubmit,
}) => {
  const [activityTab, setActivityTab] = useState<'explorer' | 'templates' | 'integrity'>('explorer');
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [isFolderOpen, setIsFolderOpen] = useState<boolean>(true);
  const [cursorPos, setCursorPos] = useState<{ line: number; col: number }>({ line: 1, col: 1 });
  const [copiedCode, setCopiedCode] = useState<boolean>(false);
  const [copiedSha, setCopiedSha] = useState<boolean>(false);
  const [importedName, setImportedName] = useState<string | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const normalizedCode = useMemo(
    () => code.replace(/\r\n/g, '\n').replace(/\r/g, '\n'),
    [code]
  );
  const lines = useMemo(() => normalizedCode.split('\n'), [normalizedCode]);
  const byteSize = useMemo(() => new TextEncoder().encode(normalizedCode).length, [normalizedCode]);
  const langMeta = useMemo(() => detectLanguageMeta(filename), [filename]);

  const resolvedSubjectCode = useMemo(() => {
    if (subjectCodeLabel) return subjectCodeLabel;
    const found = subjects.find((s) => s.id === subjectId);
    return found ? found.subject_code : 'LAB';
  }, [subjectCodeLabel, subjects, subjectId]);

  const highlightedLines = useMemo(
    () => lines.map((ln) => highlightLineTokens(ln, filename)),
    [lines, filename]
  );

  const handleActivityClick = (tab: 'explorer' | 'templates' | 'integrity') => {
    if (activityTab === tab) {
      setIsSidebarOpen((prev) => !prev);
    } else {
      setActivityTab(tab);
      setIsSidebarOpen(true);
    }
  };

  const ensureCaretVisible = (line: number, col: number) => {
    const container = scrollContainerRef.current;
    if (!container) return;

    const caretTop = 12 + (line - 1) * LINE_HEIGHT_PX;
    const caretBottom = caretTop + LINE_HEIGHT_PX;

    if (caretTop < container.scrollTop + 8) {
      container.scrollTop = Math.max(0, caretTop - 12);
    } else if (caretBottom > container.scrollTop + container.clientHeight - 20) {
      container.scrollTop = caretBottom - container.clientHeight + 28;
    }

    const approxCharWidth = 8.15;
    const caretX = (col - 1) * approxCharWidth;
    const visibleCodeWidth = container.clientWidth - 56 - 32;
    if (caretX < container.scrollLeft) {
      container.scrollLeft = Math.max(0, caretX - 24);
    } else if (visibleCodeWidth > 0 && caretX > container.scrollLeft + visibleCodeWidth) {
      container.scrollLeft = caretX - visibleCodeWidth + 48;
    }
  };

  const updateCursor = (ta: HTMLTextAreaElement, autoScroll = true) => {
    const pos = ta.selectionStart || 0;
    const before = ta.value.slice(0, pos);
    const split = before.split('\n');
    const nextPos = {
      line: split.length,
      col: split[split.length - 1].length + 1,
    };
    setCursorPos(nextPos);
    if (autoScroll) {
      ensureCaretVisible(nextPos.line, nextPos.col);
    }
  };

  const handleEditorKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl/Cmd + S saves & publishes
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
      e.preventDefault();
      if (!isSubmitting) onSubmit();
      return;
    }

    // Ctrl/Cmd + B toggles sidebar just like VS Code
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
      e.preventDefault();
      setIsSidebarOpen((prev) => !prev);
      return;
    }

    if (e.key === 'Tab') {
      e.preventDefault();
      const target = e.currentTarget;
      const start = target.selectionStart;
      const end = target.selectionEnd;

      if (e.shiftKey) {
        // Outdent current line by up to 4 spaces
        const lineStart = normalizedCode.lastIndexOf('\n', start - 1) + 1;
        const lineText = normalizedCode.slice(lineStart, end);
        const match = lineText.match(/^ {1,4}/);
        if (match) {
          const removeLen = match[0].length;
          const next = normalizedCode.slice(0, lineStart) + normalizedCode.slice(lineStart + removeLen);
          onCodeChange(next);
          setTimeout(() => {
            target.selectionStart = target.selectionEnd = Math.max(lineStart, start - removeLen);
            updateCursor(target);
          }, 0);
        }
        return;
      }

      const spaces = '    ';
      const nextCode = normalizedCode.substring(0, start) + spaces + normalizedCode.substring(end);
      onCodeChange(nextCode);
      setTimeout(() => {
        target.selectionStart = target.selectionEnd = start + spaces.length;
        updateCursor(target);
      }, 0);
    }
  };

  const handleExtensionClick = (ext: string) => {
    const dotIdx = filename.lastIndexOf('.');
    const base = dotIdx !== -1 ? filename.substring(0, dotIdx) : filename;
    onFilenameChange(`${base || 'program'}${ext}`);
  };

  const handleLoadTemplate = (tplCode: string, tplFilename: string) => {
    if (
      code.trim() &&
      code.trim() !== tplCode.trim() &&
      !window.confirm('Replace current editor buffer with this boilerplate template?')
    ) {
      return;
    }
    onCodeChange(tplCode);
    if (mode === 'create' || !filename.trim()) {
      onFilenameChange(tplFilename);
    }
    if (!includeCode && onIncludeCodeChange) {
      onIncludeCodeChange(true);
    }
  };

  const handleFileImport = (selectedFile: File) => {
    setImportedName(selectedFile.name);
    onFilenameChange(selectedFile.name);
    const reader = new FileReader();
    reader.onload = (ev) => {
      onCodeChange((ev.target?.result as string) || '');
      if (!includeCode && onIncludeCodeChange) {
        onIncludeCodeChange(true);
      }
      setActivityTab('explorer');
    };
    reader.readAsText(selectedFile);
  };

  const canSubmit =
    !isSubmitting &&
    (mode === 'edit' ? Boolean(code.trim() && sha256) : Boolean(programTitle.trim() && subjectId && (!includeCode || code.trim())));

  return (
    <div
      className={`fixed inset-0 z-50 bg-[#0B080A]/75 backdrop-blur-xs flex items-center justify-center ${
        isFullscreen ? 'p-0' : 'p-2 sm:p-4'
      }`}
    >
      <div
        className={`bg-[#1E1E1E] text-[#CCCCCC] border border-[#323233] flex flex-col overflow-hidden shadow-[0_24px_80px_rgba(0,0,0,0.65)] transition-all ${
          isFullscreen ? 'w-screen h-screen rounded-none' : 'w-[96vw] max-w-[1440px] h-[90vh] rounded-xl'
        }`}
      >
        {/* 1. VS CODE TITLE BAR */}
        <div className="h-10 bg-[#181818] border-b border-[#2B2B2B] px-3.5 flex items-center justify-between select-none shrink-0">
          {/* Left: Window Dots + Title */}
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex items-center gap-1.5 shrink-0">
              <button
                type="button"
                onClick={onClose}
                title="Close Workbench"
                className="w-3 h-3 rounded-full bg-[#FF5F56] hover:brightness-110 cursor-pointer"
              />
              <button
                type="button"
                onClick={() => setIsSidebarOpen((s) => !s)}
                title="Toggle Side Bar (Ctrl+B)"
                className="w-3 h-3 rounded-full bg-[#FFBD2E] hover:brightness-110 cursor-pointer"
              />
              <button
                type="button"
                onClick={() => setIsFullscreen((f) => !f)}
                title={isFullscreen ? 'Restore Window' : 'Maximize Workbench'}
                className="w-3 h-3 rounded-full bg-[#27C93F] hover:brightness-110 cursor-pointer"
              />
            </div>

            <div className="flex items-center gap-2 min-w-0">
              <FileCode2 className="w-4 h-4 text-[#F43F5E] shrink-0" />
              <span className="text-xs font-medium text-[#D4D4D4] truncate">{windowTitle}</span>
              <span className="hidden sm:inline-block text-[10px] font-mono bg-[#2D2D30] text-[#F43F5E] border border-[#3E3E42] px-1.5 py-0.5 rounded">
                {versionLabel}
              </span>
            </div>
          </div>

          {/* Center: Workspace Command Bar Pill */}
          <div className="hidden lg:flex items-center gap-2 bg-[#252526] border border-[#3C3C3C] rounded-md px-3 py-1 text-[11px] font-mono text-[#A0A0A0] max-w-md truncate">
            <span className="text-[#3794FF]">STRAWBERRY-IDE</span>
            <span>—</span>
            <span className="text-[#CCCCCC] truncate">
              {resolvedSubjectCode} / {filename || 'main.py'}
            </span>
          </div>

          {/* Right: Publish & Window Controls */}
          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={onSubmit}
              disabled={!canSubmit}
              className={`px-3 py-1.5 rounded text-xs font-medium flex items-center gap-1.5 transition-colors ${
                canSubmit
                  ? 'bg-[#0E639C] hover:bg-[#1177BB] text-white cursor-pointer'
                  : 'bg-[#2D2D30] text-[#6E6E6E] cursor-not-allowed'
              }`}
              title="Ctrl+S"
            >
              <Check className="w-3.5 h-3.5" />
              <span>{isSubmitting ? 'Publishing...' : submitLabel}</span>
            </button>

            <button
              type="button"
              onClick={() => setIsFullscreen((f) => !f)}
              className="p-1.5 rounded text-[#A0A0A0] hover:text-white hover:bg-[#2A2D2E] cursor-pointer"
              title={isFullscreen ? 'Exit Fullscreen' : 'Maximize Popup'}
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>

            <button
              type="button"
              onClick={onClose}
              className="p-1.5 rounded text-[#A0A0A0] hover:text-white hover:bg-[#C42B1C] cursor-pointer transition-colors"
              title="Close (Esc)"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* 2. WORKBENCH BODY */}
        <div className="flex-1 flex min-h-0 overflow-hidden">
          {/* Activity Bar */}
          <aside className="w-12 bg-[#181818] border-r border-[#2B2B2B] flex flex-col items-center py-2 justify-between shrink-0 select-none">
            <div className="flex flex-col items-center w-full gap-1">
              <button
                type="button"
                onClick={() => handleActivityClick('explorer')}
                title="Explorer & Program Config"
                className={`w-full py-2.5 flex items-center justify-center border-l-2 cursor-pointer transition-colors ${
                  isSidebarOpen && activityTab === 'explorer'
                    ? 'border-[#007ACC] text-white bg-[#252526]/60'
                    : 'border-transparent text-[#858585] hover:text-white'
                }`}
              >
                <Files className="w-5 h-5" />
              </button>

              <button
                type="button"
                onClick={() => handleActivityClick('templates')}
                title="Starter Boilerplates"
                className={`w-full py-2.5 flex items-center justify-center border-l-2 cursor-pointer transition-colors ${
                  isSidebarOpen && activityTab === 'templates'
                    ? 'border-[#007ACC] text-white bg-[#252526]/60'
                    : 'border-transparent text-[#858585] hover:text-white'
                }`}
              >
                <Sparkles className="w-5 h-5" />
              </button>

              <button
                type="button"
                onClick={() => handleActivityClick('integrity')}
                title="SHA-256 Digest & Import File"
                className={`w-full py-2.5 flex items-center justify-center border-l-2 cursor-pointer transition-colors ${
                  isSidebarOpen && activityTab === 'integrity'
                    ? 'border-[#007ACC] text-white bg-[#252526]/60'
                    : 'border-transparent text-[#858585] hover:text-white'
                }`}
              >
                <ShieldCheck className="w-5 h-5" />
              </button>
            </div>

            <button
              type="button"
              onClick={() => setIsSidebarOpen((s) => !s)}
              title="Toggle Primary Side Bar (Ctrl+B)"
              className="w-full py-2.5 flex items-center justify-center text-[#858585] hover:text-white cursor-pointer"
            >
              <PanelLeft className="w-4 h-4" />
            </button>
          </aside>

          {/* Primary Side Bar */}
          {isSidebarOpen && (
            <aside className="w-72 md:w-80 bg-[#252526] border-r border-[#2B2B2B] flex flex-col shrink-0 overflow-y-auto">
              {/* Side Bar View Header */}
              <div className="px-4 py-2 text-[11px] font-semibold tracking-wider text-[#BBBBBB] uppercase border-b border-[#2B2B2B] flex items-center justify-between shrink-0">
                <span>
                  {activityTab === 'explorer' && 'Explorer'}
                  {activityTab === 'templates' && 'Code Boilerplates'}
                  {activityTab === 'integrity' && 'Integrity & File Import'}
                </span>
              </div>

              {/* EXPLORER TAB */}
              {activityTab === 'explorer' && (
                <div className="text-xs flex-1 flex flex-col">
                  {/* Collapsible Workspace Tree */}
                  <button
                    type="button"
                    onClick={() => setIsFolderOpen((o) => !o)}
                    className="w-full px-2.5 py-1.5 bg-[#2D2D30]/60 text-[11px] font-bold text-[#CCCCCC] uppercase tracking-wide flex items-center gap-1 cursor-pointer hover:bg-[#2A2D2E]"
                  >
                    {isFolderOpen ? (
                      <ChevronDown className="w-3.5 h-3.5" />
                    ) : (
                      <ChevronRight className="w-3.5 h-3.5" />
                    )}
                    <span>STRAWBERRY-WORKSPACE</span>
                  </button>

                  {isFolderOpen && (
                    <div className="px-2 py-1.5 border-b border-[#2B2B2B]">
                      <div className="flex items-center gap-2 px-2.5 py-1.5 rounded bg-[#37373D] text-white font-mono text-xs">
                        <span
                          className="text-[9px] font-bold px-1 py-0.2 rounded text-white shrink-0"
                          style={{ backgroundColor: langMeta.color }}
                        >
                          {langMeta.badge}
                        </span>
                        <span className="truncate">{filename || 'main.py'}</span>
                        <span className="ml-auto text-[10px] text-[#3794FF]">M</span>
                      </div>
                    </div>
                  )}

                  {/* Metadata & File Properties Form */}
                  <div className="p-3.5 space-y-3.5 text-xs">
                    {mode === 'create' ? (
                      <>
                        <div>
                          <label className="block text-[11px] text-[#A0A0A0] mb-1">Target Subject *</label>
                          <select
                            value={subjectId}
                            onChange={(e) => onSubjectIdChange?.(e.target.value)}
                            className="w-full bg-[#3C3C3C] border border-[#3C3C3C] focus:border-[#007ACC] rounded px-2.5 py-1.5 text-xs text-[#E5E5E5] focus:outline-none cursor-pointer"
                            required
                          >
                            <option value="">Select Course...</option>
                            {subjects.map((s) => (
                              <option key={s.id} value={s.id}>
                                {s.subject_code} — {s.subject_name}
                              </option>
                            ))}
                          </select>
                        </div>

                        <div>
                          <label className="block text-[11px] text-[#A0A0A0] mb-1">Program Title *</label>
                          <input
                            type="text"
                            value={programTitle}
                            onChange={(e) => onProgramTitleChange?.(e.target.value)}
                            placeholder="e.g. Socket Programming"
                            className="w-full bg-[#3C3C3C] border border-[#3C3C3C] focus:border-[#007ACC] rounded px-2.5 py-1.5 text-xs text-[#E5E5E5] placeholder-[#858585] focus:outline-none"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-[11px] text-[#A0A0A0] mb-1">Brief Description</label>
                          <input
                            type="text"
                            value={programDescription}
                            onChange={(e) => onProgramDescriptionChange?.(e.target.value)}
                            placeholder="e.g. Echo server in Python"
                            className="w-full bg-[#3C3C3C] border border-[#3C3C3C] focus:border-[#007ACC] rounded px-2.5 py-1.5 text-xs text-[#E5E5E5] placeholder-[#858585] focus:outline-none"
                          />
                        </div>

                        {onIncludeCodeChange && (
                          <label className="flex items-start gap-2 p-2.5 rounded bg-[#1E1E1E] border border-[#323233] cursor-pointer">
                            <input
                              type="checkbox"
                              checked={includeCode}
                              onChange={(e) => onIncludeCodeChange(e.target.checked)}
                              className="mt-0.5 accent-[#007ACC] cursor-pointer"
                            />
                            <span className="text-[11px] text-[#CCCCCC] leading-snug">
                              Publish editor code immediately as <code className="text-[#4EC9B0]">v1.0</code>
                            </span>
                          </label>
                        )}
                      </>
                    ) : (
                      <div className="p-2.5 rounded bg-[#1E1E1E] border border-[#323233] space-y-1">
                        <div className="text-[10px] uppercase tracking-wider text-[#858585]">Target Program</div>
                        <div className="text-xs font-semibold text-white">{programTitle}</div>
                        <div className="text-[11px] font-mono text-[#4EC9B0]">Release target: {versionLabel}</div>
                      </div>
                    )}

                    {/* File Name & Language Extensions */}
                    <div className="space-y-2 pt-1 border-t border-[#2B2B2B]">
                      <label className="block text-[11px] text-[#A0A0A0]">Source Filename</label>
                      <input
                        type="text"
                        value={filename}
                        onChange={(e) => onFilenameChange(e.target.value)}
                        placeholder="main.py"
                        className="w-full bg-[#3C3C3C] border border-[#3C3C3C] focus:border-[#007ACC] rounded px-2.5 py-1.5 text-xs font-mono text-white focus:outline-none"
                      />
                      <div className="flex flex-wrap gap-1">
                        {['.py', '.c', '.cpp', '.java', '.sql', '.pl'].map((ext) => (
                          <button
                            key={ext}
                            type="button"
                            onClick={() => handleExtensionClick(ext)}
                            className={`text-[10px] font-mono px-2 py-0.5 rounded border transition-colors cursor-pointer ${
                              filename.endsWith(ext)
                                ? 'bg-[#0E639C] text-white border-[#007ACC]'
                                : 'bg-[#1E1E1E] text-[#A0A0A0] border-[#3C3C3C] hover:text-white'
                            }`}
                          >
                            {ext}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Quick Starter Switcher */}
                    <div className="space-y-1.5 pt-2 border-t border-[#2B2B2B]">
                      <div className="text-[11px] text-[#A0A0A0] flex items-center justify-between">
                        <span>Quick Snippets</span>
                        <button
                          type="button"
                          onClick={() => setActivityTab('templates')}
                          className="text-[#3794FF] hover:underline text-[10px] cursor-pointer"
                        >
                          All Templates →
                        </button>
                      </div>
                      <div className="space-y-1">
                        {STARTER_TEMPLATES.slice(0, 3).map((tpl) => (
                          <button
                            key={tpl.key}
                            type="button"
                            onClick={() => handleLoadTemplate(tpl.code, tpl.filename)}
                            className="w-full text-left px-2.5 py-1.5 rounded bg-[#1E1E1E] hover:bg-[#2A2D2E] border border-[#2B2B2B] text-[11px] text-[#CCCCCC] hover:text-white transition-colors cursor-pointer truncate"
                          >
                            {tpl.label}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TEMPLATES TAB */}
              {activityTab === 'templates' && (
                <div className="p-3 space-y-2 text-xs">
                  <p className="text-[11px] text-[#969696] pb-1">
                    Click a starter boilerplate to load it directly into the active editor:
                  </p>
                  {STARTER_TEMPLATES.map((tpl) => (
                    <button
                      key={tpl.key}
                      type="button"
                      onClick={() => handleLoadTemplate(tpl.code, tpl.filename)}
                      className="w-full text-left p-2.5 rounded bg-[#1E1E1E] hover:bg-[#2A2D2E] border border-[#323233] hover:border-[#007ACC] transition-colors cursor-pointer space-y-1"
                    >
                      <div className="font-medium text-white text-xs">{tpl.label}</div>
                      <div className="text-[10px] font-mono text-[#858585]">{tpl.filename}</div>
                    </button>
                  ))}
                </div>
              )}

              {/* INTEGRITY & IMPORT TAB */}
              {activityTab === 'integrity' && (
                <div className="p-3.5 space-y-4 text-xs">
                  <div className="bg-[#1E1E1E] border border-[#323233] rounded p-3 space-y-2">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="text-[#CCCCCC] font-medium flex items-center gap-1.5">
                        <Hash className="w-3.5 h-3.5 text-[#4EC9B0]" />
                        <span>Live SHA-256</span>
                      </span>
                      <button
                        type="button"
                        onClick={() => {
                          if (sha256) {
                            navigator.clipboard.writeText(sha256);
                            setCopiedSha(true);
                            setTimeout(() => setCopiedSha(false), 1800);
                          }
                        }}
                        className="text-[#3794FF] hover:underline text-[10px] cursor-pointer"
                      >
                        {copiedSha ? 'Copied!' : 'Copy Hash'}
                      </button>
                    </div>
                    <div className="font-mono text-[11px] text-[#4EC9B0] break-all select-all bg-[#141414] p-2 rounded border border-[#2B2B2B]">
                      {sha256 || 'Type code to compute SHA-256...'}
                    </div>
                  </div>

                  {/* Drag & Drop File Loader */}
                  <div
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={(e) => {
                      e.preventDefault();
                      if (e.dataTransfer.files?.[0]) {
                        handleFileImport(e.dataTransfer.files[0]);
                      }
                    }}
                    onClick={() => document.getElementById('vsc-import-file')?.click()}
                    className="border border-dashed border-[#454545] hover:border-[#007ACC] rounded p-5 text-center cursor-pointer bg-[#1E1E1E] hover:bg-[#252526] space-y-2 transition-colors"
                  >
                    <input
                      id="vsc-import-file"
                      type="file"
                      className="hidden"
                      onChange={(e) => {
                        if (e.target.files?.[0]) {
                          handleFileImport(e.target.files[0]);
                        }
                      }}
                    />
                    <UploadCloud className="w-6 h-6 text-[#3794FF] mx-auto" />
                    <div className="text-xs font-medium text-white">
                      {importedName ? `Loaded: ${importedName}` : 'Import Local Source File'}
                    </div>
                    <p className="text-[10px] text-[#858585]">
                      Click or drop any file to load its text directly into the VS Code editor.
                    </p>
                  </div>
                </div>
              )}
            </aside>
          )}

          {/* MAIN EDITOR GROUP */}
          <div className="flex-1 flex flex-col min-w-0 bg-[#1E1E1E]">
            {/* Editor Tabs Bar */}
            <div className="h-9 bg-[#252526] border-b border-[#2B2B2B] flex items-center justify-between pr-3 shrink-0 select-none">
              <div className="flex items-center h-full overflow-x-auto">
                <div className="h-full px-3.5 bg-[#1E1E1E] border-t-2 border-t-[#007ACC] border-r border-r-[#2B2B2B] flex items-center gap-2 text-xs font-mono text-white">
                  <span
                    className="text-[9px] font-bold px-1 rounded text-white"
                    style={{ backgroundColor: langMeta.color }}
                  >
                    {langMeta.badge}
                  </span>
                  <span>{filename || 'main.py'}</span>
                  <span className="w-2 h-2 rounded-full bg-[#D4D4D4]" title="Modified buffer" />
                </div>
              </div>

              {/* Editor Quick Toolbar */}
              <div className="flex items-center gap-1.5 text-[11px]">
                <label
                  htmlFor="vsc-quick-import"
                  className="px-2 py-1 rounded text-[#CCCCCC] hover:text-white hover:bg-[#2A2D2E] flex items-center gap-1 cursor-pointer"
                  title="Load file from disk into editor"
                >
                  <UploadCloud className="w-3.5 h-3.5 text-[#3794FF]" />
                  <span className="hidden sm:inline">Import File</span>
                </label>
                <input
                  id="vsc-quick-import"
                  type="file"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files?.[0]) handleFileImport(e.target.files[0]);
                  }}
                />

                <button
                  type="button"
                  onClick={() => {
                    navigator.clipboard.writeText(code);
                    setCopiedCode(true);
                    setTimeout(() => setCopiedCode(false), 1800);
                  }}
                  className="px-2 py-1 rounded text-[#CCCCCC] hover:text-white hover:bg-[#2A2D2E] flex items-center gap-1 cursor-pointer"
                  title="Copy buffer"
                >
                  {copiedCode ? (
                    <Check className="w-3.5 h-3.5 text-[#4EC9B0]" />
                  ) : (
                    <Copy className="w-3.5 h-3.5" />
                  )}
                  <span className="hidden sm:inline">{copiedCode ? 'Copied' : 'Copy'}</span>
                </button>

                <button
                  type="button"
                  onClick={() => onCodeChange('')}
                  className="px-2 py-1 rounded text-[#CCCCCC] hover:text-[#F48771] hover:bg-[#2A2D2E] flex items-center gap-1 cursor-pointer"
                  title="Clear editor buffer"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Clear</span>
                </button>
              </div>
            </div>

            {/* Breadcrumbs Strip */}
            <div className="h-6 px-4 bg-[#1E1E1E] border-b border-[#2A2A2A] flex items-center justify-between text-[11px] font-mono text-[#969696] shrink-0 select-none">
              <div className="flex items-center gap-1.5 truncate">
                <span>programs</span>
                <span>›</span>
                <span>{resolvedSubjectCode}</span>
                <span>›</span>
                <span className="truncate">{programTitle || 'new_experiment'}</span>
                <span>›</span>
                <span className="text-[#E5E5E5]">{filename || 'main.py'}</span>
              </div>
              {isLoadingInitialCode && (
                <span className="text-[#3794FF] text-[10px]">Loading remote file...</span>
              )}
            </div>

            {/* Error Alert Bar (Problems strip) */}
            {error && (
              <div className="px-4 py-2 bg-[#5A1D1D] border-b border-[#BE1100] text-xs text-[#F48771] flex items-center gap-2 shrink-0">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {/* Inactive-code notice when user unchecked 'includeCode' in create mode */}
            {!includeCode ? (
              <div className="flex-1 flex flex-col items-center justify-center p-8 text-center space-y-3 bg-[#1E1E1E]">
                <FileCode2 className="w-10 h-10 text-[#555555]" />
                <div className="text-sm font-medium text-[#CCCCCC]">
                  Initial Source Code Authoring Disabled
                </div>
                <p className="text-xs text-[#858585] max-w-md">
                  Only the program metadata will be saved right now. Check{' '}
                  <span className="text-[#3794FF]">"Publish editor code immediately as v1.0"</span> in the Explorer sidebar to author code here.
                </p>
              </div>
            ) : (
              /* Single Unified Scroll Container: locks Gutter, Line Highlight, Syntax & Caret 1:1 */
              <div
                ref={scrollContainerRef}
                className="vsc-editor-scroll flex-1 min-h-0 overflow-auto bg-[#1E1E1E]"
              >
                <div className="min-h-full min-w-full w-max flex items-stretch">
                  {/* Sticky Line Numbers Gutter */}
                  <div
                    style={CODE_FONT_STYLE}
                    className="w-14 sticky left-0 z-10 bg-[#1E1E1E] border-r border-[#2B2B2B] text-[#858585] py-3 pb-16 pr-3 text-right select-none shrink-0"
                  >
                    {lines.map((_, idx) => {
                      const lineNum = idx + 1;
                      const isActiveLine = cursorPos.line === lineNum;
                      return (
                        <div
                          key={lineNum}
                          style={{ height: `${LINE_HEIGHT_PX}px`, lineHeight: `${LINE_HEIGHT_PX}px` }}
                          className={
                            isActiveLine
                              ? 'text-[#C6C6C6] bg-[#2A2D2E]/50 -mr-3 pr-3'
                              : 'text-[#6E7681]'
                          }
                        >
                          {lineNum}
                        </div>
                      );
                    })}
                  </div>

                  {/* Syntax Backdrop (In-flow height driver) + Aligned Transparent Textarea */}
                  <div className="relative flex-1 min-w-[600px]">
                    <div
                      aria-hidden="true"
                      style={CODE_FONT_STYLE}
                      className="m-0 py-3 px-4 pb-16 pr-16 whitespace-pre pointer-events-none select-none text-[#D4D4D4]"
                    >
                      {highlightedLines.map((tokens, lineIdx) => {
                        const isActive = cursorPos.line === lineIdx + 1;
                        return (
                          <div
                            key={lineIdx}
                            style={{
                              height: `${LINE_HEIGHT_PX}px`,
                              lineHeight: `${LINE_HEIGHT_PX}px`,
                              backgroundColor: isActive ? 'rgba(255,255,255,0.05)' : 'transparent',
                            }}
                          >
                            {tokens.length > 0 ? (
                              tokens.map((tok, tIdx) => (
                                <span key={tIdx} style={{ color: tok.color }}>
                                  {tok.text}
                                </span>
                              ))
                            ) : (
                              <span> </span>
                            )}
                          </div>
                        );
                      })}
                    </div>

                    <textarea
                      ref={textareaRef}
                      value={normalizedCode}
                      wrap="off"
                      spellCheck={false}
                      autoCapitalize="off"
                      autoComplete="off"
                      autoCorrect="off"
                      onChange={(e) => {
                        onCodeChange(e.target.value);
                        updateCursor(e.currentTarget, true);
                      }}
                      onKeyDown={handleEditorKeyDown}
                      onClick={(e) => updateCursor(e.currentTarget, false)}
                      onKeyUp={(e) => updateCursor(e.currentTarget, true)}
                      onSelect={(e) => updateCursor(e.currentTarget, false)}
                      placeholder="# Write your program code here (Tab indents 4 spaces, Ctrl+S publishes)..."
                      style={CODE_FONT_STYLE}
                      className="vsc-editor-textarea absolute inset-0 w-full h-full m-0 py-3 px-4 pb-16 pr-16 bg-transparent text-transparent caret-[#AEAFAD] resize-none focus:outline-none whitespace-pre overflow-hidden selection:bg-[#264F78]/70"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 3. VS CODE STATUS BAR */}
        <footer className="h-6 bg-[#007ACC] text-white px-3 flex items-center justify-between text-[11px] shrink-0 select-none">
          <div className="flex items-center gap-3 min-w-0">
            <span className="font-mono font-semibold bg-[#16825D] px-2 h-6 flex items-center -ml-3">
              🍓 Strawberry Live
            </span>
            <button
              type="button"
              onClick={() => {
                if (sha256) {
                  navigator.clipboard.writeText(sha256);
                  setCopiedSha(true);
                  setTimeout(() => setCopiedSha(false), 1800);
                }
              }}
              className="hidden sm:flex items-center gap-1 hover:bg-white/15 px-1.5 py-0.5 rounded font-mono text-[10px] cursor-pointer truncate"
              title={sha256 || 'SHA-256 pending'}
            >
              <Check className="w-3 h-3" />
              <span>
                {copiedSha
                  ? 'SHA-256 Copied!'
                  : sha256
                  ? `SHA-256: ${sha256.slice(0, 12)}...`
                  : 'SHA-256: empty'}
              </span>
            </button>
            <span className="hidden md:inline text-white/85 font-mono text-[10px]">
              {lines.length} lines • {(byteSize / 1024).toFixed(2)} KB
            </span>
          </div>

          <div className="flex items-center gap-3.5 text-[11px]">
            <span>
              Ln {cursorPos.line}, Col {cursorPos.col}
            </span>
            <span className="hidden sm:inline">Spaces: 4</span>
            <span className="hidden sm:inline">UTF-8</span>
            <span className="font-medium">{langMeta.language}</span>
            <button
              type="button"
              onClick={onClose}
              className="hover:underline text-white/90 cursor-pointer pl-1"
            >
              Cancel
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
};
