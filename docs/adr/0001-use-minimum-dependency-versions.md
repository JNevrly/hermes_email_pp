# 0001: Use minimum dependency versions

Date: 2026-10-24

Status: Proposed for human review

## Context

Email++ shares its Python environment with Hermes. Speculative Python and
package upper bounds have blocked Hermes upgrades, including Python 3.14 and
Hermes' Ruff 0.15.10 requirement, without demonstrating an incompatibility in
the plugin itself. Ruff is development tooling rather than a plugin runtime
dependency, but development environments can still resolve both projects.

## Decision

- Require Python 3.13 or newer, without an upper bound.
- Declare minimum versions for runtime, development, and build dependencies.
  Remove the existing speculative ceilings, including Markdown and Ruff.
- Add an upper bound or exclusion only for a demonstrated incompatibility,
  documenting its reason and the condition for removing it.
- Keep exact resolved development versions in `uv.lock`; use locked syncs for
  repeatable CI and deliberate lockfile updates for dependency upgrades.
- Keep validation-host versions explicit. The release workflow's Python 3.13
  selection supports its existing Hermes 0.20.5 test host; it does not impose
  an upper limit on the plugin's installable Python versions.

## Alternatives

Keeping major-version ceilings would reject future releases before testing
whether they break the APIs Email++ uses. Pinning every declared requirement
would create tighter coupling to Hermes' dependency versions. Lower bounds
plus a lockfile preserve installation flexibility and reproducible validation.

## Consequences

Newer compatible versions can be installed alongside Hermes without changing
Email++ metadata. Python 3.11 and 3.12 are no longer supported. An uncapped
requirement permits future versions; it does not assert that every future
version has been tested. Existing tests and quality checks remain the evidence
for each validated environment.
