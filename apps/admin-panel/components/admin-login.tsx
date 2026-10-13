"use client";

import { useEffect, useState } from "react";

type AdminLoginProps = {
  phoneNumber: string;
  setPhoneNumber: (value: string) => void;
  statusMessage: string;
  onRequestOtp: (phoneNumber: string) => Promise<void>;
  onVerifyOtp: (otpCode: string) => Promise<void>;
};

export function AdminLogin({
  phoneNumber,
  setPhoneNumber,
  statusMessage,
  onRequestOtp,
  onVerifyOtp,
}: AdminLoginProps) {
  const [otpCode, setOtpCode] = useState("");
  const [otpRequested, setOtpRequested] = useState(false);
  const demoCode = statusMessage.match(/Demo code:\s*(\d{4,8})/i)?.[1] ?? "";

  useEffect(() => {
    if (demoCode) {
      setOtpCode(demoCode);
    }
  }, [demoCode]);

  async function handleRequestOtp() {
    await onRequestOtp(phoneNumber);
    setOtpRequested(true);
  }

  return (
    <div className="panel stack">
      <div>
        <div className="kicker">Admin Access</div>
        <h2 style={{ marginBottom: 8 }}>Manager sign-in</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          Use the admin phone number. In local testing, the newest code appears here after each request.
        </p>
      </div>

      <div>
        <label className="field-label" htmlFor="admin-phone">
          Admin phone
        </label>
        <input
          id="admin-phone"
          className="field-input"
          value={phoneNumber}
          onChange={(event) => setPhoneNumber(event.target.value)}
          placeholder="+79990000001"
        />
      </div>

      {otpRequested ? (
        <>
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
            <label className="field-label" htmlFor="admin-otp">
              OTP code
            </label>
            <input
              id="admin-otp"
              className="field-input"
              value={otpCode}
              onChange={(event) => setOtpCode(event.target.value)}
              placeholder="123456"
            />
          </div>
          <div className="button-row">
            <button className="button-primary" type="button" onClick={() => onVerifyOtp(otpCode)}>
              Verify admin login
            </button>
            <button className="button-secondary" type="button" onClick={handleRequestOtp}>
              Resend OTP
            </button>
          </div>
        </>
      ) : (
        <button className="button-primary" type="button" onClick={handleRequestOtp}>
          Send code
        </button>
      )}

      <p className={`status-line${statusMessage.toLowerCase().includes("error") || statusMessage.toLowerCase().includes("invalid") ? " error" : ""}`}>
        {statusMessage}
      </p>
      <p className="muted" style={{ margin: 0 }}>
        Local admin: <span className="pill">+79178588139</span>
      </p>
    </div>
  );
}
