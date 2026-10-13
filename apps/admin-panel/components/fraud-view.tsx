"use client";

import { AdminFraudFlag } from "../lib/types";

type FraudViewProps = {
  flags: AdminFraudFlag[];
};

export function FraudView({ flags }: FraudViewProps) {
  return (
    <div className="panel stack">
      <div>
        <div className="kicker">Fraud Review</div>
        <h2 style={{ marginBottom: 8 }}>Review queue</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          This queue highlights unusual OTP behavior and large adjustments for a quick manager review.
        </p>
      </div>

      <div className="audit-list">
        {flags.length ? (
          flags.map((flag, index) => (
            <div className="audit-row" key={`${flag.flag_type}-${flag.created_at}-${index}`}>
              <div>
                <strong>{flag.flag_type}</strong>
                <div className="muted">
                  {flag.severity} {flag.related_value ? `• ${flag.related_value}` : ""}
                </div>
                <div className="muted">{flag.description}</div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div className="muted">{new Date(flag.created_at).toLocaleString()}</div>
              </div>
            </div>
          ))
        ) : (
          <p className="muted" style={{ marginBottom: 0 }}>
            No active fraud flags detected from current data.
          </p>
        )}
      </div>
    </div>
  );
}
