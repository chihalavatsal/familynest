export interface TimelineEvent {
  id: string;
  date?: string;
  year?: number;
  title: string;
  description?: string;
  icon: 'birth' | 'death' | 'marriage' | 'job' | 'education' | 'child';
}
