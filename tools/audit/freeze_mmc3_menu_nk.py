"""Publish the verified MMC3 menu repair; rebuild both prepared ROMs exactly."""
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
QA=ROOT/'build/verification/mmc3-menu-nj'
FINAL=ROOT/'build/checkpoints/mmc3-menu-nk'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())


def main():
    assert not FINAL.exists(),'Preserve completed checkpoints'
    parent=read(ROOT/'build/checkpoints/meta-knight-nh/manifest.json')
    m5=ROOT/'build/smb-crossover-mmc5-expanded.nes'
    m3=ROOT/'build/oversized-mmc3-nf/smb-crossover-mmc3-oversized.nes'
    assert sha(m5)==parent['ROMs']['mmc5-expanded']
    digest=sha(m3)
    evidence={}
    for setting in ('off','on'):
        pixels=read(QA/f'rapid-sprite-{setting}/pixel-proof.json')
        trace=QA/f'rapid-sprite-{setting}/build/verification/browsing.bin'
        proof=read(trace.parent/'proof.json')
        assert pixels['ROM_sha256']==digest and pixels['passed'] and not pixels['bad_frames']
        assert len(pixels['stable_identity_pixels'])==33 and pixels['transition_frames']==2604
        assert pixels['rendered_screenshots_exact']==33
        assert pixels['trace_sha256']==sha(trace)
        assert proof['blank_frames_while_browsing']==0 and proof['rapid_switch_frames']==600
        assert proof['DMA_frames_checked']==2604
        evidence[setting]=dict(pixel_proof=pixels,timing=proof)
    entries=dict(ROM_sha256=digest,results={})
    for group in range(1,4):
        subset=read(QA/f'entry-sprite-{group}/results.json')
        assert subset['ROM_sha256']==digest and len(subset['results'])==11
        assert not set(entries['results'])&set(subset['results'])
        entries['results'].update(subset['results'])
    assert len(entries['results'])==33
    assert all(row['exit']==0 for row in entries['results'].values())
    evidence['cold_entries']=entries
    names=set(parent['source_files'])
    for folder in ('src','chr','audio','inc','ports/mmc3-oversized'):
        names.update(p.relative_to(ROOT).as_posix()for p in (ROOT/folder).rglob('*')
                     if p.is_file()and p.suffix not in ('.o','.pyc'))
    names.update(['tools/reference/pack_mmc3_menu.py','tools/audit/capture_roster_menu.py',
                  'tools/audit/check_mmc3_menu_pixels.py','tools/audit/freeze_mmc3_menu_nk.py',
                  'docs/qa/mmc3-menu-2026-10-23.md'])
    assert all((ROOT/n).is_file()for n in names)
    hashes={name:sha(ROOT/name)for name in sorted(names)}
    sys.path.insert(0,str(ROOT/'tools'))
    from playthroughs.roster_run import workspace_bytes
    assert workspace_bytes(ROOT)+3*sum((ROOT/n).stat().st_size for n in names)<30_000_000_000
    stage=QA/'freeze-staging-sprite';assert not stage.exists();stage.mkdir()
    with zipfile.ZipFile(stage/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as archive:
        for name in sorted(names):archive.write(ROOT/name,name)
    assert all(sha(ROOT/name)==value for name,value in hashes.items())
    source=stage/'source'
    with zipfile.ZipFile(stage/'source.zip')as archive:archive.extractall(source)
    compiler=ROOT/'tools/Windows/cc65/bin/cl65.exe'
    reference=stage/'mmc5-roundtrip.nes'
    roundtrips={}
    for mapper,command,output in [
        ('mmc5-expanded',[sys.executable,str(source/'tools/build_mmc5_expanded.py'),
                          '--workspace',str(source),'--compiler',str(compiler),'--output',str(reference)],reference),
        ('mmc3-oversized',[sys.executable,str(source/'tools/build_mmc3_oversized.py'),
                          '--compiler',str(compiler),'--reference-rom',str(reference)],
                         source/'build/oversized-mmc3-nf/smb-crossover-mmc3-oversized.nes')]:
        process=subprocess.run(command,cwd=source,capture_output=True,text=True)
        (stage/(mapper+'.log')).write_text(process.stdout+process.stderr)
        assert process.returncode==0,mapper+' source-bundle rebuild failed'
        expected=sha(m5)if mapper=='mmc5-expanded'else digest
        assert sha(output)==expected,(mapper,'rebuilt ROM differs')
        roundtrips[mapper]=dict(exact=True,ROM_sha256=expected)
    assert sha(m3)==digest and sha(m5)==parent['ROMs']['mmc5-expanded']
    FINAL.mkdir()
    shutil.copy2(stage/'source.zip',FINAL/'source.zip')
    for mapper,rom in [('mmc3-oversized',m3),('mmc5-expanded',m5)]:
        base='smb-crossover-'+mapper
        for suffix in ('.nes','.lbl','.map','.dbg'):
            original=rom.with_suffix(suffix)
            if suffix=='.dbg':
                (FINAL/(base+'.dbg.gz')).write_bytes(gzip.compress(original.read_bytes(),mtime=0))
            else:shutil.copy2(original,FINAL/(base+suffix))
            if mapper=='mmc3-oversized':shutil.copy2(original,ROOT/'build'/(base+suffix))
    report=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                status='MMC3_MENU_REPAIR_VERIFIED',parent_checkpoint='meta-knight-nh',identities=33,
                ROMs={'mmc3-oversized':digest,'mmc5-expanded':sha(m5)},
                source_zip_sha256=sha(FINAL/'source.zip'),source_files=hashes,
                source_bundle_rebuilds=roundtrips,evidence=evidence,
                limitations=['Menu atlas loads during the ordinary initial selection-screen transition.',
                             'MMC5 is unchanged; standard builds are unchanged.',
                             'Full campaigns, remaining roster/music work and physical oversized MMC3 boards remain unverified.'])
    (FINAL/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    (QA/'published.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(FINAL),ROMs=report['ROMs'],source_zip_sha256=report['source_zip_sha256'])))


if __name__=='__main__':main()
