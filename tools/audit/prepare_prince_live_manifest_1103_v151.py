"""Exact private149/150 memory proposal over cf7; no ROM emission."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import prepare_prince_strike_manifest_1103_v130 as C
O=C.O;sha=C.M.sha


def image():
 q=json.loads((O/'live-manifest-v151.json').read_text());C.M.validate(q);base,_=C.parent();raw=bytearray(base['raw'])
 for row in q['patches']:
  at=row['file_offset'];before=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex']);assert raw[at:at+len(before)]==before;raw[at:at+len(after)]=after
 assert sha(raw)==q['expected_memory_only_SHA256'];return dict(base,raw=bytes(raw)),q


def main():
 base,bub=C.parent();raw=base['raw'];prior=json.loads((O/'strike-manifest-v130.json').read_text());C.M.validate(prior)
 payload=(O/'cold-pool-v150.bin').read_bytes();assert len(payload)<=45056
 cookie=bytes([0xa7,38,2])+__import__('hashlib').sha256(b''.join((O/f'native-{n}-v149.bin').read_bytes()for n in ['runtime','metadata','state'])+payload).digest()[:13]
 text=(O/'post-owner-v149.s').read_text();a=text.index('PrCookie:\n')+len('PrCookie:\n');z=text.index('\nPrExtraEnd:',a);text=text[:a]+'.byte '+','.join(f'${v:02x}'for v in cookie)+text[z:]
 cfg=(O/'post-owner-v149.cfg').read_text().replace('post-owner-extra-v149.bin','post-owner-extra-v151.bin')
 owner,lab=C.M.A.assemble('post-owner-v151',text,cfg);(O/'post-owner-v151.o').unlink();extra=(O/'post-owner-extra-v151.bin').read_bytes();selector=(O/'post-selector-v149.bin').read_bytes()
 assert (len(owner),len(extra),len(selector))==(531,98,177)
 replacements={(65,0xae00):owner,(65,0xab72):extra,(65,0xa740):selector};patches=[];post=bytearray(raw);written=set()
 def put(at,data,**fields):
  extent=set(range(at,at+len(data)));assert not written&extent;written.update(extent);before=raw[at:at+len(data)];post[at:at+len(data)]=data;patches.append(dict(file_offset=at,bytes=len(data),old_hex=before.hex(),new_hex=data.hex(),old_SHA256=sha(before),new_SHA256=sha(data),**fields))
 for row in prior['patches']:
  if 'physical_PRG'not in row:continue
  pc=row['CPU_half_open'][0];data=replacements.get((row['physical_PRG'],pc),bytes.fromhex(row['new_hex']));put(row['file_offset'],data,physical_PRG=row['physical_PRG'],CPU_half_open=[pc,pc+len(data)],role='Current granted route plus explicit149 shared/lifetime alternative pending root review')
 for index,page in enumerate(C.M.POOL):
  data=payload[index*1024:(index+1)*1024]
  if data:put(1048592+1024*page,data,physical_CHR=page,source_offset=index*1024,role='Existing44carriers; originalart unchanged;149/150 ownedcode/data')
 pages=bub['pages']+[441]
 for page in pages:
  at=1048592+1024*page;assert post[at:at+1024]==raw[at:at+1024]
 assert post[16+65*8192+lab['CoBBCookie']-0xa000:16+65*8192+lab['CoBBCookie']-0xa000+16]==bytes.fromhex(C.COOKIE)
 q=dict(passed=True,private_source_proposal_only=True,root_shared_and_lifetime_grant_required=True,ROM_written=False,menu_admitted=False,installed=False,parent_memory_SHA256=sha(raw),expected_memory_only_SHA256=sha(post),Prince_cookie=cookie.hex(),Bub_cookie=C.COOKIE,patches=patches,details=dict(manager_bytes=531,extra_bytes=98,selector_bytes=177,physical_pages=44,payload_bytes=len(payload),physical_spare=45056-len(payload),runtime_version=149,backing_version=150,live_phase_half_open=[0xbfa3,0xbfd8],packet_stage_half_open=[0xc200,0xc235],current_Bub_body_art_exact=True),required='Finite executable/readers/NativeCallKind writer-value closure and full source-backed cold/warm/foreign/retire/corruption/lifecycle/IRQ qualification, then exact root private execution/shared grant. No ROM/menu/install admission implied.',bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),Path(C.__file__),O/'strike-manifest-v130.json',O/'live-policies-measurement-v149.json',O/'cold-link-storage-v150.json',O/'cold-pool-v150.bin',O/'post-owner-v151.s',O/'post-owner-v151.bin',O/'post-owner-extra-v151.bin',O/'post-selector-v149.s',O/'post-selector-v149.bin',O/'native-labels-v149.json',*[O/f'native-{n}-v149.bin'for n in ['runtime','metadata','state']]]})
 (O/'live-manifest-v151.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['patches','bindings']}))


if __name__=='__main__':main()
