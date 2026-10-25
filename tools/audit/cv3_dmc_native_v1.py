"""One sequential native CV3 injury-contact/DMC owner qualification."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys
from check_tmnt_render_oa import load,address,location
from observe_chip_committed_write import lua
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--character',type=int,default=5);p.add_argument('--variant',type=int,default=1);p.add_argument('--observe',action='store_true');p.add_argument('--quick',action='store_true');a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 b=load(a.rom);names=['PauseSkip','Cv3WeaponsGate','Cv3InjuryStartGate','RemainingDmcStart','AudioUpdate','NonMaskableInterrupt','IrqScrollSplit','DrawAllMetasprites','RosterOamReady']
 hooks={n:dict(address=address(b,n),physical_bank=(location(b,n)-16)//8192,bytes=list(b['raw'][location(b,n):location(b,n)+3]))for n in names}
 n='NonMaskableInterrupt';delta=int(b['syms'][n]['size'],0)-1;hooks['NmiReturn']=dict(address=address(b,n)+delta,physical_bank=hooks[n]['physical_bank'],bytes=[b['raw'][location(b,n)+delta]])
 cases=[dict(name='actual-contact',kind='contact',updates=100),dict(name='actual-contact-pressure',kind='pressure',updates=180)]
 if a.character==5 and a.variant in(1,3):cases+=[dict(name='actual-attack-then-contact',kind='attack',updates=110),dict(name='actual-contact-Start-pause-resume',kind='pause',updates=100)]
 if a.quick:cases=cases[:1]
 tables={n:list(b['raw'][location(b,'X5Menu'+n):location(b,'X5Menu'+n)+19])for n in('Up','Down','Left','Right')};nav={}
 for start in range(19):
  queue=[(start,[])];seen={start}
  for node,path in queue:
   if node==a.character:nav[str(start)]=path[0]if path else'a';break
   for n,t in tables.items():
    nxt=t[node]
    if nxt not in seen:seen.add(nxt);queue.append((nxt,path+[n.lower()]))
  else:raise AssertionError('Menu unreachable')
 fixture=ROOT/'tools/audit/cv3_dmc_native_v1.lua';guard=ROOT/'tools/audit/z2_platform_native_qa.lua';gt=guard.read_text();text=fixture.read_text().replace('-- NMI_GUARD_INSERT',gt[gt.index('local savedNmi=nil'):gt.index('local function seed(q)')]);used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))
 original=json.loads((a.source/'proof.json').read_text());name={0:'Simon',1:'Grant',2:'Sypha',3:'Alucard'}[a.variant];src=next(r for r in original['source_injury']if r['character']==name)
 payload=(a.source/(name.lower()+'-injury.dmc')).read_bytes();assert hashlib.sha256(payload).hexdigest()==src['payload_sha256']
 if a.character==4:
  lo,hi=location(b,'AvDmcLinkTakeDamage'),location(b,'AvDmcLinkTakeDamageEnd');payload=b['raw'][lo:hi];src=dict(rate=15,DAC=0,payload_sha256=hashlib.sha256(payload).hexdigest(),length=len(payload))
 cfg=dict(character=a.character,variant=a.variant,menu_index=a.character,menu_next=nav,cases=cases,hooks=hooks,observe=int(a.observe),expected_dmc=int(a.character==4 or a.variant!=2),new_route=int(a.character==5 and a.variant in(1,3)),expected_rate=src['rate'],payload=list(payload),source_payload_sha256=src['payload_sha256'],ram={n:address(b,n)for n in used if n in b['syms']},smc_fields=[address(b,n)+1 for n in['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
 irq=location(b,'IrqScrollSplit');cfg['irq_scroll_stores']=[address(b,'IrqScrollSplit')+i for i in range(66)if b['raw'][irq+i:irq+i+3]in[bytes.fromhex('8d0520'),bytes.fromhex('8e0520')]]
 script=out/'run.lua';script.write_text('CV3_DMC_NATIVE_CONFIG='+lua(cfg)+'\n'+text)
 command=[sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(out),'--emulator','C:/mesen2/Mesen.exe',str(script),str(a.rom.resolve()),'--timeout','180','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
 with(out/'host.log').open('w')as log:r=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 proof=json.loads((out/'proof.json').read_text())if(out/'proof.json').exists()else dict(passed=False);proof.update(ROM_sha256=sha(a.rom),runner_sha256=sha(__file__),fixture_sha256=sha(fixture),guard_sha256=sha(guard),source_receipt_sha256=sha(a.source/'proof.json'),source_payload_sha256=src['payload_sha256'],generated_script_sha256=sha(script),emulator_sha256=sha('C:/mesen2/Mesen.exe'),emulator_exit=r.returncode,passed=not r.returncode and proof.get('passed',False),accepted=False,scope='Real cold-menu selection and staged real enemy contact, native injury owner/request/DMC hardware; explicit delayed actor staging for pending attack. Source-only no longer substitutes for actual injury. Complete native bank/SMC/SP/IRQ/DMA/CHR guards; no campaign/identical waveform claim.')
 (out/'native-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=proof['passed'],exit=r.returncode,cases=len(proof.get('cases',[])),output=str(out))));raise SystemExit(0 if proof['passed']else 1)
if __name__=='__main__':main()
