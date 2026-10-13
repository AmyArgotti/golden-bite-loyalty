import { AuthTokens, LoyaltyDashboard, LoyaltyTransaction, MeProfile, WalletStatus } from "../lib/types";

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
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function requestOtp(phoneNumber: string) {
  return apiFetch<{ message: string; expires_in_seconds: number }>("/auth/request-otp", {
    method: "POST",
    body: JSON.stringify({ phone_number: phoneNumber, purpose: "register" }),
  });
}

export function verifyOtp(phoneNumber: string, otpCode: string) {
  return apiFetch<AuthTokens & { is_new_user: boolean; user: { id: string; role: string } }>("/auth/verify-otp", {
    method: "POST",
    body: JSON.stringify({ phone_number: phoneNumber, otp_code: otpCode }),
  });
}

export function getMe(accessToken: string) {
  return apiFetch<MeProfile>("/me", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

export function updateProfile(
  accessToken: string,
  payload: { full_name: string | null; birthday: string | null; marketing_sms_consent: boolean },
) {
  return apiFetch<MeProfile>("/me/profile", {
    method: "PATCH",
    headers: { Authorization: `Bearer ${accessToken}` },
    body: JSON.stringify(payload),
  });
}

export function getLoyalty(accessToken: string) {
  return apiFetch<LoyaltyDashboard>("/me/loyalty", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

export function getTransactions(accessToken: string) {
  return apiFetch<LoyaltyTransaction[]>("/me/transactions", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

export function getWalletStatus(accessToken: string) {
  return apiFetch<WalletStatus>("/wallet/status", {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

export function addAppleWallet(accessToken: string) {
  return apiFetch<{ download_url: string }>("/wallet/apple/add", {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}

export function refreshWallet(accessToken: string) {
  return apiFetch<WalletStatus>("/wallet/refresh", {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
  });
}
