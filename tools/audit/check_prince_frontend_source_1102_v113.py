"""Assembled frontend source and exact current physical consumer bindings."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_prince_current_cold_1102_v98 as C
O=C.O


def main():
 b,manifest=C.image();q=json.loads((O/'frontend-proposal-v109.json').read_text());assert q['passed'] and q['parent_memory_SHA256']==manifest['expected_memory_only_SHA256']
 for p,d in q['bindings'].items():assert C.M.sha((R/p).read_bytes())==d,p
 raw=bytearray(b['raw']);changed=set()
 for row in q['patches']:
  at=row['file_offset'];before=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex']);assert len(before)==len(after)and raw[at:at+len(before)]==before
  assert not changed.intersection(range(at,at+len(before)));changed.update(range(at,at+len(before)));raw[at:at+len(after)]=after
 assert C.M.sha(raw)==q['expected_memory_only_SHA256']
 source=R/'tools/reference/prince_frontend_1102_v109.inc'
 prefix='.setcpu "6502"\nSelectedCharacter=$6002\nFmAlts=$5fe5\nFmGroups=$5fe8\nExMenuDone=$b0fb\nFmCfRestoreP1=$b599\n'+source.read_text()+'\n.segment "CODE"\n'
 parts=[]
 for name,start,size,macro,physical in [('resolver',0xb077,21,'PrinceFrontendResolver',65),('masks',0xb5e6,74,'PrinceFrontendStartMasks',29)]:
  cfg=f'MEMORY{{M:start=${start:04x},size={size},file=%O;}}SEGMENTS{{CODE:load=M,type=ro;}}'
  code=prefix+macro+'\n.assert *=$'+f'{start+size:04x}'+',lderror,"Existing exact footprint"\n'
  blob,lab=C.M.A.assemble('frontend-'+name+'-v113',code,cfg);at=16+physical*8192+start-0xa000
  assert len(blob)==size and bytes(raw[at:at+size])==blob
  parts.append(dict(name=name,physical_PRG=physical,CPU_half_open=[start,start+size],bytes=size,original_SHA256=C.M.sha(b['raw'][at:at+size]),successor_SHA256=C.M.sha(blob),exact_assembled_source=True))
 assert q['resolver_entry_X29_iff_menuindex29'] and q['actual_resolver_nonindex_X']==[[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[0,7],[27,255]]
 caller=[]
 for name in ['CmHostResolveCharacter','FmResolve','FmQueueName','FmStartRetireFlags']:
  at=C.I.location(b,name);size=int(b['syms'][name].get('size','1'),0);caller.append(dict(name=name,physical_PRG=(at-16)//8192,CPU=C.I.address(b,name),bytes=size,preimage_SHA256=C.M.sha(b['raw'][at:at+size])))
 out=dict(passed=True,proposal_only=True,ROM_written=False,menu_admitted=False,parent_memory_SHA256=q['parent_memory_SHA256'],expected_memory_only_SHA256=q['expected_memory_only_SHA256'],assembled_parts=parts,caller_symbols=caller,actual_consumer_closure=dict(public_ExMenuResolve=[65,0xa7fa,0xa800],same_21B_internal_ExMenuBody=[65,0xb077,0xb08c],same_existing_return=[65,0xb0fb,0xb100],public_published_gameplay_rows='65:B08C..B0FB unchanged; no row or target added.',native_X_lifetime='CmHostResolveCharacter loads X=menuindex before NrMenuCharacter; current124:A0A6 slot resolver preservesX. Mario0 fallback loads MarioVariant0..7. The Sh/UI path can also returnFF for DK27. Actual852 complete legal-menu ingresses prove X29 iff slot29 across all93profiles/94states and Select+confirm. This does not assert X always equals menuindex or permit arbitrary direct internal-leaf ingress.',Start_Y_domain='Table search8..0; explicit fallback9. Alts0..9 andGroups0..9 are finite immutable rows; no unknown read past the same74B procedure. Both finalEA bytes become declared table data.',preserved_downstream_addresses=True,marker='Actual QueueSelection reaches FmQueueName Copy $BBCF and indirect name address$BE7E; only that Prince glyph3F becomes24, all15othercells and FmPendingC1/A25 portrait route identical.'),actual_counts=dict(unique_profiles=q['unique_named_profiles'],machine_states=q['actual_named_states'],foreign_machine_states=q['foreign_machine_states'],foreign_Start_A_pairs=q['foreign_Start_A_pairs'],Select_confirm=q['actual_Select_confirm_cases'],all32slots_256alts_masks=q['all256_FmAlts_all32_Start_mask_cases']),bindings={p.relative_to(R).as_posix():C.M.sha(p.read_bytes())for p in [Path(__file__),source,O/'frontend-proposal-v109.json',O/'post-return-manifest-v97.json',R/'tools/reference/excitebike_menu_1101_v1.inc',R/'tools/reference/shinobi_menu_1101_v13.inc',R/'src/celeste_mario_host.s',R/'src/full_roster_menu.s',R/'tools/audit/prepare_battletoads_menu_lease_v7.py',R/'tools/audit/prepare_mr_gimmick_family_1102_v18.py']})
 (O/'frontend-source-CPU-v113.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k not in ['bindings','caller_symbols','actual_consumer_closure']}))


if __name__=='__main__':main()
