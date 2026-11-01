"""Execute current CF cookie compare/publication loops at the proposed tail."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
from verify_native_relocation import NesMPU
from check_tank_terminal_leaves_1101_v1 import O,P,PIN
def main():
 b=scoped_load(P);raw=b['raw'];assert hashlib.sha256(raw).hexdigest()==PIN
 table=location(b,'CfLoaderExpectedCookie');cookie=raw[table:table+16]
 carrier=next(s for s in b['segs'].values()if s['name'].strip('"')=='CF_CARRIER')
 start=int(carrier['ooffs'],0);end=start+int(carrier['size'],0)
 hits=[];pos=start
 while (pos:=raw.find(bytes.fromhex('dd86cf'),pos,end))>=0:hits.append(pos);pos+=1
 assert len(hits)==1;at=hits[0];compare=raw[at-9:at+8]
 assert compare.hex()=='a20fe002f008bde0bfdd86cfd05cca10f1'
 publish=raw[location(b,'CfPublishCookie')-2:location(b,'CfPublishCookie')+9]
 assert publish.hex()=='a20fbd86cf9de0bfcad0f7'
 class Memory(list):
  def __getitem__(self,i):
   if isinstance(i,int) and 0xcf86<=i<0xcf96:self.reads.add(i-0xcf86)
   return super().__getitem__(i)
 cases=0;domains=set()
 for corrupt in [-1]+list(range(16)):
  m=Memory([0]*65536);m.reads=set();m[0x9000:0x9011]=compare;m[0xcf86:0xcf96]=cookie;m[0xbfe0:0xbff0]=cookie
  if corrupt>=0:m[0xbfe0+corrupt]^=255
  c=NesMPU(memory=m,pc=0x9000)
  for _ in range(150):
   if not 0x9000<=c.pc<0x9011:break
   c.step()
  else:raise AssertionError('Cookie loop failed to terminate')
  assert (c.pc==0x9011)==(corrupt in [-1,2])
  assert m.reads<=set(range(16))-{2};domains|=m.reads;cases+=1
 assert domains==set(range(16))-{2}
 m=Memory([0]*65536);m.reads=set();m[0x9000:0x900b]=publish;m[0xcf86:0xcf96]=cookie
 c=NesMPU(memory=m,pc=0x9000)
 for _ in range(100):
  if c.pc==0x900b:break
  c.step()
 else:raise AssertionError('Publish loop failed to terminate')
 assert m.reads==set(range(1,16)) and bytes(m[0xbfe1:0xbff0])==cookie[1:]
 q=dict(passed=True,ROM_sha256=PIN,compare_cases=cases,compare_indices=sorted(domains),publish_indices=sorted(m.reads),table_physical_half_open=[0xf86,0xf96],proposed_gap_start=0xf96,formal_grant=False,scope='Exact compiled cookie loop domains, isolated CPU execution. Native loader lifecycle and all other bank consumers are separate.',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (O/'CF-cookie-tail.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,compare_cases=cases,publish_bytes=15)))
if __name__=='__main__':main()
