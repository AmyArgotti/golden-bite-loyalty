import { LoyaltyRules } from "../lib/types";

type RulesViewProps = {
  rules: LoyaltyRules;
};

export function RulesView({ rules }: RulesViewProps) {
  return (
    <div className="panel stack">
      <div>
        <div className="kicker">Loyalty Rules</div>
        <h2 style={{ marginBottom: 8 }}>Current reward setup</h2>
        <p className="muted" style={{ marginTop: 0 }}>
          These live settings decide how customers earn, move up tiers, and unlock extras.
        </p>
      </div>

      <div className="rules-grid">
        <div className="tier-list">
          {rules.tiers.length ? (
            rules.tiers.map((tier) => (
              <div className="tier-row" key={tier.name}>
                <div>
                  <strong style={{ textTransform: "capitalize" }}>{tier.name}</strong>
                  <div className="muted">Starts at {tier.min_points} points</div>
                </div>
                <span className="pill">{tier.discount_percent}% discount</span>
              </div>
            ))
          ) : (
            <div className="tier-row">
              <div>
                <strong>No tiers yet</strong>
                <div className="muted">Add at least one tier before launch.</div>
              </div>
            </div>
          )}
        </div>

        <div className="bonus-list">
          <div className="bonus-row">
            <span>Points per RUB</span>
            <strong>{rules.points_per_rub_ratio}</strong>
          </div>
          <div className="bonus-row">
            <span>First order bonus</span>
            <strong>{rules.first_order_bonus}</strong>
          </div>
          <div className="bonus-row">
            <span>Birthday bonus</span>
            <strong>{rules.birthday_bonus}</strong>
          </div>
          <div className="bonus-row">
            <span>Referrer bonus</span>
            <strong>{rules.referral_referrer_bonus}</strong>
          </div>
          <div className="bonus-row">
            <span>Referee bonus</span>
            <strong>{rules.referral_referee_bonus}</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
