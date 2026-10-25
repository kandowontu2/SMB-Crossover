"""Acquire ordinary tiers physically, then qualify bounded native abilities."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from observe_chip_committed_write import lua

ROOT=Path(__file__).resolve().parents[2]
ROM84='84e55b6d60da4be5550d823f88ee40a9b220dbef5a1e8dd21de3d69aa28cb328'
BASE_SHA='5a3599ae1a88008cc828539686d2939b5ffd54c25ebaba8adab01fef866fbe6b'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def replace(text,old,new):
 assert text.count(old)==1,old[:160]
 return text.replace(old,new)

def compose(base,module):
 text=base.read_text();assert sha(base)==BASE_SHA,'Reuse the qualified immutable progression fixture'
 text=replace(text,'local record=nil','local record=nil\nlocal abilityBegin,abilityStage,abilityInput,abilityFinish,abilityReport')
 text=replace(text,"if phase=='settle'and age>=30 or phase=='next'then\n  writeBoundary=true;seed();writeBoundary=false", "if phase=='settle'and age>=30 then abilityBegin(0,'cold baseline')\n elseif phase=='next'then\n  writeBoundary=true;seed();writeBoundary=false\n elseif phase=='ability-setup'then abilityStage()\n elseif phase=='ability'then abilityStage('tick')")
 text=replace(text,"elseif phase=='score-release'and age>=50 and r('FloateyNum_Control',5)==0 then phase='attack-setup';age=0", "elseif phase=='score-release'and age>=50 and r('FloateyNum_Control',5)==0 then abilityBegin(record.after,'physical collection '..index)\n elseif phase=='ability'then abilityFinish()")
 text=replace(text,"local b={};if phase=='collect'then", "local b={};if phase=='ability'then b=abilityInput()elseif phase=='collect'then")
 old="local f=assert(io.open(OUTPUT..'native-progressive.json','w'));f:write(json({passed=true,goal_complete=false,family=C.family,hard=C.hard,cases=records,updates=updates,nmis=nmis,minSP=minSP,apuWrites=apuWrites,irq_scroll_stores=irqStores,hardware_chr_checks=chrChecks,complete_dma_checks=dmaChecks,scope='Actual head-bump/reveal/native full rise; explicit post-rise collision placement; cold selection and source-owned transformation/use. No campaign claim'}));f:close();emu.stop(0)"
 text=replace(text,old,"abilityReport();emu.stop(0)")
 return text+'\n'+module.read_text()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--family',choices=['pit','rygar','scrooge'],required=True);p.add_argument('--mode',choices=['easy','hard'],required=True);p.add_argument('--run-native',action='store_true');p.add_argument('--emulator',type=Path)
 a=p.parse_args();assert sha(a.rom)==ROM84;a.output.mkdir(parents=True,exist_ok=False);b=scoped_load(a.rom)
 for ext in ['.nes','.dbg','.lbl','.map']:shutil.copy2(a.rom.with_suffix(ext),a.output/('candidate'+ext))
 base=ROOT/'tools/audit/final_item_matrix_progressive.lua';module=ROOT/'tools/audit/final_item_abilities_native.lua';guard=ROOT/'tools/audit/final_item_abilities_failure.lua'
 native=compose(base,module)
 for p0 in [base,module,guard]:shutil.copy2(p0,a.output/p0.name)
 names=['GameLoop','GuestBeginPowerup','GuestPowerupUpdate','MarioSourcePowerupCollision','NonMaskableInterrupt','IrqScrollSplit','RosterOamReady','PitFlightUpdate','ExpandedWeapons::CatchDisk','MegaManWeapons::DamageEnemy','ShellOrBlockDefeat','ScroogeMovement::Bounce','ScroogePogoContact']
 hooks={n:dict(address=address(b,n),physical_bank=(location(b,n)-16)//8192,bytes=list(b['raw'][location(b,n):location(b,n)+3]))for n in names}
 for key,n in [('finish','GameLoop'),('NmiReturn','NonMaskableInterrupt')]:
  delta=int(b['syms'][n]['size'],0)-1;pos=location(b,n)+delta;assert b['raw'][pos]in[0x60,0x40]
  hooks[key]=dict(address=address(b,n)+delta,physical_bank=(pos-16)//8192,bytes=[b['raw'][pos]])
 pos=location(b,'IrqScrollSplit');size=int(b['syms']['IrqScrollSplit']['size'],0)
 irq=[address(b,'IrqScrollSplit')+i for i in range(size-2)if b['raw'][pos+i:pos+i+3]==b'\x8d\x05\x20'];assert irq
 character,slot,shot={'pit':(6,6,1),'rygar':(7,7,2),'scrooge':(12,8,0)}[a.family]
 abilities=[]
 for tier in [0,1,2]:
  if a.family=='pit':
   abilities += [dict(name=f'hammer-tier{tier}-face{face}',kind='hammer',tier=tier,face=face,limit=100)for face in[1,2]]
   if tier<2:abilities.append(dict(name=f'flight-gate-tier{tier}',kind='flight_gate',tier=tier,face=1,limit=190))
   else:abilities += [dict(name='flight-exhaust-recharge',kind='flight_full',tier=2,face=1,limit=350),dict(name='flight-release-recharge',kind='flight_release',tier=2,face=1,limit=240)]
  elif a.family=='rygar':
   abilities += [dict(name=f'disk-{kind}-tier{tier}-face{face}',kind=kind,tier=tier,face=face,reach=[40,64,88][tier],limit=100)for kind in['disk_free','disk_hit']for face in[1,2]]
  else:
   abilities.append(dict(name=f'pogo-ground-release-tier{tier}',kind='pogo_ground',tier=tier,face=1,limit=280))
   abilities += [dict(name=f'pogo-enemy-tier{tier}-face{face}',kind='pogo_enemy',tier=tier,face=face,limit=200)for face in[1,2]]
 used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",native+guard.read_text()))
 cfg=dict(family=a.family,character=character,slot=slot,shot=shot,hard=a.mode=='hard',hooks=hooks,irq_scroll_stores=irq,powerup_sfx=address(b,'Sfx_PowerUpGrab'),abilities=abilities,steps=[dict(type=0,before=0,after=1),dict(type=1,before=1,after=2)],ram={n:address(b,n)for n in used if n in b['syms']},art={n:dict(address=address(b,n),bank=(location(b,n)-16)//8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},smc_fields=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
 direct=set(re.findall(r"\b[wr]\('([A-Za-z_][A-Za-z_0-9]*)'",native));assert not direct-set(cfg['ram']),direct-set(cfg['ram'])
 script=a.output/'run.lua';script.write_text('FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+guard.read_text()+'\n'+native,encoding='utf-8');(a.output/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
 proof=dict(passed=False,goal_complete=False,status='prepared_not_native_run',ROM_sha256=ROM84,family=a.family,mode=a.mode,base_fixture_sha256=sha(base),ability_module_sha256=sha(module),failure_guard_sha256=sha(guard),runner_sha256=sha(Path(__file__)),script_sha256=sha(script),scope='Cold baseline0, actual physical head/block reveal/rise/contact/transforms0→1→2, then acquired-tier abilities. World/enemy states explicitly staged; no tier/inventory/fuel/flight/reach/pogo state injection.',abilities=abilities)
 (a.output/'preparation.json').write_text(json.dumps(proof,indent=2)+'\n')
 if a.run_native:
  assert a.emulator and a.emulator.is_file()
  with(a.output/'host.log').open('w')as f:
   result=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),'--emulator',str(a.emulator),str(script),str(a.output/'candidate.nes'),'--timeout','150','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],stdout=f,stderr=subprocess.STDOUT)
  q=a.output/'native-abilities.json';n=json.loads(q.read_text())if q.exists()else{}
  proof.update(passed=result.returncode==0 and n.get('passed',False),status='native_finished',emulator_exit=result.returncode,emulator_sha256=sha(a.emulator),native=n)
  (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],family=a.family,mode=a.mode,exit=result.returncode,abilities=len(n.get('abilities',[])),proof=str(a.output/'proof.json'))));raise SystemExit(0 if proof['passed']else 1)
 print(json.dumps(dict(status=proof['status'],family=a.family,mode=a.mode,abilities=len(abilities))))

if __name__=='__main__':main()
