#!/usr/bin/env bash
# Install or upgrade the Tool's files in a Workspace, for setup's Install and
# Upgrade, after the Operator has said yes. Run it from the Workspace, as the
# clone's own copy (<clone>/skills/setup/scripts/install.sh): the clone is the
# folder three levels above this file.
#
#   install.sh check
#       The Python check alone. Writes nothing.
#   install.sh install --runtime claude-code|cursor
#       Skills, VERSION, the AGENTS.md block, CLAUDE.md's @AGENTS.md line
#       (Claude Code), git init (unless the folder is the top of its own
#       repository), the Guard.
#   install.sh upgrade [--drop <skill>]...
#       Each Tool skill folder replaced, each --drop folder removed, VERSION,
#       the AGENTS.md block (text outside the markers kept), the Guard. The
#       runtime comes from workspace.md. The Operator's own skill folders,
#       veneer.md and records are never touched.
#
# Every check runs before the first write. Exit 0: done, with one line per
# step on stdout; when the Guard was not installed, its line says why (the
# Operator's own pre-commit hook, or core.hooksPath), which is not a failure.
# Exit 1: one line on stderr says what it could not do; when a check failed,
# nothing was written, and a later failure says so and is finished by
# running the same command again. Running it again leaves the same
# Workspace. The log entry, the other files and the commit stay with setup.
# Exit 2: usage.
#
# Bash 3.2 or later (macOS's own), git, and Python 3.9 or later as python3.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
CLONE="$(cd "$HERE/../../.." && pwd -P)"
BLOCK="$CLONE/skills/setup/templates/agents-block.md"
BEGIN='<!-- jenny:begin -->'
END='<!-- jenny:end -->'
PYTHON_LINE='Jenny needs Python 3.9 or later as `python3`: install it from https://www.python.org/downloads/, then ask again.'

fail() { echo "$*" >&2; exit 1; }
usage() {
  echo "usage: install.sh check | install --runtime claude-code|cursor | upgrade [--drop <skill>]..." >&2
  exit 2
}

# ---------------------------------------------------------------- checks

check_python() {
  command -v python3 >/dev/null 2>&1 &&
    python3 -c 'import sys; sys.exit(sys.version_info < (3, 9))' >/dev/null 2>&1 ||
    fail "$PYTHON_LINE"
}

check_clone() {
  [ -f "$CLONE/VERSION" ] && [ -f "$BLOCK" ] && [ -d "$CLONE/skills/jenny" ] ||
    fail "install.sh runs from the Tool clone (<clone>/skills/setup/scripts/install.sh), not from a Workspace's copy: nothing was written."
  [ "$(pwd -P)" != "$CLONE" ] ||
    fail "install.sh runs from the Workspace folder, not from the Tool clone: nothing was written."
}

check_git() {
  command -v git >/dev/null 2>&1 ||
    fail "Jenny needs git: install it from https://git-scm.com/downloads, then ask again."
}

skills_folder() {  # runtime → its skills folder
  case "$1" in
    claude-code) echo ".claude/skills" ;;
    cursor) echo ".cursor/skills" ;;
    *) fail "Unknown runtime \"$1\": Jenny runs on claude-code or cursor. Nothing was written." ;;
  esac
}

installed_version() {  # the Tool version in a skills folder, or nothing
  if [ -f "$1/jenny/VERSION" ]; then tr -d '[:space:]' < "$1/jenny/VERSION"
  elif [ -f "$1/setup/VERSION" ]; then tr -d '[:space:]' < "$1/setup/VERSION"  # Tool 0.2.0 and earlier
  fi
}

check_version() {  # $1: a version, $2: where it came from
  printf '%s\n' "$1" | grep -qE '^[0-9]+(\.[0-9]+)*$' ||
    fail "$2 holds \"$1\", which is not a Tool version (numbers and dots). Nothing was written."
}

newer() {  # exit 0 when version $1 is newer than $2, number by number
  local IFS=.
  local -a a b
  read -r -a a <<< "$1"
  read -r -a b <<< "$2"
  local i x y
  for i in 0 1 2 3; do
    x="${a[$i]:-0}" y="${b[$i]:-0}"
    [ "$((10#$x))" -gt "$((10#$y))" ] && return 0
    [ "$((10#$x))" -lt "$((10#$y))" ] && return 1
  done
  return 1
}

count_line() {  # how many lines of file $2 are exactly $1
  grep -cxF -- "$1" "$2" || true
}

check_markers() {  # AGENTS.md, if any, has no block or one whole block
  [ -f AGENTS.md ] || return 0
  ! grep -q "$(printf '\r')" AGENTS.md ||
    fail "AGENTS.md has Windows (CRLF) line endings, so its Tool block can't be found: convert it to LF line endings, then run install.sh again. Nothing was written."
  local b e
  b="$(count_line "$BEGIN" AGENTS.md)" e="$(count_line "$END" AGENTS.md)"
  [ "$b$e" = "00" ] && [ "${1:-}" != need ] && return 0
  if [ "$b$e" = "11" ] &&
     [ "$(grep -nxF -- "$BEGIN" AGENTS.md | cut -d: -f1)" -lt "$(grep -nxF -- "$END" AGENTS.md | cut -d: -f1)" ]; then
    return 0
  fi
  fail "AGENTS.md does not hold one whole Tool block (one \`$BEGIN\` line, then one \`$END\` line): ask the Operator where it is. Nothing was written."
}

# ---------------------------------------------------------------- writes

copy_skills() {  # $1: skills folder
  local sk="$1" src name
  mkdir -p "$sk"
  for src in "$CLONE"/skills/*/; do
    name="$(basename "$src")"
    rm -rf "${sk:?}/$name"
    cp -R "$src" "$sk/$name"
    find "$sk/$name" -name __pycache__ -type d -prune -exec rm -rf {} +
  done
  cp "$CLONE/VERSION" "$sk/jenny/VERSION"
  echo "Skills: $(ls -d "$CLONE"/skills/*/ | wc -l | tr -d ' ') Tool skill folders copied into $sk, $sk/jenny/VERSION set to $(tr -d '[:space:]' < "$CLONE/VERSION")"
}

build_block() {  # AGENTS.md.new, checked whole; AGENTS.md left as it is
  if [ ! -f AGENTS.md ]; then
    cp "$BLOCK" AGENTS.md.new
    BLOCK_HOW="written"
  elif [ "$(count_line "$BEGIN" AGENTS.md)" = 0 ]; then
    { cat "$BLOCK"; echo; cat AGENTS.md; } > AGENTS.md.new
    BLOCK_HOW="written at the top, the rest kept"
  else
    awk -v f="$BLOCK" -v b="$BEGIN" -v e="$END" '
      $0 == b { while ((getline l < f) > 0) print l; s = 1; next }
      $0 == e { s = 0; next }
      !s' AGENTS.md > AGENTS.md.new
    BLOCK_HOW="replaced between the markers, the rest kept"
  fi
  if [ "$(count_line "$BEGIN" AGENTS.md.new)$(count_line "$END" AGENTS.md.new)" != 11 ] ||
     ! sed -n "/^$BEGIN\$/,/^$END\$/p" AGENTS.md.new | cmp -s - "$BLOCK"; then
    rm -f AGENTS.md.new
    fail "AGENTS.md: the new Tool block did not come out whole, so AGENTS.md was left as it was. Nothing was written."
  fi
}

place_block() {
  mv AGENTS.md.new AGENTS.md
  echo "AGENTS.md: Tool block $BLOCK_HOW"
}

write_claude_md() {
  if [ ! -f CLAUDE.md ]; then
    echo "@AGENTS.md" > CLAUDE.md
    echo "CLAUDE.md: written, holding @AGENTS.md"
  elif [ "$(count_line "@AGENTS.md" CLAUDE.md)" = 0 ]; then
    { echo "@AGENTS.md"; cat CLAUDE.md; } > CLAUDE.md.new && mv CLAUDE.md.new CLAUDE.md
    echo "CLAUDE.md: @AGENTS.md added at the top, the rest kept"
  else
    echo "CLAUDE.md: already holds @AGENTS.md"
  fi
}

git_init() {
  local top
  top="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  if [ -n "$top" ] && [ "$(cd "$top" && pwd -P)" = "$(pwd -P)" ]; then
    echo "git: this folder's own repository kept"
  else
    git init -q 2>/dev/null ||
      fail "git init failed in this folder: fix it, then run install.sh again to finish."
    echo "git: repository started"
  fi
}

install_guard() {  # $1: skills folder
  # guard.py --install exits 1 with one line when it leaves the folder's own
  # hook alone; anything else (a crash, a traceback) is a failure.
  local out rc=0
  out="$(python3 -B "$1/jenny/scripts/guard.py" --install 2>&1)" || rc=$?
  if [ "$rc" = 0 ]; then
    echo "Guard: installed"
  elif [ "$rc" = 1 ] && [ -n "$out" ] && [ "$(printf '%s\n' "$out" | wc -l | tr -d ' ')" = 1 ]; then
    echo "Guard: not installed: $out"
  else
    fail "Guard: $1/jenny/scripts/guard.py --install failed ($(printf '%s' "$out" | tail -n 1)): fix it, then run install.sh again to finish."
  fi
}

# ---------------------------------------------------------------- commands

cmd_install() {
  local runtime=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --runtime) [ $# -ge 2 ] || usage; runtime="$2"; shift ;;
      *) usage ;;
    esac
    shift
  done
  [ -n "$runtime" ] || usage
  check_clone
  check_python
  check_git
  local sk have new
  sk="$(skills_folder "$runtime")"
  have="$(installed_version "$sk")" new="$(tr -d '[:space:]' < "$CLONE/VERSION")"
  check_version "$new" "$CLONE/VERSION"
  if [ -n "$have" ] && [ "$have" != "$new" ]; then
    fail "Jenny $have is already installed in $sk: a newer Tool version goes in through setup's Upgrade. Nothing was written."
  fi
  check_markers
  build_block

  copy_skills "$sk"
  place_block
  [ "$runtime" = claude-code ] && write_claude_md
  git_init
  install_guard "$sk"
}

cmd_upgrade() {
  local drops=() d
  while [ $# -gt 0 ]; do
    case "$1" in
      --drop) [ $# -ge 2 ] || usage; drops+=("$2"); shift ;;
      *) usage ;;
    esac
    shift
  done
  check_clone
  check_python
  check_git
  [ -f workspace.md ] ||
    fail "No workspace.md here: run install.sh upgrade from an installed Workspace. Nothing was written."
  local runtime sk have new
  runtime="$(sed -n 's/^Runtime: *//p' workspace.md | head -n 1 | tr -d '[:space:]')"
  [ -n "$runtime" ] || fail "workspace.md has no Runtime: line, so the skills folder is unknown. Nothing was written."
  sk="$(skills_folder "$runtime")"
  have="$(installed_version "$sk")" new="$(tr -d '[:space:]' < "$CLONE/VERSION")"
  [ -n "$have" ] ||
    fail "No Jenny skills in $sk: Jenny goes into this folder through setup's Install. Nothing was written."
  check_version "$new" "$CLONE/VERSION"
  check_version "$have" "The Workspace's installed VERSION"
  if newer "$have" "$new"; then
    fail "The Workspace is on Tool $have, newer than the clone's $new: there is no downgrade; revert the upgrade commit instead. Nothing was written."
  fi
  for d in ${drops[@]+"${drops[@]}"}; do
    case "$d" in
      ""|.|..|*/*) fail "--drop \"$d\" is not a skill folder name. Nothing was written." ;;
    esac
    [ ! -e "$CLONE/skills/$d" ] ||
      fail "--drop $d: $d is a skill in this Tool version, so it is not dropped. Nothing was written."
  done
  [ -f AGENTS.md ] ||
    fail "No AGENTS.md here, so there is no Tool block to replace: ask the Operator where it is. Nothing was written."
  check_markers need
  build_block

  copy_skills "$sk"
  for d in ${drops[@]+"${drops[@]}"}; do
    if [ -e "$sk/$d" ]; then
      rm -rf "${sk:?}/$d"
      echo "Skills: $sk/$d removed"
    fi
  done
  place_block
  install_guard "$sk"
}

[ $# -ge 1 ] || usage
cmd="$1"
shift
case "$cmd" in
  check) [ $# -eq 0 ] || usage; check_python ;;
  install) cmd_install "$@" ;;
  upgrade) cmd_upgrade "$@" ;;
  *) usage ;;
esac
