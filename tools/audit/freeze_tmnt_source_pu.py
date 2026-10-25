"""Pin the full source packet and rebuild all targets without adopting it."""
from pathlib import Path
import argparse,gzip,hashlib,json,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[2];PARENT=ROOT/'build/checkpoints/contact-pause-ps'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def game(n):return n.startswith(('src/','chr/','audio/'))or n.endswith('.cfg')
def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--expected-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 parent=json.loads((PARENT/'manifest.json').read_text());assert sha(PARENT/'candidate.nes')==parent['rom_sha256']=='646baef6cbcbe9ebc3c0a57c182592b3e777970c13b9c89eda6765f446915bb6'
 assert sha(PARENT/'source.zip')==parent['source_zip_sha256'];assert sha(a.candidate/'candidate.nes')==a.expected_sha256
 sources={p.relative_to(a.candidate/'source').as_posix():p for p in (a.candidate/'source').rglob('*')if p.is_file()};changes={}
 for n,f in sources.items():
  if game(n):
   prior=parent['source_files'].get(n)
   if sha(f)!=prior:
    assert (not(ROOT/n).exists())if prior is None else sha(ROOT/n)==prior,n
    changes[n]=dict(before=prior,after=sha(f))
 for n in parent['source_files']:
  if game(n):assert n in sources,'A parent source file disappeared'
 for pattern in ['*_pu.py','*_pv.py']:
  for f in (ROOT/'tools/audit').glob(pattern):sources[f.relative_to(ROOT).as_posix()]=f
 for f in (ROOT/'tests').glob('*-pv.lua'):sources[f.relative_to(ROOT).as_posix()]=f
 names=sorted(sources);hashes={n:sha(sources[n])for n in names};archive=a.output/'source.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for n in names:z.write(sources[n],n)
 stage=a.output/'source'
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None and set(z.namelist())==set(hashes);assert all((stage/n).resolve().is_relative_to(stage.resolve())for n in z.namelist());z.extractall(stage)
 previous=json.loads((ROOT/'build/verification/contact-pause-ps/proof.json').read_text());ordinary=previous['ordinary_flag_off_hashes'];builds={}
 for target in ['expanded','mmc3','mmc5']:
  args=[sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/(target+'.nes'))]
  if target!='expanded':args+=['--flag-off',target]
  z=subprocess.run(args,cwd=stage,capture_output=True,text=True);(a.output/(target+'.log')).write_text(z.stdout+z.stderr);assert z.returncode==0,(target,(z.stdout+z.stderr)[-2500:])
  builds[target]=sha(a.output/(target+'.nes'));assert builds[target]==(a.expected_sha256 if target=='expanded'else ordinary[target]),target
 assert all(sha(stage/n)==h for n,h in hashes.items());(a.output/'candidate.dbg.gz').write_bytes(gzip.compress((a.candidate/'candidate.dbg').read_bytes(),mtime=0))
 q=dict(passed=True,accepted=False,goal_complete=False,parent_ROM_sha256=parent['rom_sha256'],ROM_sha256=a.expected_sha256,source_files=hashes,changes=changes,
  source_zip_sha256=sha(archive),source_only_roundtrip_exact=True,builds=builds,debug_gzip_sha256=sha(a.output/'candidate.dbg.gz'),compiler_sha256=sha(ROOT/'tools/Windows/cc65/bin/cl65.exe'),driver_sha256=sha(Path(__file__)))
 (a.output/'packet.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,source_files=len(hashes),changes=list(changes),builds=builds)),flush=True)
if __name__=='__main__':main()
