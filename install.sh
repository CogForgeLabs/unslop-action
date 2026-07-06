#!/bin/sh
# Unslop installer — fetches the latest static `unslop` binary for your platform
# and verifies its SHA-256 checksum before installing.
# Usage:  curl -fsSL https://unslop.cognitive-industries.org/install.sh | sh
set -eu

REPO="CogForgeLabs/unslop-dist"
BIN="unslop"
PREFIX="${UNSLOP_PREFIX:-/usr/local/bin}"

os="$(uname -s | tr '[:upper:]' '[:lower:]')"
arch="$(uname -m)"
case "$arch" in
  x86_64|amd64) arch="x86_64" ;;
  arm64|aarch64) arch="aarch64" ;;
  *) echo "unslop: unsupported arch: $arch" >&2; exit 1 ;;
esac
case "$os" in
  linux)  target="${arch}-unknown-linux-musl" ;;
  darwin) target="${arch}-apple-darwin" ;;
  mingw*|msys*|cygwin*|windows*)
    echo "unslop: on Windows, install with PowerShell instead:" >&2
    echo "  irm https://unslop.cognitive-industries.org/install.ps1 | iex" >&2
    exit 1 ;;
  *) echo "unslop: unsupported OS: $os" >&2; exit 1 ;;
esac

# Pin a version with UNSLOP_VERSION (e.g. v0.1.0); default is the latest release.
ver="${UNSLOP_VERSION:-latest}"
if [ "$ver" = "latest" ]; then
  base="https://github.com/${REPO}/releases/latest/download"
else
  base="https://github.com/${REPO}/releases/download/${ver}"
fi
tarball="${BIN}-${target}.tar.gz"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

echo "→ downloading ${tarball} …"
curl -fsSL "${base}/${tarball}" -o "${tmp}/${tarball}"
curl -fsSL "${base}/SHA256SUMS" -o "${tmp}/SHA256SUMS"

echo "→ verifying checksum …"
# Match the exact "<hash>  <tarball>" record. `awk` with a fixed field compare
# (not a regex) avoids treating dots in the name as wildcards and won't match a
# shorter name inside a longer one; sha256sum -c then re-verifies the full line.
line="$(awk -v f="$tarball" '$2 == f { print; exit }' "${tmp}/SHA256SUMS")"
if [ -z "$line" ]; then
  echo "unslop: ${tarball} not listed in SHA256SUMS — refusing to install." >&2
  exit 1
fi
( cd "$tmp"
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s\n' "$line" | sha256sum -c -
  elif command -v shasum >/dev/null 2>&1; then
    printf '%s\n' "$line" | shasum -a 256 -c -
  else
    echo "unslop: no sha256 tool (sha256sum/shasum) found; cannot verify download." >&2
    exit 1
  fi )

tar -xzf "${tmp}/${tarball}" -C "$tmp"

# Create the target dir if it does not exist yet (e.g. a fresh $HOME/.local/bin).
mkdir -p "$PREFIX" 2>/dev/null || sudo mkdir -p "$PREFIX"
if [ -w "$PREFIX" ]; then mv "$tmp/$BIN" "$PREFIX/$BIN"; else sudo mv "$tmp/$BIN" "$PREFIX/$BIN"; fi
chmod +x "$PREFIX/$BIN"
echo "✔ installed ${BIN} → ${PREFIX}/${BIN}"
echo "  run: ${BIN} scan ."
