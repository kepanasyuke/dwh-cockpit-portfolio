const LOOP_MESSAGES = {
  WhileStatement: 'while запрещён: используй map/filter/reduce или for..of',
  DoWhileStatement: 'do..while запрещён: используй map/filter/reduce или for..of',
  BreakStatement: 'break запрещён: вынеси условие в filter/some/find',
  ContinueStatement: 'continue запрещён: вынеси условие в filter',
  LabeledStatement: 'метки запрещены',
};

export default {
  meta: {
    type: 'problem',
    docs: { description: 'Запрет while / do..while / break / continue / меток' },
    schema: [],
    messages: {
      banned: '{{reason}}',
    },
  },
  create(context) {
    const report = (node) =>
      context.report({ node, messageId: 'banned', data: { reason: LOOP_MESSAGES[node.type] } });
    return Object.keys(LOOP_MESSAGES).reduce(
      (visitors, type) => ({ ...visitors, [type]: report }),
      {},
    );
  },
};
