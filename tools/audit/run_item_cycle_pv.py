"""Read linked item fields and bind the same native item-control fixture."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys
from check_tmnt_render_oa import load,location,address
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--character',choices=['megaman','bass'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom);char=1 if a.character=='megaman'else 9
 def get(n,i):return b['raw'][location(b,n)+i]
 cfg=dict(character=char,slot=char,mush_lo=1|get('InvMushroomLo',char),mush_hi=get('InvMushroomHi',char),pool=get('InvAmmoIndex',char*16+2),cost=get('InvCosts',char*16+2));assert cfg['pool']!=255 and cfg['cost']>0
 fixture=ROOT/'tests/item-cycle-pv.lua';frozen=a.output/'fixture.lua';frozen.write_bytes(fixture.read_bytes());script=a.output/'run.lua';script.write_text('ITEM_CFG={'+','.join(k+'='+str(v)for k,v in cfg.items())+'}\ndofile('+json.dumps(frozen.as_posix())+')\n')
 z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),str(script),str(a.rom.resolve()),'--timeout','90','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],capture_output=True,text=True,cwd=ROOT);(a.output/'host.log').write_text(z.stdout+z.stderr)
 q=dict(passed=z.returncode==0,ROM_sha256=hashlib.sha256(b['raw']).hexdigest(),character=a.character,linked_fields=cfg,fixture_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),exit=z.returncode,scope='Actual cold Hard owner; starting powered state arranged, then two mature private actors physically collected, Select-only cycling and actual B firing. Emergence/all-items/campaign proof remains separate.')
 if(a.output/'result.json').exists():q['result']=json.loads((a.output/'result.json').read_text())
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q));return z.returncode
if __name__=='__main__':raise SystemExit(main())
