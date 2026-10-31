"""Read-only emitted donor, target-geometry and private data-consumer closure."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
P=R/'build/contra-force-projectile-contact-1031-v3';OLD=R/'build/contra-force-world-chr-publisher-1031-v1'
BASE=R/'build/contra-force-p1-kernel-v1';O=R/'build/contra-force-projectile-source-proof-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fields(line):return dict(x.split('=',1)for x in line.split('\t',1)[1].split(',')if '='in x)
def segments(p):return{fields(l)['name'].strip('"'):fields(l)for l in p.read_text().splitlines()if l.startswith('seg\t')}
def bounds(points):return[min(x for x,y in points),min(y for x,y in points),max(x for x,y in points),max(y for x,y in points)]
def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,source=True,native=False)
 refs=[Path(__file__),P/'source-stage.json',OLD/'source-stage.json',P/'kernel/runtime.dbg',OLD/'kernel/runtime.dbg',P/'joint/candidate.nes',P/'joint/candidate.dbg',P/'kernel/component.s',BASE/'component.s',P/'kernel/state.inc',BASE/'state.inc',P/'kernel/contact-runtime.s',P/'kernel/p1-runtime.s',P/'kernel/native-mask.s',BASE/'native-mask.s',P/'kernel-link.json',OLD/'kernel-link.json']
 try:
  old,new=segments(OLD/'kernel/runtime.dbg'),segments(P/'kernel/runtime.dbg');chunks=[]
  for n,s in old.items():
   if not n.startswith('CF_CHUNK_'):continue
   t=new[n];assert all(s[k]==t[k]for k in('start','size','oname','ooffs')),(n,s,t)
   size,pos=int(s['size'],0),int(s['ooffs'],0);oname=s['oname'].strip('"')
   a,b=OLD/'kernel'/oname,P/'kernel'/oname;refs.extend([a,b])
   assert a.read_bytes()[pos:pos+size]==b.read_bytes()[pos:pos+size],n
   chunks.append(dict(name=n,start=int(s['start'],0),size=size,image=oname,sha256=hashlib.sha256(a.read_bytes()[pos:pos+size]).hexdigest()))
  assert len(chunks)==232
  assert (P/'kernel/component.s').read_text()=='.export tbl_F94A\n'+(BASE/'component.s').read_text()
  assert (P/'kernel/state.inc').read_bytes()==(BASE/'state.inc').read_bytes()
  d['original_donor_chunks_byte_PC_image_exact']=chunks
  d['original_component_source_only_zero_byte_export']='tbl_F94A'
  tool=R/'tools/Windows/cc65/bin/od65.exe';refs.append(tool);imports=[]
  for path in json.loads((OLD/'kernel-link.json').read_text())['command']:
   if not path.endswith('.o'):continue
   refs.append(Path(path));z=subprocess.run([str(tool),'--dump-imports',path],capture_output=True,text=True);assert z.returncode==0
   if re.search(r'Name:\s+"CfNativeP1Mask"',z.stdout):imports.append(path)
  assert len(imports)==1 and Path(imports[0]).name=='p1-runtime.o',imports
  d['retired_private_data_export']=dict(name='CfNativeP1Mask',actual_old_object_consumers=imports,replacement='CfNativeP1MaskTail + exact bounded inline reader',new_public_entry_claim=False)
  b=qualified(P/'joint/candidate.nes');raw=b['raw'];at=lambda n:location(b,n)
  engine=at('EnemyGraphicsEngine::RunEngine');assert raw[engine]==0xb5 and raw[engine+2]==0x20
  handlers=['ProcessGreenKoopa','ProcessDemotedKoopa','ProcessBuzzyBeetle','ProcessRedKoopa','Noop','ProcessHammerBro','ProcessGoomba','ProcessBlooper','ProcessBulletBill','Noop','ProcessSwimmingCheepCheep','ProcessSwimmingCheepCheep','ProcessPodoboo','ProcessPiranhaPlant','ProcessJumpingParatrooper','ProcessRedFlyingParatrooper','ProcessGreenFlyingParatrooper','ProcessLakitu','ProcessSpiny','Noop','ProcessFlyingCheepCheep']
  table=raw[engine+5:engine+47];assert len(table)==42
  assert [table[i]+256*table[i+1]for i in range(0,42,2)]==[address(b,n)for n in handlers]
  d['actual_native_ID_handlers']=dict(enumerate(handlers))
  init=raw[at('CHRBankInitValues'):at('CHRBankInitValues')+12];physical=raw[at('ChrPhysicalMap'):at('ChrPhysicalMap')+256]
  pages=[physical[x]for x in init];assert pages[:8]==[14,16,17,18,19,20,21,21]
  groups={
   'koopa':['KOOPA_WALKING_1','KOOPA_WALKING_2','KOOPA_SHELL','KOOPA_SHELL_REVIVE'],
   'flying_koopa':['KOOPA_FLYING_1','KOOPA_FLYING_2'],
   'hammer':['HAMMER_BRO_WALK_1','HAMMER_BRO_WALK_2','HAMMER_BRO_THROW_1','HAMMER_BRO_THROW_2'],
   'goomba':['GOOMBA_WALKING_1','GOOMBA_WALKING_2'],
   'blooper':['BLOOPER_SWIM_1','BLOOPER_SWIM_2'],
   'cheep':['CHEEP_CHEEP_SWIM_1','CHEEP_CHEEP_SWIM_2'],
   'piranha':['PIRANHA_MOUTH_OPEN','PIRANHA_MOUTH_CLOSED'],
   'lakitu':['LAKITU_NORMAL','LAKITU_THROWING'],
   'spiny':['SPINY_WALK_1','SPINY_WALK_2','SPINY_EGG_1','SPINY_EGG_2']}
  union={};chr0=16+128*8192
  for family,poses in groups.items():
   allpoints=[];rows=[]
   for pose in poses:
    for face in ['LEFT','RIGHT']:
     name='MetaspriteData_'+pose+'_'+face;p=at(name);size=raw[p];record=raw[p+1:p+1+size];assert size%4==0
     points=[]
     for i in range(0,size,4):
      tile,attr,dy,dx=record[i:i+4];dx=dx-256 if dx&128 else dx;dy=dy-256 if dy&128 else dy
      pattern=(tile&1)*4096+(tile&254)*16
      for y in range(16):
       sy=15-y if attr&128 else y
       offset=pattern+(sy//8)*16+sy%8;page,within=divmod(offset,1024);o=chr0+pages[page]*1024+within
       lo,hi=raw[o],raw[o+8]
       for x in range(8):
        sx=7-x if attr&64 else x;bit=7-sx;color=((lo>>bit)&1)|(((hi>>bit)&1)<<1)
        if color:points.append((dx+x,dy+y))
     assert points;allpoints.extend(points);rows.append(dict(name=name,descriptor=list(record),raw_opaque_bounds=bounds(points),hardware_Y_is_raw_plus1=True))
   box=bounds(allpoints);assert box==([0,8,15,23]if family in('goomba','cheep','spiny')else[0,0,15,23]),(family,box)
   union[family]=dict(raw_opaque_family_union=box,poses=rows)
  d['compiled_native_body_geometry']=union
  target=[1,1,0,1,0,1,9,1,0,0,9,9,0,1,1,1,1,1,9,0,9]
  klabel={n:int(v,16)for v,n in re.findall(r'al ([0-9A-Fa-f]+) \.(\w+)',(P/'kernel/runtime.lbl').read_text())}
  assert list((P/'kernel/ram2.bin').read_bytes()[klabel['CfNativeTargetTop']-0xc000:klabel['CfNativeTargetTopEnd']-0xc000])==target
  d['target_policy']=dict(top_plus1=target,left=0,right=15,bottom=23,scope='Intentional static ordinary-species body-union rectangle in raw source/OAM coordinates. Transparent corners and compressed shell poses remain inside the family union. No per-pixel/per-shot target work; no equality claim to original donor enemy geometry or native player/fireball/stomp geometry. Bowser retains existing native typed bbox. Hardware adds one display Y to both source and target.')
  producers=[]
  for line in (P/'joint/candidate.dbg').read_text().splitlines():
   if not line.startswith('file\t'):continue
   f=fields(line);path=Path(f['name'].strip('"'))
   if path.name in('sprite_render.s','metasprite.s','constants.inc'):
    assert path.exists();producers.append(str(path));refs.append(path)
  d.update(passed=True,actual_DBG_producers=producers,all_other_native_player_contact_stomp_ROM_unchanged=True,scope='Read-only actual emitted donor chunks, real ordinary native dispatch/descriptor/pattern geometry, and sole old mask-import closure. No native execution or whole-level claim.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  d['bindings']={str(p.resolve()):sha(p)for p in set(refs)};p=O/'controls.json';p.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=d['passed'],error=d.get('error'))),flush=True)
if __name__=='__main__':main()
