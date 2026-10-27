"""Fresh-link four private fixes and verify their exact ROM-byte union; never install."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE = ARCHIVE / 'root-current-roster-composition-v1'
BASE_HASH = '3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
COMPONENTS = [
    ('renderer', 'mm-proto-construction-pivot-candidate-v9',
     '0a7dd88e6732bc189e432a9d55b18dd8f7ecf68a22e3b20f0a13ab7276241c09',
     {'smb1base-mmc5-expanded.cfg', 'src/level_variants.s',
      'src/megaman_weapons.s', 'src/metasprite_engine.s', 'src/sprite_render.s'}),
    ('mixer', 'common-audio-mixer-current3b-v3',
     'f4efd9ccb222501877dfc77c5189841aa9dc500756736f15aaf02a6994ae8c0f',
     {'src/guest_audio.s', 'src/mmc5_sfx.s'}),
    ('palette', 'robot-color-rotation-candidate-v3',
     'ca9a1c13e4f25a834ac665c4c9a6d67cf0be3c19ee7dc2af284a432e359be1fe',
     {'smb1base-mmc5-expanded.cfg', 'src/entrypoint.s', 'src/game.s',
      'src/x5_palette.s', 'src/robot_cold_palette_cache.s'}),
    ('Bill-Lance-HUD', 'bill-capsule-hud-current3b-v1',
     '9d296d337fc24e9b09b17043babec911c3134f60256636a7a285b39d56afd6e3',
     {'src/entrypoint.s', 'src/remaining_weapons.s', 'src/bill_hud_anchor.s'}),
]
SHARED = {'smb1base-mmc5-expanded.cfg', 'src/entrypoint.s'}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def put(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n')


def verified_source(packet):
    manifest = json.loads((packet / 'source-manifest.json').read_text())
    for name, expected in manifest.items():
        path = packet / 'source' / name
        assert path.resolve().is_relative_to((packet / 'source').resolve())
        assert sha(path) == expected, str(path)
    return manifest


def merge_insertions(original, variants, name):
    """These two shared files contain declarations only; reject replacements."""
    lines = original.splitlines(keepends=True)
    insertions = {}
    records = []
    for label, variant in variants:
        after = variant.splitlines(keepends=True)
        for kind, lo, hi, start, stop in difflib.SequenceMatcher(
                a=lines, b=after, autojunk=False).get_opcodes():
            if kind == 'equal':
                continue
            assert kind == 'insert' and lo == hi, (name, label, kind)
            addition = b''.join(after[start:stop])
            if name == 'src/entrypoint.s':
                expected_include = {
                    'palette': b'.include "robot_cold_palette_cache.s"',
                    'Bill-Lance-HUD': b'.include "bill_hud_anchor.s"',
                }[label]
                assert addition.count(expected_include) == 1
                assert b'.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5' in addition
            else:
                assert b'load=' in addition and b'type=ro' in addition
            insertions.setdefault(lo, []).append(addition)
            records.append(dict(component=label, base_line=lo,
                                inserted_bytes=len(addition),
                                inserted_sha256=hashlib.sha256(addition).hexdigest()))
    merged = []
    for index in range(len(lines) + 1):
        merged.extend(insertions.get(index, []))
        if index < len(lines):
            merged.append(lines[index])
    return b''.join(merged), records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(ARCHIVE.resolve())
    out.mkdir(parents=True, exist_ok=False)
    try:
        original = (BASE / 'candidate.nes').read_bytes()
        assert hashlib.sha256(original).hexdigest() == BASE_HASH
        base_manifest = verified_source(BASE)
        assert len(base_manifest) == 869
        source = out / 'source'
        source.mkdir()
        for name in base_manifest:
            dest = source / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(BASE / 'source' / name, dest)
        expected_rom = bytearray(original)
        offsets_seen = set()
        changed_files = set()
        shared_versions = {name: [] for name in SHARED}
        receipts = []
        for label, relative, expected_hash, expected_files in COMPONENTS:
            packet = ARCHIVE / relative
            manifest = verified_source(packet)
            changes = {n for n in manifest if manifest[n] != base_manifest.get(n)}
            assert changes == expected_files, (label, changes)
            assert not set(base_manifest) - set(manifest)
            rom = (packet / 'candidate.nes').read_bytes()
            assert hashlib.sha256(rom).hexdigest() == expected_hash
            assert len(rom) == len(original)
            offsets = {i for i, (a, b) in enumerate(zip(original, rom)) if a != b}
            assert not offsets & offsets_seen, ('overlapping ROM edits', label)
            offsets_seen.update(offsets)
            for index in offsets:
                expected_rom[index] = rom[index]
            for name in sorted(changes):
                if name in SHARED:
                    shared_versions[name].append((label, (packet/'source'/name).read_bytes()))
                else:
                    assert name not in changed_files, ('shared source needs explicit merge', name)
                    dest = source / name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(packet / 'source' / name, dest)
                changed_files.add(name)
            receipts.append(dict(component=label, packet=str(packet), ROM_sha256=expected_hash,
                                 source_manifest_sha256=sha(packet/'source-manifest.json'),
                                 changed_source=sorted(changes), changed_ROM_bytes=len(offsets)))
        merge_records = {}
        for name, versions in shared_versions.items():
            merged, merge_records[name] = merge_insertions((BASE/'source'/name).read_bytes(),
                                                          versions, name)
            (source/name).write_bytes(merged)
        put(out/'shared-declaration-merges.json', merge_records)
        manifest = {n: sha(source/n) for n in sorted(set(base_manifest) | changed_files)}
        assert len(manifest) == 871 and len(changed_files) == 13
        put(out/'source-manifest.json', manifest)
        patch = []
        for name in sorted(changed_files):
            before = (BASE/'source'/name).read_text().splitlines(True) if name in base_manifest else []
            patch.extend(difflib.unified_diff(before, (source/name).read_text().splitlines(True),
                                           fromfile='3b/'+name, tofile='private/'+name))
        (out/'source.patch').write_text(''.join(patch))
        command = [sys.executable, '-B', str(ROOT/'tools/build_mmc5_expanded.py'),
                   '--source-overlay', str(source), '--output', str(out/'candidate.nes')]
        result = subprocess.run(command, capture_output=True, text=True)
        put(out/'build-command.json', dict(command=command, returncode=result.returncode,
                                         stdout=result.stdout, stderr=result.stderr))
        assert result.returncode == 0
        assert (out/'candidate.nes').read_bytes() == expected_rom, 'Fresh linked ROM differs from byte union'
        proof = dict(built=True, source_composition_exact=True, native_run=False, adopted=False,
                     qualified=False, parent_ROM_sha256=BASE_HASH, ROM_sha256=sha(out/'candidate.nes'),
                     components=receipts, changed_source=sorted(changed_files),
                     complete_source_files=len(manifest), changed_ROM_bytes=len(offsets_seen),
                     changed_banks=sorted({(i-16)//8192 for i in offsets_seen}),
                     header_CHR_and_other_banks_exact=True, new_RAM_bytes=0,
                     source_manifest_sha256=sha(out/'source-manifest.json'),
                     source_patch_sha256=sha(out/'source.patch'), tool_sha256=sha(__file__),
                     limits='Private exact byte composition only. Component results keep their original '
                            'ROM scopes. No combined native, all-roster, all-abilities, waveform or '
                            'installation claim; production/default remain unchanged.')
        put(out/'proof.json', proof)
        print(json.dumps(proof))
    except Exception as exc:
        put(out/'failure.json', dict(passed=False, error=str(exc), traceback=traceback.format_exc()))
        raise


if __name__ == '__main__':
    main()
