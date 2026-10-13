"use client";

type ExportViewProps = {
  onExportCustomers: () => Promise<void>;
};

export function ExportView({ onExportCustomers }: ExportViewProps) {
  return (
    <div className="panel stack">
      <div>
        <div className="kicker">Reporting</div>
        <h2 style={{ marginBottom: 8 }}>Export the member list</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          Download a CSV with balances, tiers, consent status, and latest activity.
        </p>
      </div>

      <div className="button-row">
        <button className="button-primary" type="button" onClick={() => void onExportCustomers()}>
          Download customer CSV
        </button>
      </div>
    </div>
  );
}
