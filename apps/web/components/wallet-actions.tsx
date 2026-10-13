"use client";

type WalletActionsProps = {
  walletStatus: string;
  onAddAppleWallet: () => Promise<void>;
  onRefreshWallet: () => Promise<void>;
};

export function WalletActions({ walletStatus, onAddAppleWallet, onRefreshWallet }: WalletActionsProps) {
  return (
    <div className="panel stack">
      <div>
        <div className="brand-kicker">Wallet access</div>
        <h3 style={{ marginBottom: 6 }}>Keep your card in your pocket</h3>
        <p className="muted" style={{ marginTop: 0 }}>
          Add your card to Apple Wallet for faster checkout. Google Wallet support can follow after launch.
        </p>
      </div>

      <div className="button-row">
        <button className="button-primary" type="button" onClick={onAddAppleWallet}>
          Add to Apple Wallet
        </button>
        <button className="button-secondary" type="button" onClick={onRefreshWallet}>
          Refresh wallet card
        </button>
        <button className="button-secondary" type="button" disabled>
          Google Wallet soon
        </button>
      </div>

      <p className="muted wallet-status-line" style={{ margin: 0 }}>
        Current wallet status: {walletStatus}
      </p>
    </div>
  );
}
