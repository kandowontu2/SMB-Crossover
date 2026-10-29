"""Read-only conditional Gimmick lease checks on the actual ac126 parent."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import Memory,address
from verify_native_relocation import NesMPU
P=R/'build/pit-retold-host-v3/candidate.nes';O=R/'build/gimmick-component-v2'
EXPECTED='ac126b545ceb0c27f4843dbbf2eed647f07288a74a7a036d6769db6e3df0b1d2'
def bind(p):
 p=Path(p).resolve();z=p.read_bytes();return dict(path=str(p),bytes=len(z),sha256=hashlib.sha256(z).hexdigest())
LEASES=[(24,0xe80,0x1c00,'CORE_A24'),(122,0x1740,0x2000,'CORE_A122'),
        (75,0x19c0,0x2000,'COLD_A75'),(73,0x1920,0x2000,'ART_C73')]
class Watch(Memory):
 def __init__(self,b):
  self.hits=[];self.monitored=False;self.read_max={};super().__init__(b)
 def __getitem__(self,p):
  if isinstance(p,int)and 0x8000<=p<=0xffff and self.monitored:
   bank=self.banks[(p-0x8000)//8192];off=p&8191
   self.read_max[bank]=max(self.read_max.get(bank,0),off)
   for bk,lo,hi,n in LEASES:
    assert not(bank==bk and lo<=off<hi),('old consumer entered proposed lease',n,hex(p))
  return list.__getitem__(self,p)
def call(m,pc,a=0,x=0,y=0,limit=50000):
 c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.sp=a,x,y,0xfd;c.stPushWord(0x5aff);m.monitored=True
 for _ in range(limit):
  if c.pc==0x5b00:return c.processorCycles
  assert m[c.pc]!=0,('BRK',hex(c.pc));c.step()
 raise AssertionError(('old-owner call bound',hex(pc),hex(c.pc)))
def main():
 assert bind(P)['sha256']==EXPECTED
 assert not(O/'lease-proof.json').exists(),'preserve frozen receipt'
 b=scoped_load(P);extent=[]
 for bank,lo,hi,name in LEASES:
  blob=b['raw'][16+bank*8192+lo:16+bank*8192+hi];assert blob==b'\xff'*(hi-lo)
  overlaps=[];owners=[]
  for s in b['segs'].values():
   if 'ooffs'not in s or not int(s['size'],0):continue
   at=int(s['ooffs'],0)-16;end=at+int(s['size'],0)
   if at<(bank+1)*8192 and end>bank*8192:owners.append({k:s[k]for k in ['name','start','size','ooffs']})
   if at<bank*8192+hi and end>bank*8192+lo:overlaps.append(s)
  assert not overlaps,(name,overlaps)
  extent.append(dict(bank=bank,offset=[lo,hi],name=name,bytes=hi-lo,FF_sha256=hashlib.sha256(blob).hexdigest(),emitted_old_owners=owners))
 # Authentic native drivers, not wrapper aliases. Follow their actual indirect
 # data parsers for every native request/song; track every mapped ROM access.
 contra=[];gradius=[]
 for request in range(1,0x4e):
  m=Watch(b);m.page(1,23);m.page(2,24)
  call(m,address(b,'init_pulse_and_noise_channels'))
  call(m,address(b,'init_sound_code_vars'),a=request)
  cost=[]
  for _ in range(256):cost.append(call(m,address(b,'handle_sound_slots')))
  contra.append(dict(request=request,ticks=256,read_max=m.read_max,cycles=[min(cost),max(cost)]))
 for song in range(16):
  m=Watch(b);m.page(1,122);call(m,address(b,'GradiusNativeInit'),a=song)
  cost=[]
  for _ in range(256):cost.append(call(m,address(b,'GradiusNativePlay')))
  gradius.append(dict(song=song,ticks=256,read_max=m.read_max,cycles=[min(cost),max(cost)]))
 # Immutable source art bounds are label/record-derived, never FF inference.
 art=[]
 for name,s in b['syms'].items():
  if 'seg'not in s:continue
  g=b['segs'][s['seg']]
  if g.get('name')in ['"KIRBY_GFX"','"VIC_CORE"']:
   at=int(s['val'],0);assert at<int(g['start'],0)+int(g['size'],0)or at==int(g['start'],0)+int(g['size'],0)
   art.append(name)
 O.mkdir(exist_ok=True)
 sources=[P,P.with_suffix('.dbg'),P.with_suffix('.lbl'),R/'src/audio/roster/contra.inc',
  R/'build/generated/guest-audio/contra.inc',R/'src/gradius_audio.s',R/'src/gradius-native.inc',
  R/'src/kirby_art.inc',R/'src/kirby_copy_icons.inc',R/'src/meta_knight_art.inc',
  R/'src/vic_native_motion.s',R/'src/vic_native_weapons.s',R/'src/vic_gear.s',R/'src/vic_world_queries.s',Path(__file__)]
 proof=dict(status='PRIVATE_CONDITIONAL_LEASE_CHECK_PARTIAL',parent=bind(P),leases=extent,
  actual_Contra_requests=contra,actual_Gradius_songs=gradius,old_graphics_or_core_labels=len(art),
  source_scope='All77 native Contra request IDs and16 original Gradius init IDs each256 actual ticks, mapped indirect-ROM reads tracked. No instruction/service stubs. This finite campaign does not prove arbitrary corrupted stream pointers or the entire legal song duration; complete source pointer/record ownership review remains required before allocation is called closed.',
  bindings=[bind(p)for p in sources])
 (O/'lease-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(proof=bind(O/'lease-proof.json'),contra=len(contra),gradius=len(gradius))))
if __name__=='__main__':main()
