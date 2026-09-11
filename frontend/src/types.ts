export interface SalaryRecord {
  id: number;
  employee_id: number;
  base_salary: number;
  currency: string;
  bonus_target_pct: number;
  effective_date: string;
  reason: string | null;
  created_at: string;
}

export interface EmployeeListItem {
  id: number;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  department: string;
  job_title: string;
  job_level: string;
  country: string;
  status: "active" | "inactive";
  current_salary: number | null;
  currency: string | null;
}

export interface EmployeeDetail {
  id: number;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  department: string;
  job_title: string;
  job_level: string;
  country: string;
  currency: string;
  manager_id: number | null;
  status: "active" | "inactive";
  hire_date: string;
  salary_records: SalaryRecord[];
}

export interface PaginatedEmployees {
  items: EmployeeListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface GroupAverage {
  group: string;
  headcount: number;
  avg_salary: number;
  median_salary: number;
  total_cost: number;
  currency: string;
}

export interface GroupPayIndex {
  group: string;
  headcount: number;
  avg_pay_index: number;
  median_pay_index: number;
}

export interface HistogramBucket {
  range_start: number;
  range_end: number;
  count: number;
}

export interface AnalyticsSummary {
  total_employees: number;
  active_employees: number;
  inactive_employees: number;
  by_department: GroupPayIndex[];
  by_country: GroupAverage[];
  by_level: GroupPayIndex[];
  pay_index_histogram: HistogramBucket[];
}

export interface ReferenceData {
  departments: string[];
  job_levels: string[];
  countries: { name: string; currency: string }[];
}

export interface EmployeeFilters {
  page: number;
  page_size: number;
  department?: string;
  country?: string;
  job_level?: string;
  status?: string;
  search?: string;
}
