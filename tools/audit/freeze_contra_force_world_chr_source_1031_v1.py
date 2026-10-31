"""Compact files-only CF world-CHR repair closure. Never Git/native/install."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/contra-force-world-chr-publisher-1031-v1'
O=R/'docs/qa/checkpoints/2026-10-31/contra-force-world-chr-source-v1'
H=R/'docs/qa/checkpoints/2026-10-31/contra-force-scroll-source-v1/handoff.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf8',newline='\n')
def check(p,passed=True):
 q=json.loads(p.read_text())
 if passed:assert q['passed']
 for f,h in q.get('bindings',{}).items():assert sha(f)==h,('Changed dependency',f)
 return q

def main():
 assert not O.exists();O.mkdir()
 parent=check(H);stage=check(P/'source-stage.json')
 positive=[R/'build'/n/'controls.json'for n in['contra-force-native-enemy-pattern-controls-1031-v2','contra-force-world-chr-seam-controls-1031-v2','contra-force-world-chr-menu-controls-1031-v1']]
 negative=[R/'build/contra-force-native-enemy-pattern-diagnostic-1031-v1/controls.json',R/'build/contra-force-world-chr-seam-controls-1031-v1/controls.json']
 for p in positive:check(p)
 for p in negative:check(p,False)
 assert stage['candidate']=='a4410264ffccc7ce44e3b5ead1da639428cfa0594c94b2f63fa99fb4feab5b38'
 fixed=dict(CPU_address=0xe0c6,physical_bank=127,bytes=[18,20,21,22,23,24,25,26,4,5,6,7],readable_with_rawA3_rawC2=True,source='Genuine linked fixed E-ROM CHRBankInitValues, used by native MapperInit and FmNativePrepare')
 correction=dict(passed=True,product_changed=False,original_stage=str(P/'source-stage.json'),original_stage_sha256=sha(P/'source-stage.json'),
  superseded_field='only_semantic_change',superseded_value=stage['only_semantic_change'],
  authoritative_semantics='Authenticated CF graphics preserves the prior native scroll publisher and restores ONLY native sprite windows1..3 using genuine fixed CHRBankInitValues plus legacy X5ChrMode0. Body0, own weapon6, special4, all backgrounds and donor movement/art/contact are unchanged.',
  cause='Preparation copied the prior scroll-builder metadata literal; its replacement missed already-mangled UTF8 text. Emitted source and exact product oracle correctly contain the32B world-window repair. No frozen receipt/source/object was rewritten.',fixed_table=fixed)
 save(O/'metadata-correction.json',correction)
 diagnostics=json.loads(negative[0].read_text())
 bad=next(f for f in diagnostics['cohorts'][0]['frames']if f['enemies'])
 scope=dict(passed=True,source=True,native=False,installed=False,admitted=False,candidate=stage['candidate'],parent=stage['parent'],source_ready74=True,menu_profiles=86,
  cause='CF entered direct/wide portrait maps1..3; later CF graphics replaced only0. Goomba native A2/A4 records read portrait physical533 instead of native17. Body-only native checks passed but full-frame review failed.',
  exact_old_hardware_windows=bad['hardware_CHR'],corrected_native_windows1_3=[16,17,18],fixed_table=fixed,
  change='Extend own helper BFBA..<BFC6 from12B to32B BFBA..<BFDA inside previously-owned38B tail. Save/restoreX; copy native window shadows1..3 and clear ONLYtheir direct modes. Existing body publisher requests normal native reload. No new lease/global field/common/NMI code.',
  original_source_motion_jump_weapons_contacts_art_unchanged=True,all_nonCF_ROM_CHR_header_menu_BT_exact=True,
  all_native_and_private_entry_PCs_exact=True,diagnostic_end_label_relocated=['CfHostScrollPublishEnd',0xbfc6,0xbfda],cookie=stage['cookie'],
  source_controls=dict(classes=4,real_cold_parser_Main_and_normalNMI=True,worldX=[369]*4,camera=[257]*4,actual_Goomba_patterns_physical17=True,actual_lives_bodyP0=True,graphics_API_full64flag_pairs=512,extra_foreground_CPU_per_graphics_call=75,real_normal_lag_paused_NMI_IRQ_cuts=1024,full_AXYP_livepage1_33SMC_rawmaps=True,menu_pairs=86,ready_counts=[74,74],actual_Start_flags=10240),
  retained_negatives=['1cbb native advancing-scroll body/camera passed but full-frame Goomba art visually fails; not installation-qualified.','First seam test excluded native CurrentCHRBank page1 fields as dead stack then incorrectly expected6 global differences. V2 explicitly includes those live native fields and asserts exact restored shadows. No product change/assertion removed.'],
  remaining=['Root must run new bounded actual enemy-pattern/DMA native packet and visually review; no hardware/native pass asserted.','Shot/native-enemy geometry remains separate; source pistol visible pixels and genuine donor collision radii are being audited without muzzle/art changes.','Iron menu leftover A OR outside16name cells is separate existing UI issue, not modified.','No successful full1-1, earned pickups/shooting,60Hz or crowding claim.'])
 save(O/'scope.json',scope)
 (O/'README.md').write_text('''# Contra Force native enemy CHR restoration

The frozen1cbb controller smoke advanced correctly, but full-frame review found fragmented Goombas. Actual cold source execution confirmed hardware pages [962,532,533,534,19,20,21,21,0,1,2,3]. The native Goomba correctly emitted A2/A4/palette3, which read stale portrait page533 in window2.

This genuine source child extends the existing own BFBA helper from12 to32bytes, within38 owned bytes. It preserves the original scroll publisher, saves/restoresX, copies fixed E0C6 native CHRBankInitValues[1..3] and clears only their direct interpretation. Normal native publication maps physical16/17/18. Body0, weapon6, special4, backgrounds, all donor physics/art/contacts and all unrelated ROM bytes remain exact. The real24KB carrier and full cookie are regenerated(version4). All public/native/private entry PCs stay fixed; only a diagnostic end label moves.

Four natural cold/menu/Start/parser/sourceMain cohorts reachX369/camera257 with actual complete Goomba source patterns and normalNMI final hardware mappings.512 full-flag graphics pairs and1024 actual normal/lag/pausedNMI/IRQ cuts preserve AXYP/livepage1/all33SMC/maps. The helper adds75 foreground CPU per graphics call.86 menu pairs and10240 Start masks match1cbb. Source proof does not establish native PPU timing or installation readiness.

The original stage contains a copied stale semantic-description literal. metadata-correction.json explicitly supersedes that field without changing its original bytes or emitted product. Native fragment negatives, the test's initial page1-accounting failure and the separate failed crouch-fire evidence remain retained. No native process, Git index, Download or old source was changed.
''',encoding='utf8')
 tools=[R/'tools/audit'/n for n in['prepare_contra_force_world_chr_publisher_1031_v1.py','contra_force_native_enemy_pattern_diagnostic_1031_v1.py','contra_force_native_enemy_pattern_controls_1031_v2.py','contra_force_world_chr_seam_controls_1031_v1.py','contra_force_world_chr_seam_controls_1031_v2.py','contra_force_world_chr_foreign_menu_1031_v1.py',Path(__file__).name]]
 native=R/'build/contra-force-scroll-native-1031-v1/burns'
 refs=[native/'ready.json']+[native/'capture'/n for n in['binding.json','result.json','trace.csv','body-DMA.csv','source-record.csv','jump.png','endpoint.png','candidate-controller.log']]
 refs+=[R/'build/contra-force-scroll-review-1031-v1/burns-enemy-review.png']
 files=set(positive+negative+tools+refs+[P/'source-stage.json',O/'scope.json',O/'metadata-correction.json',O/'README.md'])
 files.update(p for p in P.iterdir()if p.is_file()and p.suffix=='.json')
 files.update(p for d in(P/'kernel',P/'joint')for p in d.iterdir()if p.is_file()and p.suffix in('.s','.cfg','.dep'))
 members={p.relative_to(R).as_posix():sha(p)for p in sorted(files)};save(O/'source-members.json',members)
 with zipfile.ZipFile(O/'source-only.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in files:z.write(p,p.relative_to(R).as_posix())
 with zipfile.ZipFile(O/'source-only.zip')as z:assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in members.items())
 bindings=dict(parent['bindings']);bindings.update(stage['bindings'])
 for p in positive+negative:bindings.update(json.loads(p.read_text()).get('bindings',{}))
 bindings.update({str(p.resolve()):sha(p)for p in files|{H,O/'source-members.json',O/'source-only.zip'}})
 hand=dict(**scope,actual_link_recipe=str(P/'final-link.json'),actual_kernel_recipe=str(P/'kernel-link.json'),actual_config=str(P/'joint/candidate.cfg'),inherited_parent_handoff=str(H),inherited_parent_handoffSHA=sha(H),archive_members=len(members),archive_bytes=(O/'source-only.zip').stat().st_size,bindings=bindings)
 save(O/'handoff.json',hand)
 owned=tools+[O/n for n in['metadata-correction.json','scope.json','README.md','source-members.json','source-only.zip','handoff.json','owned-files.json']]
 save(O/'owned-files.json',dict(files=[p.relative_to(R).as_posix()for p in owned],stage_or_commit=False))
 print(json.dumps(dict(path=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),candidate=stage['candidate'],bindings=len(bindings),members=len(members),bytes=hand['archive_bytes'])),flush=True)
if __name__=='__main__':main()
