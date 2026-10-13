"use client";

import { useMemo, useState } from "react";

import { CustomerDetail } from "../components/customer-detail";
import { CustomerOperations } from "../components/customer-operations";
import { CustomerSearch } from "../components/customer-search";
import { ScanPanel } from "../components/scan-panel";
import { StaffLogin } from "../components/staff-login";
import { PurchaseResult, StaffAuth, StaffCustomer, StaffCustomerDetail, StaffOperationResult } from "../lib/types";
import {
  adjustPoints,
  getCustomerDetail,
  redeemPoints,
  registerPurchase,
  requestOtp,
  searchCustomers,
  scanCustomer,
  verifyOtp,
} from "../services/api";

export default function StaffPanelPage() {
  const [staffPhoneNumber, setStaffPhoneNumber] = useState("+79990000002");
  const [auth, setAuth] = useState<StaffAuth | null>(null);
  const [statusMessage, setStatusMessage] = useState("Sign in with the staff phone number to open the counter tools.");
  const [searchPhoneNumber, setSearchPhoneNumber] = useState("");
  const [searchMemberId, setSearchMemberId] = useState("");
  const [customers, setCustomers] = useState<StaffCustomer[]>([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState<string | null>(null);
  const [selectedCustomerDetail, setSelectedCustomerDetail] = useState<StaffCustomerDetail | null>(null);
  const [lastResult, setLastResult] = useState<PurchaseResult | StaffOperationResult | null>(null);

  const selectedCustomer = useMemo(
    () => customers.find((customer) => customer.customer_id === selectedCustomerId) ?? null,
    [customers, selectedCustomerId],
  );

  async function handleRequestOtp(phoneNumber: string) {
    try {
      const result = await requestOtp(phoneNumber);
      setStatusMessage(result.message);
    } catch (error) {
      setStatusMessage(`Staff OTP error: ${(error as Error).message}`);
    }
  }

  async function handleVerifyOtp(otpCode: string) {
    try {
      const nextAuth = await verifyOtp(staffPhoneNumber, otpCode);
      setAuth(nextAuth);
      setStatusMessage(`Signed in as ${nextAuth.user.role}. Search a customer to continue.`);
    } catch (error) {
      setStatusMessage(`Staff login error: ${(error as Error).message}`);
    }
  }

  async function handleSearch() {
    if (!auth) {
      return;
    }
    try {
      const results = await searchCustomers(auth.access_token, {
        phoneNumber: searchPhoneNumber || undefined,
        memberId: searchMemberId || undefined,
      });
      setCustomers(results);
      const nextCustomerId = results[0]?.customer_id ?? null;
      setSelectedCustomerId(nextCustomerId);
      if (nextCustomerId) {
        setSelectedCustomerDetail(await getCustomerDetail(auth.access_token, nextCustomerId));
      } else {
        setSelectedCustomerDetail(null);
      }
      setStatusMessage(results.length ? `Found ${results.length} customer record(s).` : "No customers found.");
    } catch (error) {
      setStatusMessage(`Search error: ${(error as Error).message}`);
    }
  }

  async function handleSelectCustomer(customer: StaffCustomer) {
    if (!auth) {
      return;
    }
    setSelectedCustomerId(customer.customer_id);
    try {
      const detail = await getCustomerDetail(auth.access_token, customer.customer_id);
      setSelectedCustomerDetail(detail);
    } catch (error) {
      setStatusMessage(`Customer detail error: ${(error as Error).message}`);
    }
  }

  async function refreshSelectedCustomerDetail(customerId: string) {
    if (!auth) {
      return;
    }
    const detail = await getCustomerDetail(auth.access_token, customerId);
    setSelectedCustomerDetail(detail);
  }

  async function handleScan(scanValue: string) {
    if (!auth) {
      return;
    }
    try {
      const detail = await scanCustomer(auth.access_token, scanValue);
      const summaryCustomer: StaffCustomer = {
        customer_id: detail.customer_id,
        member_id: detail.member_id,
        phone_number: detail.phone_number,
        points_balance: detail.points_balance,
        tier: detail.tier,
      };
      setCustomers((current) => {
        const existing = current.find((item) => item.customer_id === detail.customer_id);
        if (existing) {
          return current.map((item) => (item.customer_id === detail.customer_id ? summaryCustomer : item));
        }
        return [summaryCustomer, ...current];
      });
      setSelectedCustomerId(detail.customer_id);
      setSelectedCustomerDetail(detail);
      setStatusMessage(`Customer found by scan: ${detail.member_id}`);
    } catch (error) {
      setStatusMessage(`Scan error: ${(error as Error).message}`);
    }
  }

  function patchSelectedCustomer(pointsBalance: number, tier: string) {
    if (!selectedCustomer) {
      return;
    }
    setCustomers((current) =>
      current.map((customer) =>
        customer.customer_id === selectedCustomer.customer_id ? { ...customer, points_balance: pointsBalance, tier } : customer,
      ),
    );
    setSelectedCustomerDetail((current) =>
      current
        ? {
            ...current,
            points_balance: pointsBalance,
            tier,
          }
        : current,
    );
  }

  async function handlePurchase(payload: { purchaseAmount: number; orderReference: string }) {
    if (!auth || !selectedCustomer) {
      return;
    }
    try {
      const result = await registerPurchase(auth.access_token, {
        customer_id: selectedCustomer.customer_id,
        purchase_amount: payload.purchaseAmount,
        order_reference: payload.orderReference,
      });
      patchSelectedCustomer(result.new_points_balance, result.new_tier);
      await refreshSelectedCustomerDetail(selectedCustomer.customer_id);
      setLastResult(result);
      setStatusMessage(`Purchase saved. Added ${result.total_points_added} points including bonuses.`);
    } catch (error) {
      setStatusMessage(`Purchase error: ${(error as Error).message}`);
    }
  }

  async function handleRedeem(payload: { pointsToRedeem: number; comment: string }) {
    if (!auth || !selectedCustomer) {
      return;
    }
    try {
      const result = await redeemPoints(auth.access_token, {
        customer_id: selectedCustomer.customer_id,
        points_to_redeem: payload.pointsToRedeem,
        comment: payload.comment,
      });
      patchSelectedCustomer(result.points_balance, result.tier);
      await refreshSelectedCustomerDetail(selectedCustomer.customer_id);
      setLastResult(result);
      setStatusMessage(result.message);
    } catch (error) {
      setStatusMessage(`Redeem error: ${(error as Error).message}`);
    }
  }

  async function handleAdjust(payload: { pointsDelta: number; comment: string }) {
    if (!auth || !selectedCustomer) {
      return;
    }
    try {
      const result = await adjustPoints(auth.access_token, {
        customer_id: selectedCustomer.customer_id,
        points_delta: payload.pointsDelta,
        comment: payload.comment,
      });
      patchSelectedCustomer(result.points_balance, result.tier);
      await refreshSelectedCustomerDetail(selectedCustomer.customer_id);
      setLastResult(result);
      setStatusMessage(result.message);
    } catch (error) {
      setStatusMessage(`Adjustment error: ${(error as Error).message}`);
    }
  }

  return (
    <main className="page">
      <section className="panel hero-panel reveal" style={{ marginBottom: 18 }}>
        <div className="brand-strip">
          <img className="brand-logo" src="/golden-bite-logo.jpeg" alt="Golden Bite logo" />
          <div>
            <div className="kicker">Golden Bite Operations</div>
            <div className="muted">Shawarma and grill</div>
          </div>
        </div>
        <h1 className="headline">Counter tools built for a busy shift.</h1>
        <p className="muted" style={{ maxWidth: 760 }}>
          Find the customer, add the order, redeem points, and fix balances without slowing the line down.
        </p>
        <div className="hero-pill-row">
          <span className="code-pill">Fast member lookup</span>
          <span className="code-pill">Live points updates</span>
          <span className="code-pill">Built for the cashier line</span>
        </div>
      </section>

      {!auth ? (
        <StaffLogin
          phoneNumber={staffPhoneNumber}
          setPhoneNumber={setStaffPhoneNumber}
          statusMessage={statusMessage}
          onRequestOtp={handleRequestOtp}
          onVerifyOtp={handleVerifyOtp}
        />
      ) : (
        <div className="shell">
          <div className="stack reveal">
            <CustomerSearch
              phoneNumber={searchPhoneNumber}
              setPhoneNumber={setSearchPhoneNumber}
              memberId={searchMemberId}
              setMemberId={setSearchMemberId}
              customers={customers}
              selectedCustomerId={selectedCustomerId}
              onSearch={handleSearch}
              onSelectCustomer={handleSelectCustomer}
            />
            <ScanPanel onScan={handleScan} />
          </div>

          <div className="stack reveal reveal-delay-1">
            <div className="panel active-session-panel">
              <div className="button-row" style={{ justifyContent: "space-between", alignItems: "center" }}>
                <strong>{auth.user.role.toUpperCase()} session active</strong>
                <span className="code-pill">{staffPhoneNumber}</span>
              </div>
              <p className="status-line" style={{ marginTop: 12 }}>
                {statusMessage}
              </p>
              {lastResult ? (
                <p className="muted" style={{ marginBottom: 0 }}>
                  Latest result: {"total_points_added" in lastResult
                    ? `${lastResult.new_points_balance} pts • ${lastResult.new_tier} tier`
                    : `${lastResult.points_balance} pts • ${lastResult.tier} tier`}
                </p>
              ) : null}
            </div>

            <CustomerOperations
              customer={selectedCustomer}
              onPurchase={handlePurchase}
              onRedeem={handleRedeem}
              onAdjust={handleAdjust}
            />
            <CustomerDetail customer={selectedCustomerDetail} />
          </div>
        </div>
      )}
    </main>
  );
}
