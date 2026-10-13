import {
  AdminAuditLog,
  AdminAuth,
  AdminDashboard,
  AdminFraudFlag,
  AdminStaffCreateInput,
  AdminStaffUpdateInput,
  AdminStaffUser,
  LoyaltyRules,
} from "../lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function requestOtp(phoneNumber: string) {
  return apiFetch<{ message: string; expires_in_seconds: number }>("/auth/request-otp", {
    method: "POST",
    body: JSON.stringify({ phone_number: phoneNumber, purpose: "login" }),
  });
}

export function verifyOtp(phoneNumber: string, otpCode: string) {
  return apiFetch<AdminAuth>("/auth/verify-otp", {
    method: "POST",
    body: JSON.stringify({ phone_number: phoneNumber, otp_code: otpCode }),
  });
}

export function getAdminDashboard(accessToken: string) {
  return apiFetch<AdminDashboard>("/admin/dashboard", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

export function getLoyaltyRules(accessToken: string) {
  return apiFetch<LoyaltyRules>("/admin/config/loyalty-rules", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

export function getAdminStaff(accessToken: string) {
  return apiFetch<AdminStaffUser[]>("/admin/staff", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

export function getAuditLogs(accessToken: string) {
  return apiFetch<AdminAuditLog[]>("/admin/audit-logs", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

export function getFraudFlags(accessToken: string) {
  return apiFetch<AdminFraudFlag[]>("/admin/fraud-flags", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

export function createAdminStaff(accessToken: string, payload: AdminStaffCreateInput) {
  return apiFetch<AdminStaffUser>("/admin/staff", {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify(payload),
  });
}

export function updateAdminStaff(accessToken: string, staffId: string, payload: AdminStaffUpdateInput) {
  return apiFetch<AdminStaffUser>(`/admin/staff/${staffId}`, {
    method: "PATCH",
    headers: { Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify(payload),
  });
}

export function updateLoyaltyRules(accessToken: string, payload: LoyaltyRules) {
  return apiFetch<LoyaltyRules>("/admin/config/loyalty-rules", {
    method: "PATCH",
    headers: { Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify(payload),
  });
}

export async function downloadCustomerExport(accessToken: string) {
  const response = await fetch(`${API_BASE_URL}/admin/customers/export`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    cache: "no-store",
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }
  return response.text();
}
