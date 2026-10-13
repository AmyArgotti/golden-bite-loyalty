import { PurchaseResult, StaffAuth, StaffCustomer, StaffCustomerDetail, StaffOperationResult } from "../lib/types";

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
    throw new Error(text || `Request failed with ${response.status}`);
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
  return apiFetch<StaffAuth>("/auth/verify-otp", {
    method: "POST",
    body: JSON.stringify({ phone_number: phoneNumber, otp_code: otpCode }),
  });
}

export function searchCustomers(accessToken: string, query: { phoneNumber?: string; memberId?: string }) {
  const params = new URLSearchParams();
  if (query.phoneNumber) {
    params.set("phone_number", query.phoneNumber);
  }
  if (query.memberId) {
    params.set("member_id", query.memberId);
  }
  return apiFetch<StaffCustomer[]>(`/staff/customers/search?${params.toString()}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

export function getCustomerDetail(accessToken: string, customerId: string) {
  return apiFetch<StaffCustomerDetail>(`/staff/customers/${customerId}`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

export function scanCustomer(accessToken: string, scanValue: string) {
  return apiFetch<StaffCustomerDetail>("/staff/customers/scan", {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify({ scan_value: scanValue }),
  });
}

export function registerPurchase(
  accessToken: string,
  payload: { customer_id: string; purchase_amount: number; order_reference?: string },
) {
  return apiFetch<PurchaseResult>("/staff/purchases", {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify(payload),
  });
}

export function redeemPoints(
  accessToken: string,
  payload: { customer_id: string; points_to_redeem: number; comment?: string },
) {
  return apiFetch<StaffOperationResult>("/staff/redeem", {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify(payload),
  });
}

export function adjustPoints(
  accessToken: string,
  payload: { customer_id: string; points_delta: number; comment: string },
) {
  return apiFetch<StaffOperationResult>("/staff/adjust", {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify(payload),
  });
}
