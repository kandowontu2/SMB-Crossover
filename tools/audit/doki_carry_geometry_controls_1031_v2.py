"""Actual original carried-position prefixes, preserving all source code."""
from pathlib import Path
import hashlib,json,re,sys,traceback
from py65.devices.mpu6502 import MPU
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location,Memory as CartMemory
P=R/'build/doki-original-rebuild-1031-v1';H=R/'build/doki-original-physics-audit-1031-v2/audit.json';O=R/'build/doki-carry-geometry-controls-1031-v2'
INST=R/'build/contra-force-world-chr-publisher-1031-v1/joint/candidate.nes';US=R.parent/'mario in kid icarus/vendor/smb2';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,source_CPU=True,native=False,cases=[])
 try:
  q=json.loads(H.read_text());assert q['passed'];original=(P/'original-files/main_pro.bin').read_bytes();rebuilt=(P/'assembled/main_pro.bin').read_bytes();temp=(P/'original-files/temp_prg.bin').read_bytes();raw=Path('C:/NES/Super Mario Bros. 2 (USA).nes').read_bytes();b=qualified(INST)
  D={};U={}
  for l in(P/'assembled/original.dbg').read_text().splitlines():
   if l.startswith('sym\t'):
    z=dict(x.split('=',1)for x in l[4:].split(',')if '='in x)
    if 'val'in z:D[z['name'].strip('"')]=int(z['val'],0)
  # Load RAM labels plus only the genuine1/2 source labels needed here, avoiding
  # coincidentally same-address music labels from the unrelated3/4 bank pair.
  for p in[US/'bin/native.nes.ram.nl',US/'bin/native.nes.1.nl']:
   for l in p.read_text().splitlines():
    m=re.match(r'\$([0-9a-fA-F]+)#([^#]+)#',l)
    if m:U[m[2]]=int(m[1],16)
  for l in(US/'bin/native.nes.2.nl').read_text().splitlines():
   m=re.match(r'\$([0-9a-fA-F]+)#ItemCarryYOffsets#',l)
   if m:U['ItemCarryYOffsets']=int(m[1],16)
  start=D['actor_throw'];blob=original[start-0x6000:start-0x6000+180];stop=start+blob.index(bytes([0x95,D['pos_y_hi_actor'],0xc0,5]))+2
  assert original[start-0x6000:stop-0x6000]==rebuilt[start-0x6000:stop-0x6000]
  d['Doki_prefix']=dict(CPU=[start,stop],disk_offset=1869+start-0x6000,bytes=stop-start,exact_original_source_assembled=True,hex=original[start-0x6000:stop-0x6000].hex())
  fields=['x','xh','y','yh','face','animation','heldstage','hitbox','actorindex','actorX','actorXH','actorY','actorYH','actorface']
  names={
   'DDP':['pos_x_lo_player','pos_x_hi_player','pos_y_lo_player','pos_y_hi_player','player_dir','player_ani_frame','timer_actor_held','col_box_actor','actor_index','pos_x_lo_actor','pos_x_hi_actor','pos_y_lo_actor','pos_y_hi_actor','disp_dir_actor'],
   'USA':['PlayerXLo','PlayerXHi','PlayerYLo','PlayerYHi','PlayerDirection','PlayerAnimationFrame','ObjectBeingCarriedTimer','ObjectHitbox','byte_RAM_12','ObjectXLo','ObjectXHi','ObjectYLo','ObjectYHi','EnemyMovementDirection'],
   'S2':['S2X','S2Page','S2Y','S2YPage','S2Face','S2Animation','S2ObjectLift','S2ObjectHitbox','S2Source12','S2X','S2Page','S2Y','S2YPage','S2ObjectFacing0']}
  F={k:dict(zip(fields,[(D if k=='DDP'else U)[n]if k!='S2'else address(b,n)for n in ns]))for k,ns in names.items()}
  for n in ['actorX','actorXH','actorY','actorYH']:F['S2'][n]+=1
  starts={'DDP':start,'USA':U['CarryObject'],'S2':address(b,'S2O960F')};stops={'DDP':stop,'USA':0x966e,'S2':address(b,'S2CarryGeometryReturn')}
  def at1(n,count):
   off=16+(2 if n=='ItemCarryYOffsets'else 1)*16384+U[n]-0x8000;return raw[off:off+count]
  offsetTable=at1('ItemCarryYOffsets',28)
  class Flat:
   def __init__(self,kind):
    self.m=bytearray(65536)
    if kind=='DDP':self.m[0x6000:0xe000]=original;self.m[0x6000:0x65ff]=temp
    else:self.m[0x8000:0xc000]=raw[16+16384:16+2*16384];self.m[0xc000:]=raw[16+7*16384:16+8*16384]
   def __getitem__(self,p):return self.m[p]
   def __setitem__(self,p,v):self.m[p]=v&255
  for v in range(4):
   native=[0,1,3,2][v]
   for face in[0,1]:
    for crouch in[0,4]:
     for stage in[1,4,7]:
      row=dict(character=q['stats'][v]['name'],face=face,crouch=bool(crouch),lift_stage=stage,engines={})
      for kind in F:
       if kind=='S2':m=CartMemory(b);m.page(1,(location(b,'S2O960F')-16)//8192);m[address(b,'S2NativeCharacter')]=native
       else:m=Flat(kind)
       if kind=='USA':
        p=U['ItemCarryYOffsetsRAM'];m[p:p+28]=offsetTable;m[U['CurrentCharacter']]=native
        for i,n in[(0,'CarryYOffsetBigLo'),(7,'CarryYOffsetSmallLo'),(14,'CarryYOffsetBigHi'),(21,'CarryYOffsetSmallHi')]:m[p+i]=at1(n,4)[native]
       vals=dict(x=128,xh=1,y=100,yh=0,face=face,animation=crouch,heldstage=stage,hitbox=0,actorindex=0)
       for n,value in vals.items():m[F[kind][n]]=value
       c=MPU(memory=m,pc=starts[kind]);c.sp=253;c.p=0x24;c.x=0
       for _ in range(1000):
        if c.pc==stops[kind]:break
        assert m[c.pc]!=0,(kind,hex(c.pc));c.step()
       else:raise AssertionError('Carry prefix bound')
       row['engines'][kind]={n:m[F[kind][n]]for n in ['actorX','actorXH','actorY','actorYH','actorface']}
      assert row['engines']['USA']==row['engines']['S2'],row;d['cases'].append(row)
  d.update(passed=True,cases_count=len(d['cases']),original_USA_installed_S2_bigform_exact=True,source_Doki_fixed_crouch_offset=8,scope='Actual original carry prefixes through world-coordinate commit, stop before original native renderer. Explicit valid big-form held-actor setup/real original carry-table initialization. No visual/natural-pickup/collision/admission claim. Doki fixed carry/fixed+crouch8 must be retained separately from SMB2U per-character/small-form tables.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  refs=[Path(__file__),H,P/'original-files/main_pro.bin',P/'original-files/temp_prg.bin',P/'assembled/main_pro.bin',P/'assembled/original.dbg',INST,INST.with_suffix('.dbg'),US/'src/prg-2-3.asm',P/'source/src/obj/actor/throw.s'];d['bindings']={str(p.resolve()):sha(p)for p in refs};p=O/'controls.json';p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=d['passed'],error=d.get('error'))),flush=True)
if __name__=='__main__':main()
