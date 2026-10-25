"""Cold-menu native Mac and TMNT actor lifecycle fixtures; exact-hash packets."""
from pathlib import Path
from collections import deque
import argparse,hashlib,json,re,subprocess,sys
import numpy as np
from PIL import Image,ImageDraw
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load as load
from observe_chip_committed_write import lua
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['rom','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--emulator',required=True);p.add_argument('--character',type=int,choices=[15,19],required=True)
 p.add_argument('--diagnostic',action='store_true');p.add_argument('--focus',default='')
 a=p.parse_args();a.output.mkdir(exist_ok=False);b=load(a.rom)
 fixture=ROOT/'tools/audit/mac_tmnt_native_fixture.lua'
 names=['PauseSkip','NonMaskableInterrupt','PowerUpObjHandler','HandlePowerUpCollision','TnPreparePickupDispatch','TnRisePickupDispatch','TnCollectEquipment','UnionPwrUpCore','LmEnsure','LmDeathStartGate','PlayerLoseLife','GiveOneCoin','FloateyNumbersCore','X5InventoryInit','X5ProfilesNewGame','LmResetGate','KillPlayer']
 hooks={n:dict(address=address(b,n),physical_bank=(location(b,n)-16)//8192,bytes=list(b['raw'][location(b,n):location(b,n)+3]))for n in names}
 n='NonMaskableInterrupt';d=int(b['syms'][n]['size'],0)-1
 hooks['NmiReturn']=dict(address=address(b,n)+d,physical_bank=(location(b,n)+d-16)//8192,bytes=[b['raw'][location(b,n)+d]])
 used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",fixture.read_text()))
 cases=([dict(name=f'{kind}-life{life}',kind=kind,life=life)for kind in ['coin','score','oneup']for life in [2,127,255]]+[dict(name='staged-area-marker-control',kind='area',life=2),dict(name='coin-gain-then-actual-death',kind='death',life=2),dict(name='last-life-game-over',kind='gameover',life=0),dict(name='real-game-over-to-new-game',kind='newgame',life=2)] if a.character==15 else [dict(name='real-question-block-reveal',kind='real',variant=0,slot=5,scroll=80,relative=120)]+[dict(name=f'turtle{v}-slot{s}-scroll{c}',kind='collect',variant=v,slot=s,scroll=c,relative=120)for v in range(4)for s in [0,5]for c in [0,80,240]]+[dict(name=f'turtle{v}-ghost-scroll{c}',kind='miss',variant=v,slot=5,scroll=c,relative=120)for v in range(4)for c in [80,240]]+[dict(name=f'edge{r}-scroll{c}',kind='edge',variant=1,slot=5,scroll=c,relative=r)for r in [-4,248]for c in [80,240]])
 if a.focus:cases=[q for q in cases if a.focus in q['name']]
 cfg=dict(character=a.character,cases=cases,diagnostic=int(a.diagnostic),hooks=hooks,ram={n:address(b,n)for n in used if n in b['syms']},power_id=address(b,'PowerUpObject'),smc_fields=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],stack_guard=int(next(g for g in b['segs'].values()if g.get('name')=='"SMCCODE"')['start'],0)+int(next(g for g in b['segs'].values()if g.get('name')=='"SMCCODE"')['size'],0))
 count=address(b,'X5MenuPresent')-address(b,'X5MenuCharacters')
 tab=lambda n:list(b['raw'][location(b,n):location(b,n)+count])
 target=tab('X5MenuCharacters').index(a.character);maps={n.lower():tab('X5Menu'+n)for n in ['Up','Down','Left','Right']}
 cfg['menu_target']=target;cfg['menu_moves']=[]
 for start in range(count):
  todo=deque([(start,[])]);seen={start}
  while todo:
   node,path=todo.popleft()
   if node==target:cfg['menu_moves'].append(path[0]if path else '');break
   for direction,links in maps.items():
    nxt=links[node]
    if nxt not in seen:seen.add(nxt);todo.append((nxt,path+[direction]))
  else:raise AssertionError('Menu unreachable')
 script=a.output/'run.lua';script.write_text('MAC_TMNT_NATIVE_CONFIG='+lua(cfg)+'\n'+fixture.read_text())
 with(a.output/'host.log').open('w')as f:
  result=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),'--emulator',a.emulator,str(script),str(a.rom),'--timeout','200','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],stdout=f,stderr=subprocess.STDOUT)
 proof=json.loads((a.output/'proof.json').read_text())if(a.output/'proof.json').exists()else dict(passed=False)
 pixels=[];paths=[]
 for raw in sorted(a.output.glob('*.argb')):
  v=np.frombuffer(raw.read_bytes(),dtype='<u4').reshape(240,256);rgb=np.stack(((v>>16)&255,(v>>8)&255,v&255),axis=2).astype(np.uint8)
  Image.fromarray(rgb).save(raw.with_suffix('.png'));pixels.append(dict(file=raw.name,sha256=sha(raw)));paths.append(raw.with_suffix('.png'))
 if paths:
  sheet=Image.new('RGB',(1024,((len(paths)+3)//4)*260),(24,28,36));draw=ImageDraw.Draw(sheet)
  for i,path in enumerate(paths):
   with Image.open(path)as im:sheet.paste(im,(i%4*256,i//4*260+20))
   draw.text((i%4*256+2,i//4*260+2),path.stem,fill='white')
  sheet.save(a.output/'overview.png')
 proof.update(passed=result.returncode==0 and proof.get('passed',False),emulator_exit=result.returncode,ROM_sha256=sha(a.rom),ROM_path=str(a.rom.resolve()),fixture_sha256=sha(fixture),runner_sha256=sha(Path(__file__)),script_sha256=sha(script),emulator_sha256=sha(Path(a.emulator)),physical_frames=pixels,goal_complete=False)
 (a.output/'native-proof.json').write_text(json.dumps(proof,indent=2))
 print(json.dumps(dict(passed=proof['passed'],cases=len(proof.get('cases',[])),violations=len(proof.get('violations',[])),ROM_sha256=proof['ROM_sha256'],output=str(a.output))))
 raise SystemExit(0 if proof['passed']else 1)
if __name__=='__main__':main()
