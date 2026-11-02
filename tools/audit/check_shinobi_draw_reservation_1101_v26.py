"""Execute direct source draw and its native reservation boundary on v26."""
import hashlib,itertools,json
import prepare_shinobi_draw_reservation_1101_v26 as P
import check_hogan_current_bounded_v1 as M
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU


def run(m,pc,*,a=85,x=7,y=91,p=0x71,stop_jump=False):
 c=NesMPU(memory=m,pc=pc);c.a=a;c.x=x;c.y=y;c.p=p;c.sp=239;c.stPushWord(0x5aff)
 for _ in range(50000):
  if c.pc==0x5b00 or stop_jump and m[c.pc]==0x4c:break
  assert m[c.pc],('BRK',hex(c.pc),m.rawtags)
  c.step()
 else:raise AssertionError('CPU step bound')
 if not stop_jump:assert c.sp==239
 return c


def preload(b):
 m=M.Bus(b);raw=b['raw']
 kernel=b''.join(raw[16+1048576+p*1024:16+1048576+(p+1)*1024]for p in P.PAGES)
 meta=b''.join(raw[16+1048576+p*1024:16+1048576+(p+1)*1024]for p in [516,517])
 m.ram[3][:len(kernel)]=kernel;m.ram[2][0x1000:0x1800]=meta
 m.raw_page(1,3);m.raw_page(2,2)
 M.put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=36,Player_SprAttrib=0)
 return m


def reserve(m):
 b=m.bundle;pc=address(b,'RosterProjectileOamReady');bank=128|((location(b,'RosterProjectileOamReady')-16)//8192)
 m.raw_page(1,bank);m.raw_page(2,216)
 M.put(m,CurrentBank=bank,CurrentBankC=216)
 before=M.get(m,'CurrentOAMOffset');run(m,pc,stop_jump=True)
 assert M.get(m,'CurrentOAMOffset')==before,('duplicate/stale reservation',before,M.get(m,'CurrentOAMOffset'))
 assert M.get(m,'ObjectMetasprite')==0
 assert M.get(m,'SmPosePtr')+256*M.get(m,'SmPosePtr',1)==address(b,'ObjectMetasprite')


def main():
 old,new=scoped_load(P.BASE/'candidate.nes'),scoped_load(P.O/'candidate.nes')
 lab=P.S.labels(P.R/'build/shinobi-hurt-layout-1101-v5/component.lbl')
 def offset(pc):
  i=pc-0xa000;return 16+1048576+P.PAGES[i//1024]*1024+i%1024
 allowed={offset(pc)for pc in range(lab['ShHostDraw'],lab['ShRenderMasks'])}|set(range(16+65*8192+0xa78,16+65*8192+0xa88))
 changes=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
 assert len(old['raw'])==len(new['raw'])and set(changes)<=allowed
 assert all(old['raw'][offset(pc)]==new['raw'][offset(pc)]for pc in range(lab['ShSourceBounds'],lab['ShNativeCombatEnd']))
 poses=json.loads((P.R/'build/shinobi-component-1101-v2/pose-packets.json').read_text())['poses']
 cases=[(pose,0,0,128,224,0,True)for pose in poses]
 cases +=[(poses[0],prefix,rotation,x,y,bits,ready)for prefix,rotation,x,y,bits,ready in itertools.product([24,208,252],[4,252],[4,248],[32,224],[0,30],[True,False])]
 rows=[];digest=hashlib.sha256()
 for pose,prefix,rotation,x,y,bits,ready in cases:
  pair=[]
  for b in [old,new]:
   m=preload(b)
   M.put(m,CurrentOAMOffset=prefix,GuestOamRotationActive=int(rotation!=0),RgOamRotation=rotation,ObjectMetasprite=123,SmPosePtr=0x10)
   m[address(b,'SmPosePtr')+1]=0xa3
   for slot in range(5):
    for at,value in {0xc300:pose['pose'],0xc30b:pose['frame'],0xc363:pose['facing'],0xc379:x,0xc38f:y}.items():m[at+slot]=value
   m[0xc800]=167 if ready else 0;m[0xc810]=bits
   m[0xc880:0xc900]=[165]*128;m[0x200:0x300]=[248,0,0,0]*64
   scratch=bytes(range(161,169));m[3:11]=scratch
   c=run(m,lab['ShHostDraw'])
   assert(c.a,c.x,c.y,c.p&0xce)==(85,7,91,0x71&0xce)
   assert bytes(m[3:11])==scratch and m.rawtags[1:3]==[3,2]
   pair.append((bytes(m[0x200:0x300]),M.get(m,'CurrentOAMOffset'),c.processorCycles))
   if b is new:
    assert m[0xc80f]==0
    reserve(m)
    assert M.get(m,'CurrentOAMOffset')%4==0
  assert pair[0][:2]==pair[1][:2],('render changed',pose,prefix,rotation,x,y,bits,ready)
  row=[pose['pose'],pose['frame'],pose['facing'],prefix,rotation,x,y,bits,ready,pair[1][1],pair[0][2],pair[1][2]]
  rows.append(row);digest.update(repr(row).encode())
 # Actual authenticated cold scene and public HuDraw after a stale banked pointer.
 new['segs']['shinobi_rom']={'start':str(0xa800),'ooffs':str(16+65*8192+0x800)}
 for n,a in P.S.labels(P.R/'build/shinobi-scene-1101-v7/resident.lbl').items():
  if n.startswith('Sh')and 0xa800<=a<0xae00:new['syms'][n]={'val':str(a),'seg':'shinobi_rom'}
 m=M.fresh(new)
 M.put(m,SelectedCharacter=36,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160,Player_X_Position=120,Player_Y_Position=176,Player_Y_HighPos=1)
 M.invoke(m,'ShScene');assert m.ram[2][0x800]==167
 public=[]
 for rotation in [0,4,252]:
  M.put(m,CurrentOAMOffset=24,GuestOamRotationActive=1,RgOamRotation=rotation,ObjectMetasprite=123,SmPosePtr=0x10)
  m[address(new,'SmPosePtr')+1]=0xa3
  r=M.invoke(m,'HuDraw');assert r['P']&1
  assert m.rawtags[1]==M.get(m,'CurrentBank')and m.rawtags[2]==M.get(m,'CurrentBankC')
  reserve(m);public.append(dict(rotation=rotation,cursor=M.get(m,'CurrentOAMOffset'),cycles=r['CPU']))
 q=dict(passed=True,ROM_sha256=P.S.sha(P.O/'candidate.nes'),base_sha256=P.S.sha(P.BASE/'candidate.nes'),cases=len(rows),source_poses=len(poses),authenticated_HuDraw_cases=public,combat_span_exact=True,only_draw_span_and_cookie_changed=True,AXYP_except_handled_C_R0_R7_maps_preserved=True,ordered_OAM_and_cursor_exact=True,stable_zero_descriptor_after_maps_restored=True,trace_sha256=digest.hexdigest(),rows=rows,scope='Real cached ShHostDraw versus exact v23 baseline, all source poses plus clipping/capacity/rotation/projectile/not-ready cases; real RosterProjectileOamReady after restoring both ROM mappings. Actual cold authenticated ShScene and HuDraw. CPU fixtures only; no native video/Main/ISR/full1-1 claim.')
 (P.O/'draw-CPU.json').write_text(json.dumps(q,indent=2)+'\n')
 print(json.dumps({k:v for k,v in q.items()if k!='rows'}))
 import check_shinobi_contact_visible_1101_v23 as contact
 contact.P.O=P.O;contact.main()


if __name__=='__main__':main()
