"""Adopt only the verified host optimizations; native music stays staged."""
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

ROOT=Path(__file__).resolve().parents[2]
EXTERNAL=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-render-od')
LIVE=EXTERNAL/'host-only-v2'
PARENT=ROOT/'build/checkpoints/tmnt-world-render-oa'
FINAL=ROOT/'build/checkpoints/tmnt-host-render-od'
QA=ROOT/'build/verification/tmnt-render-od'
EXPECTED='89d8b2002ad0f471e1d4a782d52b681e5f641cba7843ba5f2eb019841b8cdf72'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))


def main():
    assert not FINAL.exists() and not(QA/'proof.json').exists()
    assert sha(LIVE/'candidate.nes')==EXPECTED
    checks={}
    for name in ['preparation.json','health-CPU-v1/proof.json','primary-CPU-v1/proof.json',
                 'primary-IRQ-CPU-v1/proof.json','movement-CPU-v1/proof.json','UI-CPU-v1/proof.json',
                 'inventory-CPU-v1/proof.json','source-equipment-CPU-v1/proof.json','shared-hooks-CPU-v1/proof.json',
                 'performance-vs-OA.json','route-review.json','visual-review.json','graphics-v2/proof.json',
                 'discover-results.json','replay-results.json','equipment-results.json','primary-results.json',
                 'boss-results.json','ammo-results.json','audio-regressions-v1/proof.json','gradius-audio-v1/result.json']:
        p=LIVE/name;q=json.loads(p.read_text());assert q['passed'],name
        assert q.get('ROM_sha256',q.get('new_ROM_sha256',q.get('ROM_SHA256')))==EXPECTED,name
        checks[name]=record(p)
    entry=json.loads((LIVE/'entry-37/results.json').read_text())
    assert entry['rom_sha256']==EXPECTED and entry['identities']==len(entry['results'])==37
    assert all(q['exit']==0 for q in entry['results'].values())
    checks['entry-37/results.json']=record(LIVE/'entry-37/results.json')
    ordinary=json.loads((LIVE/'ordinary/proof.json').read_text());assert ordinary['passed']
    for mapper,digest in ordinary['ordinary_mapper_hashes'].items():assert sha(LIVE/f'ordinary/{mapper}.nes')==digest
    public={f'smb-crossover-{n}.nes':sha(ROOT/f'build/smb-crossover-{n}.nes')for n in ['mmc3','mmc5','mmc3-oversized','mmc5-expanded']}
    assert public==json.loads((ROOT/'build/verification/tmnt-render-oa/proof.json').read_text())['unchanged_public_ROMs']
    parent=json.loads((PARENT/'manifest.json').read_text());prep=json.loads((LIVE/'preparation.json').read_text())
    assert prep['parent_ROM_sha256']==parent['rom_sha256'] and prep['changed_PRG_banks']==[59,86,89] and prep['CHR_unchanged']
    changed=prep['source_changes'];allowed=set(changed)|{'docs/qa/final-verification-plan-2026-10-23.md'}
    assert all(sha(ROOT/n)==h for n,h in parent['source_files'].items()if n not in allowed)
    for n,q in changed.items():
        assert (sha(ROOT/n)if(ROOT/n).exists()else None)==q['before'],n
        assert sha(LIVE/'source'/n)==q['after'],n
    names=set(parent['source_files'])|set(changed)|{'docs/qa/tmnt-host-render-2026-10-24.md'}
    names|={p.relative_to(ROOT).as_posix()for folder in ['tools/audit','tools/reference']
            for pattern in ['*_od.*','*tmnt*oc.py'] for p in(ROOT/folder).glob(pattern)}
    sources={n:LIVE/'source'/n if n in changed else ROOT/n for n in sorted(names)}
    hashes={n:sha(p)for n,p in sources.items()}
    stage=EXTERNAL/'snapshot-v1';stage.mkdir(exist_ok=False)
    with zipfile.ZipFile(stage/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,p in sources.items():z.write(p,n)
    unpacked=stage/'source'
    with zipfile.ZipFile(stage/'source.zip')as z:
        assert z.testzip()is None and set(z.namelist())==set(hashes)
        assert all((unpacked/n).resolve().is_relative_to(unpacked.resolve())for n in z.namelist());z.extractall(unpacked)
    assert all(sha(unpacked/n)==h for n,h in hashes.items())
    result=subprocess.run([sys.executable,str(unpacked/'tools/build_mmc5_expanded.py'),'--workspace',str(unpacked),
        '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(stage/'roundtrip.nes')],cwd=unpacked,capture_output=True,text=True)
    (stage/'rebuild.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0 and sha(stage/'roundtrip.nes')==EXPECTED
    debug=(LIVE/'candidate.dbg').read_bytes();packed=gzip.compress(debug,mtime=0)
    assert gzip.decompress(packed)==debug;(stage/'candidate.dbg.gz').write_bytes(packed)
    required=(stage/'source.zip').stat().st_size+len(packed)+1_000_000
    required+=sum((LIVE/('candidate'+e)).stat().st_size for e in ['.nes','.lbl','.map'])
    assert sum(n for _,n,_ in inventory(ROOT,skip_reparse=True))+required<30_000_000_000
    # All external acceptance and the independent source-only rebuild precede
    # adoption. Only the explicitly hashed game changes enter the live tree.
    for n,q in changed.items():
        assert (sha(ROOT/n)if(ROOT/n).exists()else None)==q['before'],n
        shutil.copy2(LIVE/'source'/n,ROOT/n);assert sha(ROOT/n)==q['after']
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
    limits=['Private37-identity MMC5 checkpoint; final every-identity/every-powerup matrix and full MMC3 port remain open.',
            'Triple-shot stress still drops32/31 draws per120updates; this improves OA51/50 but does not establish constant60Hz.',
            'Native TMNT soundtrack, original weapon effects and body-render experiments remain external and unaccepted.',
            'Equipment targets/RNG are arranged in component tests; natural reward delivery of every item remains open.',
            'All lossless route PNGs are retained; human overview review is sampled, supplemented by automated CHR/scroll checks.',
            'Non-own-inventory and non-TMNT movement paths incur small dispatch overhead, measured and covered by exact CPU comparisons and all37 cold entries.']
    proof=dict(passed=True,goal_complete=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),ROM_SHA256=EXPECTED,
        parent='tmnt-world-render-oa',game_changes=changed,checks=checks,ordinary_flag_off_hashes=ordinary['ordinary_mapper_hashes'],
        unchanged_public_ROMs=public,source_only_rebuild_exact=True,limitations=limits)
    QA.mkdir(parents=True,exist_ok=True);(QA/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    FINAL.mkdir()
    for src,dst in [(stage/'source.zip',FINAL/'source.zip'),(stage/'candidate.dbg.gz',FINAL/'candidate.dbg.gz')]:shutil.copy2(src,dst)
    for ext in ['.nes','.lbl','.map']:shutil.copy2(LIVE/('candidate'+ext),FINAL/('candidate'+ext))
    manifest=dict(utc=proof['utc'],status='PRIVATE_TMNT_HOST_OPTIMIZATION_WITH_OPEN_ROSTER_WORK',identities=37,
        parent_checkpoint='tmnt-world-render-oa',rom_sha256=EXPECTED,source_files=hashes,source_zip_sha256=sha(FINAL/'source.zip'),
        source_bundle_rebuild=dict(exact=True,stage=str(stage)),evidence=record(QA/'proof.json'),limitations=limits,goal_complete=False)
    (FINAL/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    assert all(sha(ROOT/'build'/n)==h for n,h in public.items())
    used=sum(n for _,n,_ in inventory(ROOT,skip_reparse=True));assert used<30_000_000_000
    summary=dict(checkpoint=str(FINAL),ROM_SHA256=EXPECTED,source_zip_sha256=manifest['source_zip_sha256'],source_files=len(hashes),
                 workspace_bytes=used,retained_lossless_evidence=True,goal_complete=False)
    (QA/'checkpoint.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
