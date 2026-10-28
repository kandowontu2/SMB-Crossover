"""Finite actual menu/lives portrait admission counterexample on frozen83db."""
from pathlib import Path
import argparse,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from celeste_host_controls_v4 import *
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists();b=scoped_load(a.rom);rows=[]
 for variant,mode in itertools.product([0,4],[0,1]):
  q=seed(b,0);q.put(CrossoverMenuIndex=0,MarioVariant=variant,OperMode=mode,CurrentOAMOffset=0)
  run(q,'MenuResolveCharacter')
  if mode==0:c,_,_=run(q,'DrawSelectionPreview')
  else:
   run(q,'DrawPlayer_Intermediate');c,_,_=run(q,'X5PortraitRender',x=q.get('ObjectMetasprite'),y=0)
  rows.append(dict(variant=variant,mode=mode,actual_native_caller='DrawSelectionPreview'if mode==0 else'DrawPlayer_Intermediate->X5PortraitRender',ObjectMetasprite=q.get('ObjectMetasprite'),CurrentOAMOffset=q.get('CurrentOAMOffset'),Cbank=q.m.banks[2],first16OAM=list(q.m[0x200:0x210])))
 assert all(r['CurrentOAMOffset']>0 for r in rows if r['variant']==0)
 assert all(r['ObjectMetasprite']==address(b,'METASPRITE_SMALL_MARIO_STANDING')and r['CurrentOAMOffset']==8 and r['Cbank']==98 for r in rows if r['variant']==4)
 proof=dict(passed=False,counterexample_confirmed=True,source_CPU_only=True,native_run=False,reason='Cold native raw0 portrait producer bypasses PlayerGfxHandler; it emits the two-part small Mario record29, not the four-part native Celeste standing record. Initial diagnostic incorrectly expected zero OAM; that assertion failed before writing evidence, and actual8B result is retained here.',rows=rows,bindings={str(f):sha(f)for f in[Path(__file__),a.rom,a.rom.with_suffix('.dbg'),R/'src/screen_render.s',R/'src/x5_menu_ui.s']})
 a.output.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps({'counterexample_confirmed':True,'sha256':sha(a.output),'rows':rows}))
if __name__=='__main__':main()
