"""Adopt the three-file, current-parent Roll pickup fade fix with rollback."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/roll-fade-current9e0e-v1')
PARENT = '9e0e5ed5d4957aac9baa040ea76616ee4a88233312700b78a8c55250c19f42d3'
FINAL = '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out = D / 'adoption-v1'
    assert not out.exists(), 'One-shot adoption already started; inspect retained state.'
    default = ROOT / 'build/smb-crossover-mmc5-expanded.nes'
    installed = Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    assert sha(default) == sha(installed) == sha(D / 'baseline/candidate.nes') == PARENT
    assert sha(D / 'candidate.nes') == FINAL
    packet = D / 'final-packet-v3/proof.json'
    assert sha(packet) == '0dd47e4e6af95c9266591fc9d0b574295b69e5bff0ef63b1970a60c2035b1915'
    q = json.loads(packet.read_text())
    assert q['passed'] and q['current_parent'] == PARENT and q['combined_candidate'] == FINAL
    assert q['fresh_CPU_cases'] == 181028 and q['fresh_current_native_profiles'] == 4
    assert q['current_candidate_both_modes_passed'] and q['current_parent_both_negative_fade_receipts_retained']
    assert not q['historical_full_pool_reused_as_current'] and q['selected_actual_PPU_frames_reviewed'] == 48
    manifest = D / 'final-packet-v3/manifest.json'
    assert sha(manifest) == q['manifest_sha256'] == '5a655a4c27317d377d4d597cde30104e8d339e21bc01822dae9fd6e27176bf6a'
    for name, digest in json.loads(manifest.read_text()).items():
        assert sha(Path(name)) == digest, name
    for row in q['matched_idle_controls']:
        assert row['completed_updates_each'] == row['baseline_actual_wall_frames'] == row['candidate_actual_wall_frames'] == row['renders_each'] == 120
        assert row['inclusive_cycle_delta_mean'] == 60
    build = json.loads((D / 'proof.json').read_text())
    assert build['passed'] and build['changed_PRG_bytes'] == {'119': 36}
    assert build['all_old_symbol_addresses_identical'] and build['old_symbols_checked'] == 72217
    assert build['all_other_ROM_bytes_identical'] and build['RAM_CHR_art_identical']
    before = json.loads((D / 'parent-source-ledger.json').read_text())
    after = json.loads((D / 'candidate-source-ledger.json').read_text())
    files = {n: dict(before_sha256=before.get(n), after_sha256=after.get(n))
             for n in sorted(set(before) | set(after)) if before.get(n) != after.get(n)}
    assert set(files) == {'src/roll.s', 'src/roll_render.s', 'src/roll_drop_fade.s'}
    for name, digest in before.items():
        assert sha(ROOT / name) == digest, name
    for name, row in files.items():
        assert sha(D / 'overlay' / name) == row['after_sha256'], name
    assert not (ROOT / 'src/roll_drop_fade.s').exists()
    for mapper, digest in build['ordinary_flag_off_hashes'].items():
        assert sha(D / ('candidate-' + mapper + '.nes')) == digest
    # Independently rerun whole-CPU and raw PPU/RGB checks by ROOT.
    refs = {}
    for name in ['root-fade-cpu-v1/proof.json', 'root-owner-cpu-v1/proof.json', 'root-calm-rgb-v1/proof.json']:
        path = D / name
        obj = json.loads(path.read_text())
        assert obj['passed']
        refs[str(path)] = sha(path)
    rgb = json.loads((D / 'root-calm-rgb-v1/proof.json').read_text())
    assert sha(D / 'root-calm-rgb-v1/proof.json') == '83e9d375fa3535df0f3ef077f9734fd2110a2803cba70053dc5965d5bd7fdf30'
    for name, digest in rgb['bindings'].items():
        assert sha(Path(name)) == digest, name
    raw = (D / 'candidate.nes').read_bytes()
    old = (D / 'baseline/candidate.nes').read_bytes()
    at = 16+119*8192
    assert raw[:at] == old[:at] and raw[at+8192:] == old[at+8192:]
    assert sum(x != y for x, y in zip(raw, old)) == 36
    assert raw[at+0x68f:at+0x692] == bytes.fromhex('20c0aa')
    assert old[at+0xac0:at+0xae1] == b'\xff'*33
    out.mkdir()
    shutil.copy2(installed, out / 'previous-MMC5.nes')
    suffixes = ['.nes', '.dbg', '.lbl', '.map', '.build.json', '.build.log', '.cv3-mirror.json']
    previous = out / 'previous-default'
    previous.mkdir()
    for suffix in suffixes:
        source = default.with_suffix(suffix)
        if source.exists():
            shutil.copy2(source, previous / source.name)
    for name, row in files.items():
        if row['before_sha256'] is not None:
            backup = out / 'previous-source' / name
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, backup)
    try:
        for name in files:
            shutil.copy2(D / 'overlay' / name, ROOT / name)
        with (out / 'fresh-ROOT-build.log').open('w') as log:
            subprocess.run([sys.executable, str(ROOT / 'tools/build_mmc5_expanded.py'),
                            '--output', str(out / 'candidate.nes')], cwd=ROOT,
                           check=True, stdout=log, stderr=subprocess.STDOUT)
        assert sha(out / 'candidate.nes') == FINAL, 'Fresh canonical ROOT compile differs'
        for suffix in suffixes:
            assert (out / 'candidate.nes').with_suffix(suffix).is_file(), suffix
    except BaseException:
        for name, row in files.items():
            if row['before_sha256'] is None:
                (ROOT / name).unlink(missing_ok=True)
            else:
                shutil.copy2(out / 'previous-source' / name, ROOT / name)
        raise
    stage = installed.with_name(installed.stem + '.staging-' + FINAL[:8] + '.nes')
    assert not stage.exists()
    shutil.copy2(out / 'candidate.nes', stage)
    assert sha(stage) == FINAL
    stage.replace(installed)
    for suffix in suffixes:
        shutil.copy2((out / 'candidate.nes').with_suffix(suffix), default.with_suffix(suffix))
    assert sha(default) == sha(installed) == FINAL
    proof = dict(adopted=True, goal_complete=False, ROM_sha256=FINAL, parent_ROM_sha256=PARENT,
                 fresh_canonical_ROOT_compile_exact=True, installed=str(installed), source_files=files,
                 changed_PRG_bytes={'119': 36}, all_other_ROM_RAM_CHR_art_and_old_addresses_exact=True,
                 old_scoped_symbol_addresses_retained=72217, new_RAM_bytes=0, new_CHR_bytes=0,
                 predicate='Nonempty pickup hidden when (AgeHi!=0 OR Age>=240) AND (native FrameCounter&1)!=0.',
                 root_independent_receipts=refs, ROOT_CPU_cases=164748,
                 fresh_component_CPU_cases=q['fresh_CPU_cases'], native_profiles=q['profiles'],
                 matched_idle_controls=q['matched_idle_controls'], raw_PPU_RGB_frames=48,
                 qualification_packet_sha256=sha(packet), manifest_sha256=sha(manifest),
                 rollback=str(out), scope=q['scope'],
                 remaining='Current calm/native/CPU component qualification only. Historical full-pool9bac/c32b receipts remain historical. Crowded visibility, original mobile executable fidelity, all-current roster/item/campaign/music work and MMC3 expanded certification remain open.')
    (out / 'proof.json').write_text(json.dumps(proof, indent=2)+'\n')
    dest = ROOT / 'build/verification/roll-drop-fade'
    dest.mkdir(exist_ok=True)
    shutil.copy2(out / 'proof.json', dest / 'proof.json')
    print(json.dumps(dict(adopted=True, ROM_sha256=FINAL, proof=str(out / 'proof.json'), proof_sha256=sha(out / 'proof.json'))))


if __name__ == '__main__':
    main()
