"use client";

import { useState, useTransition } from "react";

import { demoLoyalty, demoTransactions } from "../lib/demo";

import { Dashboard } from "../components/dashboard";
import { LoginPanel } from "../components/login-panel";
import { ProfilePanel } from "../components/profile-panel";
import { WalletActions } from "../components/wallet-actions";
import { AuthTokens, LoyaltyDashboard, LoyaltyTransaction, MeProfile } from "../lib/types";
import {
  addAppleWallet,
  getLoyalty,
  getMe,
  getTransactions,
  getWalletStatus,
  refreshWallet,
  requestOtp,
  updateProfile,
  verifyOtp,
} from "../services/api";

export default function HomePage() {
  const [demoMode, setDemoMode] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState("+79991234567");
  const [statusMessage, setStatusMessage] = useState("Request an OTP to open your Golden Bite card.");
  const [tokens, setTokens] = useState<AuthTokens | null>(null);
  const [profile, setProfile] = useState<MeProfile | null>(null);
  const [loyalty, setLoyalty] = useState<LoyaltyDashboard | null>(null);
  const [transactions, setTransactions] = useState<LoyaltyTransaction[]>([]);
  const [walletStatus, setWalletStatus] = useState("not_added");
  const [isPending, startTransition] = useTransition();

  async function handleRequestOtp(nextPhoneNumber: string) {
    try {
      const result = await requestOtp(nextPhoneNumber);
      setStatusMessage(result.message);
    } catch (error) {
      setStatusMessage(`Error requesting OTP: ${(error as Error).message}`);
    }
  }

  async function handleVerifyOtp(otpCode: string) {
    try {
      const auth = await verifyOtp(phoneNumber, otpCode);

      const [me, loyaltyData, transactionData, walletData] = await Promise.all([
        getMe(auth.access_token),
        getLoyalty(auth.access_token),
        getTransactions(auth.access_token),
        getWalletStatus(auth.access_token),
      ]);

      startTransition(() => {
        setTokens({ access_token: auth.access_token, refresh_token: auth.refresh_token });
        setStatusMessage(auth.is_new_user ? "Account created. Loyalty card ready." : "Welcome back.");
        setProfile(me);
        setLoyalty(loyaltyData);
        setTransactions(transactionData);
        setWalletStatus(walletData.status);
      });
    } catch (error) {
      setStatusMessage(`Error verifying OTP: ${(error as Error).message}`);
    }
  }

  async function handleProfileSave(payload: {
    full_name: string | null;
    birthday: string | null;
    marketing_sms_consent: boolean;
  }) {
    if (!tokens) {
      return;
    }
    try {
      const me = await updateProfile(tokens.access_token, payload);
      setProfile(me);
      setStatusMessage("Profile updated.");
    } catch (error) {
      setStatusMessage(`Error updating profile: ${(error as Error).message}`);
    }
  }

  async function handleAddAppleWallet() {
    if (!tokens) {
      return;
    }
    try {
      const result = await addAppleWallet(tokens.access_token);
      setStatusMessage(`Apple Wallet pass ready: ${result.download_url}`);
      setWalletStatus("active");
    } catch (error) {
      setStatusMessage(`Error creating wallet pass: ${(error as Error).message}`);
    }
  }

  async function handleRefreshWallet() {
    if (!tokens) {
      return;
    }
    try {
      const result = await refreshWallet(tokens.access_token);
      setWalletStatus(result.status);
      setStatusMessage("Wallet status refreshed.");
    } catch (error) {
      setStatusMessage(`Error refreshing wallet: ${(error as Error).message}`);
    }
  }

  const previewLoyalty = demoMode ? demoLoyalty : loyalty;

  return (
    <main className="page-shell">
      <section className="hero">
        <div className="stack reveal">
          <div className="panel hero-panel">
            <div className="brand-mark">
              <img className="brand-logo" src="/golden-bite-logo.jpeg" alt="Golden Bite logo" />
              <div className="brand-copy">
                <strong>Golden Bite</strong>
                <span>Shawarma and grill</span>
              </div>
            </div>
            <div className="brand-kicker">Black card loyalty</div>
            <h1 className="headline">Your Golden Bite card, ready in seconds.</h1>
            <p className="subhead">
              Sign in with your phone, collect points on every order, and keep your card ready at the counter. Your
              balance and rewards update after every purchase.
            </p>
            <div className="hero-pill-row">
              <span className="card-badge">OTP login</span>
              <span className="card-badge">Fast points</span>
              <span className="card-badge">Wallet-ready card</span>
              <span className="card-badge">Tier discounts</span>
            </div>
          </div>

          {demoMode ? (
            <>
              <div className="panel stack">
                <div className="brand-kicker">Interactive preview</div>
                <h2 style={{ margin: 0 }}>Meet your member dashboard</h2>
                <p className="muted" style={{ margin: 0 }}>Explore a fictional member card and recent activity. This preview uses sample data.</p>
                <button className="button-secondary" type="button" onClick={() => setDemoMode(false)}>Back to sign in</button>
              </div>
              <Dashboard phoneNumber="Demo member" fullName="Alex Morgan" loyalty={demoLoyalty} transactions={demoTransactions} />
            </>
          ) : tokens && loyalty ? (
            <>
              <Dashboard
                phoneNumber={phoneNumber}
                fullName={profile?.profile.full_name ?? null}
                loyalty={{ ...loyalty, wallet_status: walletStatus }}
                transactions={transactions}
              />
              <ProfilePanel
                fullName={profile?.profile.full_name ?? null}
                birthday={profile?.profile.birthday ?? null}
                marketingSmsConsent={profile?.profile.marketing_sms_consent ?? false}
                onSave={handleProfileSave}
              />
              <WalletActions
                walletStatus={walletStatus}
                onAddAppleWallet={handleAddAppleWallet}
                onRefreshWallet={handleRefreshWallet}
              />
            </>
          ) : (
            <>
            <div className="panel stack">
              <div className="brand-kicker">Take a look inside</div>
              <p className="muted" style={{ margin: 0 }}>Discover the member experience with a sample loyalty card.</p>
              <button className="button-primary" type="button" onClick={() => setDemoMode(true)}>Explore demo</button>
            </div>
            <LoginPanel
              onOtpRequested={handleRequestOtp}
              onOtpVerified={handleVerifyOtp}
              phoneNumber={phoneNumber}
              setPhoneNumber={setPhoneNumber}
              statusMessage={isPending ? "Loading your dashboard..." : statusMessage}
            />
            </>
          )}
        </div>

        <aside className="panel reveal reveal-delay-1">
          <div className="card-preview floating-card">
            <div className="card-badge">Golden Bite Black Card</div>
            {!tokens && <span className="muted">Sample member card</span>}
            <div>
              <p style={{ opacity: 0.75, marginBottom: 4 }}>Tier</p>
              <h2 style={{ margin: 0, textTransform: "capitalize" }}>{previewLoyalty?.tier ?? "Silver"}</h2>
            </div>
            <div>
              <p style={{ opacity: 0.75, marginBottom: 4 }}>Points balance</p>
              <h3 style={{ margin: 0, fontSize: 36 }}>{previewLoyalty?.points_balance ?? 1280}</h3>
            </div>
            <div>
              <p style={{ opacity: 0.75, marginBottom: 4 }}>Barcode</p>
              <strong>{previewLoyalty?.barcode_value ?? "100001"}</strong>
            </div>
            <div>
              <p style={{ opacity: 0.75, marginBottom: 4 }}>Wallet</p>
              <strong>{demoMode ? "Sample card" : walletStatus.replaceAll("_", " ")}</strong>
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}
