# Incident Checklist

Use this checklist when something goes wrong during live service.

## SMS Provider Down

- confirm the issue affects multiple phones
- check recent `auth.send_otp_failed` audit entries
- check Twilio dashboard or provider status page
- inform the manager that customer OTP login is degraded
- if needed, pause loyalty signups until SMS recovers

## Internet Outage

- confirm the restaurant internet is unavailable
- verify whether mobile data can reach the system
- if the whole site is unavailable, pause loyalty activity temporarily
- record purchases that need loyalty credit later
- apply approved manual recovery process after connectivity returns

## Wrong Point Adjustment

- identify the affected customer and transaction time
- review the audit log entry
- calculate the correct balance
- apply a reversing adjustment with a clear comment
- note the reason for the correction

## Wallet Pass Not Updating

- confirm the purchase was registered correctly
- confirm the customer can still open the wallet pass
- check wallet status and recent audit history
- regenerate the pass if needed
- verify wallet web-service URL and pass signing configuration
- if unresolved, advise the customer to reopen or re-add the pass

## When To Escalate Immediately

- repeated OTP failures for multiple customers
- repeated purchase posting failures
- backup failure
- restore uncertainty after data loss
- suspicious large manual adjustments
