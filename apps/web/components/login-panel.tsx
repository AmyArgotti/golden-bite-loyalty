"use client";

import { useEffect, useState } from "react";

type LoginPanelProps = {
  onOtpRequested: (phoneNumber: string) => Promise<void>;
  onOtpVerified: (otpCode: string) => Promise<void>;
  phoneNumber: string;
  setPhoneNumber: (value: string) => void;
  statusMessage: string;
};

export function LoginPanel({
  onOtpRequested,
  onOtpVerified,
  phoneNumber,
  setPhoneNumber,
  statusMessage,
}: LoginPanelProps) {
  const [otpCode, setOtpCode] = useState("");
  const [otpRequested, setOtpRequested] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const demoCode = statusMessage.match(/Demo code:\s*(\d{4,8})/i)?.[1] ?? "";

  useEffect(() => {
    if (demoCode) {
      setOtpCode(demoCode);
    }
  }, [demoCode]);

  async function handleRequestOtp() {
    setSubmitting(true);
    try {
      await onOtpRequested(phoneNumber);
      setOtpRequested(true);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleVerifyOtp() {
    setSubmitting(true);
    try {
      await onOtpVerified(otpCode);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="panel stack">
      <div>
        <div className="brand-kicker">Golden Bite Access</div>
        <h2 style={{ marginBottom: 8 }}>Enter your phone to unlock your card</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          Enter your phone number to receive a one-time sign-in code.
        </p>
      </div>

      <div className="onboarding-grid">
        <div className="onboarding-step">
          <strong>1. Enter your phone</strong>
          <p className="muted" style={{ marginBottom: 0 }}>We send a one-time code to open your card.</p>
        </div>
        <div className="onboarding-step">
          <strong>2. Verify once</strong>
          <p className="muted" style={{ marginBottom: 0 }}>After that, your points, tier, and wallet card are ready.</p>
        </div>
      </div>

      <div>
        <label className="field-label" htmlFor="phone">
          Phone number
        </label>
        <input
          id="phone"
          type="tel"
          autoComplete="tel"
          className="field-input"
          placeholder="+79991234567"
          value={phoneNumber}
          onChange={(event) => setPhoneNumber(event.target.value)}
        />
      </div>

      {otpRequested ? (
        <div className="otp-grid">
          {demoCode ? (
            <div className="demo-code-card">
              <div>
                <div className="field-label" style={{ marginBottom: 4 }}>
                  Latest test code
                </div>
                <strong className="demo-code-value">{demoCode}</strong>
              </div>
              <button className="button-secondary" type="button" onClick={() => setOtpCode(demoCode)}>
                Use this code
              </button>
            </div>
          ) : null}
          <div>
            <label className="field-label" htmlFor="otp">
              OTP code
            </label>
            <input
              id="otp"
              inputMode="numeric"
              autoComplete="one-time-code"
              className="field-input"
              placeholder="123456"
              value={otpCode}
              onChange={(event) => setOtpCode(event.target.value)}
            />
          </div>
          <div className="button-row">
            <button className="button-primary" type="button" disabled={submitting} onClick={handleVerifyOtp}>
              Verify code
            </button>
            <button className="button-secondary" type="button" disabled={submitting} onClick={handleRequestOtp}>
              Resend OTP
            </button>
          </div>
        </div>
      ) : (
        <button className="button-primary" type="button" disabled={submitting} onClick={handleRequestOtp}>
          Send code
        </button>
      )}

      <p
        className={statusMessage.toLowerCase().includes("error") || statusMessage.toLowerCase().includes("invalid") ? "error-text" : "success"}
        style={{ margin: 0 }}
        role="status"
        aria-live="polite"
      >
        {statusMessage}
      </p>

      {!otpRequested ? (
        <p className="muted helper-line" style={{ margin: 0 }}>
          New here? Your card is created automatically after the first successful sign-in.
        </p>
      ) : null}
    </div>
  );
}
