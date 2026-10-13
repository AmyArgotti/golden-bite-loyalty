import { AdminAuditLog } from "../lib/types";

type AuditViewProps = {
  logs: AdminAuditLog[];
};

export function AuditView({ logs }: AuditViewProps) {
  return (
    <div className="panel stack">
      <div>
        <div className="kicker">Audit Trail</div>
        <h2 style={{ marginBottom: 8 }}>Recent activity</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          Every sign-in and points-changing action lands here for review.
        </p>
      </div>

      <div className="audit-list">
        {logs.length ? (
          logs.map((log) => (
            <div className="audit-row" key={log.id}>
              <div>
                <strong>{log.action}</strong>
                <div className="muted">
                  {log.actor_role} • {log.entity_type}
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div className="muted">{new Date(log.created_at).toLocaleString()}</div>
                <div className="muted">{log.entity_id ? log.entity_id.slice(0, 8) : "no-entity"}</div>
              </div>
            </div>
          ))
        ) : (
          <p className="muted" style={{ marginBottom: 0 }}>
            No audit entries yet.
          </p>
        )}
      </div>
    </div>
  );
}
