"""Real current vectors at bounded WWF load/auth/retire/construct seams."""
from pathlib import Path
import hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import wwf_first_hogan_owner_controls_v1 as T
from ff_wram_host_isr_v4 import clone
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
H=T.H;J=T.J;O=R/'build/wwf-first-hogan-owner-isr-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
state=lambda c:(c.pc,c.a,c.x,c.y,c.p,c.sp)

def interrupt(m,c,kind):
 b=m.bundle;before=(state(c),m.rawtags[:],[H.get(m,n)for n in ['CurrentBank','CurrentBankC']],bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]),bytes(m[:256]),[bytes(x)for x in m.ram]);expected=m.rawtags[:]
 if kind=='NMI':
  for slot,name,tail in[(1,'CurrentBank',b'\x15\x51'),(2,'CurrentBankC',b'\x16\x51')]:
   if expected[slot]!=H.get(m,name):
    op=bytes(m[c.pc:c.pc+3]);assert op in [b'\x8d'+tail,b'\x8e'+tail]
    assert(c.a if op[0]==0x8d else c.x)==H.get(m,name)
    expected[slot]=H.get(m,name)
  c.nmi()
 else:assert not c.p&4;c.irq()
 low=c.sp
 for steps in range(100000):
  if state(c)==before[0]:break
  assert m[c.pc]!=0,('real ISR BRK',kind,hex(c.pc),m.rawtags)
  low=min(low,c.sp);c.step()
 else:raise AssertionError(('ISR bound',kind,hex(c.pc)))
 assert m.rawtags==expected and [H.get(m,n)for n in ['CurrentBank','CurrentBankC']]==before[2]
 assert bytes(m[0x15a:0x17b])==before[3] and bytes(m[0x101+c.sp:0x200])==before[4]
 assert bytes(m[3:11])==before[5][3:11] and [bytes(x)for x in m.ram]==before[6]
 return low

def snapshots(b,name,loaded=False):
 m=T.make(b)
 if loaded:T.run(m,'WfLoad')
 m.raw_page(1,0xe0);H.put(m,CurrentBank=0xe0)
 c=NesMPU(memory=m,pc=address(b,name));c.a,c.x,c.y,c.p,c.sp=83,17,91,0x31,224;c.stPushWord(0x5aff)
 entries={address(b,n):n for n in ['WfLoad','WfCopyCore','WfCopyPage','WfVerifyPage','WfPublishCookie','WfReturnC','WfReturnOriginal','WfAuthC2','WfAuthByte','WfConstructCold','WfHostCold','WfRetire']}
 seen=set();out=[]
 for i in range(600000):
  if c.pc==0x5b00:break
  reason=None;op=bytes(m[c.pc:c.pc+3])
  if c.pc in entries:
   n=entries[c.pc]
   if n in ['WfCopyPage','WfVerifyPage']:
    if m[5]in[0,8,16,23]and c.x in[4,17]and c.y in[0,91]:reason=(n,m[5])
   elif n=='WfAuthByte':
    if c.x in[0,15]:reason=(n,c.x)
   else:reason=(n,c.x if n=='WfPublishCookie'else 0)
  if op in[b'\x8d\x15\x51',b'\x8d\x16\x51',b'\x8e\x15\x51']:
   reason=('pending-map',c.pc,c.x if op[0]==0x8e else c.a)
  if reason is not None and reason not in seen:
   seen.add(reason);out.append((reason,*clone(m,c)))
  assert m[c.pc]!=0;c.step()
 else:raise AssertionError(('discovery bound',name))
 return out

def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,source=True,native=False,no_host_hooks=True,rows=[])
 try:
  b=T.qualified(J/'candidate.nes');minsp=224;masked=0
  for name,loaded in [('WfLoad',False),('WfCheck',True),('WfConstructCold',True),('WfRetire',True)]:
   shots=snapshots(b,name,loaded)
   for reason,m,c in shots:
    # Accepted copying/constructing requires the actual negative NmiDisable
    # forced-blank interval. Do not fabricate a normal rendering NMI there.
    contexts=['lag']if name in['WfLoad','WfConstructCold']else['normal','lag','paused']
    for context in contexts:
     for kind in ['NMI','IRQ']:
      z,d=clone(m,c);H.put(z,NmiDisable=255 if context=='lag'else 0,GamePauseStatus=int(context=='paused'))
      if kind=='IRQ'and d.p&4:
       before=state(d);d.irq();assert state(d)==before;masked+=1;continue
      lo=interrupt(z,d,kind);minsp=min(minsp,lo)
      # Resume the real caller and prove actual source images/outcomes.
      for step in range(600000):
       if d.pc==0x5b00:break
       assert z[d.pc]!=0,('continued BRK',name,reason,context,kind,hex(d.pc));d.step()
      else:raise AssertionError(('continuation bound',name,reason))
      assert(d.a,d.x,d.y,d.sp)==(83,17,91,224)
      if name=='WfLoad':assert d.p&1;T.exact(z)
      if name=='WfConstructCold':assert d.p&1 and z.ram[2][address(b,'WfHostReady')-0xc000]==167
      if name=='WfCheck':assert d.p&1
      if name=='WfRetire':assert z.ram[2][0x1fe0]==z.ram[3][0x1fe0]==0
      q['rows'].append(dict(API=name,reason=reason,context=context,vector=kind,minimum_SP=lo))
  q.update(passed=True,real_cuts=len(q['rows']),masked_IRQ_requests=masked,minimum_SP=minsp,pending_map_rule='Only actual STA/STX5115/5116 with source register equal to shadow; native NMI completes that pending publication. No mapper/opcode/CPU normalization.',accepted_loader_NMI_scope='Actual forced-blank negative-NmiDisable lag path; normal/pausedNMI exercised on pure auth/retire, not fabricated during copying.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  q['bindings']={str(p.resolve()):sha(p)for p in [Path(__file__),Path(T.__file__),J.parent/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',R/'tools/audit/contra_force_internal_checkpoint_isr_controls_v1.py']}
  T.save(O/'controls.json',q)
 print(json.dumps(dict(passed=True,real_cuts=q['real_cuts'],minimum_SP=q['minimum_SP'],SHA256=sha(O/'controls.json'))))

if __name__=='__main__':main()
