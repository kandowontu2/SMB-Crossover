"""Real reset/IdleLoop Main caller plus actual IRQ/NMI on private Tank code."""
from pathlib import Path
import hashlib,inspect,itertools,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_visible_1101_v5 import O,P,PIN
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import check_hogan_current_bounded_v1 as M
import check_kirby_owner_main_1101_v2 as K
import ff_host_pickups_vectors_v2 as V
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 base=scoped_load(P/'candidate.nes');assert sha(base['raw'])==PIN;raw=(O/'candidate.nes').read_bytes();b=dict(base,raw=raw);assembly=json.loads((O/'graft-assembly.json').read_text())
 ranges=[(128|r['bank'],r['run_PC'],r['run_PC']+r['used'])for r in assembly['source_owner_intervals']]
 ranges.extend([(2,0xb600,0xb600+721),(2,0xbca0,0xbca0+306)])
 def owned(m,c):return any(bank==m.rawtags[1]and lo<=c.pc<hi for bank,lo,hi in ranges)if 0xa000<=c.pc<0xc000 else 0x15a<=c.pc<0x17b
 # Exact actual owning caller executes reset's profilingJSR, IdleLoop PHA,
 # JSR GameLoop and the parent PLA. EntrySPFA comes from source, not a test
 # farcall at arbitrary224. Keep only3 bounded in-memory Main samples.
 m=M.fresh(b);M.put(m,CrossoverMenuIndex=0);M.invoke(m,'MenuResolveCharacter');M.invoke(m,'QueueSelection')
 while M.get(m,'MarioVariant')!=7:
  M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);M.invoke(m,'CrossoverMenuInput')
 M.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0);s=M.invoke(m,'CrossoverMenuInput');M.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=s['A'],x=s['X'],y=s['Y'],p=s['P']);M.invoke(m,'PauseRoutine',a=0)
 samples=[];minimum=255
 for i in range(600):
  if M.get(m,'OperMode_Task')==3 and M.get(m,'GameEngineSubroutine')==8:break
  K.keys(m,0);origin=M.fork(m);before=bytes(m.ram[2][0x1fe0:0x1ff0]);deep=[255,0]
  def depth(mem,c,step):
   if c.sp<deep[0]:deep[:]=[c.sp,step]
  c,low=K.call(m,'GameLoop',depth);minimum=min(minimum,low)
  if before!=(O/'cookie.bin').read_bytes()and bytes(m.ram[2][0x1fe0:0x1ff0])==(O/'cookie.bin').read_bytes():samples.append(('cold-scene',origin,M.fork(m),(c.a,c.x,c.y,c.p,c.sp),deep[1]))
  M.consume(m)
 else:raise AssertionError('Native parser bounded')
 assert len(samples)==1
 for kind in ['walk','head']:
  M.put(m,PlayerStatus=2,PlayerSize=0,Player_State=0,Player_X_Position=96,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_X_Speed=0,Player_Y_Speed=0,TimerControl=0,GameEngineSubroutine=8,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0,BlockBounceTimer=0)
  if kind=='head':
   M.put(m,Player_State=1,Player_Y_Position=83,Player_Y_Speed=255,Player_Y_MoveForce=0);M.invoke(m,'BlockBufferColli_Head',y=0);at=M.get(m,'R6')+256*M.get(m,'R7')+M.get(m,'R2');m[at]=0xc1
  K.keys(m,1 if kind=='walk'else 0);origin=M.fork(m);deep=[255,0];c,low=K.call(m,'GameLoop',depth);minimum=min(minimum,low)
  if kind=='head':assert m[at]==0 and not M.get(m,'Enemy_Flag',5),'Actual native question head destruction'
  samples.append((kind,origin,M.fork(m),(c.a,c.x,c.y,c.p,c.sp),deep[1]));M.consume(m)
 previous=V.pending_store;old_interrupt=V.interrupt
 # Native SMB music uses its named MusicData pointerDA/DB. Tank neither
 # imports nor borrows it. The earlier Kirby-oriented vector helper allowed
 # only the guest audio pointer range; retain every other strict ABI check.
 audio_line="audio=range(address(b,'XgAudioPtr'),address(b,'XgAudioZeroPageEnd'))"
 replacement="audio=set(range(address(b,'XgAudioPtr'),address(b,'XgAudioZeroPageEnd')))|{address(b,'MusicDataLow'),address(b,'MusicDataHigh')}"
 actual=inspect.getsource(V.interrupt);assert audio_line in actual;ns=dict(V.__dict__);exec(actual.replace(audio_line,replacement),ns);V.interrupt=ns['interrupt']
 def pending(mem,c,slot,op):
  if previous(mem,c,slot,op):return True
  target=0x5115 if slot==1 else 0x5116;value={0x8d:c.a,0x8e:c.x,0x8c:c.y}.get(mem[c.pc])
  return value is not None and bytes(mem[c.pc+1:c.pc+3])==target.to_bytes(2,'little')and value==M.get(mem,'CurrentBank'if slot==1 else'CurrentBankC')
 V.pending_store=pending;rows=[];worst=255
 try:
  for kind,origin,expected,regs,deepcut in samples:
   for interrupt in ['IRQ','NMI']:
    n=M.fork(origin);cuts=set();events=[];masked=0
    def observe(mem,c,step):
     nonlocal masked
     tag=mem.rawtags[1]if 0xa000<=c.pc<0xc000 else -1;key=(tag,c.pc)
     if (not owned(mem,c)and step!=deepcut)or key in cuts:return
     cuts.add(key)
     if interrupt=='IRQ'and c.p&4:masked+=1;return
     row=V.interrupt(mem,c,interrupt);events.append(dict(PC=c.pc,foreground_SP=c.sp,**row))
    c,low=K.call(n,'GameLoop',observe)
    assert (c.a,c.x,c.y,c.p,c.sp)==regs and K.fg(n)==K.fg(expected),('ActualMain resume',kind,interrupt)
    level=min([e['minimum_SP']for e in events],default=255);worst=min(worst,level);rows.append(dict(case=kind,interrupt=interrupt,actual_return_cases=len(events),masked_IRQ_cuts=masked,unique_owned_PC_cuts=len(cuts),minimum_ISR_SP=level,event_digest=sha(json.dumps(events,sort_keys=True).encode())))
 finally:V.pending_store=previous;V.interrupt=old_interrupt
 assert worst>=135,(worst,'12-byte reserved margin aboveSMC122')
 q=dict(passed=True,current_ROM_sha256=sha(raw),base_ROM_sha256=PIN,actual_Reset_IdleLoop_Main=True,actual_Main_entry_SP=250,actual_Main_minimum_SP=minimum,actual_ISR_minimum_SP=worst,minimum_reserve_above_SMC=worst-123,required_reserve=12,actual_IRQ_NMI_returns=sum(r['actual_return_cases']for r in rows),samples=rows,native_SMB_audio_pointer_exception=[address(b,'MusicDataLow'),address(b,'MusicDataHigh')],exception_bound_to_named_audio_only=True,actual_native_question_destruction=True,owning_full_relink=False,resources_pending=True,native_Mesen=False,installed=False,scope='One real cold-scene Main plus powered walk and destructive head Main. Sequential adversarial actual IRQ or lagNMI at each reached unique ownedPC/SMC instruction; every return ABI/liveRAM/33SMC/ZP/map checked by native vector harness, then whole Main foreground equals un-interrupted reference. This is not isolated independent interrupts at every entire-ROM instruction or full-stage qualification.',bindings={str(p.relative_to(R)):sha(p.read_bytes())for p in[Path(__file__),R/'tools/audit/check_kirby_owner_main_1101_v2.py',R/'tools/audit/ff_host_pickups_vectors_v2.py']})
 (O/'Main-vector-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
