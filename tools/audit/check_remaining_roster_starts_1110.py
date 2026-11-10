"""Inventory exact compiled menu starts without admitting placeholder profiles.

The linked-symbol inputs are read only.  All stage, powerup and native Mesen
claims remain separate from this finite CPU frontend inventory.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

import audit_dkjr_installed_ingress_1108_v1 as I
from check_getsu_giant_rebase_1110 import W
from inventory_playable_menu_1101_v3 import menu_name

R = I.R
REQUESTED = {
    'Prince of Persia': ('PRINCE PERSIA', 'PRINCE OF PERSIA'),
    'Donkey Kong Jr.': ('DONKEY KONG JR', 'DK JR'),
    'Sonic (Master System reference)': ('SONIC',),
    'Jay McCray': ('JAY MCCRAY',),
    'Steve Hermann': ('STEVE HERMANN',),
    'Getsu Fuma': ('GETSU FUMA',),
    'Mega Giant Mario': ('GIANT MARIO',),
}


def digest(raw):
    return sha256(raw).hexdigest()


def inventory(raw):
    bundle = W.bundle(raw)
    fields = sorted(name for name, row in bundle['syms'].items()
                    if 'Variant' in name and '::' not in name
                    and not name.startswith('.') and int(row['val'], 0) < 0x8000)
    fields += ['FmAlts']
    rows = []
    for slot in range(32):
        model = I.UI.seed(bundle, slot)
        seen = set()
        for cycle in range(33):
            name, cells = menu_name(model)
            profile = dict(raw=I.N.get(model, 'SelectedCharacter'),
                           variants={name: I.N.get(model, name) for name in fields
                                     if I.N.get(model, name)})
            signature = (profile['raw'], tuple(cells), tuple(profile['variants'].items()))
            if signature in seen:
                break
            seen.add(signature)
            confirmations = []
            for button in (16, 128):
                fork = I.N.fork(model)
                I.UI.key(fork, button)
                confirmations.append(I.N.get(fork, 'CrossoverMenuState') == 0)
            assert confirmations[0] == confirmations[1], (slot, cycle, name, confirmations)
            rows.append(dict(slot=slot, cycle=cycle, name=name,
                             confirm_starts=confirmations[0], **profile))
            I.UI.key(model, 32)
        else:
            raise AssertionError(('Select cycle exceeds finite roster bound', slot))
    unique = {(row['slot'], row['raw'], row['name']): row for row in rows}
    statuses = {}
    for identity, aliases in REQUESTED.items():
        matches = [row for row in unique.values()
                   if any(alias in row['name'] for alias in aliases)]
        statuses[identity] = dict(status='absent' if not matches else
                                 'startable' if all(row['confirm_starts'] for row in matches)
                                 else 'locked', matches=matches)
    return dict(select_states=len(rows), distinct_named_entries=len(unique),
                confirmable_named_entries=sum(row['confirm_starts'] for row in unique.values()),
                locked=[row for row in unique.values() if not row['confirm_starts']],
                requested=statuses, rows=rows)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--rom', required=True, type=Path)
    cli.add_argument('--expected', required=True)
    cli.add_argument('--output', required=True, type=Path)
    args = cli.parse_args()
    raw = args.rom.read_bytes()
    assert digest(raw) == args.expected and len(raw) == 2_097_168
    assert not args.output.exists()
    result = inventory(raw)
    result.update(passed=True, ROM_sha256=args.expected, ROM_written=False,
                  Mesen_run=False, full_stage=False, all_powerups=False,
                  scope='Exact compiled32slot menu resolution, Select cycles and Start/A '
                        'confirmation using actual6502 instructions. No placeholder admission, '
                        'native replay, gameplay initialization or fullstage inference.',
                  source_SHA256=digest(Path(__file__).read_bytes()))
    args.output.mkdir()
    (args.output / 'inventory.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('rows', 'requested')}))
    print(json.dumps(result['requested']))


if __name__ == '__main__':
    main()
