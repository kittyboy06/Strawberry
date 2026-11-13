export interface Year {
  id: string;
  year_number: number;
  display_name: string;
}

export interface Semester {
  id: string;
  year_id: string;
  semester_number: number;
  display_name: string;
}

export interface Subject {
  id: string;
  semester_id: string;
  subject_code: string;
  subject_name: string;
  is_active: boolean;
  semester_label?: string;
}

export interface ExperimentVersion {
  id: string;
  experiment_id: string;
  version_number: number;
  storage_path: string;
  filename: string;
  sha256: string;
  created_at?: string;
}

export interface Experiment {
  id: string;
  subject_id: string;
  experiment_number: number;
  title: string;
  description: string;
  is_published: boolean;
  current_version?: ExperimentVersion | null;
}
