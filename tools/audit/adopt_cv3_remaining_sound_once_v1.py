"""Install the exact passing standalone CV3 repair, retaining a hash-named rollback."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PACK = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/cv3-remaining-legacy-wrapper-v2')
PARENT = '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
FINAL = '2cb5fca0757c3e347c264eab0bf3f22bd02d851787f38802a4af3cb0c3aa1fa5'
SUFFIXES = ['.nes', '.dbg', '.lbl', '.map', '.build.json', '.build.log', '.cv3-mirror.json']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def install_exact(p, target):
    staged = target.with_name(target.name + '.staging-' + FINAL[:8])
    assert not staged.exists(), staged
    shutil.copy2(p, staged)
    assert sha(staged) == FINAL
    staged.replace(target)


def main():
    out = PACK / 'adoption-v1'
    assert not out.exists(), 'One-shot adoption already started; inspect retained state.'
    default = ROOT / 'build/smb-crossover-mmc5-expanded.nes'
    installed = Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')
    dated = installed.with_name('SMB-Crossover-2026-10-26-CV3-MMC5.nes')
    assert sha(default) == sha(installed) == PARENT
    assert not dated.exists()
    assert sha(PACK / 'candidate.nes') == FINAL
    ready_path = PACK / 'freeze-v2/readiness-source-only.json'
    native_path = PACK / 'native-freeze-v1/qualification-native.json'
    assert sha(ready_path) == 'fab1c3c38bd8885ca957442bf84b155adfd7f17a3142118b6c29e769c1141445'
    assert sha(native_path) == '27341f8a370064076b0712d06ce18106bca18dfaf5531cbd2e215f06ff39c4bf'
    ready = json.loads(ready_path.read_text())
    native = json.loads(native_path.read_text())
    assert ready['passed'] and native['passed']
    assert ready['candidate']['sha256'] == FINAL
    assert native['actual_numeric_Hard'] == 1
    assert native['all_DMA_frame_count_differences_vs_baseline'] == []
    assert native['complete_GAME_counts']['candidate']['strict_completed_DMA'] == 167
    assert native['recovered_PPU717']['source_exact_all256bytes']
    assert len(ready['all_frozen_bindings']) == 2521
    assert len(native['all_new_frozen_bindings']) == 31
    for packet, key in [(ready, 'all_frozen_bindings'), (native, 'all_new_frozen_bindings')]:
        for p, h in packet[key].items():
            assert sha(p) == h, p
    checks = []
    for row in ready['source_receipts']:
        p = Path(row['path'])
        assert sha(p) == row['sha256']
        obj = json.loads(p.read_text())
        assert obj['passed'], p
        checks.append(dict(name=p.parent.name, passed=True, receipt=str(p), sha256=sha(p), layer='source/CPU'))
    checks.append(dict(name='same-input Hard1F240 native recovery', passed=True,
                       receipt=str(native_path), sha256=sha(native_path), layer='native'))
    rows = ready['source_files']
    assert len(rows) == 636
    changed = []
    for row in rows:
        p = ROOT / row['path']
        assert (sha(p) if p.exists() else None) == row['accepted50b_sha256'], row['path']
        assert sha(PACK / 'source' / row['path']) == row['sha256']
        if row['sha256'] != row['accepted50b_sha256']:
            changed.append(row)
    assert len(changed) == 8
    old = default.read_bytes()
    new = (PACK / 'candidate.nes').read_bytes()
    assert old[:16] == new[:16] and old[16+128*8192:] == new[16+128*8192:]
    changed_banks = [i for i in range(128) if old[16+i*8192:16+(i+1)*8192] != new[16+i*8192:16+(i+1)*8192]]
    assert changed_banks == [2, 28, 29, 82, 84]
    out.mkdir()
    shutil.copy2(installed, out / ('previous-' + PARENT + '.nes'))
    for suffix in SUFFIXES:
        p = default.with_suffix(suffix)
        if p.exists():
            q = out / 'previous-default' / p.name
            q.parent.mkdir(exist_ok=True)
            shutil.copy2(p, q)
    for row in changed:
        p = ROOT / row['path']
        if p.exists():
            q = out / 'previous-source' / row['path']
            q.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, q)
    try:
        for row in changed:
            shutil.copy2(PACK / 'source' / row['path'], ROOT / row['path'])
        with (out / 'fresh-ROOT-build.log').open('w') as log:
            subprocess.run([sys.executable, '-B', str(ROOT / 'tools/build_mmc5_expanded.py'),
                            '--output', str(out / 'candidate.nes')], cwd=ROOT, check=True,
                           stdout=log, stderr=subprocess.STDOUT)
        assert sha(out / 'candidate.nes') == FINAL, 'Fresh ROOT compile differs'
        for row in rows:
            assert sha(ROOT / row['path']) == row['sha256'], row['path']
        for suffix in SUFFIXES:
            assert (out / 'candidate.nes').with_suffix(suffix).is_file(), suffix
        install_exact(out / 'candidate.nes', dated)
        install_exact(out / 'candidate.nes', installed)
        for suffix in SUFFIXES:
            shutil.copy2((out / 'candidate.nes').with_suffix(suffix), default.with_suffix(suffix))
        assert sha(default) == sha(installed) == sha(dated) == FINAL
    except BaseException:
        for row in changed:
            p = ROOT / row['path']
            if row['accepted50b_sha256'] is None:
                p.unlink(missing_ok=True)
            else:
                shutil.copy2(out / 'previous-source' / row['path'], p)
        for p in (out / 'previous-default').iterdir():
            shutil.copy2(p, default.parent / p.name)
        shutil.copy2(out / ('previous-' + PARENT + '.nes'), installed)
        raise
    checks += [dict(name='fresh canonical ROOT compile and all636 source bindings', passed=True),
               dict(name='installed/default/dated ROM exact hash', passed=True),
               dict(name='unchanged header/CHR and all non-CV3 banks', passed=True)]
    proof = dict(passed=True, adopted=True, goal_complete=False, rom_sha256=FINAL,
                 parent_rom_sha256=PARENT, source_files=changed, checked_source_files=len(rows),
                 verified_source_bindings=2521, verified_native_bindings=31, checks=checks,
                 installed=str(installed), dated_build=str(dated), rollback=str(out),
                 changed_PRG_banks=changed_banks, CHR_header_exact=True,
                 historical_eaa3_native_results_not_reused_as_current=True,
                 scope='Standalone CV3 sound repair and measured Hard1F draw recovery. '
                       'Other eaa3 native cells remain historical. No combined4285/Parodius, '
                       'Turtle70ba or Chip8b4 trial is installed. Full37-character1-1/item/campaign '
                       'and constant60Hz claims remain unverified.')
    (out / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    public = ROOT / 'docs/qa/cv3-sound-adoption-2026-10-26.json'
    shutil.copy2(out / 'proof.json', public)
    print(json.dumps(dict(adopted=True, ROM_sha256=FINAL, installed=str(installed), proof=str(public))))


if __name__ == '__main__':
    main()
