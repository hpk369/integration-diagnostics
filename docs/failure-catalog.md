# Failure catalog

The label spec for the eval set and the first draft of the KB articles P2 will ingest.
One entry per issue type. Fill an entry in when its ticket asks you to.

**Entry template**

```markdown
## <issue_type>

- **What the customer says:** one quote, in their words
- **Evidence signature:** what the parsers and checks see
- **Root cause:** one or two sentences
- **Fix:** numbered steps, for whoever owns it
- **Class / owner:** configuration | expected_behavior | product_defect | specialist_owned / customer_admin | customer_dev | engineering | billing | support
- **Customer-facing sentence:** how you'd explain it in a reply
```

| # | issue_type | Class | Owner | Entry written |
| --- | --- | --- | --- | --- |
| 1 | saml_clock_skew | configuration | customer_admin | [ ] |
| 2 | saml_audience_mismatch | configuration | customer_admin | [ ] |
| 3 | saml_signing_cert_rotated | configuration | customer_admin | [ ] |
| 4 | saml_nameid_mismatch | configuration | customer_admin | [ ] |
| 5 | oidc_redirect_uri_mismatch | configuration | customer_admin | [ ] |
| 6 | jwt_expired_or_wrong_claims | expected_behavior | customer_dev | [ ] |
| 7 | api_key_invalid | configuration | customer_dev | [ ] |
| 8 | rate_limited | expected_behavior | customer_dev | [ ] |
| 9 | webhook_signature_invalid | configuration | customer_dev | [ ] |
| 10 | scim_user_conflict | expected_behavior | customer_admin | [ ] |
| 11 | server_error_defect | product_defect | engineering | [ ] |
| 12 | account_billing_hold | specialist_owned | billing | [ ] |
| — | insufficient_evidence | — | support | [ ] |
