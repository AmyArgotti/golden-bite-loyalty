"use client";

import { useState, useTransition } from "react";

import { AdminLogin } from "../components/admin-login";
import { AuditView } from "../components/audit-view";
import { DashboardView } from "../components/dashboard-view";
import { ExportView } from "../components/export-view";
import { FraudView } from "../components/fraud-view";
import { RulesView } from "../components/rules-view";
import { RulesEditor } from "../components/rules-editor";
import { StaffView } from "../components/staff-view";
import { StaffManagement } from "../components/staff-management";
import { AdminAuditLog, AdminAuth, AdminDashboard, AdminFraudFlag, AdminStaffUser, LoyaltyRules } from "../lib/types";
import {
  createAdminStaff,
  downloadCustomerExport,
  getAdminDashboard,
  getAdminStaff,
  getAuditLogs,
  getFraudFlags,
  getLoyaltyRules,
  requestOtp,
  updateAdminStaff,
  updateLoyaltyRules,
  verifyOtp,
} from "../services/api";

export default function AdminPanelPage() {
  const [phoneNumber, setPhoneNumber] = useState("+79990000001");
  const [statusMessage, setStatusMessage] = useState("Use the admin phone number to open the control room.");
  const [auth, setAuth] = useState<AdminAuth | null>(null);
  const [dashboard, setDashboard] = useState<AdminDashboard | null>(null);
  const [rules, setRules] = useState<LoyaltyRules | null>(null);
  const [staff, setStaff] = useState<AdminStaffUser[]>([]);
  const [auditLogs, setAuditLogs] = useState<AdminAuditLog[]>([]);
  const [fraudFlags, setFraudFlags] = useState<AdminFraudFlag[]>([]);
  const [isPending, startTransition] = useTransition();

  async function handleRequestOtp(nextPhoneNumber: string) {
    try {
      const result = await requestOtp(nextPhoneNumber);
      setStatusMessage(result.message);
    } catch (error) {
      setStatusMessage(`Admin OTP error: ${(error as Error).message}`);
    }
  }

  async function handleVerifyOtp(otpCode: string) {
    try {
      const nextAuth = await verifyOtp(phoneNumber, otpCode);
      setAuth(nextAuth);
      const [dashboardData, rulesData, staffData, auditData, fraudData] = await Promise.all([
        getAdminDashboard(nextAuth.access_token),
        getLoyaltyRules(nextAuth.access_token),
        getAdminStaff(nextAuth.access_token),
        getAuditLogs(nextAuth.access_token),
        getFraudFlags(nextAuth.access_token),
      ]);
      startTransition(() => {
        setDashboard(dashboardData);
        setRules(rulesData);
        setStaff(staffData);
        setAuditLogs(auditData);
        setFraudFlags(fraudData);
      });
      setStatusMessage(`Signed in as ${nextAuth.user.role}. Admin data loaded.`);
    } catch (error) {
      setStatusMessage(`Admin login error: ${(error as Error).message}`);
    }
  }

  async function handleCreateStaff(payload: { phone_number: string; role: string; is_active: boolean }) {
    if (!auth) {
      return;
    }
    try {
      const created = await createAdminStaff(auth.access_token, payload);
      setStaff((current) => [created, ...current]);
      setStatusMessage(`Created ${created.role} user ${created.phone_number}.`);
    } catch (error) {
      setStatusMessage(`Create staff error: ${(error as Error).message}`);
    }
  }

  async function handleUpdateStaff(staffId: string, payload: { role?: string; is_active?: boolean }) {
    if (!auth) {
      return;
    }
    try {
      const updated = await updateAdminStaff(auth.access_token, staffId, payload);
      setStaff((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setStatusMessage(`Updated ${updated.phone_number}.`);
    } catch (error) {
      setStatusMessage(`Update staff error: ${(error as Error).message}`);
    }
  }

  async function handleSaveRules(payload: LoyaltyRules) {
    if (!auth) {
      return;
    }
    try {
      const updated = await updateLoyaltyRules(auth.access_token, payload);
      setRules(updated);
      setStatusMessage("Loyalty rules updated.");
    } catch (error) {
      setStatusMessage(`Rules update error: ${(error as Error).message}`);
    }
  }

  async function handleExportCustomers() {
    if (!auth) {
      return;
    }
    try {
      const csv = await downloadCustomerExport(auth.access_token);
      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "golden-bite-customers.csv";
      anchor.click();
      URL.revokeObjectURL(url);
      setStatusMessage("Customer export downloaded.");
    } catch (error) {
      setStatusMessage(`Export error: ${(error as Error).message}`);
    }
  }

  return (
    <main className="page">
      <section className="hero">
        <div className="stack reveal">
          <div className="panel">
            <div className="brand-strip">
              <img className="brand-logo" src="/golden-bite-logo.jpeg" alt="Golden Bite logo" />
              <div>
                <div className="kicker">Golden Bite Control Room</div>
                <div className="muted">Shawarma and grill</div>
              </div>
            </div>
            <h1 className="headline">One place to run the loyalty program.</h1>
            <p className="muted" style={{ maxWidth: 680 }}>
              Watch store activity, update the reward rules, manage staff access, and keep an eye on exceptions.
            </p>
            <div className="button-row">
              <span className="pill">OTP sign-in</span>
              <span className="pill">Live totals</span>
              <span className="pill">Rules and staff</span>
            </div>
          </div>

          {auth && dashboard && rules ? (
            <>
              <DashboardView dashboard={dashboard} />
              <RulesView rules={rules} />
              <RulesEditor rules={rules} onSave={handleSaveRules} />
              <StaffView staff={staff} />
              <StaffManagement staff={staff} onCreate={handleCreateStaff} onUpdate={handleUpdateStaff} />
              <ExportView onExportCustomers={handleExportCustomers} />
              <FraudView flags={fraudFlags} />
              <AuditView logs={auditLogs} />
            </>
          ) : (
            <AdminLogin
              phoneNumber={phoneNumber}
              setPhoneNumber={setPhoneNumber}
              statusMessage={isPending ? "Loading admin data..." : statusMessage}
              onRequestOtp={handleRequestOtp}
              onVerifyOtp={handleVerifyOtp}
            />
          )}
        </div>

        <aside className="panel stack reveal reveal-delay-1">
          <div>
            <div className="kicker">Seeded Access</div>
            <h2 style={{ marginBottom: 8 }}>Local admin access</h2>
            <p className="muted" style={{ marginTop: 0 }}>
              Use the seeded number below when you are testing locally.
            </p>
          </div>
          <div className="metric">
            <div className="muted">Admin phone</div>
            <p className="metric-value" style={{ fontSize: 24 }}>
              +79178588139
            </p>
          </div>
          <div className="metric">
            <div className="muted">Expected role</div>
            <p className="metric-value" style={{ fontSize: 24 }}>
              admin
            </p>
          </div>
          <div className="metric">
            <div className="muted">Operational view</div>
            <p className="metric-value" style={{ fontSize: 24 }}>
              staff + rules + audit
            </p>
          </div>
        </aside>
      </section>
    </main>
  );
}
