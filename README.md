# unslop-action

The official GitHub Action for [Unslop](https://unslop.cognitive-industries.org):
non-LLM code intelligence that scans your code for bugs, vulnerabilities, and
leaked secrets. Offline, deterministic, SARIF out.

The Action installs the `unslop` CLI, runs the engines you pick over your repo,
uploads results to GitHub code scanning, and (on Team plans) reports findings
inline on the pull request with an optional merge gate.

## Quick start

```yaml
name: unslop
on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read
  security-events: write   # for the code scanning SARIF upload

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: CogForgeLabs/unslop-action@v1
        with:
          engines: scan,secrets
          fail-on: none
```

That runs the free, local scan on every push and pull request and uploads the
SARIF to the Security tab. No account or license is required for public repos.

## Team features (inline PR comments + merge gate + dashboard)

Install the [Unslop GitHub App](https://github.com/apps/unslop-code-intelligence)
on your repo, link it at `https://unslop.cognitive-industries.org/app`, and save
the upload token it gives you as an Actions secret named `UNSLOP_UPLOAD_TOKEN`.
Then:

```yaml
      - uses: CogForgeLabs/unslop-action@v1
        with:
          engines: scan,secrets
          fail-on: high
          app-upload: 'true'
          upload-token: ${{ secrets.UNSLOP_UPLOAD_TOKEN }}
          license: ${{ secrets.UNSLOP_LICENSE }}
```

With a Team license the App posts inline review comments, publishes a pass/fail
check run at your `fail-on` threshold, and syncs findings to your org dashboard.
Without the token and license the same workflow still runs the free scan, so it
is safe to commit before you finish setting up the App.

## Inputs

| Input | Default | Description |
|---|---|---|
| `path` | `.` | Path to scan. |
| `engines` | `scan,secrets` | Comma-separated: `scan`, `secrets`, `quality`. |
| `format` | `sarif` | `text`, `json`, or `sarif`. |
| `output` | `unslop.sarif` | Where to write the report. |
| `fail-on` | `none` | Fail the job at this severity or above (`critical`/`high`/`medium`/`low`/`none`). Team license required to gate CI. |
| `license` | `` | Contents of an Unslop license file. Use `${{ secrets.UNSLOP_LICENSE }}`. |
| `version` | `latest` | `unslop` version to install (e.g. `v0.1.1`) or `latest`. |
| `app-upload` | `false` | Upload results to the Unslop GitHub App for inline comments, the gate, and dashboard sync. |
| `app-endpoint` | `https://api.cognitive-industries.org` | App API base. |
| `upload-token` | `` | Per-installation token from `…/app`. Use `${{ secrets.UNSLOP_UPLOAD_TOKEN }}`. |

## Outputs

| Output | Description |
|---|---|
| `report` | Path to the generated report. |
| `findings` | Total number of findings. |

## Pricing

Free forever for local scans on public repos. Pro, Team, and Enterprise add the
IDE extension, private-repo CI, org dashboards, and air-gapped deployment. See
[the pricing page](https://unslop.cognitive-industries.org).
