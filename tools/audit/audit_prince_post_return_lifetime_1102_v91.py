"""Exact source-dead lifetime/hook proposal; no resource or menu grant inferred."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_post_return_core_1102_v79 as C
O=C.O
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
 names=['post-return-measurement-v78.json','deferred-death-measurement-v78.json','deferred-death-CPU-v79.json','post-return-foreign-CPU-v81.json','tag-transport-CPU-v84.json','cold-link-storage-v87.json','native-stack-CPU-v89.json','post-return-cold-CPU-v90.json','post-return-nested-IRQ-CPU-v92.json']
 proofs={n:json.loads((O/n).read_text())for n in names}
 for name,q in proofs.items():
  assert q.get('passed',q.get('measured')),(name,'Not measured/passed')
  for path,digest in q.get('bindings',{}).items():assert sha(R/path)==digest,(name,path)
 graph={k:v for n in ['contact-recovery.json','world-coordinate-recovery-v7.json','combat-tail-recovery-v34.json']for k,v in json.loads((O/n).read_text())['instructions'].items()};assert len(graph)==2485
 overlaps={};direct=[];packet=[]
 for key,v in graph.items():
  if v['mn']in ['JSR','JMP']or v['mode']not in ['abs','zpg','abx','aby','zpx','zpy']:continue
  lo=v['value'];hi=lo+(256 if v['mode']in ['abx','aby','zpx','zpy']else 1)
  if lo<0x800 and hi>0x766:
   overlaps[key]=v
   if v['mode']in ['abs','zpg']:direct.append(key)
  if lo<0x235 and hi>0x200:packet.append(key)
 assert not direct and not packet
 assert set(overlaps)=={'5:871D','5:8725','4:AD50','4:B8DB','7:E991','7:E996'}
 prior=json.loads((O/'collision-lifetime-proposal-v62.json').read_text());assert prior['passed']
 assert prior['original_reader_closure']['finite_HP_indices']==[0,1]
 assert prior['original_reader_closure']['source_unreachable_ledger']==['4:B8DB','7:E991','7:E996']
 assert {k:v for k,v in overlaps.items()}==prior['original_reader_closure']['conservative_audio_index_sites']
 cold=proofs['post-return-cold-CPU-v90.json'];hot=proofs['native-stack-CPU-v89.json'];nested=proofs['post-return-nested-IRQ-CPU-v92.json'];fit=proofs['cold-link-storage-v87.json'];foreign=proofs['post-return-foreign-CPU-v81.json'];tags=proofs['tag-transport-CPU-v84.json']
 assert fit['physical_spare']==cold['physical_spare']==584 and fit['payload_bytes']==44472
 assert len(cold['corruption_fail_closed'])==5 and len(cold['cold_guard_rejections'])==9 and cold['positive']['distinct_staged_prefix_instruction_PC']==11
 assert hot['real_IRQ_lagNMI_cuts']=={'IRQ':1846,'lagNMI':1846}and hot['actual_lag_NmiDisable']==255
 assert hot['all_lag_cuts_reached_lag_branch_exactly_once']and hot['all_lag_cuts_rejected_regular_branch']
 assert nested['counts']['lag_NMI_gather']==1846 and nested['counts']['nested_IRQ']>0
 assert tags['physical_operand']==0x179 and tags['selector_growth']==0 and tags['bad_header_bytes_rejected_before_stage']==32
 audio=(O/'native-audio-v78.s').read_text();public=(O/'native-public-v78.s').read_text();policies=(O/'native-policies-v78.s').read_text();runtime=(O/'native-runtime-v78.bin').read_bytes();metadata=(O/'native-metadata-v78.bin').read_bytes();state=(O/'native-state-v78.bin').read_bytes()
 assert ' lda $c65f,y\n sta $c766,y\n cmp $c766,y'in audio and ' cpy #154'in audio
 assert ' ldx #$65\nFreshLastPage:\n sta $c700,x\n dex\n bpl FreshLastPage'in public
 assert public.count('PpServiceTag=$0179')==1
 assert len(runtime)==8159 and len(metadata)==6095 and 0xc800+len(metadata)==0xdfcf and len(state)==1529
 assert metadata[-1]==0x20 and ' cpy #6'in policies and 'ColorsPacket:.byte $3f,$11,3,$27,$16,$20'in policies
 installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes();patches=[]
 for pc,name,size in [(0xa760,'post-return-v78.bin',15),(0xa795,'post-return-second-v78.bin',15)]:
  blob=(O/name).read_bytes();at=16+124*8192+pc-0xa000;old=installed[at:at+size];assert old==bytes([0xea])*size
  patches.append(dict(physical_PRG=124,CPU_half_open=[pc,pc+len(blob)],file_offset=at,old_hex=old[:len(blob)].hex(),new_hex=blob.hex(),full_source_pad_half_open=[pc,pc+size],full_pad_preimage_hex=old.hex(),full_pad_preimage_SHA256=hashlib.sha256(old).hexdigest(),untouched_tail_bytes=size-len(blob)))
 at=16+124*8192+0xd75;assert installed[at:at+3]==bytes.fromhex('8d6a01');patches.append(dict(physical_PRG=124,CPU_half_open=[0xad75,0xad78],file_offset=at,old_hex='8d6a01',new_hex='2060a7',predecessor_JSR_FarCallCommon_hex=installed[at-3:at].hex()))
 assert patches[-1]['predecessor_JSR_FarCallCommon_hex']=='205a01'
 files=[Path(__file__),*[O/n for n in names],O/'contact-recovery.json',O/'world-coordinate-recovery-v7.json',O/'combat-tail-recovery-v34.json',O/'collision-lifetime-proposal-v62.json',O/'native-services-v78.s',O/'native-audio-v78.s',O/'native-public-v78.s',O/'native-policies-v78.s',O/'native-runtime-v78.bin',O/'native-metadata-v78.bin',O/'native-state-v78.bin',O/'native-labels-v78.json',O/'post-return-v78.s',O/'post-return-v78.bin',O/'post-return-second-v78.bin',O/'deferred-selector-v79.s',O/'deferred-selector-v79.bin',O/'cold-worker-v87.s',O/'cold-worker-v87.bin',O/'cold-pool-v87.bin',R/'docs/qa/allocations/prince-collision-lifetime-1102-v62.json']
 q=dict(passed=True,proposal_only=True,resource_granted=False,ROM_written=False,menu_or_install_admitted=False,source_fixture_parent_SHA256='16a9de64b18370a03885ff503141fc08edd25f3bd026d480854a1754efa1490b',current_installed_hook_preimage_SHA256=hashlib.sha256(installed).hexdigest(),exact_shared_hook_patches=patches,requested_existing_exclusive_RAM2_half_open=dict(synchronous_gateway_packet=[0xc200,0xc20d],live_audio_extension=[0xc766,0xc780],cold_prefix_PC_extension=[0xc678,0xc67a],metadata_extension=[0xdfce,0xdfcf]),physical_resources=dict(existing_pages=44,new_pages=0,capacity=45056,payload_bytes=44472,spare_bytes=584),runtime_fit=dict(RAM3_bytes=8159,metadata_bytes=6095,metadata_end=0xdfcf,preclock_spare=1,clock_untouched=[0xdfd0,0xdfd3]),original_reader_closure=dict(source_instruction_boundaries=2485,direct_766_800=[],conservative_indexed_766_800=overlaps,finite_HP_death_X=[0,1],finite_defender_Y=[0,14],source_unreachable_guard_ledger=prior['original_reader_closure']['source_unreachable_ledger'],packet_direct_and_all256_index_aliases=[],indirect=prior['original_reader_closure']['indirect_sites'],indirect_domain=prior['original_reader_closure']['script_reader'],one_metadata_byte='DFCE is final immutable ColorsPacket value20; exact Y0..5 copy loop reads the fixed six-byte native palette command and writes only native VRAM buffer. Original actor readers cannot reach this metadata tail.'),gateway_packet=dict(bytes=13,roles='SavedR0..7 then allfive original transportSMC bytes',lifetime='Synchronous foreground-only NativeCall; actual traces reject NativeCall reentry and any source Draw/native MetaspriteRenderLoop until return. Source original graph has zero direct/indexed packet alias and immutable script/15command indirect closure. IRQ, actual FF lag NMI and IRQ inside lag audio preserve all private bytes including packet. Next authentic Draw overwrites every consumed packet byte before synchronous native renderer.'),cold_lifetime=dict(prefix_PC=[0xc65f,0xc67a],copy_readback=[0xc766,0xc800],bytes=154,conditions=['Uninitialized before original actor constructor','Both headers invalid','SEI','Forcedblank','NMI disabled'],actual_prefix_instruction_PC=11,all_source_live_bytes_equal_genuine_Fresh=True,source_C700_zero=[0xc700,0xc766],fail_closed_corruptions=5,rejected_guards=9,shared_manager_not_part_of_isolated_typed_worker_proof=True),transport_tag=dict(physical_operand=0x179,new_scratch_bytes=0,selector_growth=0,contract=tags['lifetime'],published_rows=37,stage_reads=tags['counts']['tag_consumed_before_native_rewrite'],bad_header_bytes=32),native_hook=dict(first_displaced_STA_exact=True,no_request_ABI_exact_cases=foreign['no_queued_request_AXYP_SP_exact_cases'],queued_owner_tail_cases=foreign['queued_owned_tail_to_genuine_Kill_cases'],source_pad_reader_closure=foreign['indirect_consumer_closure'],A_bank='Actual NrObjectWeaponTail runs in PRG124; its AD72 FarCallCommon restores the caller A-bank124 before AD75. Exact same bank source padding implements the hook. First STA restores original saved resultA before any classification. Owned queuedC1 tail-jumps genuine fixed KillPlayer97D6 only after all residentowner frames have returned.',epoch_order='Original source fatal death reaches85→185 at epoch20, queues2 inside movement. Actual later public row34 in that same GameCore epoch consumes2→1 and returnsC1. Native Kill occurs only after the full shared transport returns; first draw/collision follow native initializer normally. Native pit already-engine11 requests returnC0 and do not duplicate native Kill.'),interrupt_proof=dict(real_IRQ=1846,actual_FF_lag_NMI=1846,lag_branch_PC=hot['actual_lag_branch_PC'],regular_branch_forbidden_PC=hot['forbidden_regular_NMI_branch_PC'],minimum_ISR_SP=hot['minimum_SP'],nested_lag_IRQ_cases=nested['counts']['nested_IRQ'],minimum_nested_SP=nested['minimum_nested_IRQ_SP'],precise_async_audio_exception=hot['native_audio_counter']),supersedes_previous_lag_wording=hot['supersedes_lag_wording'],remaining=['Root exact lifetime/hook grant; no shared writes authorized by this receipt.','Current9cf and joint38+39 gate rebase, BBcookie and actual Ex37 successfulcold carry fix coordinated with DK; no v65-only/current image claim.','Complete current-image shared cold/auth/retire/respawn, native gameplay and1-1 traversal.','Original audio event production preserved as typed C0AD/AE/AF latches; eventual native music/SFX mapping remains incomplete.'],bindings={p.relative_to(R).as_posix():sha(p)for p in files})
 (O/'post-return-lifetime-proposal-v91.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','resource_granted','requested_existing_exclusive_RAM2_half_open','physical_resources','runtime_fit','interrupt_proof']}))


if __name__=='__main__':main()
