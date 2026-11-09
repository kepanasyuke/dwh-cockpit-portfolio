'use client';

import { useState } from 'react';
import { formatValue } from '@/lib/format';
import type { Column, Row } from '@/lib/types';

const cellOf = (row: Row, column: Column): string => formatValue(row[column.key] ?? null, column.format);

const sorted = (rows: Row[], key: string): Row[] =>
  [...rows].sort((left, right) =>
    typeof left[key] === 'number' && typeof right[key] === 'number'
      ? (right[key] as number) - (left[key] as number)
      : String(left[key]).localeCompare(String(right[key])),
  );

export const DataGrid = ({
  columns,
  rows,
  empty = 'Нет данных за выбранный период',
  onRowClick,
}: {
  columns: Column[];
  rows: Row[];
  empty?: string;
  onRowClick?: (row: Row) => void;
}) => {
  const [sortKey, setSortKey] = useState(columns[0]?.key ?? '');
  return (
    <table className="grid">
      <thead>
        <tr>
          {columns.map((column) => (
            <th
              key={column.key}
              className={`${column.align === 'right' ? 'right' : ''}${sortKey === column.key ? ' sorted' : ''}`}
              onClick={() => setSortKey(column.key)}
            >
              {column.title}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.length === 0 ? (
          <tr>
            <td colSpan={columns.length} className="empty">
              {empty}
            </td>
          </tr>
        ) : null}
        {sorted(rows, sortKey).map((row, index) => (
          <tr key={index} className={onRowClick ? 'clickable' : undefined} onClick={() => onRowClick?.(row)}>
            {columns.map((column) => (
              <td key={column.key} className={column.align === 'right' ? 'right' : undefined}>
                {cellOf(row, column)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
};
