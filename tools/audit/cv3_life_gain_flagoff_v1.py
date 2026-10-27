"""Fresh ordinary builds; complete already-linked output after draft catalog fault."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];B=R/'build';P='cv3_life_gain_watch'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 original=json.loads((B/(P+'_build.json')).read_text());rows=[];resume='--resume-built'in sys.argv
 expected={'mmc3':'d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb','mmc5':'f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'}
 for mapper in['mmc3','mmc5']:
  out=B/(P+'_'+mapper+'_flagoff.nes');assert out.exists()==resume;cmd=[];i=0;old=original['command']
  while i<len(old):
   arg=old[i]
   if arg in['--asm-define','-D']:
    value=old[i+1];name=value.split('=',1)[0]
    if name=='ENABLE_MMC5_EXPANDED':i+=2;continue
    if name in['MAPPER_MMC3','MAPPER_MMC5']:value=name+'='+str(int(name=='MAPPER_'+mapper.upper()))
    cmd.extend([arg,value]);i+=2;continue
   if arg=='-C':cmd.extend([arg,str(R/'smb1base.cfg')]);i+=2;continue
   if arg=='--ld-args':cmd.extend([arg,'--dbgfile,'+str(out.with_suffix('.dbg'))]);i+=2;continue
   if arg in['-m','-Ln','-o']:cmd.extend([arg,str(out.with_suffix({'-m':'.map','-Ln':'.lbl','-o':'.nes'}[arg]))]);i+=2;continue
   cmd.append(arg);i+=1
  if not resume:
   run=subprocess.run(cmd,cwd=R,capture_output=True,text=True);out.with_suffix('.build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stdout+run.stderr
  assert sha(out)==expected[mapper]
  rows.append(dict(mapper=mapper,passed=True,whole_binary_exact=True,sha256=sha(out),command=cmd))
 paths=[Path(__file__),B/(P+'_build.json'),B/(P+'_entrypoint.s'),B/(P+'_cv3.s'),B/(P+'_core.s'),B/(P+'_helper.s'),B/'cv3_watch_single_owner_combat.s']
 report=B/(P+'_flagoff.json');assert not report.exists();report.write_text(json.dumps(dict(passed=True,source_only=True,native_run=False,rows=rows,retained_setup_negative='Initial reused report writer expected a nonexistent prefix_combat.s after both actual ordinary compiles and hash assertions succeeded. No ROM failure; these same linked files are bound, without a redundant rebuild.',bindings={str(p):sha(p)for p in paths}),indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(dict(passed=True,path=str(report),sha256=sha(report))))
if __name__=='__main__':main()
