import jseslint from '@eslint/js';
import stylistic from '@stylistic/eslint-plugin';

import { defineConfig, globalIgnores } from 'eslint/config';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import simpleImportSortPlugin from 'eslint-plugin-simple-import-sort';
import { eslintBoundariesConfig } from './eslint.boundaries.js';

export default defineConfig([
  globalIgnores(['dist', 'node_modules', 'public', 'src/shared/api/schema/generated.ts']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      jseslint.configs.recommended,
      tseslint.configs.recommended,
      reactHooks.configs.flat.recommended,
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
  },
  {
    files: ['**/*.{ts,tsx}'],
    plugins: {
      'simple-import-sort': simpleImportSortPlugin,
    },
    rules: {
      'simple-import-sort/imports': [
        'error',
        {
          groups: [
            ['^react'],
            ['^[@a-zA-Z]'],
            ['^@/app'],
            ['^@/features'],
            ['^@/shared'],
            [String.raw`^\./*`, String.raw`^./\w+$`, String.raw`^\.\./*`],
            ['(.json)'],
            ['(.svg|.png)'],
            ['(.css|.scss)'],
          ],
        },
      ],
    },
  },
  {
    files: ['**/*.{ts,tsx}'],
    plugins: {
      '@stylistic': stylistic
    },
    extends: [
      stylistic.configs.recommended,
    ],
    rules: {
      '@stylistic/indent': ['error', 2],
      '@stylistic/quotes': ['error', 'single'],
      '@stylistic/semi': ['error', 'always'],
      '@stylistic/comma-dangle': ['error', 'always-multiline'],
      '@stylistic/object-curly-spacing': ['error', 'always'],
      '@stylistic/arrow-parens': ['error', 'always'],
      '@stylistic/space-in-parens': ['error', 'never'],
      '@stylistic/brace-style': ['error', '1tbs'],
      '@stylistic/member-delimiter-style': [
        'error',
        {
          multiline: {
            delimiter: 'semi',
            requireLast: true
          },
          singleline: {
            delimiter: 'semi',
            requireLast: true
          },
          multilineDetection: 'brackets'
        }
      ]
    },
  },
  {
    files: ['src/shared/ui/kit/*.{ts,tsx}'],
    rules: {
      'react-refresh/only-export-components': 'off',
    },
  },
  eslintBoundariesConfig,
]);
