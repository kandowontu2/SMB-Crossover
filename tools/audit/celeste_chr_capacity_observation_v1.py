"""Read-only capacity observation; does not release CHR or build a ROM."""
from pathlib import Path
import hashlib
import json
import re

R = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    output = R / 'docs/qa/celeste-chr-capacity-observation-2026-10-28.json'
    assert not output.exists(), 'Preserve the original observation'
    rom = R / 'build/roster-shared-celeste-small-chr-v1.nes'
    assert sha(rom) == 'f56a0e154c86c2bcc3577bd99e48dfab71ee61282defa6d16963a2c73e4487c9'
    asset = R / 'chr/characters/celeste-mario.chr'
    metadata = R / 'chr/characters/celeste-mario-assets.json'
    art = R / 'src/celeste_mario_art.inc'
    decoded = json.loads(metadata.read_text())
    original = asset.read_bytes()
    assert len(original) == 16384 and sha(asset) == decoded['output_chr_sha256']
    start = 16 + 128 * 8192 + 740 * 1024
    assert rom.read_bytes()[start:start + len(original)] == original
    table_text = art.read_text().split('CmArtBanks:', 1)[1].split('.popseg', 1)[0]
    table = [int(x) for x in re.findall(r'\d+', table_text.split('.byte', 1)[1])]
    assert len(table) == 26 and set(table) == {0, 1, 2}
    records = decoded['records']
    assert len(records) == 52
    for record in records:
        assert record['bank'] == table[record['pose']]
        assert record['face'] in (1, 2)
        assert all(part[0] % 2 == 0 and part[0] + 1 < 64 for part in record['parts'])
    files = [Path(__file__), rom, asset, metadata, art,
             R / 'src/celeste_mario_render_small_host.inc', R / 'src/celeste_mario_host_entry.s',
             R / 'src/celeste_mario_host_state.inc', R / 'smb1base-mmc5-expanded.cfg',
             R / 'build/celeste_small_chr_handoff_v1.json',
             R / 'build/verification/celeste-small-native-chr-easy-v1/review.json']
    observation = {
        'status': 'STATIC CAPACITY OBSERVATION; NO RELEASE, ALLOCATION, CODE OR ASSET CHANGE',
        'ROM_sha256': sha(rom), 'source_records': len(records), 'pose_banks': table,
        'all_source_records_need_only_sprite_window0': True,
        'body_pages_including_initial_bank0': [740, 741, 742],
        'current_full_incbin_bytes': len(original), 'record_addressable_prefix_bytes': 3072,
        'potential_suffix_pages': [743, 755], 'potential_suffix_bytes': 13312,
        'suffix_nonzero_bytes': sum(x != 0 for x in original[3072:]),
        'reason': 'All26 source poses, including unused large poses, select only pages0/1/2; '
                  'every actual 8x16 pair fits that selected1KB window. The corrected draw '
                  'publishes only window0. The old16KB copy also retained unrelated source patterns.',
        'remaining_before_reuse': [
            'Audit all physical CHR publishers/consumers and valid identity/scene lifecycles',
            'Keep original source asset and first3KB exact; formally trim the build incbin/allocator',
            'Prove other profiles and palettes/windows unchanged on actual compiled callers',
            'Fresh exact-hash native replay with complete captured-pixel equality, not sampled inference',
            'Only then reserve any part of the suffix for another character'
        ],
        'native_claim': 'Existing f56a native receipt is historical evidence for that exact untrimmed '
                        'build. No trim candidate or new native test exists.',
        'bindings': {str(path.resolve()): sha(path) for path in files}
    }
    output.write_text(json.dumps(observation, indent=2) + '\n')
    print(json.dumps({'output': str(output), 'sha256': sha(output), 'potential_bytes': 13312,
                      'released_bytes': 0}))


if __name__ == '__main__':
    main()
