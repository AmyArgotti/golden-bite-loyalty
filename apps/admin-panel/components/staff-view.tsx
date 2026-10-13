import { AdminStaffUser } from "../lib/types";

type StaffViewProps = {
  staff: AdminStaffUser[];
};

export function StaffView({ staff }: StaffViewProps) {
  return (
    <div className="panel stack">
      <div>
        <div className="kicker">Staff Access</div>
        <h2 style={{ marginBottom: 8 }}>Current access roster</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          This is the current list of staff and admin users with login status.
        </p>
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
            <span className="pill">{user.phone_verified_at ? "verified" : "unverified"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
