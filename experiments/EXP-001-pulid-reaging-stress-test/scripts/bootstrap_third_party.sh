#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
THIRD_PARTY="$ROOT/third_party"
PATCH_DIR="$ROOT/experiments/EXP-001-pulid-reaging-stress-test/patches"
mkdir -p "$THIRD_PARTY"

clone_at() {
  local name="$1"
  local url="$2"
  local commit="$3"
  local dir="$THIRD_PARTY/$name"

  if [[ ! -d "$dir/.git" ]]; then
    git clone "$url" "$dir"
  fi

  git -C "$dir" fetch --all --tags --prune
  git -C "$dir" checkout --detach "$commit"
  local actual
  actual="$(git -C "$dir" rev-parse HEAD)"
  if [[ "$actual" != "$commit" ]]; then
    echo "ERROR: $name expected $commit, got $actual" >&2
    exit 2
  fi
  echo "$name -> $actual"
}

clone_at "PuLID" "https://github.com/ToTheBeginning/PuLID.git" \
  "a66a6a1901729897fa1dc11d10397943caf15470"
clone_at "AdaFace" "https://github.com/mk-minchul/AdaFace.git" \
  "c60eaa786a42c03444f3df7096dbaf9d57ae010d"
clone_at "MiVOLO" "https://github.com/WildChlamydia/MiVOLO.git" \
  "37475e3f8818b5f22448003feec3e64b01bfb188"

echo "Pinned third-party repositories are ready under $THIRD_PARTY"


PULID_PATCH="$PATCH_DIR/pulid_reproducibility.patch"
if git -C "$THIRD_PARTY/PuLID" apply --reverse --check "$PULID_PATCH" >/dev/null 2>&1; then
  echo "PuLID reproducibility patch already applied"
else
  git -C "$THIRD_PARTY/PuLID" apply --check "$PULID_PATCH"
  git -C "$THIRD_PARTY/PuLID" apply "$PULID_PATCH"
  echo "Applied PuLID reproducibility patch"
fi
