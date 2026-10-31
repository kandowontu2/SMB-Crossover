"""All-flags native portrait consumer plus real vectors across new lives offset."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import bowser_playable_contact_controls_v1 as A
from check_tmnt_render_oa import load,address,location
from verify_native_relocation import NesMPU
H=A.H;T=A.T;N=A.N;V=T.V;J=A.J;P=A.P
O=R/'build/bowser-playable-lives-vectors-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def seed(b,form,mode):
 if mode==0:
  m=N.C.fresh(b,0);H.put(m,CrossoverMenuIndex=26,FmAlts=form,SelectedCharacter=0)
  for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:N.invoke(m,n)
 else:
  m=A.A.boot(b,form)
  H.put(m,OperMode=1,OperMode_Task=1,AltEntranceControl=0,DisableIntermediate=0)
  N.invoke(m,'DisplayIntermediate')
 H.put(m,CurrentOAMOffset=0)
 for i in range(0x200,0x300,4):m[i]=248
 return m

def done(m,c):
 c,low=H.finish(m,c);assert c.sp==224
 return c,low

def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,source_CPU=True,native=False,flags=[],vectors=[])
 try:
  old,new=load(P/'candidate.nes'),load(J/'candidate.nes')
  for form,mode in itertools.product([0,8],[0,1]):
   seeds=[seed(b,form,mode)for b in[old,new]]
   for flag in range(64):
    states=[]
    for base in seeds:
     m=T.fork(base);c,low=done(m,H.start(m,'BwColdDraw',a=0,x=H.get(m,'ObjectMetasprite'),y=0,p=T.flags(flag)))
     states.append((m,c,low))
    x,a,_=states[0];y,z,low=states[1]
    assert(a.a,a.x,a.y,a.p,a.sp)==(z.a,z.x,z.y,z.p,z.sp),(form,mode,flag,'returned actual native AXYP')
    assert y.rawtags==x.rawtags and [bytes(v)for v in y.ram]==[bytes(v)for v in x.ram]
    assert(H.get(x,'Player_X_Position'),H.get(x,'Player_Y_Position'))==(H.get(y,'Player_X_Position'),H.get(y,'Player_Y_Position'))
    oldparts=A.visible(x);newparts=A.visible(y)
    assert newparts==[[yy+(8 if mode else 0),t,p,xx]for yy,t,p,xx in oldparts]
    assert len(newparts)==(7 if form else 11)
    q['flags'].append(dict(form=form,mode=mode,flags=flag,parts=len(newparts),old_CPU=a.processorCycles,new_CPU=z.processorCycles,minimum_SP=low))
   # Actual unique instruction snapshots in the complete cold renderer, not
   # a guessed source frame. Covers temporary PlayerY and genuine SFC maps.
   m=T.fork(seeds[1]);H.put(m,NmiDisable=0);c=H.start(m,'BwColdDraw',a=0,x=H.get(m,'ObjectMetasprite'),y=0,p=0x30)
   snapshots=[];seen=set();expected_bank=((location(new,'BwColdDraw')-16)//8192)|128
   for step in range(100000):
    if c.pc==0x5b00:break
    tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
    key=(tag,c.pc,H.get(m,'Player_Y_Position'))
    # Every new helper instruction; the actual native child instruction
    # boundary while its source coordinates are temporarily translated.
    if key not in seen and ((tag==expected_bank and 0xa000<=c.pc<0xc000)or c.pc==address(new,'DrawMetasprite')or 0x15a<=c.pc<0x17b):
     seen.add(key);snapshots.append((step,T.fork(m),(c.pc,c.a,c.x,c.y,c.p,c.sp,c.processorCycles)))
    c.step()
   else:raise AssertionError('actual portrait trace bound')
   for step,snap,regs in snapshots:
    cases=[('NMI',0,0),('NMI',255,0),('NMI',0,1)]
    if not regs[4]&4:cases.append(('IRQ',255,0))
    for kind,lag,pause in cases:
     m=T.fork(snap);H.put(m,NmiDisable=lag,GamePauseStatus=pause)
     control=T.fork(m);expected=NesMPU(memory=control,pc=regs[0]);expected.a,expected.x,expected.y,expected.p,expected.sp,expected.processorCycles=regs[1:]
     done(control,expected)
     live=NesMPU(memory=m,pc=regs[0]);live.a,live.x,live.y,live.p,live.sp,live.processorCycles=regs[1:]
     r=V.interrupt(m,live,kind);done(m,live)
     assert(live.a,live.x,live.y,live.p,live.sp)==(expected.a,expected.x,expected.y,expected.p,expected.sp)
     assert m.rawtags==control.rawtags and [bytes(v)for v in m.ram]==[bytes(v)for v in control.ram]
     assert A.visible(m)==A.visible(control)
     assert H.get(m,'Player_Y_Position')==H.get(control,'Player_Y_Position')
     q['vectors'].append(dict(form=form,mode=mode,step=step,PC=regs[0],lag=lag,pause=pause,**r))
  q.update(passed=True,allflags_cases=len(q['flags']),real_vector_cases=len(q['vectors']),all33SMC_live_page1_AXYP_SP_rawmaps_preserved=True,lives_only_translation=8,select_positions_unchanged=True)
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),Path(A.__file__),Path(V.__file__),P/'candidate.nes',J/'candidate.nes',J/'candidate.dbg',J/'bowser.bin']}
 (O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['flags','vectors','bindings']}));assert q['passed']
if __name__=='__main__':main()
