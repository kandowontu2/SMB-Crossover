"""Freeze a bounded private Parodius integration proof, without publishing it."""
from pathlib import Path
import datetime
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'build/verification/parodius-integration-nl'
FINAL=ROOT/'build/checkpoints/parodius-integration-nl'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())


def main():
    assert not FINAL.exists(),'Preserve completed checkpoints'
    parent=read(ROOT/'build/checkpoints/mmc3-menu-nk/manifest.json')
    rom=QA/'smb-crossover-mmc5-parodius-v8.nes';digest=sha(rom)
    components=read(QA/'components-boundary-v8/results.json')
    assert components['ROM_sha256']==digest
    assert set(components['results'])=={'1','2','3'}
    assert all(row['exit']==0 for row in components['results'].values())
    evidence=dict(components=components,component_details={},routes={},cold_entries=read(QA/'entry-v8/results.json'))
    for variant in (1,2,3):
        folder=QA/'components-boundary-v8'/str(variant)
        script=folder/'components.lua'
        assert script.read_text()==f'PN_VARIANT={variant}\n'+(ROOT/'tests/parodius-integration.lua').read_text()
        proof=read(folder/'build/verification/proof.json')
        assert proof['passed'] and proof['missingPoses']==0 and proof['rendererBudgetChecks']>100 and proof['viewportChecks']>100
        evidence['component_details'][str(variant)]=dict(proof=proof,script_sha256=sha(script))
    assert evidence['cold_entries']['rom_sha256']==digest
    assert len(evidence['cold_entries']['results'])==3
    assert all(row['exit']==0 for row in evidence['cold_entries']['results'].values())
    for name in ('octopus','twinbee','pentarou'):
        route=read(QA/f'replay-{name}-v8/manifest.json')
        assert route['ROM_sha256']==digest and route['fixed_replay'] and route['exit']==0
        assert route['result']['cleared'] and route['result']['deaths']==0 and route['result']['failure']is None
        assert route['inputs_sha256']==sha(QA/f'replay-{name}-v8/inputs.csv')
        evidence['routes'][name]=route
    names=set(parent['source_files'])
    for folder in ('src','chr','audio','inc','ports/mmc3-oversized','reference/parodius-nes'):
        names.update(p.relative_to(ROOT).as_posix()for p in (ROOT/folder).rglob('*')
                     if p.is_file()and p.suffix not in ('.o','.pyc','.pdf'))
    names.update(p.relative_to(ROOT).as_posix()for p in (ROOT/'tools').rglob('*parodius*.py'))
    names.update(['tests/parodius-integration.lua','tools/audit/check_full_roster_entry.py',
                  'tools/playthroughs/new_roster_run_nd.py','tools/playthroughs/new_roster_policy_nd.lua',
                  'docs/qa/parodius-integration-2026-10-23.md',
                  'docs/qa/final-verification-plan-2026-10-23.md'])
    hashes={name:sha(ROOT/name)for name in sorted(names)}
    stage=QA/'snapshot-v8';assert not stage.exists();stage.mkdir()
    with zipfile.ZipFile(stage/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as archive:
        for name in sorted(names):archive.write(ROOT/name,name)
    source=stage/'source'
    with zipfile.ZipFile(stage/'source.zip')as archive:archive.extractall(source)
    output=stage/'roundtrip.nes'
    result=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),
                           '--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),
                           '--output',str(output)],cwd=source,capture_output=True,text=True)
    (stage/'roundtrip.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0 and sha(output)==digest,'Private source-bundle rebuild differs'
    assert all(sha(ROOT/name)==value for name,value in hashes.items()),'Sources changed during snapshot'
    for mapper,value in parent['ROMs'].items():
        assert sha(ROOT/'build'/('smb-crossover-'+mapper+'.nes'))==value,'Published ROM was modified'
    FINAL.mkdir();shutil.copy2(stage/'source.zip',FINAL/'source.zip')
    for suffix in ('.nes','.lbl','.map','.dbg'):
        original=rom.with_suffix(suffix)
        if suffix=='.dbg':(FINAL/'candidate.dbg.gz').write_bytes(gzip.compress(original.read_bytes(),mtime=0))
        else:shutil.copy2(original,FINAL/('candidate'+suffix))
    report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                status='PRIVATE_PARODIUS_COMPONENT_AND_EASY_1_1_PROOF_NOT_RELEASED',
                identities=36,ROM_sha256=digest,source_zip_sha256=sha(FINAL/'source.zip'),
                source_files=hashes,source_bundle_rebuild_exact=True,evidence=evidence,
                limitations=['Bell pickup/drop rules, source audio, shield contact fidelity and MMC3 integration remain unfinished.',
                             'No full-roster/all-powerup final QA claim. See the final verification plan.',
                             'Component arenas seed world/equipment state explicitly; campaign replays do not.',
                             'Palette quantization is declared; dynamic native palette overrides remain open.',
                             'Published MMC3 and MMC5 ROMs are unchanged.'])
    (FINAL/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(FINAL),ROM_sha256=digest,source_bundle_rebuild_exact=True,published=False)))


if __name__=='__main__':main()
