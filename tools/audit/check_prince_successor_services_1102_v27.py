"""Actual613b manager/cold/Fresh/public epochs and service-tag closure."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import prepare_prince_successor_manifest_1102_v26 as M
import check_prince_host_services_1102_v18 as H
import check_hogan_current_bounded_v1 as N
from check_tmnt_render_oa import address,location
O=M.O


def invoke(m,bank,target,args=(83,71,109,0x31),interrupt=None):
 b=m.bundle;m[address(b,'SafecallA_SMC')+1]=args[0];m[address(b,'FarcallJmpTarget_SMC')+1]=target&255;m[address(b,'FarcallJmpTarget_SMC')+2]=target>>8
 c=N.NesMPU(memory=m,pc=address(b,'FarCallCommon'));c.a=bank;c.x,c.y=args[1:3];c.p=args[3];c.sp=224;c.stPushWord(0x5aff);low=c.sp;cuts=set();injected=False;live=True;tagwrites=0;read_before_world_write=0;world_written=False;frame_writes=[]
 for _ in range(4000000):
  if c.pc==0x5b00:break
  cut=(c.pc,c.sp,m.rawtags[1]);low=min(low,c.sp)
  if m.rawtags[1]==193 and(0xa740<=c.pc<0xa7f2 or 0xaaf7<=c.pc<0xabd4 or 0xae00<=c.pc<0xb013):cuts.add(cut)
  if 0xb3ef<=c.pc<0xb3fc or 0xdcc5<=c.pc<0xdd24:cuts.add(cut)
  # C09E is only the world leaf's SavedY. The service resolver reads its
  # incoming typed tag; genuine world routine must STY before its own LDY.
  op=bytes(m[c.pc:c.pc+3])if m.rawtags[1]==3 and 0xbde2<=c.pc<0xbfa3 else None
  if op==bytes.fromhex('8c9ec0'):world_written=True;tagwrites+=1
  if op==bytes.fromhex('ac9ec0'):assert world_written,('World SavedY read before write',hex(c.pc));read_before_world_write+=1
  if interrupt is not None and not injected and cut==interrupt[1]:
   injected=True;regs=(c.a,c.x,c.y,c.p,c.sp,c.pc);maps=m.rawtags[:];state=[bytes(x)for x in m.ram];scratch=bytes(m[3:11]);smc=bytes(m[0x15a:0x17b]);wr=len(m.ram_writes)
   assert not c.p&4;c.irq()if interrupt[0]=='IRQ'else c.nmi()
   for _ in range(200000):
    low=min(low,c.sp)
    if c.pc==regs[5]and c.sp==regs[4]:break
    assert m[c.pc]!=0,('Native service ISR BRK',interrupt,hex(c.pc));c.step()
   else:raise AssertionError(('Native service ISR bound',interrupt))
   if maps!=m.rawtags:
    ins=bytes(m[c.pc:c.pc+3]);assert ins in [bytes.fromhex('8d1551'),bytes.fromhex('8d1651'),bytes.fromhex('8e1651')]
    window=1 if ins[1]==0x15 else 2;shadow=N.get(m,'CurrentBank'if window==1 else'CurrentBankC');assert m.rawtags[window]==shadow and all(maps[k]==m.rawtags[k]for k in range(4)if k!=window)
   assert regs[:3]==(c.a,c.x,c.y)and regs[3]&0xef==c.p&0xef and regs[4:]==(c.sp,c.pc)
   assert state==[bytes(x)for x in m.ram]and scratch==bytes(m[3:11])and smc==bytes(m[0x15a:0x17b])and not m.ram_writes[wr:]
  assert m[c.pc]!=0,('Actual Prince service BRK',hex(c.pc),m.rawtags);c.step()
 else:raise AssertionError(('Actual Prince service bound',hex(c.pc)))
 assert c.sp==224 and(interrupt is None or injected)
 return dict(regs=[c.a,c.x,c.y,c.p,c.sp],CPU=c.processorCycles,minSP=low,cuts=cuts,world_SavedY_writes=tagwrites,world_SavedY_reads=read_before_world_write)


def main():
 old,new,patches,event=M.bundle();m=N.fresh(new);m.ram[2][:]=bytes([0x9d])*8192;m.ram[3][:]=bytes([0x6b])*8192
 for k in [2,3]:m.ram[k][0x1fe0:0x1ff0]=bytes(16)
 m.raw_page(2,2);N.put(m,CurrentBankC=2,SelectedCharacter=38,OperMode=1,GameEngineSubroutine=8,GamePauseStatus=0,FrameCounter=0,Player_X_Position=48,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,NmiDisable=255,DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=160,FamilyMainCommit=1,ReloadCHRBank=0)
 m.ppuctrl=160;m[0x2001]=0;before=m.ppu_reads
 print('Executing actual shared typed cold route.',flush=True)
 cold=invoke(m,193,0xae00);assert cold['regs'][3]&1,cold
 print('Actual shared typed cold route passed.',flush=True)
 # Use actual linked cookie address, not a private hand-bound table value.
 lab=H.P.T.labels(O/'owner-third-v23.lbl');at=16+65*8192+lab['PrCookie']-0xa000;cookie=new['raw'][at:at+16]
 assert m.ram[2][0x1fe0:0x1ff0]==m.ram[3][0x1fe0:0x1ff0]==cookie
 assert m.ram[2][0xab]==0xa7 and m.ram[2][0x6cf]==5 and not m.ram[2][0xac]
 assert bytes(m.ram[2][0x200:0x235])==bytes(53)
 source_cold=dict(CPU=cold['CPU'],minSP=cold['minSP'],buffered_PPU_reads=m.ppu_reads-before,complete_both_headers_last_published=True,Ready=167,originalHP=5)
 # Diagnostics are not machine state. Do not deep-copy the cold loader's
 # large historical write log into every hot interrupt fixture.
 for name in ['writes','ram_writes','ppu_log','blocked']:setattr(m,name,[])
 # Warm scene/Fresh clears original actor-live state while preserving every
 # executable byte and pose metadata. Old native packet is source-dead and
 # is retained until Draw writes its complete consumed packet.
 seed=N.fork(m);profile=json.loads((O/'public-routes-measurement-v24.json').read_text());expected=H.host(H.W.scoped_load(H.E.C.BASE));fresh_cases=0;warm_cycles=[]
 for row in [15,36]:
  for pattern in [0x19,0xe3]:
   n=N.fork(seed)
   for lo,hi in profile['source_original_live_state_zero_ranges']:n.ram[2][lo-0xc000:hi-0xc000]=bytes([pattern])*(hi-lo)
   packet=bytes(n.ram[2][0x200:0x235]);code=[bytes(n.ram[k])for k in [2,3]];out=invoke(n,193,0xb08c+3*row);assert out['regs'][3]&1
   for i,(a,z)in enumerate(zip(n.ram[2][:0x800],expected.s[:0x800])):
    if not 0x200<=i<0x235:assert a==z,('Fresh original state',row,pattern,hex(i),a,z)
   assert bytes(n.ram[2][0x200:0x235])==packet
   assert bytes(n.ram[2][0x800:])==code[0][0x800:]and bytes(n.ram[3])==code[1]
   fresh_cases+=1;warm_cycles.append(out['CPU'])
 print('Warm Fresh/scene constructors passed.',flush=True)
 # Actual public native HuMovement executes the original four-phase owner
 # clock. No source/callback fixture is installed in this candidate bus.
 n=N.fork(seed);N.put(n,DisableScreenFlag=0,NmiDisable=1,SavedJoypad1Bits=0)
 for name in ['Block_Buffer_1','Block_Buffer_2']:
  at=address(new,name)
  for row in range(13):
   for col in range(16):n[at+16*row+col]=0x54 if row>=11 else 0
 ticks=0;sourcewrites=reads=0
 for epoch in range(16):
  N.put(n,FrameCounter=epoch,SavedJoypad1Bits=1 if epoch>=4 else 0)
  out=invoke(n,207,address(new,'HuMovement'));assert out['regs'][3]&1,('Public movement declined',epoch,out)
  sourcewrites+=out['world_SavedY_writes'];reads+=out['world_SavedY_reads'];ticks+=1
  state=[bytes(x)for x in n.ram];duplicate=invoke(n,207,address(new,'HuMovement'));delta=[(bank,i,a,z)for bank in range(4)for i,(a,z)in enumerate(zip(state[bank],n.ram[bank]))if a!=z]
  assert not duplicate['regs'][3]&1 and all((bank,i)==(2,0x9e)for bank,i,_,_ in delta),('Duplicate epoch source state',epoch,duplicate,delta)
 assert sourcewrites and reads and sourcewrites==reads
 print('Actual native movement phase/duplicate/tag cases passed.',flush=True)
 # All reached transport/auth/new tag/resolver instructions run real IRQ
 # and lag-NMI continuations. Movement is paused by duplicate epoch here,
 # leaving a short finite service whose rejection still consumes the tag.
 for name in ['writes','ram_writes','ppu_log','blocked']:setattr(n,name,[])
 trace_seed=N.fork(n);reference=N.fork(trace_seed);ref=invoke(reference,207,address(new,'HuMovement'));cuts=sorted(ref['cuts']);counts={};minimum=224
 for kind in ['IRQ','lagNMI']:
  for cut in cuts:
   z=N.fork(trace_seed);got=invoke(z,207,address(new,'HuMovement'),interrupt=(kind,cut))
   assert got['regs']==ref['regs']and z.ram==reference.ram and z.rawtags==reference.rawtags
   assert bytes(z[3:11])==bytes(reference[3:11])and bytes(z[0x15a:0x17b])==bytes(reference[0x15a:0x17b])
   minimum=min(minimum,got['minSP']);counts[kind]=counts.get(kind,0)+1
 world=R/'tools/reference/prince_host_world_1102_v8.s';text=world.read_text();uses=[z.strip()for z in text.splitlines()if re.search(r'\bSavedY\b',z)];assert uses==['SavedY=$c09e','sty SavedY','ldy SavedY'],uses
 q=dict(passed=True,proposal_only=True,ROM_written=False,grant=False,base_SHA256=M.A.PIN,successor_memory_SHA256=M.sha(new['raw']),actual_shared_typed_cold=source_cold,warm_Fresh_and_scene_constructor_cases=fresh_cases,warm_CPU=warm_cycles,warm_packet_preserved=True,all_original_actor_live_state_equals_fresh=True,all_executable_state_and_metadata_unchanged=True,actual_native_HuMovement_epochs=ticks,duplicate_epochs_rejected=ticks,actual_world_SavedY_write_before_read_pairs=reads,source_SavedY_uses=uses,real_IRQ_lagNMI_cuts=counts,minimum_ISR_SP=minimum,SourceStateTag_C09E_lifetime='Typed public entry consumes tag before any original world call. World SavedY has one direct STY/LDY pair and always writes before read; original donor graph/source slot audit excludes geometry range. IRQ/native lag-NMI perform no private RAM writes.',all_Bub_v9_event_spans_preserved=event,scope='Actual613b shared manager and common worker copy verified617/619 bootstrap, execute3 lossless source streams, genuine constructor then publish both complete16Bheaders. Actual public movement/Fresh/scene and tag/ISR execute in memory. No menu/native emulator/fullstage; original palette/health/hurt/combat/native collision profiles still unbound.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'successor-proposal-v26.json',O/'cold-pool-v25.bin',O/'owner-third-v23.bin',O/'owner-third-extra-v23.bin',O/'public-selector-v24.bin',O/'public-private-v24.bin',O/'public-fresh-v24.bin',world,R/'docs/qa/allocations/prince-executable-state-1102-v15.json',M.A.BASE]})
 (O/'successor-services-CPU-v27.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','source_SavedY_uses']}))


if __name__=='__main__':main()
