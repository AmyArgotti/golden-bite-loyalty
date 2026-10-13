"use client";

import { StaffCustomer } from "../lib/types";

type CustomerSearchProps = {
  phoneNumber: string;
  setPhoneNumber: (value: string) => void;
  memberId: string;
  setMemberId: (value: string) => void;
  customers: StaffCustomer[];
  selectedCustomerId: string | null;
  onSearch: () => Promise<void>;
  onSelectCustomer: (customer: StaffCustomer) => void;
};

export function CustomerSearch({
  phoneNumber,
  setPhoneNumber,
  memberId,
  setMemberId,
  customers,
  selectedCustomerId,
  onSearch,
  onSelectCustomer,
}: CustomerSearchProps) {
  return (
    <div className="panel stack">
      <div>
        <div className="kicker">Lookup</div>
        <h3 style={{ marginBottom: 8 }}>Find the customer fast</h3>
        <p className="muted" style={{ marginTop: 0 }}>
          Search by phone or member ID, then lock in the active customer before you add the order.
        </p>
      </div>

      <div>
        <label className="field-label" htmlFor="search-phone">
          Phone number
        </label>
        <input
          id="search-phone"
          className="field-input"
          value={phoneNumber}
          onChange={(event) => setPhoneNumber(event.target.value)}
          placeholder="+79991234567"
        />
      </div>

      <div>
        <label className="field-label" htmlFor="search-member">
          Member ID
        </label>
        <input
          id="search-member"
          className="field-input"
          value={memberId}
          onChange={(event) => setMemberId(event.target.value)}
          placeholder="GB-100001"
        />
      </div>

      <button className="button-primary" type="button" onClick={onSearch}>
        Search customers
      </button>

      <div className="list">
        {customers.map((customer) => (
          <button
            key={customer.customer_id}
            className={`customer-row${selectedCustomerId === customer.customer_id ? " active" : ""}`}
            type="button"
            onClick={() => onSelectCustomer(customer)}
          >
            <strong>{customer.member_id}</strong>
            <div className="muted">{customer.phone_number}</div>
            <div className="muted">
              {customer.points_balance} pts • {customer.tier}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
