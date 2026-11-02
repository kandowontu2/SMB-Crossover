"""Freeze reviewed CPU successor and exact current1966 shared patch proposal."""
import json,zipfile
from pathlib import Path
import check_bubble_bobble_native_proxy_1102_v5 as Q
P=Q.P;C=Q.C;N=Q.N;R=Q.R;O=Q.O
CURRENT=R/'build/wwf-death-1102-v2/candidate.nes'
PIN='1966a4883a888a5e62f90c4d3e96d25ecf028ddd7d714214727793418d633243'


def main():
 old=P.scoped_load(P.ROM);b,q,route=Q.bundle();raw=CURRENT.read_bytes();assert P.sha(raw)==PIN
 # Original source padding survives the Ex typed source overlay. This is not
 # a new blank-byte lease. Bind exact old source/code and every typed reader.
 proto=R/'src/protoman.s';assert '.res $1108-(*-ProtoArtBegin), $ff'in proto.read_text()
 ex=R/'build/excitebike-pose-1101-v3';loader=(ex/'dispatch-loader.bin').read_bytes();current_loader=old['raw'][16+65*8192+0xe00:16+65*8192+0xe00+len(loader)]
 assert len(loader)==556 and all(a==d for i,(a,d)in enumerate(zip(loader,current_loader))if not 0x216<=i<0x226)
 assert(ex/'dispatch.s').read_text().count('ExRetireBoth:\n jsr ExRetire\n jmp $a849')==1
 assert 'F:start=$b031,size=49'in(ex/'dispatch.cfg').read_text()
 assert old['raw'][16+65*8192+0x102c:16+65*8192+0x1031]==bytes([255])*5
 lease=json.loads((ex/'dispatch-lease.json').read_text());assert lease['passed']and lease['source_declared_padding']and lease['A_CPU_half_open']==[0xa740,0xa800]
 proof_sources=[proto,R/'src/protoman_art.inc',R/'src/protoman_cold.s',R/'src/protoman_pose_ids.inc',R/'tools/audit/prepare_excitebike_dispatch_1101_v1.py',R/'tools/audit/compose_excitebike_owner_1101_v1.py',R/'tools/reference/excitebike_resident_dispatch_1101_v1.inc',ex/'dispatch.s',ex/'dispatch.cfg',ex/'dispatch-loader.bin',ex/'owner-loader.inc',ex/'scene.lbl',ex/'dispatch-lease.json']
 funding=dict(source_padding= dict(source='src/protoman.s',declaration='.res $1108-(*-ProtoArtBegin), $ff',original_Ex_lease_AE00_B108=776,old_source_overlay_end=0xb02c,next_fixed_segment_start=0xb031,five_pad_bytes_retained_from_original_source=True,not_alignment_directive=True),dispatcher_source_lease=dict(proof='tools/audit/prepare_excitebike_dispatch_1101_v1.py::lease',exact_half_open=[0xa740,0xa800],bytes=192,Proto_descriptor_index_domain=[0,26],immutable_descriptor_end_C=0xc696,complete_art_end_C=0xc738,reader_source='src/protoman_cold.s',successor_used=184,successor_spare=8),old_Ex_source_rebound_to_current=dict(source_loader_bytes=556,all_non_cookie_bytes_exact=True,cookie_half_open=[0xb016,0xb026]),complete_typed_indexed_and_indirect_domains=[dict(reader='ExHeadersByte/ExRetireByte/ExPublishByte',range=[0xb016,0xb026],index='X15..0',source='owner-loader.inc'),dict(reader='ExLoadSaveSmc/ExLoadRestoreSmc/ExDispatchSaveSmc/ExDispatchRestoreSmc',range=[0xb011,0xb016],index='X0..4/4..0',source='owner-loader.inc +excitebike_resident_dispatch_1101_v1.inc'),dict(reader='ExForeignLo/Hi/Bank-4,X',ranges=[[0xa7e5,0xa7e7],[0xb060,0xb062],[0xb105,0xb107]],index='OnlyX4/5 after bounded5SMC save; two UIselectors26/30',source='excitebike_resident_dispatch_1101_v1.inc'),dict(reader='ExCopyByte/ExVerifyByte/ExZeroByte (R0),Y',range=[0xc000,0xe000],index='OnlymappedRAM2/3 destinations; no ROM65 source pointer',source='owner-loader.inc'),dict(reader='ExDispatch FarCallCommon cached service',range=[0xa500,0xa56f],index='37aligned actualpublicrow targets0..36; typed37 newlybounded separately',source='excitebike_resident_dispatch_1101_v1.inc'),dict(reader='Native current farcall/JSR ingresses',targets=['A7E9scene','B026RetireBoth','B08C+3*row0..36','B100ROMreset'],source='Frozen actualPRG79 endpoint proof +source-bound native UI/scene andSh retirement seams; noB029 interior target')],surviving_interior_B029_B031_readers_entries=[],source_bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes())for p in proof_sources})
 receipts=[]
 for name in['native-proxy-CPU.json','native-proxy-Main-CPU.json','native-proxy-typed-contact-CPU.json','native-proxy-ports-CPU.json','native-proxy-cold-CPU.json']:
  p=O/name;z=json.loads(p.read_text());assert z['passed']
  for rel,h in z['bindings'].items():assert P.sha((R/rel).read_bytes())==h,('Stale successor receipt',name,rel)
  receipts.append(p)
 patches=[];covered=set()
 def span(bank,start,size,owner,proof,blob=None):
  at=16+bank*8192+(start&8191);pre=old['raw'][at:at+size];post=b['raw'][at:at+size]
  assert raw[at:at+size]==pre,('Current shared preimage',bank,hex(start))
  if blob is not None:assert post==(O/blob).read_bytes()
  covered.update(range(at,at+size));patches.append(dict(physical_PRG=bank,CPU_half_open=[start,start+size],file_offset=at,bytes=size,original_owner=owner,source_reclaim_proof=proof,old_SHA256=P.sha(pre),new_SHA256=P.sha(post),old_hex=pre.hex(),new_hex=post.hex(),compiled_blob='build/bubble-bobble-source-1101-v1/'+blob if blob else None,actual_changed_bytes=sum(a!=d for a,d in zip(pre,post))))
 span(123,0xaf40,len((O/'common-split.bin').read_bytes()),'Mac9source-declared192Bpad','common-cold-1102-v1 grant; exact9track/mixedrestart/DMC source closures.191of192 used.','common-split.bin')
 span(123,0xb9d6,len((O/'common-split-map.bin').read_bytes()),'Mac9source-declared42Bpad','Same formal247Bpool,38of42 used; BF93..BFA0 remains untouched.','common-split-map.bin')
 span(65,0xa740,len((O/'native-proxy-routes.bin').read_bytes()),'Ex192Bsource-funded Proto pad/dispatcher','Frozen route compaction178B +6B typed-input restore tail; total184of192; all37Ex ABI+foreign+ISR proof.','native-proxy-routes.bin')
 span(65,0xae00,len((O/'native-proxy-owner.bin').read_bytes()),'Ex556Bloader within AE00..B108 grant','Source-factor full9row common worker;531Bmanager, fulltwo16Bheaders, bothowner/currentExcookie/readback/protection/NMI equivalence.','native-proxy-owner.bin')
 span(65,0xb013,19,'Exoldloader/cookie extent','Manager endsB013; frozen source compact scene gate19B.','native-proxy-route-scene-gate.bin')
 span(65,0xb026,3,'ExRetireBoth11Bentry','Original JSRAE34/JMPA849 then5FF; replaced3BJMPCoRetire. AC2C/AD88 callers retain exactB026.','native-proxy-route-retire-stub.bin')
 span(65,0xb029,8,'ExRetireBoth reclaimed8B','Allbank65 absolute control/data operand census has zero interior readers/entries; typed37 only, realB0FB untouched.','native-proxy-typed-contact.bin')
 span(65,0xb031,49,'Exresident foreignUI continuation','Frozen source-compacted same native status/colors tail, full foreign differential; preserves37legacyveneers.','native-proxy-route-foreign.bin')
 span(65,0xb062,21,'Exresident scene continuation','Frozen source-compacted owning scene; originalExscene AXYP/state exact.','native-proxy-route-scene-own.bin')
 span(65,0xb101,2,'ExReset currentJSRcallee operand','Same existing row19 ROM-only retirement seam; retarget AE34→CoRetire; B100JSR opcode andfollowingSEC/RTS unchanged.')
 at=Q.Q.Q.location(old,'InitScreen')+8
 for off in[4,9]:
  pos=at+off;bank=(pos-16)//8192;pc=0xa000+(pos-16)%8192
  span(bank,pc,1,'Native InitScreen existing scene farcall operand','Frozen source-bound existing targetA7E9→CoSceneGateB013; originalclassification/foreigntail/frames unchanged.')
 span(74,0xbf03,49,'SMB2source owning contact gate','Frozen source exact49B PH/PHA classifier+SMB2 continuation; source duplicateA-save removal and sharedprecedingBF00JMP fund raw39 typed37. Foreign0..38 exact +original25 path; same49B.','native-proxy-contact-gate.bin')
 span(65,0xadb6,34,'Sh source-owned shot gate','Existing33Bshot +40Bbbox +1FF=74B. Duplicate SafecallA save omitted under actual outer farcall ABI; new39 compare costs1 net byte.','native-proxy-ports.bin')
 span(65,0xadd8,38,'Sh source-owned bbox gate shifted1B','NativeBoundingBoxCore inputAdead; source PHP-only/no redundantA reload/save funds raw39 and genericHuFullBox16. All23Shposes/fullSMC exact; totalshot+bbox72of74.','native-proxy-bbox.bin')
 span(77,0xab0d,1,'Native LmBoundingBoxGate existing farcall low operand','Actual current macro AB09 startsSTASafecallA; targetADD7→ADD8, highAD/bankC1 unchanged.')
 carriers=[]
 for i,page in enumerate([301,305,337,362,363,440,819,666,441]):
  at=1048592+1024*page;pre=old['raw'][at:at+1024];post=b['raw'][at:at+1024];assert raw[at:at+1024]==pre
  covered.update(range(at,at+1024));carriers.append(dict(physical_CHR=page,file_offset=at,bytes=1024,old_SHA256=P.sha(pre),new_SHA256=P.sha(post),new_blob='build/bubble-bobble-source-1101-v1/'+('native-proxy.bin'if i<8 else'native-proxy-helper.chr'),new_blob_offset=i*1024 if i<8 else 0,grant='bubble-bobble-rebase-1102-v2.json'if i<8 else'bubble-helper-row-1102-v2.json'))
 changes={i for i,(a,d)in enumerate(zip(old['raw'],b['raw']))if a!=d};assert changes<=covered,('Undeclared memory-only patch',sorted(changes-covered)[:16])
 merged=bytearray(raw)
 for i in changes:merged[i]=b['raw'][i]
 assert all(a==d for i,(a,d)in enumerate(zip(raw,merged))if i not in changes)
 assert merged[792580:792583]==bytes.fromhex('3aaf88'),'Current WWF3B row lost'
 assert old['raw'][16+79*8192:16+80*8192]==b['raw'][16+79*8192:16+80*8192]
 assert old['raw'][16+65*8192+0x108c:16+65*8192+0x1101]==b['raw'][16+65*8192+0x108c:16+65*8192+0x1101]
 flat=[]
 for p in patches:
  flat.append(dict(offset=p['file_offset'],old=p['old_hex'],new=p['new_hex'],role=p['original_owner']+'; '+p['source_reclaim_proof'],existing_grant='common-cold-1102-v1.json'if p['physical_PRG']==123 else'Existing Ex/Sh source-backed typed owner grant; actual successor routing grant pending',required_successor_grant='Root pending exact commonrouting/contact/ports grant'))
 for p in carriers:
  at=p['file_offset'];flat.append(dict(offset=at,old=old['raw'][at:at+1024].hex(),new=b['raw'][at:at+1024].hex(),role='Bub/Bob granted physical carrier '+str(p['physical_CHR']),existing_grant=p['grant'],required_successor_grant=None))
 manifest=dict(passed=True,proposal_only=True,ROM_written=False,admitted=False,base_ROM=str(CURRENT.relative_to(R)),base_ROM_SHA256=PIN,CPU_model_base_SHA256=P.PIN,in_memory_backend_only_over1966_SHA256=P.sha(merged),existing_PRG79_router_changed_bytes=0,existing37_Ex_veneers_realExMenuDone_unchanged=True,bodygate_ordinary_contact_row=37,HuBody11_profile_reject=True,typed_virtual_row37=dict(resident_entry=0xb029,private_entry=0xa06f,virtual_B0FB_never_executed=True,typed_input_restore_half_open=[0xa7f2,0xa7f8]),common_worker=dict(bytes=229,total_granted=247,unused=18),private_code=dict(A000_BFE0_used=8160-q['code_spare'],end=q['code_end'],spare=q['code_spare'],original_A100_B53A_unchanged=True,helper_tail_bytes=q['helper_bytes'],helper_tail_spare=q['helper_spare']),cookie=q['BB_cookie'],payload_SHA256=P.sha((O/'native-proxy.bin').read_bytes()),helper_row_SHA256=P.sha((O/'native-proxy-helper.chr').read_bytes()),shared_patches=patches,owned_carriers=carriers,changed_bytes=len(changes),no_new_mutable_RAM=True,no_AI_birth_hook=True,no_menu_or_confirmation_write=True,frontend_composition='Apply exact frontend1249B delta over1966 independently, retain AD64 confirmation SEC until root approves private native candidate. Frontend agent owns composer.',grant_status='Existing physical carriers, conditional RAM and247Bcommon storage granted. Actual commonrouting/typedcontact49B/Shports+caller bindings remain proposals for root review.',receipts={p.relative_to(R).as_posix():P.sha(p.read_bytes())for p in receipts},scope='Exactcurrent1966 old/new preimages and sole in-memory diff closure. Allcurrent Metal/Arthur/Ex and WWF outside declared patch bytes preserved; no candidate ROM written. Actual native/controller/stageclear qualification remains root-owned.')
 manifest.update(funding_closure=funding,patches=flat,exported_actual_entries=dict(native_contact37=0xb029,CoSceneGate=route['CoSceneGate'],CoRetire=q['owner_labels']['CoRetire'],HuBody11='ExistingB0AD remainsprofile rejection forraw39',NativeHead=q['vectors']['10']['target']if '10'in q['vectors']else q['vectors'][10]['target'],NativeSide=q['vectors']['14']['target']if '14'in q['vectors']else q['vectors'][14]['target'],NativeFullBox=q['labels']['BbNativeFullBox'],NativeShotGate=0xadb6,NativeBBoxGate=0xadd8))
 out=O/'native-proxy-shared-proposal-1966.json';out.write_text(json.dumps(manifest,indent=2)+'\n')
 source=[R/'tools/audit'/n for n in['prepare_bubble_bobble_native_proxy_1102_v5.py','check_bubble_bobble_native_proxy_1102_v5.py','check_bubble_bobble_native_main_1102_v5.py','check_bubble_bobble_typed_contact_1102_v5.py','check_bubble_bobble_native_ports_1102_v5.py','check_bubble_bobble_native_cold_1102_v5.py','freeze_bubble_bobble_native_proxy_1102_v5.py']]
 generated=[p for p in O.glob('native-proxy*')if p.suffix in['.bin','.chr','.s','.cfg','.lbl','.json']and not p.name.startswith('native-proxy-qualified-')]
 files=sorted(set(source+generated+proof_sources));packet=O/'native-proxy-qualified-1102-v5.zip'
 with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED,9)as z:
  for p in files:z.write(p,p.relative_to(R).as_posix())
 freeze=dict(passed=True,ROM_written=False,admitted=False,archive=packet.relative_to(R).as_posix(),archive_SHA256=P.sha(packet.read_bytes()),archive_bytes=packet.stat().st_size,manifest=out.relative_to(R).as_posix(),manifest_SHA256=P.sha(out.read_bytes()),source_files=[p.relative_to(R).as_posix()for p in source],files={p.relative_to(R).as_posix():dict(SHA256=P.sha(p.read_bytes()),bytes=p.stat().st_size)for p in files},inherited_frozen_inputs=['qualified-native-proofs-1102-v1.json','native-ingress-qualified-1102-v4.json'],scope=manifest['scope'])
 (O/'native-proxy-qualified-1102-v5.json').write_text(json.dumps(freeze,indent=2)+'\n');print(json.dumps(dict(passed=True,manifest=out.relative_to(R).as_posix(),shared_spans=len(patches),changed_bytes=len(changes),packet_bytes=packet.stat().st_size,packet_SHA256=freeze['archive_SHA256'],ROM_written=False)))


if __name__=='__main__':main()
