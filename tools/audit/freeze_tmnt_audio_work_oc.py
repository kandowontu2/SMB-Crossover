"""Freeze reproducible staged audio work without adopting its failed performance gate."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from archive_workspace_hz import inventory

ROOT=Path(__file__).resolve().parents[2]
OUT=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-oc')
OB=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-ob')
STAGE=OUT/'candidate-v7'
EXPECTED='dde53bc1bdb02489230dcd561b96496d1551cdc2b0b684c98cede6d3ca5c3fff'
GAME=['audio/tmnt/native-drum.dmc','src/tmnt_audio_samus_cold.s','src/tmnt_audio.s',
      'src/tmnt_audio_resident.s','src/tmnt_audio_writers.s','src/tmnt-native.inc',
      'src/entrypoint.s','src/samus_audio.s','src/gradius_audio.s','src/guest_audio.s',
      'src/music_drivers/audio.s','src/player.s','src/metasprite_engine.s','smb1base-mmc5-expanded.cfg']


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def record(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))


def main():
    packet=OUT/'work-packet-v1';assert not packet.exists()
    assert sha(STAGE/'candidate.nes')==EXPECTED
    parent=json.loads((ROOT/'build/checkpoints/tmnt-world-render-oa/manifest.json').read_text())
    assert all(sha(ROOT/n)==h for n,h in parent['source_files'].items()if n!='docs/qa/final-verification-plan-2026-10-23.md'),'Live OA source changed'
    prep=json.loads((STAGE/'preparation.json').read_text());assert prep['passed']and prep['ROM_sha256']==EXPECTED
    checks={}
    for name in ['linked-CPU-v1/proof.json','front-gates-CPU-v1/proof.json','fallback-CPU-v3/proof.json','native-audio-allones-v1/result.json']:
        p=STAGE/name;q=json.loads(p.read_text());assert q['passed']and q['ROM_sha256']==EXPECTED,name;checks[name]=record(p)
    entry=json.loads((STAGE/'entry-37/results.json').read_text())
    assert entry['rom_sha256']==EXPECTED and entry['identities']==len(entry['results'])==37
    assert all(q['exit']==0 for q in entry['results'].values());checks['entry-37/results.json']=record(STAGE/'entry-37/results.json')
    perf=json.loads((STAGE/'performance-proof.json').read_text())
    assert perf['ROM_sha256']==EXPECTED and perf['measurement_valid']and not perf['performance_gate_passed']and not perf['passed']
    names=set(parent['source_files'])|set(json.loads((OB/'work-packet-v1/manifest.json').read_text())['source_files'])|set(GAME)
    names|={'tests/tmnt-native-audio-oc.lua','docs/qa/tmnt-native-audio-integration-2026-10-24.md'}
    for folder in ['tools/audit','tools/reference']:
        names|={p.relative_to(ROOT).as_posix()for p in(ROOT/folder).glob('*_oc.*')}
    sources={n:(STAGE/'source'/n if n in GAME else ROOT/n)for n in sorted(names)}
    hashes={n:sha(p)for n,p in sources.items()};packet.mkdir()
    with zipfile.ZipFile(packet/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n,p in sources.items():z.write(p,n)
    source=packet/'source'
    with zipfile.ZipFile(packet/'source.zip')as z:
        assert z.testzip()is None
        assert all((source/n).resolve().is_relative_to(source.resolve())for n in z.namelist());z.extractall(source)
    assert all(sha(source/n)==h for n,h in hashes.items())
    compiler=ROOT/'tools/Windows/cc65/bin/cl65.exe'
    z=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),
        '--compiler',str(compiler),'--output',str(packet/'roundtrip.nes')],cwd=source,capture_output=True,text=True)
    (packet/'rebuild.log').write_text(z.stdout+z.stderr);assert z.returncode==0 and sha(packet/'roundtrip.nes')==EXPECTED
    ordinary={}
    for mapper,digest in [('mmc3','97913a42a48b1d48c0dfde61fcc6f9eb406ec325f749dc439b96af85ba3108b4'),
                          ('mmc5','7982aed6838e7c56e15390c67b7ddc05bd3acaab7a59bd5e2d3a91eb5bf07128')]:
        target=packet/f'ordinary-{mapper}.nes'
        z=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),
            '--compiler',str(compiler),'--output',str(target),'--flag-off',mapper],cwd=source,capture_output=True,text=True)
        (packet/f'ordinary-{mapper}.log').write_text(z.stdout+z.stderr);assert z.returncode==0 and sha(target)==digest
        ordinary[mapper]=digest
    public={f'smb-crossover-{n}.nes':sha(ROOT/f'build/smb-crossover-{n}.nes')for n in ['mmc3','mmc5','mmc3-oversized','mmc5-expanded']}
    expected_public=json.loads((ROOT/'build/verification/tmnt-render-oa/proof.json').read_text())['unchanged_public_ROMs']
    assert public==expected_public
    assert all(sha(ROOT/n)==h for n,h in parent['source_files'].items()if n!='docs/qa/final-verification-plan-2026-10-23.md')
    proof=dict(status='STAGED_FUNCTIONAL_AUDIO_PERFORMANCE_GATE_FAILED_NOT_ADOPTED',accepted=False,goal_complete=False,
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),ROM_sha256=EXPECTED,live_ROM_sha256=parent['rom_sha256'],
        source_files=hashes,source_zip_sha256=sha(packet/'source.zip'),source_only_rebuild_exact=True,
        checks=checks,failed_performance_gate=record(STAGE/'performance-proof.json'),ordinary_mapper_hashes=ordinary,
        unchanged_public_ROMs=public,live_game_source_unchanged=True,
        scope='Reproducible external work packet. Audio/source/compatibility checks pass, but ordinary combat adds dropped draws; no accepted checkpoint, final campaign/item certification or goal-completion claim.')
    (packet/'manifest.json').write_text(json.dumps(proof,indent=2)+'\n')
    qa=ROOT/'build/verification/tmnt-audio-oc';qa.mkdir(parents=True,exist_ok=True)
    receipt=dict(work_packet=record(packet/'manifest.json'),source_zip=record(packet/'source.zip'),ROM_sha256=EXPECTED,
                 accepted=False,goal_complete=False,workspace_bytes=sum(n for _,n,_ in inventory(ROOT,skip_reparse=True)))
    assert receipt['workspace_bytes']<30_000_000_000
    assert not(qa/'staged-work.json').exists();(qa/'staged-work.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
