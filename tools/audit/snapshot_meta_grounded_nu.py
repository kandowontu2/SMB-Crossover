"""Freeze the tested NU repair and rebuild its source bundle byte-for-byte."""
from pathlib import Path
import datetime
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile
from archive_workspace_hz import ARCHIVE,bounded,inventory,sha

ROOT=Path(__file__).resolve().parents[2]
QA=ROOT/'build/verification/meta-knight-source-nu'
FINAL=ROOT/'build/checkpoints/meta-knight-grounded-nu'


def main():
    assert not FINAL.exists(),'Never overwrite a frozen checkpoint'
    proof=json.loads((QA/'proof.json').read_text());rom=Path(proof['rom'])
    assert proof['passed']and not proof['goal_complete']and sha(rom)==proof['rom_sha256']
    parent=json.loads((ROOT/'build/checkpoints/little-mac-star-nt/manifest.json').read_text())
    names=set(parent['source_files'])|set(proof['source_changes'])|{
        'tools/reference/observe_meta_knight_original.lua','reference/meta-knight/art-manifest.json',
        'reference/meta-knight/native-animation-contact.png','tests/meta-knight-nes-moves.lua',
        'tests/meta-knight-food-blocks.lua','tests/meta-rotor-differential.lua',
        'tools/audit/check_meta_art_nu.py','tools/audit/check_meta_moves_nu.py',
        'tools/audit/check_meta_rotor_nu.py','tools/audit/summarize_meta_nu.py',
        'tools/audit/snapshot_meta_grounded_nu.py','tools/audit/archive_nt_evidence_nu.py',
        'tools/audit/archive_meta_drafts_nu.py','tools/playthroughs/meta_grounded_policy_nu.lua',
        'docs/qa/meta-knight-source-2026-10-24.md','docs/qa/firebar-empty-mounts-2026-10-24.md',
        'docs/qa/final-verification-plan-2026-10-23.md',
        'tools/audit/meta_native_observer_nu.lua','tools/audit/prepare_meta_native_nu.py',
        'tools/audit/check_meta_native_nu.py','tools/audit/meta_native_nu.md'}
    hashes={n:sha(ROOT/n)for n in sorted(names)}
    rel=Path('build/verification/meta-knight-source-nu/snapshot-v1')
    stage=bounded(ARCHIVE/rel,ARCHIVE);assert not stage.exists()and not stage.is_relative_to(ROOT.resolve())
    stage.mkdir(parents=True)
    with zipfile.ZipFile(stage/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for n in sorted(names):z.write(ROOT/n,n)
    source=stage/'source'
    with zipfile.ZipFile(stage/'source.zip')as z:
        assert all((source/i.filename).resolve().is_relative_to(source.resolve())for i in z.infolist());z.extractall(source)
    target=stage/'roundtrip.nes'
    result=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),
                           '--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(target)],
                          cwd=source,capture_output=True,text=True)
    (stage/'rebuild.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0 and sha(target)==sha(rom),'Exact frozen source-only rebuild'
    raw=target.with_suffix('.dbg').read_bytes();packed=target.with_suffix('.dbg.gz')
    packed.write_bytes(gzip.compress(raw,mtime=0));assert gzip.decompress(packed.read_bytes())==raw
    target.with_suffix('.dbg').unlink()
    assert all(sha(ROOT/n)==h for n,h in hashes.items()),'Source changed while preserving'
    for name,h in proof['unchanged_public_roms'].items():assert sha(ROOT/'build'/f'smb-crossover-{name}.nes')==h
    FINAL.mkdir();shutil.copy2(stage/'source.zip',FINAL/'source.zip')
    for suffix in('.nes','.lbl','.map','.dbg.gz'):shutil.copy2(rom.with_suffix(suffix),FINAL/('candidate'+suffix))
    record=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                status='PRIVATE_GROUNDED_META_REPAIR_WITH_OPEN_AUDIO_HUE_MMC3_AND_FULL_ROSTER_MATRIX',
                parent_checkpoint='little-mac-star-nt',identities=37,rom_sha256=sha(rom),
                source_zip_sha256=sha(FINAL/'source.zip'),source_bundle_rebuild=dict(exact=True,staging_retained=str(stage)),
                source_files=hashes,evidence=dict(proof_sha256=sha(QA/'proof.json'),proof=proof),
                limitations=proof['limitations'],goal_complete=False)
    (FINAL/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
    receipt=json.loads((ROOT/'workspace-archive.json').read_text())
    assert Path(receipt['archive']).resolve()==ARCHIVE.resolve()
    assert all(i['relative']!=rel.as_posix()for i in receipt['directories'])
    files={p.relative_to(stage).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))for p,n,t in inventory(stage)}
    item=dict(relative=rel.as_posix(),bytes=sum(v['bytes']for v in files.values()),files=len(files))
    assert all(sha(stage/n)==v['sha256']for n,v in files.items())
    report=dict(utc=record['utc'],archive=str(ARCHIVE),moves=[item],created_directly_in_verified_archive=True,
                archived_bytes=item['bytes'],all_files_sha256_verified=True,deleted_files=0)
    receipt['directories'].append(item);receipt['archived_bytes']+=item['bytes'];receipt['archived_files']+=item['files']
    receipt.setdefault('additional_archives',[]).append(report)
    (ROOT/'workspace-archive.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (QA/'source-staging-archive.json').write_text(json.dumps(dict(report=report,files=files),indent=2)+'\n')
    (QA/'checkpoint.json').write_text(json.dumps(dict(checkpoint=str(FINAL),rom_sha256=sha(rom),source_zip_sha256=record['source_zip_sha256'],goal_complete=False),indent=2)+'\n')
    print(json.dumps({k:record[k]for k in('status','rom_sha256','source_zip_sha256')}))


if __name__=='__main__':main()
