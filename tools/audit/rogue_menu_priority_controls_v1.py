"""Verify exact preview OAM priority and preserve all80selection contracts."""
from pathlib import Path
import importlib.util
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
import rogue_current_menu_controls_v1 as existing
from link_pit_rygar_sophia_audit_cpu import scoped_load

O = R/'build/rogue-current-menu-v6'


def main():
    existing.O = O
    existing.main()
    spec = importlib.util.spec_from_file_location('priority_menu_adapter', O/'menu-controls-adapter.py')
    menu = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(menu)
    menu.ROOT = R
    old = scoped_load(R/'build/rogue-current-menu-v5/candidate.nes')
    new = scoped_load(O/'candidate.nes')
    cases = []
    for slot, count in enumerate(menu.COUNTS):
        pair = [menu.fresh(b, slot) for b in (old, new)]
        for a in pair:
            a.invoke('MenuResolveCharacter')
            a.invoke('QueueSelection')
        for variant in range(count):
            if variant:
                for a in pair:
                    menu.button(a, 32)
            before, after = [bytes(a.m[0x200:0x300]) for a in pair]
            length = pair[0].get('CurrentOAMOffset')
            assert length == pair[1].get('CurrentOAMOffset')
            assert 0 < length < 256 and length % 4 == 0, (slot, variant, length)
            expected = bytearray(before)
            for i in range(2, length, 4):
                expected[i] &= 0xdf
            assert after == bytes(expected), (slot, variant)
            if (slot, variant) == (2, 1):
                assert length == 20 and all(before[i] & 0x20 for i in range(2, length, 4))
                assert all(not after[i] & 0x20 for i in range(2, length, 4))
            cases.append(dict(slot=slot, variant=variant, OAM_bytes=length,
                              cleared_priority_parts=sum(before[i] != after[i] for i in range(2, length, 4))))
    report = dict(passed=True, source_CPU_only=True, native_run=False,
                  ROM_sha256=existing.sha(O/'candidate.nes'), cases=cases,
                  exact_preview_only_attribute_mask=True,
                  source_bindings={str(p): existing.sha(p) for p in [Path(__file__).resolve(),
                      O/'controls.json', O/'menu-controls-adapter.py',
                      R/'build/rogue-current-menu-v5/candidate.nes', O/'candidate.nes']})
    assert not (O/'preview-priority-controls.json').exists()
    (O/'preview-priority-controls.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=True, preview_cases=len(cases), Rogue_parts_restored=5)))


if __name__ == '__main__':
    main()
