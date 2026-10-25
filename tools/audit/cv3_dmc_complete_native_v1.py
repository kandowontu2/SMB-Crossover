"""One granted sequential native worker; freeze scripts before an optional run."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
from check_tmnt_render_oa import load,address,location
from observe_chip_committed_write import lua
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--character',type=int,default=5);p.add_argument('--variant',type=int,default=1);p.add_argument('--profile',choices=('basic','controls','pressure','legacy','death','character'),default='basic');p.add_argument('--quick',action='store_true');p.add_argument('--ram-power-on',choices=('AllZeros','AllOnes'),default='AllZeros');p.add_argument('--run',action='store_true');a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 b=load(a.rom);mirror=int('Cv3DmcPriority'in b['syms']);names=['PauseSkip','Cv3WeaponsGate','Cv3InjuryStartGate','KillPlayer','RemainingDmcStart','Cv3MusicAndNoiseTick','AudioUpdate','NonMaskableInterrupt','IrqScrollSplit','DrawAllMetasprites','RosterOamReady']
 hooks={n:dict(address=address(b,n),physical_bank=(location(b,n)-16)//8192,bytes=list(b['raw'][location(b,n):location(b,n)+3]))for n in names}
 n='NonMaskableInterrupt';delta=int(b['syms'][n]['size'],0)-1;hooks['NmiReturn']=dict(address=address(b,n)+delta,physical_bank=hooks[n]['physical_bank'],bytes=[b['raw'][location(b,n)+delta]])
 if a.profile=='basic':cases=[dict(name=f'actual-{kind}-mode{mode}',kind=kind,mode=mode,updates=100)for kind in(('primary','contact')if a.variant in(1,2)else('contact','attack'))for mode in(0,1)]
 elif a.profile=='controls':cases=[dict(name=f'{kind}-mode1',kind=kind,mode=1,updates=110)for kind in('primary-pause','scene','preempt','priority')]
 elif a.profile=='pressure':cases=[dict(name=f'no-source-six-goomba-mode{mode}',kind='idle',mode=mode,updates=240)for mode in(0,1)]
 elif a.profile in('death','character'):cases=[dict(name='actual-fatal-contact'if a.profile=='death'else'staged-character-reset-owner',kind=a.profile,mode=1,updates=180)]
 else:cases=[dict(name='ordinary-source-injury-Hard',kind='contact',mode=1,updates=120)] # Easy intentionally uses legacy shrink/injury policy.
 if a.quick:cases=[q for q in cases if q['mode']==1][:2]
 tables={n:list(b['raw'][location(b,'X5Menu'+n):location(b,'X5Menu'+n)+19])for n in('Up','Down','Left','Right')};nav={}
 for start in range(19):
  queue=[(start,[])];seen={start}
  for node,path in queue:
   if node==a.character:nav[str(start)]=path[0]if path else'a';break
   for n,t in tables.items():
    nxt=t[node]
    if nxt not in seen:seen.add(nxt);queue.append((nxt,path+[n.lower()]))
  else:raise AssertionError('Menu unreachable')
 fixture=ROOT/'tools/audit/cv3_dmc_complete_native_v1.lua';guard=ROOT/'tools/audit/z2_platform_native_qa.lua';gt=guard.read_text();text=fixture.read_text().replace('-- NMI_GUARD_INSERT',gt[gt.index('local savedNmi=nil'):gt.index('local function seed(q)')]);used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))
 samples=[];orig=json.loads((D/'cv3-dmc-followup-v1/capacity-source-v1/proof.json').read_text())
 for sound,name in[(0x74,'Grant'),(0x75,'Sypha'),(0x76,'Alucard'),(0x73,'Simon')]:
  source=next(r for r in orig['source_injury']if r['character']==name);payload=(D/'cv3-dmc-followup-v1/capacity-source-v1'/(name.lower()+'-injury.dmc')).read_bytes();assert hashlib.sha256(payload).hexdigest()==source['payload_sha256']
  if sound==0x75 and not mirror:continue
  samples.append(dict(sound=sound,bank=125 if mirror and sound!=0x73 else 127,address=0xf5c0 if sound==0x75 else 0xff00,rate=source['rate'],payload=list(payload),source=1))
 if mirror:
  payload=(D/'cv3-primary-sfx-v1/source-cpu-v2/cv3-event72.dmc').read_bytes();assert hashlib.sha256(payload).hexdigest()=='c1b646c36508ad4d134078c8184fea7bd632f50127c5f2af6550e89097cbda01';samples.append(dict(sound=0x72,bank=125,address=0xf140,rate=15,payload=list(payload),source=1))
 lo,hi=location(b,'AvDmcLinkTakeDamage'),location(b,'AvDmcLinkTakeDamageEnd');samples.append(dict(sound=21,bank=127,address=address(b,'AvDmcLinkTakeDamage'),rate=15,payload=list(b['raw'][lo:hi]),source=0))
 cfg=dict(character=a.character,variant=a.variant,menu_index=a.character,menu_next=nav,cases=cases,hooks=hooks,observe=0,mirror=mirror,samples=samples,end_levels={'114':24,'116':4,'117':34,'118':4,'115':0,'21':0},overlays=[[0x1140,0x1581],[0x15c0,0x1681],[0x1af7,0x1b8a]],ram={n:address(b,n)for n in used if n in b['syms']},smc_fields=[address(b,n)+1 for n in['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
 if mirror:
  fixed=b['raw'][16+127*8192:16+128*8192];clone=b['raw'][16+125*8192:16+126*8192];assert all(x==y or any(lo<=i<hi for lo,hi in cfg['overlays'])for i,(x,y)in enumerate(zip(fixed,clone)))
 irq=location(b,'IrqScrollSplit');cfg['irq_scroll_stores']=[address(b,'IrqScrollSplit')+i for i in range(66)if b['raw'][irq+i:irq+i+3]in[bytes.fromhex('8d0520'),bytes.fromhex('8e0520')]]
 script=out/'run.lua';script.write_bytes(('CV3_DMC_COMPLETE_NATIVE_CONFIG='+lua(cfg)+'\n'+text).encode());assert not re.search(r'\b(?:True|False)\b',script.read_text().splitlines()[0]);(out/'configuration.json').write_text(json.dumps(cfg,indent=2)+'\n')
 dependencies=[Path(__file__),fixture,guard,ROOT/'tools/audit/observe_chip_committed_write.py',ROOT/'tools/audit/run_mesen_isolated.py',ROOT/'tools/audit/check_tmnt_render_oa.py']
 frozen=out/'frozen';frozen.mkdir();bindings={}
 for f in dependencies:shutil.copyfile(f,frozen/f.name);bindings[f.name]=sha(f)
 (out/'bindings.json').write_text(json.dumps(dict(ROM_sha256=sha(a.rom),script_sha256=sha(script),dependencies=bindings,emulator_sha256=sha('C:/mesen2/Mesen.exe'),source_injury_receipt_sha256=sha(D/'cv3-dmc-followup-v1/capacity-source-v1/proof.json')),indent=2)+'\n')
 if not a.run:print(json.dumps(dict(prepared=True,script=str(script),ROM_sha256=sha(a.rom),cases=len(cases))));return
 command=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator','C:/mesen2/Mesen.exe',str(script),str(a.rom.resolve()),'--timeout','180','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState='+a.ram_power_on,'--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 with(out/'host.log').open('w')as log:result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 proof=json.loads((out/'proof.json').read_text())if(out/'proof.json').exists()else dict(passed=False);proof.update(ROM_sha256=sha(a.rom),bindings_sha256=sha(out/'bindings.json'),profile=a.profile,ram_power_on=a.ram_power_on,emulator_exit=result.returncode,passed=not result.returncode and proof.get('passed',False),accepted=False,scope='Real menu selection, explicitly staged native combat/driver controls and physical B/Start inputs. Individual source-only priority/preemption/scene controls are labeled, not substituted for real primary/injury owners. Actual mapping/interrupt/OAM/CHR guards; no campaign/waveform or unavailable-state claim.')
 (out/'native-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],exit=result.returncode,cases=len(proof.get('cases',[])),output=str(out))));raise SystemExit(0 if proof['passed']else 1)
if __name__=='__main__':main()
