'use client';

import { createContext, useContext, useState, type ReactNode } from 'react';

export type Filters = { period: number; city: string };

export type FiltersValue = Filters & {
  query: string;
  setPeriod: (period: number) => void;
  setCity: (city: string) => void;
};

export const PERIODS = [7, 14, 28];

const DEFAULTS: Filters = { period: 7, city: 'all' };

const Context = createContext<FiltersValue>({
  ...DEFAULTS,
  query: '',
  setPeriod: () => undefined,
  setCity: () => undefined,
});

const queryOf = (filters: Filters): string =>
  `?period=${filters.period}&city=${encodeURIComponent(filters.city === 'all' ? '' : filters.city)}`;

export const FiltersProvider = ({ children }: { children: ReactNode }) => {
  const [filters, setFilters] = useState<Filters>(DEFAULTS);
  return (
    <Context.Provider
      value={{
        ...filters,
        query: queryOf(filters),
        setPeriod: (period) => setFilters({ ...filters, period }),
        setCity: (city) => setFilters({ ...filters, city }),
      }}
    >
      {children}
    </Context.Provider>
  );
};

export const useFilters = (): FiltersValue => useContext(Context);
