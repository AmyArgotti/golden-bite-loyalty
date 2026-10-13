"use client";

import { StaffCustomerDetail } from "../lib/types";

type CustomerDetailProps = {
  customer: StaffCustomerDetail | null;
};

export function CustomerDetail({ customer }: CustomerDetailProps) {
  if (!customer) {
    return (
      <div className="panel customer-hero-card">
        <h3>Customer quick view</h3>
        <p className="muted" style={{ marginBottom: 0 }}>
          Choose a customer to see loyalty details and recent activity.
        </p>
        <p className="muted helper-line" style={{ marginBottom: 0 }}>
          Tip: search by phone for speed, or scan the member code at the counter.
        </p>
      </div>
    );
  }

  return (
    <div className="stack">
      <div className="panel">
        <div className="button-row" style={{ justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div className="kicker">Quick View</div>
            <h3 style={{ marginBottom: 6 }}>{customer.member_id}</h3>
            <p className="muted" style={{ marginTop: 0, marginBottom: 0 }}>
              {customer.phone_number}
            </p>
          </div>
          <span className="code-pill">{customer.barcode_value}</span>
        </div>

        <div className="summary-grid" style={{ marginTop: 16 }}>
          <div className="summary-card">
            <div className="muted">Points</div>
            <strong>{customer.points_balance}</strong>
          </div>
          <div className="summary-card">
            <div className="muted">Lifetime</div>
            <strong>{customer.lifetime_points}</strong>
          </div>
          <div className="summary-card">
            <div className="muted">Tier</div>
            <strong style={{ textTransform: "capitalize" }}>{customer.tier}</strong>
          </div>
          <div className="summary-card">
            <div className="muted">Discount</div>
            <strong>{customer.discount_percent}%</strong>
          </div>
        </div>

        <div style={{ marginTop: 14 }}>
          <div className="muted">QR value</div>
          <div className="mono-box">{customer.qr_code_value}</div>
        </div>
      </div>

      <div className="panel">
        <h3 style={{ marginBottom: 8 }}>Recent activity</h3>
        <div className="activity-list">
          {customer.recent_transactions.length ? (
            customer.recent_transactions.map((transaction, index) => (
              <div className="activity-item" key={`${transaction.transaction_type}-${index}`}>
                <div>
                  <strong style={{ textTransform: "capitalize" }}>
                    {transaction.transaction_type.replaceAll("_", " ")}
                  </strong>
                  <p className="muted" style={{ marginBottom: 0 }}>
                    {transaction.comment || "Golden Bite staff action"}
                  </p>
                </div>
                <div style={{ textAlign: "right" }}>
                  <strong className={transaction.points_delta >= 0 ? "positive" : "negative"}>
                    {transaction.points_delta >= 0 ? "+" : ""}
                    {transaction.points_delta} pts
                  </strong>
                  <p className="muted" style={{ marginBottom: 0 }}>
                    {new Date(transaction.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            ))
          ) : (
            <div className="activity-item">
              <div>
                <strong>No recent activity yet</strong>
                <p className="muted" style={{ marginBottom: 0 }}>
                  The next purchase or reward action will appear here.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
