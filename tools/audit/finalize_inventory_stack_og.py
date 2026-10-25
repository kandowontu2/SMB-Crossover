"""One-shot verified source-only rebuild and narrow inventory-stack adoption."""
from pathlib import Path
import datetime
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from archive_workspace_hz import inventory

ROOT = Path(__file__).resolve().parents[2]
EXTERNAL = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-sophia-lock-og')
LIVE = EXTERNAL/'fix-v1'
PARENT = ROOT/'build/checkpoints/injury-page-of'
FINAL = ROOT/'build/checkpoints/inventory-stack-og'
QA = ROOT/'build/verification/inventory-stack-og'
EXPECTED = '2e916d5da5448bec576a930fddf3d1469472b976756c95da6fadddb2ca98729a'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path):
    return dict(path=str(path),bytes=path.stat().st_size,sha256=sha(path))


def main():
    assert not FINAL.exists() and not (QA/'proof.json').exists()
    assert sha(LIVE/'candidate.nes') == EXPECTED
    checks = {}
    for name in ['CPU-v2/proof.json','IRQ-CPU-v1/proof.json',
            'guarded-easy-v3/proof.json','guarded-hard-v3/proof.json',
            'routes/discover-results.json','routes/replay-results.json','routes/route-review.json',
            'visual-review.json','performance-vs-OF.json','audio-regressions-v1/proof.json']:
        f = LIVE/name; q = json.loads(f.read_text())
        assert q['passed'] and q['ROM_sha256'] == EXPECTED, name
        checks[name] = record(f)
    negative = EXTERNAL/'reproduction-v7/proof.json'; q = json.loads(negative.read_text())
    assert q['passed'] and q['expectation']=='freeze' and q['ROM_sha256']==sha(PARENT/'candidate.nes')
    assert q['observed']['first_poison_address']==0x17a and q['observed']['first_invalid_pc']==0x17b
    checks['negative_reproduction'] = record(negative)
    entry = json.loads((LIVE/'entry-37/results.json').read_text())
    assert entry['rom_sha256']==EXPECTED and entry['identities']==len(entry['results'])==37
    assert all(q['exit']==0 for q in entry['results'].values())
    checks['entry-37/results.json'] = record(LIVE/'entry-37/results.json')
    public = {f'smb-crossover-{n}.nes':sha(ROOT/f'build/smb-crossover-{n}.nes')
              for n in ['mmc3','mmc5','mmc3-oversized','mmc5-expanded']}
    old_receipt = json.loads((ROOT/'build/verification/proto-hurt-of/proof.json').read_text())
    assert public == old_receipt['unchanged_public_ROMs']
    parent = json.loads((PARENT/'manifest.json').read_text())
    assert sha(PARENT/'source.zip')==parent['source_zip_sha256']
    prep = json.loads((LIVE/'preparation.json').read_text())
    assert prep['parent_ROM_sha256']==parent['rom_sha256'] and prep['ROM_sha256']==EXPECTED
    assert prep['changed_PRG_banks']==[59,66] and prep['CHR_unchanged'] and prep['all_preexisting_labels_unchanged']
    changes = prep['source_changes']
    documentation = {'docs/qa/final-verification-plan-2026-10-23.md',
        'docs/qa/full-roster-sweep-2026-10-24.md','docs/qa/inventory-stack-repair-2026-10-24.md'}
    assert all(sha(ROOT/n)==h for n,h in parent['source_files'].items() if n not in set(changes)|documentation)
    for name,q in changes.items():
        assert (sha(ROOT/name) if (ROOT/name).exists() else None)==q['before'], name
        assert sha(LIVE/'source'/name)==q['after'], name
    names = set(parent['source_files']) | set(changes) | documentation | {'tools/playthroughs/full_roster_policy_og.lua'}
    names |= {p.relative_to(ROOT).as_posix() for p in (ROOT/'tools/audit').glob('*_og.*')}
    sources = {n:LIVE/'source'/n if n in changes else ROOT/n for n in sorted(names)}
    hashes = {n:sha(f) for n,f in sources.items()}
    stage = EXTERNAL/'snapshot-v1'; stage.mkdir(exist_ok=False)
    with zipfile.ZipFile(stage/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,f in sources.items(): z.write(f,name)
    unpacked = stage/'source'
    with zipfile.ZipFile(stage/'source.zip') as z:
        assert z.testzip() is None and set(z.namelist())==set(hashes)
        assert all((unpacked/n).resolve().is_relative_to(unpacked.resolve()) for n in z.namelist())
        z.extractall(unpacked)
    assert all(sha(unpacked/n)==h for n,h in hashes.items())
    compiler = ROOT/'tools/Windows/cc65/bin/cl65.exe'
    command = [sys.executable,str(unpacked/'tools/build_mmc5_expanded.py'),
        '--workspace',str(unpacked),'--compiler',str(compiler)]
    result = subprocess.run(command+['--output',str(stage/'roundtrip.nes')],cwd=unpacked,capture_output=True,text=True)
    (stage/'rebuild.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0 and sha(stage/'roundtrip.nes')==EXPECTED
    ordinary = {}
    for mapper in ['mmc3','mmc5']:
        target = stage/f'ordinary-{mapper}.nes'
        result = subprocess.run(command+['--flag-off',mapper,'--output',str(target)],cwd=unpacked,capture_output=True,text=True)
        (stage/f'ordinary-{mapper}.log').write_text(result.stdout+result.stderr)
        assert result.returncode==0 and sha(target)==old_receipt['ordinary_flag_off_hashes'][mapper], mapper
        ordinary[mapper]=sha(target)
    assert all(sha(unpacked/n)==h for n,h in hashes.items())
    debug = (LIVE/'candidate.dbg').read_bytes(); packed = gzip.compress(debug,mtime=0)
    assert gzip.decompress(packed)==debug
    (stage/'candidate.dbg.gz').write_bytes(packed)
    required = (stage/'source.zip').stat().st_size+len(packed)+1_000_000
    required += sum((LIVE/('candidate'+ext)).stat().st_size for ext in ['.nes','.lbl','.map'])
    assert sum(n for _,n,_ in inventory(ROOT,skip_reparse=True))+required < 30_000_000_000
    # Adopt only after every acceptance gate and independent rebuild above.
    for name,q in changes.items():
        assert (sha(ROOT/name) if (ROOT/name).exists() else None)==q['before']
        shutil.copy2(LIVE/'source'/name,ROOT/name)
        assert sha(ROOT/name)==q['after']
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
    limits = [
        'Narrow private MMC5 stack repair. Full37/every-item/final-mapper goal remains open.',
        'Two fresh Sophia zero-death1-1discoveries and exact independent replays reach movable1-2;37cold entries are not37level clears.',
        'Raw temporary projectile origins are projected only with positive native proof; original failed traces/reports remain retained and all strict bounds stay unchanged.',
        'Two24-frame overviews plus three borrowed-origin frames were viewed. Full PNG retention is not exhaustive human pixel review.',
        'Sophia route lag2270/2235 NMIs remains open. Turtle heavy-weapon27/25lagNMIs are unchanged.',
        'Old frame-timed OF input dies before its old failure on the faster query; that failed controller is retained and not counted as repaired replay evidence.',
        'All requested source audio/fidelity work, other route/powerup failures and full oversized MMC3 integration still require completion.',
        'Published ROMs and the guide are preserved; no final release is claimed.',
    ]
    proof = dict(passed=True,goal_complete=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        ROM_SHA256=EXPECTED,parent='injury-page-of',game_changes=changes,checks=checks,
        ordinary_flag_off_hashes=ordinary,unchanged_public_ROMs=public,
        source_only_rebuild_exact=True,limitations=limits)
    QA.mkdir(parents=True,exist_ok=True); (QA/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    FINAL.mkdir()
    for f in ['source.zip','candidate.dbg.gz']:shutil.copy2(stage/f,FINAL/f)
    for ext in ['.nes','.lbl','.map']:shutil.copy2(LIVE/('candidate'+ext),FINAL/('candidate'+ext))
    manifest = dict(utc=proof['utc'],status='PRIVATE_INVENTORY_STACK_REPAIR_WITH_OPEN_ROSTER_WORK',identities=37,
        parent_checkpoint='injury-page-of',rom_sha256=EXPECTED,source_files=hashes,
        source_zip_sha256=sha(FINAL/'source.zip'),source_bundle_rebuild=dict(exact=True,stage=str(stage)),
        evidence=record(QA/'proof.json'),limitations=limits,goal_complete=False)
    (FINAL/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    assert all(sha(ROOT/'build'/n)==h for n,h in public.items())
    used = sum(n for _,n,_ in inventory(ROOT,skip_reparse=True)); assert used<30_000_000_000
    summary = dict(checkpoint=str(FINAL),ROM_SHA256=EXPECTED,source_zip_sha256=manifest['source_zip_sha256'],
        source_files=len(hashes),workspace_bytes=used,retained_lossless_evidence=True,goal_complete=False)
    (QA/'checkpoint.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
