"""Exact currentcf7 source159 memory proposal, no ROM/menu emission."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import measure_prince_backdrop_binding_1103_v157 as B
C,O,sha=B.M.C,B.O,B.M.sha


def image():
 q=json.loads((O/'backdrop-manifest-v159.json').read_text());C.M.validate(q);base,_=C.parent();raw=bytearray(base['raw'])
 for row in q['patches']:
  at=row['file_offset'];before=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex']);assert raw[at:at+len(before)]==before;raw[at:at+len(after)]=after
 assert sha(raw)==q['expected_memory_only_SHA256'];return dict(base,raw=bytes(raw)),q


def main():
 base,bub=C.parent();raw=base['raw'];prior=json.loads((O/'live-manifest-v155.json').read_text());C.M.validate(prior)
 payload=(O/'cold-pool-v158.bin').read_bytes();cookie=bytes([0xa7,38,2])+hashlib.sha256(b''.join(B.images())+payload).digest()[:13]
 text=(O/'post-owner-v155.s').read_text();a=text.index('PrCookie:\n')+len('PrCookie:\n');z=text.index('\nPrExtraEnd:',a);text=text[:a]+'.byte '+','.join(f'${v:02x}'for v in cookie)+text[z:]
 cfg=(O/'post-owner-v130.cfg').read_text().replace('post-owner-extra-v130.bin','post-owner-extra-v159.bin');owner,lab=C.M.A.assemble('post-owner-v159',text,cfg)
 for ext in ['o','cfg']:(O/('post-owner-v159.'+ext)).unlink()
 extra=(O/'post-owner-extra-v159.bin').read_bytes();selector=(O/'post-selector-v153.bin').read_bytes();assert(len(owner),len(extra),len(selector))==(531,98,175)
 replacements={(65,0xae00):owner,(65,0xab72):extra,(65,0xa740):selector};patches=[];post=bytearray(raw);written=set()
 def put(at,data,**fields):
  extent=set(range(at,at+len(data)));assert not written&extent;written.update(extent);before=raw[at:at+len(data)];post[at:at+len(data)]=data;patches.append(dict(file_offset=at,bytes=len(data),old_hex=before.hex(),new_hex=data.hex(),old_SHA256=sha(before),new_SHA256=sha(data),**fields))
 for row in prior['patches']:
  if 'physical_PRG'not in row:continue
  pc=row['CPU_half_open'][0];data=replacements.get((row['physical_PRG'],pc),bytes.fromhex(row['new_hex']));put(row['file_offset'],data,physical_PRG=row['physical_PRG'],CPU_half_open=[pc,pc+len(data)],role='Current granted route plus exact pending153 shared/lifetime alternative, source backdrop157')
 for index,page in enumerate(C.M.POOL):
  data=payload[index*1024:(index+1)*1024]
  if data:put(1048592+1024*page,data,physical_CHR=page,source_offset=index*1024,role='Existing44carriers, originalart unchanged, correctedsource cold/live payload')
 for page in bub['pages']+[441]:
  at=1048592+1024*page;assert post[at:at+1024]==raw[at:at+1024]
 assert post[16+65*8192+lab['CoBBCookie']-0xa000:16+65*8192+lab['CoBBCookie']-0xa000+16]==bytes.fromhex(C.COOKIE)
 q=dict(passed=True,private_source_proposal_only=True,root_shared_and_lifetime_grant_required=True,ROM_written=False,menu_admitted=False,installed=False,parent_memory_SHA256=sha(raw),expected_memory_only_SHA256=sha(post),Prince_cookie=cookie.hex(),Bub_cookie=C.COOKIE,patches=patches,details=dict(manager_bytes=531,extra_bytes=98,selector_bytes=175,selector_spare=3,manager_executed_padding_unchanged=True,physical_pages=44,payload_bytes=len(payload),physical_spare=45056-len(payload),runtime_version=153,metadata_state_tables_version=157,backing_version=158,live_phase_half_open=[0xbfa3,0xbfd8],installer_half_open=[0xc766,0xc77f],packet_stage_half_open=[0xc200,0xc235],current_Bub_body_art_exact=True),required='Actual159 fullcold/current-owner/foreign/failclosed/IRQ/FF/nested and palette/name/entrance tests then exact root shared/lifetime amendment. No ROM emission, menu or nightly admission.',bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),Path(B.__file__),O/'backdrop-binding-v157.json',O/'backdrop-pool-v158.json',O/'cold-pool-v158.bin',O/'live-manifest-v155.json',O/'post-owner-v159.s',O/'post-owner-v159.bin',O/'post-owner-extra-v159.bin',O/'post-selector-v153.s',O/'post-selector-v153.bin',O/'native-labels-v153.json']})
 (O/'backdrop-manifest-v159.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['patches','bindings']}))


if __name__=='__main__':main()
