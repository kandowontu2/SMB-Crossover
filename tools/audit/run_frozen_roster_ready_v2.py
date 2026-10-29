"""Strict native launcher allowing only user recent-ROM history to differ."""
from pathlib import Path
import copy
import json
import sys
import run_frozen_roster_ready_v1 as original

ROOT = Path(__file__).resolve().parents[2]
PRIVATE = ROOT / 'build/verification/kamikaze-private-emulator-v1/settings.json'
PRIVATE_SHA = '94071b0f5eec14da9de92a6036cdbaf9d23d84776906b318b2451202bef485de'


def main():
    # Historical private settings were proved to differ only in the host Lua
    # timeout. Reconstruct their original semantic baseline without touching
    # either file. ALL other settings remain exact except the recent ROM list.
    assert original.sha(PRIVATE) == PRIVATE_SHA
    reference = json.loads(PRIVATE.read_bytes().decode('utf-8-sig'))
    assert reference['Debug']['ScriptWindow']['ScriptTimeout'] == 5
    reference['Debug']['ScriptWindow']['ScriptTimeout'] = 1
    current = json.loads(original.SETTINGS.read_bytes().decode('utf-8-sig'))
    for value in [reference, current]:
        value.pop('RecentFiles')
    assert current == reference, 'Settings other than recent-ROM history changed'
    before = original.sha(original.SETTINGS)
    original.SETTINGS_SHA = before
    # Preserve every existing dependency/process/no-restart/hardware check.
    # No original source or prior receipt is rewritten.
    result = original.main()
    ready = Path(sys.argv[1]).resolve()
    receipt = ready.parent / 'launch.json'
    data = json.loads(receipt.read_text())
    data['actual_launcher'] = dict(path=str(Path(__file__).resolve()), sha256=original.sha(__file__))
    data['settings_review'] = dict(
        unchanged_semantics_except='RecentFiles', reconstructed_from_private_sha256=PRIVATE_SHA,
        historical_global_sha256='66d3c35063c1692c595bab6e07a21854f37b4af970597251a4e320b91d37a9aa',
        actual_before_sha256=before, settings_modified=False)
    receipt.write_text(json.dumps(data, indent=2) + '\n')
    return result


if __name__ == '__main__':
    raise SystemExit(main())
