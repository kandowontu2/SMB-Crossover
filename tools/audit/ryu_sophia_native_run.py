"""Real input/actor native fixture for the frozen Ryu and Sophia repair."""
from pathlib import Path
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
 p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 p.add_argument('--emulator',required=True);p.add_argument('--character',type=int,choices=[10,11],required=True)
 p.add_argument('--diagnostic',action='store_true');p.add_argument('--focus',default='')
 a=p.parse_args();a.output.mkdir(exist_ok=False);b=load(a.rom)
 fixture=ROOT/'tools/audit/ryu_sophia_native_fixture.lua'
 names=['PauseSkip','ExpandedWeapons','AvRyuSpecial','InventoryGrant','InventoryUiTick','InventoryClearActive','RemainingWeapons::SophiaInput','NonMaskableInterrupt','HandlePowerUpCollision','PowerUpObjHandler']
 hooks={n:dict(address=address(b,n),physical_bank=(location(b,n)-16)//8192,bytes=list(b['raw'][location(b,n):location(b,n)+3]))for n in names}
 n='NonMaskableInterrupt';delta=int(b['syms'][n]['size'],0)-1
 hooks['NmiReturn']=dict(address=address(b,n)+delta,physical_bank=(location(b,n)+delta-16)//8192,bytes=list(b['raw'][location(b,n)+delta:location(b,n)+delta+1]))
 cases=[dict(name=f'ryu-slash-pickup{item}',kind='ryu',item=item)for item in range(1,5)]+[dict(name='ryu-ordinary-primary',kind='primary',item=0)] if a.character==10 else [dict(name=f'sophia-free{free}',kind='sophia',free=free)for free in [1,2,3]]+[dict(name='sophia-existing-missile',kind='sophia',free=9,active=1)]
 if a.focus:cases=[c for c in cases if a.focus in c['name']]
 used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",fixture.read_text()))
 cfg=dict(character=a.character,cases=cases,diagnostic=int(a.diagnostic),hooks=hooks,ram={n:address(b,n)for n in used if n in b['syms']},power_id=address(b,'PowerUpObject'),smc_fields=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
 script=a.output/'run.lua';script.write_text('RYU_SOPHIA_NATIVE_CONFIG='+lua(cfg)+'\n'+fixture.read_text())
 with(a.output/'host.log').open('w')as f:
  result=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),'--emulator',a.emulator,str(script),str(a.rom),'--timeout','110','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],stdout=f,stderr=subprocess.STDOUT)
 proof=json.loads((a.output/'proof.json').read_text())if(a.output/'proof.json').exists()else dict(passed=False)
 pixels=[];paths=[]
 for raw in sorted(a.output.glob('*.argb')):
  v=np.frombuffer(raw.read_bytes(),dtype='<u4').reshape(240,256)
  rgb=np.stack(((v>>16)&255,(v>>8)&255,v&255),axis=2).astype(np.uint8)
  Image.fromarray(rgb).save(raw.with_suffix('.png'));pixels.append(dict(file=raw.name,sha256=sha(raw)));paths.append(raw.with_suffix('.png'))
 if paths:
  sheet=Image.new('RGB',(1024,((len(paths)+3)//4)*260),(24,28,36));draw=ImageDraw.Draw(sheet)
  for i,path in enumerate(paths):
   with Image.open(path)as im:sheet.paste(im,(i%4*256,i//4*260+20))
   draw.text((i%4*256+2,i//4*260+2),path.stem,fill='white')
  sheet.save(a.output/'overview.png')
 proof.update(passed=result.returncode==0 and proof.get('passed',False),emulator_exit=result.returncode,ROM_sha256=sha(a.rom),ROM_path=str(a.rom.resolve()),fixture_sha256=sha(fixture),runner_sha256=sha(Path(__file__)),script_sha256=sha(script),emulator_sha256=sha(Path(a.emulator)),physical_frames=pixels,goal_complete=False,dependencies={str(q.relative_to(ROOT)):sha(q)for q in [ROOT/'tools/run_mesen.py',ROOT/'tools/audit/run_mesen_isolated.py']})
 (a.output/'native-proof.json').write_text(json.dumps(proof,indent=2))
 print(json.dumps(dict(passed=proof['passed'],cases=len(proof.get('cases',[])),violations=len(proof.get('violations',[])),ROM_sha256=proof['ROM_sha256'],output=str(a.output))))
 raise SystemExit(0 if proof['passed']else 1)

if __name__=='__main__':main()
