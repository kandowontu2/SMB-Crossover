"""Native atlas and remaining direct-OAM tile ownership of Tank window5."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_visible_1101_v5 import O,P,PIN
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 b=scoped_load(P/'candidate.nes');r=b['raw'];assert sha(r)==PIN;records=[];flowers=[];pairs=set()
 limit=address(b,'METASPRITE_MEGAMAN_STANDING');assert limit==145
 for face in ['Right','Left']:
  lo=location(b,'MetaspriteTable'+face+'Lo');hi=location(b,'MetaspriteTable'+face+'Hi');base=lo-address(b,'MetaspriteTable'+face+'Lo')
  for i in range(1,limit):
   ptr=r[lo+i]+256*r[hi+i];at=base+ptr;n=r[at];assert n%4==0 and n<=252
   tiles=[r[at+j]for j in range(1,n+1,4)];assert not any(t&1 and 0x40<=t<0x80 for t in tiles),(face,i,tiles)
   if any(t in[0x78,0x7a]for t in tiles):flowers.append((face,i,tiles))
   pairs.update(tiles);records.append((face,i,ptr,n,sha(r[at:at+n+1])))
 assert [(face,i)for face,i,t in flowers]==[('Right',64),('Left',64)]
 direct={n:address(b,n)for n in['BRICK_CHUNK_TILE','PLATFORM_GIRDER','VINE_TILE_1','VINE_TILE_2','FIREBALL_TILE1','FIREBALL_TILE2']}
 for n,t in direct.items():assert not(t&1 and 0x40<=t<0x80)and t not in[0x78,0x7a],(n,t)
 rows=[]
 for n in ['FirebarSprite1','FirebarSprite2','DrawBrickDebris::Chunk']:
  at=location(b,n);data=r[at:at+1+r[at]];tiles=list(data[1::4]);assert not any((t&1 and 0x40<=t<0x80)or t in[0x78,0x7a]for t in tiles);rows.append(dict(name=n,hex=data.hex(),tile_values=tiles))
 root=R/'build/bt-ready-menu-1031-v2/joint/src';paths=[root/n for n in['metasprite_engine.s','metasprite.s','native_goomba_draw.s','world_firebars.s','ryu_platform.s','sprite_render.s','megaman_weapons.s']]
 s=(root/'native_goomba_draw.s').read_text();assert 'lda (Ptr),y' in s and 'cmp #<MetaspriteData_GOOMBA_WALKING_2_RIGHT'in s
 s=(root/'metasprite_engine.s').read_text();assert 'ldy FloateyNum_Control,x\n  ldx FloateyNumMetasprites-1,y' in s
 q=dict(passed=True,current_ROM_sha256=PIN,native_fixed_record_faces=len(records),native_indices_half_open=[1,145],native_fixed_record_digest=sha(json.dumps(records).encode()),sprite_window5_native_reference_count=0,only_native_flower_tile_users=flowers,native_direct_tile_constants=direct,real_direct_dynamic_records=rows,source_contract='RawMario0 native world uses fixed1..144; native score maps back into that atlas. Goomba kernel reads authenticated fixed Goomba pointers. Native debris/firebar/vine/small-platform direct tiles are disjoint window5 and78/7A. Guest family shot/art branches remain declined by SelectedCharacter0; no extra guest tile emitter is admitted by Tank7.',window5_allocation=dict(physicalCHR=502,masks_tiles=[0x41,0x65],pickup_tiles=[0x67,0x69],original_pickup_top_bottom_four_cell_descriptor=True),limits=['Hostile cheats that manually force arbitrary guest metasprite IDs into native objects are outside this typed native domain.','This closes native tile numbers and chosen software window, not cycle-accurate rendered pixels or Mesen visual qualification.'],bindings={str(p.relative_to(R)):sha(p.read_bytes())for p in paths+[Path(__file__)]})
 (O/'native-art-ownership.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,native_records=len(records),native_window5_references=0,flower_records=len(flowers))))
if __name__=='__main__':main()
