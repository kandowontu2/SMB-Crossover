"""Exact immutable source payload layout in the proposed42-page pool.

This creates a component blob, never a host ROM or an allocation.
"""
from pathlib import Path
import hashlib,json
import audit_prince_pool_1102_v1 as A
R,O=A.R,A.O


def main():
 pool=json.loads((O/'pool-proposal.json').read_text())
 assert pool['passed']and pool['ROM_sha256']==A.SHA and pool['complete_publication_retest']
 assert pool['proposed_physical_CHR_pages']==A.POOL and len(A.POOL)==42
 parts=[('original_body_patterns','prince-body-8x16.chr'),('source_core_fixture','prince-core.bin'),('original_pose_metadata','prince-pose-packets.bin')]
 blob=bytearray();rows=[]
 for name,file in parts:
  data=(O/file).read_bytes();start=len(blob);blob.extend(data)
  rows.append(dict(name=name,offset=start,bytes=len(data),end=len(blob),sha256=hashlib.sha256(data).hexdigest(),first_page_index=start//1024,first_page_offset=start%1024,last_page_index=(len(blob)-1)//1024))
 assert [v['bytes']for v in rows]==[31072,6081,5426]and len(blob)==42579
 used=len(blob);blob.extend(bytes([255])*(42*1024-len(blob)))
 pageimages={p:bytes(blob[i*1024:(i+1)*1024])for i,p in enumerate(A.POOL)}
 def read(offset,count):
  return bytes(pageimages[A.POOL[n//1024]][n%1024]for n in range(offset,offset+count))
 for (_,file),row in zip(parts,rows):assert read(row['offset'],row['bytes'])==(O/file).read_bytes()
 # All real body reads remain below the code-bearing tail of logical page30.
 # Do not assume the whole last1KB is art or that adjacent physical pages exist.
 art=json.loads((O/'source-art.json').read_text());pairs=set();bodypages=set();count=0
 for pose in art['poses']:
  for part in pose['parts_8x16']:
   index=part['pattern_pair'];start=index*32
   assert 0<=index<971 and start+32<=rows[0]['end']
   assert read(start,32)==(O/'prince-body-8x16.chr').read_bytes()[start:start+32]
   pairs.add(index);bodypages.add(start//1024);count+=1
 assert pairs==set(range(971))and bodypages==set(range(31))
 file=O/'pooled-source.bin';file.write_bytes(blob)
 q=dict(passed=True,proposal_only=True,resource_granted=False,host_ROM_created=False,ROM_preimage_SHA256=A.SHA,raw_identity_proposal=38,proposed_physical_pages=A.POOL,pool_bytes=len(blob),source_payload_bytes=used,unused_tail_bytes=len(blob)-used,payload_sha256=hashlib.sha256(blob).hexdigest(),packed_regions=rows,body_physical_pages=A.POOL[:31],code_backing_physical_pages=A.POOL[30:37],metadata_backing_physical_pages=A.POOL[36:42],source_facing_packets=len(art['poses']),actual_body_pair_reads_checked=count,all971_pairs_reachable=True,max_body_read_end=31072,first_code_byte_in_logical_page30=352,first_metadata_byte_in_logical_page36=289,final_metadata_byte_in_logical_page41=595,conditional_runtime=dict(code=dict(window='A000..C000',source_image='A000..B7C1',uncommitted_spare_bytes=2111),state_metadata=dict(window='C000..E000',original_state='C000..C800',pose_metadata='C800..DD32',uncommitted_spare_bytes=718),host_zero_page_bytes=0,WRAM_banks='Root must grant; fixture windows are not physical WRAM ownership.'),remaining=['The source core still has20 explicit fixture environment callbacks at5200..5330; relink to real owned host leaves before hardware execution.','Common resident bootstrap/router is coordinated by root/Bub owner;247B proposed Mac padding is not a Prince-only grant.','Host renderer must translate logical atlas pages through the31-entry physical map and publish at most3 independent sprite windows.','Original world/control,combat,health/death/pickups,source cadence and lifecycle must be integrated and qualified; this component is not native playable.'],bindings={str(p.relative_to(R)):A.sha(p)for p in[Path(__file__),O/'pool-proposal.json',O/'resource-request.json',O/'source-art.json',*[O/f for _,f in parts]]})
 (O/'pooled-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
