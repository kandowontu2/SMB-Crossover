"""Bounded current14b DK forwarding source qualification; no output files.

Use run_bounded_build_v1.py with an absent output root. It validates exact
current linked machine code and real ISR continuations, not native cadence.
The embedded receipt names the earlier in-memory proof of these same bytes.
"""

import sys,json,hashlib,time
from pathlib import Path
from collections import Counter
from unittest.mock import patch
sys.path[:0]=[str(Path.cwd()/'tools/audit'),str(Path.cwd()/'tools/reference')]
import compose_dkjr_sonic_dispatch_1123 as C
import check_dkjr_sonic_dispatch_1123 as Q
import measure_battletoads_passthrough_fit_1114 as Fit
import check_shared_side_tank_precheck_1110 as Side
import check_mega_giant_resident_1110 as Audio
from check_mini_funded_actor_1108_v3 import registers,live_stack
from py65.devices.mpu6502 import MPU
N,W,B=Q.N,Q.W,Q.B
H=lambda b:hashlib.sha256(b).hexdigest()
off=C.S.off
REFERENCE_HOST_RECEIPT='5b4d267d5f3b8a17bb56d53e1bc599c0720a4b2bba8b3374c3e0ac4e966e4385'
import compose_dkjr_public_side_forward_1123 as F
started=time.monotonic()
def report(stage,**kw):print(json.dumps(dict(stage=stage,seconds=round(time.monotonic()-started,2),**kw),separators=(',',':')),flush=True)
def deny(*a,**k):raise AssertionError('No output or subprocess allowed')

def qualify(parent):
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
     installed=parent
     assert H(installed)==F.PIN
     combined=installed;parent=C.inverse(installed)
     candidate,composition=F.proposal(combined)
     assembled=F.program();oldside=F.OLD_SIDE
     assert oldside==Fit.side()[0]
     result=dict(installed=H(installed),parent287=H(parent),parent14b=H(combined),
      candidate14b=H(candidate),source_SHA256=F.SOURCE_SHA256,
      side_SHA256=H(assembled['images']['SIDE']),tail_SHA256=H(assembled['images']['TAIL']),
      changed_bytes=composition['changed_bytes'],
      owned_spans=[[off(33,0xbea2),94],[off(33,0xbf99),28]],
      retained_Giant153_exact=True,side_labels=assembled['symbols'],
      reference_host_receipt=REFERENCE_HOST_RECEIPT,
      bindings={Path(q).name:H(Path(q).read_bytes()) for q in (F.__file__,__file__)})
     report('composition',**result)
     # Detached exhaustive foreign owner/status and both typed raw0 predicate outcomes.
     memories=[]
     for index,code in enumerate((oldside,assembled['images']['SIDE'])):
      mem=[0]*65536;mem[0xbea2:0xbf00]=code
      if index:mem[0xbf99:0xbfb5]=assembled['images']['TAIL']
      memories.append(mem)
     units=0
     for owner in range(256):
      if owner==40:continue
      for status in range(32,256):
       if not status&32:continue
       for admitted in ((False,True) if owner==0 else (False,)):
        outcomes=[]
        for mem in memories:
         mem[0x6002]=owner;mem[0x16a]=85;mem[0x162]=0;mem[0x179]=0
         c=MPU(memory=mem,pc=0xbea2);c.a,c.x,c.y,c.p,c.sp=85,7,91,status,236;c.stPushWord(0x5aff)
         callbacks=0
         for _ in range(120):
          if c.pc==0xbf38:break
          if c.pc==0x15a:
           target=mem[0x16c]+256*mem[0x16d]
           if target!=0xbfb0:break
           c.a=mem[0x16a];c.p=(c.p&~1)|int(admitted);c.pc=c.stPopWord()+1;callbacks+=1;continue
          c.step()
         else:raise AssertionError(('detached bound',owner,status,c.pc))
         outcomes.append((c.pc,*registers(c,0xef),bytes(mem[0x101+c.sp:0x200]),mem[0x16a],mem[0x16c],mem[0x16d],mem[0x162],mem[0x179],callbacks))
        assert outcomes[0]==outcomes[1],('foreign detached',owner,status,admitted,outcomes)
        units+=1
     result['foreign_detached']=units;report('foreign_detached',cases=units)
     basebundle=W.Symbols.bundle()
     def bundle(raw):return dict(basebundle,raw=raw)
     def rebound(c,raw):
      z=Q.clone(c);m=z.memory;m.bundle=dict(m.bundle,raw=raw)
      for window,tag in enumerate(tuple(m.rawtags)):
       if tag&128:m.raw_page(window,tag)
      W.clear_logs(m);return z
     def native_state(m):
      return (bytes(m[:0x100]),bytes(m[0x200:0x800]),bytes(m[0x5c00:0x8000]),tuple(map(bytes,m.ram)),tuple(m.rawtags),tuple(m.chr_latches),bytes(m.vram),m.ppuctrl,m.ppu_addr,m.toggle,m.buffer,m.upper,m.lastset,tuple(m.protection))
     def equal(a,b,label):
      assert registers(a,0xef)==registers(b,0xef),(label,'regs',registers(a),registers(b))
      assert live_stack(a)==live_stack(b),(label,'live stack')
      sa,sb=native_state(a.memory),native_state(b.memory)
      if sa!=sb:raise AssertionError((label,'native state sections',[i for i,(x,y) in enumerate(zip(sa,sb)) if x!=y]))
     def finish(c,stop,watch=None):
      for _ in range(300000):
       if (c.pc,c.sp)==stop:return
       if watch:watch(c)
       assert c.memory[c.pc],('BRK',hex(c.pc),c.memory.rawtags,c.sp)
       c.step()
      raise AssertionError(('actual side bound',hex(c.pc),c.sp,stop))
     seed=Q.enter(combined,'DK')
     for cold in range(300):
      if tuple(N.get(seed,n) for n in ('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
      B.main_step(seed,0)
     else:raise AssertionError('DK cold bound')
     for _ in range(4):B.main_step(seed,0)
     captured=[]
     class Capture:
      def run(self,c,stop):
       def watch(q):
        if q.pc==0x90e4 and q.memory.rawtags[0]==254:captured.append(Q.clone(q))
       finish(c,stop,watch)
     B.main_step(seed,0,Capture())
     assert len(captured)==4 and {c.y for c in captured}=={17,18,19,20}
     report('DK_real_probes',cold_Main_returns=cold,probes=[(c.a,c.x,c.y,c.sp,c.memory.rawtags) for c in captured])
     cuts={};timings=Counter();dcases=0;rejected=0
     def point(c):return (c.memory.rawtags[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1,c.pc)
     def collect(c,stop,label):
      tag,pc=point(c)
      if tag==161 and (0xbea2<=pc<0xbf00 or 0xbf99<=pc<0xbfb5) or pc in (0x15a,0x15d,0x16b,0x16e,0x174,0x17a):
       key=(tag,pc,c.sp,c.p&5)
       if key not in cuts:
        z=Q.clone(c);z.memory.combined_terminal=stop;cuts[key]=z
     def end(c):return ((c.memory[0x101+c.sp]+256*c.memory[0x102+c.sp]+1)&65535,c.sp+2)
     def query(original,raw,change=None,trace=False):
      c=rebound(original,raw);m=c.memory
      if change:change(m)
      stop=end(c);counts=Counter()
      def watch(q):
       tag,pc=point(q)
       if (tag,pc)==(193,0xb0b6):counts['public14']+=1
       if (tag,pc)==(193,0xaf27):counts['full_header']+=1
       if (tag,pc)==(213,0xa8dc):counts['quick']+=1
       if (tag,pc)==(254,0x958b):counts['native958B']+=1
       if trace:collect(q,stop,'DK')
      finish(c,stop,watch);return c,counts
     mutations=[('normal',None),('zero_epoch',lambda m:m.ram[2].__setitem__(0x8ff,0)),('stale_epoch',lambda m:m.ram[2].__setitem__(0x8ff,(m[0xe]-1)&255)),('zero_frame',lambda m:N.put(m,FrameCounter=0)),('engine7',lambda m:N.put(m,GameEngineSubroutine=7)),('pause',lambda m:N.put(m,GamePauseStatus=1)),('timer',lambda m:N.put(m,TimerControl=1))]
     for bank in (2,3):
      for ix in range(16):
       def corrupt(m,bank=bank,ix=ix):m.ram[bank][0x1fe0+ix]^=1;m.ram[2][0x8ff]=0
       mutations.append(('full_bad_%d_%d'%(bank,ix),corrupt))
      for ix in (0,1):
       def prefix(m,bank=bank,ix=ix):m.ram[bank][0x1fe0+ix]^=1
       mutations.append(('prefix_bad_%d_%d'%(bank,ix),prefix))
     for original in captured:
      for label,change in mutations:
       a,ac=query(original,combined,change);b,bc=query(original,candidate,change,label in ('normal','full_bad_2_0'))
       equal(a,b,('DK',original.y,label));assert ac==bc,('DK actual callbacks',original.y,label,ac,bc)
       if 'bad_' in label:assert not b.p&1 and bc['native958B']==0,(label,registers(b),bc);rejected+=1
       if label=='normal':assert bc['public14']==bc['native958B']==bc['quick']==1 and bc['full_header']==0;timings[a.processorCycles-b.processorCycles]+=1
       dcases+=1
     result['DK_queries']=dict(cases=dcases,rejected_header_cases=rejected,normal_cycles_saved=dict(timings));report('DK_public_carry',**result['DK_queries'])
     defaults=N.fresh(bundle(combined));fcases=0;foreign_timing=Counter()
     for owner in range(256):
      if owner==40:continue
      for tile in (0,0x54,0xc3):
       original=Side.new_leaf(defaults,owner,owner&7,8,17,253,176,tile,0x21)
       a=rebound(original,combined);b=rebound(original,candidate);stop=end(a)
       finish(a,stop);finish(b,stop,lambda q:collect(q,stop,'foreign'))
       equal(a,b,('foreign actual',owner,tile));foreign_timing[a.processorCycles-b.processorCycles]+=1;fcases+=1
     result['foreign_actual']=dict(cases=fcases,cycle_delta=dict(foreign_timing));report('foreign_actual',**result['foreign_actual'])
     audio_seeds=[N.fresh(bundle(r)) for r in (combined,candidate)];audio_cases=0
     for value in range(256):
      for p in (0x20,0x21,0x60,0x65,0x2c,0xe9):
       outcomes=[Audio.call_audio(m,0x87,value,0,p)[0] for m in audio_seeds]
       assert outcomes[0]==outcomes[1],('canonical Rogue reader',value,p,outcomes)
       expected=combined[off(33,0xbf14)+value] if value<36 else 0
       assert outcomes[1][4]==expected,(value,p,outcomes,expected)
       audio_cases+=1
     result['Giant_reader_actual']=audio_cases;report('Giant_reader',cases=audio_cases)
     giant_cases=0
     for tile in range(256):
      for p in (0x21,0x60,0x65,0xa5):
       original=Side.new_leaf(defaults,0,9,8,17,253,176,tile,p)
       a=rebound(original,combined);b=rebound(original,candidate);stop=end(a)
       finish(a,stop);finish(b,stop,lambda q:collect(q,stop,'Giant'))
       equal(a,b,('Giant tile',tile,p));giant_cases+=1
     result['Giant_leaf_actual']=giant_cases;report('Giant_leaf',cases=giant_cases,cuts=len(cuts))

     # Paired genuine cold constructors and ordinary Main, preserving all source state.
     profiles=[]
     for owner in ('DK','Sonic','Super','Mini'):
      machines=[Q.enter(raw,owner) for raw in (combined,candidate)]
      for cold_index in range(300):
       ready=[tuple(N.get(m,n) for n in ('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8) for m in machines]
       assert ready[0]==ready[1],('cold readiness',owner,cold_index)
       if all(ready):break
       for m in machines:B.main_step(m,0)
       assert native_state(machines[0])==native_state(machines[1]),('cold native',owner,cold_index)
      else:raise AssertionError(('paired cold bound',owner))
      phases={}
      for phase,pad,returns in (('settle',0,4),('idle',0,4),('Right',1,8)):
       savings=[];positions=[]
       for _ in range(returns):
        totals=[B.main_step(m,pad)[0] for m in machines]
        assert native_state(machines[0])==native_state(machines[1]),('paired Main state',owner,phase)
        savings.append(totals[0]-totals[1])
        positions.append((N.get(machines[1],'Player_X_Position')+256*N.get(machines[1],'Player_PageLoc'),N.get(machines[1],'Player_Y_Position')))
       phases[phase]=dict(returns=returns,saved_cycles=sorted(set(savings)),final_position=positions[-1])
      profiles.append(dict(owner=owner,cold_Main_returns=cold_index,phases=phases))
      report('paired_Main',**profiles[-1])
     result['paired_profiles']=profiles
     required={i['pc'] for i in assembled['instructions'] if i['segment']=='TAIL'}|{0xbed1,0xbed3,0xbed5,0xbefd}
     covered={key[1] for key in cuts};eligible={key[1] for key in cuts if not key[3]&4}
     assert required<=covered and required<=eligible,('new instruction IRQ closure',sorted(required-covered),sorted(required-eligible))
     result['all_tail_and_new_ingress_instructions_reached_and_IRQ_eligible']=sorted(required)

     counts=Counter();minimum=255
     for original in cuts.values():
      for kind in ('IRQ','busyNMI'):
       if kind=='IRQ' and original.p&4:continue
       a,b=Q.clone(original),Q.clone(original)
       for c in (a,b):N.put(c.memory,NmiDisable=255)
       before=(b.pc,b.sp,registers(b,0xef));stack=live_stack(b);private=tuple(map(bytes,b.memory.ram));smc=bytes(b.memory[0x15a:0x17b])
       if kind=='IRQ':b.irq()
       else:b.nmi()
       finish(b,(before[0],before[1]));minimum=min(minimum,b.sp)
       assert registers(b,0xef)==before[2] and live_stack(b)==stack,(kind,'changed relocated return',before,registers(b))
       assert tuple(map(bytes,b.memory.ram))==private and bytes(b.memory[0x15a:0x17b])==smc,(kind,'changed private or SMC',before)
       terminal=original.memory.combined_terminal
       for c in (a,b):finish(c,terminal)
       assert registers(a,0xef)==registers(b,0xef) and live_stack(a)==live_stack(b),(kind,'continuation registers',before)
       assert tuple(map(bytes,a.memory.ram))==tuple(map(bytes,b.memory.ram)),(kind,'continuation WRAM',before)
       assert tuple(a.memory.rawtags)==tuple(b.memory.rawtags) and tuple(a.memory.chr_latches)==tuple(b.memory.chr_latches),(kind,'mapping',before)
       assert Q.Old.state(a.memory)==Q.Old.state(b.memory),(kind,'native continuation',before)
       counts[kind]+=1
     result['interrupts']=dict(cuts=len(cuts),cases=dict(counts),minimum_return_SP=minimum,hardware_status_mask='EF; synthetic internal Break excluded')
     result.update(passed=True,outputs=0,Mesen=False,production_source_unchanged=True,scope='Detached all foreign owner/status; actual current combined DK four naturally reached side probes plus fault paths; actual foreign fixtures; retained Giant reader and leaf; native ISR return and continuation. Paired real-cold and ordinary Main for DK, Sonic, Super and Mini. Not physical cadence or full route.')
     result['receipt_SHA256']=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
     report('PASS',**result)
     return result


if __name__=='__main__':
    qualify(F.M.ROM.read_bytes())
