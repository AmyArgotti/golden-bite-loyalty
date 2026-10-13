import { AdminDashboard } from "../lib/types";

type DashboardViewProps = {
  dashboard: AdminDashboard;
};

export function DashboardView({ dashboard }: DashboardViewProps) {
  return (
    <div className="panel stack">
      <div>
        <div className="kicker">KPIs</div>
        <h2 style={{ marginBottom: 8 }}>Today at a glance</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          Quick numbers for customers, points, purchases, and review items.
        </p>
      </div>

      <div className="dashboard-grid">
        <div className="metric">
          <div className="muted">Active customers</div>
          <p className="metric-value">{dashboard.active_customers}</p>
          <div className="muted">Members seen recently</div>
        </div>
        <div className="metric">
          <div className="muted">Points issued</div>
          <p className="metric-value">{dashboard.total_points_issued}</p>
          <div className="muted">Total points granted</div>
        </div>
        <div className="metric">
          <div className="muted">Transactions today</div>
          <p className="metric-value">{dashboard.transactions_today}</p>
          <div className="muted">Purchases and redemptions</div>
        </div>
        <div className="metric">
          <div className="muted">Pending fraud flags</div>
          <p className="metric-value">{dashboard.pending_fraud_flags}</p>
          <div className="muted">Needs review</div>
        </div>
      </div>
    </div>
  );
}
