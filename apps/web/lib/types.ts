export type LoyaltyDashboard = {
  member_id: string;
  points_balance: number;
  lifetime_points: number;
  tier: string;
  discount_percent: number;
  qr_code_value: string;
  barcode_value: string;
  wallet_status: string;
};

export type LoyaltyTransaction = {
  transaction_type: string;
  points_delta: number;
  rub_amount: number | null;
  source: string;
  comment: string | null;
  created_at: string;
};

export type AuthTokens = {
  access_token: string;
  refresh_token: string;
};

export type MeProfile = {
  user_id: string;
  phone_number: string;
  role: string;
  profile: {
    full_name: string | null;
    birthday: string | null;
    marketing_sms_consent: boolean;
  };
};

export type WalletStatus = {
  status: string;
  last_synced_at: string | null;
};
