"use client";

import { useState } from "react";

import { AdminStaffUser } from "../lib/types";

type StaffManagementProps = {
  staff: AdminStaffUser[];
  onCreate: (payload: { phone_number: string; role: string; is_active: boolean }) => Promise<void>;
  onUpdate: (staffId: string, payload: { role?: string; is_active?: boolean }) => Promise<void>;
};

export function StaffManagement({ staff, onCreate, onUpdate }: StaffManagementProps) {
  const [phoneNumber, setPhoneNumber] = useState("+79990000003");
  const [role, setRole] = useState("staff");

  return (
    <div className="panel stack">
      <div>
        <div className="kicker">Staff Management</div>
        <h2 style={{ marginBottom: 8 }}>Create and update access</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          Add staff, switch roles, and turn access on or off without leaving the control room.
        </p>
      </div>

      <div className="button-row">
        <input className="field-input" value={phoneNumber} onChange={(event) => setPhoneNumber(event.target.value)} />
        <input className="field-input" value={role} onChange={(event) => setRole(event.target.value)} />
        <button
          className="button-primary"
          type="button"
          onClick={() => onCreate({ phone_number: phoneNumber, role, is_active: true })}
        >
          Create user
        </button>
      </div>

      <div className="bonus-list">
        {staff.map((user) => (
          <div className="bonus-row" key={user.id}>
            <div>
              <strong>{user.phone_number}</strong>
              <div className="muted">
                {user.role} • {user.is_active ? "active" : "inactive"}
              </div>
            </div>
            <div className="button-row">
              <button
                className="button-secondary"
                type="button"
                onClick={() => onUpdate(user.id, { is_active: !user.is_active })}
              >
                {user.is_active ? "Disable" : "Enable"}
              </button>
              <button
                className="button-secondary"
                type="button"
                onClick={() =>
                  onUpdate(user.id, {
                    role: user.role === "staff" ? "admin" : "staff",
                  })
                }
              >
                Toggle role
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
