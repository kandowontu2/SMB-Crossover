"""Freeze exact55B private event successor and requested shared21B lease."""
import json,zipfile
from pathlib import Path
import check_bubble_native_event_1102_v9 as E
P=E.P;R=E.R;O=E.O;G=E.G


def main():
 old,new,q,route=E.bundle();prior=old['raw'];after=new['raw'];receipts=[]
 for name in['native-event-v9-CPU.json','native-event-v9-closure.json','native-bounce-owner-gate-measurement-v9.json']:
  p=O/name;z=json.loads(p.read_text());assert z['passed'],name
  for rel,h in z.get('bindings',{}).items():assert P.sha((R/rel).read_bytes())==h,('Stale receipt',name,rel)
  receipts.append(p)
 image=(O/'native-event-v9-image.bin').read_bytes();before=(O/'native-cold-fix.bin').read_bytes();art=(O/'native-cold-fix-helper.chr').read_bytes()
 assert image[0x100:0x153a]==before[0x100:0x153a]and len(image)==8192
 assert q['BB_cookie']==(bytes([0xa7,39,1])+bytes.fromhex(P.sha(image+art))[:13]).hex()
 patches=[];covered=set()
 def span(at,count,role,grant,proof):
  post=after[at:at+count];pre=prior[at:at+count];patches.append(dict(offset=at,old=pre.hex(),new=post.hex(),role=role,existing_grant=grant,source_proof=proof,old_SHA256=P.sha(pre),new_SHA256=P.sha(post)));covered.update(range(at,at+count))
 for z in q['shared_event_proposal']:
  span(z['offset'],len(bytes.fromhex(z['old'])),z['role'],'Conditional root reservation for v9 source measurement; exact shared successor grant still required','native-event-v9-closure.json; actual source-declared navigation .res and original source stomp ABI/callers')
 span(q['common_cookie_ROM_file_offset'],16,'Complete existing BB16B cookie; both headers bind unchanged art/helper and new explicit-event code','bubble-cold-fixed-1102-v8.json; exact v9 cookie successor pending','Only existing owner cookie changes; all531B manager instructions/Excookie/retire target are exact.')
 pages=[301,305,337,362,363,440,819,666]
 for pc,count,role in[(0xa000+27*3,3,'Private public27 vector becomes actual native stomp event'),(q['labels']['BbNativeStomp'],20,'Replace old velocity inference with saved-AXYP original D36B event callback'),(q['native_event']['old_inferred_ingress'],3,'Remove NativeIn heuristic; same layout retained with3NOP')]:
  offset=pc-0xa000;at=1048592+pages[offset//1024]*1024+offset%1024;span(at,count,role,'Existing Bub code carriers/conditionalRAM; exact v9 private successor pending','Original5434B source unchanged; existing20B leaf and existing vector/JSR extent reused. No new state or physical carrier.')
 changed={i for i,(a,b)in enumerate(zip(prior,after))if a!=b};assert changed<=covered and len(changed)==55
 assert before[0x100:0x153a]==image[0x100:0x153a]
 public=[i for i in range(38)if before[3*i:3*i+3]!=image[3*i:3*i+3]];assert public==[27]
 for bank in[29,65,66,74,76,77,79,96,123]:
  start=16+bank*8192;diff={i for i in changed if start<=i<start+8192}
  assert not diff or bank==65 and diff<=set(range(q['common_cookie_ROM_file_offset'],q['common_cookie_ROM_file_offset']+16)),bank
 assert all(prior[1048592+p*1024:1048592+(p+1)*1024]==after[1048592+p*1024:1048592+(p+1)*1024]for p in[441])
 manifest=dict(passed=True,proposal_only=True,ROM_written=False,native=False,admitted=False,base_ROM=G.B.ROM.relative_to(R).as_posix(),base_ROM_SHA256=G.B.PIN,in_memory_candidate_SHA256=P.sha(after),patches=patches,changed_bytes=55,shared_new_route_bytes=21,existing_complete_BB_cookie_bytes=16,private_actual_changed_bytes=24,source_original_A100_B53A_and800art_exact=True,whole1024_helper_art_row_exact=True,no_new_mutable_RAM=True,no_new_physical_carrier=True,fixed_MegaManBounceVelocity_unchanged=True,all_Sh_Ex_Arthur_Metal_WWF_frontend_bytes_retained=True,shared_scope='Only original124 source stomp thunk11B and source-declared navigation tail10B require a new routing grant; existing BBcookie successor16B. AllPRG65 instructions/37Exveneers/Shports/typed37/PRG79 unchanged.',native_stomp_event_API=dict(actual_chain='EnemyStomped -> fixed MegaManBounceVelocity ->124:A4B0 -> owner39 A0D6 -> existingA179/Y12 -> HuBounceOnly27 -> B0DD -> authenticated privateA051 -> A0E9',public_row=27,resident_veneer=0xb0dd,private_vector=0xa051,private_callback=0xa0e9,foreign_path='Every raw!=39 rejoins byte-identical124:A190 original chain with original savedP/Y/A. Native fallback side effects retained.',source_callback='One original D36B restart, same28update/43px jump and directional latch; full AXYP except public carry restored; native wrapper preserves its existingP contract. No velocity inference or second motion step.'),code_end=q['code_end'],private_code_spare=q['code_spare'],box_hole_bytes=q['box_hole_bytes'],box_hole_spare=q['box_hole_spare'],helper_bytes=224,helper_spare=0,cookie=q['BB_cookie'],payload_SHA256=P.sha(image),helper_SHA256=P.sha(art),receipts={p.relative_to(R).as_posix():P.sha(p.read_bytes())for p in receipts},native_Easy_stomp_qualified=False,native_performance_qualified=False,scope='Exact source/CPU-only successor over current private5a8a including delivered WWF951B. No ROM written, menu admission or installation. Root exact grant/composer/native actual gameplay tests remain required.')
 out=O/'native-event-v9-successor-5a8a.json';out.write_text(json.dumps(manifest,indent=2)+'\n')
 source=[R/'tools/audit'/n for n in['measure_bubble_native_bounce_router_1102_v9.py','measure_bubble_native_bounce_gate_1102_v9.py','prepare_bubble_native_event_1102_v9.py','check_bubble_native_event_1102_v9.py','check_bubble_native_event_closure_1102_v9.py','freeze_bubble_native_event_1102_v9.py']]
 generated=[p for p in O.glob('native-event-v9*')if p.suffix in['.bin','.s','.cfg','.lbl','.json']and not p.name.startswith('native-event-v9-qualified')]
 inputs=[O/'native-bounce-owner-gate-measurement-v9.json']+[R/'build/bub-menu-navigation-1102-v1'/n for n in['navigation.s','navigation.bin','navigation.lbl','proposal.json']]
 files=sorted(set(source+generated+inputs));packet=O/'native-event-v9-qualified.zip'
 with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED,9)as z:
  for p in files:z.write(p,p.relative_to(R).as_posix())
 freeze=dict(passed=True,ROM_written=False,admitted=False,archive=packet.relative_to(R).as_posix(),archive_SHA256=P.sha(packet.read_bytes()),archive_bytes=packet.stat().st_size,manifest=out.relative_to(R).as_posix(),manifest_SHA256=P.sha(out.read_bytes()),source_files=[p.relative_to(R).as_posix()for p in source],files={p.relative_to(R).as_posix():dict(SHA256=P.sha(p.read_bytes()),bytes=p.stat().st_size)for p in files},inherited_frozen_inputs=['native-cold-fix-qualified-1102-v8.json','native-stomp-qualified-1102-v7.json'],scope=manifest['scope'])
 (O/'native-event-v9-qualified.json').write_text(json.dumps(freeze,indent=2)+'\n');print(json.dumps(dict(passed=True,ROM_written=False,manifest=out.relative_to(R).as_posix(),manifest_SHA256=freeze['manifest_SHA256'],archive=freeze['archive'],archive_SHA256=freeze['archive_SHA256'],archive_bytes=freeze['archive_bytes'],expected_candidate_SHA256=manifest['in_memory_candidate_SHA256'],changed_bytes=55)))


if __name__=='__main__':main()
