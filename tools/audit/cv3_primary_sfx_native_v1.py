"""One sequential isolated native Mesen run, bank-qualified CV3 audio fixture."""
from pathlib import Path
import argparse,csv,hashlib,json,re,subprocess,sys
from check_tmnt_render_oa import load,address,location
from observe_chip_committed_write import lua
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--rom',type=Path,required=True);p.add_argument('--capture',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);p.add_argument('--character',type=int,default=5)
 p.add_argument('--observe',action='store_true');p.add_argument('--quick',action='store_true');p.add_argument('--controls',action='store_true');a=p.parse_args()
 out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 b=load(a.rom);names=['PauseSkip','Cv3WeaponsGate','AudioUpdate','NonMaskableInterrupt','IrqScrollSplit','DrawAllMetasprites','RosterOamReady']
 hooks={n:dict(address=address(b,n),physical_bank=(location(b,n)-16)//8192,bytes=list(b['raw'][location(b,n):location(b,n)+3]))for n in names}
 if 'Cv3MusicAndNoiseTick'in b['syms']:
  n='Cv3MusicAndNoiseTick';hooks[n]=dict(address=address(b,n),physical_bank=(location(b,n)-16)//8192,bytes=list(b['raw'][location(b,n):location(b,n)+3]))
 n='NonMaskableInterrupt';delta=int(b['syms'][n]['size'],0)-1
 hooks['NmiReturn']=dict(address=address(b,n)+delta,physical_bank=hooks[n]['physical_bank'],bytes=[b['raw'][location(b,n)+delta]])
 cases=[]
 if a.character==5:
  for mode in (0,1):
   for power in (0,1,2):
    for face in (1,2):
     cases.append(dict(name=f'B-mode{mode}-power{power}-face{face}',kind='weapon',mode=mode,power=power,face=face,updates=68))
  cases+=[dict(name='source-only-stream',kind='stream',updates=68),dict(name='legacy-source-cue',kind='legacy',updates=68),dict(name='six-goomba-pressure',kind='pressure',power=2,updates=240)]
 else:cases=[dict(name='non-CV3-legacy-source',kind='legacy',updates=80),dict(name='non-CV3-six-goomba-pressure',kind='pressure',updates=240)]
 if a.quick:cases=cases[:2]
 if a.controls:
  assert a.character==5 and 'Cv3NoiseActive'in b['syms']
  cases=[dict(name='owner-'+kind,kind=kind,power=2,updates=150 if kind=='pause'else 110)for kind in ('retrigger','pause','stop','world','dmc')]
 tables={n:list(b['raw'][location(b,'X5Menu'+n):location(b,'X5Menu'+n)+19])for n in ('Up','Down','Left','Right')}
 menu_index=a.character;navigation={}
 for start in range(19):
  queue=[(start,[])];seen={start}
  for node,path in queue:
   if node==menu_index:navigation[str(start)]=path[0]if path else 'a';break
   for n,t in tables.items():
    nxt=t[node]
    if nxt not in seen:seen.add(nxt);queue.append((nxt,path+[n.lower()]))
  else:raise AssertionError('Menu unreachable')
 fixture=ROOT/'tools/audit/cv3_primary_sfx_native_v1.lua';guard=ROOT/'tools/audit/z2_platform_native_qa.lua'
 gt=guard.read_text();text=fixture.read_text().replace('-- NMI_GUARD_INSERT',gt[gt.index('local savedNmi=nil'):gt.index('local function seed(q)')])
 used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))
 raw=[{k:int(v)for k,v in r.items()}for r in csv.DictReader((a.capture/'event-1f-apu.csv').open())]
 source=[sorted([[r['address'],r['value']]for r in raw if r['frame']==f])for f in range(28)]
 cfg=dict(character=a.character,menu_index=menu_index,menu_next=navigation,cases=cases,hooks=hooks,source=source,observe=int(a.observe),brick_sfx=address(b,'Sfx_BrickShatter'),
  ram={n:address(b,n)for n in used if n in b['syms']},smc_fields=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
 irq=location(b,'IrqScrollSplit');cfg['irq_scroll_stores']=[address(b,'IrqScrollSplit')+i for i in range(66)if b['raw'][irq+i:irq+i+3]in [bytes.fromhex('8d0520'),bytes.fromhex('8e0520')]]
 script=out/'run.lua';script.write_text('CV3_PRIMARY_NATIVE_CONFIG='+lua(cfg)+'\n'+text)
 command=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator','C:/mesen2/Mesen.exe',str(script),str(a.rom.resolve()),'--timeout','180','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 with(out/'host.log').open('w')as log:r=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 proof=json.loads((out/'proof.json').read_text())if(out/'proof.json').exists()else dict(passed=False)
 proof.update(ROM_sha256=sha(a.rom),emulator_exit=r.returncode,fixture_sha256=sha(fixture),runner_sha256=sha(__file__),imported_guard_sha256=sha(guard),generated_script_sha256=sha(script),emulator_sha256=sha(Path('C:/mesen2/Mesen.exe')),passed=not r.returncode and proof.get('passed',False),accepted=False,scope='Actual cold menu/alternate and B, explicitly staged native actor/power/mode arenas. Original source noise schedule compared to hardware writes; source stream controls are explicit injections. Native five-SMC, A/C bank/stack, visible line31 IRQ, complete DMA and hardware CHR latch checks. No full-roster/campaign or identical waveform claim.')
 (out/'native-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],exit=r.returncode,cases=len(proof.get('cases',[])),output=str(out))))
 raise SystemExit(0 if proof['passed']else 1)
if __name__=='__main__':main()
