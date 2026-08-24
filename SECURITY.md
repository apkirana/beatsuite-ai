# Security

Beat Suite AI is a **research and demonstration prototype**. It models a healthcare monitoring
workflow, but it has not been through a security audit, a privacy review, or any clinical validation.
Do not connect it to real patient data, real medical devices, or a real care setting.

## Reporting a vulnerability

Please open a private security advisory through GitHub's
[Security tab](https://github.com/apkirana/beatsuite-ai/security/advisories/new), or email
puspa.kirana@utwente.nl. Please do not open a public issue for an unfixed vulnerability.

## Setting up an instance safely

1. **Generate a real `SECRET_KEY`.** The app refuses to start without one unless
   `FLASK_ENV=development`. A predictable key lets anyone forge a session cookie.

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Create accounts with `scripts/seed_users.py`.** No accounts ship with the code. The script
   generates random passwords and prints them once.

   ```bash
   python scripts/seed_users.py
   ```

3. **Keep `FLASK_DEBUG=false`.** Flask's debug mode exposes an interactive console that executes
   arbitrary Python against the running process.

4. **Set `ALLOWED_ORIGINS` to your actual front-end origin.** CORS runs with
   `supports_credentials=True`, so a wildcard would let any website drive the API as a logged-in user.

5. **Serve over HTTPS and leave `SESSION_COOKIE_SECURE=true`,** so session cookies are never sent in
   the clear.

6. **Restrict who can reach the deployment.** If it is a demo, put it behind authentication at the
   load balancer or keep it off the public internet.

## How credentials are handled

Passwords are stored as **PBKDF2-HMAC-SHA256** with a per-user 16-byte random salt and 600,000
iterations, in the format `pbkdf2_sha256$<iterations>$<salt>$<hash>`. Verification is constant-time via
`hmac.compare_digest`.

Earlier versions stored **unsalted SHA-256** digests, and a `users.json` containing them was committed
to this repository. That scheme is unsuitable for passwords: it is fast enough to brute-force at scale
and vulnerable to precomputed rainbow tables. Those hashes remain in the git history of this repository
and **any password that ever existed under the old scheme must be considered public.**

Legacy hashes still verify, so existing installations keep working, but they are re-hashed into the new
format automatically on the next successful login. Anyone running an older instance should rotate every
password regardless.

## Known limitations

These are understood gaps, listed so nobody mistakes the prototype for a hardened system:

- **Sessions are in-process memory.** They vanish on restart and are not shared across instances.
  A real deployment needs Redis or a database.
- **Login throttling is per-process and in-memory.** It slows down guessing against a single instance;
  it is not a substitute for a rate limiter at the edge.
- **User records live in a JSON file,** not a database with access control, transactions, or an audit log.
- **No CSRF protection** on state-changing endpoints beyond the `SameSite=Lax` cookie attribute.
- **No audit trail** of who read which patient record — a requirement in any real care setting.
- **Patient data is synthetic.** The repository's data files are fabricated examples, and the GDPR and
  medical-device obligations that would apply to real data have not been addressed.
