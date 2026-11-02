"""One exact current Darkwing table hole, never inferred from page contents."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools/reference')]
import compile_prince_host_lifecycle_1102_v12 as L
import check_hogan_current_bounded_v1 as N
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
O=L.O;PAGE=291
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 assert sha(L.BASE)==L.PIN;b=scoped_load(L.BASE);raw=b['raw'];pool=json.loads((O/'pool-proposal.json').read_text())
 assert PAGE not in pool['proposed_physical_CHR_pages']
 collisions={n:p for n,p in pool['domains'].items()if PAGE in p};assert not collisions
 # The old complete finite writer inventory remains at its actual current
 # ROM offsets. Full containing private source chunks bind the RAM writers.
 inv=R/'build/metal-storm-chr-closure-1101-v10/current-consumer-inputs.json';old=json.loads(inv.read_text());direct=0;changed=[]
 for w in old['unchanged_inherited_writers']:
  if Path(w['file']).suffix!='.nes':continue
  at=w['file_offset'];expected=bytes.fromhex(w['old_bytes'])
  if raw[at:at+len(expected)]!=expected:changed.append(dict(segment=w['segment'],file_offset=at,old=expected.hex(),actual=raw[at:at+len(expected)].hex()))
  else:direct+=1
 prior=json.loads((O/'writer-preservation.json').read_text());private=[]
 for w in prior['private_writer_bindings']:
  matches=[p for p in w['source_page_matches']if hashlib.sha256(raw[1048592+1024*p:1048592+1024*(p+1)]).hexdigest()==w['source_chunk_SHA256']]
  assert matches,(w['segment'],w['source_offset']);private.append(dict(segment=w['segment'],source_offset=w['source_offset'],actual_current_page_matches=matches))
 # All direct old table bytes remain exact; historical retired SMB3 tables
 # are intentionally excluded from the already refined live domain union.
 tables=0;changed_tables=[]
 for name,v in old['current_table_bytes'].items():
  if Path(v['file']).suffix!='.nes':continue
  at=v['file_offset'];expected=bytes.fromhex(v['hex'])
  if raw[at:at+len(expected)]==expected:tables+=1
  else:changed_tables.append(name)
 # Original/current Darkwing body and weapon selector tables are explicit.
 art=R/'src/darkwing_art.inc';text=art.read_text();actual_tables={}
 def table(name):
  body=text.split(name+':',1)[1];values=[]
  for line in body.splitlines():
   line=line.strip()
   if not line:continue
   if not line.startswith('.byte '):break
   values.extend(int(x)for x in line[6:].split(','))
  at=location(b,name);assert raw[at:at+len(values)]==bytes(values)
  actual_tables[name]=dict(file_offset=at,bytes=len(values),values=values,SHA256=hashlib.sha256(bytes(values)).hexdigest());return values
 pages=table('DwPoseBankLo');base=table('DwAnimationBase');last=table('DwAnimationLast');delay=table('DwAnimationDelay')
 assert len(pages)==71 and len(base)==len(last)==len(delay)==42 and 35 not in pages
 domain=sorted({256+v for v in pages});assert domain==pool['domains']['Darkwing body']
 assert all(base[i]+last[i]<len(pages)for i in range(42))
 oldrom=R/'build/arthur-side-clamp-1101-v8/weapon-tail-candidate.nes';oldraw=oldrom.read_bytes();spans=[]
 for name in ['DwAnimate','DwPublishBody','DwDrawShots','X5PublishChr','X5SetPhysicalChr','X5SetSpecialChr']:
  at=location(b,name);bank=(at-16)//8192;start=16+8192*bank
  assert raw[start:start+8192]==oldraw[start:start+8192],('Published source bank changed',name,bank)
  spans.append(dict(name=name,physical_PRG=bank,PC=address(b,name),whole_bank_SHA256=hashlib.sha256(raw[start:start+8192]).hexdigest()))
 seed=N.fresh(b);bodycases=0;emitted=set()
 for anim in range(42):
  for phase in range(last[anim]+1):
   for face in [1,2]:
    for tick in [0,delay[anim]]:
     m=N.fork(seed);N.put(m,SelectedCharacter=address(b,'CHARACTER_SCROOGE'),DarkwingVariant=1,DwAnim=anim,DwPhase=phase,DwAnimTick=tick,PlayerFacingDir=face)
     N.invoke(m,'DwAnimate',a=anim);N.invoke(m,'DwPublishBody');page=N.get(m,'CurrentCHRBank')+256*(N.get(m,'X5ChrMode')&3)
     assert page in domain and page!=PAGE;(emitted.add(page));bodycases+=1
 # Actual weapon publisher is independent of weapon age/type: the two page
 # setters run before the10-slot draw loop. Empty slots still execute ingress.
 m=N.fork(seed);N.put(m,SelectedCharacter=address(b,'CHARACTER_SCROOGE'),DarkwingVariant=1)
 for i in range(10):m[address(b,'RgShotType')+i]=0
 N.invoke(m,'DwDrawShots');weapons=[N.get(m,'SsChrPhysical')+256*(N.get(m,'X5SpecialChrUpper')&3),N.get(m,'CurrentCHRBank',5)+256*(N.get(m,'X5ChrMode',5)&3)]
 assert weapons==[302,303]
 # Legacy CHR mapping explicitly clears5130 and writes one byte. Therefore
 # it cannot publish any physical page>=256, including291. Typed upper1
 # publications are covered by the finite actual source domains above.
 legacy=(R/'src/mmc5_expanded.s').read_text();assert 'X5PublishChr:\n  lda X5WideChrActive\n  jne X5WidePublication\n  lda #0\n  sta $5130'in legacy
 assert 'lda ChrPhysicalMap,y'in legacy
 occupied={*pool['proposed_physical_CHR_pages'],301,305,337,362,363,440,441,666,819}
 assert PAGE not in occupied
 image=raw[1048592+PAGE*1024:1048592+(PAGE+1)*1024]
 q=dict(passed=not changed and not changed_tables,proposal_only=True,resource_granted=False,ROM_written=False,current_ROM_SHA256=L.PIN,proposed_page=PAGE,bytes=1024,file_offset=1048592+PAGE*1024,preimage_SHA256=hashlib.sha256(image).hexdigest(),allocation_basis='Actual source selector hole: Darkwing low35 is absent from every71pose entry;42animation base/last ranges stay within those71 rows. Generic legacy maps always publish upper0. This does not rely on FF/zero contents.',existing_all_finite_domains_exclude_page=True,exact_Darkwing_body_domain=domain,actual_Darkwing_body_cases=bodycases,actual_Darkwing_pages_seen=sorted(emitted),actual_Darkwing_weapon_pages=weapons,actual_tables=actual_tables,whole_native_publisher_banks_unchanged_since_granted_domain_ROM=spans,inherited_direct_writers_exact=direct,changed_inherited_direct_writers=changed,inherited_private_writer_chunks_exact=len(private),private_writer_bindings=private,current_old_table_bindings_exact=tables,changed_old_tables=changed_tables,all_current_42_and_Bub9_excluded=True,remaining=['Root must review the finite consumer/lease closure and grant291 before any ROM write.','Actual setter/menu/lag-NMI transient291 cuts follow separately.','RAM2 executable-state amendment and owner/cold/scene/native-services remain independent.'],scope='One source/table-derived carrier proposal on1966, rebinding existing finite domain evidence and complete inherited writer instructions to current ROM. No source art is replaced and no storage is inferred from blank bytes.',bindings={str(p.relative_to(R)):sha(p)for p in [Path(__file__),L.BASE,inv,O/'pool-proposal.json',O/'writer-preservation.json',art,R/'src/darkwing_core.s',R/'src/darkwing_weapons.s',R/'src/mmc5_expanded.s',R/'docs/qa/allocations/roster-rebase-1102-v3.json',R/'docs/qa/allocations/roster-rebase-1102-v4.json']})
 (O/'extra-carrier-291-v14.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','actual_tables','private_writer_bindings','whole_native_publisher_banks_unchanged_since_granted_domain_ROM']}))


if __name__=='__main__':main()
