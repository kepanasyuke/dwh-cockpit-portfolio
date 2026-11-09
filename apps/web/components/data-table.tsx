import { formatValue } from '@/lib/format';
import type { Column, Table } from '@/lib/types';

const cellOf = (row: Record<string, string | number>, column: Column): string =>
  formatValue(row[column.key] ?? '', column.format);

export const DataTable = ({ table }: { table: Table }) => (
  <table className="data">
    <thead>
      <tr>
        {table.columns.map((column) => (
          <th key={column.key} className={column.align === 'right' ? 'align-right' : undefined}>
            {column.title}
          </th>
        ))}
      </tr>
    </thead>
    <tbody>
      {table.rows.map((row, index) => (
        <tr key={index}>
          {table.columns.map((column) => (
            <td key={column.key} className={column.align === 'right' ? 'align-right' : undefined}>
              {cellOf(row, column)}
            </td>
          ))}
        </tr>
      ))}
    </tbody>
  </table>
);
