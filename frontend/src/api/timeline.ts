import { api } from './client';
import type { TimelineEvent } from '../types';

export const timelineApi = {
  getTimeline: (personId: string) =>
    api.get<TimelineEvent[]>(`/people/${personId}/timeline`),
};
