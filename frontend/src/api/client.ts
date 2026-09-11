import axios from "axios";
import type {
  AnalyticsSummary,
  EmployeeDetail,
  EmployeeFilters,
  PaginatedEmployees,
  ReferenceData,
  SalaryRecord,
} from "../types";

const api = axios.create({ baseURL: "/api" });

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
