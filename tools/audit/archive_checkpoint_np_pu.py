"""One-shot reversible archive of superseded NP for the30GB cap."""
from pathlib import Path
import datetime,json,os
from archive_workspace_hz import ROOT,ARCHIVE,bounded,inventory,sha
def records(folder):
 return {p.relative_to(folder).as_posix():dict(bytes=n,mtime_ns=t,sha256=sha(p))for p,n,t in inventory(folder)}
def main():
 qa=ROOT/'build/verification/tmnt-music-pu';qa.mkdir(parents=True,exist_ok=True)
 assert not(qa/'archive-receipt.json').exists(),'Never repeat successful archive'
 receipt=json.loads((ROOT/'workspace-archive.json').read_text());assert Path(receipt['archive']).resolve()==ARCHIVE.resolve()
 assert not ARCHIVE.resolve().is_relative_to(ROOT.resolve())
 protected=[ROOT/('build/checkpoints/'+c+'/'+n)for c in ['contact-pause-ps','grant-grip-pm','smb3-shrink-pc']for n in ['candidate.nes','source.zip']]
 protected += [ROOT/('build/smb-crossover-'+n+'.nes')for n in ['mmc3','mmc5','mmc3-oversized','mmc5-expanded']]
 protected += [ROOT/'Player Guide/SMB-Crossover-Players-Guide-NU.pdf'];hashes={str(p):sha(p)for p in protected}
 rel='build/checkpoints/chr-publication-np';source=bounded(ROOT/rel,ROOT/'build/checkpoints');target=bounded(ARCHIVE/rel,ARCHIVE)
 assert source.is_dir()and not target.exists()and source.drive.lower()==target.drive.lower()
 assert not any(r['relative']==rel for r in receipt['directories'])
 files=records(source);assert len(files)==6;size=sum(r['bytes']for r in files.values())
 plan=dict(source=str(source),target=str(target),relative=rel,bytes=size,files=files,deleted_files=0,
  utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason='NP is superseded by adopted PS. Preserve all bytes externally and preserve current/parent checkpoints, public ROMs and guide locally.')
 (qa/'archive-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 target.parent.mkdir(parents=True,exist_ok=True);os.rename(source,target)
 assert records(target)==files and all(sha(Path(p))==h for p,h in hashes.items())
 move=dict(relative=rel,bytes=size,files=len(files));receipt['directories'].append(move);receipt['archived_bytes']+=size;receipt['archived_files']+=len(files)
 receipt.setdefault('additional_archives',[]).append(dict(utc=plan['utc'],archive=str(ARCHIVE),moves=[move],archived_bytes=size,all_files_sha256_verified=True,deleted_files=0))
 (ROOT/'workspace-archive.json').write_text(json.dumps(receipt,indent=2)+'\n');plan.update(all_files_sha256_verified=True,protected_files=hashes)
 (qa/'archive-receipt.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps(dict(archived_bytes=size,files=len(files),deleted_files=0,all_files_sha256_verified=True)))
if __name__=='__main__':main()
