"""Lossless original-pose packing and measured sparse-template proposal.

No existing ROM/CHR is modified. The assigned16-page budget is an upper bound,
not permission to claim audio/loader completeness or extra hook capacity.
"""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2]
P=R/'build/thomas-host-boundary-1031-v2';A=R/'build/thomas-original-component-v5/assets'
O=R/'build/thomas-sparse-template-1031-v1'
G=R/'docs/qa/checkpoints/2026-10-31/thomas-first-host-resource-v1/resource-contract.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest=lambda v:hashlib.sha256(bytes(v)).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
 assert not O.exists();O.mkdir(parents=True)
 stage=json.loads((P/'source-stage.json').read_text());grant=json.loads(G.read_text())
 for p,h in grant['bindings'].items():assert sha(p)==h,p
 assert grant['conditional_grant']['CHR_pages']==[426,442]
 image=(P/'component.bin').read_bytes();poses=json.loads((A/'poses.json').read_text())
 patterns=(A/'thomas-8x16.chr').read_bytes();indices=(A/'thomas-source-indices.bin').read_bytes()
 assert len(patterns)==4672
 body=patterns+bytes(5120-len(patterns));descriptors=bytearray();rows=[];ptrs=[];pages=[];pixel_cases=0
 for n,pose in enumerate(poses['poses']):
  used=sorted({r[1]//32 for r in pose['records']});assert len(used)<=3
  mapping=used+[used[0]]*(4-len(used));pages.extend(mapping)
  ptrs.append(0xd000+len(descriptors));descriptors.append(4*pose['parts'])
  expected=bytearray(48*80);actual=bytearray(48*80)
  for y,pair,attr,x in pose['records']:
   slot=used.index(pair//32);tile=(slot*32+pair%32)*2
   descriptors.extend([y,tile,attr,x]);assert tile&1==0
   # Decode the actual physical1KiB CHR page selected for this native window.
   physical=mapping[tile//64];offset=physical*1024+(tile%64)*16
   pattern=body[offset:offset+32]
   for dy in range(16):
    for dx in range(8):
     at=(dy//8)*16+(dy&7);v=((pattern[at]>>(7-dx))&1)|(((pattern[at+8]>>(7-dx))&1)<<1)
     if v:actual[(y+dy)*48+x+dx]=v
  expected[:]=indices[n*48*80:(n+1)*48*80]
  assert actual==expected,(n,pose['command'],'native-window packing lost original pixels')
  # Original index3 remains opaque black; index0 alone is transparent.
  opaque=sum(v!=0 for v in expected);pixel_cases+=48*80
  rows.append(dict(command=pose['command'],parts=pose['parts'],physical_page_offsets=mapping,
   descriptor_pointer=ptrs[-1],source_index_sha256=digest(expected),opaque_pixels=opaque,
   max_sprites_per_line=max(sum(y<=line<y+16 for y,_,_,x in pose['records'])for line in range(80))))
 ptrlo=bytes(v&255 for v in ptrs);ptrhi=bytes(v>>8 for v in ptrs)
 metadata=bytes(descriptors)+ptrlo+ptrhi+bytes(pages)
 assert len(metadata)<=2048
 state=bytearray(8192);state[0x1000:0x1000+len(metadata)]=metadata
 (O/'body.chr').write_bytes(body);(O/'C2-template.bin').write_bytes(state)
 (O/'native-descriptors.bin').write_bytes(descriptors);(O/'metadata.bin').write_bytes(metadata)
 carriers=bytearray();loads=[]
 def pack(name,data,bank,dest):
  for page in range(8):
   chunk=data[page*1024:(page+1)*1024];assert len(chunk)==1024
   if len(set(chunk))==1:
    loads.append(dict(destination_bank=bank,destination=dest+1024*page,fill=chunk[0],template=name,page=page))
   else:
    at=len(carriers)//1024;carriers.extend(chunk)
    loads.append(dict(destination_bank=bank,destination=dest+1024*page,CHR_page=426+at,template=name,page=page,sha256=digest(chunk)))
 pack('A3-code',image,3,0xa000);pack('C2-state-and-metadata',state,2,0xc000)
 body_first=426+len(carriers)//1024;carriers.extend(body)
 assert len(carriers)//1024==12
 (O/'measured-source-pages.chr').write_bytes(carriers)
 resident=grant['conditional_grant']['resident'];raw=(R/'build/contra-force-world-roles-1031-v2/joint/candidate.nes').read_bytes()
 lo,hi=resident['file_range'];assert digest(raw[lo:hi])==resident['preimage_sha256']
 dump(O/'pose-packing.json',dict(passed=True,poses=rows,original_source_index_pixels=pixel_cases,metadata_bytes=len(metadata),descriptor_bytes=len(descriptors),body_physical_pages=5,
   body_first_physical_page_in_proposal=body_first,max_pattern_windows=3,original_palette=poses['palette'],
   palette_proposal='Only sprite P0 shades3F11..13=[27,30,0F]. Never queue universal3F00/10. Hardware publisher not integrated.',
   origin='X=Player_X-16; Y=GroundPlane-48. SourceB6 applied to actor position once and canceled from canvas origin; native command retains baked jump art.'))
 dump(O/'resource-needs.json',dict(status='MEASURED_SOURCE_TEMPLATE_NOT_LOADER_QUALIFIED',host_sha256=stage['bindings'][str((R/'build/contra-force-world-roles-1031-v2/joint/candidate.nes').resolve())],
   allocation_contract=sha(G),code=dict(origin='A3:A000',emitted_bytes=stage['emitted_bytes'],nonuniform_1KiB_pages=5,uniform_FF_pages=3),
   state=dict(bank='selectedRAM2/C2',native_state_bytes=2048,transaction_end='C838',private_metadata_origin='D000',metadata_bytes=len(metadata),metadata_end=f'{0xd000+len(metadata):04X}',nonuniform_1KiB_pages=2,zero_fill_pages=6),
   body=dict(bytes=len(patterns),padded_bytes=len(body),physical_pages=5,max_pages_per_pose=3,source_poses=42),
   measured_functional_template_pages=12,total_granted_pages=16,remaining_granted_pages=4,
   optional_audio=dict(original_region_bytes=1983,source='build/thomas-original-component-v5/source/thomas_audio_original.inc',status='Original-address audio reconstruction only. Relocation/bank/channel/APU/NMI ownership pending; no executable2page-fit claim.',prospective_bank='selectedRAM1/A1'),
   resident=dict(**resident,measured_loader_bytes=None,status='Granted1478B; no loader emitted yet. Required stable A/C bounce, sparsecopy/verify, cookie+epoch and5FFF protocol remain actual implementation work.'),
   no_new_globals=True,all_current_host_bytes_unchanged=True,loads=loads,
   future_loader_requirements=['Full matching selected10/FmAlts40/epoch+cookie before cacheopcode/state accesses','Retire nativeC2 andA3cookies before overwrite; publish validity last','Sparse clear/fill separate from cartridge CHR; no literal24KB carrier','Genuine normal/lag/pauseNMI+IRQ/SMC33/maps/stack controls on real loaded source','No new resident/hook/menu span inferred from this fit']))
 dump(O/'source-stage.json',dict(passed=True,source_only=True,source_pixels=161280,carrier_pages=12,bindings={str(p):sha(p)for p in [Path(__file__),G,P/'source-stage.json',P/'component.bin',A/'poses.json',A/'thomas-8x16.chr',A/'thomas-source-indices.bin']+[p for p in O.rglob('*')if p.is_file()]}))
 print(json.dumps(dict(result='PASS',carrier_pages=12,remaining=4,metadata=len(metadata),stage_sha256=sha(O/'source-stage.json'))))
if __name__=='__main__':main()
