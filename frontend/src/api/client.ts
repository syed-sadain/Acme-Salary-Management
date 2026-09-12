import axios from "axios";
import type {
  AnalyticsSummary,
  EmployeeDetail,
  EmployeeFilters,
  PaginatedEmployees,
  ReferenceData,
  SalaryRecord,
} from "../types";

// Base URL for the API. Defaults to the relative "/api" path, which works in
// local dev (Vite proxies it) and in Docker (nginx proxies it). When the
// frontend is deployed separately from the backend (e.g. Vercel frontend +
// Render/Railway backend), set VITE_API_BASE_URL to the backend's public URL
// at build time. See docs/DEPLOYMENT.md.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
});

export interface NewEmployeePayload {
  first_name: string;
  last_name: string;
  email: string;
  department: string;
  job_title: string;
  job_level: string;
  country: string;
  hire_date: string;
  status: string;
  starting_salary: {
    base_salary: number;
    currency: string;
    bonus_target_pct: number;
    effective_date: string;
    reason?: string;
  };
}

export interface NewSalaryRecordPayload {
  base_salary: number;
  currency: string;
  bonus_target_pct: number;
  effective_date: string;
  reason?: string;
}

export async function fetchEmployees(
  filters: EmployeeFilters,
): Promise<PaginatedEmployees> {
  const { data } = await api.get<PaginatedEmployees>("/employees", {
    params: filters,
  });
  return data;
}

export async function fetchEmployee(id: number): Promise<EmployeeDetail> {
  const { data } = await api.get<EmployeeDetail>(`/employees/${id}`);
  return data;
}

export async function createEmployee(
  payload: NewEmployeePayload,
): Promise<EmployeeDetail> {
  const { data } = await api.post<EmployeeDetail>("/employees", payload);
  return data;
}

export async function deactivateEmployee(id: number): Promise<EmployeeDetail> {
  const { data } = await api.delete<EmployeeDetail>(`/employees/${id}`);
  return data;
}

export async function addSalaryRecord(
  id: number,
  payload: NewSalaryRecordPayload,
): Promise<SalaryRecord> {
  const { data } = await api.post<SalaryRecord>(
    `/employees/${id}/salary-records`,
    payload,
  );
  return data;
}

export async function fetchAnalyticsSummary(): Promise<AnalyticsSummary> {
  const { data } = await api.get<AnalyticsSummary>("/analytics/summary");
  return data;
}

export async function fetchReferenceData(): Promise<ReferenceData> {
  const { data } = await api.get<ReferenceData>("/analytics/reference-data");
  return data;
}
