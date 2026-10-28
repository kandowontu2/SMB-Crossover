"""Two private ordinary-target rebuilds of the real sparse transaction source."""
from pathlib import Path
import json,subprocess,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
O=R/'build/rogue-dawn-host-transactions-v3'
def main():
 d=json.loads((O/'build.json').read_text())
 for row in d['bindings']:assert ref.binding(row['path'])==row,row['path']
 rows=[]
 for mapper,expected in [('mmc5','f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'),('mmc3','d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb')]:
  out=O/('flagoff-'+mapper+'.nes')
  cmd=list(d['commands'][0]);cmd[cmd.index('-C')+1]=str(R/'smb1base.cfg')
  for flag,suffix in [('-o','.nes'),('-m','.map'),('-Ln','.lbl')]:cmd[cmd.index(flag)+1]=str(out.with_suffix(suffix))
  cmd=[v.replace('--dbgfile,'+str(O/'candidate.dbg'),'--dbgfile,'+str(out.with_suffix('.dbg')))for v in cmd]
  repl={'ENABLE_MMC5_EXPANDED=1':'ENABLE_MMC5_EXPANDED=0','MAPPER_MMC3=0':'MAPPER_MMC3='+str(int(mapper=='mmc3')),'MAPPER_MMC5=1':'MAPPER_MMC5='+str(int(mapper=='mmc5'))}
  cmd=[repl.get(v,v)for v in cmd]
  if not out.exists():
   z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);out.with_suffix('.log').write_text(z.stdout+z.stderr)
   assert z.returncode==0,(mapper,(z.stdout+z.stderr)[-2000:])
  # The expanded-only CV3 DMC mirror postprocessor is intentionally inapplicable
  # to ordinary786448B images. Their genuine assembler bytes are the baseline.
  actual=ref.digest(out.read_bytes());assert actual==expected,(mapper,actual,expected)
  rows.append(dict(mapper=mapper,passed=True,sha256=actual,command=cmd,ROM=ref.binding(out)))
 proof=dict(passed=True,native_run=False,source_only=True,ordinary_wholeROM_byteequivalent=True,rows=rows,bindings=[ref.binding(p)for p in[Path(__file__),O/'build.json',R/'smb1base.cfg']])
 (O/'ordinary-controls.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,rows=[dict(mapper=r['mapper'],sha256=r['sha256'])for r in rows])))
if __name__=='__main__':main()
