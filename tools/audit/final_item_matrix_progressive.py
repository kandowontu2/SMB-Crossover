"""Prepare/run scoped physical-block progressive fixtures (no native run by default)."""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, sys
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from observe_chip_committed_write import lua

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 p.add_argument('--family',choices=['pit','rygar','scrooge'],default='pit');p.add_argument('--mode',choices=['easy','hard'],required=True)
 p.add_argument('--expected-sha256');p.add_argument('--run-native',action='store_true');p.add_argument('--emulator',type=Path)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=scoped_load(a.rom)
 if a.expected_sha256:assert sha(a.rom)==a.expected_sha256,'ROM binding'
 assert ((b['raw'][6]>>4)|(b['raw'][7]&240))==5,'This fixture binds expanded MMC5'
 for ext in ['.nes','.dbg','.lbl','.map']:
  q=a.rom.with_suffix(ext)
  if q.exists():shutil.copy2(q,a.output/('candidate'+ext))
 if not(a.output/'candidate.dbg').exists():shutil.copy2(a.rom.with_suffix('.dbg.gz'),a.output/'candidate.dbg.gz')
 fixture=ROOT/'tools/audit/final_item_matrix_progressive.lua';base=ROOT/'tools/audit/continuation_20261024/legacy-native-items-v3.lua'
 head=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/native-probes-qa-v2/items-v1/fixtures/alucard-hard/dependency-0.lua')
 # Keep source fixture attribution explicit: arena and cold-menu schedule reused,
 # inventory assertions replaced by these three families' real progressive owner.
 (a.output/'fixture.lua').write_bytes(fixture.read_bytes())
 names=['GameLoop','GuestBeginPowerup','GuestPowerupUpdate','MarioSourcePowerupCollision','NonMaskableInterrupt','IrqScrollSplit','RosterOamReady']
 hooks={n:dict(address=address(b,n),physical_bank=(location(b,n)-16)//8192,bytes=list(b['raw'][location(b,n):location(b,n)+3]))for n in names}
 for key,n in [('finish','GameLoop'),('NmiReturn','NonMaskableInterrupt')]:
  d=int(b['syms'][n]['size'],0)-1;at=location(b,n)+d
  assert b['raw'][at]in [0x60,0x40],(key,hex(b['raw'][at]))
  hooks[key]=dict(address=address(b,n)+d,physical_bank=(at-16)//8192,bytes=[b['raw'][at]])
 char,slot,shot={'pit':(6,6,1),'rygar':(7,7,2),'scrooge':(12,8,0)}[a.family]
 used=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",fixture.read_text()))
 irq_at=location(b,'IrqScrollSplit');irq_size=int(b['syms']['IrqScrollSplit']['size'],0)
 irq_stores=[address(b,'IrqScrollSplit')+i for i in range(irq_size-2)if b['raw'][irq_at+i:irq_at+i+3]==bytes([0x8d,0x05,0x20])]
 assert irq_stores,'Bound actual IRQ scroll stores'
 cfg=dict(family=a.family,character=char,slot=slot,shot=shot,hard=a.mode=='hard',hooks=hooks,irq_scroll_stores=irq_stores,powerup_sfx=address(b,'Sfx_PowerUpGrab'),steps=[dict(type=0,before=0,after=1),dict(type=1,before=1,after=2),dict(type=1,before=2,after=2)],ram={n:address(b,n)for n in used if n in b['syms']},art={n:dict(address=address(b,n),bank=(location(b,n)-16)//8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']},smc_fields=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2])
 assert cfg['ram']['PlayerStatus']<0x8000
 script=a.output/'run.lua';script.write_text('FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+fixture.read_text(),encoding='utf-8')
 (a.output/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
 rec=dict(status='prepared_not_native_run',passed=False,goal_complete=False,ROM_sha256=sha(a.rom),ROM_path=str(a.rom.resolve()),family=a.family,mode=a.mode,fixture_sha256=sha(fixture),runner_sha256=sha(Path(__file__)),script_sha256=sha(script),reuse=[dict(path=str(base),sha256=sha(base),scope='Cold owner/mode selection and guarded GameLoop arena; no inventory/power-tier injection.'),dict(path=str(head),sha256=sha(head),scope='Actual A head bump; visible/logical question block; native reveal/full rise/no-premature-grant; explicit post-rise collision placement.')],expected=['Actual A head bump creates source-owned reward actor','Stable reward stamp/type; visible native full rise before grant','Physical collision executes actual source owner','Native60-update transform twice, plus tier2 cap','No direct PlayerStatus mutation by fixture','Actual B shot/cane and native cleanup after each acquired tier','PPU captures, APU writes, five SMC operands, NMI actual/shadow banks and stack guard'],limits=['Explicit world/PPU blocks staged; mature actor is placed into collision only after full native rise at guarded loop entry, matching historical fixture policy','No native run or pass until explicit --run-native and a Mesen worker grant','Pit flight/hammer, Rygar hit damage and Scrooge pogo remain separate assertions','Star and1-up intentionally remain separate physical fixtures; no generic item counter'])
 (a.output/'preparation.json').write_text(json.dumps(rec,indent=2)+'\n')
 if a.run_native:
  assert a.emulator and a.emulator.is_file(),'Explicit deterministic Mesen binary required'
  with(a.output/'host.log').open('w')as f:
   r=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),'--emulator',str(a.emulator),str(script),str(a.output/'candidate.nes'),'--timeout','150','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],stdout=f,stderr=subprocess.STDOUT)
  proof=a.output/'native-progressive.json';z=json.loads(proof.read_text())if proof.exists()else{}
  rec.update(status='native_finished',passed=r.returncode==0 and z.get('passed',False),emulator_exit=r.returncode,emulator_sha256=sha(a.emulator),native=z)
  (a.output/'proof.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec));raise SystemExit(0 if rec['passed']else 1)
 print(json.dumps({k:rec[k]for k in ['status','passed','ROM_sha256','family','mode']}))

if __name__=='__main__':main()
