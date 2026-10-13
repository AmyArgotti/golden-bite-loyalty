import type { LoyaltyDashboard, LoyaltyTransaction } from "./types";

// Fictional data for the portfolio preview. No authentication or API calls.
export const demoLoyalty: LoyaltyDashboard = {
  member_id: "GB-DEMO-001", points_balance: 1280, lifetime_points: 6280,
  tier: "silver", discount_percent: 5, qr_code_value: "GB-DEMO-001",
  barcode_value: "100001", wallet_status: "preview",
};
export const demoTransactions: LoyaltyTransaction[] = [
  { transaction_type: "purchase", points_delta: 180, rub_amount: 1800,
    source: "staff", comment: "Dinner at Golden Bite", created_at: "2026-10-12T18:30:00Z" },
  { transaction_type: "redemption", points_delta: -250, rub_amount: null,
    source: "staff", comment: "Points redeemed at checkout", created_at: "2026-10-10T12:00:00Z" },
  { transaction_type: "purchase", points_delta: 350, rub_amount: 3500,
    source: "staff", comment: "Weekend order", created_at: "2026-10-09T19:00:00Z" },
];
