"""Compact in-place Bass draft controls. No native, copies or output trees."""
from pathlib import Path
import hashlib,itertools,json,traceback
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from verify_native_relocation import NesMPU

R=Path(__file__).resolve().parents[2]
BUILD=R/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(q,name,a=0,x=0,y=0,flags=0x30,stop=None,irq_at=None,nmi_at=None):
 b,m=q.b,q.m;s=b['syms'][name];g=b['segs'][s['seg']]
 pc=address(b,name);bank=(int(g['ooffs'],0)-16)//8192;window=(pc-0x8000)//8192
 m.page(window,bank)
 if window in(1,2):q.set('CurrentBank'if window==1 else'CurrentBankC',bank|128)
 c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,flags,0xfd;c.stPushWord(0x5aff)
 if hasattr(m,'cpu'):m.cpu=c
 m.writes=[];trace=[];irqs=0
 for index in range(100000):
  if c.pc==(address(b,stop)if stop else 0x5b00):return c,trace,irqs
  if index==nmi_at:
   regs=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc);banks=m.banks[:]
   smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2]
   before_smc=[m[at]for at in smc]
   protected=['SmTemp','SmTempX','SmTempPage','SmTempY','SmClearance','SmSlot','SmHeadX','SmHeadPage','SmSourceJumped','SmCeilingHit','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_Speed']
   at=[address(b,n)for n in protected]+[address(b,'MmYFraction')+i for i in range(2)]+[address(b,'MmVY')+i for i in range(3)]
   values=[m[i]for i in at]
   c.nmi()
   for _ in range(100000):
    if(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc)==regs:break
    c.step()
    if getattr(m,'pending_dma',False):m.pending_dma=False
   else:raise AssertionError(('NMI resume',name,index))
   assert m.banks==banks and[m[i]for i in smc]==before_smc and[m[i]for i in at]==values,('NMI live owner/5SMC',index,banks,m.banks,before_smc,[m[i]for i in smc],[(hex(i),a,m[i])for i,a in zip(at,values)if m[i]!=a])
  if index==irq_at:
   assert not c.p&4
   regs=(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc);banks=m.banks[:]
   c.irq()
   for _ in range(2000):
    if(c.a,c.x,c.y,c.p&0xcf,c.sp,c.pc)==regs:break
    c.step()
   else:raise AssertionError(('IRQ resume',name,index))
   assert m.banks==banks;irqs+=1
  trace.append((c.pc,c.p,m.banks[:]))
  c.step()
 raise AssertionError(('timeout',name,hex(c.pc),m.banks))
def app(q):
 return bytes(q.m[:0x100])+bytes(q.m[0x200:0x800])+bytes(q.m[0x5c00:0x8000])
def setup(b,char=9,**v):
 q=Arena(b,char);q.put(RlVariant=0,OperMode_Task=3,AreaType=1,AreaPointer=194,
  Player_State=1,PlayerSize=0,Player_Y_Position=88,Player_Y_Speed=252,
  MmVY=0,MmXFraction=0,GuestHurtTicks=0,RgCrouch=0)
 q.array('MmVY',[0,0,252]);q.put(**v);return q
def fixed(q,name,v,n):q.array(name,[(v>>(8*i))&255 for i in range(n)])
def block(q,world,y,tile):
 base=address(q.b,'Block_Buffer_2'if world//256&1 else'Block_Buffer_1')
 at=base+(world%256)//16+((y-32)&240);q.m[at]=tile;return at
def reg(c):return(c.a,c.x,c.y,c.p,c.sp)
def main():
 old=scoped_load(BUILD/'smb-crossover-mmc5-expanded.nes');new=scoped_load(BUILD/'bass_corner_private.nes')
 assert hashlib.sha256(old['raw']).hexdigest()=='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
 proof=dict(passed=False,native_run=False,base_sha256=hashlib.sha256(old['raw']).hexdigest(),candidate_sha256=hashlib.sha256(new['raw']).hexdigest(),counts={},costs={})
 try:
  # All physical status bits, including V/D/I, on the two compiled getters.
  flags=[0x20|((i&3))+((i&4)<<0)+((i&8)<<0)+((i&16)<<2)+((i&32)<<2)for i in range(64)]
  count=0;foreign=[];owned=[]
  for char,variant,state,crouch,hurt,pose,dirs in itertools.product(range(20),[0,1],[0,1],[0,1],[0,1],[0,1],[0,8]):
   for name,base in [('MegaManCollisionAdder',3),('MegaManCollisionBox',12)]:
    # Keep the exhaustive64flags on raw legacy selectors; public callers use
    # four representative flags here, and genuinely route other families.
    for f in [0x20,0x63,0xa8,0xef]:
     qs=[setup(b,char,RlVariant=variant,Player_State=state,RgCrouch=crouch,GuestHurtTicks=hurt,RgShootPose=pose,SavedJoypadBits=dirs)for b in[old,new]]
     cs=[run(q,name,a=char,x=19,y=23,flags=f)[0]for q in qs]
     if char==9 and variant==0:
      expected=base+(0 if hurt else 2 if crouch else 1 if state and not(pose and dirs)else 0)
      assert cs[1].y==expected,(name,char,variant,state,crouch,hurt,pose,dirs,cs[1].y,expected)
      assert(cs[0].a,cs[0].x,cs[0].p,cs[0].sp)==(cs[1].a,cs[1].x,cs[1].p,cs[1].sp)
      assert app(qs[0])==app(qs[1]);owned.append(cs[1].processorCycles-cs[0].processorCycles)
     else:
      assert reg(cs[0])==reg(cs[1]),('foreign getter regs',char,variant,state,crouch,hurt,pose,dirs,reg(cs[0]),reg(cs[1]))
      assert app(qs[0])==app(qs[1]),('foreign getter RAM',char,name)
      foreign.append(cs[1].processorCycles-cs[0].processorCycles)
     count+=1
  proof['counts']['public_getters']=count
  proof['costs']['public_foreign_getters']=[min(foreign),max(foreign)]
  proof['costs']['public_Bass_getters']=[min(owned),max(owned)]
  count=0
  for char,variant,crouch,hurt,f,name in itertools.product(range(6,13),[0,1],[0,1],[0,1],flags,['KbLegacyExpandedCollisionAdder','KbLegacyExpandedCollisionBox']):
   qs=[setup(b,char,RlVariant=variant,RgCrouch=crouch,GuestHurtTicks=hurt)for b in[old,new]]
   cs=[run(q,name,a=char,x=19,y=23,flags=f)[0]for q in qs]
   if char!=9 or variant!=0:assert reg(cs[0])==reg(cs[1])and app(qs[0])==app(qs[1]),('rawforeign',char,variant,name,f)
   count+=1
  proof['counts']['raw_selectors_all64_flags']=count
  n=0
  for state,face,mode,status in itertools.product([0,1,2],[1,2],[0,1],range(3)):
   q=setup(new,Player_State=state,PlayerFacingDir=face,CrossoverBehaviorVersion=mode,PlayerStatus=status)
   c,_,_=run(q,'MegaManCollisionBox');q.set('Player_BoundBoxCtrl',c.y)
   assert c.y==(12 if state==0 else 13)
   c,_,_=run(q,'PlayerBGCollision',stop='BillBGHeadConsumer')
   assert c.y==(30 if state==0 else 37),('actual grounded/air prefix',state,face,mode,status,c.y)
   n+=1
  proof['counts']['actual_published_body_BG_head_prefixes']=n
  n=0;costs=[]
  for char,variant,mode,state,face,f in itertools.product(range(20),[0,1],[0,1],[0,1],[1,2],[0x20,0x63,0xa8,0xef]):
   if char==9 and variant==0:continue
   qs=[setup(b,char,RlVariant=variant,CrossoverBehaviorVersion=mode,Player_State=state,PlayerFacingDir=face)for b in[old,new]]
   cs=[run(q,'PlayerBGCollision',flags=f)[0]for q in qs]
   assert reg(cs[0])==reg(cs[1])and app(qs[0])==app(qs[1]),('foreign full BG',char,variant,mode,state,face,f)
   costs.append(cs[1].processorCycles-cs[0].processorCycles);n+=1
  proof['counts']['foreign_complete_empty_BG']=n;proof['costs']['foreign_complete_empty_BG']=[min(costs),max(costs)]
  # Reconstruct only the preserved first-contact state, not deleted rawRAM.
  q=setup(new,Player_X_Position=89,Player_PageLoc=1)
  fixed(q,'MmXFraction',16384,2);fixed(q,'MmYFraction',8187,2)
  fixed(q,'MmVX',90112,3);fixed(q,'MmVY',-226647,3)
  at=block(q,352,80,196)
  c,t,_=run(q,'PlayerBGCollision')
  after_bg=dict(y=q.get('Player_Y_Position'),fraction=q.get('MmYFraction')+256*q.get('MmYFraction',1),pending=q.get('SmCeilingHit'),target=q.get('SmTempY'),speed=q.get('Player_Y_Speed'))
  assert after_bg['pending']==2 and after_bg['target']==91,after_bg
  c,t,_=run(q,'SamusAfterBGCollisionBridge')
  assert q.get('Player_Y_Position')==91 and q.get('MmYFraction')+256*q.get('MmYFraction',1)==0x8050
  assert[q.get('MmVY',i)for i in range(3)]==[0x55,0xd5,0]and q.get('Player_Y_Speed')==0 and q.get('SmCeilingHit')==0
  proof['actual_first_contact_reconstruction']=dict(explicit_reconstructed_fields_only=True,head_cell=at,after_BG=after_bg,post_anchor=91+0x8050/65536,velocity_Q16=0xd555,source_only=True)
  # Finite both-facing/phase/page/block pipelines, real native effect bodies.
  rows=[]
  for face,mode,x,page,fine,kind in itertools.product([1,2],[0,1],[89,250,2],[0,1],[0,0x7fff,0x8000,0xffff],[196,81,86]):
   q=setup(new,PlayerFacingDir=face,CrossoverBehaviorVersion=mode,Player_X_Position=x,Player_PageLoc=page,Player_Y_Position=90,BlockBounceTimer=0)
   fixed(q,'MmXFraction',0x4000,2);fixed(q,'MmYFraction',fine,2);fixed(q,'MmVX',65536 if face==1 else -65536,3);fixed(q,'MmVY',-5*65536,3)
   world=x+256*page;cell=(world+8)&~15;at=block(q,cell,80,kind)
   run(q,'PlayerBGCollision');assert q.get('SmCeilingHit')==2,(face,mode,x,page,fine,kind,q.get('SmCeilingHit'))
   run(q,'SamusAfterBGCollisionBridge')
   assert q.get('Player_Y_Position')==91 and q.get('MmYFraction')+256*q.get('MmYFraction',1)==0x8050
   assert[q.get('MmVY',i)for i in range(3)]==[0x55,0xd5,0]and q.get('Player_Y_Speed')==0
   rows.append((face,mode,x,page,fine,kind))
  proof['counts']['full_BG_post_effect_pipelines']=len(rows)
  rows=[]
  for face,mode,fine,dirs in itertools.product([1,2],[0,1],[0,0x7fff,0x8000,0xffff],[4,8,12]):
   q=setup(new,PlayerFacingDir=face,CrossoverBehaviorVersion=mode,Player_X_Position=89,Player_PageLoc=1,Player_Y_Position=84,RgShootPose=1,SavedJoypadBits=dirs)
   fixed(q,'MmXFraction',0x4000,2);fixed(q,'MmYFraction',fine,2);fixed(q,'MmVX',65536 if face==1 else -65536,3);fixed(q,'MmVY',-5*65536,3);block(q,352,80,196)
   run(q,'PlayerBGCollision');assert q.get('SmCeilingHit')==2
   run(q,'SamusAfterBGCollisionBridge');assert q.get('Player_Y_Position')==88 and q.get('MmYFraction')==12 and q.get('MmYFraction',1)==0
   rows.append((face,mode,fine,dirs))
  proof['counts']['air_aim24px_full_pipelines']=len(rows)
  # The valid wall clamp body is byte-exact. Exercise actual banked entry.
  n=0
  for char,face,mode,x,page,f in itertools.product([1,2,3,4,7,9,10,11],[1,2],[0,1],[0,1,94,250,255],[0,1],[0x20,0x61,0xa8,0xef]):
   qs=[setup(b,char,PlayerFacingDir=face,CrossoverBehaviorVersion=mode,Player_X_Position=x,Player_PageLoc=page,R0=face,Player_X_Speed=22 if face==1 else 234)for b in[old,new]]
   for q in qs:fixed(q,'MmVX',65536 if face==1 else -65536,3)
   cs=[run(q,'SamusStopAtWallBanked',a=char,flags=f)[0]for q in qs]
   assert reg(cs[0])==reg(cs[1])and app(qs[0])==app(qs[1]),('validwall',char,face,mode,x,page,f)
   n+=1
  proof['counts']['valid_wall_exact_controls']=n
  # Actual IRQ at every enabled instruction boundary of a full head call.
  def head():
   q=setup(new,Player_X_Position=89,Player_PageLoc=1,Player_Y_Position=88)
   fixed(q,'MmXFraction',0x4000,2);fixed(q,'MmYFraction',8187,2);fixed(q,'MmVX',90112,3);fixed(q,'MmVY',-226647,3)
   block(q,352,80,196);return q
  q=head();c,tr,_=run(q,'BillBGHeadConsumer',y=37,flags=0x20);reference=(reg(c),app(q),q.m.banks[:]);n=0
  for i,(pc,f,banks)in enumerate(tr):
   if f&4:continue
   q=head();cc,_,irqs=run(q,'BillBGHeadConsumer',y=37,flags=0x20,irq_at=i)
   assert(reg(cc)[:3]+(reg(cc)[3]&0xcf,reg(cc)[4]),app(q),q.m.banks[:])==(reference[0][:3]+(reference[0][3]&0xcf,reference[0][4]),reference[1],reference[2]),('IRQ outcome',i,hex(pc))
   n+=irqs
  proof['counts']['actual_IRQ_head_boundaries']=n
  from current3cee_postdma_mask_cpu_v4 import Bus
  n=0
  for i in range(0,len(tr),8):
   q=head();q.put(NmiDisable=0,DisableScreenFlag=1,Mirror_PPUCTRL=0xa8,Mirror_PPUMASK=30,Sprite0HitDetectFlag=1,ReloadCHRBank=0,X5WideChrActive=1,VRAM_Buffer_AddrCtrl=0)
   physical=q.m.banks[:]
   q.m=Bus(new,bytes(q.m[:0x8000]),pads=(0,0))
   for w,bank in enumerate(physical):q.m.page(w,bank)
   run(q,'BillBGHeadConsumer',y=37,flags=0x20,nmi_at=i);n+=1
  proof['counts']['actual_complete_NMI_head_boundaries']=n
  proof['passed']=True
  proof['limits']='Finite assembled source controls only; no native/cadence/PPU or executed originalSWF proof. Real simultaneous corner calcAxis, hurt/sliding ceiling lifecycle and music/foreign performance remain separate limits.'
 except BaseException as ex:
  proof['error']=repr(ex);proof['traceback']=traceback.format_exc()
  with(BUILD/'bass_corner_history.jsonl').open('a')as f:f.write(json.dumps(dict(stage='assembled source controls',passed=False,candidate=proof['candidate_sha256'],error=repr(ex),counts=proof['counts']))+'\n')
  raise
 finally:
  proof['tool_sha256']=sha(__file__)
  (BUILD/'bass_corner_source_controls.json').write_text(json.dumps(proof,indent=2)+'\n')
  print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
