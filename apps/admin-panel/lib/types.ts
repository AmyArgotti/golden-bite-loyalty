export type AdminAuth = {
  access_token: string;
  refresh_token: string;
  user: {
    id: string;
    role: string;
  };
};

export type AdminDashboard = {
  active_customers: number;
  total_points_issued: number;
  transactions_today: number;
  pending_fraud_flags: number;
};

export type LoyaltyRules = {
  points_per_rub_ratio: number;
  tiers: Array<{
    name: string;
    min_points: number;
    discount_percent: number;
  }>;
  first_order_bonus: number;
  birthday_bonus: number;
  referral_referrer_bonus: number;
  referral_referee_bonus: number;
};

export type AdminStaffUser = {
  id: string;
  phone_number: string;
  role: string;
  is_active: boolean;
  phone_verified_at: string | null;
};

export type AdminAuditLog = {
  id: string;
  actor_user_id: string | null;
  actor_role: string;
  action: string;
  entity_type: string;
  entity_id: string | null;
  before_data: Record<string, unknown> | null;
  after_data: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
};

export type AdminFraudFlag = {
  flag_type: string;
  severity: string;
  description: string;
  related_value: string | null;
  created_at: string;
};

export type AdminStaffCreateInput = {
  phone_number: string;
  role: string;
  is_active: boolean;
};

export type AdminStaffUpdateInput = {
  role?: string;
  is_active?: boolean;
};
