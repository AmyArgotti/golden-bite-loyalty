"use client";

import { StaffCustomer } from "../lib/types";
import { useState } from "react";

type CustomerOperationsProps = {
  customer: StaffCustomer | null;
  onPurchase: (payload: { purchaseAmount: number; orderReference: string }) => Promise<void>;
  onRedeem: (payload: { pointsToRedeem: number; comment: string }) => Promise<void>;
  onAdjust: (payload: { pointsDelta: number; comment: string }) => Promise<void>;
};

export function CustomerOperations({ customer, onPurchase, onRedeem, onAdjust }: CustomerOperationsProps) {
  const [purchaseAmount, setPurchaseAmount] = useState("1350");
  const [orderReference, setOrderReference] = useState("ORDER-1055");
  const [pointsToRedeem, setPointsToRedeem] = useState("100");
  const [redeemComment, setRedeemComment] = useState("Reward applied at checkout");
  const [pointsDelta, setPointsDelta] = useState("50");
  const [adjustComment, setAdjustComment] = useState("Compensation for service issue");

  if (!customer) {
    return (
      <div className="panel active-customer-panel">
        <h3>Select a customer</h3>
        <p className="muted" style={{ marginBottom: 0 }}>
          Search and select a loyalty member to enable checkout actions.
        </p>
      </div>
    );
  }

  return (
    <div className="stack">
      <div className="panel">
        <div className="kicker">Active Customer</div>
        <h2 style={{ marginBottom: 8 }}>{customer.member_id}</h2>
        <div className="summary-grid">
          <div className="summary-card">
            <div className="muted">Phone</div>
            <strong>{customer.phone_number}</strong>
          </div>
          <div className="summary-card">
            <div className="muted">Points</div>
            <strong>{customer.points_balance}</strong>
          </div>
          <div className="summary-card">
            <div className="muted">Tier</div>
            <strong style={{ textTransform: "capitalize" }}>{customer.tier}</strong>
          </div>
          <div className="summary-card">
            <div className="muted">Customer ID</div>
            <strong>{customer.customer_id.slice(0, 8)}</strong>
          </div>
        </div>
      </div>

      <div className="operations">
        <div className="panel stack operation-card">
          <div className="operation-tag">Earn</div>
          <h3 style={{ marginBottom: 0 }}>Register purchase</h3>
          <div>
            <label className="field-label">Purchase amount</label>
            <input
              className="field-input"
              value={purchaseAmount}
              onChange={(event) => setPurchaseAmount(event.target.value)}
            />
          </div>
          <div>
            <label className="field-label">Order reference</label>
            <input
              className="field-input"
              value={orderReference}
              onChange={(event) => setOrderReference(event.target.value)}
            />
          </div>
          <button
            className="button-primary"
            type="button"
            onClick={() => onPurchase({ purchaseAmount: Number(purchaseAmount), orderReference })}
          >
            Add purchase and points
          </button>
        </div>

        <div className="panel stack operation-card">
          <div className="operation-tag">Redeem</div>
          <h3 style={{ marginBottom: 0 }}>Redeem reward</h3>
          <div>
            <label className="field-label">Points to redeem</label>
            <input
              className="field-input"
              value={pointsToRedeem}
              onChange={(event) => setPointsToRedeem(event.target.value)}
            />
          </div>
          <div>
            <label className="field-label">Comment</label>
            <input
              className="field-input"
              value={redeemComment}
              onChange={(event) => setRedeemComment(event.target.value)}
            />
          </div>
          <button
            className="button-secondary"
            type="button"
            onClick={() => onRedeem({ pointsToRedeem: Number(pointsToRedeem), comment: redeemComment })}
          >
            Redeem points
          </button>
        </div>

        <div className="panel stack operation-card">
          <div className="operation-tag">Adjust</div>
          <h3 style={{ marginBottom: 0 }}>Manual adjustment</h3>
          <div>
            <label className="field-label">Points delta</label>
            <input className="field-input" value={pointsDelta} onChange={(event) => setPointsDelta(event.target.value)} />
          </div>
          <div>
            <label className="field-label">Comment</label>
            <input
              className="field-input"
              value={adjustComment}
              onChange={(event) => setAdjustComment(event.target.value)}
            />
          </div>
          <button
            className={Number(pointsDelta) < 0 ? "button-danger" : "button-primary"}
            type="button"
            onClick={() => onAdjust({ pointsDelta: Number(pointsDelta), comment: adjustComment })}
          >
            Save adjustment
          </button>
        </div>
      </div>
    </div>
  );
}
