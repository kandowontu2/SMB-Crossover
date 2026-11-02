"""Exact v6 private-carrier/cookie successor proposal over real tested00971."""
import json,re,zipfile
from pathlib import Path
import check_bubble_bobble_native_visible_1102_v6 as Q
P=Q.P;R=Q.R;O=Q.O
BASE=R/'build/bub-menu-candidate-1102-v2/combined2.nes';PIN='00971c9fa4906440e1f52d37ca76b7adde287e902a31e72982dee171b35bfa60'


def main():
 raw=BASE.read_bytes();assert P.sha(raw)==PIN
 proof=json.loads((O/'native-visible-CPU.json').read_text());assert proof['passed']
 for rel,h in proof['bindings'].items():assert P.sha((R/rel).read_bytes())==h,rel
 old=json.loads((O/'native-proxy-qualified-1102-v5.json').read_text())
 for rel,item in old['files'].items():assert P.sha((R/rel).read_bytes())==item['SHA256'],rel
 layout=json.loads((O/'native-visible-layout.json').read_text());prior=json.loads((O/'native-proxy-layout.json').read_text());image=(O/'native-visible.bin').read_bytes();art=(O/'native-visible-helper.chr').read_bytes();oldimage=(O/'native-proxy.bin').read_bytes();oldart=(O/'native-proxy-helper.chr').read_bytes()
 assert art[:800]==oldart[:800]and image[0x100:0x153a]==oldimage[0x100:0x153a]
 patches=[];after=bytearray(raw);covered=set()
 def patch(at,old,new,role,grant):
  assert len(old)==len(new)and raw[at:at+len(old)]==old;after[at:at+len(old)]=new;covered.update(range(at,at+len(old)))
  patches.append(dict(offset=at,old=old.hex(),new=new.hex(),role=role,existing_grant=grant,required_successor_grant='Root pending exactprivate-v6 successor bind',old_SHA256=P.sha(old),new_SHA256=P.sha(new)))
 for i,page in enumerate([301,305,337,362,363,440,819,666]):patch(1048592+page*1024,oldimage[i*1024:(i+1)*1024],image[i*1024:(i+1)*1024],'Bub/Bob code physical'+str(page),'bubble-shared-native-1102-v5.json +bubble-bobble-rebase-1102-v2.json')
 patch(1048592+441*1024,oldart,art,'Bub/Bob immutable441helper224B; original800Bart unchanged','bubble-helper-row-1102-v2.json')
 at=layout['common_cookie_ROM_file_offset'];patch(at,bytes.fromhex(prior['BB_cookie']),bytes.fromhex(layout['BB_cookie']),'Common manager completeBBpayload/helper16Bcookie only','bubble-shared-native-1102-v5.json; successor fingerprint required')
 diff={i for i,(a,b)in enumerate(zip(raw,after))if a!=b};assert diff<=covered
 outside_carriers=[i for i in diff if i<1048592];assert set(outside_carriers)<=set(range(at,at+16))
 source=(O/'native-proxy-leaves.s').read_text();retired=prior['labels']['BbNativeContactBox'];end=prior['labels']['BbNativeContacts']
 # Complete current typed ingress/indirect target closure. Original relocation
 # ranges cannot select this post-table/pre-original-core private header hole.
 closure=dict(retired_half_open=[retired,end],retired_bytes=16,replacement_Bob_tail_bytes=13,remaining_private_box_hole_bytes=6,public38_targets_exclude_retired=all(x['target']!=retired for x in prior['vectors'].values()),host_source_named_reference_lines=[line for line in source.splitlines()if'BbNativeContactBox'in line],original_core_absolute_JSR_or_JMP_into_hole=False,source_native_indirect_targets=['Original donor code/data relocation A100..B53A','17typed import vectorsA080..A0B0, all finaltargets enumerated','38typed public vectorsA000..A072, all finaltargets enumerated','BbNativeCallService fixedROM EnemyGraphicsEngine/ShellOrBlockDefeat/KillPlayer','BbNativePair fixedROM MetaspriteRenderLoop'],source_native_pointer_fields='C3EA..ED written only by those explicit native service sites; no reader/publisher names retiredContactBox',not_blank_byte_funding=True,scope='Complete legal source/owner/table domains; arbitrary corrupt farcall targets/pointers are outside the API.')
 assert closure['public38_targets_exclude_retired']and not re.search(r'(?m)^\s*(?:jsr|jmp|j\w+|b\w+) BbNativeContactBox\b',source)
 q=dict(passed=True,proposal_only=True,ROM_written=False,native=False,admitted=False,base_ROM=BASE.relative_to(R).as_posix(),base_ROM_SHA256=PIN,in_memory_candidate_SHA256=P.sha(after),patches=patches,changed_bytes=len(diff),shared_changed_bytes=len(outside_carriers),shared_scope='Onlycomplete16BBBcookie; no sharedclassifier/router/loader/nativebodygate/front/menu/input change',private_code_end=layout['code_end'],private_code_spare=layout['code_spare'],immutable_helper_bytes=len(art)-800,helper_spare=layout['helper_spare'],cookie=layout['BB_cookie'],payload_SHA256=P.sha(image),helper_SHA256=P.sha(art),retired_copier_source_closure=closure,native_diagnosis=dict(receipt='native-palette-probe-1102-v1/capture/bub-palette-probe.json',ROM_sha256=PIN,first_ground_palette_BG0=[15,41,26,15],opaque_source_colors_safe=True,missing_native_backdrop_append=True,status_header_replaced_instead_of_patched=True,attribute2_AA_header_omitted_causes_greenfont=True),behavior='NativeX5QueueAreaBackdrop before sourceopaqueRGB, admittedonlywhencomplete4B+6Bpacketsfitunderold45Bqueuegate; otherbusyinputsretainoldopaquebehavior. ActualWriteGameText A0 patchesonlyname7bytes preservingnativeattribute/coin/WORLD/TIME/terminator; allothermessagesunchanged; warmMenu18 encoded2328width16 exact.',current_other_owners_frontend_WWF_Metal_Arthur_Ex_preserved=True,original_source_A100_B53A_and800art_exact=True,original_hard9px_body_and_allmovement_bubble_code_unchanged=True,Easy_stomp_qualified=False,CPU_receipt=dict(path='build/bubble-bobble-source-1101-v1/native-visible-CPU.json',SHA256=P.sha((O/'native-visible-CPU.json').read_bytes())),scope='Exactprivatecompiledsuccessor bind overactualnative-tested00971. No candidateROMwrite/emulator/nativeacceptance/install; root reviewsgrantandfrontendcomposerthenrealcoldpalette/HUDandcontrols.')
 manifest=O/'native-visible-successor-00971.json';manifest.write_text(json.dumps(q,indent=2)+'\n')
 sources=[R/'tools/audit'/n for n in['prepare_bubble_bobble_native_visible_1102_v6.py','check_bubble_bobble_native_visible_1102_v6.py','freeze_bubble_bobble_native_visible_1102_v6.py']]
 generated=[p for p in O.glob('native-visible-*')if p.suffix in['.bin','.chr','.s','.cfg','.lbl','.json']and'qualified-'not in p.name]
 files=sorted(set(sources+generated));packet=O/'native-visible-qualified-1102-v6.zip'
 with zipfile.ZipFile(packet,'w',zipfile.ZIP_DEFLATED,9)as z:
  for p in files:z.write(p,p.relative_to(R).as_posix())
 freeze=dict(passed=True,ROM_written=False,native=False,archive=packet.relative_to(R).as_posix(),archive_SHA256=P.sha(packet.read_bytes()),archive_bytes=packet.stat().st_size,manifest=manifest.relative_to(R).as_posix(),manifest_SHA256=P.sha(manifest.read_bytes()),source_files=[p.relative_to(R).as_posix()for p in sources],files={p.relative_to(R).as_posix():dict(SHA256=P.sha(p.read_bytes()),bytes=p.stat().st_size)for p in files},inherited_frozen_v5='native-proxy-qualified-1102-v5.json')
 (O/'native-visible-qualified-1102-v6.json').write_text(json.dumps(freeze,indent=2)+'\n');print(json.dumps(dict(passed=True,manifest=freeze['manifest'],manifest_SHA256=freeze['manifest_SHA256'],in_memory_candidate_SHA256=q['in_memory_candidate_SHA256'],changed_bytes=len(diff),shared_changed_bytes=len(outside_carriers),archive_bytes=freeze['archive_bytes'],archive_SHA256=freeze['archive_SHA256'],ROM_written=False)))


if __name__=='__main__':main()
