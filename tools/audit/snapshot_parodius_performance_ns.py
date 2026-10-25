"""Preserve verified NS source and exact rebuild without inflating the workspace."""
from pathlib import Path
import datetime,gzip,hashlib,json,shutil,subprocess,sys,zipfile
from archive_workspace_hz import ARCHIVE,bounded,inventory
ROOT=Path(__file__).resolve().parents[2];QA=ROOT/'build/verification/parodius-performance-ns';FINAL=ROOT/'build/checkpoints/parodius-performance-ns'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not FINAL.exists(),'Never replace a saved checkpoint'
 proof=json.loads((QA/'proof.json').read_text());rom=QA/'candidate-v4.nes';assert proof['passed']and proof['rom_sha256']==sha(rom)
 parent=json.loads((ROOT/'build/checkpoints/parodius-death-nr/manifest.json').read_text());names=set(parent['source_files'])
 names.update(['src/parodius_fast_render.s','tools/audit/check_parodius_draw_rotation.py','tools/audit/check_parodius_performance.py','tools/audit/parodius_performance_observer.lua','tools/audit/diagnose_parodius_palette_ns.py','tools/audit/run_parodius_routes_ns.py','tools/audit/summarize_parodius_performance_ns.py','tools/audit/snapshot_parodius_performance_ns.py','tests/parodius-performance.lua','docs/qa/parodius-performance-2026-10-23.md'])
 hashes={n:sha(ROOT/n)for n in sorted(names)}
 relative=Path('build/verification/parodius-performance-ns/snapshot-v1');stage=bounded(ARCHIVE/relative,ARCHIVE);assert not stage.exists()and not stage.is_relative_to(ROOT.resolve());stage.mkdir(parents=True)
 with zipfile.ZipFile(stage/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for n in sorted(names):z.write(ROOT/n,n)
 source=stage/'source'
 with zipfile.ZipFile(stage/'source.zip')as z:
  assert all((source/i.filename).resolve().is_relative_to(source.resolve())for i in z.infolist());z.extractall(source)
 rebuilt=stage/'roundtrip.nes'
 result=subprocess.run([sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(rebuilt)],cwd=source,capture_output=True,text=True)
 (stage/'rebuild.log').write_text(result.stdout+result.stderr);assert result.returncode==0 and sha(rebuilt)==sha(rom),'Exact source-bundle rebuild'
 assert all(sha(ROOT/n)==h for n,h in hashes.items()),'Source changed during preservation'
 debug=rebuilt.with_suffix('.dbg');raw=debug.read_bytes();packed=debug.with_suffix('.dbg.gz');packed.write_bytes(gzip.compress(raw,mtime=0));assert gzip.decompress(packed.read_bytes())==raw;debug.unlink()
 for n,wanted in proof['unchanged_public_roms'].items():assert sha(ROOT/'build'/f'smb-crossover-{n}.nes')==wanted
 FINAL.mkdir();shutil.copy2(stage/'source.zip',FINAL/'source.zip')
 for suffix in ('.nes','.lbl','.map','.dbg.gz'):shutil.copy2(rom.with_suffix(suffix),FINAL/('candidate'+suffix))
 record=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='PRIVATE_PARODIUS_DRAW_OPTIMIZATION_WITH_OPEN_LAG_DROPOUT_AUDIO_MMC3_AND_FINAL_MATRIX',parent_checkpoint='parodius-death-nr',identities=37,rom_sha256=sha(rom),source_zip_sha256=sha(FINAL/'source.zip'),source_bundle_rebuild=dict(exact=True,rom_sha256=sha(rebuilt),staging_retained=str(stage)),source_files=hashes,evidence=dict(proof=proof,proof_sha256=sha(QA/'proof.json')),limitations=proof['limits'])
 (FINAL/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
 archive=json.loads((ROOT/'workspace-archive.json').read_text());assert Path(archive['archive']).resolve()==ARCHIVE.resolve()and all(x['relative']!=relative.as_posix()for x in archive['directories'])
 records={p.relative_to(stage).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))for p,n,t in inventory(stage)};item=dict(relative=relative.as_posix(),bytes=sum(x['bytes']for x in records.values()),files=len(records))
 assert all(sha(stage/p)==r['sha256']and(stage/p).stat().st_size==r['bytes']for p,r in records.items())
 report=dict(utc=record['utc'],archive=str(ARCHIVE),moves=[item],created_directly_in_verified_archive=True,archived_bytes=item['bytes'],all_files_sha256_verified=True,deleted_files=0)
 archive['directories'].append(item);archive['archived_bytes']+=item['bytes'];archive['archived_files']+=item['files'];archive.setdefault('additional_archives',[]).append(report)
 (ROOT/'workspace-archive.json').write_text(json.dumps(archive,indent=2)+'\n');(QA/'source-staging-archive.json').write_text(json.dumps(dict(report=report,files=records),indent=2)+'\n')
 (QA/'checkpoint.json').write_text(json.dumps(dict(checkpoint=str(FINAL),rom_sha256=sha(rom),source_zip_sha256=record['source_zip_sha256'],goal_complete=False),indent=2)+'\n')
 sys.path.insert(0,str(ROOT/'tools'));from playthroughs.roster_run import workspace_bytes
 assert workspace_bytes(ROOT)<30_000_000_000
 print(json.dumps(dict(checkpoint=str(FINAL),rom_sha256=sha(rom),source_zip_sha256=record['source_zip_sha256'],source_bundle_rebuild_exact=True)))
if __name__=='__main__':main()
