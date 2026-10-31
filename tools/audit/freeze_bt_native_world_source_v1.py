"""Freeze qualified BT own/menu +223B cold rows +native world32; pending."""
from pathlib import Path
import difflib,hashlib,json,re,shutil,zipfile
R=Path(__file__).resolve().parents[2];P=R/'build/bt-current-cf-component-v2';O=R/'build/bt-native-world-source-v2';J=O/'joint';D=R/'docs/qa/checkpoints/2026-10-31/bt-current-cold-world-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

def main():
 assert not(O/'handoff.json').exists()and not D.exists();files={Path(__file__)}
 initial=[P/'handoff.json',O/'source-stage.json',R/'build/bt-jmp-row-cold-source-v1/source-stage.json',R/'build/bt-jmp-row-cold-proposal-v1/proposal.json',R/'docs/qa/checkpoints/2026-10-31/battletoads-jmp-router-resources/root-review.json']
 for p in initial:
  q=json.loads(p.read_text());files.add(p)
  for f,h in q['bindings'].items():assert sha(f)==h,('immutable source input',f);files.add(Path(f))
 stage=json.loads((O/'source-stage.json').read_text());assert stage['candidate']==sha(J/'candidate.nes')=='9b1089d254dfb18ceb5bb2bc14951f2b782aa40cf82fcde63b9cb07d82f456c6'
 checks={};receipts=[]
 for n in['bt-jmp-row-cold-controls-v3','bt-jmp-row-scene-controls-v1','bt-jmp-cold-retirement-controls-v3','bt-native-world-controls-v1','bt-native-world-isr-controls-v1','bt-pending-full-parser-controls-v3','bt-native-world-retirement-controls-v1','bt-native-world-foreign-v1','bt-native-world-bowser-v1','bt-native-world-menu-v1']:
  p=R/'build'/n/'controls.json';q=json.loads(p.read_text());assert q['passed'],p;checks[n]=q;files.add(p);receipts.append(dict(path=str(p),sha256=sha(p)))
  for f,h in q['bindings'].items():assert sha(f)==h,('exact control input',f);files.add(Path(f))
 for p in J.rglob('*'):
  if p.is_file()and p.suffix.lower()in['.s','.asm','.inc','.cfg','.chr','.rle','.dep','.d','.o','.bin']:files.add(p)
 for line in(J/'candidate.dbg').read_text().splitlines():
  if line.startswith('file\t'):
   p=Path(re.search(r'name="([^"]+)"',line).group(1));p=p if p.is_absolute()else R/p;assert p.is_file(),p;files.add(p)
 files|=set(O.glob('*.json'))|{J/n for n in['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','source-stage.json']}
 tools={Path(__file__)}|set((R/'tools/audit').glob('bt_jmp*.py'))|set((R/'tools/audit').glob('bt_native_world*.py'))|set((R/'tools/audit').glob('bt_pending_full_parser*.py'))|set((R/'tools/audit').glob('prepare_bt_jmp*.py'))|set((R/'tools/audit').glob('measure_bt_jmp*.py'))|set((R/'tools/audit').glob('prepare_bt_native_world*.py'))
 refs={R/'tools/reference/bt_jmp_row_cold_proposal_v1.s'};files|=tools|refs
 for base in[R/'build/bt-jmp-row-cold-source-v1',R/'build/bt-jmp-row-cold-proposal-v1',R/'build/bt-native-world-source-v1']:
  files|=set(base.glob('*.json'))
 patch=''
 for name in['bt/router.s','bt/api.s','bt/loader.s','bt/stream.s']:
  patch+=''.join(difflib.unified_diff((P/'joint'/name).read_text().splitlines(True),(J/name).read_text().splitlines(True),fromfile='8961/'+name,tofile='BT-cold-world/'+name))
 (O/'source.patch').write_text(patch,encoding='utf-8')
 transport=checks['bt-jmp-row-cold-controls-v3'];world=checks['bt-native-world-controls-v1'];parser=checks['bt-pending-full-parser-controls-v3'];retire=checks['bt-native-world-retirement-controls-v1'];foreign=checks['bt-native-world-foreign-v1']
 proof=dict(source=True,passed=True,candidate=stage['candidate'],parent_own_component='8961be0a5c51ca091efdddea07c122a0c7a8204e1eb071b2cd001bba4a7c9f8c',source_parent66=True,installed_current68_M3_separate=True,ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,admitted=False,
  router_emitted_allocated=[223,224],public_B020_B08C_B08E_fixed=True,all108_owner_target_witnesses=True,all_owner_rows_flags=9472,unchanged_callbacks=9216,cold_ROM17_26_actual_pairs=256,foreign_fullflag_rejects=113344,cookie_poison=1024,transport_real_vectors=1600,minimum_transport_ISR_SP=188,whole_BW_CF_native_scene_pairs=432,unready31_33_native_name_pairs=512,
  own_native_world_tail_bytes=18,own_native_world_tail_address='0xb53d',only_world_child_changed_bytes=31,new_BT_cookie=stage['BT_cookie'],new_BT_cache=stage['BT_cache'],native_QueueMegaManFacePalette_pairs=2048,unchanged_other_rows_allflags=2304,unready_corrupt32_rejects=1088,world_tail_real_vectors=116,
  actual_CF_to_BT_prewrite_retirement_pairs=16,actual_pending_menu_retire_before_Selected0=8,forbidden_context_BTload_rejects=4,direct_BtLoad_still_requires_explicit_CfRetire=True,
  full_native_parser_cohorts=4,real_pending_Start_blocks=4,explicit_frontend_Selected33_projection_only=True,fullparser_Main_NMI=128,source_guest_preload=False,source_physics_support_HP_preload=False,actual_parser_world32_calls=0,native_caller_world32_direct_proof_separate=True,
  ordinary_foreign_Main_pairs=foreign['cases'],ordinary_foreign_Main_CPU_delta=foreign['CPU_delta'],Bowser_natural_parser_Main=240,actual_menu_profiles=83,source_controls=receipts,
  remaining=['BT and CF remain pending; no natural-ready menu or native emulator/admission evidence','Future raw33 ready preview must use native-other path, not DK>=28 shortcut','Current installed68 M3/e54 source must be surgically grafted before any CF67 worker or publication','CF P1 experiment is separate on ef2f and not adopted','Direct exported loaders require explicit caller retirement; no blanket protection claim','BT names/HUD are still inherited pair/native text; campaign/audio/extras not claimed'])
 save(O/'freeze-proof.json',proof)
 api=dict(source=True,candidate=stage['candidate'],source_stage=str(J/'source-stage.json'),actual_link_recipe=str(O/'final-link.json'),actual_main_recipe=str(R/'build/bt-current-cf-component-v2/main-build.json'),actual_main_object=str(P/'joint/main.o'),actual_union_object=str(R/'build/cf-bt-shared-transport-v3/joint/union.o'),actual_object_count=85,
  resident_row=dict(address='0xb020',execution_raw_PRG_bank=215,physical_ROM_bank=87,rows=36,stride=3,instruction='JMP BtRouter',reject_address='0xb08c',router_address='0xb08e',bytes=223,allocated=224),
  incoming_contract='Genuine FarCallCommon target must remain B020+3*service until router captures targetLo before any nestedcall/SMC write. Direct arbitrary BtRouter entry is not an API. Original nativeAXYP is saved; no own rowJSR return exists. Existing outer worker/mapping frame is retained. Success restores nativeP/A/X/Y then SFC+3; rejection restores nativeAXY/P withCclear.',
  cold_policy={'3':'valid cache explicit decline/noOAM; invalid reject','15':'full valid BT->cached nativeCmFresh once+sourceCtor; invalid nativeCmFresh once','17':'always ROM72 BtColdPortrait B011,8parts,neverRAM3','18':'unready nativeFmQueueName; valid BT cachedecline, menu retirement makes cold-name path unready','19':'full valid BT->cached nativeJnReset once+source motion reset; invalid genuineJnReset once','26':'always ROM72 BtColdColors B091->BtAcquire AF7F->legal forcedblank BtLoad/Ensure','30':'explicit unavailable, native caller text retained','32':'full valid BT->cached A060->BtNativeWorldPalette B53D->genuine HuNativeWorldPalette; invalid rejects before guest'},
  true_exports={'BtCheck':dict(address='0xadc0',physical_ROM_bank=93,execution_raw_PRG_bank=221),'BtLoad':dict(address='0xae01',physical_ROM_bank=93,execution_raw_PRG_bank=221),'BtRetire':dict(address='0xaf41',physical_ROM_bank=93,execution_raw_PRG_bank=221),'BtAcquire':dict(address='0xaf7f',physical_ROM_bank=93,execution_raw_PRG_bank=221),'BtColdPortrait':dict(address='0xb011',physical_ROM_bank=72,execution_raw_PRG_bank=200),'BtColdColors':dict(address='0xb091',physical_ROM_bank=72,execution_raw_PRG_bank=200),'BtNativeWorldPalette':dict(address='0xb53d',execution_raw_PRG_bank=3,cache_image_offset=0x153d)},
  retirement='Actual InitScreen executes early CfSceneRetireForeign before entire S2/Qw/Ar/Fw scene chain. Its subsequent genuine SetupIntermediate calls GetPlayerColors/ROM26/Acquire; every A3 copy/constructor write observes C2invalid. Title/active/notbusy/normal color contexts cannot load. Direct exported BtLoad does not clear C2 and explicitly requires prior CfRetire.',BT_cookie=stage['BT_cookie'],BT_cache=stage['BT_cache'],remaining=proof['remaining'])
 save(O/'integration-api.json',api)
 (O/'HANDOFF.txt').write_text('''Frozen source9b1089d2: genuine BTv7 own/menu producer on38a6, qualified223/224B JMP-row cold transport, and18B own-cache native-world32 tail. Current source66 ready, BT/CFpending. Current installed68 M3/e54 is separate and must be surgically grafted next; never replace latest Main/common from old bundle. No P1 experiment or CF67 worker adopted.

All36 public row PCs B020+3Y, rejectB08C and workerB08E remain fixed. A rowJMP adds no private return frame; targetLo is captured before nestedcall/SMC mutation. Original SFCworker/oldbank frame remains; nativeP/A/X/Y restored before callback, Cclear-only reject. Genuine SFC target is a mandatory ingress contract; arbitrary direct BtRouter calls are unsupported. All9472 owner/row/flag outcomes,108 actual target witnesses,113344 foreign rejects,1024cookiepoisons and1600 realvectors pass.432 BW/CF full native scenes and512 unready-name native callers pass.

New cache row32 tails genuine HuNativeWorldPalette. It adds18B inside own8KB image; loader/carryingstream fingerprints regenerate from actual linked source. Only31 bytes beyond7247 change.2048 actual QueueMegaManFacePalette area/background/fullflag pairs,2304 unchanged-other-row pairs,1088 unready/corrupt rejections,116 real tailvectors pass. The four actual cold parsers never naturally call32; direct native-caller proof is separate, not an inferred after-load ordering claim.

Sixteen actual CF->BT scene/SetupIntermediate transitions prove CF C2valid clears before every new A3 write; title/active/notbusy/normal calls reject load. Direct exported BtLoad STILL requires explicit prior CfRetire; a stale-cookie direct misuse witness is retained. Four complete native parser cohorts plus128Main/NMI pass, AFTER proving pending Start blocks then projecting only futurefrontendSelected33 into the real ready continuation. No valid guest image/cookie/Ready/support/HP preloaded. This is not natural-ready admission.

Final actual282 legacyMain pairs preserve complete application/OAM/CHR/maps and0CPUdelta;83menus and240natural Bowser Main pass. Current Main producer is bt-current-cf-component-v2/main-build.json; real46group union object remains cf-bt-shared-transport-v3/joint/union.o. Final linker consumes85 distinct objects. Builderguards every actual compiler/link output. One retained negative caught ancestor-bound stream/cookie incbins; corrected source explicitly rebinds them before regeneration. All old checkpoints, installed ROM and native evidence unchanged.
''',encoding='utf-8')
 files|={O/'source.patch',O/'freeze-proof.json',O/'integration-api.json',O/'HANDOFF.txt'}
 archive=O/'source-only.zip';members=[];ext={'.s','.asm','.inc','.cfg','.chr','.rle','.dep','.d','.py','.json','.txt','.patch','.md','.lua'}
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(files):
   if p.suffix.lower()in ext or p.suffix.lower()=='.bin'and p.stat().st_size<=65536:
    rel=p.relative_to(R).as_posix();z.write(p,rel);members.append(rel)
 files.add(archive);q=dict(source=True,status='FROZEN_PENDING_BT_COLD_WORLD_SOURCE',candidate=stage['candidate'],parent=stage['parent'],joint=str(J),source_stage=str(J/'source-stage.json'),ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,publication_allowed=False,source_archive_members=len(members),bindings={str(p.resolve()):sha(p)for p in sorted(files)})
 save(O/'handoff.json',q)
 for f,h in q['bindings'].items():assert sha(f)==h,('postfreeze',f)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for n in z.namelist():assert hashlib.sha256(z.read(n)).hexdigest()==sha(R/n),n
 D.mkdir(parents=True)
 for n in['handoff.json','source-only.zip','source.patch','freeze-proof.json','integration-api.json','HANDOFF.txt']:shutil.copyfile(O/n,D/n)
 for row in receipts:
  p=Path(row['path']);c=json.loads(p.read_text());compact={k:v for k,v in c.items()if k not in['cohorts','checks','rows','vectors','bindings','scene','name','paths','menu','cold','menus']};compact.update(full_receipt=str(p),sha256=sha(p));save(D/(p.parent.name+'.json'),compact)
 save(D/'receipt.json',dict(source=True,candidate=stage['candidate'],handoff=sha(O/'handoff.json'),verified_bindings=len(files),archive_members=len(members),bindings={str(p.resolve()):sha(p)for p in D.iterdir()}))
 owned=tools|refs|set(D.iterdir())|{D/'owned-files.txt'};(D/'owned-files.txt').write_text('\n'.join(p.relative_to(R).as_posix()for p in sorted(owned))+'\n')
 print(json.dumps(dict(candidate=stage['candidate'],handoff=sha(O/'handoff.json'),bindings=len(files),archive_members=len(members),checkpoint=str(D),owned_files=str(D/'owned-files.txt'))))
if __name__=='__main__':main()
