"""Adopt only the reviewed TMNT world renderer and freeze its exact private source."""
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
EXTERNAL = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-render-oa')
LIVE = EXTERNAL/'candidate-v1'
FINAL = ROOT/'build/checkpoints/tmnt-world-render-oa'
QA = ROOT/'build/verification/tmnt-render-oa'
EXPECTED = '06908a38ac7c658c40f6c064b82e71f84ecc0b5f4617ed8b9a17fba6ad677701'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def record(p): return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))


def main():
    assert not FINAL.exists() and not (QA/'proof.json').exists()
    assert sha(LIVE/'candidate.nes') == EXPECTED
    checks = {}
    for name in ('source-proof.json','render-CPU-v1/proof.json','aggregate-render-CPU-v1/proof.json',
                 'CPU-v1/proof.json','shared-fallback-v1/proof.json','performance-proof.json',
                 'route-review.json','visual-review.json','graphics-v2/proof.json',
                 'discover-results.json','replay-results.json','equipment-results.json',
                 'primary-results.json','boss-results.json','ammo-results.json'):
        p = LIVE/name; q = json.loads(p.read_text()); assert q['passed'], name
        assert q.get('ROM_sha256',q.get('new_ROM_sha256')) == EXPECTED, name
        checks[name] = record(p)
    entry = json.loads((LIVE/'entry-37/results.json').read_text())
    assert entry['rom_sha256'] == EXPECTED and entry['identities'] == len(entry['results']) == 37
    assert all(r['exit'] == 0 for r in entry['results'].values())
    ordinary = dict(mmc3='97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4',
                    mmc5='7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128')
    for mapper,digest in ordinary.items(): assert sha(LIVE/f'ordinary-{mapper}.nes') == digest
    public = {f'smb-crossover-{n}.nes':sha(ROOT/f'build/smb-crossover-{n}.nes') for n in ('mmc3','mmc5','mmc3-oversized','mmc5-expanded')}
    assert public == json.loads((ROOT/'build/verification/tmnt-perf-nz/proof.json').read_text())['unchanged_public_ROMs']
    parent = json.loads((ROOT/'build/checkpoints/tmnt-empty-render-nz/manifest.json').read_text())
    source = json.loads((LIVE/'source-proof.json').read_text())
    assert parent['rom_sha256'] == source['parent_ROM_sha256']
    changed = source['source_changes']
    allowed = set(changed)|{'docs/qa/final-verification-plan-2026-10-23.md'}
    assert all(sha(ROOT/n) == h for n,h in parent['source_files'].items() if n not in allowed)
    for n,q in changed.items():
        assert (sha(ROOT/n) if (ROOT/n).exists() else None) == q['before'], n
        assert sha(LIVE/'source'/n) == q['after'], n
    retained = {p.relative_to(EXTERNAL).as_posix():dict(bytes=n,sha256=sha(p)) for p,n,_ in inventory(EXTERNAL)}
    ledger = EXTERNAL/'retained-before-freeze.json'; assert not ledger.exists()
    ledger.write_text(json.dumps(retained,indent=2)+'\n')
    for n,q in changed.items():
        shutil.copy2(LIVE/'source'/n, ROOT/n); assert sha(ROOT/n) == q['after']
    limits = [
        'Private37-identity MMC5 checkpoint; final every-character/every-item matrix and full MMC3 port remain open.',
        'Triple-shot drawing CPU improves2.41–2.52percent; lag remains50–51NMIs/120updates in the arranged component.',
        'All recorded gameplay-state fields match; Donatello has two controller sample differences from changed NMI timing. No byte-exact input comparison claim for that performance pair.',
        'Native component inventory/targets/RNG are arranged; untouched natural delivery of every reward is not established.',
        'Transient NES sprite overload, declared source palette adaptation and missing native TMNT audio remain.',
        'Full lossless route PNGs retained; human visual review is sampled, supplemented by native graphics/scroll checks.',
    ]
    proof = dict(passed=True,goal_complete=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 ROM_SHA256=EXPECTED,parent='tmnt-empty-render-nz',game_changes=changed,checks=checks,
                 all37_entries=record(LIVE/'entry-37/results.json'),ordinary_flag_off_hashes=ordinary,
                 unchanged_public_ROMs=public,retained_before_freeze=record(ledger),limitations=limits)
    (QA/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    names = set(parent['source_files'])|set(changed)|{'docs/qa/tmnt-world-render-2026-10-24.md'}
    names |= {p.relative_to(ROOT).as_posix() for p in (ROOT/'tools/audit').glob('*tmnt*oa.py')}
    hashes = {n:sha(ROOT/n) for n in sorted(names)}
    stage = EXTERNAL/'snapshot-v1'; stage.mkdir(exist_ok=False)
    with zipfile.ZipFile(stage/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n in sorted(names): z.write(ROOT/n,n)
    unpacked = stage/'source'
    with zipfile.ZipFile(stage/'source.zip') as z:
        assert z.testzip() is None
        assert all((unpacked/n).resolve().is_relative_to(unpacked.resolve()) for n in z.namelist()); z.extractall(unpacked)
    assert all(sha(unpacked/n) == h for n,h in hashes.items())
    result = subprocess.run([sys.executable,str(unpacked/'tools/build_mmc5_expanded.py'),
        '--workspace',str(unpacked),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),
        '--output',str(stage/'roundtrip.nes')],cwd=unpacked,capture_output=True,text=True)
    (stage/'rebuild.log').write_text(result.stdout+result.stderr)
    assert result.returncode == 0 and sha(stage/'roundtrip.nes') == EXPECTED
    debug = (LIVE/'candidate.dbg').read_bytes(); packed = gzip.compress(debug,mtime=0)
    assert gzip.decompress(packed) == debug; (stage/'candidate.dbg.gz').write_bytes(packed)
    assert all(sha(ROOT/n) == h for n,h in hashes.items())
    assert all(sha(ROOT/'build'/n) == h for n,h in public.items())
    required = (stage/'source.zip').stat().st_size+len(packed)+500000
    required += sum((LIVE/('candidate'+ext)).stat().st_size for ext in ('.nes','.lbl','.map'))
    before = sum(n for _,n,_ in inventory(ROOT,skip_reparse=True)); assert before+required < 30_000_000_000
    FINAL.mkdir()
    for src,dst in [(stage/'source.zip',FINAL/'source.zip'),(stage/'candidate.dbg.gz',FINAL/'candidate.dbg.gz')]: shutil.copy2(src,dst)
    for ext in ('.nes','.lbl','.map'): shutil.copy2(LIVE/('candidate'+ext),FINAL/('candidate'+ext))
    manifest = dict(utc=proof['utc'],status='PRIVATE_TMNT_WORLD_RENDER_OPTIMIZATION_WITH_OPEN_ROSTER_WORK',
                    identities=37,parent_checkpoint='tmnt-empty-render-nz',rom_sha256=EXPECTED,
                    source_files=hashes,source_zip_sha256=sha(FINAL/'source.zip'),
                    source_bundle_rebuild=dict(exact=True,stage=str(stage)),evidence=record(QA/'proof.json'),
                    limitations=limits,goal_complete=False)
    (FINAL/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    total = sum(n for _,n,_ in inventory(ROOT,skip_reparse=True)); assert total < 30_000_000_000
    summary = dict(checkpoint=str(FINAL),ROM_SHA256=EXPECTED,source_zip_sha256=manifest['source_zip_sha256'],
                   source_files=len(hashes),workspace_bytes=total,retained_lossless_evidence=True,goal_complete=False)
    (QA/'checkpoint.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary),flush=True)


if __name__ == '__main__':main()
