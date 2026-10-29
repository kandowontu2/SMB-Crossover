"""Rebuild the two actual ordinary flags from the private sparse entrypoint."""
from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools')]
import rogue_dawn_map_v1 as ref
O=R/'build/rogue-dawn-host-body-v1'

def main():
 d=json.loads((O/'build.json').read_text());rows=[]
 for row in d['bindings']:assert ref.binding(row['path'])==row,row['path']
 for mapper,expected in [('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'),('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb')]:
  out=O/('flagoff-'+mapper+'.nes');cmd=list(d['commands'][0]);cmd[cmd.index('-C')+1]=str(R/'smb1base.cfg')
  for flag,suffix in[('-o','.nes'),('-m','.map'),('-Ln','.lbl')]:cmd[cmd.index(flag)+1]=str(out.with_suffix(suffix))
  cmd[cmd.index('--create-full-dep')+1]=str(out.with_suffix('.dep'))
  cmd=[v.replace('--dbgfile,'+str(O/'candidate.dbg'),'--dbgfile,'+str(out.with_suffix('.dbg')))for v in cmd]
  flags={'ENABLE_MMC5_EXPANDED=1':'ENABLE_MMC5_EXPANDED=0','MAPPER_MMC3=0':'MAPPER_MMC3='+str(int(mapper=='mmc3')),'MAPPER_MMC5=1':'MAPPER_MMC5='+str(int(mapper=='mmc5'))}
  cmd=[flags.get(v,v)for v in cmd]
  if not out.exists():
   z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);out.with_suffix('.log').write_text(z.stdout+z.stderr)
   assert z.returncode==0,(mapper,(z.stdout+z.stderr)[-3000:])
  assert ref.digest(out.read_bytes())==expected,(mapper,ref.digest(out.read_bytes()))
  rows.append(dict(mapper=mapper,passed=True,ROM=ref.binding(out),command=cmd,dependency_file=ref.binding(out.with_suffix('.dep'))))
 proof=dict(passed=True,native_run=False,rows=rows,bindings=[ref.binding(p)for p in[Path(__file__),O/'build.json',R/'smb1base.cfg']])
 (O/'ordinary-controls.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,ordinary=[r['ROM']['sha256']for r in rows])))
if __name__=='__main__':main()
