"use client";

import { useState } from "react";

type ProfilePanelProps = {
  fullName: string | null;
  birthday: string | null;
  marketingSmsConsent: boolean;
  onSave: (payload: { full_name: string | null; birthday: string | null; marketing_sms_consent: boolean }) => Promise<void>;
};

export function ProfilePanel({ fullName, birthday, marketingSmsConsent, onSave }: ProfilePanelProps) {
  const [nameValue, setNameValue] = useState(fullName ?? "");
  const [birthdayValue, setBirthdayValue] = useState(birthday ?? "");
  const [consent, setConsent] = useState(marketingSmsConsent);
  const [saving, setSaving] = useState(false);

  async function handleSave() {
    setSaving(true);
    try {
      await onSave({
        full_name: nameValue || null,
        birthday: birthdayValue || null,
        marketing_sms_consent: consent,
      });
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="panel stack">
      <div>
        <div className="brand-kicker">Member profile</div>
        <h3 style={{ marginBottom: 6 }}>Keep your profile ready</h3>
        <p className="muted" style={{ marginTop: 0 }}>
          Keep your name and birthday current so your rewards and support stay smooth.
        </p>
      </div>

      <div>
        <label className="field-label" htmlFor="profile-name">
          Full name
        </label>
        <input
          id="profile-name"
          className="field-input"
          value={nameValue}
          onChange={(event) => setNameValue(event.target.value)}
          placeholder="Amy Argotti"
        />
      </div>

      <div>
        <label className="field-label" htmlFor="profile-birthday">
          Birthday
        </label>
        <input
          id="profile-birthday"
          className="field-input"
          type="date"
          value={birthdayValue}
          onChange={(event) => setBirthdayValue(event.target.value)}
        />
      </div>

      <label className="checkbox-row">
        <input type="checkbox" checked={consent} onChange={(event) => setConsent(event.target.checked)} />
        <span>Allow Golden Bite to send loyalty updates and occasional offers</span>
      </label>

      <div className="button-row">
        <button className="button-primary" type="button" onClick={handleSave} disabled={saving}>
          Save profile
        </button>
      </div>
    </div>
  );
}
