"""One-shot exact source rebuild and guarded adoption of OJ collision routing."""
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
EXTERNAL=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-collision-dispatch-oj')
LIVE=EXTERNAL/'probe-v3'
PARENT=ROOT/'build/checkpoints/inventory-stack-og'
FINAL=ROOT/'build/checkpoints/collision-dispatch-oj'
QA=ROOT/'build/verification/collision-dispatch-oj'
EXPECTED='88906bd9b21a65c2a09128730599a4683ff6123a655386c1b55d3e0ec1ef3b8a'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def record(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))


def main():
    assert not FINAL.exists()and not(QA/'proof.json').exists()
    assert sha(LIVE/'candidate.nes')==EXPECTED
    checks={}
    for n in ['CPU-v1/proof.json','IRQ-CPU-v1/proof.json','layout-v1/proof.json',
            'collision-comparison-v2.json','turtle-performance-vs-OG.json',
            'guarded-easy-v1/proof.json','guarded-hard-v1/proof.json',
            'routes/route-review.json','visual-review.json','audio-regressions-v1/proof.json']:
        f=LIVE/n;q=json.loads(f.read_text());assert q['passed']and q['ROM_sha256']==EXPECTED,n
        checks[n]=record(f)
    review=json.loads((LIVE/'routes/route-review.json').read_text())
    assert len(review['runs'])==3 and not review['all_four_requested_routes_pass']
    assert sum(v['complete_lossless_frames']for v in review['runs'].values())==14298
    negative=LIVE/'routes/replay-results.json';q=json.loads(negative.read_text())
    assert not q['passed']and q['ROM_sha256']==EXPECTED
    checks['unchanged_failed_four_case_replay_aggregate']=record(negative)
    visual=json.loads((LIVE/'visual-review.json').read_text())
    assert visual['root_viewed']and not visual['exhaustive_human_pixel_review']
    assert all(sha(Path(q['path']))==q['sha256']for q in visual['images'])
    entry=LIVE/'entry-37/results.json';q=json.loads(entry.read_text())
    assert q['rom_sha256']==EXPECTED and q['identities']==len(q['results'])==37
    assert all(c['exit']==0 for c in q['results'].values());checks['entry-37/results.json']=record(entry)
    parent=json.loads((PARENT/'manifest.json').read_text())
    assert sha(PARENT/'candidate.nes')==parent['rom_sha256']and sha(PARENT/'source.zip')==parent['source_zip_sha256']
    prep=json.loads((LIVE/'preparation.json').read_text());changes=prep['source_changes']
    assert prep['parent_ROM_sha256']==parent['rom_sha256']and prep['ROM_sha256']==EXPECTED
    assert prep['changed_PRG_banks']==[66,127]and prep['CHR_unchanged']and prep['all_preexisting_labels_unchanged']
    assert set(changes)=={'src/expanded.s','src/entrypoint.s','smb1base-mmc5-expanded.cfg','src/hot_collision_gate.s'}
    documentation={'docs/qa/final-verification-plan-2026-10-23.md','docs/qa/collision-dispatch-2026-10-24.md',
        'docs/qa/controller-progress-2026-10-24.md'}
    assert all(sha(ROOT/n)==h for n,h in parent['source_files'].items()if n not in documentation)
    for n,q in changes.items():
        assert(sha(ROOT/n)if(ROOT/n).exists()else None)==q['before'],n
        assert sha(LIVE/'source'/n)==q['after'],n
    old_receipt=json.loads((ROOT/'build/verification/inventory-stack-og/proof.json').read_text())
    public={n:sha(ROOT/'build'/n)for n in old_receipt['unchanged_public_ROMs']}
    assert public==old_receipt['unchanged_public_ROMs']
    names=set(parent['source_files'])|set(changes)|documentation
    names|={p.relative_to(ROOT).as_posix()for suffix in ['oh','oi','oj','ok']for p in(ROOT/'tools/audit').glob('*_'+suffix+'.*')}
    sources={n:LIVE/'source'/n if n in changes else ROOT/n for n in sorted(names)}
    hashes={n:sha(f)for n,f in sources.items()}
    stage=EXTERNAL/'snapshot-v1';stage.mkdir(exist_ok=False)
    with zipfile.ZipFile(stage/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,f in sources.items():z.write(f,n)
    unpacked=stage/'source'
    with zipfile.ZipFile(stage/'source.zip')as z:
        assert z.testzip()is None and set(z.namelist())==set(hashes)
        assert all((unpacked/n).resolve().is_relative_to(unpacked.resolve())for n in z.namelist())
        z.extractall(unpacked)
    assert all(sha(unpacked/n)==h for n,h in hashes.items())
    command=[sys.executable,str(unpacked/'tools/build_mmc5_expanded.py'),'--workspace',str(unpacked),
        '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe')]
    z=subprocess.run(command+['--output',str(stage/'roundtrip.nes')],cwd=unpacked,capture_output=True,text=True)
    (stage/'rebuild.log').write_text(z.stdout+z.stderr)
    assert z.returncode==0 and sha(stage/'roundtrip.nes')==EXPECTED
    ordinary={}
    for mapper in ['mmc3','mmc5']:
        target=stage/('ordinary-'+mapper+'.nes')
        z=subprocess.run(command+['--flag-off',mapper,'--output',str(target)],cwd=unpacked,capture_output=True,text=True)
        (stage/('ordinary-'+mapper+'.log')).write_text(z.stdout+z.stderr)
        assert z.returncode==0 and sha(target)==old_receipt['ordinary_flag_off_hashes'][mapper],mapper
        ordinary[mapper]=sha(target)
    assert all(sha(unpacked/n)==h for n,h in hashes.items())
    debug=(LIVE/'candidate.dbg').read_bytes();packed=gzip.compress(debug,mtime=0)
    assert gzip.decompress(packed)==debug;(stage/'candidate.dbg.gz').write_bytes(packed)
    required=(stage/'source.zip').stat().st_size+len(packed)+1_000_000
    required+=sum((LIVE/('candidate'+ext)).stat().st_size for ext in ['.nes','.lbl','.map'])
    assert sum(n for _,n,_ in inventory(ROOT,skip_reparse=True))+required<30_000_000_000
    # All proof, source, hash and storage gates above precede the four-file adoption.
    for n,q in changes.items():
        assert(sha(ROOT/n)if(ROOT/n).exists()else None)==q['before']
        shutil.copy2(LIVE/'source'/n,ROOT/n);assert sha(ROOT/n)==q['after']
    assert all(sha(ROOT/n)==h for n,h in hashes.items())
    limits=[
        'Narrow private MMC5 optimization. Full37/both-mode/every-item/source-fidelity/final-mapper goal remains open.',
        'Three current-hash zero-death1-1discoveries and exact independent replays reach movable1-2;37cold entries are not37clears.',
        'Chip Hard discovery still fails; the original four-case discovery/replay aggregates remain failed and retained.',
        'The OI older-hash sweep has39clean discoveries/29failures with no new fixed replay credit. Darkwing first Arrow is stamped but not physically acquired.',
        'Sampled human overview/borrowed-origin inspection does not certify every pixel of14298retained PNGs.',
        'Matched native component arenas improve lag without recorded state differences. Sophia attack and other gameplay still lag; no constant60Hz claim.',
        'Video-poll-indexed first component fixture was invalid for matched gameplay; its failed report remains retained and uncredited.',
        'Source audio/art/behavior gaps, remaining route/item failures, full oversized MMC3 integration and final complete matrix still require completion.',
        'Published ROMs and player guide are preserved; no final release is claimed.'
    ]
    proof=dict(passed=True,goal_complete=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        ROM_SHA256=EXPECTED,parent='inventory-stack-og',game_changes=changes,checks=checks,
        ordinary_flag_off_hashes=ordinary,unchanged_public_ROMs=public,source_only_rebuild_exact=True,limitations=limits)
    QA.mkdir(parents=True,exist_ok=True);(QA/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    FINAL.mkdir()
    for n in ['source.zip','candidate.dbg.gz']:shutil.copy2(stage/n,FINAL/n)
    for ext in ['.nes','.lbl','.map']:shutil.copy2(LIVE/('candidate'+ext),FINAL/('candidate'+ext))
    manifest=dict(utc=proof['utc'],status='PRIVATE_COLLISION_QUERY_OPTIMIZATION_WITH_OPEN_ROSTER_WORK',identities=37,
        parent_checkpoint='inventory-stack-og',rom_sha256=EXPECTED,source_files=hashes,source_zip_sha256=sha(FINAL/'source.zip'),
        source_bundle_rebuild=dict(exact=True,stage=str(stage)),evidence=record(QA/'proof.json'),limitations=limits,goal_complete=False)
    (FINAL/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    assert all(sha(ROOT/'build'/n)==h for n,h in public.items())
    used=sum(n for _,n,_ in inventory(ROOT,skip_reparse=True));assert used<30_000_000_000
    summary=dict(checkpoint=str(FINAL),ROM_SHA256=EXPECTED,source_zip_sha256=manifest['source_zip_sha256'],
        source_files=len(hashes),workspace_bytes=used,retained_lossless_evidence=True,goal_complete=False)
    (QA/'checkpoint.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
