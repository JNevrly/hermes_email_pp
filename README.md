# Hermes Email++

[![PyPI](https://img.shields.io/pypi/v/hermes-email-pp.svg)](https://pypi.org/project/hermes-email-pp/)
[![Release](https://github.com/JNevrly/hermes_email_pp/actions/workflows/release.yml/badge.svg)](https://github.com/JNevrly/hermes_email_pp/actions/workflows/release.yml)

Hermes Email++ is a third-party IMAP/SMTP platform adapter for Hermes Agent.
It is registered as `email_pp`, independently of Hermes' built-in `email`
platform. It routes each RFC email thread to its own Hermes session, sends
plain-text and HTML email, and supports a review-draft workflow for common
inline forwards.

## Installation And Enablement

Install from the Hermes dashboard's **Settings > Plugins > Install from Git**
flow using `JNevrly/hermes_email_pp`, then enable `email-pp` when prompted.
Email++ requires Hermes Agent 0.20.5 or later in the 0.20 release line.

The dashboard installs the repository as a directory plugin. It stays disabled
until you explicitly enable it. Restart the gateway after installing or
changing configuration. `hermes plugins list` shows discovery and enablement,
and `hermes gateway status` shows the registered and connected platforms.

Select **Channels > Email++ > Configure** to enter all settings below. Vanilla
Hermes renders these as text/password inputs: enter `true` or `false` for the
two boolean settings, and `always`, `forwarded`, or `never` for quote mode.
Leave optional fields blank to use their documented runtime defaults. Restart
the gateway after saving. The card asks for **Allow all users** even though its
secure runtime default is `false`: enter `false` unless you deliberately want
to accept every non-automated sender.

```dotenv
EMAIL_PP_ADDRESS=agent@example.com
EMAIL_PP_PASSWORD=an-app-password
EMAIL_PP_IMAP_HOST=imap.example.com
EMAIL_PP_SMTP_HOST=smtp.example.com
EMAIL_PP_ALLOWED_USERS=operator@example.com
EMAIL_PP_REQUIRE_AUTHENTICATED_SENDER=true
```

All four required variables must be non-empty before environment-driven
configuration enables Email++. The `EMAIL_PP_*` namespace is deliberately
isolated: built-in `EMAIL_*` credentials are never read.

Enable the Email++ gateway platform in the active profile's `config.yaml` when
it is not auto-enabled from the complete required environment configuration:

```yaml
plugins:
  enabled: [email-pp]
platforms:
  email_pp:
    enabled: true
```

For a mailbox shared with the built-in adapter, use **only one** adapter. Keep
the `EMAIL_*` credentials absent and disable `email` in the gateway
configuration before enabling Email++ with its `EMAIL_PP_*` credentials. Two
adapters polling the same mailbox can race, duplicate processing, or send
conflicting replies.

### Settings

Environment variables take precedence over matching `extra` values in the
Email++ platform configuration.

| Setting | Required | Default | Meaning |
| --- | --- | --- | --- |
| `EMAIL_PP_ADDRESS` | Yes | - | Agent mailbox address and SMTP envelope identity. |
| `EMAIL_PP_PASSWORD` | Yes | - | IMAP/SMTP password or provider-issued app password. |
| `EMAIL_PP_IMAP_HOST` | Yes | - | IMAP server hostname. |
| `EMAIL_PP_SMTP_HOST` | Yes | - | SMTP server hostname. |
| `EMAIL_PP_IMAP_PORT` | No | `993` | IMAP-over-TLS port. |
| `EMAIL_PP_SMTP_PORT` | No | `587` | SMTP STARTTLS port; use `465` for implicit TLS. |
| `EMAIL_PP_SENDER_NAME` | No | `Hermes Agent` | Display name used for outgoing replies; the mailbox address remains `EMAIL_PP_ADDRESS`. |
| `EMAIL_PP_POLL_INTERVAL` | No | `15` | Inbox polling interval in seconds; values below one second are treated as one second. |
| `EMAIL_PP_MAILBOX` | No | `INBOX` | Mailbox selected for polling. |
| `EMAIL_PP_ALLOWED_USERS` | No | empty | Comma-separated sender-address allowlist. Required unless `EMAIL_PP_ALLOW_ALL_USERS` is enabled. |
| `EMAIL_PP_ALLOW_ALL_USERS` | No | `false` | Accept every non-automated sender. This also bypasses sender-authentication checks; do not use for an Internet-facing mailbox. |
| `EMAIL_PP_REQUIRE_AUTHENTICATED_SENDER` | No | `true` | Require a passing DMARC result in `Authentication-Results` for allowlisted senders. |
| `EMAIL_PP_AUTHSERV_ID` | No | empty | Optional authentication-service identifier that must prefix the trusted `Authentication-Results` header. |
| `EMAIL_PP_QUOTE_MODE` | No | `always` | `always` quotes the source email, `forwarded` quotes only parsed forwards, and `never` omits visible quotes. |
| `EMAIL_PP_PROCESS_HISTORY_WINDOW` | No | `0` | Unread mail recovery at a cold gateway start: `0` skips existing mail, `-1` processes all unread mail, and a positive exact-second window processes only unread mail newer than that cutoff. |
| `EMAIL_PP_DELETE_PROCESSED` | No | `false` | Delete authorized email only after Hermes completes successfully and its reply is accepted by SMTP. Requires IMAP UIDPLUS support. |

`EMAIL_PP_ALLOW_ALL_USERS` accepts every non-automated sender and disables the
allowlist and sender-authentication checks. Leave it disabled for an
Internet-facing mailbox. The safer default,
`EMAIL_PP_REQUIRE_AUTHENTICATED_SENDER=true`, remains enabled unless you
explicitly turn it off.

At a cold gateway start, Email++ normally ignores unread mail already present
in the selected mailbox. Set `EMAIL_PP_PROCESS_HISTORY_WINDOW` to `-1` to
recover all unread mail, or to a positive number of seconds to recover only
recent unread mail. Invalid values and values below `-1` prevent the adapter
from starting. Automatic reconnects in a running gateway retain their mailbox
state and process unread mail received during the outage.

Set `EMAIL_PP_DELETE_PROCESSED=true` only for a dedicated agent mailbox when
you want successful requests removed automatically. Email++ retains rejected,
malformed, cancelled, and failed requests. It records a successful response
before deleting and retries a failed mailbox deletion without rerunning Hermes.
Deletion requires IMAP `UIDPLUS`; Email++ never uses broad `EXPUNGE`, so it
cannot remove messages another mailbox client has marked for deletion.

## Email Behavior

### Ordinary Replies

Each RFC thread is mapped to a private Hermes thread. `Message-ID`,
`References`, and `In-Reply-To` preserve continuity across replies and gateway
restarts. Replies include both `text/plain` and safe `text/html` alternatives.
The selected quote mode controls whether the original content is visibly
quoted; normal replies retain RFC `In-Reply-To` and `References` headers.

The adapter rejects automated mail, self-mail, malformed message-ID headers,
senders outside the allowlist, and (by default) messages without a passing
DMARC result. It only sends when Hermes supplies a known sender and reply
route, preventing arbitrary outbound email addresses from being used as a
delivery target.

### Forwarded Review Drafts

Email++ recognizes English inline forwards in these forms:

```text
---------- Forwarded message ---------
```

```text
-----Original Message-----
```

```text
________________________________
```

Outlook/O365 HTML forwards using an `hr` followed by the standard
`divRplyFwdMsg` header block are also supported.

Use a short task prompt before the boundary, followed by a complete forwarded
message with at least `From`, `Subject`, and a non-empty body. The first Hermes
response is sent only to the forwarder as a threaded reply with subject
`Re: <forwarding subject>`. It uses standard `In-Reply-To` and `References`
headers; when a forwarding wrapper has valid Outlook conversation headers, it
also preserves `Thread-Topic` and extends `Thread-Index`. It never sends to the
original correspondent; its visible quote contains only the original message,
never the wrapper task prompt. A reply to that message stays in the same Hermes
session and is sent as a normal revision.

Only English Gmail and Outlook inline forwards matching the boundaries above
are supported. Attachments-as-forwards, localized client formatting, nested or
ambiguous forwards, and forwards without the required headers/body are not
parsed. A suspected forward that cannot be parsed receives a safe notice and
creates no draft or agent task. This fail-closed behavior prevents wrapper text
or untrusted forwarded content from being mistaken for an instruction.

## Security And Data Handling

- Use a dedicated mailbox and a least-privilege provider app password, not a
  primary account password. Restrict IMAP/SMTP access to TLS-enabled endpoints.
- Store secrets in the Hermes profile `.env` with owner-only filesystem
  permissions or use the deployment platform's secret store. Never commit the
  `.env` file or app password.
- Use a small, explicit `EMAIL_PP_ALLOWED_USERS` list. Leave
  `EMAIL_PP_ALLOW_ALL_USERS` unset, and keep authenticated-sender verification
  enabled. Set `EMAIL_PP_AUTHSERV_ID` when the receiving infrastructure has a
  known authentication-results service.
- Treat sender authentication as a mailbox-side defense, not proof that email
  content is trustworthy. Forwarded message bodies are reference data and are
  explicitly separated from the authorized task prompt.
- Inbound attachments are written to temporary files and exposed to Hermes as
  media URLs; the adapter does not scan, size-limit, or delete them itself.
  Apply mailbox-provider malware controls, restrict tool access for the Email++
  platform, and clean the host temporary directory according to local policy.
- Thread routing, delivery details, quote sources, and draft context are kept
  locally at `~/.hermes/email_pp/threads.json` (or the active `HERMES_HOME`).
  The directory is mode `0700` and the state file is mode `0600`, but it is not
  encrypted. It is bounded to 500 threads and a 90-day retention period; back
  up or purge it according to the mailbox's data-retention policy.

## Limitations

The adapter polls one IMAP mailbox and supports IMAP-over-TLS plus SMTP
STARTTLS or implicit SMTP TLS. It does not provide mailbox synchronization,
server-side draft storage, attachment malware scanning, arbitrary outbound
mail, non-English forward parsing, or direct delivery to an original
forwarded-message sender.

## Development Validation

Run the complete release checks with an editable Hermes Agent v0.20.5 source
checkout installed into the development environment:

```console
$ uv sync --group dev
$ uv pip install -e /path/to/hermes-agent-v0.20.5
$ .venv/bin/ruff check .
$ .venv/bin/ruff format --check .
$ .venv/bin/mypy hermes_email_pp
$ .venv/bin/pytest --cov=hermes_email_pp tests/
$ uv build --out-dir dist --clear
```

The release workflow installs the official v0.20.5 source checkout in editable
mode before running the adapter and Git-install contract tests. Its wheel smoke
test confirms the `email-pp` entry point can load without replacing Hermes'
built-in `email` registration.

## Releases

1. Update the version in `pyproject.toml`, `plugin.yaml`, and
   `hermes_email_pp/__init__.py`, then add the matching version section to
   `CHANGELOG.md`.
2. Regenerate the lockfile with `uv lock`. Before tagging, verify it with
   `uv lock --check` and `uv sync --group dev --locked`.
3. Commit and merge the release changes, then create and push a tag matching
   `vX.Y.Z`. The tag must equal `v` followed by `[project].version`, for example
   package version `0.2.0` requires tag `v0.2.0`.
4. The Release workflow runs the full validation suite, builds the wheel and
   source distribution, publishes those exact artifacts to PyPI, and creates a
   GitHub Release with generated notes and the same artifacts. A failure at any
   stage prevents later stages from running.

The workflow has a manual `workflow_dispatch` tag input for recovering a valid
existing tag; it applies the same tag and version validation. Leave `skip_pypi`
disabled unless the exact version is already on PyPI. That recovery option lets
the workflow create a missing GitHub Release without attempting a duplicate
PyPI upload.

Before the first release, create a protected GitHub Actions environment named
`pypi` and configure PyPI Trusted Publishing for project `hermes-email-pp` with
GitHub owner `JNevrly`, repository `hermes_email_pp`, workflow
`.github/workflows/release.yml` (workflow filename `release.yml`), and
environment `pypi`. PyPI supports creating this as a pending publisher before
the project exists. No PyPI API token or repository secret is needed.
