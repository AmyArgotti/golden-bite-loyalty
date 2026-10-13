"use client";

import { useState } from "react";

import { LoyaltyRules } from "../lib/types";

type RulesEditorProps = {
  rules: LoyaltyRules;
  onSave: (payload: LoyaltyRules) => Promise<void>;
};

export function RulesEditor({ rules, onSave }: RulesEditorProps) {
  const [pointsPerRubRatio, setPointsPerRubRatio] = useState(String(rules.points_per_rub_ratio));
  const [firstOrderBonus, setFirstOrderBonus] = useState(String(rules.first_order_bonus));
  const [birthdayBonus, setBirthdayBonus] = useState(String(rules.birthday_bonus));

  return (
    <div className="panel stack">
      <div>
        <div className="kicker">Config Editing</div>
        <h2 style={{ marginBottom: 8 }}>Update the core reward values</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          Update the main earn rate and the bonus values that shape the offer.
        </p>
      </div>

      <div className="rules-form-grid">
        <div>
          <label className="field-label" htmlFor="points-per-rub">Points per RUB</label>
          <input
            id="points-per-rub"
            className="field-input"
            value={pointsPerRubRatio}
            onChange={(event) => setPointsPerRubRatio(event.target.value)}
          />
        </div>
        <div>
          <label className="field-label" htmlFor="first-order-bonus">First order bonus</label>
          <input
            id="first-order-bonus"
            className="field-input"
            value={firstOrderBonus}
            onChange={(event) => setFirstOrderBonus(event.target.value)}
          />
        </div>
        <div>
          <label className="field-label" htmlFor="birthday-bonus">Birthday bonus</label>
          <input
            id="birthday-bonus"
            className="field-input"
            value={birthdayBonus}
            onChange={(event) => setBirthdayBonus(event.target.value)}
          />
        </div>
      </div>

      <button
        className="button-primary"
        type="button"
        onClick={() =>
          onSave({
            ...rules,
            points_per_rub_ratio: Number(pointsPerRubRatio),
            first_order_bonus: Number(firstOrderBonus),
            birthday_bonus: Number(birthdayBonus),
          })
        }
      >
        Save loyalty rules
      </button>
    </div>
  );
}
