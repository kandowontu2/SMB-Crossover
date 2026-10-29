"""Fresh whole ordinary builds of the private floor source; no native."""
from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import rogue_dawn_map_v1 as ref
O=R/'build/rogue-dawn-floor-v2'

def main():
 assert not(O/'ordinary-controls.json').exists()
 d=json.loads((O/'build.json').read_text());rows=[]
 for z in d['bindings']:assert ref.binding(z['path'])==z,z['path']
 for mapper,expected in [('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'),('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb')]:
  out=O/('flagoff-'+mapper+'.nes');cmd=[z for z in d['executed_commands'][-1]if not z.endswith('.o')]
  cmd[cmd.index('-C')+1]=str(R/'smb1base.cfg')
  for flag,ext in [('-o','.nes'),('-m','.map'),('-Ln','.lbl')]:cmd[cmd.index(flag)+1]=str(out.with_suffix(ext))
  cmd[cmd.index('--create-full-dep')+1]=str(out.with_suffix('.dep'))
  cmd=[z.replace('--dbgfile,'+str(O/'candidate.dbg'),'--dbgfile,'+str(out.with_suffix('.dbg')))for z in cmd]
  flags={'ENABLE_MMC5_EXPANDED=1':'ENABLE_MMC5_EXPANDED=0','MAPPER_MMC3=0':'MAPPER_MMC3='+str(int(mapper=='mmc3')),'MAPPER_MMC5=1':'MAPPER_MMC5='+str(int(mapper=='mmc5'))}
  cmd=[flags.get(z,z)for z in cmd]
  z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);out.with_suffix('.log').write_text(z.stdout+z.stderr)
  assert z.returncode==0,(mapper,(z.stdout+z.stderr)[-4000:])
  assert ref.digest(out.read_bytes())==expected
  rows.append(dict(mapper=mapper,ROM=ref.binding(out),command=cmd,actual_ASM_deps=ref.binding(out.with_suffix('.dep'))))
 proof=dict(passed=True,native_run=False,rows=rows,bindings=[ref.binding(p)for p in[Path(__file__),O/'build.json',R/'smb1base.cfg']])
 (O/'ordinary-controls.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,ROMs=[z['ROM']['sha256']for z in rows])))
if __name__=='__main__':main()
