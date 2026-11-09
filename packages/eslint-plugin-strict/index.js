import singleExit from './rules/single-exit.js';
import noLoopJumps from './rules/no-loop-jumps.js';

export default {
  meta: { name: 'eslint-plugin-strict', version: '1.0.0' },
  rules: {
    'single-exit': singleExit,
    'no-loop-jumps': noLoopJumps,
  },
};
