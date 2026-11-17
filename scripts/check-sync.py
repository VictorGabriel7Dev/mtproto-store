#!/usr/bin/env python3
# ======================================================================
#  MTPROTO-STORE  ::  Telegram as unlimited object storage over MTProto
#  Conformance guard: the CONTRACT must match the binary, and no upstream
#  branding may leak. Runs in CI and locally. Durable fix for doc drift.
#
#  Copyright (C) 2026  VictorGabriel7Dev
#  SPDX-License-Identifier: AGPL-3.0-or-later
#
#  Free software under the GNU AGPL v3 or later. NETWORK COPYLEFT: run a
#  modified version, even as a service, and you MUST offer its source.
#
#  Site      : https://victorgabriel.dev
#  Source    : https://github.com/VictorGabriel7Dev/mtproto-store
#  GitHub    : @VictorGabriel7Dev https://github.com/VictorGabriel7Dev
#  Telegram  : @VictorGabriel_Dev https://t.me/VictorGabriel_Dev
#  E-mail    : contato@victorgabriel.dev
# ======================================================================
"""
Fails (exit 1) if:
  - a CLI verb exists in main.go's switch but is not documented in CONTRACT.md
    (or vice versa), aliases included;
  - an ERR_* / 2FA_REQUIRED code is emitted in main.go but not in CONTRACT.md
    (or vice versa);
  - any upstream branding leaks into a tracked file.
This is the durable answer to the recurring "docs drifted from the binary" bug.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

code = open("main.go", encoding="utf-8").read()
contract = open("CONTRACT.md", encoding="utf-8").read()
fail = []

# --- CLI verbs: switch(main.go) vs ### headings + "alias `x`" (CONTRACT) ---
verbs_code = set()
for m in re.findall(r'\n\tcase ((?:"[a-z0-9-]+"(?:, )?)+):', code):
    verbs_code |= set(re.findall(r'"([a-z0-9-]+)"', m))
verbs_doc = set(re.findall(r'^### `([a-z0-9-]+)', contract, re.M))
verbs_doc |= set(re.findall(r'alias `([a-z0-9-]+)`', contract))
if verbs_code - verbs_doc:
    fail.append("verb(s) in code but missing from CONTRACT.md: %s" % sorted(verbs_code - verbs_doc))
if verbs_doc - verbs_code:
    fail.append("verb(s) in CONTRACT.md but missing from code: %s" % sorted(verbs_doc - verbs_code))

# --- error codes ---
errs_code = set(re.findall(r'printError\("([A-Z0-9_]+)"', code))
errs_code |= set(re.findall(r'"code":\s*"([A-Z0-9_]+)"', code))
if '"2FA_REQUIRED"' in code:
    errs_code.add("2FA_REQUIRED")
errs_doc = set(re.findall(r'`(ERR_[A-Z0-9_]+|2FA_REQUIRED)`', contract))
if errs_code - errs_doc:
    fail.append("error code(s) in code but missing from CONTRACT.md: %s" % sorted(errs_code - errs_doc))
if errs_doc - errs_code:
    fail.append("error code(s) in CONTRACT.md but missing from code: %s" % sorted(errs_doc - errs_code))

# --- no upstream branding in any tracked file ---
tracked = subprocess.check_output(["git", "ls-files"]).decode().split()
# Assembled from split string literals on purpose: this guard file must not itself
# contain the forbidden substrings, or a naive branding grep (including the
# repository's own pre-push hook) would flag the guard. The alternatives match the
# upstream project's name and its tag and module-path variants.
brand = re.compile("|".join([
    "vd" "171", "vd" "backup", "vd" "[-_]backup", "telegram-" "vd" "b",
]), re.I)
for f in tracked:
    if f in ("go.sum",) or f.startswith("scripts/check-sync"):
        continue
    try:
        text = open(f, encoding="utf-8", errors="ignore").read()
    except OSError:
        continue
    for i, ln in enumerate(text.splitlines(), 1):
        if brand.search(ln):
            fail.append("upstream branding leak in %s:%d -> %s" % (f, i, ln.strip()[:60]))

# --- every translated README carries the same command rows (i18n doc-sweep guard) ---
primary = sorted(verbs_code - {"status", "list-backups"})  # aliases live in prose, not their own row
for rf in [f for f in tracked if re.match(r'README(\.[a-z]{2})?\.md$', f)]:
    rtext = open(rf, encoding="utf-8").read()
    for v in primary:
        if "`" + v not in rtext:
            fail.append("%s is missing the `%s` command row" % (rf, v))

if fail:
    print("FAILED: CONTRACT <-> code / branding mismatch")
    for x in fail:
        print("  - " + x)
    sys.exit(1)
print("OK: contract matches the binary; no branding leak.")
