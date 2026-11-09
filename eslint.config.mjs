import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import strict from './packages/eslint-plugin-strict/index.js';

const STYLE_RULES = {
  'strict/single-exit': 'error',
  'strict/no-loop-jumps': 'error',
  'max-statements': ['error', 2],
  'no-plusplus': 'error',
  'no-var': 'error',
  'prefer-const': 'error',
  'no-labels': 'error',
  'no-lone-blocks': 'error',
  'no-else-return': 'error',
  'consistent-return': 'error',
  'no-param-reassign': 'error',
  'prefer-arrow-callback': 'error',
  'arrow-body-style': ['error', 'as-needed'],
};

export default tseslint.config(
  { ignores: ['**/node_modules/**', '**/.next/**', '**/out/**', '**/dist/**', '**/*.d.ts', '**/.eslintrc*'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    languageOptions: {
      parserOptions: { ecmaVersion: 'latest', sourceType: 'module', ecmaFeatures: { jsx: true } },
      globals: { window: 'readonly', document: 'readonly', fetch: 'readonly', console: 'readonly', process: 'readonly' },
    },
    plugins: { strict },
    rules: STYLE_RULES,
  },
  {
    files: ['packages/eslint-plugin-strict/**/*.js'],
    rules: { 'max-statements': 'off', 'strict/single-exit': 'off' },
  },
);
