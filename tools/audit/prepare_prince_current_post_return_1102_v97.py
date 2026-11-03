"""Granted Prince source rebase over exact root Bub66; memory manifest only."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import measure_prince_owner_routes_1102_v23 as A
import compile_prince_host_lifecycle_1102_v12 as L
from link_pit_rygar_sophia_audit_cpu import scoped_load
O=A.O;sha=lambda data:hashlib.sha256(data).hexdigest()
NIGHTLY=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
INSTALLED='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
PARENT='b7e2a161ea2781a8346b126b9c759f7c60f2583e2a18e58f8ca888d041c0bd53'
BUB=R/'build/bub-upgrades-root-1102-v65'
POOL=[341,343,345,347,349,351,353,355,357,359,361,365,369,373,377,381,383,385,387,389,391,393,544,545,605,607,609,611,613,615,617,619,621,623,625,627,690,691,692,693,695,795,291,514]


def validate(q):
 assert q.get('passed',q.get('status','').startswith('APPROVED'))
 for name,digest in q.get('bindings',{}).items():assert sha((R/name).read_bytes())==digest,name


def parent():
 grant=json.loads((R/'docs/qa/allocations/joint-native-rare-gate-1102-v70.json').read_text());assert grant['status'].startswith('APPROVED')
 q=json.loads((BUB/'proposal.json').read_text());validate(q);raw=bytearray(NIGHTLY.read_bytes());assert sha(raw)in [INSTALLED,PARENT]
 image=(BUB/'private-image.bin').read_bytes();cookie=bytes.fromhex(q['new_cookie']);assert cookie.hex()=='a727012fc2a56833ecdc5633d1cb1e7f'
 if sha(raw)==INSTALLED:
  assert q['parent_ROM_SHA256']==INSTALLED
  for i,page in enumerate(q['pages']):raw[1048592+1024*page:1048592+1024*(page+1)]=image[i*1024:(i+1)*1024]
  at=q['cookie_offset'];assert raw[at:at+16]==bytes.fromhex(q['old_cookie']);raw[at:at+16]=cookie
  for row in grant['approved_exact_patches']:
   at=row['file_offset'];before=bytes.fromhex(row['old']);after=bytes.fromhex(row['new']);assert raw[at:at+len(before)]==before;raw[at:at+len(after)]=after
 assert sha(raw)==PARENT
 for i,page in enumerate(q['pages']):assert raw[1048592+1024*page:1048592+1024*(page+1)]==image[i*1024:(i+1)*1024]
 assert raw[q['cookie_offset']:q['cookie_offset']+16]==cookie and not set(POOL)&set(q['pages'])
 native=scoped_load(L.BASE);return dict(native,raw=bytes(raw)),q


def bundle():
 base,bub=parent();raw=base['raw'];grant_path=R/'docs/qa/allocations/prince-post-return-lifetime-1102-v70.json';grant=json.loads(grant_path.read_text());assert grant['status'].startswith('APPROVED')
 assert grant['proposal_SHA256']==sha((O/'post-return-lifetime-proposal-v91.json').read_bytes())
 runtime=(O/'native-runtime-v78.bin').read_bytes();metadata=(O/'native-metadata-v78.bin').read_bytes();state=(O/'native-state-v78.bin').read_bytes();payload=(O/'cold-pool-v87.bin').read_bytes();lab=json.loads((O/'native-labels-v78.json').read_text())
 assert len(payload)==44472 and(lab['PpNativeRoute'],lab['PpNativeRetire'])==(0xdf1e,0xd98f)
 cookie=bytes([0xa7,38,2])+hashlib.sha256(runtime+metadata+state+payload).digest()[:13]
 text=(O/'collision-owner-v59.s').read_text();old=''' cmp #38
 bne PrWorkerDone
 CoFar PrColdBoot,3''';new=''' cmp #38
 beq PrWorkerPrince
 sec ; Successful common Ex37/Bub39 cold must retain C1 after CMP.
 rts
PrWorkerPrince:
 CoFar PrColdBoot,3''';assert text.count(old)==1;text=text.replace(old,new)
 retire=bub['labels']['BbNativeRetire'];old='BbNativeRetire=$bb7a';assert text.count(old)==1;text=text.replace(old,f'BbNativeRetire=${retire:04x}')
 start=text.index('CoBBCookie:.byte ');end=text.index('\n',start);text=text[:start]+'CoBBCookie:.byte '+','.join(f'${v:02x}'for v in bytes.fromhex(bub['new_cookie']))+text[end:]
 start=text.index('PrCookie:\n')+len('PrCookie:\n');end=text.index('\nPrExtraEnd:',start);text=text[:start]+'.byte '+','.join(f'${v:02x}'for v in cookie)+text[end:]
 cfg=(O/'collision-owner-v59.cfg').read_text().replace('collision-owner-extra-v59.bin','post-owner-extra-v97.bin');owner,owner_labels=A.assemble('post-owner-v97',text,cfg);extra=(O/'post-owner-extra-v97.bin').read_bytes()
 assert len(owner)==531 and len(extra)==94 and owner_labels['CoCold']==0xae00 and owner_labels['CoRetire']==0xae0b and owner_labels['CoOwnerEnd']==0xb013 and owner_labels['PrTypedWorker']==0xab72 and owner_labels['PrExtraEnd']==0xabd0
 selector,select_labels=A.assemble('post-selector-v97',(O/'deferred-selector-v79.s').read_text(),(O/'deferred-selector-v79.cfg').read_text());assert selector==(O/'deferred-selector-v79.bin').read_bytes()and len(selector)==156
 prior=json.loads((O/'collision-manifest-v59.json').read_text());validate(prior);post=bytearray(raw);patches=[];written=set()
 replacements={(65,0xa740):selector,(65,0xae00):owner,(65,0xab72):extra}
 def put(at,blob,**fields):
  extent=set(range(at,at+len(blob)));assert not written&extent,(at,'Overlap');written.update(extent);before=raw[at:at+len(blob)];post[at:at+len(blob)]=blob
  patches.append(dict(file_offset=at,bytes=len(blob),old_hex=before.hex(),new_hex=blob.hex(),old_SHA256=sha(before),new_SHA256=sha(blob),**fields))
 for row in prior['patches']:
  if 'physical_PRG'not in row:continue
  at=row['file_offset'];before=bytes.fromhex(row['old_hex']);actual=raw[at:at+len(before)];exceptions=set(range(bub['cookie_offset'],bub['cookie_offset']+16))
  assert all(a==z or at+i in exceptions for i,(a,z)in enumerate(zip(actual,before))),('Current shared preimage drift',at)
  pc=row['CPU_half_open'][0];blob=replacements.get((row['physical_PRG'],pc),bytes.fromhex(row['new_hex']))
  put(at,blob,physical_PRG=row['physical_PRG'],CPU_half_open=[pc,pc+len(blob)],role='Existing granted Prince resident/descriptor routing; current body cookies and successful Ex coldC')
 for i,page in enumerate(POOL):
  blob=payload[i*1024:(i+1)*1024]
  if blob:put(1048592+page*1024,blob,physical_CHR=page,source_offset=i*1024,role='Existing44 Prince carriers; original art exact plus granted cold/runtime/state')
 for row in grant['approved_exact_PRG124_hook_patches']:
  at=row['file_offset'];before=bytes.fromhex(row['old_hex']);assert raw[at:at+len(before)]==before
  put(at,bytes.fromhex(row['new_hex']),physical_PRG=124,CPU_half_open=row['CPU_half_open'],role='Granted same-bank native post-resident death hook')
 # Every existing Bub carrier and its physical art remain exact. The manager
 # cookie has a new symbolic address after adding Prince but identical bytes.
 for page in bub['pages']+[441]:
  at=1048592+page*1024;assert post[at:at+1024]==raw[at:at+1024]
 at=16+65*8192+owner_labels['CoBBCookie']-0xa000;assert post[at:at+16]==bytes.fromhex(bub['new_cookie'])
 joint=json.loads((R/'docs/qa/allocations/joint-native-rare-gate-1102-v70.json').read_text())
 for row in joint['approved_exact_patches']:
  at=row['file_offset'];blob=bytes.fromhex(row['new']);assert not written&set(range(at,at+len(blob)))and post[at:at+len(blob)]==blob
 changed={i for i,(a,z)in enumerate(zip(raw,post))if a!=z};assert changed<=written
 return base,dict(base,raw=bytes(post)),patches,dict(Prince_cookie=cookie.hex(),Bub_cookie=bub['new_cookie'],Bub_native_retire=retire,manager_bytes=531,extra_bytes=94,extra_remaining=4,selector_bytes=156,selector_remaining=22,Ex_success_carry_repaired=True,all_current_Bub_body_art_exact=True,joint_gate_exact=True,new_native_route=lab['PpNativeRoute'],native_retire=lab['PpNativeRetire'],actual_changed_bytes=len(changed),physical_pages=44,payload_bytes=len(payload),physical_spare=45056-len(payload))


def main():
 base,new,patches,details=bundle();files=[Path(__file__),BUB/'proposal.json',BUB/'private-image.bin',O/'collision-manifest-v59.json',O/'post-return-lifetime-proposal-v91.json',O/'post-return-checkpoint-v95.json',O/'native-runtime-v78.bin',O/'native-metadata-v78.bin',O/'native-state-v78.bin',O/'cold-pool-v87.bin',O/'post-owner-v97.s',O/'post-owner-v97.bin',O/'post-owner-extra-v97.bin',O/'post-selector-v97.s',O/'post-selector-v97.bin',R/'docs/qa/allocations/prince-post-return-lifetime-1102-v70.json',R/'docs/qa/allocations/joint-native-rare-gate-1102-v70.json']
 q=dict(passed=True,private_source_composition_only=True,ROM_written=False,menu_admitted=False,installed=False,installed_ancestor_SHA256=INSTALLED,parent_memory_SHA256=sha(base['raw']),expected_memory_only_SHA256=sha(new['raw']),patches=patches,details=details,required='Actual complete Ex37/Prince38/Bub39 cold/load/header/retire and changed-image lifecycle/respawn/IRQ/native mechanics. This manifest alone is not native-ready. No fourth owner/DK route or performance manager rewrite.',bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in files})
 (O/'post-return-manifest-v97.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['patches','bindings']}))


if __name__=='__main__':main()
