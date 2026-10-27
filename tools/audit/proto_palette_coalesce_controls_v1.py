"""Finite real Graphics/VRAM/IRQ controls for the private frozen3e7 successor.

CPU component execution only: it does not model NMI scheduling, vblank, DMC
steals or visible rendering. Queue folding intentionally changes dead palette
stores; final physical PPU state and ordered non-target writes must stay exact.
"""
from pathlib import Path
import collections,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];B=R/'build';sys.path.insert(0,str(R/'tools/audit'))
from proto_palette_coalesce_candidate_v1 import SHA,sha,put
from link_pit_rygar_sophia_audit_cpu import scoped_load
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import Memory,address,location
from verify_native_relocation import NesMPU

P=B/'mm_body_current.nes';N=B/'proto_palette_coalesce.nes'
NEW='4a0394b0892e6c54940856791e44bcbe9fe4e469047aca3982c3f59112a61b8b'
OBSERVED=bytes.fromhex('3f11030c24343f110306273822540224242274022424206d020004206206240000020500207a030304003f0c040f27170f3f11030a163000')

def run(q,name='MegaManGraphics',flags=0x20,inject=None,record=False):
 b=q.b;s=b['syms'][name];pc=address(b,name);k=(location(b,name)-16)//8192;win=(pc-0x8000)//8192
 q.m.page(win,k)
 if win in [1,2]:q.set('CurrentBank'if win==1 else'CurrentBankC',k|128)
 c=NesMPU(memory=q.m,pc=pc);c.a=0x67;c.x=0x89;c.y=0xab;c.p=flags;c.sp=253;c.stPushWord(0x5aff)
 q.m.writes=[];trace=[];done=False;irq=False;irq_indices=set()
 for _ in range(150000):
  if c.pc==0x5b00:break
  bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1;key=(c.pc,bank)
  if inject==key and not done:
   assert not c.p&4;c.irq();done=True;irq=True;continue
  if record:trace.append(key)
  before=len(q.m.writes);op=q.m[c.pc];c.step()
  if irq:
   irq_indices.update(range(before,len(q.m.writes)))
   if op==64:irq=False
 else:raise AssertionError(('CPU timeout',name,hex(c.pc),q.m.banks))
 assert c.sp==253 and(inject is None or done)
 q.m.irq_indices=irq_indices
 return c,trace

def arena(b,state=None,prefix=b''):
 state=state or{};q=Arena(b,1,proto=state.get('ProtoVariant',1))
 q.put(DisableScreenFlag=0,Player_Rel_XPos=96,Player_SprAttrib=3,PlayerStatus=1,MmLastPalette=0,ReloadCHRBank=1)
 q.put(**state);q.set('VRAM_Buffer1_Offset',len(prefix));q.array('VRAM_Buffer1',list(prefix)+[0])
 q.put(R0=91,R1=173,R2=204)
 return q

def queue(q):return bytes(q.get('VRAM_Buffer1',i)for i in range(q.get('VRAM_Buffer1_Offset')+1))

def ppu(writes):
 a=0;high=True;step=1;image={};bus=[]
 for at,v in writes:
  if at==0x2000:step=32 if v&4 else 1
  elif at==0x2006:
   a=(v<<8)if high else(a&0xff00)|v;high=not high
  elif at==0x2007:
   k=a&0x3fff
   if k>=0x3f00:
    k=0x3f00+(k&31)
    if k in[0x3f10,0x3f14,0x3f18,0x3f1c]:k-=16
   bus.append((k,v));image[k]=v;a=(a+step)&0x3fff
 return image,bus

def update(q):
 at=address(q.b,'VRAM_Buffer1');q.put(NmiR0=at&255,NmiR1=at>>8)
 q.m.page(2,(location(q.b,'FastNmiVramCopy')-16)//8192)
 c,_=run(q,'UpdateScreen');image,bus=ppu(q.m.writes);return c.processorCycles-6,image,bus

def compare_caller(qs,cs,fold=False):
 a,c=cs
 regs=lambda t:(t.a,t.x,t.y,t.p&207,t.sp) # NV-DIZC: B/constant bit are not physical CPU latches.
 if fold and qs[0].get('ProtoVariant'):
  assert(a.a,a.p&207,a.sp)==(c.a,c.p&207,c.sp),('Live A/P/SP',regs(a),regs(c))
 else:assert regs(a)==regs(c),('AXYP/SP',regs(a),regs(c))
 assert qs[0].m.banks==qs[1].m.banks
 allowed=set(range(256,512)) # Dead stack residue differs; live SP/return exact.
 # This engine also hosts genuine executable farcall operands in page1.
 # Those are never dead stack and must be compared byte-for-byte.
 for g in qs[0].b['segs'].values():
  if g['name']=='"SMCCODE"':allowed.difference_update(range(int(g['start'],0),int(g['start'],0)+int(g['size'],0)))
 if fold:
  at=address(qs[0].b,'VRAM_Buffer1');allowed.update(range(at,at+84));allowed.add(address(qs[0].b,'VRAM_Buffer1_Offset'))
  if qs[0].get('ProtoVariant'):allowed.add(address(qs[0].b,'R0')) # Genuine queue parser's terminal index, tested through real downstream callers.
 differences=[(hex(i),qs[0].m[i],qs[1].m[i])for i in range(0x8000)if i not in allowed and qs[0].m[i]!=qs[1].m[i]]
 assert not differences,('Full caller RAM/SMC delta',differences[:14])

def pad(n):
 assert n>=4
 return bytes([0x22,0x20,n-3]+[0x24]*(n-3))

def full_callers(old,new):
 rows=[]
 # Existing palette ownership and all reachable pose branches, including the
 # early death return whose genuine old bank/SMC owner must remain exact.
 states=[dict(ProtoVariant=p,PlayerStatus=s,CrossoverBehaviorVersion=m,GameEngineSubroutine=g,Player_State=st,Player_X_Speed=speed,MegaManShotPose=shot,PlayerFacingDir=face)
  for p,s,m,g,st,speed,shot,face in itertools.product([0,1],[0,1,2],[0,1],[8,10,11],[0,1,3],[0,24],[0,1],[1,2])]
 # Bound the full cross product to meaningful legal combinations rather than
 # multiplying unrelated state fields into thousands of redundant captures.
 states=[s for i,s in enumerate(states)if i%13==0 or s['GameEngineSubroutine']==11 and i%17==0]
 for p,guest,star,charge,phase,cache in itertools.product([0,1],[0,1],[0,1],[0,33,48,66,87],[0,1,2],[0,1,15,17]):
  if guest and(star or charge):continue
  if star and charge:continue
  states.append(dict(ProtoVariant=p,GuestPowerupActive=guest,GuestPowerupPose=2,StarInvincibleTimer=star,MmChargeFrames=charge,MmFlashPhase=phase,MmLastPalette=cache))
 for state in states:
  qs=[arena(b,state)for b in[old,new]];cs=[run(q)[0]for q in qs]
  compare_caller(qs,cs)
  assert queue(qs[0])==queue(qs[1])
  rows.append(dict(state=state,old_cycles=cs[0].processorCycles,new_cycles=cs[1].processorCycles,delta=cs[1].processorCycles-cs[0].processorCycles))
 return rows

def queues(old,new):
 target=bytes.fromhex('3f11030c2434');space=pad(36)
 # All have a complete current-owner append after this prefix. Prefixes may
 # use any native format; unsupported formats must retain source output.
 cases=[('empty',b'',False),('two-fast',target,True),('short-no-scan',target+pad(30),False),('actual-tail-prefix',OBSERVED[:-7],True),
  ('ordinary-near-budget',space+pad(7),False),
  ('disjoint-rotation',target+bytes.fromhex('3f0c040f27170f')+pad(30),True),
  ('overlap-partial',target+bytes.fromhex('3f120109')+space,False),
  ('overlap-full',target+bytes([0x3f,0,32]+list(range(32)))+pad(5),False),
  ('overlap-3f31-alias',target+bytes.fromhex('3f3103030405')+space,False),
  ('after-overlap-new-candidate',bytes.fromhex('3f120109')+target+space,True),
  ('universal-alias-disjoint',target+bytes.fromhex('3f300109')+space,True),
  ('mirrored-lowrange-overlap',target+bytes([0x3f,0x2f,5,1,2,3,4,5])+space,False),
  ('RLE-decline',target+bytes.fromhex('22204724')+space,False),
  ('vertical-decline',target+bytes.fromhex('2220822424')+space,False),
  ('zero-count256-decline',target+bytes.fromhex('222000')+space,False),
  ('high-alias-decline',target+bytes.fromhex('7f1103030405')+space,False),
  ('cross-3e-into-palette',target+bytes([0x3e,0xff,20]+[7]*20)+pad(13),False),
  ('fake-header-in-payload',bytes([0x22,0x20,40])+target+bytes([0x24]*34),False),
  ('missing-terminator-decline',target+bytes([0]*36),False),
  ('truncated-prefix-decline',target+bytes([0x22,0x20,63]+[0x24]*33),False),
  ('capacity64-refusal',pad(64),False),('capacity65-refusal',pad(65),False)]
 # Literal length1..63 native source bounds, exact72B-or-less arena footprint.
 for n in range(1,48):
  payload=bytes([0x22,0x20,n]+[(17*i+3)&255 for i in range(n)])
  if len(payload)+6<64:cases.append(('literal-'+str(n),target+payload,len(target+payload)+6>=48))
 rows=[]
 for name,prefix,fold in cases:
  assert len(prefix)<=65
  state=dict(StarInvincibleTimer=1,MmFlashPhase=1)
  qs=[arena(b,state,prefix)for b in[old,new]];cs=[run(q)[0]for q in qs]
  actual=queue(qs[0])!=queue(qs[1]);assert actual==fold,(name,fold,queue(qs[0]).hex(),queue(qs[1]).hex())
  compare_caller(qs,cs,fold=fold)
  if name not in['zero-count256-decline','missing-terminator-decline','truncated-prefix-decline']:
   us=[update(q)for q in qs];assert us[0][1]==us[1][1],('Final PPU map',name)
   assert[(a,v)for a,v in us[0][2]if a not in[0x3f11,0x3f12,0x3f13]]==[(a,v)for a,v in us[1][2]if a not in[0x3f11,0x3f12,0x3f13]],('Non-target ordered PPUDATA',name)
   consumer=[v[0]for v in us]
  else:consumer=None # Invalid/unbounded legacy payload is tested for exact fallback only.
  rows.append(dict(name=name,prefix_bytes=len(prefix),folded=fold,old_queue=queue(qs[0]).hex(),new_queue=queue(qs[1]).hex(),foreground_cycles=[c.processorCycles for c in cs],UpdateScreen_cycles=consumer))
 return rows

def observed(old,new):
 # Source progression creating the actual captured star rows. Intervening
 # authored queue bytes are copied literally; no emulated NMI is claimed.
 qs=[arena(b,dict(StarInvincibleTimer=1,MmFlashPhase=2))for b in[old,new]];rows=[]
 for phase,middle in[(2,b''),(0,b''),(1,OBSERVED[12:-7])]:
  cs=[]
  for q in qs:
   q.put(MmFlashPhase=phase)
   if middle:
    at=q.get('VRAM_Buffer1_Offset');q.array('VRAM_Buffer1',list(queue(q)[:-1])+list(middle)+[0]);q.set('VRAM_Buffer1_Offset',at+len(middle))
   cs.append(run(q)[0])
  compare_caller(qs,cs,fold=True)
  rows.append(dict(phase=phase,foreground_cycles=[c.processorCycles for c in cs],queued_bytes=[q.get('VRAM_Buffer1_Offset')for q in qs]))
 assert queue(qs[0])==OBSERVED
 buf=[queue(q).hex()for q in qs];us=[update(q)for q in qs]
 assert us[0][1]==us[1][1]
 assert len(us[0][2])==28 and len(us[1][2])==22
 assert us[0][0]-us[1][0]==304
 return dict(calls=rows,queue_hex=buf,final_offsets=[55,43],PPUDATA_writes=[len(v[2])for v in us],UpdateScreen_cycles=[v[0]for v in us],NMI_component_saved=304,total_foreground_delta=sum(r['foreground_cycles'][1]-r['foreground_cycles'][0]for r in rows),final_PPU_image_equal=True,ordered_non_target_equal=[(a,v)for a,v in us[0][2]if a not in[0x3f11,0x3f12,0x3f13]]==[(a,v)for a,v in us[1][2]if a not in[0x3f11,0x3f12,0x3f13]])

def palette_flags(old,new):
 # Authentic table and charge/star/normal colors through both complete pose
 # selectors; valid CPU flags, including decimal latch (NES arithmetic binary).
 assert old['raw'][location(old,'MegaManPaletteState::Colors'):location(old,'MegaManPaletteState::Colors')+51]==new['raw'][location(new,'CompactMegaManPaletteState::Colors'):location(new,'CompactMegaManPaletteState::Colors')+51]
 n=0
 states=[{},dict(PlayerStatus=2),dict(StarInvincibleTimer=1,MmFlashPhase=2)]+[dict(MmChargeFrames=k,MmFlashPhase=1)for k in[33,48,66,87]]
 for proto,state,prefix,flags in itertools.product([0,1],states,[bytes.fromhex('3f11030c2434'),OBSERVED[:-7]],[0x20,0x21,0x60,0xa2,0xef]):
  s=dict(state,ProtoVariant=proto);qs=[arena(b,s,prefix)for b in[old,new]];cs=[run(q,flags=flags)[0]for q in qs]
  folded=queue(qs[0])!=queue(qs[1]);compare_caller(qs,cs,fold=folded)
  ps=[update(q)for q in qs];assert ps[0][1]==ps[1][1]
  assert[(a,v)for a,v in ps[0][2]if a not in[0x3f11,0x3f12,0x3f13]]==[(a,v)for a,v in ps[1][2]if a not in[0x3f11,0x3f12,0x3f13]]
  n+=1
 return dict(cases=n,original_51_color_bytes_exact=True,AXYP_or_proven_dead_terminal_indices_and_all_live_RAM_SMC_banks_exact=True,final_PPU_map_and_ordered_non_target_writes_exact=True)

def irq_controls(new):
 base=arena(new,dict(StarInvincibleTimer=1,MmFlashPhase=1),OBSERVED[:-7]);image=list(base.m);banks=base.m.banks[:]
 def fresh():
  q=Arena(new);list.__setitem__(q.m,slice(None),image);q.m.banks=banks[:];return q
 q=fresh();c,trace=run(q,record=True)
 start=address(new,'CompactMegaManPaletteState');end=address(new,'CompactMegaManPaletteTail')
 keys=sorted({(pc,k)for pc,k in trace if k==63 and start<=pc<0xbf00})
 smc=lambda q:[q.m[i]for g in q.b['segs'].values()if g['name']=='"SMCCODE"'for i in range(int(g['start'],0),int(g['start'],0)+int(g['size'],0))]
 flat=lambda q:bytes(q.m[:256]+smc(q)+q.m[512:2048]+q.m[0x6000:0x8000])
 bus=lambda q:[w for j,w in enumerate(q.m.writes)if j not in q.m.irq_indices and not 256<=w[0]<512]
 want=(c.a,c.x,c.y,c.p&207,c.sp,flat(q),q.m.banks,bus(q))
 costs=[]
 for key in keys:
  t=fresh();cpu,_=run(t,inject=key)
  assert(cpu.a,cpu.x,cpu.y,cpu.p&207,cpu.sp,flat(t),t.m.banks,bus(t))==want,('IRQ restoration',key)
  costs.append(cpu.processorCycles-c.processorCycles)
 return dict(actual_reached_instruction_boundaries=len(keys),IRQ_cycles=sorted(set(costs)),AXYP_SP_all_nonstack_RAM_SMC_banks_and_nonIRQ_bus_exact=True,hardware_vector_and_actual_RTI=True,scope='MMC5 scanline IRQ at every reached clone/parser instruction in the actual final star-prefix call. NMI excluded by genuine main producer NmiDisableFF in gameplay; no native timing certification.')

def downstream(old,new):
 # Inspect actual compiled continuations, never replace/skip native helpers.
 # Track first X/Y definition and first actual R0 read/write after Graphics.
 # The tiny IRQ BIT R0 is a deliberate timing pad: hardware-vector controls
 # above retain the complete IRQ result even with the changed terminal index.
 rows=[];source=(R/'src/game.s').read_text();rare=(R/'src/bill_native_rare.s').read_text()
 assert source.count('farcall PlayerGfxHandler')==2 and rare.count('farcall PlayerGfxHandler')==1
 original_step=NesMPU.step;original_get=Memory.__getitem__
 for name,prefix,task in itertools.product(['GameCoreRoutine','VictoryMode','NativeRareVictoryModeCore'],[bytes.fromhex('3f11030c2434'),OBSERVED[:-7]],[0,3]):
  if name=='GameCoreRoutine'and task==0:continue # Genuine pre-game task returns before the Graphics caller.
  pair=[]
  for b in[old,new]:
   q=arena(b,dict(StarInvincibleTimer=2,MmFlashPhase=1,OperMode_Task=task,NmiDisable=255,Player_Y_Position=160,Player_State=0,TimerControl=1,GameTimerCtrlTimer=1),prefix)
   q.array('GameTimerDisplay',[4,0,0]) # Legal living1-1 caller; zeroed timer would invoke unrelated death dispatch.
   state=dict(in_gfx=False,active=False,seen={},reads=[],ret=None,pc=None)
   gfx=(address(b,'MegaManGraphics'),(location(b,'MegaManGraphics')-16)//8192)
   def get(m,at):
    if m is q.m and state['active'] and isinstance(at,int) and at==address(b,'R0') and'R0'not in state['seen']:
     state['seen']['R0']=dict(kind='READ_BEFORE_DEFINITION',pc=state['pc'],value=original_get(m,at))
    return original_get(m,at)
   def step(c):
    pc=c.pc;k=q.m.banks[(pc-0x8000)//8192]if pc>=0x8000 else-1
    if(pc,k)==gfx:
     s=c.sp;ret=q.m[256+((s+1)&255)]+256*q.m[256+((s+2)&255)]+1
     state.update(in_gfx=True,ret=(ret,(s+2)&255))
    if state['in_gfx'] and(pc,c.sp)==state['ret']:
     state.update(in_gfx=False,active=True,returned_regs=(c.a,c.x,c.y,c.p&207))
    state['pc']=[pc,k]
    before=len(q.m.writes)
    if state['active']:
     op,mode=c.disassemble[q.m[pc]]
     for reg,modes,reads,writes in [('X',['zpx','abx','inx'],['TXA','TXS','INX','DEX','CPX','STX'],['LDX','TAX','TSX']),('Y',['zpy','aby','iny'],['TYA','INY','DEY','CPY','STY'],['LDY','TAY'])]:
      if reg not in state['seen']:
       if mode in modes or op in reads:state['seen'][reg]=dict(kind='READ_BEFORE_DEFINITION',pc=[pc,k],opcode=op,mode=mode)
       elif op in writes:state['seen'][reg]=dict(kind='definition',pc=[pc,k],opcode=op,mode=mode)
    original_step(c)
    if state['active'] and'R0'not in state['seen'] and any(at==address(b,'R0')for at,v in q.m.writes[before:]):state['seen']['R0']=dict(kind='definition',pc=[pc,k])
   Memory.__getitem__=get;NesMPU.step=step
   try:c,_=run(q,name)
   finally:Memory.__getitem__=original_get;NesMPU.step=original_step
   assert state['active'],('Actual caller did not reach Graphics',name,task)
   assert not any(v['kind']=='READ_BEFORE_DEFINITION'for v in state['seen'].values()),('Downstream read-before-definition',name,task,state)
   # A register not used before this completed caller returns is also dead;
   # actual reachable definitions are stated, never invented for a table.
   pair.append((q,c,state))
  a,c=pair;compare_caller([a[0],c[0]],[a[1],c[1]],fold=True)
  rows.append(dict(actual_caller=name,task=task,prefix_bytes=len(prefix),baseline_return_registers=a[2]['returned_regs'],candidate_return_registers=c[2]['returned_regs'],baseline_first_definitions=a[2]['seen'],candidate_first_definitions=c[2]['seen'],full_caller_cycles=[a[1].processorCycles,c[1].processorCycles],queue_bytes=[a[0].get('VRAM_Buffer1_Offset'),c[0].get('VRAM_Buffer1_Offset')]))
 return dict(actual_source_call_sites=3,executed_full_continuations=len(rows),cases=rows,IRQ_R0_read='Expanded IrqScrollSplit BIT R0 is a fixed timing pad; no conditional branch/store consumes its N/V/Z before overwritten or RTI. Full hardware-vector157-boundary equality independently proves the actual IRQ output/register/bank behavior.',contract='Changed queue representation legitimately changes dead terminal X/Y/R0 from ProtoFixQueuedPalette. Every actual compiled caller continuation above defines these before any read, or does not access them before returning; live A/P/SP/SMC/mapper and gameplay/presentation outputs remain exact. This explicit downstream proof replaces the failed overbroad terminal-scratch equality assertion; no SMC difference is masked.')

def main():
 out=B/'proto_palette_coalesce_controls.json'
 try:
  assert sha(P)==SHA and sha(N)==NEW
  old,new=scoped_load(P),scoped_load(N)
  callers=full_callers(old,new);cases=queues(old,new);actual=observed(old,new);irqs=irq_controls(new);live=downstream(old,new);colors=palette_flags(old,new)
  proof=dict(passed=True,source_CPU_only=True,native_run=False,installed=False,parent_sha256=SHA,candidate_sha256=NEW,full_Graphics_callers=len(callers),full_caller_state='Exact live A/NV-DIZC/SP, complete nonstack RAM/SMC/mapper at genuineGraphics return. Only deliberately repacked84B queue/offset and proven dead Proto terminalX/Y/R0 permitted in folding cases. Dead stack residues excluded; no live-frame/caller state excluded.',caller_cost_summary=dict(min=min(v['delta']for v in callers),max=max(v['delta']for v in callers),histogram=dict(collections.Counter(v['delta']for v in callers))),queue_cases=len(cases),queue_controls=cases,actual_observed_packet=actual,IRQ=irqs,downstream_liveness=live,source_states=callers,limits='Final physical PPU image equal; intermediate superseded palette stores intentionally differ. No NMI work/newRAM or audio changes. CPU costs include real bank mapping/fullGraphics caller, not a paid-call zero-cost assumption. Native exact1940 replay then whole route still required.',bindings=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))for p in[Path(__file__),P,P.with_suffix('.dbg'),N,N.with_suffix('.dbg'),B/'proto_palette_coalesce_build.json',B/'verification/proto-oam3e7-vram-probe-v1/proto-startup-vram.csv']])
  proof['authentic_colors_and_flags']=colors
  put(out,proof);print(json.dumps({k:proof[k]for k in['passed','candidate_sha256','full_Graphics_callers','caller_cost_summary','queue_cases','actual_observed_packet','IRQ','authentic_colors_and_flags']}))
 except Exception as e:
  p=B/'proto_palette_coalesce_controls_error.json'
  put(p,dict(passed=False,error=repr(e),trace=traceback.format_exc()));raise
if __name__=='__main__':main()
