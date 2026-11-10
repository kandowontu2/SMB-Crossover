"""Offline lossless relative-OAM cache, read from the frozen actual host source."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];O=R/'build/arthur-draw-cache-v1';P=R/'build/arthur-host-integration-v2'
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import arthur_actual_host_controls_v1 as A
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def byte(b,n,i=0):return b['raw'][A.location(b,n)+i]
def word(b,lo,hi,i):return byte(b,lo,i)+256*byte(b,hi,i)
def rawat(b,pc):
 # All immutable Arthur art is in actual physical70/C view.
 return 16+70*8192+pc-0xc000
def expand(b,mode,key):
 index=byte(b,'ArPalBodyPoseIndex',key)if key<54 else byte(b,'ArPalShotIndex',key-54)
 if index==255:return None
 mid=(index&127)+(43 if mode else 0);at=rawat(b,word(b,'ArPalRecordLo','ArPalRecordHi',mid));raw=b['raw']
 header,layout=raw[at:at+2];count=header>>4;page=header&15
 la=rawat(b,word(b,'ArPalLayoutLo','ArPalLayoutHi',layout));out=bytearray([count,255 if page==15 else 100+page])
 for i in range(count):
  cell=raw[at+2+i];x,y=raw[la+2*i:la+2*i+2]
  tile=(cell&31)*2
  if key>=54:tile|=0x81|(0x40 if cell&128 else 0)
  attr=((cell&96)<<1)^(64 if index&128 else 0);pal=x>>6
  if mode==2 and pal==1:pal=3
  attr|=pal|((y&128)>>2)
  dx=x&63;dx=dx-64 if dx>=32 else dx
  if index&128:dx=-dx-8
  dy=y&127;dy=dy-128 if dy>=64 else dy
  out.extend([dy&255,tile,attr,dx&255])
 return bytes(out)

def main():
 assert not O.exists();O.mkdir();b=A.scoped_load(P/'candidate.nes')
 records=[];recordids={};cases=[];pointers=[]
 # Final fixed source-pose table: body0..53, native weapon-index54..73.
 for mode in range(3):
  for key in range(74):
   data=expand(b,mode,key)
   if data is None:pointers.append(None);continue
   if data not in recordids:recordids[data]=len(records);records.append(data)
   ident=recordids[data];pointers.append(ident);cases.append(dict(mode=mode,key=key,record=ident,parts=data[0]))
 size=444;offsets=[]
 for data in records:offsets.append(size);size+=len(data)
 assert size<=8192,('8KB cache does not fit',size)
 cache=bytearray()
 for ident in pointers:
  ptr=0 if ident is None else 0xc000+offsets[ident];cache.extend([ptr&255,ptr>>8])
 for data in records:cache.extend(data)
 (O/'cache-expanded.bin').write_bytes(cache)
 # Canonical records fit the already granted, currently unused3CHR pages.
 canonical=[];canonicalids={};sourceptr=[]
 for mid in range(86):
  at=rawat(b,word(b,'ArPalRecordLo','ArPalRecordHi',mid));header,layout=b['raw'][at:at+2];la=rawat(b,word(b,'ArPalLayoutLo','ArPalLayoutHi',layout));data=bytearray([header>>4,header&15])
  for i in range(header>>4):
   cell=b['raw'][at+2+i];x,y=b['raw'][la+2*i:la+2*i+2]
   # Absolute bitplane/palette role decoding can happen at forced blank.
   dx=x&63;dx=dx-64 if dx>=32 else dx;dy=y&127;dy=dy-128 if dy>=64 else dy
   data.extend([dy&255,cell,x>>6,dx&255,32 if y&128 else 0])
  data=bytes(data)
  if data not in canonicalids:canonicalids[data]=len(canonical);canonical.append(data)
  sourceptr.append(canonicalids[data])
 # Five-byte canonical rows retain raw cell flags. Keep their measured
 # size as an alternative; the actual result also fits the3granted pages.
 simple=sum(map(len,canonical))+172+94
 # Four-byte canonical OAM rows can infer body/shot role from the masterID.
 four=[];fourids={};fourptr=[]
 for mid in range(86):
  at=rawat(b,word(b,'ArPalRecordLo','ArPalRecordHi',mid));header,layout=b['raw'][at:at+2];la=rawat(b,word(b,'ArPalLayoutLo','ArPalLayoutHi',layout));data=bytearray([header>>4,header&15])
  # Actual master family is source-authenticated by the pose-map membership,
  # not a guessed arithmetic boundary.
  shot=any((byte(b,'ArPalShotIndex',i)&127)==mid%43 for i in range(20))
  for i in range(header>>4):
   cell=b['raw'][at+2+i];x,y=b['raw'][la+2*i:la+2*i+2]
   tile=(cell&31)*2|(0x81|(0x40 if cell&128 else 0)if shot else 0)
   attr=((cell&96)<<1)|(x>>6)|((y&128)>>2)
   dx=x&63;dx=dx-64 if dx>=32 else dx;dy=y&127;dy=dy-128 if dy>=64 else dy
   data.extend([dy&255,tile,attr,dx&255])
  data=bytes(data)
  if data not in fourids:fourids[data]=len(four);four.append(data)
  fourptr.append(fourids[data])
 inputsize=172+54+20;inputoffs=[]
 for data in four:inputoffs.append(inputsize);inputsize+=len(data)
 payload=bytearray()
 for ident in fourptr:payload.extend([inputoffs[ident]&255,inputoffs[ident]>>8])
 payload.extend(byte(b,'ArPalBodyPoseIndex',i)for i in range(54));payload.extend(byte(b,'ArPalShotIndex',i)for i in range(20))
 for data in four:payload.extend(data)
 assert len(payload)==inputsize and inputsize<=3072
 (O/'canonical-input.bin').write_bytes(payload)
 d=dict(status='OFFLINE_DRAW_CACHE_DATA_ONLY_NO_RAM_HEADER_OR_PRG_GRANT',source_ROM_sha256=sha(P/'candidate.nes'),source_pose_mode_cases=len(cases),expanded_unique_records=len(records),expanded_cache_bytes=size,cache_table_bytes=444,canonical_input_bytes=inputsize,canonical_input_granted_CHR_candidate_pages=[881,884],unused_within_3pages=3072-inputsize,WRAM_bank_candidate=1,WRAM_bank_bytes=8192,unused_cache_bank_bytes=8192-size,simple_5byte_canonical_input_alternative_bytes=simple,cases=cases,record_offsets=offsets,bindings={str(p.resolve()):sha(p)for p in[Path(__file__),P/'candidate.nes',P/'candidate.dbg',O/'cache-expanded.bin',O/'canonical-input.bin']},limits=['Data-only offline sizing; no physical RAM-bank/header/loader lease or code installed.','Existing source motion, five weapons and authored double jump are untouched.','Runtime emitter, real mapper/NMI restoration and all pixel/priority/clipping controls remain to implement before requesting adoption.'])
 (O/'plan.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({k:v for k,v in d.items()if k not in['cases','record_offsets','bindings','limits']}))
if __name__=='__main__':main()
