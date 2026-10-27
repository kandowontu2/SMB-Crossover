"""Freeze compact final Cheats source evidence in the one existing v8 tree.
No capture, native launch, source clone, installation or user-data restoration.
"""
from pathlib import Path
import ast,difflib,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
D=Path(r'C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/current3b-cheats-four-draft-v8')
S=D/'source';F=D/'source-freeze-v1';assert not F.exists();F.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):p.write_text(json.dumps(v,indent=2)+'\n',newline='\n')
def bind(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
oldmanifest=json.loads((D/'source-manifest.json').read_text());base=dict(oldmanifest);base.pop('src/cheats_four.s',None)
for row in json.loads((D/'changes.json').read_text()):base[row['path']]=row['old']
assert len(base)==869
eol=json.loads((D/'baseline-source-eol-alias.json').read_text());assert eol['LF_normalized_content_exact']
base['smb1base-mmc5-expanded.cfg']=eol['ROOT_raw_sha256']
for n,h in base.items():assert sha(ROOT/n)==h,('current production input differs',n)
current={str(p.relative_to(S)).replace('\\','/'):sha(p)for p in S.rglob('*')if p.is_file()}
assert len(current)==870 and set(current)==set(base)|{'src/cheats_four.s'}
changed=sorted(n for n,h in current.items()if base.get(n)!=h)
assert changed==sorted(['src/cheats.s','src/guest_injury.s','src/guest_source_stomp.s','src/common.s','src/mmc5.s','src/vic_adapter.s','smb1base-mmc5-expanded.cfg','src/entrypoint.s','src/cheats_four.s']),changed
patch=[];sources=[]
for n in changed:
 before=(ROOT/n).read_bytes()if n in base else b'';after=(S/n).read_bytes()
 if before:
  assert (b'\r\n'in before)==(b'\r\n'in after),('unrelated EOL change',n)
 patch.extend(difflib.unified_diff(before.decode().replace('\r\n','\n').splitlines(True),after.decode().replace('\r\n','\n').splitlines(True),fromfile='a/'+n if before else '/dev/null',tofile='b/'+n))
 sources.append(dict(path=n,original_sha256=base.get(n),candidate_sha256=current[n],candidate_bytes=len(after),source_path=str(S/n),original_CRLF=bool(b'\r\n'in before),candidate_CRLF=bool(b'\r\n'in after)))
assert (S/'src/cheats_four.s').read_bytes()==(ROOT/'tools/audit/cheats_four_cold_draft_v1.s').read_bytes()
put(F/'baseline-source-manifest.json',base);put(F/'source-manifest.json',current);put(D/'source-manifest.json',current)
(F/'implementation.patch').write_text(''.join(patch),newline='\n')
put(F/'changed-sources.json',dict(passed=True,changed_files=sources,all_other861_input_files_raw_exact=True,original_EOL_preserved=True,patch_line_ending='Unified diff LF-normalized for review; raw source hashes and originals determine exact deployment EOL.'))
rom=D/'candidate.nes';baseline=ROOT/'build/smb-crossover-mmc5-expanded.nes'
assert sha(rom)=='1a20a086e049f3173c1cbc6c8a227d27516245b8671e8c966487df6ef23a5e90'
assert sha(baseline)=='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
b=scoped_load(rom);raw=b['raw'];old=baseline.read_bytes();mirror=json.loads(rom.with_suffix('.cv3-mirror.json').read_text())
assert mirror['ROM_sha256']==sha(rom)
overlays=mirror['declared_overlay_offsets'];fixed=raw[16+127*8192:16+128*8192];clone=raw[16+125*8192:16+126*8192]
for i,(x,y)in enumerate(zip(fixed,clone)):assert x==y or any(lo<=i<hi for lo,hi in overlays)
for lo,hi in overlays:assert clone[lo:hi]==old[16+125*8192+lo:16+125*8192+hi]
seg=next(z for z in b['segs'].values()if z['name']=='"CHEATS_FOUR"')
assert int(seg['start'],0)==0xa000 and int(seg['size'],0)<=0x1800 and (int(seg['ooffs'],0)-16)//8192==63
assert raw[:16]==old[:16]and raw[16+128*8192:]==old[16+128*8192:]
put(F/'layout.json',dict(passed=True,cold_bank=dict(decimal=63,hex='$3F',CPU_start=0xa000,bytes=int(seg['size'],0),reserved_end_exclusive=0xb800),other_worker_reservation=dict(bank=63,CPU_start=0xbf00,CPU_end_exclusive=0xc000),persistent_flags=dict(symbol='CheatInvincible',address=address(b,'CheatInvincible'),bits=dict(invincible=1,air_jump=2,wrap=4,timer=8,full_power=16),new_bytes=0),genuine_moved_policy=dict(name='GuestWaterStompPolicy',oldPC=0xe054,newPC=address(b,'GuestWaterStompPolicy'),physical_bank=126),injury_helper=dict(PC=address(b,'CheatsInjuryMask'),bytes=9,physical_bank=126),current_fixed_127_regenerated_into125=True,declared_clone_sample_and_manager_spans_unchanged=overlays,all_other_clone_bytes_match_final127=True,header_CHR_exact=True))
receipts=[D/'baseline-alias-v1.json',D/'baseline-source-eol-alias.json',D/'candidate.build.json',D/'candidate.cv3-mirror.json']
for name in['cpu-final-1a20-owner-v1','cpu-final-1a20-wrapper-v1','cpu-final-1a20-abi-v1','cpu-final-1a20-extra-v3','cpu-final-1a20-interrupt-v2']:
 q=D/name/'proof.json';j=json.loads(q.read_text());assert j['passed']and j['ROM']==sha(rom);receipts.extend(sorted(q.parent.glob('*.json')))
mm5=json.loads((D/'ordinary-mmc5-build.json').read_text());mm3=json.loads((D/'ordinary-control.build.json').read_text())
assert mm5['receipt']['sha256']=='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833'
assert mm3['sha256']=='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'
assert sha(D/'ordinary-control.nes')==mm3['sha256']
put(F/'ordinary-builds.json',dict(passed=True,final_same_source_MMC3=mm3,final_same_source_MMC5=mm5,scope='Expanded flag off; one output path reused sequentially to avoid binary/debug duplication.'))
cases=json.loads((D/'cpu-final-1a20-owner-v1/full-power-smoke.json').read_text())['cases']
put(F/'costs.json',dict(source_CPU_only=True,default_off_actual_wrapper_cases=222,default_off_added_cycles_each=4,injury_predicate_added_cycles=5,Vic_unprotected_terrain_path_added_cycles=2,Vic_protected_path_saved_cycles=1,full_power_helper_cases=cases,maximum_first_full_power_cycles=max(z['cycles'][0]for z in cases),maximum_measured_second_helper_cycles=max(z['cycles'][1]for z in cases),limits='Helper costs exclude outer farcall/main/render scheduling. Material first-use purchase cost, especially ships, is disclosed. No native lag/cadence or all-cheats-enabled timing qualification.'))
negatives=[D/'cpu-final-page-owner-extra-v1/failure.json',D/'cpu-final-page-owner-extra-v2/failure.json',D/'ryu-refill-branch-draft-negative.json',D/'cpu-final-interrupt-v1/failure.json',D/'before-paint-guard.json',D/'before-paint-guard.patch',D/'before-default-carried-upgrades.json',D/'before-default-carried-upgrades.patch',D/'before-self-contained-page.json',D/'before-self-contained-page.patch',D/'before-ryu-steady-refill.json',D/'before-ryu-steady-refill.patch',D/'ryu-refill-branch-draft-correction.patch']
receipts+=negatives+[D/'ordinary-mmc5-build.json']
tools=['cheats_four_baseline_alias_v1.py','cheats_four_cpu_v2.py','cheats_four_wrapper_cpu_v2.py','cheats_four_abi_cpu_v1.py','cheats_four_owner_page_cpu_v1.py','cheats_four_owner_page_cpu_v2.py','cheats_four_owner_page_cpu_v3.py','cheats_four_interrupt_cpu_v1.py','cheats_four_interrupt_cpu_v2.py','cheats_four_source_freeze_v1.py']
pending=[ROOT/'tools/audit'/n for n in tools];seen=set();dependencies=[]
while pending:
 p=pending.pop()
 if p in seen:continue
 seen.add(p);dependencies.append(p)
 tree=ast.parse(p.read_text(encoding='utf-8-sig'))
 for node in ast.walk(tree):
  names=[node.module]if isinstance(node,ast.ImportFrom)and node.module else[n.name for n in node.names]if isinstance(node,ast.Import)else[]
  for n in names:
   for q in[ROOT/'tools/audit'/(n.replace('.','/')+'.py'),ROOT/'tools'/(n.replace('.','/')+'.py')]:
    if q.is_file()and q not in seen:pending.append(q)
receipts+=[F/n for n in['baseline-source-manifest.json','source-manifest.json','implementation.patch','changed-sources.json','layout.json','ordinary-builds.json','costs.json']]
bindings=[bind(p)for p in sorted(set(receipts+dependencies+[rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),ROOT/'tools/audit/cheats_four_cold_draft_v1.s',ROOT/'tools/build_mmc5_expanded.py',ROOT/'tools/prepare_cv3_dmc_mirror.py']))]
put(F/'readiness.json',dict(passed=True,source_ready_for_parent_composition=True,native_ready=False,adopted=False,ROM_sha256=sha(rom),baseline_ROM_sha256=sha(baseline),candidate_source_files=870,base_source_files=869,changed_deployable_files=9,bindings=bindings,limits=['SOURCE CPU controls only; no native PPU/DMA/audio/cadence/playthrough qualification.','Parent character_select composition must preserve Options CHEATS focus2 on B return and allow new fourth AUDIO TEST row; standalone old ScreenPalette clears focus.','Menu direct PPU writes require existing forced-blank/NmiDisable caller contract; full parent composition needs later bounded render check.','Physical actor initialization/life/area behavior and active DMC fetch/clone/IRQ are not fully native qualified.','No captures, native workers, runtime copies, new source clones, deleted-tree restoration, ROOT production/default/settings/Git changes.'],retained_original_failures=['Missing removed baseline debug path before game assertions; new verified exact ROOT alias.','Extra owner v1 wrongly expected active selection invariant; native InventoryGrant legitimately auto-equips a compatible new item.','Extra owner v2 exposed genuine Ryu50-then99 repeated HUD dirty writes; repaired and qualified.','First Ryu repair draft CPX/Z bug changed zero-max behavior; explicit actual-CPU failure retained and corrected.','Interrupt v1 incorrectly expected physical C mapping to match committed shadow during IRQ; v2 retains IRQ hardware and separately proves NMI shadow restore.']))
print(json.dumps(dict(passed=True,ROM=sha(rom),source_files=len(current),changed=changed,bindings=len(bindings),readiness=str(F/'readiness.json'),sha256=sha(F/'readiness.json'))))
if __name__=='__main__':pass
