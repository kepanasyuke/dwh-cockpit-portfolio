'use client';

import { useEffect, useState, type Dispatch, type SetStateAction } from 'react';
import { demoDashboard } from './demo';
import { apiBase, type Project } from './projects';
import type { Dashboard } from './types';

export type Feed = {
  data: Dashboard | null;
  loading: boolean;
  error: string | null;
};

export type Json = Record<string, unknown>;

export type WidgetFeed = {
  data: Json | null;
  error: string | null;
};

export const INITIAL: Feed = { data: null, loading: true, error: null };
export const NO_WIDGET: WidgetFeed = { data: null, error: null };

const okState = async (response: Response): Promise<Feed> => ({
  data: (await response.json()) as Dashboard,
  loading: false,
  error: null,
});

const failState = (reason: string): Feed => ({ data: null, loading: false, error: reason });

const request = async (url: string): Promise<Feed> =>
  fetch(url).then((response) => (response.ok ? okState(response) : failState(`HTTP ${response.status}`)));

const load = (url: string, done: Dispatch<SetStateAction<Feed>>): Promise<void> =>
  request(url).then(done, (reason) => done(failState(String(reason))));

const useLoader = (url: string, setFeed: Dispatch<SetStateAction<Feed>>, feed: Feed): Feed => {
  useEffect(() => void load(url, setFeed), [url, setFeed]);
  return feed;
};

export const useDashboard = (project: Project): Feed & { dashboard: Dashboard } => {
  const [feed, setFeed] = useState<Feed>(INITIAL);
  return { ...useLoader(`${apiBase(project)}/api/dashboard`, setFeed, feed), dashboard: feed.data ?? demoDashboard(project) };
};

const toWidget = (reason: string): WidgetFeed => ({ data: null, error: reason });

const readWidget = (response: Response): Promise<WidgetFeed> =>
  response.ok
    ? response.json().then((data: Json) => ({ data, error: null }))
    : Promise.resolve(toWidget(`HTTP ${response.status}`));

const postWidget = (project: Project, body: Json | null, done: (feed: WidgetFeed) => void): Promise<void> =>
  fetch(`${apiBase(project)}/api/widget`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body ?? {}),
  })
    .then(readWidget, () => toWidget('backend недоступен'))
    .then(done);

const useWidgetLoader = (
  project: Project,
  body: Json | null,
  setFeed: Dispatch<SetStateAction<WidgetFeed>>,
  feed: WidgetFeed,
): WidgetFeed => {
  useEffect(() => void postWidget(project, body, setFeed), [project, body, setFeed]);
  return feed;
};

export const useWidget = (project: Project, body: Json | null): WidgetFeed => {
  const [feed, setFeed] = useState<WidgetFeed>(NO_WIDGET);
  return useWidgetLoader(project, body, setFeed, feed);
};

export const useWidgetSubmit = (project: Project): { feed: WidgetFeed; submit: (body: Json) => void } => {
  const [feed, setFeed] = useState<WidgetFeed>(NO_WIDGET);
  return { feed, submit: (body: Json) => void postWidget(project, body, setFeed) };
};
