"""Save the source-linked resource base required by the joint roster merge."""
from pathlib import Path
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R/'tools/audit'))
from checkpoint_roster_progress_1030_v2 import save, sha


def main():
    out = R/'build/character-host-union-resources-v1'
    path = out/'controls.json'
    controls = json.loads(path.read_text())
    assert controls['passed']
    assert controls['ROM_sha256'] == sha(out/'ice/candidate.nes') == '3925aa18859df68958ff782e5acc6558f877f1c0e81f22bd1e1ae54db9746ddb'
    assert controls['PN_stage']['decoded_actual_OAM_pairs'] == 1940
    assert controls['Ice_stage']['cases'] == 2160
    bindings = dict(controls['source_bindings'])
    for current in [path, Path(__file__).resolve(), R/'tools/audit/prepare_union13_resources_v1.py',
                    R/'tools/audit/union13_resources_controls_v1.py']:
        bindings[str(current)] = sha(current)
    save('union-v13-dense-resources', dict(
        status='SOURCE_REPRODUCTION_AND_RENDERER_CPU_PARITY_PASS_NATIVE_PENDING',
        ROM_sha256=controls['ROM_sha256'], PN_stage_ROM_sha256=controls['PN_stage']['ROM_sha256'],
        original_V13_ROM_sha256='3f24a0e1bc73d8655811b333aa52285ace1af5e469fcc7b6158b06afce54f72c',
        actual_source_changes='Qualified four PN producer files and two Ice producer files, explicit split CHR layout. No binary patching: source reassembled and linked; exact original V13 reproduction checked first.',
        PN=dict(source_pages=192, dense_pages=36, table_byte_changes=54, free_CHR=[868, 1024],
                actual_publishers=54, actual_OAM_pairs=1940),
        Ice=dict(source_descriptors=60, canonical_descriptors=19, cases=2160,
                 actual_parts=9072, physical_PRG_bank=70, free_offsets=[1423, 2144], free_bytes=721),
        invariants='Every runtime instruction, RAM address and other symbol value exact. Only IcPose alias values/IcArtEnd, descriptor bytes,54PN table bytes and dense CHR differ.',
        limits=['New native comparison pending; no joint Rogue/Quick/Arthur implementation or new admission flags.',
                'Existing V13 Bill extra missed frame remains; data compaction does not fix it.',
                'Conditional root Quick/Arthur allocations remain unchanged.']), bindings)


if __name__ == '__main__':
    main()
