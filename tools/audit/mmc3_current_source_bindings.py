"""Bind the current private MMC3 port's retained addresses and audio hook."""
from pathlib import Path
import argparse
import hashlib
import json
from check_tmnt_audio_fallback_oc import qualified
from check_tmnt_render_oa import load, address, location

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=False)
    path = args.prepared / 'candidate.nes'
    old, new = load(args.baseline), load(path)
    assert sha(args.baseline) == '417e254d331cbf0b8df0c7ec1081273f7d9f867830a9596d2fd272a5050acf2f'
    assert len(old['raw']) == len(new['raw']) == 2097168
    assert new['raw'][:16] == old['raw'][:16]
    before, after = qualified(args.baseline), qualified(path)
    removed = {name: value for name, value in before.items() if after.get(name) != value}
    # The replacement restore leaf intentionally removes its private loop
    # back-edge; DCE9 is a JSR operand now, not an old callable entry.
    assert removed == {('LOCAL-MACRO_SYMBOL-14BC', 'Load'): 0xdce9}, removed
    assert ('LOCAL-MACRO_SYMBOL-14BC', 'Load') not in after
    changed = [i for i, (a, b) in enumerate(zip(old['raw'], new['raw'])) if a != b]
    banks = sorted({(i-16)//8192 for i in changed})
    assert banks == [10, 27, 28, 82, 84, 255], banks
    for name, value in dict(NextBank_SMC=0x13e, SafecallA_SMC=0x155,
                            FarcallJmpTarget_SMC=0x157, SafereturnA_SMC=0x159).items():
        assert address(new, name) == address(old, name) == value
    common = location(new, 'FarCallCommon')
    assert (common-16)//8192 == 254
    assert old['raw'][common:common+49] == new['raw'][common:common+49]
    assert new['raw'][16+254*8192:16+255*8192] == old['raw'][16+254*8192:16+255*8192]
    helper = location(new, 'Cv3NoiseVolumeStore')
    assert (helper-16)//8192 == 28
    target = address(new, 'Cv3NoiseVolumeStore')
    call = bytes([0x20, target & 255, target >> 8])
    driver = new['raw'][16+27*8192:16+28*8192]
    calls = [i for i in range(len(driver)-2) if driver[i:i+3] == call]
    assert len(calls) == 1
    generated = (args.prepared / 'source/build/generated/guest-audio/castlevania.inc').read_text()
    assert generated.count('.if ::ENABLE_FULL_ROSTER\n  JSR ::Cv3NoiseVolumeStore\n.else\n') == 1
    assert 'ENABLE_MMC5_EXPANDED' not in generated
    raw_chr = args.prepared / 'source/chr/characters/oversized-raw.chr'
    old_chr = args.baseline.parent / 'source/chr/characters/oversized-raw.chr'
    assert raw_chr.read_bytes() == old_chr.read_bytes()
    proof = dict(passed=True, adopted=False, goal_complete=False, ROM_sha256=sha(path),
                 baseline_ROM_sha256=sha(args.baseline), changed_bytes=len(changed), changed_banks=banks,
                 retained_qualified_symbols_exact=len(before)-1,
                 removed_private_restore_backedge=dict(scope='LOCAL-MACRO_SYMBOL-14BC', name='Load', old_address=0xdce9),
                 immutable_common_and_complete_LOWCODE_bank_exact=True, six_tiny_SMC_bytes_all_old_addresses_exact=True,
                 generated_driver_hook=dict(physical_bank=27, bank_offset=calls[0], target=target, target_bank=28),
                 raw_CHR_sha256=sha(raw_chr), raw_CHR_exact=True,
                 scope='Read-only complete current220-to-ae97 port composition and active generated audio-hook binding. CPU helper checks are separate. No native mapper/IRQ/PPU/music/cadence, release or full-roster qualification.')
    (args.output / 'proof.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
