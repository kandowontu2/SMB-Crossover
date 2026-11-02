"""CPU proof for the assembly-only bbox design; never writes a ROM file."""
import copy,hashlib,itertools,json
import prepare_shinobi_bbox_design_1101_v29 as P
import check_shinobi_draw_reservation_1101_v26 as D
import check_hogan_current_bounded_v1 as M
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load


def proposal():
 old=scoped_load(P.BASE);new=copy.deepcopy(old);raw=bytearray(old['raw']);lab=P.S.labels(P.O/'resident-design.lbl')
 k=P.S.labels(P.R/'build/shinobi-hurt-layout-1101-v5/component.lbl')
 def at(pc):
  i=pc-0xa000;return 16+1048576+P.PAGES[i//1024]*1024+i%1024
 resident=(P.O/'resident-design.bin').read_bytes();start=16+65*8192+0x800
 raw[start:start+1536]=resident+bytes([255])*(1536-len(resident))
 # No foreign identity can execute cached code through this native ingress.
 hook=16+77*8192+0xb09
 original=bytes.fromhex('8d6a01a91b8d6c01a9ac8d6d01a9d94c5a01');assert raw[hook:hook+18]==original
 replacement=bytearray(original);replacement[4]=lab['ShBBoxIngress']&255;replacement[9]=lab['ShBBoxIngress']>>8;replacement[14]=193;raw[hook:hook+18]=replacement
 for pc in range(0xa000,0xbc00-2):
  if bytes(raw[at(pc+i)]for i in range(3))==bytes.fromhex('bdf8ba'):
   assert pc==0xb558,hex(pc)
   for i,v in enumerate(bytes.fromhex('bd36ef')):raw[at(pc+i)]=v
 code=(P.O/'body-design.bin').read_bytes()
 for i,v in enumerate(code+bytes([234])*(256-len(code))):raw[at(0xbaf8+i)]=v
 for row,target in [(11,k['ShReject']),(16,0xbaf8)]:
  for i,v in enumerate([76,target&255,target>>8]):raw[at(0xa000+3*row+i)]=v
 # Existing external source-owned entries moved by the30-byte compaction.
 for hook,name in [(16+66*8192+0x1957+18,'ShMenuResolve'),(location(old,'MegaManFullShotBank'),'ShShotBankGate')]:
  call=bytearray(raw[hook:hook+18]);assert call[0:3]==bytes.fromhex('8d6a01')
  call[4]=lab[name]&255;call[9]=lab[name]>>8;call[14]=193;raw[hook:hook+18]=call
 def page(p):return raw[16+1048576+p*1024:16+1048576+(p+1)*1024]
 cookie=bytes([167,36,1])+hashlib.sha256(b''.join(page(p)for p in P.PAGES+[516,517,503,504,505,517])).digest()[:13]
 raw[16+65*8192+0xa78:16+65*8192+0xa88]=cookie
 new['raw']=raw;new['segs']['shinobi_rom']={'start':str(0xa800),'ooffs':str(start)}
 for n,a in lab.items():
  if n.startswith('Sh')and 0xa800<=a<0xae00:new['syms'][n]={'val':str(a),'seg':'shinobi_rom'}
 if hasattr(P,'CANDIDATE'):
  final=scoped_load(P.CANDIDATE);current=scoped_load(P.CURRENT_BASE)
  delta=[i for i,(a,b)in enumerate(zip(old['raw'],raw))if a!=b]
  changes=set(delta)
  assert all(final['raw'][i]==raw[i]and current['raw'][i]==old['raw'][i]for i in delta)
  assert all(a==b for i,(a,b)in enumerate(zip(current['raw'],final['raw']))if i not in changes)
  old=current;new['raw']=final['raw']
 return old,new,k


def foreign(old,new):
 seeds=[M.fresh(b)for b in [old,new]];count=0;digest=hashlib.sha256();sunny=0
 cpu=M.NesMPU;hits=[]
 class Trace(cpu):
  def step(self):
   if self.pc==0xab09 and self.memory.rawtags[1]==205:hits.append(M.get(self.memory,'SelectedCharacter'))
   return super().step()
 contexts=[(0,0,0,0),(3,16,1,1),(120,64,0,0),(240,176,1,0),(250,239,0,1),(255,250,1,1)]
 M.NesMPU=Trace
 try:
  for owner,(x,y,crouch,pose),flags in itertools.product([n for n in range(256)if n!=36],contexts,[0x30,0x31,0x70,0xf1]):
   pair=[];before_hits=len(hits)
   for seed in seeds:
    m=M.fork(seed);M.put(m,SelectedCharacter=owner,Player_Rel_XPos=x,Player_Rel_YPos=y,Player_X_Position=x,Player_Y_Position=y,Player_Y_HighPos=1,CrouchingFlag=crouch,Cv3Variant=pose)
    m.ram[2][0x70]=0x87 if pose else 0;m[0x6c0f]=crouch
    r=M.invoke(m,'LmBoundingBoxGate',a=0xa5,x=0,y=0,p=flags)
    pair.append((tuple(r[n]for n in ['A','X','Y','P']),bytes(m[:256]),bytes(m[0x200:0x800]),[bytes(z)for z in m.ram],m.rawtags,[M.get(m,n)for n in ['CurrentBank','CurrentBankC']]))
   assert pair[0]==pair[1],('Foreign body changed',owner,x,y,crouch,pose,flags,pair[0][0],pair[1][0])
   if owner==19:assert len(hits)==before_hits,'Sunny entered proposed fallback';sunny+=1
   count+=1;digest.update(repr([owner,x,y,crouch,pose,flags,pair[0][0]]).encode())
 finally:M.NesMPU=cpu
 return dict(passed=True,cases=count,all_255_foreign_raw_values_exact=True,Sunny_cases_bypass_shared_hook=sunny,trace_sha256=digest.hexdigest(),compared='Actual full LmBoundingBoxGate chain: AXYP, ZP, RAM0200..07FF, all four PRG-RAM banks, mapping and bank mirrors. Stack scratch and intermediate mapper bus writes excluded.')


def own(old,new,k):
 seed=M.fresh(new);M.put(seed,SelectedCharacter=36,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160)
 M.invoke(seed,'ShScene');assert seed.ram[2][0x800]==167
 poses=sorted(set(z['pose']for z in json.loads((P.R/'build/shinobi-hurt-layout-1101-v5/pose-packets.json').read_text())['poses']))
 cases=0;cycles=[];digest=hashlib.sha256()
 for pose,(x,y,ypage,camera),flags in itertools.product(poses,[(0,0,1,0),(3,16,1,506),(120,64,1,0),(240,176,1,506),(250,239,1,0),(120,250,1,506),(120,250,0,0),(120,8,2,506)],[0x30,0xf1]):
  m=M.fork(seed);world=camera+x
  M.put(m,Player_X_Position=world&255,Player_PageLoc=world>>8,Player_Y_Position=y,Player_Y_HighPos=ypage,Player_Rel_XPos=x,Player_Rel_YPos=y,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8)
  m.ram[2][0x300]=pose;m.ram[2][0x363]=4
  # Stale viewport coordinates differ deliberately, as after real native scroll.
  for at,v in [(0x379,177),(0x384,0),(0x38f,201),(0x39a,0)]:m.ram[2][at]=v
  source=bytes(m.ram[2][0x300:0x482]);scratch=bytes(range(0xa1,0xa9));m[3:11]=scratch;oam=bytes(m[0x200:0x300])
  reference=D.preload(old)
  for name in ['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','ScreenLeft_X_Pos','ScreenLeft_PageLoc']:M.put(reference,**{name:M.get(m,name)})
  reference[0xc300]=pose;reference[0xc363]=4
  D.run(reference,k['ShImportPosition']);c=D.run(reference,k['ShSourceBounds'],x=0)
  expected=[255]*4
  if c.p&1:
   left,right,top,bottom=[reference[0xc000+i]+256*reference[0xc001+i]for i in [8,10,12,14]];top-=32;bottom-=32
   if left<256 and top<256 and bottom>=0:expected=[left,max(0,top),min(right,255),min(bottom,255)]
  abi=M.invoke(M.fork(m),'ShCheckCode',a=85,x=0,y=0,p=flags)
  r=M.invoke(m,'HuFullBox',a=85,x=0,y=0,p=flags)
  assert list(m[address(new,'BoundingBox_UL_Corner'):address(new,'BoundingBox_UL_Corner')+4])==expected,(pose,x,y,ypage,camera,expected)
  assert [r[n]for n in ['A','X','Y','P']]==[abi[n]for n in ['A','X','Y','P']]
  assert bytes(m[3:11])==scratch and bytes(m[0x200:0x300])==oam
  assert bytes(m.ram[2][0x300:0x482])==source,'Source actor state changed'
  cases+=1;cycles.append(r['CPU']);digest.update(repr([pose,x,y,ypage,camera,flags,expected]).encode())
 return dict(passed=True,cases=cases,original_source_pose_bounds_exact=True,current_camera_used_without_mutating_actor=True,AXYP_except_handled_C_R0_R7_OAM_preserved=True,cycles=[min(cycles),max(cycles)],trace_sha256=digest.hexdigest())


def main():
 old,new,k=proposal();q=dict(passed=False,ROM_written=False,baseline_sha256=P.S.sha(getattr(P,'CURRENT_BASE',P.BASE)),ROM_sha256=P.S.sha(P.CANDIDATE)if hasattr(P,'CANDIDATE')else None)
 q['foreign']=foreign(old,new);q['own']=own(old,new,k);q['passed']=True
 q['scope']='In-memory assembly proposal or exact specified ROM candidate. All-owner native hook and original source pose box CPU proof; this check writes no ROM and makes no installed/native/controller/ISR or injury-compaction qualification.'
 (getattr(P,'CHECK_OUTPUT',P.O)/'CPU-design.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
