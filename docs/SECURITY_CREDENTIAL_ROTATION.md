# Credential Rotation Checklist (VPS)

Use this after removing plaintext credentials from code/scripts.

1. Rotate VPS root password immediately via hosting control panel.
2. Replace password-based SSH with key-based auth where possible.
3. Update local environment variables (do not commit):
   - `CRYPTOMENTOR_VPS_HOST`
   - `CRYPTOMENTOR_VPS_USER`
   - `CRYPTOMENTOR_VPS_PASSWORD`
4. Remove/replace any old plaintext credential files from local machine history.
5. Verify deployment scripts run only with environment-provided secrets.
