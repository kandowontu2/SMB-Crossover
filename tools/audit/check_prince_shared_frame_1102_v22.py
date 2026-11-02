"""All fixed Sh/Ex/typed-BB ingress transport parity, source-only proposal."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import compile_prince_host_lifecycle_1102_v12 as L
import check_hogan_current_bounded_v1 as N
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
O=L.O;B=R/'build/bubble-bobble-source-1101-v1'


def bundles():
 old=scoped_load(L.BASE);raw=bytearray(old['raw'])
 def put(pc,data):raw[16+65*8192+pc-0xa000:16+65*8192+pc-0xa000+len(data)]=data
 for pc,name in [(0xae00,'native-visible-owner.bin'),(0xa740,'native-proxy-routes.bin'),(0xb031,'native-proxy-route-foreign.bin'),(0xb026,'native-proxy-route-retire-stub.bin')]:put(pc,(B/name).read_bytes())
 put(0xb101,bytes.fromhex('0bae'));old=dict(old,raw=bytes(raw));new=dict(old);raw=bytearray(old['raw'])
 for pc,name in [(0xaaf7,'shared-frame-v22.bin'),(0xa740,'shared-selector-v22.bin'),(0xb031,'shared-foreign-v22.bin')]:put(pc,(O/name).read_bytes())
 new['raw']=bytes(raw);return old,new


def seeds(bundles):
 out=[]
 for b in bundles:
  m=N.fresh(b);m.ram[2][:]=bytes(8192);m.ram[3][:]=bytes(8192)
  for row in range(38):
   target=0xa800+32*row;dest=0xc700+4*row
   code=bytearray()
   for op,offset in [(0x8d,0),(0x8e,1),(0x8c,2)]:code+=bytes([op,(dest+offset)&255,(dest+offset)>>8])
   code+=bytes([8,0x68,0x8d,(dest+3)&255,(dest+3)>>8,0xa9,0x40+row,0xa2,0x80+row,0xa0,0xc0+row,0x38 if row&1 else 0x18,0x60]);m.ram[3][target-0xa000:target-0xa000+len(code)]=code
   for origin in [0xa000,0xa500]:m.ram[3][origin-0xa000+3*row:origin-0xa000+3*row+3]=bytes([76,target&255,target>>8])
  m.ram[3][0x1b76]=0x60 # Typed genuine-retirement boundary, equal in both buses.
  m.raw_page(2,2);N.put(m,CurrentBankC=2,NmiDisable=1,ReloadCHRBank=0,FamilyMainCommit=1);out.append(m)
 return out


def call(seed,char,row,family,flags=0x31,args=(83,71,109),poison=None,interrupt=None,cmap=2):
 m=N.fork(seed);N.put(m,SelectedCharacter=char)
 cookie=(B/('native-visible-BB-cookie.bin'if char==39 else'common-current-Ex-cookie.bin')).read_bytes()if family=='Ex'else m.bundle['raw'][16+65*8192+0xa78:16+65*8192+0xa88]
 for bank in [2,3]:m.ram[bank][0x1fe0:0x1ff0]=cookie
 if poison is not None:m.ram[poison[0]][0x1fe0+poison[1]]^=1
 m.raw_page(2,cmap);N.put(m,CurrentBankC=cmap)
 target=(0xaa88 if family=='Sh'else 0xb08c)+3*row
 if row==37:assert family=='Ex';target=0xb029
 m[address(m.bundle,'SafecallA_SMC')+1]=args[0];m[address(m.bundle,'FarcallJmpTarget_SMC')+1]=target&255;m[address(m.bundle,'FarcallJmpTarget_SMC')+2]=target>>8
 c=N.NesMPU(memory=m,pc=address(m.bundle,'FarCallCommon'));c.a=193;c.x,c.y=args[1:];c.p=flags;c.sp=224;c.stPushWord(0x5aff);cuts=set();injected=False;low=c.sp;forward=False
 for _ in range(20000):
  if c.pc==0x5b00:break
  if c.pc==address(m.bundle,'NextBank_SMC')and m.rawtags[1]==193:forward=True;break
  low=min(low,c.sp);cut=(c.pc,c.sp,m.rawtags[1]);cuts.add(cut)
  if interrupt is not None and not injected and cut==interrupt[1]:
   injected=True;regs=(c.a,c.x,c.y,c.p,c.sp,c.pc);maps=m.rawtags[:];private=[bytes(x)for x in m.ram];scratch=bytes(m[3:11]);smc=bytes(m[0x15a:0x17b]);writes=len(m.ram_writes)
   assert not c.p&4;c.irq()if interrupt[0]=='IRQ'else c.nmi()
   for _ in range(200000):
    low=min(low,c.sp)
    if c.pc==regs[5]and c.sp==regs[4]:break
    assert m[c.pc]!=0,('Shared frame ISR BRK',interrupt,hex(c.pc));c.step()
   else:raise AssertionError(('Shared frame ISR bound',interrupt))
   if maps!=m.rawtags:
    op=bytes(m[c.pc:c.pc+3]);assert op in [bytes([0x8d,0x15,0x51]),bytes([0x8e,0x16,0x51]),bytes([0x8d,0x16,0x51])]
    window=1 if op[1]==0x15 else 2;shadow=N.get(m,'CurrentBank'if window==1 else'CurrentBankC');assert m.rawtags[window]==shadow and all(maps[i]==m.rawtags[i]for i in range(4)if i!=window)
   assert regs[:3]==(c.a,c.x,c.y)and regs[3]&0xef==c.p&0xef and regs[4:]==(c.sp,c.pc)
   assert private==[bytes(x)for x in m.ram]and scratch==bytes(m[3:11])and smc==bytes(m[0x15a:0x17b])
   assert not m.ram_writes[writes:]
  assert m[c.pc]!=0,('Shared transport BRK',hex(c.pc),char,row,family);c.step()
 else:raise AssertionError(('Shared transport bound',char,row,family,hex(c.pc)))
 assert (c.sp==224 or forward)and(interrupt is None or injected)
 return m,(c.a,c.x,c.y,c.p,c.sp),cuts,low,forward,c.processorCycles


def compare(a,z,context):
 x,r,*_=a;y,s,*_=z;assert r==s and x.ram==y.ram and x.rawtags==y.rawtags,(context,'register/private/map',r,s)
 assert bytes(x[:256])==bytes(y[:256])and bytes(x[0x200:0x8000])==bytes(y[0x200:0x8000]),(context,'native/ZP')
 assert bytes(x[0x15a:0x17b])==bytes(y[0x15a:0x17b]),(context,'live SMC',[(hex(i),x[i],y[i])for i in range(0x15a,0x17b)if x[i]!=y[i]])
 assert a[4]==z[4],(context,'native UI continuation')


def main():
 old,new=bundles();ss=seeds([old,new]);cases=foreign=typed=0
 for family in ['Sh','Ex']:
  for char in range(40):
   for row in range(38 if family=='Ex'else 37):
    for flags in [0x30,0xf1]:
     pair=[call(seed,char,row,family,flags,args=((row*7+char)&255,(row*3+char)&255,(row*11+char)&255))for seed in ss];compare(*pair,(family,char,row,flags));cases+=1;foreign+=int(char not in ([36]if family=='Sh'else[37,39]));typed+=int(row==37)
 extra=0
 for family,char in [('Sh',36),('Ex',37),('Ex',39)]:
  for row in range(37):
   for cmap in [0,1,216,255]:
    pair=[call(seed,char,row,family,args=(32,255,73),cmap=cmap)for seed in ss];compare(*pair,('Cmapping',family,char,row,cmap));extra+=1
 poison=0
 for family,char in [('Sh',36),('Ex',37),('Ex',39)]:
  for bank in [2,3]:
   for byte in range(16):
    pair=[call(seed,char,0,family,poison=(bank,byte))for seed in ss];compare(*pair,('header',family,char,bank,byte));assert not pair[1][1][3]&1;poison+=1
 cuts_count=0;minimum=224
 for family,char in [('Sh',36),('Ex',37),('Ex',39)]:
  base=call(ss[1],char,2,family);cuts=sorted(base[2])
  for kind in ['IRQ','lagNMI']:
   for cut in cuts:
    got=call(ss[1],char,2,family,interrupt=(kind,cut));x,r=base[:2];y,s=got[:2]
    # Actual IRQ may update native IRQ/OAM bookkeeping. Its immediate exact
    # return above proves private RAM/R0..7/SMC/AXYP and legal mapper restore;
    # final public continuation must also preserve those transport outputs.
    assert r==s and x.ram==y.ram and x.rawtags==y.rawtags
    # Genuine lag NMI builds the native VRAM pointer in ZP00/01 (reset.s
    # ContinueNMI); these two ISR-owned bytes are not foreground ABI scratch.
    assert bytes(x[2:256])==bytes(y[2:256])and bytes(x[0x15a:0x17b])==bytes(y[0x15a:0x17b])
    if kind=='IRQ':assert bytes(x[:2])==bytes(y[:2])
    minimum=min(minimum,got[3]);cuts_count+=1
 cycle_rows=[]
 for family,char in [('Sh',36),('Ex',37),('Ex',39)]:
  a,z=[call(seed,char,2,family)for seed in ss];cycle_rows.append(dict(family=family,rawID=char,row=2,old_cycles=a[5],new_cycles=z[5],delta=z[5]-a[5],scope='Real transport plus identical typed private callee fixture.'))
 q=dict(passed=True,private_CPU_only=True,ROM_written=False,shared_sources_written=False,symbolic_only=True,actual_fixed_public_row_cases=cases,foreign_cases=foreign,genuine_typed_B029_cases=typed,original_C_mapping_cases=extra,complete_header_byte_rejections=poison,real_IRQ_lagNMI_cuts=cuts_count,minimum_SP=minimum,uninterrupted_AXYP_SP_all_ZP_full_SMC_native_private_mapper_state_equal=True,ISR_AXYP_SP_R0_7_full_SMC_private_mapper_continuation_equal=True,lagNMI_native_scratch_exception='ZP00/01 native VRAM pointer, written by genuine ContinueNMI in src/reset.s; all other ZP and full SMC remain exact. Native ISR bookkeeping outside foreground scratch may advance.',cycle_cost=cycle_rows,conditional_source_funding=141,grant=False,current_composition_not_frozen=True,scope='Exact unchanged1966 Sh transport plus stable531B two-owner manager/typed178B Ex/BB frame in memory. All real fixed public veneers/raw0..39, typed private callee fixtures and native original UI forwarding boundary. No source actor/gameplay/native emulator qualification.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),R/'tools/audit/measure_prince_shared_frame_1102_v22.py',O/'shared-frame-v22.bin',O/'shared-selector-v22.bin',O/'shared-foreign-v22.bin',O/'shared-frame-measurement-v22.json',B/'native-visible-owner.bin',B/'native-proxy-routes.bin',B/'native-proxy-route-foreign.bin',R/'src/reset.s',L.BASE]})
 (O/'shared-frame-CPU-v22.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
