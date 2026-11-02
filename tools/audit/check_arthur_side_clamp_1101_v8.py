"""Actual installed wall ABI, Arthur source geometry, mapper and IRQ checks."""
from pathlib import Path
import hashlib,itertools,json,re
import prepare_arthur_side_clamp_1101_v8 as P
import check_hogan_current_bounded_v1 as M
import arthur_source_map_v1 as G
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load
O=P.O


def state(c):return(c.pc,c.a,c.x,c.y,c.p,c.sp)


def bundle():
 b=scoped_load(P.BASE);assert P.sha(P.BASE)==P.SHA
 raw=bytearray(b['raw']);at=location(b,'SamusStopAtWallBanked');old=(O/'old-wall.bin').read_bytes();new=(O/'new-wall.bin').read_bytes()
 assert raw[at:at+215]==old and len(new)==215
 raw[at:at+215]=new
 n=dict(b);n['raw']=bytes(raw);return b,n


def seed(b):
 m=M.Bus(b);M.put(m,SelectedCharacter=0,OperMode=1,GameEngineSubroutine=8,FamilyMainCommit=1,NmiDisable=255,
  Mirror_PPUCTRL=160,Player_X_Position=49,Player_PageLoc=1,Player_Y_Position=130,Player_Y_HighPos=1,
  Player_State=1,ArMode=1,Player_CollisionBits=255,SideCollisionTimer=9,XgWallContact=3,
  Player_X_Scroll=7,MmXFraction=17,SmTempX=47,SmTempPage=79)
 m[address(b,'MmVX'):address(b,'MmVX')+3]=[37,73,1]
 m[address(b,'MmXFraction')+1]=29
 return m


def fields(m,low=0x7f):return bytes(m[:0x101+low]+m[0x1e1:0x8000])


def result(z):return(z['A'],z['X'],z['Y'],z['P']&0xef)


def main():
 for path,h in json.loads((O/'assembly.json').read_text())['bindings'].items():assert P.sha(P.R/path)==h,path
 old,new=bundle();bases=[seed(b)for b in [old,new]];foreign=0;arith=0;away=0;wrapper=0;costs=[]
 xs=[0,1,14,15,16,239,240,255];flags=[0x20,0x31,0x61,0xa9]
 for raw,side,xi,flag in itertools.product([i for i in range(39)if i!=32],[1,2],range(8),flags):
  pair=[]
  for initial in bases:
   m=M.fork(initial);speed=[0,2,254][xi%3];M.put(m,SelectedCharacter=raw,R0=side,Player_X_Position=xs[xi],Player_PageLoc=[0,1,127,255][xi%4],Player_X_Speed=speed,GuestHurtTicks=xi&1)
   # Cover source Samus's positive/negative/zero fractional velocities, while
   # retaining arbitrary incoming X to test the entire callable ABI.
   m[address(m.bundle,'MmVX'):address(m.bundle,'MmVX')+3]=[[0,0,0],[1,0,0],[0,1,0],[0,0,1],[1,255,255],[0,0,128],[255,255,127],[73,19,254]][xi]
   z=M.invoke(m,'SamusStopAtWallBanked',a=raw,x=19,y=73,p=flag);pair.append((m,z))
  (a,za),(b,zb)=pair
  assert result(za)==result(zb),('foreign CPU',raw,side,xi,flag,result(za),result(zb))
  assert fields(a,min(za['minimum_SP'],zb['minimum_SP']))==fields(b,min(za['minimum_SP'],zb['minimum_SP'])),('foreign RAM',raw,side,xi,flag,[(hex(k),a[k],b[k])for k in range(0x8000)if not 0x180<=k<0x200 and a[k]!=b[k]][:8])
  assert a.ram==b.ram and a.rawtags==b.rawtags and a.chr_latches==b.chr_latches,('foreign mapping/WRAM',raw,side,xi)
  assert bytes(a[0x15a:0x17b])==bytes(b[0x15a:0x17b]) and bytes(a[0x1e1:0x200])==bytes(b[0x1e1:0x200])
  costs.append(zb['CPU']-za['CPU']);foreign+=1
 print('Foreign wall ABI',foreign,'cases pass',flush=True)
 direct=0
 for raw,side,incoming,flag in itertools.product([i for i in range(39)if i!=32],[1,2],[0,19,32,128,255],flags):
  pair=[]
  for initial in bases:
   m=M.fork(initial);M.put(m,SelectedCharacter=raw,R0=side,Player_X_Speed=254)
   z=M.invoke(m,'SamusStopAtWallBanked::NativeGuest',a=incoming,x=19,y=side,p=flag);pair.append((m,z))
  (a,za),(b,zb)=pair;low=min(za['minimum_SP'],zb['minimum_SP'])
  assert result(za)==result(zb)and fields(a,low)==fields(b,low)and a.ram==b.ram and a.rawtags==b.rawtags,('NativeGuest arbitraryA',raw,side,incoming,flag)
  direct+=1
 for side,x,page,flag in itertools.product([1,2],range(256),[0,1,127,128,255],flags):
  m=M.fork(bases[1]);speed=2 if side==1 else 254;M.put(m,SelectedCharacter=32,R0=side,Player_X_Position=x,Player_PageLoc=page,Player_X_Speed=speed,GuestHurtTicks=x&1)
  before=fields(m);z=M.invoke(m,'SamusStopAtWallBanked',a=32,x=19,y=73,p=flag)
  position=((page<<8)|x);expected=((position&0xfff0)+(-1 if side==1 else 16))&65535
  assert M.get(m,'Player_X_Position')==expected&255 and M.get(m,'Player_PageLoc')==expected>>8,('Arthur16bit',side,x,page,flag,expected)
  assert M.get(m,'SmTempX')==47 and M.get(m,'SmTempPage')==79,'Arthur does not borrow foreign clamp scratch'
  assert M.get(m,'SideCollisionTimer')==16 and M.get(m,'XgWallContact')==side
  assert bytes(m[address(new,'MmVX'):address(new,'MmVX')+3])==bytes(3)
  assert M.get(m,'MmXFraction')==0 and M.get(m,'MmXFraction',1)==0 and M.get(m,'Player_X_Speed')==0 and M.get(m,'Player_X_Scroll')==0
  assert M.get(m,'Player_CollisionBits')==(255^side if x&1 else 255)
  overflow=(side==1 and page==128 and x<16)or(side==2 and page==127 and x>=240)
  assert result(z)==(0,19,16,0x23|(flag&0x0c)|(64 if overflow else 0)),('Arthur AXYP',side,x,page,flag,result(z))
  assert m.ram==bases[1].ram and m.rawtags==bases[1].rawtags
  arith+=1
 # Zero velocity retains the original left clamp; positive left velocity is
 # the original away early return. These are real original guard semantics.
 for x,page,speed,flag in itertools.product(xs,[0,1,255],[0,1,127,128,255],flags):
  m=M.fork(bases[1]);M.put(m,SelectedCharacter=32,R0=2,Player_X_Position=x,Player_PageLoc=page,Player_X_Speed=speed)
  z=M.invoke(m,'SamusStopAtWallBanked',a=32,x=19,y=73,p=flag)
  if 1<=speed<=128:
   # CMP#1's N test treats 128-1 as positive, preserving the source guard.
   assert(M.get(m,'Player_X_Position'),M.get(m,'Player_PageLoc'))==(x,page)
   assert M.get(m,'SideCollisionTimer')==9 and M.get(m,'Player_X_Scroll')==7
  else:
   expected=(((page<<8)|x)&0xfff0)+16;expected&=65535
   assert(M.get(m,'Player_X_Position'),M.get(m,'Player_PageLoc'))==(expected&255,expected>>8)
  away+=1
 for raw,engine,flag in itertools.product(range(39),[0,1,6,7,9,10,11,12],flags):
  pair=[]
  for initial in bases:
   m=M.fork(initial);M.put(m,SelectedCharacter=raw,GameEngineSubroutine=engine,R0=1)
   z=M.invoke(m,'SamusStopAtWall',a=85,x=19,y=73,p=flag);pair.append((m,z))
  (a,za),(b,zb)=pair;assert result(za)==result(zb)and fields(a)==fields(b)and a.ram==b.ram and a.rawtags==b.rawtags,('script engine',raw,engine,flag);wrapper+=1
 print('Arthur16bit',arith,'guard',away,'non8 wrapper',wrapper,'pass',flush=True)
 # Original GNG source side points are reached through the authentic DF69 /
 # DF79 calls. Stop just before the genuine world consumer EA55.
 source=0
 for pc,x,page,y in itertools.product([0xe9f1,0xea01],[0,1,7,8,15,239,240,248,255],[0,1,255],[0,15,128,235]):
  c=G.machine(7);c.x=0;c.memory[0x5af]=x;c.memory[0x583]=page;c.memory[0x599]=y;c.memory[0x56d]=0;c.pc=pc
  for _ in range(40):
   if c.pc==0xea55:break
   c.step()
  else:raise AssertionError(('GNG side source closure',hex(c.pc)))
  point=c.memory[0x74]|c.memory[0x78]<<8;assert point==(((page<<8)|x)+(8 if pc==0xe9f1 else-8))&65535
  source+=1
 cuts={};cls=M.NesMPU;step=cls.step
 def record(c):
  if c.pc>=0x8000 and c.memory.rawtags[(c.pc-0x8000)//8192]==138 and 0xa290<=c.pc<0xa367:
   cuts.setdefault((c.pc,c.sp),(M.fork(c.memory),state(c)))
  return step(c)
 cls.step=record
 try:
  for raw,side,speed in itertools.product([2,5,32,36],[1,2],[0,2,254]):
   m=M.fork(bases[1]);M.put(m,SelectedCharacter=raw,R0=side,Player_X_Speed=speed);M.invoke(m,'SamusStopAtWallBanked',a=raw)
 finally:cls.step=step
 for kind,(m0,s)in itertools.product(['IRQ','lag-NMI'],cuts.values()):
  m=M.fork(m0);c=cls(memory=m,pc=s[0]);c.pc,c.a,c.x,c.y,c.p,c.sp=s
  before=state(c);smc=bytes(m[0x15a:0x17b]);live=bytes(m[0x101+c.sp:0x200]);maps=m.rawtags[:]
  if kind=='IRQ':c.irq()
  else:c.nmi()
  for _ in range(100000):
   if state(c)==before:break
   assert m[c.pc]!=0,(kind,hex(before[0]),'BRK');c.step()
  else:raise AssertionError((kind,hex(before[0]),'ISR bound'))
  assert bytes(m[0x15a:0x17b])==smc and bytes(m[0x101+c.sp:0x200])==live
  assert m.rawtags==maps and m.ram==m0.ram
  for n in ['CurrentBank','CurrentBankC','SmTempX','SmTempPage','R0','R1']:assert M.get(m,n)==M.get(m0,n)
 q=dict(passed=True,base_sha256=P.SHA,proposed_candidate_sha256=hashlib.sha256(new['raw']).hexdigest(),foreign_actual_farcall_cases=foreign,foreign_NativeGuest_arbitrary_A_cases=direct,foreign_all_application_RAM_WRAM_AXYP_mapping_exact=True,Arthur_16bit_cases=arith,Arthur_original_left_guard_cases=away,non8_script_engine_wrapper_cases=wrapper,original_GNG_side_point_cases=source,original_GNG_sha256=G.EXPECTED,source_side_callers=['7:DF69 JSR E9F1 nativeX+8','7:DF79 JSR EA01 nativeX-8'],host_anchor='ArHostImport nativeX=PlayerWorldX+8; side offsets remain[0,16].',source_side_point_bytes_sha256=hashlib.sha256(G.load()[16+7*16384+0x29f1:16+7*16384+0x2a2b]).hexdigest(),unique_changed_worker_interrupt_boundaries=len(cuts),IRQ_lag_NMI_cuts=2*len(cuts),foreign_CPU_cycle_delta=[min(costs),max(costs)],scope='Actual FarCallCommon/native wall routine. Exact-ID32 geometry correction in original215B; all foreign scratch values retained, live stack/SMC/maps/WRAM interrupt contracts. Untimed CPU qualification only; native controller earned flower and1-1 still required.',bindings={str(p.relative_to(P.R)):P.sha(p)for p in [Path(__file__),Path(P.__file__),P.SOURCE,O/'new-wall.bin',O/'new-wall.lbl',O/'assembly.json']})
 (O/'CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
