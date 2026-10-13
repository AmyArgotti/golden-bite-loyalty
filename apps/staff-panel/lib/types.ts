export type StaffAuth = {
  access_token: string;
  refresh_token: string;
  user: {
    id: string;
    role: string;
  };
};

export type StaffCustomer = {
  customer_id: string;
  member_id: string;
  phone_number: string;
  points_balance: number;
  tier: string;
};

export type PurchaseResult = {
  earned_points: number;
  bonus_points: number;
  total_points_added: number;
  new_points_balance: number;
  new_tier: string;
  discount_percent: number;
};

export type StaffOperationResult = {
  message: string;
  points_balance: number;
  tier: string;
  discount_percent: number;
};

export type StaffTransaction = {
  transaction_type: string;
  points_delta: number;
  rub_amount: number | null;
  source: string;
  comment: string | null;
  created_at: string;
};

export type StaffCustomerDetail = {
  customer_id: string;
  member_id: string;
  phone_number: string;
  points_balance: number;
  lifetime_points: number;
  tier: string;
  discount_percent: number;
  qr_code_value: string;
  barcode_value: string;
  recent_transactions: StaffTransaction[];
};
