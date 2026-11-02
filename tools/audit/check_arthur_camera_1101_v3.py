"""Check Arthur camera arithmetic and the compacted genuine farcall transport."""
import itertools,json,re
import prepare_arthur_camera_1101_v3 as P
import prepare_arthur_auth_fast_1101_v2 as A
import check_arthur_auth_fast_1101_v2 as Q
import check_arthur_auth_fast_isr_1101_v2 as I
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location


def state(c):return(c.pc,c.a,c.x,c.y,c.p,c.sp)


def seed(b):
 m=M.fresh(b)
 at=location(b,'ArCacheSignature');m.ram[2][0x1fe0:0x1ff0]=b['raw'][at:at+16]
 M.put(m,SelectedCharacter=32,OperMode=1,GameEngineSubroutine=8,ArHostReady=167,FamilyMainCommit=1,NmiDisable=255)
 return m


def transport(m,slot,a=85,p=0x31,collect=None):
 b=m.bundle;target=address(b,'ArOwnServices')+3*slot
 m[address(b,'SafecallA_SMC')+1]=a
 m[address(b,'FarcallJmpTarget_SMC')+1]=target&255
 m[address(b,'FarcallJmpTarget_SMC')+2]=target>>8
 c=M.NesMPU(memory=m,pc=address(b,'FarCallCommon'))
 c.a=198;c.x=19;c.y=73;c.p=p;c.sp=224;c.stPushWord(0x5aff)
 leaves={address(b,n) for n in ['ArDispatch','ArProbeDispatch']}
 for _ in range(2000):
  if c.pc in leaves and m.rawtags[(c.pc-0x8000)//8192]==154:return c
  if collect is not None and c.pc>=0x8000 and m.rawtags[(c.pc-0x8000)//8192]==198 and 0xbd00<=c.pc<0xbf10:
   collect.setdefault((c.pc,c.sp),(M.fork(m),state(c)))
  assert m[c.pc]!=0,('BRK',slot,hex(c.pc))
  c.step()
 raise AssertionError(('transport bound',slot,hex(c.pc)))


def main():
 old,new=[scoped_load(p/'candidate.nes') for p in [A.O,P.O]]
 at=16+70*8192+0x1d00
 changed=[i for i,(a,z)in enumerate(zip(old['raw'],new['raw']))if a!=z]
 assert changed and all(at<=i<at+768 for i in changed)
 assert old['raw'][at+0x210:at+0x300]==new['raw'][at+0x210:at+0x300], 'auth body, clock, menu remain identical'
 seeds=[seed(b) for b in [old,new]];count=0
 slots=[0,1,2,3,4,5,6,7,8,10,14,15,16,17,19,20,24,25,26,30,32]
 for slot,a,p in itertools.product(slots,[0,85,255],[0x20,0x21,0x60,0xa1]):
  pair=[]
  for initial in seeds:
   m=M.fork(initial);M.put(m,Player_X_Position=239,ScreenLeft_X_Pos=128,Player_Pos_ForScroll=13)
   c=transport(m,slot,a,p);pair.append((m,c))
  (x,c),(y,d)=pair
  assert state(c)==state(d),(slot,a,p,state(c),state(d))
  pos=address(new,'Player_Pos_ForScroll')
  assert M.get(y,'Player_Pos_ForScroll')==(111 if slot==0 else 13)
  for lo,hi in [(0,256),(512,2048)]:
   assert all(x[k]==y[k] for k in range(lo,hi)if slot!=0 or k!=pos),(slot,'native')
  assert x.ram==y.ram and x.rawtags==y.rawtags
  assert bytes(x[0x101+c.sp:0x200])==bytes(y[0x101+d.sp:0x200]),(slot,'live stack')
  count+=1
 arithmetic=0
 for px,left in itertools.product([0,1,127,128,239,255],range(256)):
  m=M.fork(seeds[1]);M.put(m,Player_X_Position=px,ScreenLeft_X_Pos=left,Player_Pos_ForScroll=77)
  transport(m,0)
  assert M.get(m,'Player_Pos_ForScroll')==(px-left)&255
  arithmetic+=1
 cuts={}
 for slot in [0,10]:transport(M.fork(seeds[1]),slot,collect=cuts)
 for kind,(m0,s)in itertools.product(['IRQ','lag-NMI'],cuts.values()):
  m=M.fork(m0);c=M.NesMPU(memory=m,pc=s[0]);c.pc,c.a,c.x,c.y,c.p,c.sp=s
  before=state(c);smc=bytes(m[0x15a:0x17b]);live=bytes(m[0x101+c.sp:0x200]);maps=m.rawtags[:]
  shadows=[M.get(m,'CurrentBank'),M.get(m,'CurrentBankC')]
  if kind=='IRQ':c.irq()
  else:c.nmi()
  for _ in range(100000):
   if state(c)==before:break
   assert m[c.pc]!=0,(kind,hex(before[0]),'BRK');c.step()
  else:raise AssertionError((kind,hex(before[0]),'ISR return bound'))
  assert bytes(m[0x15a:0x17b])==smc and bytes(m[0x101+c.sp:0x200])==live
  assert m.rawtags==maps and [M.get(m,'CurrentBank'),M.get(m,'CurrentBankC')]==shadows
  for n in ['ArTemp','ArTempHi','R0','R1','Player_Pos_ForScroll']:assert M.get(m,n)==M.get(m0,n)
  assert m.ram==m0.ram
 # Repeat the complete-cookie/policy and reached policy IRQ checks on this hash.
 A.BASE=A.O/'candidate.nes';A.O=P.O
 Q.main();I.main()
 result=dict(passed=True,ROM_sha256=P.sha(P.O/'candidate.nes'),changed_ROM_bytes=len(changed),only_physical_bank=70,owned_half_open=[0xbd00,0xc000],transport_cases=count,camera_arithmetic_cases=arithmetic,normal_probe_interrupt_cuts=len(cuts)*2,unique_transport_boundaries=len(cuts),scope='Actual FarCallCommon/table/dispatch transport preserved through genuine worker ingress; only movement publishes pre-step viewport lowbyte. No source physics or native emulator claim. Complete policy/auth and IRQ receipts are CPU.json/ISR.json.')
 (P.O/'camera-CPU.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))


if __name__=='__main__':main()
