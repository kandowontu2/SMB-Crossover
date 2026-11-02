"""Pack verified Prince pose metadata and report unallocated resource needs."""
from pathlib import Path
import hashlib,json
from recover_prince_core_1101_v1 import O,P,R


def main():
 art=json.loads((O/'source-art.json').read_text());core=json.loads((O/'core-recovery.json').read_text());proof=json.loads((O/'core-CPU.json').read_text())
 pairs=list(zip(art['poses'][::2],art['poses'][1::2]));limit=max(p['source_frame']for p in art['poses'])+1
 blob=bytearray([255]*(2*limit));pagecounts=[];sizes=[]
 for a,b in pairs:
  left,right=a['parts_8x16'],b['parts_8x16'];assert a['source_facing']==0 and b['source_facing']==255 and a['source_frame']==b['source_frame']
  assert len(left)==len(right)
  for x,y in zip(left,right):assert(x['x']==-y['x']and x['y']==y['y']and x['pattern_pair']==y['pattern_pair']and x['attribute']^y['attribute']==64)
  assert a['source_projection_geometry']==b['source_projection_geometry']
  assert all(p['attribute']==1 for p in left),'Original player body uses one source sprite palette'
  pages=sorted({p['pattern_pair']//32 for p in left});assert 1<=len(pages)<=3 and len(left)<=13
  pos=len(blob);frame=a['source_frame'];blob[frame*2:frame*2+2]=pos.to_bytes(2,'little');start=len(blob)
  blob.append(len(left)|(len(pages)<<4));blob.extend(pages);blob.extend(a['source_projection_geometry'].values())
  for p in left:
   window=pages.index(p['pattern_pair']//32);tile=(window<<6)|((p['pattern_pair']&31)<<1)
   assert -128<=p['x']<128 and -128<=p['y']<128
   blob.extend([p['y']&255,tile,p['x']&255])
  sizes.append(len(blob)-start);pagecounts.append(len(pages))
 # Decode every face from the exact compact artifact and compare all native
 # descriptors. Pixel parity was independently checked in source-art.json.
 decoded=0
 for pose in art['poses']:
  offset=int.from_bytes(blob[pose['source_frame']*2:pose['source_frame']*2+2],'little');header=blob[offset];n=header&15;np=header>>4;pages=list(blob[offset+1:offset+1+np]);at=offset+1+np;assert list(blob[at:at+3])==list(pose['source_projection_geometry'].values());at+=3;actual=[]
  for _ in range(n):
   dy,tile,dx=blob[at:at+3];at+=3;dy=dy if dy<128 else dy-256;dx=dx if dx<128 else dx-256
   actual.append(dict(x=-dx if pose['source_facing'] else dx,y=dy,pattern_pair=pages[tile>>6]*32+((tile&63)>>1),attribute=65 if pose['source_facing']else 1))
  expected=[{k:v for k,v in p.items()if k!='source_cells'}for p in pose['parts_8x16']]
  assert actual==expected,(pose['source_frame'],pose['source_facing'])
  decoded+=1
 (O/'prince-pose-packets.bin').write_bytes(blob)
 request=dict(status='SOURCE_COMPONENT_RESOURCE_REQUEST_NOT_A_GRANT',raw_identity_proposal=38,menu='Excitebike alternate; coordinate with Exraw37 owner. Ex grants are not Prince grants.',donor_sha256=P.SHA,source_core=dict(code_bytes=core['component_code_bytes'],script_bytes=core['script_bytes'],table_bytes=core['table_bytes'],aligned_image_bytes=core['compact_code_image_bytes'],fixture_half_open=['A000','B7C1'],remaining_in_one_8KB_code_bank=8192-core['compact_code_image_bytes']),conditional_state=dict(bytes=2048,fixture_half_open=['C000','C800'],new_host_zero_page_bytes=0),pose_metadata=dict(bytes=len(blob),frame_index_bytes=2*limit,pose_packet_bytes=sum(sizes),decoded_facing_packets=decoded,packet_sprite_limit=13,layout='Frame offset table; header low4bits sprite count/high2bits page count;1..3relativeCHRpages;3original projection witnesses(070F,06F1-anchorY,04C3);dy,tile,dx perpart. FaceFF negates X and XORs horizontalflip. Source palette1 is constant.'),conditional_state_plus_pose_bytes=2048+len(blob),remaining_in_one_8KB_state_metadata_bank=8192-2048-len(blob),CHR=dict(pattern_bytes=art['pattern_bytes'],pages_1KB=art['CHR_1KB_pages'],pair_count=art['native_8x16_pattern_pairs'],maximum_simultaneous_body_pages=max(pagecounts),pages_per_pose={str(n):pagecounts.count(n)for n in sorted(set(pagecounts))},runtime_mapping='Requestthree private sprite windows at most; atlaspagesremainunallocated.'),host_work_still_required=['20declared original world/health/audio environment boundaries need real host bindings; three unexercised boundary kinds remain explicit in core-recovery.json.','Original once-per4foreground-phase schedule observed in untimed donor must be qualified on native timing; no60Hzsourceupdate substitution.','Exact-identity constructor,retirement,cacheheaders and sourceclock/NMI/IRQ ownership; no resources granted by this receipt.','Resident cold loader/CHRpublisher/service dispatcher and renderer are not included in6081-byte source core.','Original combat selectorF090 onward, controller-earned host health/death/pickups, bodyterrain adapter and full1-1 remain open.'],native=False,installed=False,helpers_added=False,source_CPU_case_total=sum(proof[n]for n in ['action_selection_cases','animation_advances','fall_cases','direct_all15_command_cases','input_decode_cases','original_control_cases']),bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'prince-core.bin',O/'prince-pose-packets.bin',O/'prince-body-8x16.chr',O/'core-CPU.json',O/'core-recovery.json',O/'source-art.json']})
 (O/'resource-request.json').write_text(json.dumps(request,indent=2)+'\n');print(json.dumps({k:v for k,v in request.items()if k not in ['bindings','host_work_still_required']}))


if __name__=='__main__':main()
