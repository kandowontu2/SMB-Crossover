"""Save the exact menu-only successor, its bounded native check, and private ROM."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

R = Path(__file__).resolve().parents[2]
O = R / 'build/roster-visual-fixes-1030-v1'
N = R / 'build/current-chip-menu-ui44c-1030-v1'
D = R / 'docs/qa/checkpoints/2026-10-30/roster-menu-visual-fixes'
TARGET = '44c92ad7f75f74d5d4712a5bb30fb057b6d8adda54983ca149c4b7d03492ff34'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def copy_exact(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        assert sha(src) == sha(dst), ('Existing checkpoint differs', dst)
    else:
        shutil.copy2(src, dst)
    assert sha(src) == sha(dst)


def main():
    assert sha(O / 'candidate.nes') == TARGET
    source = json.loads((O / 'source-proof.json').read_text())
    menu = json.loads((O / 'menu-controls.json').read_text())
    native = json.loads((N / 'result.json').read_text())
    packet = json.loads((N / 'native-facing-smoke-packet.json').read_text())
    for q in (source, packet):
        for path, digest in q['bindings'].items():
            assert sha(path) == digest, path
    assert source['passed'] and menu['passed'] and native['passed']
    assert source['candidate'] == menu['candidate'] == native['ROM_sha256'] == TARGET
    assert source['all_gameplay_instructions_WRAM_payloads_header_other_CHR_exact']
    assert native['frames'] == 341 and native['completed_loops'] == 326
    assert native['markers']['first-active']['frame'] == 266
    assert native['zero_deaths'] and native['nmi_checks'] == native['irq_checks'] == 75
    assert (N / 'root-selected-native-frames.png').is_file(), 'View the five native frames first'
    D.mkdir(parents=True, exist_ok=True)
    archive = D / 'source-and-native.zip'
    assert not archive.exists(), 'Do not replace a checkpoint'
    suffixes = {'.s', '.inc', '.cfg', '.json', '.md', '.py', '.patch', '.chr', '.nam', '.rle', '.dep', '.d', '.png'}
    files = {p for p in O.rglob('*') if p.is_file() and p.suffix in suffixes}
    files |= {p for p in N.iterdir() if p.is_file()}
    files |= {Path(__file__), R / 'tools/audit/prepare_roster_visual_fixes_1030_v1.py',
              R / 'tools/audit/controls_roster_visual_fixes_1030_v1.py'}
    assert not any(p.suffix in {'.nes', '.o'} for p in files)
    members = []
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(files):
            member = p.relative_to(R).as_posix()
            z.write(p, member)
            members.append(dict(member=member, sha256=sha(p)))
    with zipfile.ZipFile(archive) as z:
        assert z.namelist() == [q['member'] for q in members]
        for q in members:
            assert hashlib.sha256(z.read(q['member'])).hexdigest() == q['sha256']
    (D / 'archive-members.json').write_text(json.dumps(members, indent=2) + '\n')
    for name in ('source-proof.json', 'source.patch', 'menu-controls.json'):
        copy_exact(O / name, D / name)
    for name in ('result.json', 'root-selected-native-frames.png'):
        copy_exact(N / name, D / ('native-' + name))
    downloads = Path('C:/Users/kando/Downloads')
    latest = downloads / 'SMB-Crossover-Latest-WIP-MMC5.nes'
    old = sha(latest)
    assert old == '08f1a75fb13f1974270bf9c6732d050f778f7f5b8b8a3361683416c242a176f3'
    backup = downloads / ('SMB-Crossover-Before-Menu-Fixes-' + old[:8] + '-MMC5.nes')
    copy_exact(latest, backup)
    version = downloads / 'SMB-Crossover-2026-10-30-Ready54-Menu-Fixes-MMC5.nes'
    copy_exact(O / 'candidate.nes', version)
    shutil.copy2(version, latest)
    assert sha(latest) == sha(version) == TARGET
    receipt = dict(
        status='PRIVATE_WIP_MENU_REPAIR_INSTALLED', candidate=TARGET, previous=old,
        ready=54, pending=26, total_identities=80,
        latest=str(latest), versioned=str(version), backup=str(backup),
        changes=['24px source-derived gray Donkey Kong icon without rescaling',
                 'Gray Chip/Goku/Gimmick/SMB3 Bowser thumbnails face right',
                 'Pending Bowser and Thomas color previews face right',
                 'Fourth row no longer shares the preview panel palette',
                 'Ready Quick Man and Arthur no longer have coming-soon markers'],
        all_gameplay_bytes_and_existing_symbol_values_unchanged=True,
        actual_native_result_pass=True, root_viewed_all_five_selected_PPU_frames=True,
        native_scope=dict(physical_frames=341, global_completed_loops=326,
                          genuinely_active_completed_updates=75,
                          zero_deaths=True, native_NMI_checks=75, native_IRQ_checks=75,
                          all_source_and_physical_CHR_OAM_checks_retained=True),
        fixture_scope_correction='The inherited fixture says 220 active updates but counts startup GameLoops. Actual gameplay scope is 75 completed updates; no full level claim.',
        limits=['No new roster unlock in this menu-only build.',
                'Goku and Gimmick cold colored portraits are separate pending source leaves.',
                'Not a full1-1/allpowerups/performance qualification.'],
        archive=str(archive), archive_sha256=sha(archive), archive_members=len(members),
        bindings={str(p):sha(p) for p in [O/'source-proof.json', O/'menu-controls.json',
                  N/'result.json', N/'native-facing-smoke-packet.json', N/'root-selected-native-frames.png']},
    )
    dst = R / 'docs/qa/roster-menu-visual-fixes-2026-10-30.json'
    assert not dst.exists()
    dst.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(installed=str(latest), sha256=TARGET,
                          archive_bytes=archive.stat().st_size, members=len(members))))


if __name__ == '__main__':
    main()
