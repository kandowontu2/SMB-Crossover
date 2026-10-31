"""Freeze actual source owner-boundary hooks; CF/BT stay pending."""
from pathlib import Path
import difflib,hashlib,json,re,shutil,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/cf-bt-shared-transport-v3';O=R/'build/cf-owner-retirement-v2';J=O/'joint'
D=R/'docs/qa/checkpoints/2026-10-31/cf-owner-retirement-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
def main():
 assert not(O/'handoff.json').exists()and not D.exists()
 files={Path(__file__)};verified=0
 manifests=[P/'handoff.json',R/'build/contra-force-retire-qualified-v1/handoff.json',R/'build/contra-force-checkpoint-loader-qualified-v1/handoff.json',O/'source-stage.json']
 for p in manifests:
  q=json.loads(p.read_text());files.add(p)
  for f,h in q['bindings'].items():assert sha(f)==h,('immutable input',f);files.add(Path(f));verified+=1
 stage=json.loads((O/'source-stage.json').read_text());assert stage['candidate']==sha(J/'candidate.nes')=='f5231061660c6b898554a86c429db8357bd80da71b8aa38525b09636a6eb8e5e'
 receipts=[]
 names=['cf-owner-retirement-coverage-v2','cf-owner-retirement-hook-abi-v2','cf-owner-retirement-foreign-main-v1','cf-owner-retirement-menu-controls-v1','cf-owner-retirement-bowser-cold-v1','cf-owner-retirement-source-closure-v2','contra-force-owner-retirement-rebind-v1']
 checks={}
 for n in names:
  p=R/'build'/n/'controls.json';q=json.loads(p.read_text());assert q['passed'],p
  checks[n]=q;files.add(p);receipts.append(dict(path=str(p),sha256=sha(p)))
  for f,h in q['bindings'].items():assert sha(f)==h,('exact control input',f);files.add(Path(f))
 for p in J.rglob('*'):
  if p.is_file()and p.suffix.lower()in['.s','.asm','.inc','.cfg','.chr','.rle','.dep','.d','.o','.bin']:files.add(p)
 for line in(J/'candidate.dbg').read_text().splitlines():
  if line.startswith('file\t'):
   p=Path(re.search(r'name="([^"]+)"',line).group(1));p=p if p.is_absolute()else R/p
   assert p.is_file(),p;files.add(p)
 files|=set(O.glob('*.json'))|{J/n for n in['candidate.nes','candidate.dbg','candidate.lbl','candidate.map','source-stage.json']}
 own_tools=set((R/'tools/audit').glob('*cf_owner_retirement*.py'));files|=own_tools
 negatives=[]
 for root in[R/'build/cf-owner-retirement-v1',R/'build/cf-owner-retirement-coverage-v1',R/'build/cf-owner-retirement-source-closure-v1',R/'build/cf-owner-retirement-hook-abi-v1']:
  for p in root.glob('*.json'):
   try:q=json.loads(p.read_text())
   except ValueError:continue
   if isinstance(q,dict)and q.get('passed')is False:
    files.add(p);negatives.append(dict(path=str(p),sha256=sha(p),error=q.get('error','')))
 diagnostic=R/'build/cf-owner-retirement-scene-diagnostic-v1/controls.json';files.add(diagnostic)
 patch=[]
 for n in['src/character_select.s','bowser/cold.s','cf-loader.s','private.cfg']:
  patch.extend(difflib.unified_diff((P/'joint'/n).read_text().splitlines(True),(J/n).read_text().splitlines(True),fromfile='inert-a7da/'+n,tofile='owner-retirement/'+n))
 patch.extend(difflib.unified_diff([], (J/'cf-retire.s').read_text().splitlines(True),fromfile='/dev/null',tofile='owner-retirement/cf-retire.s'))
 (O/'source.patch').write_text(''.join(patch),encoding='utf-8')
 abi=checks['cf-owner-retirement-hook-abi-v2'];coverage=checks['cf-owner-retirement-coverage-v2'];closure=checks['cf-owner-retirement-source-closure-v2']
 proof=dict(source=True,passed=True,candidate=stage['candidate'],parent=stage['parent'],ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,
  menu_retire_before_Selected_publication=128,actual_scene_retire_before_every_installed_foreign_A3_writer=12,global_validity_clear_before_Selected_publication=4,direct_BT_explicit_caller_contract=4,
  actual_hook_allflag_pairs=abi['actual_allflag_hook_pairs'],real_new_hook_vectors=abi['real_vector_cases'],minimum_ISR_SP=abi['minimum_ISR_SP'],actual_foreign_Main=282,foreign_Main_CPU_delta=[0,0],menu_identities=83,Start_masks=10240,actual_Bowser_parser_Main=240,
  fullAXYP_SP_all33SMC_livepage1_maps_orderedapplication_exact=True,exact_new_ROM_envelopes=closure['exact_changed_envelopes'],changed_bytes=358,
  all_header_CHR_payload_cookie_images_preserved=True,original_menu34B=True,scene_first18B_and_owned_tail15B=True,BW_ROM_AUX_used_and_granted=204,
  preserved_current66_publicPCs=True,inherited_phase1_internal_labels=closure['already_frozen_phase1_internal_table_relocations'],new_loader_internal_relocations=closure['only_12_internal_CF_loader_diagnostic_labels_rebound_to_frozen60a5'],
  source_controls=receipts,old_stale_CF_guard_acceptance_reproduced=coverage['old_parent_negative'],
  missing=['CF natural cold/menu/lives/palette/nativeDrawAll/runtime/warm-player integration remains pending','Corrected BTv7 own cold/menu/lifecycle source is next dependency, not adopted here','Exported direct FW/BW/BT loader API calls require caller retirement; worker existence is not automatic global hook','Soundtest temporary Selected writes are not an admission/lifecycle claim'])
 save(O/'freeze-proof.json',proof)
 save(O/'retained-negatives.json',dict(negatives=negatives,
  extra_sprite_clear='V1 expected one MoveAllSpritesOffscreen. Unchanged a7da has two on an old FF palette-owned Bowser transition: original native clear, then FwMuxSceneA::Retire clearing prior FF parts before native P1 restoration. Bound parent/new diagnostic and v2 demand identical original call counts.',
  stale_object='Builderv1 compiled new cold.o but inherited final link consumed frozen c663 cold.o. Postlink missing new helper failed. V2 binds/replaces actual sole cold producer; no frozen output was overwritten.',
  symbol_scope='Closurev1 incorrectly treated already-frozen phase1 common internal/table labels as fixed public PCs. V2 checks no new current66 moves vs actual a7da; twelve CF loader internal diagnostic exports rebind exactly to frozen60a5.'))
 note='''Source-qualified CF owner-retirement foundation on exact a7da, ready66 unchanged.

Candidate f5231061660c6b898554a86c429db8357bd80da71b8aa38525b09636a6eb8e5e.
Adopts genuine frozen CfRetire36B (01a85af9) and internal-checkpoint449B
loader (60a5bd7c). Kernel/carrier/cookies and every current66 image remain.
No CF presentation/cold admission or new lease is included.

Existing MenuResolve34B calls CfRetire BEFORE the original Bw/Fw/S2/Qw/Ar/
Fm/Cm chain can publish Selected. Actual128 four-class/menu-slot cases pass.
Existing BwScene18B prefix retires BEFORE its S2/Qw/Ar/Fw child chain,
not after. Its original child is factored through existing15B A88 tail.
Both actual installed foreign A3 writers (FwLoad in FwSceneInit, BwLoad in
BwScene) execute after validity clear:12 full foreign copy transitions pass.
Global CrossoverInit already clears C2 in actual QwBoot before Selected:
four classes pass. BtLoad has no installed caller in this pending leaf;
four actual exported-API sequences explicitly call CfRetire before it.
Direct loader API users still own retirement as an explicit precondition.

Full hook flags/registers/application/ordered writes, real vector cuts,
33SMC/live page1/maps, sourceA and genuine SFC caller return are qualified.
Exact counts/minimum SP are in freeze-proof.json. Parent negative is real:
a7da could overwrite A3 with Bowser while leaving CF C2 A7, then wrongly
accept stale CF auth. New menu/scene transitions reject before firstA2.
The retained sprite-clear negative was a wrong test expectation; original
FF palette retirement legitimately performs the second clear. No product
assertion or original child callback was removed.

282 current Main pairs are exact, with0CPU delta for ordinary Main;83 menu
identities/10240 Start masks remain. Both Bowser forms pass native parser
and120Main each. Public menu/scene/body entries stay fixed;12 owned CF C78
internal diagnostic labels rebind to frozen60a5. Already reviewed a7da
internal common table shifts are inherited, not new edits. Only358ROMbytes
change inside five exact owned envelopes; header/CHR/payload/cookies exact.

CF and BT remain pending. Natural CF cold/presentation/runtime/warm health
and player transitions are not implemented here. Unconditional retirement
at the scene boundary is a safe pending-owner foundation, not a ready-CF
warm lifecycle policy. Corrected BTv7 source is the next cold-parser join.
Temporary soundtest Selected stores and arbitrary direct API users are not
covered by a blanket global claim. No native run/install/publication.

Actual build commands are main-build/cold-build/cf-loader-build/cf-retire-
build/final-link JSON under build/cf-owner-retirement-v2. Every output/dep/
cfg was guarded beneath its new private root before execution. Full source
closure, actual linked objects and exact frozen dependencies are bound.
No full ROM is included in the source-only archive.
'''
 (O/'HANDOFF.txt').write_text(note,encoding='utf-8')
 files|={O/n for n in['source.patch','freeze-proof.json','retained-negatives.json','HANDOFF.txt']}
 archive=O/'source-only.zip';members=[];ext={'.s','.asm','.inc','.cfg','.chr','.rle','.dep','.d','.py','.json','.txt','.patch','.md','.lua'}
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
  for p in sorted(files):
   if p.suffix.lower()in ext or p.suffix.lower()=='.bin'and p.stat().st_size<=65536:
    rel=p.relative_to(R).as_posix();z.write(p,rel);members.append(rel)
 files.add(archive)
 out=dict(source=True,status='FROZEN_SOURCE_CPU_QUALIFIED_CF_OWNER_RETIREMENT_FOUNDATION',candidate=stage['candidate'],parent=stage['parent'],joint=str(J),source_stage=str(J/'source-stage.json'),ready=66,CF_pending=True,BT_pending=True,native=False,installed=False,admitted=False,publication_allowed=False,source_archive_members=len(members),bindings={str(p.resolve()):sha(p)for p in sorted(files)})
 save(O/'handoff.json',out)
 for f,h in out['bindings'].items():assert sha(f)==h,('post-freeze binding',f)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for n in z.namelist():assert hashlib.sha256(z.read(n)).hexdigest()==sha(R/n),n
 D.mkdir(parents=True)
 for n in['handoff.json','source-only.zip','HANDOFF.txt','source.patch','freeze-proof.json','retained-negatives.json']:shutil.copyfile(O/n,D/n)
 for row in receipts:
  p=Path(row['path']);q=json.loads(p.read_text());q={k:v for k,v in q.items()if k not in['ABI','vectors','rows','checks','menus','scene','menu','global_init','direct_BT_contract','cohorts','bindings']}
  q.update(full_receipt=str(p),sha256=sha(p));save(D/(p.parent.name+'.json'),q)
 save(D/'receipt.json',dict(source=True,candidate=out['candidate'],handoff=sha(O/'handoff.json'),verified_bindings=len(files),archive_members=len(members),bindings={str(p.resolve()):sha(p)for p in sorted(D.iterdir())}))
 owned=own_tools|set(D.iterdir())|{D/'owned-files.txt'}
 (D/'owned-files.txt').write_text('\n'.join(p.relative_to(R).as_posix()for p in sorted(owned))+'\n')
 print(json.dumps(dict(handoff=str(O/'handoff.json'),SHA256=sha(O/'handoff.json'),candidate=out['candidate'],bindings=len(files),archive_members=len(members),checkpoint=str(D),receiptSHA256=sha(D/'receipt.json'))))
if __name__=='__main__':main()
