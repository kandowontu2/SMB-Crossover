"""Finite assembled reservation/reference, foreign, partial-writer controls.

The independent reference executes the unchanged8487 emitters with explicitly
logged allocation changes at their genuine entry/post-shot/body boundaries.
No native result is implied. Outputs remain a single flat compact receipt.
"""
from pathlib import Path
import hashlib,itertools,json,traceback
import mm_proto_body_priority_partition_v6 as fixture
from check_tmnt_render_oa import address,location,Memory
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU

R=Path(__file__).resolve().parents[2];B=R/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n')

def application(c,m):
 # All live registers/flags, application RAM, mapper and ordered I/O. The
 # returned caller has no live local stack; only old dead upper-stack bytes
 # differ when new genuine JSRs use them. Lower192 stack bytes remain exact.
 return(c.a,c.x,c.y,c.p&207,c.sp,bytes(m[:0x1c0]+m[0x200:0x8000]),tuple(m.banks),
        tuple((at,v)for at,v in m.writes if 0x2000<=at<0x5c00))

def run(b,cfg,reference=False,irq_at=None):
 c,m,before=fixture.setup(b,cfg);l=lambda n:address(b,n)
 if 'body_id'in cfg:m[l('ObjectMetasprite')]=cfg['body_id']
 raw=m.bundle['raw'];pre=False;post=False;body=False;bodywrites=[];nonbody=[];mut=[];trace=[]
 active=(reference or 'MmReserveBegin'in b['syms'])and cfg.get('char',1)==1 and cfg.get('shuffle',0)%2==0 and not cfg.get('dead',0) and not cfg.get('hidden',False)
 reserve=44 if cfg.get('variant',0)else 40
 zero_writes=0;lastwrite=0;lastpc=0;irqs=[]
 for step in range(150000):
  if c.pc==0x7f00:break
  bank=m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
  if reference and active and not pre and zero_writes==64 and m.writes and m.writes[-1]==(l('CurrentOAMOffset'),0):
   assert m[lastpc]==0x86 or m[lastpc]==0x8e,('Reference preowner not real STX',hex(lastpc),m[lastpc])
   for n,v in [('GuestOamRotationActive',128+cfg.get('variant',0)),('RgOamRotation',0),('CurrentOAMOffset',reserve)]:m[l(n)]=v
   c.x=reserve;pre=True;mut.append(['reserve_before_prebody',step,lastpc,reserve])
  if reference and active and bank==4 and c.pc==l('MegaManProjectileOamReady'):
   assert pre
   p=m[l('CurrentOAMOffset')]-reserve;assert 0<=p<=255-reserve
   m[l('RgOamUsed')]=p;m[l('RgOamPlayerStart')]=0
   c.a=0;c.x=cfg.get('variant',0);c.p=(c.p&~0x83)|3
   c.pc=l('DrawAllMetasprites::InitObjectLoop');post=True;mut.append(['post_shot_count',step,p])
  if bank==4 and c.pc==l('DrawMetasprite')and c.y==0:
   body=True
  if reference and active and bank==4 and c.pc==l('DrawAllMetasprites::DoneDrawingPlayer'):
   p=m[l('RgOamUsed')];logical=(m[l('CurrentOAMOffset')]+p)&255
   first=m[l('RgOamFirst')];physical=(logical-first)&255;rotation=(-first)&255
   v=bool((physical^rotation)&(physical^logical)&128)
   m[l('CurrentOAMOffset')]=logical;m[l('RgOamRotation')]=0
   c.a=logical;c.x=physical;c.y=0;c.p=(c.p&~0xc2)|2|(64 if v else 0)
   mut.append(['restore_source_return_contract',step,logical,physical,int(v)])
  if irq_at==step:
   prior=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,bytes(m[:0x100]+m[0x200:0x2000]+m[0x5c00:0x8000]),tuple(m.banks))
   assert not c.p&4
   start=len(m.writes);c.irq()
   for _ in range(400):
    if c.pc==prior[0]and c.sp==prior[5]:break
    c.step()
   else:raise AssertionError('IRQ failed return')
   now=(c.pc,c.a,c.x,c.y,c.p&207,c.sp,bytes(m[:0x100]+m[0x200:0x2000]+m[0x5c00:0x8000]),tuple(m.banks))
   assert prior==now,('Actual IRQ clobber',step,hex(prior[0]));irqs=m.writes[start:];del m.writes[start:]
  trace.append((step,c.pc,bank));lastpc=c.pc;start=len(m.writes);c.step()
  for at,v in m.writes[start:]:
   if 0x200<=at<0x300:
    if not pre and at%4==0 and v==248:zero_writes+=1
    elif body:bodywrites.append((at,v))
    elif pre:nonbody.append((at,v))
  if not reference and active and not pre and zero_writes==64 and m.writes and m.writes[-1][0]==l('CurrentOAMOffset'):
   # Candidate's genuine initial reservation; do not change any observed state.
   if m.writes[-1][1]==reserve:pre=True
 else:raise AssertionError(('Draw timeout',cfg,hex(c.pc),m.banks))
 assert c.sp==253
 for n,v in before.items():assert bytes(m[l(n):l(n)+4])==v,('Projectile state changed',n,cfg)
 if active:
  assert pre and (post or not reference)
  assert all(at-0x200>=reserve for at,v in nonbody),('Nonbody overlapped physical body reservation',cfg,reserve,nonbody[:10])
  assert all(at-0x200<reserve for at,v in bodywrites),('Body exceeded reservation',cfg,reserve,bodywrites)
 return c,m,trace,dict(mutations=mut,body_OAM_writes=len(bodywrites),nonbody_OAM_writes=len(nonbody),IRQ=irqs)

def partial(b,name,char,tag,offset,variant=0,vine_y=0):
 m=Memory(b);pc=address(b,name);bank=(location(b,name)-16)//8192;m.page(1,bank)
 for n,v in dict(CurrentBank=bank|128,CurrentBankC=m.banks[2]|128,SelectedCharacter=char,
                 ProtoVariant=variant,GuestOamRotationActive=tag,CurrentOAMOffset=offset,
                 Enemy_Rel_YPos=80,Enemy_Rel_XPos=96,Vine_Start_Y_Position=16,ObjectOffset=0,
                 Enemy_Y_Position=80,Enemy_OffscreenBits=0).items():m[address(b,n)]=v
 m[0x5204]=128
 c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,0,vine_y,0x61,253;c.stPushWord(0x7eff);m.writes=[]
 for _ in range(20000):
  if c.pc==0x7f00:break
  c.step()
 else:raise AssertionError(('Partial timeout',name))
 return c,m

def main():
 result=dict(passed=False,native=False,counts={});rows=[]
 try:
  old,new=[scoped_load(B/n)for n in ['smb-crossover-mmc5-expanded.nes','mm_body_reserve.nes']]
  result.update(baseline=sha(B/'smb-crossover-mmc5-expanded.nes'),candidate=sha(B/'mm_body_reserve.nes'))
  assert result['baseline']=='8487c439ded9bc6274e1dc8f8e051494fa96ee518553d9c2f382eccf2e71d0e6'
  for char,variant,flag,shuffle in itertools.product([c for c in range(20)if c!=1],[0,1],[0x20,0xe1],[0,1]):
   cfg=dict(entry='DrawAllMetasprites',char=char,variant=variant,flags=flag,shuffle=shuffle,types=[1,1,1,1])
   c,m,_,_=run(old,cfg);d,n,_,_=run(new,cfg)
   assert application(c,m)==application(d,n),('Foreign whole draw',cfg,[(hex(i),m[i],n[i])for i in range(0x8000)if not 0x1c0<=i<0x200 and m[i]!=n[i]][:20],(c.a,c.x,c.y,c.p),(d.a,d.x,d.y,d.p))
   delta=d.processorCycles-c.processorCycles;assert delta<=0,('Foreign slowdown',cfg,delta)
   rows.append(dict(kind='foreign',delta=delta))
  result['counts']['foreign_draws']=len(rows)
  cases=[]
  for var,phase,face,mask,first in itertools.product([0,1],[0,1],[1,2],[0,1,15],[0,156]):
   cases.append(dict(entry='DrawAllMetasprites',char=1,variant=var,shuffle=phase,face=face,first=first,flags=0x61,
                     types=[1 if mask>>i&1 else 0 for i in range(4)],world=3))
  for var,phase,dead,hidden,flip in itertools.product([0,1],[0,1],[0,1],[False,True],[0,128]):
   cases.append(dict(entry='DrawAllMetasprites',char=1,variant=var,shuffle=phase,dead=dead,hidden=hidden,flip=flip,types=[6,5,4,3],flags=0x20))
  for var,phase in itertools.product([0,1],[0,1]):
   cases.append(dict(entry='DrawAllMetasprites',char=1,variant=var,shuffle=phase,types=[1,2,3,6],special=6,drops=4,numbers=6,world=6,fireowners=6,fireparts=12,flags=0x61))
  flags=[0x20|(n&15)|((n&16)<<2)|((n&32)<<2)for n in range(64)]
  for var,phase,flag in itertools.product([0,1],[0,1],flags):
   cases.append(dict(entry='DrawAllMetasprites',char=1,variant=var,shuffle=phase,types=[1,2,3,6],flags=flag))
  for pose,face in itertools.product(range(48),[1,2]):
   cases.append(dict(entry='DrawAllMetasprites',char=1,variant=0,shuffle=0,types=[1]*4,body_id=address(old,'METASPRITE_MM_HAIR_STAND')+pose,face=face,flags=0x61))
  for pose,face in itertools.product(range(16),[1,2]):
   cases.append(dict(entry='DrawAllMetasprites',char=1,variant=1,shuffle=0,types=[1]*4,proto_pose=pose,face=face,flags=0x61))
  for kind,age,face in itertools.product(range(1,7),[0,1,31,255],[1,2]):
   cases.append(dict(entry='DrawAllMetasprites',char=1,variant=1,shuffle=0,types=[kind]*4,age=age,face=face,flags=0x61))
  for cfg in cases:
   c,m,_,_=run(old,cfg,reference=True);d,n,trace,summary=run(new,cfg)
   assert application(c,m)==application(d,n),('Partition reference',cfg,[(hex(i),m[i],n[i])for i in range(0x8000)if not 0x1c0<=i<0x200 and m[i]!=n[i]][:20],(c.a,c.x,c.y,c.p),(d.a,d.x,d.y,d.p))
   a,am,_,_=run(old,cfg)
   rows.append(dict(kind='owned',cfg=cfg,delta=d.processorCycles-a.processorCycles,cycles=d.processorCycles,body_OAM_writes=summary['body_OAM_writes']))
  result['counts']['owned_draws']=len(cases)
  # Real leaf returns, source write order and geometry. The reference moves
  # ONLY the initial cursor4 for a retained Proto priority image.
  partialrows=[]
  for kind,oldname,newname in [('vine','DrawVine','DrawVine'),('lift','DrawSmallPlatform','DrawSmallPlatform')]:
   for char,tag,offset,vine_y in itertools.product([0,1,9],[0,1,128,129],[16,40,44,64,68,92,116,140,164,184,188],[0,1]if kind=='vine'else[0]):
    shift=4 if char==1 and tag==129 and offset==40 else 0
    c,m=partial(old,oldname,char,tag,offset+shift,vine_y=vine_y);d,n=partial(new,newname,char,tag,offset,vine_y=vine_y)
    # Relocated genuine farcall targets differ in SMC; all other scratch,
    # registers and emitted OAM writes retain the real source contract.
    ignore=set(range(0x100,0x200))
    for seg in old['segs'].values():
     if seg.get('name')=='"SMCCODE"':ignore.update(range(int(seg['start'],0),int(seg['start'],0)+int(seg['size'],0)))
    diff=[(i,m[i],n[i])for i in range(0x8000)if i not in ignore and m[i]!=n[i]]
    assert not diff,('Partial RAM',kind,char,tag,offset,diff[:20])
    assert(c.a,c.x,c.y,c.p&207,c.sp,tuple(m.banks))==(d.a,d.x,d.y,d.p&207,d.sp,tuple(n.banks)),('Partial ABI',kind,char,tag,offset,(c.a,c.x,c.y,c.p),(d.a,d.x,d.y,d.p))
    assert[(a,v)for a,v in m.writes if 0x200<=a<0x300]==[(a,v)for a,v in n.writes if 0x200<=a<0x300],('Partial OAM',kind)
    partialrows.append(dict(kind=kind,char=char,tag=tag,offset=offset,vine_group=vine_y,intentional_shift=shift,delta=d.processorCycles-c.processorCycles))
  result['counts']['partial_leaves']=len(partialrows)
  # Actual IRQ/RTI around each distinct new body-helper instruction.
  irqrows=[];cfg=dict(entry='DrawAllMetasprites',char=1,variant=1,shuffle=0,types=[1]*4,flags=0x20,world=2)
  c,m,trace,_=run(new,cfg);expected=application(c,m)
  starts=[address(new,n)for n in ['MmReserveBegin','MmReserveFinish','MmReserveExit']]
  seen=set()
  for step,pc,bank in trace:
   if bank!=4 or pc in seen or not any(a<=pc<a+110 for a in starts):continue
   seen.add(pc);d,n,_,_=run(new,cfg,irq_at=step)
   # IRQ-owned PPUregister final latches differ only by the genuine IRQ.
   for at in [0x2005,0x2006,0x5128,0x5130]:m[at]=n[at]
   assert application(c,m)[:7]==application(d,n)[:7],('Whole IRQ draw result',step,hex(pc))
   irqrows.append([step,pc])
  result['counts']['actual_IRQ_boundaries']=len(irqrows)
  result.update(passed=True,full_caller_foreign_state_exact=True,original_body_record_order=True,
                partition_reference='Original8487 emitters; reserve actual40/44 BEFORE all nonbody, bodyphysical0, original logical return arithmetic.',
                foreign_cycle_delta=[min(r['delta']for r in rows if r['kind']=='foreign'),max(r['delta']for r in rows if r['kind']=='foreign')],
                owned_cycle_delta=[min(r['delta']for r in rows if r['kind']=='owned'),max(r['delta']for r in rows if r['kind']=='owned')],
                partial_cycle_delta=[min(r['delta']for r in partialrows),max(r['delta']for r in partialrows)],
                rows=rows,partials=partialrows,IRQ=irqrows,
                limits='Finite assembled controls only. Construction phase can alias skipped DMA. Bodypriority may hide world/shots on that turn; native-order turns remain. No native/cadence/visual acceptance.')
 except BaseException as ex:
  result['error']=repr(ex);result['traceback']=traceback.format_exc();result['completed_rows']=rows;raise
 finally:
  result['tool_sha256']=sha(__file__);put(B/'mm_body_reserve_cpu.json',result)
  print(json.dumps({k:v for k,v in result.items()if k in['passed','error','counts','foreign_cycle_delta','owned_cycle_delta','partial_cycle_delta']},indent=2))

if __name__=='__main__':main()
