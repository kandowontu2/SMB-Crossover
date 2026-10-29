"""Provenance-bound Retold player assets, no patched ROM or shared source writes."""
from pathlib import Path
import hashlib,json,zlib
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
A=R/'build/source-acquisition/kid-icarus-retold-2026-10-29'
O=R/'build/pit-retold-assets-v1'
BASES=[Path('C:/NES/Kid Icarus (USA, Europe).nes'),Path('C:/NES/Kid Icarus (USA, Europe) (Rev 1).nes')]
SAMPLES=[('STAND','reference-native',300),('WALK1','reference-native',405),
 ('WALK2','reference-native',415),('WALK3','reference-native',425),
 ('JUMP','reference-combat',457),('CROUCH','reference-combat',330),
 ('SHOOT','reference-combat',405),('JUMP_SHOOT','reference-combat',462),
 ('UP_SHOOT','reference-combat',512)]
SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):return dict(path=str(Path(p).resolve()),bytes=Path(p).stat().st_size,sha256=SHA(p))
RGB={0x20:(252,252,252),0x26:(248,120,88),0x07:(82,33,0)}
UNKNOWN=(255,0,200,255)

def ips():
 p=(A/'retold.ips').read_bytes();assert hashlib.sha256(p).hexdigest()=='81c34ed0e92994229b5d81b435deddd4c463c9ae35e5c76cdaef5a1fa250445d'
 assert p[:5]==b'PATCH';i=5;out={};records=[]
 while p[i:i+3]!=b'EOF':
  header=i;at=int.from_bytes(p[i:i+3],'big');n=int.from_bytes(p[i+3:i+5],'big');i+=5
  if n:payload=i;part=p[i:i+n];i+=n;kind='literal'
  else:
   n=int.from_bytes(p[i:i+2],'big');payload=i+2;part=bytes([p[payload]])*n;i+=3;kind='RLE'
  assert len(part)==n
  rec=dict(index=len(records),target_start=at,target_end=at+n,kind=kind,IPS_header_offset=header,IPS_payload_offset=payload)
  records.append(rec)
  for j,v in enumerate(part):out[at+j]=dict(value=v,record=rec['index'],IPS_offset=payload+(j if kind=='literal'else 0),kind=kind)
 assert p[i:i+3]==b'EOF'and i+3==len(p),'No unsupported truncation/extension trailer'
 return out,records

def tile(values,known,palette,strict):
 im=Image.new('RGBA',(8,8));pix=im.load()
 for y in range(8):
  for x in range(8):
   if strict and(not known[y]or not known[y+8]):pix[x,y]=UNKNOWN;continue
   v=((values[y]>>(7-x))&1)|(((values[y+8]>>(7-x))&1)<<1)
   if v:pix[x,y]=RGB[palette[v]]+(255,)
 return im

def pose(parts,tiles,known,palette,face,strict):
 im=Image.new('RGBA',(48,48))
 for p in reversed(parts):
  pic=tile(tiles[p['tile']],known[p['tile']],palette,strict)
  attr=p['attribute'];x=p['x_relative_to_grid_foot'];y=p['y_relative_to_grid_foot']
  if face=='Left':x=-x-8;attr^=64
  if attr&64:pic=pic.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
  if attr&128:pic=pic.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
  im.alpha_composite(pic,(24+x,36+y))
 return im

def sheet(poses,tiles,known,palette,strict,path):
 w=650;h=54+len(poses)*174
 im=Image.new('RGB',(w,h),(35,43,54));d=ImageDraw.Draw(im)
 title='IPS ONLY: magenta = uncovered bit-plane row'if strict else'IPS + corroborated original byte(s); not a verified full ROM patch'
 d.text((8,8),title,fill='white');d.text((8,26),'Existing native Right OAM; Left = exact horizontal mirror. Neutral isolated preview.',fill=(190,200,212))
 for i,p in enumerate(poses):
  y=54+i*174;d.text((8,y+5),p['pose'],fill='white')
  for j,face in enumerate(['Right','Left']):
   pic=pose(p['parts'],tiles,known,palette,face,strict).resize((160,160),Image.Resampling.NEAREST)
   x=145+j*235
   bg=Image.new('RGBA',pic.size,(69,83,97,255));bg.alpha_composite(pic);im.paste(bg.convert('RGB'),(x,y))
   d.text((x+4,y+146),face,fill=(255,225,110))
 im.save(path)

def main():
 assert not(O/'handoff.json').exists(),'Frozen output must remain immutable'
 O.mkdir(exist_ok=True)
 patch,records=ips();bases=[p.read_bytes()for p in BASES]
 author=dict(CRC32='F54EECE6',MD5='17ED4EAE20777A826589AF14FA70AEA1',SHA1='EA586E7E2B884ED67B99EAEC0678A8FAF8C94F46')
 for raw in bases:assert f'{zlib.crc32(raw):08X}'!=author['CRC32']and hashlib.sha1(raw).hexdigest().upper()!=author['SHA1']
 files=[Path(__file__),A/'retold.ips',A/'selected-patch-acquisition.json',A/'patch-records.json',A/'og_readme.txt',A/'scraped_info.txt',R/'tools/reference/build_expanded_assets.py',R/'src/pit_metasprites.inc']+BASES
 captures={};poses=[];required=set();originals={}
 for name,folder,frame in SAMPLES:
  prefix=R/'build'/folder/f'pit-{frame}'
  paths=[prefix.with_suffix(s)for s in['.chr','.oam','.pal']]
  data,oam,pal=[p.read_bytes()for p in paths];files+=paths
  assert len(data)==8192 and len(oam)==256 and len(pal)==32
  parts=[]
  for slot in range(8,14):
   sy,t,attr,sx=oam[slot*4:slot*4+4]
   if sy>=240:continue
   assert attr&3==0
   originals.setdefault(t,[]).append((str(paths[0]),data[t*16:t*16+16]))
   # This identifies exact original tile equivalence, not a uniquely observed
   # CPU upload bank: the two original ROM copies are byte-identical.
   assert all(raw[16+t*16:32+t*16]==data[t*16:t*16+16]for raw in bases)
   assert all(raw[0x2010+t*16:0x2020+t*16]==data[t*16:t*16+16]for raw in bases)
   parts.append(dict(slot=slot,OAM_Y=sy,tile=t,attribute=attr,OAM_X=sx,visible_top=sy+1))
   required.add(t)
  left=min(p['OAM_X']for p in parts);right=max(p['OAM_X']+8 for p in parts)
  bottom=max(p['visible_top']+8 for p in parts);center=left+(right-left)//2
  for p in parts:p.update(x_relative_to_grid_foot=p['OAM_X']-center,y_relative_to_grid_foot=p['visible_top']-bottom)
  poses.append(dict(pose=name,source_folder=folder,source_frame=frame,source_OAM_parts=parts,parts=parts,
   captured_grid_foot=dict(x=center,y=bottom),source_Player_RAM_foot_NOT_captured=True,
   host_anchor=dict(x=0,y=32,reason='Existing Pit body integration bottom anchor; do not change gameplay box.'),
   dimensions=[right-left,bottom-min(p['visible_top']for p in parts)],capture_bindings=[bind(p)for p in paths]))
  captures[f'{folder}/{frame}']=dict(P0=list(pal[16:20]),body_tiles=sorted(p['tile']for p in parts))
 arrow=R/'build/reference-native/pit-655';ac=arrow.with_suffix('.chr').read_bytes();ap=arrow.with_suffix('.pal').read_bytes()
 assert all(raw[16+60*16:32+60*16]==ac[60*16:61*16]for raw in bases)
 required.add(60);originals.setdefault(60,[]).append((str(arrow.with_suffix('.chr')),ac[60*16:61*16]));files+=[arrow.with_suffix('.chr'),arrow.with_suffix('.pal')]
 tiles={};known={};tile_receipts=[];fallback=[]
 for t in sorted(required):
  values=[];mask=[];provenance=[]
  for j in range(16):
   at=16+t*16+j
   if at in patch:values.append(patch[at]['value']);mask.append(True);provenance.append(dict(file_offset=at,**patch[at]))
   else:
    v=bases[0][at];assert bases[1][at]==v and all(raw[j]==v for _,raw in originals[t])
    values.append(v);mask.append(False);proof=dict(file_offset=at,value=v,tile=t,tile_byte=j,source='unchanged authentic local ROM/captured CHR agreement',capture_sources=sorted(set(path for path,_ in originals[t])))
    provenance.append(proof);fallback.append(proof)
  tiles[t]=bytes(values);known[t]=mask
  tile_receipts.append(dict(tile=t,patch_target_file_offset=16+t*16,full_literal_or_RLE=sum(mask)==16,patch_covered_bytes=sum(mask),bytes=bytes(values).hex(),provenance=provenance))
 palette=captures['reference-native/300']['P0']
 assert palette==[15,32,38,7]and all(v['P0']==palette for v in captures.values())
 palette_matches=[]
 for at in range(16,len(bases[0])-4):
  if bases[0][at:at+4]==bytes(palette)and bases[1][at:at+4]==bytes(palette):
   assert not any(at+i in patch for i in range(4));palette_matches.append(at)
 assert palette_matches
 # Raw compact asset contains only the selected graphics, never ROM code.
 packed=b''.join(tiles[t]for t in sorted(required));(O/'retold-player-patterns.2bpp').write_bytes(packed)
 for i,row in enumerate(tile_receipts):row['packed_asset_offset']=i*16
 proof=dict(status='READ_ONLY_RETOLD_PATCH_PLUS_AUTHENTIC_LOCAL_BASE_ASSET_ADAPTATION',
  author='dACE; final build240 / RHDN1.2; GB Of Myths & Monsters graphics ported/adapted to NES Kid Icarus',
  author_required_base=author,author_base_matched=False,full_ROM_patch_applied_or_written=False,
  source_palette=palette,palette_basis='Actual original native captures; every matching original P0 palette record in both local revisions is unmodified by IPS. Static RGB preview is approximate, not patched-game PPU capture.',
  palette_candidate_file_offsets=palette_matches,IPS_records=len(records),IPS_RLE_records=sum(r['kind']=='RLE'for r in records),
  patch_target_bank_choice='IPS-targeted first pattern copy at file$10. Native capture proves tile bytes/OAM identity, but cannot distinguish the original identical copy at$2010. No unique CPU upload-bank proof claimed.',
  selected_tiles=len(required),fully_patch_supplied_tiles=sum(all(known[t])for t in required),original_byte_dependencies=fallback,
  tiles=tile_receipts,poses=poses,arrow=dict(tile=60,source='existing native arrow sample655; separate from body pose captures',source_CHR=bind(arrow.with_suffix('.chr'))),
  mirror_rule='Left: x=-x-8 and attribute XOR40; preserve V/palette. Derived exact mirror, not a newly captured original left sequence.',
  aliases_supported_without_new_drawing={'FLAP1':'JUMP','FLAP2':'JUMP','FLAPSHOT1':'JUMP_SHOOT','FLAPSHOT2':'JUMP_SHOOT','HURT':'JUMP','DIE':'CROUCH'},
  aliases_are_existing_host_choices_NOT_new_retold_animation_proof=True,
  gaps=['Author GoodNES base not present; no full patch compatibility/native gameplay proof.',
        'Original patched CPU metasprite/capture behavior and all areas not executed; recorded original OAM geometry reused explicitly.',
        'Crouch-shot arm and jump-up composite, hammer phases, climb/death/portrait choices need explicit existing-Pit adaptation; not silently called original Retold poses.',
        'Host packing8x16, runtime/menu/variant admission, palette roles/world preservation, CHR capacities and native visual review remain unimplemented.',
        'Source Player RAM foot was not captured; original OAM grid anchor and existing host32px bottom anchor are distinguished.',
        'No mechanics changes, new GB abilities, sprite allocation or shared output is made.'])
 (O/'pose-assets.json').write_text(json.dumps(proof,indent=2)+'\n')
 sheet(poses,tiles,known,palette,True,O/'literal-only-poses.png')
 sheet(poses,tiles,known,palette,False,O/'local-asset-poses.png')
 im=Image.new('RGB',(768,156),(35,43,54));d=ImageDraw.Draw(im);d.text((5,4),'Retold patched player tiles; labels are original8x8 tile IDs. * uses corroborated original bytes.',fill='white')
 for i,t in enumerate(sorted(required)):
  x=(i%16)*48;y=26+(i//16)*64
  pic=tile(tiles[t],known[t],palette,False).resize((40,40),Image.Resampling.NEAREST);bg=Image.new('RGBA',pic.size,(69,83,97,255));bg.alpha_composite(pic);im.paste(bg.convert('RGB'),(x,y))
  d.text((x,y+42),f'{t:02X}'+('*'if not all(known[t])else''),fill='white')
 im.save(O/'player-tile-map.png')
 report=R/'docs/qa/pit-retold-art-basis-2026-10-29.txt'
 text=f'''PIT GAME BOY GRAPHICAL ALTERNATE: READ-ONLY ASSET BASIS, NOT INTEGRATED.
Source: exact acquired dACE Kid Icarus - Retold final240 IPS81c34ed0e92994229b5d81b435deddd4c463c9ae35e5c76cdaef5a1fa250445d, original README and archived RHDN metadata. The author describes NES graphics ported/adapted from Game Boy Of Myths & Monsters. This does not import Game Boy mechanics.
The author-required GoodNES CRC F54EECE6 / SHA1 EA586E7E2B884ED67B99EAEC0678A8FAF8C94F46 is unmatched. No patched ROM is generated and no authenticated full application is claimed. The usable asset is expressly Retold patch plus authentic local-base/captured-CHR agreement.
{len(required)} selected native8x8 body/arrow tiles; {sum(all(known[t])for t in required)} complete from IPS literal/RLE writes. {len(fallback)} unchanged bytes are individually bound to BOTH local authentic revisions and existing native captured CHR. Body tile00 first low-plane byte atfile$10 is07, not an assumed zero. Strict literal-only poses mark uncovered rows magenta; full local-asset preview uses exactly those corroborated original bytes. Every other pixel is decoded from the actual IPS data. No painted/invented pixel.
The IPS changes the first original player-pattern copy atfile$10; identical original tilebytes also occur at$2010. Captured OAM supplies exact tile IDs, per-part H/V, position and priority/palette attributes. It establishes original pixel identity, not a uniquely observed ROM upload bank. We intentionally select the patch-targeted first copy for this source adaptation. Original native Right poses are stand,3walk samples,jump,crouch,ground/jump/up bow. Left previews use an exact geometric/H-bit mirror; no new original left timing is claimed. Each pose stores actual OAM, NES Y+1 grid bounds, grid-foot offsets and the separately authored existing-host bottom anchor32.
P0 is the actual native captured0F/20/26/07; all matching original records in both local revisions are untouched by this patch. Preview RGB uses the current asset builder's static color approximation, not authenticated patched-game PPU color evidence. Body OAM and pixels are isolated; no NES8-sprite selection/world/priority/CHR publication proof.
Existing host flap aliases may reuse the corresponding jump/bow rasters; they are existing Pit choices, not newly established Retold animation phases. Current crouch-shot/jump-up composites, hammer overlays, climb/death substitutions and portrait need explicit source-derived adaptation in later integration. All original gameplay remains existing Pit unless separately requested.
Artifacts: build/pit-retold-assets-v1/pose-assets.json; retold-player-patterns.2bpp (compact selected graphics only); literal-only-poses.png; local-asset-poses.png; player-tile-map.png. No original-ROM copies, full patch, source/runtime clones, shared asset/source/CFG/menu/RAM/CHR allocation, native emulator or broad download.
'''
 report.write_text(text);files+=[report]
 outputs=[O/n for n in['pose-assets.json','retold-player-patterns.2bpp','literal-only-poses.png','local-asset-poses.png','player-tile-map.png']]
 hand=dict(status=proof['status'],source_bindings=[bind(p)for p in sorted(set(files))],output_bindings=[bind(p)for p in outputs],report=bind(report),full_ROM_patch_authenticated=False,native_run=False,shared_changed=False)
 (O/'handoff.json').write_text(json.dumps(hand,indent=2)+'\n')
 print(json.dumps(dict(handoff=bind(O/'handoff.json'),selected_tiles=len(required),fully_patch_supplied_tiles=proof['fully_patch_supplied_tiles'],unchanged_bytes=len(fallback),report=bind(report))))

if __name__=='__main__':main()
