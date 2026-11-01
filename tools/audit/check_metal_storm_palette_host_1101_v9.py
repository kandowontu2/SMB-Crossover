"""Original-source shape, real native world/OAM coexistence and palette tests."""
from pathlib import Path
import collections,hashlib,itertools,json,sys,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
import prepare_metal_storm_palette_host_1101_v9 as P
import metal_storm_cpu_1101_v2 as M
from arthur_cache_host_controls_v1 import OverlayMemory
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
from PIL import Image,ImageDraw
OUT=P.OUT;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
# Display-only classic NES RGB lookup. All fidelity decisions below compare
# original NES color indices, not this monitor-dependent visualization.
RGB=[(124,124,124),(0,0,252),(0,0,188),(68,40,188),(148,0,132),(168,0,32),(168,16,0),(136,20,0),(80,48,0),(0,120,0),(0,104,0),(0,88,0),(0,64,88),(0,0,0),(0,0,0),(0,0,0),
 (188,188,188),(0,120,248),(0,88,248),(104,68,252),(216,0,204),(228,0,88),(248,56,0),(228,92,16),(172,124,0),(0,184,0),(0,168,0),(0,168,68),(0,136,136),(0,0,0),(0,0,0),(0,0,0),
 (248,248,248),(60,188,252),(104,136,252),(152,120,248),(248,120,248),(248,88,152),(248,120,88),(252,160,68),(248,184,0),(184,248,24),(88,216,84),(88,248,152),(0,232,216),(120,120,120),(0,0,0),(0,0,0),
 (252,252,252),(164,228,252),(184,184,248),(216,184,248),(248,184,248),(248,164,192),(240,208,176),(252,224,168),(248,216,120),(216,248,120),(184,248,184),(184,248,216),(0,252,252),(248,216,248),(0,0,0),(0,0,0)]

def sourcepixels(cells,data,anchor=(128,112),mapping=None,palette0=False):
 out={}
 for cell in cells:
  a=cell['attributes'];pattern=P.decode(data[cell['pattern_index']*32:cell['pattern_index']*32+32])
  for yy,xx in itertools.product(range(16),range(8)):
   v=pattern[15-yy if a&128 else yy][7-xx if a&64 else xx]
   if mapping is not None:v=mapping[v]
   x,y=anchor[0]+cell['dx']+xx,anchor[1]+cell['dy']+yy
   if v and 0<=x<256 and 0<=y<240:out.setdefault((x,y),(0 if palette0 else a&3,v))
 return out

def main():
 q=dict(passed=False,native=False,installed=False,resource_granted=False)
 try:
  stage=json.loads((OUT/'palette-assembly.json').read_text());inputs=json.loads((OUT/'palette-inputs.json').read_text());w=json.loads((P.V8/'native-witness.json').read_text());callers=json.loads((OUT/'native-palette-callers.json').read_text());art=json.loads((P.V7/'art.json').read_text())
  for packet in[stage,callers]:
   for p,h in packet['bindings'].items():assert sha(p)==h,p
  body=(P.V7/'body.chr').read_bytes();shots=(P.V7/'shots.chr').read_bytes();raw=bytearray(w['raw_length'])
  for s in w['spans']+callers['spans']:raw[s['offset']:s['offset']+s['size']]=bytes.fromhex(s['hex'])
  for key,h in inputs['native_patterns'].items():
   page,pos=map(int,key.split(':'));at=1048592+page*1024+pos;raw[at:at+32]=bytes.fromhex(h)
  for r in inputs['native_descriptors']:
   p=bytes.fromhex(r['descriptor_hex']);raw[r['file_offset']:r['file_offset']+len(p)]=p
  syms=dict(w['syms']);syms.update(callers['syms']);b=dict(raw=raw,syms=syms,segs=w['segs']);minimum=224;helperhits=collections.Counter();digest=hashlib.sha256();previews={};maxcycles=0
  def put(m,**kw):
   for n,v in kw.items():m[address(b,n)]=v
  def run(m,pc,a=85,x=7,y=91,p=0x71,ports=()):
   nonlocal minimum,maxcycles
   c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=a,x,y,p,224;c.stPushWord(0x5ffe);start=c.processorCycles
   for _ in range(100000):
    if c.pc==0x5fff:break
    minimum=min(minimum,c.sp)
    if c.pc in ports or(isinstance(m,OverlayMemory)and m.rawtags[1]==128 and c.pc==address(b,'SprObjectOffscrChk')):
     c.pc=(c.stPopWord()+1)&65535;continue
    if c.pc==address(b,'LmPrivateGate')and isinstance(m,OverlayMemory)and m.rawtags[1]==221:
     # Ordinary world object: the existing private-pickup gate declines. Its
     # transport and carry consumer execute, but its own actor cache is outside
     # this scoped native palette-caller fixture.
     c.p&=254;c.pc=(c.stPopWord()+1)&65535;continue
    if isinstance(m,OverlayMemory):
     for name,tag in[('MetaspriteRenderLoop',132),('X5SetPhysicalChr',190),('X5PublishChr',190),('DrawPowerUp',128),('DrawBlock',128)]:
      if m.rawtags[1]==tag and c.pc==address(b,name):helperhits[name]+=1
    assert m[c.pc]!=0,('BRK',hex(c.pc),getattr(m,'rawtags',None));c.step()
   else:raise AssertionError(('CPU bound',hex(c.pc)))
   assert c.sp==224;maxcycles=max(maxcycles,c.processorCycles-start)
   return c.a,c.x,c.y,c.p&0xcf
  def make(name):
   v=stage['variants'][name];actor=(OUT/(name+'-actor.bin')).read_bytes();render=(OUT/(name+'-render.bin')).read_bytes();chrdata=(OUT/(name+'.chr')).read_bytes()
   raw[1048592+495*1024:1048592+500*1024]=chrdata
   m=OverlayMemory(b);m.raw_page(1,3);m.raw_page(2,2);m.ram[3][:len(actor)]=actor;m.ram[2][0xd00:0xd00+len(render)]=render
   put(m,CurrentBank=3,CurrentBankC=2,SelectedCharacter=35,OperMode=1,GameEngineSubroutine=8,CurrentOAMOffset=0,GuestOamRotationActive=0,RgOamRotation=0,SsChrActive=0,InvHudActive=0,X5WideChrActive=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,Player_SprAttrib=0,VRAM_Buffer1_Offset=0)
   m[0xc800]=167
   for i in range(11):m[i]=(29*i+17)&255
   for i,logical in enumerate(inputs['native_CHR_init_logical']):m[address(b,'CurrentCHRBank')+i]=logical;m[address(b,'X5ChrMode')+i]=0
   m[0x200:0x300]=bytes([240,0,0,0])*64;m.writes.clear();m.ram_writes.clear();return m
  def invoke(m,name,which):
   abi=bytes(m[:11]);smc=bytes(m[i]for i in[0x16a,0x16c,0x16d]);maps=m.rawtags[:]
   got=run(m,stage['variants'][name]['labels'][which]);assert got==(85,7,91,0x41),(which,got)
   assert bytes(m[:11])==abi and bytes(m[i]for i in[0x16a,0x16c,0x16d])==smc and m.rawtags==maps,which
  def publish(m):
   old=m.rawtags[1];m.raw_page(1,190);put(m,CurrentBank=190);run(m,address(b,'X5PublishChr'));m.raw_page(1,old);put(m,CurrentBank=old)
  def image(m,lo=0,hi=None):
   out={};cells=[]
   if hi is None:hi=m[address(b,'CurrentOAMOffset')]
   for off in range(lo,hi,4):
    y,t,a,x=m[0x200+off:0x204+off];slot=(t&1)*4+((t&254)*16)//1024;page=m.chr_latches[slot];at=1048592+page*1024+((t&254)*16)%1024;pattern=bytes(raw[at:at+32]);cells.append([y,t,a,x,page])
    for xy,v in sourcepixels([dict(dx=x,dy=y+1,attributes=a,pattern_index=0)],pattern,(0,0)).items():out.setdefault(xy,v)
   return out,cells
  def setbody(m,r,anchor=(128,112)):
   for a,v in{0x480:anchor[0]&255,0x498:anchor[0]>>8,0x4b0:anchor[1]%240,0x4c8:(anchor[1]//240)&255,0x510:128,0x4e0:r['state'],0x4f8:r['frame'],0x540:r['facing']|r['gravity']}.items():m[0xc000+a]=v
  def setshot(m,r,slot=2,anchor=(128,112)):
   for a,v in{0x480:anchor[0]&255,0x498:anchor[0]>>8,0x4b0:anchor[1]%240,0x4c8:(anchor[1]//240)&255,0x510:128,0x528:r['type'],0x540:r['flags'],0x558:0 if r['vertical']else 12,0x630:r['phase'],0x648:0}.items():m[0xc000+a+slot]=v
  def world(m,r,anchor=(128,112)):
   old=m.rawtags[1];oldbank=m[address(b,'CurrentBank')];m.raw_page(1,132);put(m,CurrentBank=132)
   packet=bytes.fromhex(r['descriptor_hex']);m[0x5ca0:0x5ca0+len(packet)]=packet
   put(m,R0=160,R1=92,R3=r['native_R3'],R4=anchor[0],R5=0,R6=anchor[1],R7=1)
   lo=m[address(b,'CurrentOAMOffset')];run(m,address(b,'MetaspriteRenderLoop'));hi=m[address(b,'CurrentOAMOffset')]
   m.raw_page(1,old);put(m,CurrentBank=oldbank);return lo,hi
  bodycases=shotcases=queuecases=worldcases=0;world_p0_exceptions=[];scenes=[]
  for name,v in stage['variants'].items():
   for kind,records,data in[('body',art['body_packets'],body),('shot',art['shot_packets'],shots)]:
    for r in records:
     if kind=='shot'and r['type']==131 and r['phase']>2:continue
     m=make(name)
     if kind=='body':setbody(m,r)
     else:setshot(m,r)
     invoke(m,name,'MsRenderDraw');publish(m);got,_=image(m);original=sourcepixels(r['cells'],data);want=sourcepixels(r['cells'],data,mapping=v[kind],palette0=True)
     assert set(got)==set(original)and got==want,('shape/remap',name,kind,r)
     assert all(p==0 for p,z in got.values())
     digest.update(repr((name,kind,sorted(got.items()))).encode());bodycases+=kind=='body';shotcases+=kind=='shot'
   for offset in[0,6,64,71,72,80]:
    m=make(name);put(m,VRAM_Buffer1_Offset=offset);at=address(b,'VRAM_Buffer1');before=bytes(m[at:at+96]);invoke(m,name,'MsRenderColors');after=bytes(m[at:at+96])
    if offset<72:
     assert after[offset:offset+7]==bytes([63,17,3]+v['palette'][1:]+[0]);assert m[address(b,'VRAM_Buffer1_Offset')]==offset+6
     assert after[:offset]==before[:offset]and after[offset+7:]==before[offset+7:]
    else:assert after==before
    queuecases+=1
   m=make(name);publish(m);beforelatches=m.chr_latches[:];invoke(m,name,'MsRenderColors');assert m.chr_latches==beforelatches
   # All real descriptor/R3 variants under all actual area palette packets.
   for context in inputs['native_used_colors']:
    r=next(r for r in inputs['native_descriptors']if(r['name'],r['pose'],r['native_R3'])==(context['name'],context['pose'],context['native_R3']))
    put(m,CurrentOAMOffset=0);lo,hi=world(m,r);pixels,_=image(m,lo,hi);pals=inputs['world_sprite_palettes'][context['area']];adapted=[v['palette']]+pals[1:]
    assert hi-lo==len(r['cells'])*4,(r,lo,hi)
    expected={}
    for cell in reversed(r['cells']):
     attr=cell['attributes'];pal=(attr&3)if attr&32 else(attr|r['native_R3'])&3
     signed=lambda n:n if n<128 else n-256
     rec=dict(dx=signed(cell['dx']),dy=signed(cell['dy'])+1,pattern_index=0,attributes=(attr&252)|pal)
     for xy,z in sourcepixels([rec],bytes.fromhex(inputs['native_patterns'][cell['pattern_key']])).items():expected.setdefault(xy,z)
    assert pixels==expected,('actual native world shape/pattern/palette',context['area'],r['name'],r['pose'],r['native_R3'])
    for (xx,yy),(pal,z)in pixels.items():
     if pal:assert adapted[pal][z]==pals[pal][z]
    changes=sum(adapted[pal][z]!=pals[pal][z]for pal,z in pixels.values())
    if changes:world_p0_exceptions.append(dict(variant=name,area=context['area'],name=r['name'],pose=r['pose'],native_R3=r['native_R3'],opaque_pixels=len(pixels),recolored_pixels=changes))
    else:assert all(pal or r['name']=='POWERUP'for pal,z in pixels.values())
    worldcases+=1
   assert all(e['name']=='POWERUP'and e['pose']in['STAR','FIREFLOWER']and e['native_R3']==0 for e in world_p0_exceptions)
   # Actual native producer emits all actors into one OAM and publishes all
   # native and Metal CHR together. Fixtures are within the eight-sprite limit.
   for area in inputs['world_sprite_palettes']:
    m=make(name);r=next(r for r in art['body_packets']if r['state']==0 and r['frame']==0 and r['facing']==0 and r['gravity']==0);setbody(m,r,(64,156))
    shot=next(r for r in art['shot_packets']if r['type']==128 and r['flags']==0 and not r['vertical']and r['phase']==0);setshot(m,shot,2,(108,170));invoke(m,name,'MsRenderDraw');metalend=m[address(b,'CurrentOAMOffset')]
    records=[('KOOPA','WALK_1',1,(152,160)),('GOOMBA','WALK_1',0,(8,176)),('POWERUP','MUSHROOM',0,(208,112)),('PIRANHA','OPEN',0,(208,64)),('PODOBOO','NORMAL',0,(176,112)),('FIREBAR','0',0,(120,112))]
    emitted=[]
    for nn,pose,attr,anchor in records:
     matches=[r for r in inputs['native_descriptors']if r['name']==nn and r['native_R3']==attr and r['pose']==pose]
     if not matches:
      matches=[r for r in inputs['native_descriptors']if r['name']==nn and r['native_R3']==attr];assert matches,(nn,pose)
     r=matches[0];lo,hi=world(m,r,anchor);emitted.append((r,lo,hi))
    publish(m);pixels,cells=image(m);native_pixels,native_cells=image(m,metalend);pals=inputs['world_sprite_palettes'][area];adapted=[v['palette']]+pals[1:]
    assert all(pal!=0 and adapted[pal][z]==pals[pal][z]for pal,z in native_pixels.values())
    occupancy=[sum(y+1<=line<y+17 for y,t,a,x,page in cells)for line in range(240)];assert max(occupancy)<=8,(name,area,max(occupancy))
    actual_world_keys=set(native_pixels);assert not(actual_world_keys&set(image(m,0,metalend)[0])),'No actor hidden behind another'
    assert all(m.chr_latches[i]==beforelatches[i]for i in[1,2,3,4,7,8,9,10,11])
    scenes.append(dict(variant=name,area=area,OAM_cells=len(cells),maximum_sprites_on_scanline=max(occupancy),opaque_world_pixels=len(native_pixels),all_world_RGB_indices_exact=True,Metal_only_P0=True))
    if area=='Ground':previews[name]=(pixels,adapted,cells)
  q.update(body_shape_remap_contexts=bodycases,shot_shape_remap_contexts=shotcases,native_world_palette_contexts=worldcases,palette_queue_capacity_cases=queuecases,combined_actual_native_producer_scenes=scenes,world_P0_cycle_exceptions=world_p0_exceptions)
  # Execute actual current native DrawBlock and DrawPowerUp palette decisions.
  m=make('red-white-black');m.raw_page(1,128);put(m,CurrentBank=128);blockcases=powercases=0
  for area,replacement,slot in itertools.product(range(4),[0,196],[0,1]):
   put(m,ObjectOffset=slot,AreaType=area);m[address(b,'Block_Metatile')+slot]=replacement
   run(m,address(b,'DrawBlock'));assert m[address(b,'Block_SprAttrib')+slot]==(1 if replacement==196 and area!=1 else 3);blockcases+=1
  for kind,tick,priority,slot in itertools.product(range(4),range(8),[0,32],[0,1]):
   put(m,ObjectOffset=slot,FrameCounter=tick);m[address(b,'PowerUpType')+slot]=kind;m[address(b,'Enemy_SprAttrib')+slot]=priority|2
   run(m,address(b,'DrawPowerUp'));want=(priority|((tick>>1)&3))if kind in[1,2]else priority|2
   assert m[address(b,'Enemy_SprAttrib')+slot]==want,(kind,tick,priority,slot);powercases+=1
  q.update(actual_DrawBlock_contexts=blockcases,actual_DrawPowerUp_contexts=powercases,private_pickup_gate_boundary='Existing FarCall transport runs; LmPrivateGate returns Cclear for ordinary native object. Its cache and offscreen continuation are explicit ports; no original/private pickup qualification inferred.')
  groups={}
  for area,pals in inputs['world_sprite_palettes'].items():
   norm=lambda z:48 if z==32 else z
   sets=[sorted({norm(z)for z in p})for p in[[38,15,21],[33,32,1]]+[p[1:]for p in pals[1:]]]
   assert len({tuple(s)for s in sets})==5 and all(len(s)==3 for s in sets)
   groups[area]=dict(full_three_color_sets=sets,required_distinct_sprite_palettes=5,available_sprite_palettes=4,unique_NES_colors=len(set(itertools.chain.from_iterable(sets))))
  q['exact_two_Metal_plus_three_world_palettes_impossible']=groups
  # Constructor/actor/terrain/lifecycle remains authentic after the renderer
  # callback relocation. Use the original donor CPU, not generic velocities.
  lab=stage['variants']['red-white-black']['labels'];fields=json.loads((ROOT/'build/metal-storm-objects-host-1101-v6/assembly.json').read_text())['source_fields']
  raw[16+126*8192+0x15d8:16+126*8192+0x15dc]=bytes([0,208,3,3]);raw[16+127*8192+0xf36+0x61]=1
  def terrain(om,nm):
   for row,col in itertools.product(range(15),range(20)):
    solid=row>=13;om[0x300+row*20+col]=248 if solid else 0
    if row>=2:nm[0x300+(col//16)*208+(row-2)*16+(col&15)]=97 if solid else 0
  def original_draw(om):
   camera=bytes(om[0x710:0x714]);om.regs[6:8]=[12,13];om.map();table=om[0x800e]+256*om[0x800f];om[0x24]=table&255;om[0x25]=table>>8
   om[0x61]=0;om[0x710]=0;om[0x711]=0;om[0x713]=0;om[0x42]=252
   for slot in([3,2,1,0]if om[0x53]&1 else[0,1,2,3]):
    if om[0x510+slot]&128:run(om,0xf282,x=slot,y=om[0x61])
   om[0x710:0x714]=camera;om.regs[6:8]=[0,1];om.map()
  frames=duplicates=0;gravity=set();shotframes=0
  for axis in['walk','jump','reverse','shoot-right','shoot-up','shoot-down']:
   nm=make('red-white-black');nm[0xc000:0xc800]=bytes([90])*2048
   for name,v in dict(Player_X_Position=72,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,SelectedCharacter=35,OperMode=1,GameEngineSubroutine=8,GamePauseStatus=0).items():nm[fields[name]]=v
   nm[0xc732]=255;nm[0xc733]=7;om=M.machine().memory;om.regs[6:8]=[0,1];om.map();terrain(om,nm)
   assert run(nm,lab['MsNativeConstruct'])[3]&1;om[:2048]=bytes(nm[0xc000:0xc800]);terrain(om,nm)
   for tick in range(96):
    pad=(1 if tick<48 else 2)if axis=='walk'else(129 if tick%48<20 else 1)if axis=='jump'else(136 if tick in[4,5]else 132 if tick in[48,49]else 0)if axis=='reverse'else 64 if axis=='shoot-right'else 72 if axis=='shoot-up'else 68
    nm[fields['SavedJoypadBits']]=pad;nm[fields['FrameCounter']]=(tick+200)&255
    run(om,0xad8c,ports={0x8874,0x9ed7,0xff18,0xff39});om.regs[6:8]=[4,5];om.map()
    for slot in[3,2,1]:
     if om[0x510+slot]&128:run(om,0x8e54 if om[0x528+slot]==131 else 0x8eae,x=slot)
    om.regs[6:8]=[0,1];om.map();assert run(nm,lab['MsHostStep'],ports={0x5000,0x5006,0x5009,0x5018})==(85,7,91,0x41)
    om[0x31]=int(f'{pad:08b}'[::-1],2);original_draw(om);put(nm,CurrentOAMOffset=0);invoke(nm,'red-white-black','MsRenderDraw');publish(nm)
    diffs=[i for i in range(0x480,0x750)if not 0x6a8<=i<0x6ac and om[i]!=nm[0xc000+i]];assert not diffs,('composed state',axis,tick,[hex(i)for i in diffs[:12]])
    before=bytes(nm[0xc000:0xc800]);run(nm,lab['MsHostStep'],ports={0x5000,0x5006,0x5009,0x5018});assert before==bytes(nm[0xc000:0xc800]);duplicates+=1
    run(nm,lab['MsNativeApplyDelta']);gravity.add(om[0x734]);shotframes+=bool(om[0x512]|om[0x513]);frames+=1
  assert gravity=={0,128}and shotframes
  q.update(composed_original_constructor_actor_terrain_lifecycle_render_frames=frames,original_constructors=6,duplicate_epoch_guards=duplicates,source_gravity_directions=sorted(gravity),source_frames_with_shots=shotframes,unchanged_source_physics=True)
  # One small comparison PNG from the actual combined OAM/CHR producer above.
  sheet=Image.new('RGB',(1536,548),(22,27,36));draw=ImageDraw.Draw(sheet)
  for i,(name,(pixels,pals,cells))in enumerate(previews.items()):
   panel=Image.new('RGB',(256,240),RGB[34]);pd=ImageDraw.Draw(panel)
   for (x,y),(pal,z)in pixels.items():pd.point((x,y),fill=RGB[pals[pal][z]])
   pd.text((4,4),'NATIVE WORLD PALETTES UNCHANGED',fill=(0,0,0));pd.text((182,48),'PIRANHA',fill=(0,0,0));pd.text((106,91),'FIREBAR',fill=(0,0,0));pd.text((168,91),'PODOBOO',fill=(0,0,0));pd.text((201,136),'ITEM',fill=(0,0,0));pd.text((7,208),'GOOMBA    METAL / SHOT    KOOPA',fill=(0,0,0))
   sheet.paste(panel.resize((512,480),Image.Resampling.NEAREST),(i*512,50));draw.text((i*512+12,12),name.upper(),fill=(242,242,242))
   pc=stage['variants'][name]['pixel_counts'];draw.text((i*512+12,32),f'Body recolored {pc["body"]["intentionally_recolored_pixels"]}/10946 | Shot {pc["shot"]["intentionally_recolored_pixels"]}/316',fill=(230,230,230))
  draw.text((12,533),'Intentional NES player palette adaptation. Native producer fixture; no emulator/admission claim. Star/flower phase0 exceptions are listed in receipt.',fill=(235,235,235));sheet.save(OUT/'player-palette-comparison.png')
  q.update(passed=True,renderer_bytes=2350,actor_bytes=8083,maximum_standalone_cycles=maxcycles,minimum_standalone_SP=minimum,actual_native_helper_hits=dict(helperhits),aggregate_pixels_sha256=digest.hexdigest(),native_P1_P2_P3_packets_unchanged=True,all_native_pattern_bytes_unchanged=True,global_CHR_consumer_closure=False,scope='Actual native renderer and CHR publisher compose original-world descriptors with authentic Metal actor and intentional player-only bitplane/attribute/color remapping. Shape/alpha exact in936contexts. P1/P2/P3 and native world patterns exact; native star/flower phase0 shares changed P0 and is explicitly counted. Constructor/terrain/actor/lifecycle remains source-CPU exact in576frames. Fixture caches/CHR495..499 are not granted; no cold loader/Main/ISR/raster/menu/full gameplay or native admission.')
  files=[Path(__file__),Path(P.__file__),P.REF,Path(M.__file__),M.ROM,OUT/'palette-assembly.json',OUT/'palette-inputs.json',OUT/'native-palette-callers.json',P.V8/'native-witness.json',P.V7/'art.json',ROOT/'build/metal-storm-objects-host-1101-v6/assembly.json',OUT/'player-palette-comparison.png']
  q['bindings']={str(p.resolve()):sha(p)for p in files}
 except Exception:q['error']=traceback.format_exc();raise
 finally:(OUT/'palette-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['bindings','error','world_P0_cycle_exceptions','combined_actual_native_producer_scenes','exact_two_Metal_plus_three_world_palettes_impossible']}))
if __name__=='__main__':main()
