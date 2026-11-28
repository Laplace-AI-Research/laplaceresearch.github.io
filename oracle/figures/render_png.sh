#!/usr/bin/env bash
# Render each SVG figure to a 2x PNG with headless Chrome. Usage: ./render_png.sh
set -euo pipefail
cd "$(dirname "$0")"
FONTS="$(cd ../../assets/fonts && pwd)"
for svg in fig*.svg; do
  w=$(grep -o 'width="[0-9]*"' "$svg" | head -1 | grep -o '[0-9]*')
  h=$(grep -o 'height="[0-9]*"' "$svg" | head -1 | grep -o '[0-9]*')
  tmp="$(mktemp --suffix=.html)"
  printf '<!doctype html><style>@font-face{font-family:Inter;src:url("file://%s/inter-latin-opsz-normal.woff2")}@font-face{font-family:"Geist Mono";src:url("file://%s/geist-mono-latin-wght-normal.woff2")}html,body{margin:0}</style>%s' "$FONTS" "$FONTS" "$(cat "$svg")" > "$tmp"
  google-chrome --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
    --window-size="$w,$h" --screenshot="$PWD/${svg%.svg}.png" "file://$tmp" >/dev/null 2>&1
  rm -f "$tmp"
done
