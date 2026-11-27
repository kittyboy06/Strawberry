export interface CodeTemplate {
  key: string;
  label: string;
  language: string;
  filename: string;
  code: string;
}

export const STARTER_TEMPLATES: CodeTemplate[] = [
  {
    key: 'blank',
    label: 'Python • Starter Stub',
    language: 'Python',
    filename: 'main.py',
    code: `# Write your Python program here

def main():
    pass

if __name__ == '__main__':
    main()
`,
  },
  {
    key: 'c_blank',
    label: 'C • Starter Stub',
    language: 'C',
    filename: 'main.c',
    code: `#include <stdio.h>

int main() {
    return 0;
}
`,
  },
  {
    key: 'sql_blank',
    label: 'SQL • Starter Stub',
    language: 'SQL',
    filename: 'query.sql',
    code: `-- Write your SQL statements here
`,
  },
  {
    key: 'java_blank',
    label: 'Java • Starter Stub',
    language: 'Java',
    filename: 'Main.java',
    code: `public class Main {
    public static void main(String[] args) {
        
    }
}
`,
  },
];

export interface FileLangMeta {
  badge: string;
  color: string;
  language: string;
}

export function detectLanguageMeta(filename: string): FileLangMeta {
  const lower = filename.toLowerCase();
  if (lower.endsWith('.py')) return { badge: 'PY', color: '#3776AB', language: 'Python' };
  if (lower.endsWith('.c')) return { badge: 'C', color: '#559CD6', language: 'C' };
  if (lower.endsWith('.cpp') || lower.endsWith('.cc')) {
    return { badge: 'C++', color: '#00599C', language: 'C++' };
  }
  if (lower.endsWith('.java')) return { badge: 'JV', color: '#E76F00', language: 'Java' };
  if (lower.endsWith('.sql')) return { badge: 'SQL', color: '#2DD4BF', language: 'SQL' };
  if (lower.endsWith('.js')) return { badge: 'JS', color: '#F7DF1E', language: 'JavaScript' };
  if (lower.endsWith('.ts')) return { badge: 'TS', color: '#3178C6', language: 'TypeScript' };
  if (lower.endsWith('.pl')) return { badge: 'PL', color: '#E11D48', language: 'Prolog' };
  return { badge: 'TXT', color: '#858585', language: 'Plain Text' };
}

export interface HighlightToken {
  text: string;
  color: string;
}

const KEYWORDS = new Set([
  'import', 'from', 'as', 'def', 'class', 'return', 'if', 'elif', 'else', 'for', 'while',
  'with', 'try', 'except', 'finally', 'raise', 'pass', 'break', 'continue', 'in', 'is',
  'not', 'and', 'or', 'True', 'False', 'None', 'async', 'await', 'lambda', 'yield',
  'int', 'char', 'float', 'double', 'void', 'struct', 'typedef', 'sizeof', 'unsigned',
  'const', 'static', 'public', 'private', 'protected', 'new', 'this', 'boolean', 'String',
  'SELECT', 'FROM', 'WHERE', 'JOIN', 'ON', 'CREATE', 'TABLE', 'IF', 'NOT', 'EXISTS',
  'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'ORDER', 'BY', 'GROUP', 'HAVING',
  'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'DEFAULT', 'CASCADE', 'DESC', 'ASC', 'AS',
  'USE', 'DATABASE', 'DROP', 'ALTER', 'VARCHAR', 'INT', 'DECIMAL', 'UUID', 'TIMESTAMPTZ',
  'select', 'from', 'where', 'join', 'on', 'create', 'table', 'insert', 'into', 'values',
]);

/**
 * Lightweight deterministic tokenizer using VS Code Dark+ palette.
 * Color-only spans keep monospace character advance widths identical to textarea text.
 */
export function highlightLineTokens(line: string, filename: string): HighlightToken[] {
  if (!line) return [];
  const lower = filename.toLowerCase();
  const isSql = lower.endsWith('.sql');
  const isCStyle =
    lower.endsWith('.c') ||
    lower.endsWith('.cpp') ||
    lower.endsWith('.java') ||
    lower.endsWith('.js') ||
    lower.endsWith('.ts');

  const tokens: HighlightToken[] = [];
  let i = 0;

  while (i < line.length) {
    if (!isCStyle && !isSql && line[i] === '#') {
      tokens.push({ text: line.slice(i), color: '#6A9955' });
      break;
    }
    if (isSql && line.slice(i, i + 2) === '--') {
      tokens.push({ text: line.slice(i), color: '#6A9955' });
      break;
    }
    if (isCStyle && line.slice(i, i + 2) === '//') {
      tokens.push({ text: line.slice(i), color: '#6A9955' });
      break;
    }
    if (isCStyle && i === 0 && line.trimStart().startsWith('#')) {
      tokens.push({ text: line, color: '#C586C0' });
      break;
    }

    if (line[i] === '"' || line[i] === "'") {
      const quote = line[i];
      let j = i + 1;
      while (j < line.length) {
        if (line[j] === '\\') {
          j += 2;
          continue;
        }
        if (line[j] === quote) {
          j++;
          break;
        }
        j++;
      }
      tokens.push({ text: line.slice(i, j), color: '#CE9178' });
      i = j;
      continue;
    }

    if (/[0-9]/.test(line[i]) && (i === 0 || !/[A-Za-z0-9_]/.test(line[i - 1]))) {
      let j = i + 1;
      while (j < line.length && /[0-9.xXa-fA-F]/.test(line[j])) j++;
      tokens.push({ text: line.slice(i, j), color: '#B5CEA8' });
      i = j;
      continue;
    }

    if (/[A-Za-z_]/.test(line[i])) {
      let j = i + 1;
      while (j < line.length && /[A-Za-z0-9_]/.test(line[j])) j++;
      const word = line.slice(i, j);
      if (KEYWORDS.has(word)) {
        tokens.push({ text: word, color: '#569CD6' });
      } else if (j < line.length && line[j] === '(') {
        tokens.push({ text: word, color: '#DCDCAA' });
      } else {
        tokens.push({ text: word, color: '#D4D4D4' });
      }
      i = j;
      continue;
    }

    if (/[{}()[\].,:;+\-*/%=<>!&|]/.test(line[i])) {
      tokens.push({ text: line[i], color: '#FFD700' });
      i++;
      continue;
    }

    let j = i + 1;
    while (j < line.length && /\s/.test(line[j])) j++;
    tokens.push({ text: line.slice(i, j), color: '#D4D4D4' });
    i = j;
  }

  return tokens;
}
