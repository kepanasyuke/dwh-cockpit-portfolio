'use client';

import { useEffect, useState, type Dispatch, type SetStateAction } from 'react';
import { useFilters } from '@/components/filters-provider';
import type { Answer } from './types';

export type Feed<T> = {
  data: T | null;
  error: string | null;
  loading: boolean;
};

export const API = process.env.NEXT_PUBLIC_COCKPIT_API ?? 'http://127.0.0.1:8109';

const okState = async <T,>(response: Response): Promise<Feed<T>> => ({
  data: (await response.json()) as T,
  error: null,
  loading: false,
});

const failState = <T,>(reason: string): Feed<T> => ({ data: null, error: reason, loading: false });

const read = <T,>(url: string): Promise<Feed<T>> =>
  fetch(url).then(
    (response) => (response.ok ? okState<T>(response) : failState<T>(`HTTP ${response.status}`)),
    (reason) => failState<T>(String(reason)),
  );

const useFetch = <T,>(url: string, setFeed: Dispatch<SetStateAction<Feed<T>>>, feed: Feed<T>): Feed<T> => {
  useEffect(() => void read<T>(url).then(setFeed), [url, setFeed]);
  return feed;
};

export const useJson = <T,>(url: string): Feed<T> => {
  const [feed, setFeed] = useState<Feed<T>>({ data: null, error: null, loading: true });
  return useFetch<T>(url, setFeed, feed);
};

export const useScreen = <T,>(path: string): Feed<T> => {
  const filters = useFilters();
  return useJson<T>(`${API}${path}${filters.query}`);
};

export const readAnswer = async (question: string): Promise<Answer | null> => {
  const response = await read<Answer>(`${API}/api/ask?q=${encodeURIComponent(question)}`);
  return response.data;
};
