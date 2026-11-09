const SKIP_KEYS = new Set(['parent', 'loc', 'range', 'start', 'end', 'tokens', 'comments']);

const FUNCTION_TYPES = new Set([
  'FunctionDeclaration',
  'FunctionExpression',
  'ArrowFunctionExpression',
]);

const isNode = (value) => Boolean(value) && typeof value === 'object' && typeof value.type === 'string';

const isNestedFunction = (node) => FUNCTION_TYPES.has(node.type);

const childrenOf = (node) =>
  Object.keys(node)
    .filter((key) => !SKIP_KEYS.has(key))
    .map((key) => node[key])
    .flat()
    .filter(isNode);

export const returnsOf = (node, acc = [], isRoot = true) => {
  if (!isNode(node) || (!isRoot && isNestedFunction(node))) return acc;
  if (node.type === 'ReturnStatement') acc.push(node);
  return childrenOf(node).reduce((all, child) => returnsOf(child, all, false), acc);
};

export default {
  meta: {
    type: 'suggestion',
    docs: { description: 'Ровно один выход из функции: не более одного return' },
    schema: [],
    messages: {
      tooMany: 'Один выход из функции: найдено {{count}} return (лимит 1).',
    },
  },
  create(context) {
    const check = (node) => {
      const count = returnsOf(node.body, [], false).length;
      if (count > 1) context.report({ node, messageId: 'tooMany', data: { count } });
    };
    return {
      FunctionDeclaration: check,
      FunctionExpression: check,
      ArrowFunctionExpression: check,
    };
  },
};
