import { QRCodeSVG } from "qrcode.react";
import Barcode from "react-barcode";
import { LoyaltyDashboard, LoyaltyTransaction } from "../lib/types";

type DashboardProps = {
  phoneNumber: string;
  fullName: string | null;
  loyalty: LoyaltyDashboard;
  transactions: LoyaltyTransaction[];
};

export function Dashboard({ phoneNumber, fullName, loyalty, transactions }: DashboardProps) {
  return (
    <div className="stack">
      <div className="panel premium-dashboard">
        <div className="brand-kicker">Welcome back</div>
        <h2 style={{ margin: "6px 0" }}>{fullName || "Golden Bite Member"}</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          {phoneNumber} • Member {loyalty.member_id}
        </p>

        <div className="hero-pill-row" style={{ marginTop: 8 }}>
          <span className="card-badge">Ready at checkout</span>
          <span className="card-badge">{loyalty.discount_percent}% member discount</span>
          <span className="card-badge" style={{ textTransform: "capitalize" }}>{loyalty.tier} tier</span>
        </div>

        <div className="barcode-panel">
          <div>
            <p className="muted" style={{ marginTop: 0, marginBottom: 6 }}>
              Scan at checkout
            </p>
            <div className="member-qr">
              <QRCodeSVG value={loyalty.qr_code_value} size={128} marginSize={4} title={`Member ${loyalty.member_id}`} />
            </div>
          </div>
          <div>
            <p className="muted" style={{ marginTop: 0, marginBottom: 6 }}>
              Barcode
            </p>
            <div className="member-barcode" role="img" aria-label={`Member barcode ${loyalty.barcode_value}`}>
              <Barcode value={loyalty.barcode_value} format="CODE128" width={1.4} height={64} fontSize={16} margin={12} />
            </div>
          </div>
        </div>

        <div className="stats-grid">
          <div className="stat">
            <p className="muted" style={{ marginTop: 0 }}>
              Points
            </p>
            <p className="stat-value">{loyalty.points_balance}</p>
          </div>
          <div className="stat">
            <p className="muted" style={{ marginTop: 0 }}>
              Tier
            </p>
            <p className="stat-value" style={{ textTransform: "capitalize" }}>
              {loyalty.tier}
            </p>
          </div>
          <div className="stat">
            <p className="muted" style={{ marginTop: 0 }}>
              Discount
            </p>
            <p className="stat-value">{loyalty.discount_percent}%</p>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="button-row" style={{ justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h3 style={{ marginBottom: 6 }}>Recent activity</h3>
            <p className="muted" style={{ margin: 0 }}>
              Every order, reward, and balance change shows up here.
            </p>
          </div>
          <div className="card-badge">
            Wallet: {loyalty.wallet_status}
          </div>
        </div>

        <div className="history-list">
          {transactions.length ? (
            transactions.map((transaction, index) => (
              <div className="history-item" key={`${transaction.transaction_type}-${index}`}>
                <div>
                  <strong style={{ textTransform: "capitalize" }}>
                    {transaction.transaction_type.replaceAll("_", " ")}
                  </strong>
                  <p className="muted" style={{ marginBottom: 0 }}>
                    {transaction.comment || "Golden Bite loyalty activity"}
                  </p>
                </div>
                <div style={{ textAlign: "right" }}>
                  <strong className={transaction.points_delta >= 0 ? "success" : "error-text"}>
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
            <div className="history-item">
              <div>
                <strong>No activity yet</strong>
                <p className="muted" style={{ marginBottom: 0 }}>
                  Your first order will appear here right after checkout.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
