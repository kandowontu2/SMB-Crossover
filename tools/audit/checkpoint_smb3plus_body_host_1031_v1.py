"""Freeze the private body/palette join without admitting playable characters."""
from pathlib import Path
import json
import shutil
import sys
import zipfile

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/audit'))
import prepare_functional_roster_visuals58_v1 as B

P = R / 'build/peach-palette-fix-1030-v1'
O = R / 'build/smb3plus-body-host-1030-v3'
J = O / 'joint'
D = R / 'docs/qa/checkpoints/2026-10-31/smb3plus-body-palette-host'


def main():
    assert not D.exists() and not (O / 'handoff.json').exists()
    parent = json.loads(B.read(P / 'handoff.json'))
    stage = json.loads(B.read(O / 'source-stage.json'))
    controls = json.loads(B.read(O / 'body-controls-v5.json'))
    for receipt in [parent, stage, controls]:
        B.bound(receipt)
    assert stage['candidate'] == 'fbef5aaffb545e4da35a74dacbd4474267795d8f988e59a4927a7f3ff8efa5e9'
    assert controls['candidate'] == stage['candidate'] and controls['passed']
    assert (controls['foreign_pairs'], controls['source_pixel_cases'], controls['source_palette_cases']) == (4536, 2156, 28)
    assert len(controls['unsupported_existing_Kuribo_records']) == 112
    assert not controls['full_source_form_coverage']
    paths = {Path(p) for receipt in [parent, stage, controls] for p in receipt['bindings']}
    paths.update(p for p in J.rglob('*') if p.is_file())
    paths.update(O / name for name in [
        'source-stage.json', 'body-controls-v4.json', 'body-controls-v5.json',
        'body-negative.json', 'body-negative-v2.json', 'palette-fixture-negative.json',
        'main-build.json', 'union-build.json', 'chr-build.json', 'final-link.json'])
    paths.update(R / f'tools/audit/smb3plus_body_host_controls_1030_v{i}.py' for i in range(1, 6))
    paths.update(R / f'tools/audit/prepare_smb3plus_body_host_1030_v{i}.py' for i in [1, 2])
    paths.add(Path(__file__))
    assert all(p.is_file() and p.resolve().is_relative_to(R) for p in paths)
    bindings = {str(p): B.sha(p) for p in sorted(paths)}
    source_suffixes = {'.s', '.inc', '.cfg', '.chr', '.bin', '.py', '.json', '.lua', '.dep', '.d', '.md', '.png'}
    sources = [p for p in sorted(paths) if p.suffix.lower() in source_suffixes]
    assert all(p.suffix.lower() not in {'.nes', '.exe', '.o', '.dbg', '.lbl', '.map'} for p in sources)
    # The inherited rebuild closure contains earlier source revisions as well
    # as the actual successor. Bound that measured35MB set, not capture data.
    assert sum(p.stat().st_size for p in sources) < 48 * 1024 * 1024
    D.mkdir(parents=True)
    archive = D / 'source-only.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sources:
            z.write(p, p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist()) == len(sources)
        for p in sources:
            assert z.read(p.relative_to(R).as_posix()) == p.read_bytes()
    handoff = dict(
        status='PRIVATE_SMB3PLUS_BODY_PALETTE_SOURCE_FROZEN_NOT_ADMITTED',
        source=True, native=False, installed=False, menu_unlocked=False,
        candidate=stage['candidate'], parent=stage['parent'], joint=str(J),
        controls_sha256=B.sha(O / 'body-controls-v5.json'),
        foreign_pairs=4536, source_pixel_cases=2156, source_palette_cases=28,
        unsupported_existing_Kuribo_records=112, full_source_form_coverage=False,
        CHR_pages=[969, 1019], retired_constant_table_bytes=324,
        audio_owners_byte_exact=controls['audio_owners_byte_exact'],
        archive_sha256=B.sha(archive), archive_bytes=archive.stat().st_size,
        archive_members=len(sources), bindings=bindings,
        limits=stage['limits'] + [
            'Existing disabled Kuribo records are retained failures, not qualified forms.',
            'No new characters are installed or admitted by this graphics-only checkpoint.'])
    B.write(O / 'handoff.json', json.dumps(handoff, indent=2) + '\n')
    for name in ['handoff.json', 'source-stage.json', 'body-controls-v5.json']:
        shutil.copy2(O / name, D / name)
    B.write(D / 'README.md',
        'Private SMB3+ Toad/Peach body and palette integration. This is not a playable unlock. '
        'The candidate uses the genuine recovered 50 CHR pages at969..<1019. Its existing Mario/Luigi '
        'rendering matches4536 old/new CPU cases;2156 regular guest body cases match the original '
        'donor pixels and28 form/statue palettes match the donor palette helper. All81 frames were '
        'examined. The112 records belonging to the host\'s already-disabled Kuribo shoe remain '
        'explicit failures; this is not full source-form coverage.\n\n'
        'The first build exceeded the M3 logic bank and would overlap Rogue Dawn audio. Its link '
        'failure is retained. The successor replaces a sole read of seven constant CHR-high tables '
        'with the same-length immediate value, preserving pointer/register outputs. Four retired '
        '81-byte table spans hold the new helpers and palettes without moving public entries. '
        'Rogue Dawn\'s neighboring audio owners remain byte-exact. The palette fixture\'s missing '
        'RenderForm seed was corrected in a successor; that failure is retained too.\n\n'
        'Kick, float, growth and special-form behavior, real terrain/combat, native gameplay and '
        'menu admission remain. Downloads stays on the corrected64-identity Peach build f56e55cd. '
        'The source archive contains no ROM, executable, object or debug-symbol binaries.\n')
    print(json.dumps(dict(checkpoint=str(D), bindings=len(bindings), members=len(sources),
        archive_bytes=archive.stat().st_size, handoff_sha256=B.sha(O / 'handoff.json'),
        candidate=stage['candidate'], installed=False)))


if __name__ == '__main__':
    main()
