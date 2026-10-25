"""Publish the Meta Knight increment with explicit, hash-bound evidence.

This checkpoint does not re-certify ND's other full routes or mark the
remaining requested character implementations complete.
"""
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
QA=ROOT/'build/verification/meta-knight-nh'
FINAL=ROOT/'build/checkpoints/meta-knight-nh'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
read=lambda path:json.loads(path.read_text())


def main():
    assert not FINAL.exists(), 'Preserve completed checkpoints'
    roms={'mmc5-expanded':QA/'smb-crossover-mmc5-expanded-nh.nes',
          'mmc3-oversized':ROOT/'build/oversized-mmc3-nf/smb-crossover-mmc3-oversized.nes'}
    evidence={}
    for mapper,short in [('mmc5-expanded','m5'),('mmc3-oversized','m3')]:
        digest=sha(roms[mapper])
        entry=read(QA/f'all-entry-{short}-release/results.json')
        assert entry.get('rom_sha256',entry.get('ROM_sha256'))==digest
        assert len(entry['results'])==33 and all(row['exit']==0 for row in entry['results'].values())
        replay=read(QA/f'verified-{short}/manifest.json')
        assert replay['ROM_sha256']==digest and replay['fixed_replay'] and replay['controller_only']
        assert not replay['memory_writes'] and replay['exit']==0
        assert replay['result']['cleared'] and replay['result']['deaths']==0
        assert replay['inputs_sha256']==sha(QA/f'verified-{short}/inputs.csv')
        component=next((QA/f'components-{short}-release').glob('*.log'))
        assert 'PASS Meta Knight:' in component.read_text() and '\nFAIL' not in component.read_text()
        evidence[mapper]=dict(ROM_sha256=digest,entry=entry,replay=replay,
                              component_log_sha256=sha(component))
    parent=read(ROOT/'build/checkpoints/full-roster-nd/manifest.json')
    names=set(parent['source_files'])
    for folder in ('src','chr','audio','inc','ports/mmc3-oversized'):
        names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*')
                     if p.is_file() and p.suffix not in ('.o','.pyc'))
    names.update(['README.md','smb1base-mmc5-expanded.cfg','build_options.ini',
                  'tools/build_mmc3_oversized.py','tools/prepare_mmc3_oversized.py',
                  'tools/prepare_smb3_hud.py','tools/audit/check_mmc3_oversized.py',
                  'tools/audit/check_full_roster_entry.py','tools/audit/freeze_meta_knight_nh.py',
                  'tools/reference/prepare_meta_knight.py','tools/reference/build_new_roster_audio.py',
                  'tools/reference/build_playlist_audio.py','tools/reference/capture_new_roster_music.py',
                  'tools/playthroughs/new_roster_run_nd.py','tools/playthroughs/new_roster_policy_nd.lua',
                  'tests/meta-knight.lua','docs/qa/meta-knight-2026-10-23.md'])
    assert all((ROOT/name).is_file() for name in names),[name for name in names if not(ROOT/name).is_file()]
    assert all(not Path(name).is_absolute() and '..' not in Path(name).parts for name in names)
    hashes={name:sha(ROOT/name) for name in sorted(names)}
    from sys import path
    path.insert(0,str(ROOT/'tools'))
    from playthroughs.roster_run import workspace_bytes
    used=workspace_bytes(ROOT)
    reserve=2*sum(p.stat().st_size for p in roms.values())+sum((ROOT/n).stat().st_size for n in names)
    assert used+reserve<30_000_000_000
    stage=QA/'freeze-staging'
    assert not stage.exists(), 'Preserve earlier freeze diagnostics'
    stage.mkdir()
    with zipfile.ZipFile(stage/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name in sorted(names):archive.write(ROOT/name,name)
    assert all(sha(ROOT/name)==digest for name,digest in hashes.items())
    unpacked=stage/'source'
    with zipfile.ZipFile(stage/'source.zip') as archive:archive.extractall(unpacked)
    compiler=ROOT/'tools/Windows/cc65/bin/cl65.exe'
    reference=stage/'roundtrip-mmc5.nes'
    commands=[
        [sys.executable,str(unpacked/'tools/build_mmc5_expanded.py'),'--workspace',str(unpacked),
         '--compiler',str(compiler),'--output',str(reference)],
        [sys.executable,str(unpacked/'tools/build_mmc3_oversized.py'),
         '--compiler',str(compiler),'--reference-rom',str(reference)]]
    roundtrips={}
    for mapper,command in zip(('mmc5-expanded','mmc3-oversized'),commands):
        process=subprocess.run(command,cwd=unpacked,capture_output=True,text=True)
        (stage/(mapper+'.log')).write_text(process.stdout+process.stderr)
        assert process.returncode==0, ('Source-bundle rebuild failed',mapper)
        built=reference if mapper=='mmc5-expanded' else unpacked/'build/oversized-mmc3-nf/smb-crossover-mmc3-oversized.nes'
        assert sha(built)==sha(roms[mapper]), ('Source-bundle ROM differs',mapper)
        roundtrips[mapper]=dict(exact=True,ROM_sha256=sha(built))
    FINAL.mkdir(parents=True)
    shutil.copy2(stage/'source.zip',FINAL/'source.zip')
    for mapper,rom in roms.items():
        base='smb-crossover-'+mapper
        for suffix in ('.nes','.lbl','.map','.dbg'):
            source=rom.with_suffix(suffix)
            shutil.copy2(source,ROOT/'build'/(base+suffix))
            target=FINAL/(base+suffix)
            if suffix=='.dbg':
                target=target.with_suffix('.dbg.gz');target.write_bytes(gzip.compress(source.read_bytes(),mtime=0))
            else:shutil.copy2(source,target)
    report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                status='META_KNIGHT_INCREMENT_VERIFIED',identities=33,
                parent_checkpoint='full-roster-nd',ROMs={m:sha(p) for m,p in roms.items()},
                source_zip_sha256=sha(FINAL/'source.zip'),source_files=hashes,evidence=evidence,
                source_bundle_rebuilds=roundtrips,
                limitations=['Other requested alternates and broader character/music repairs remain in progress.',
                             'Meta Knight surface1-1 Easy proof is not full-campaign or Hard-route certification.',
                             'DPCM percussion omitted; no exact source-music loop boundary proven.',
                             'Oversized MMC3 physical cartridge compatibility is unverified.'])
    (FINAL/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    (QA/'published.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(FINAL),ROMs=report['ROMs'],source_zip_sha256=report['source_zip_sha256'])))


if __name__=='__main__':main()
