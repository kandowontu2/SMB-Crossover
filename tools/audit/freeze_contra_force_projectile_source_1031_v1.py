"""Freeze compact source-only CF contact evidence; no Git/native/install actions."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/contra-force-projectile-contact-1031-v3'
H=R/'docs/qa/checkpoints/2026-10-31/contra-force-world-chr-source-v1/handoff.json'
O=R/'docs/qa/checkpoints/2026-10-31/contra-force-projectile-contact-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf8',newline='\n')
def check(p,positive=False):
 q=json.loads(p.read_text())
 if positive:assert q['passed'],p
 for f,h in q.get('bindings',{}).items():assert sha(f)==h,('Changed bound dependency',p,f)
 return q
def main():
 assert not O.exists();O.mkdir()
 parent=check(H,True);stage=check(P/'source-stage.json',True)
 assert stage['candidate']=='f4767d595a25bf64355b1e2cea86be7a93046f1cf139a4d9b0544e35f9ed4182'
 names=['contra-force-projectile-earned-controls-1031-v4','contra-force-projectile-mask-controls-1031-v2','contra-force-projectile-axis-controls-1031-v3','contra-force-projectile-group-controls-1031-v1','contra-force-projectile-geometry-controls-1031-v1','contra-force-projectile-vector-controls-1031-v2','contra-force-projectile-mask-vectors-1031-v2','contra-force-projectile-source-proof-1031-v2']
 positive=[R/'build'/n/'controls.json'for n in names];proofs=[check(p,True)for p in positive]
 audit=R/'build/contra-force-shot-shape-audit-1031-v1/audit.json';check(audit,True)
 negative_dirs=['contra-force-projectile-contact-1031-v1','contra-force-projectile-contact-1031-v2','contra-force-projectile-scalar-controls-1031-v1','contra-force-projectile-axis-controls-1031-v2','contra-force-projectile-axis-diagnostic-1031-v1','contra-force-projectile-earned-controls-1031-v2','contra-force-projectile-earned-controls-1031-v3','contra-force-projectile-earned-crouch-controls-1031-v1','contra-force-projectile-vector-controls-1031-v1','contra-force-projectile-mask-vectors-1031-v1','contra-force-projectile-source-proof-1031-v1','contra-force-scroll-combat-negative-1031-v1','contra-force-scroll-combat-pulse-controls-1031-v1','contra-force-standing-shot-negative-1031-v1']
 negative=[]
 for name in negative_dirs:
  folder=R/'build'/name
  for filename in('controls.json','negative.json'):
   p=folder/filename
   if p.exists():check(p);negative.append(p)
 corrections=dict(passed=True,original_receipts_unchanged=True,items=[
  dict(artifact=str(P/'source-stage.json'),field='original_donor_component_bytes_exact_except_zero_byte_export',correction='Original source is exact plus a zero-byte export. All232 donor chunk PCs/sizes remain fixed;64 operand bytes across15 chunks change only to the actual relocated private CfGate addresses. No instruction policy/muzzle/art/radius/motion change. See source-proof-v2.'),
  dict(artifact=str(audit),field='settled_native_negative.closed_shot_bottom',correction='That descriptive closed bound includes the last edge. Exact original strict half-open extent atY189/radius8 excludesY197 (last integer196); both versions still miss native reduced top198. The25 actual original comparator executions and measured source muzzle/art evidence remain valid.'),
  dict(artifact=str(positive[0]),field='scope',correction='Only four right-facing earned histories actually execute in v4. The sentence describing left-facing histories is inherited unused-policy text. Natural left route attempts remain failed v2/v3; both-facing/page-edge coverage is explicitly staged geometry, not natural left-controller completion.'),
  dict(artifact=str(R/'build/contra-force-projectile-vector-controls-1031-v2/controls.json'),field='scope',correction='The mangled arrow glyphs mean genuine outer SFC to A3 to C2 to A1. This is a source-CPU interrupt fixture, not a native result.')])
 save(O/'coverage-corrections.json',corrections)
 scope=dict(passed=True,source=True,native=False,admitted=False,installed=False,candidate=stage['candidate'],parent=stage['parent'],cookie=stage['cookie'],source_ready74=True,menu_profiles=86,
  change='Replace own point-only CF/native contact with genuine donor radii and strict overlap against source-derived static ordinary native body unions. Original donor shot allocator/motion/muzzle/poses/art remain unchanged. Native player-contact/stomp boxes are untouched.',
  intentional_host_adaptation='Ordinary native target rectangles use actual compiled family-pose opaque unions: rawX0..15,Y0..23 orY8..23. Hardware display Y adds1 to both source and native. Rectangles include transparent corners and compressed shell poses; this is not original donor-enemy geometry or per-frame opaque-pixel equality. Bowser retains original native typed target box.',
  exclusions='Original native immunity/active/Y-page/duplicate/defeated checks remain; typed zero entries reject Buzzy/Bullet/Podoboo and no-op IDs; squished Goomba state>=2 rejects. Radius0/invalid29 rejects.',
  resources=dict(new_RAM_fields=0,new_PRG_CHR_OAM_leases=0,A1_helper=[0xbf8c,0xbfe0],C2_code_data=[0xddd2,0xddfd],A3_end=0xbfdc,C2_existing_life_and_P1_workspace_untouched=True,mask_factor='145-byte table becomes81-byte exact tail plus19-byte bounded inline lookup; net45B saved. One original CfP1Temp write, exact flags/output. Private CfNativeP1Mask data export retired; actual sole object consumer is own p1-runtime.o.'),
  fixed_scope=dict(original_chunks=232,donor_gate_operand_relocations=64,chunks_with_relocations=15,matched_native_PC_locations=stage['all_native_matched_PC_locations_preserved'],all_nonCF_ROM_CHR_header_BT_menu_Start_exact=True,private_suffix_PC_relocations_disclosed=True),
  controls=dict(natural_right_facing_earned_Goomba_defeats=4,native_score_and_SFX_and_original_impact=True,mask_all64flag_cases=9280,strict_axis_phase_cases=2852,both_facing_pageedge_staged_cases=600,stale_hazard_exclusions=18,complete_DrawAll_normalNMI_pairs=16,contact_actual_ISR_cuts=5056,mask_actual_ISR_cuts=344),
  limits=['No native execution, readiness change, install or Download modification. Root must review and launch a new bounded exact-hash shooting packet.','Natural standing pistol vs short Goomba still misses; Iron settled crouch remains too high. Actual four-class positives use authentic duck timing (Iron freshDown+B startup). No arbitrary muzzle/velocity/art change.','Both-facing/page-edge coverage is staged source CPU. Natural left-facing route attempts hit a ceiling or native enemy and remain failures.','No earned upgraded weapons/Bowser defeat, full1-1 clear, tall-pipe traversal, mushroom/flower, native timing or60Hz claim.','Iron menu leftover A OR is a separate existing UI issue, unchanged.'])
 save(O/'scope.json',scope)
 save(O/'negative-ledger.json',dict(retained_files=[dict(path=str(p),sha256=sha(p),passed=json.loads(p.read_text()).get('passed'))for p in negative],interpretation=[
  'Original heldDown+B and settledDown pulse/standing point-contact outcomes are retained. Settled Iron still misses after body-target adaptation; authentic startup policy has a separate earned positive.',
  'First two source link attempts exceeded existing A3/cookie bounds. V3 funds the same adapter with an exact mask-data factor and local guard compaction; no extra lease.',
  'Scalar/axis v1/v2 wrongly required all33 freshly entered outerSFC operand bytes unchanged. Genuine NextBank and SafereturnA result operands change; allother31 are exact. Interrupts preserve all33.',
  'Vector v1 expected a temporary normal-NMI mapper commit to override the later foreground restore. V2 retains ISR effects and respects actual later writes; source unchanged.',
  'Mask-vector v1 completed its first ISR proof but failed record construction from duplicate kind metadata. V2 removes the duplicate key only; all assertion logic unchanged.',
  'First emitted donor-byte proof caught real private gate relocation operands. V2 enumerates exact genuine target replacements instead of claiming byte equality.',
  'Natural left-route v2/v3 are real controller-policy ceiling/contact failures. No state or source was changed to force those outcomes.']))
 (O/'README.md').write_text('''# Contra Force projectile contact source successor

Candidate f476 is a separate child of the frozen a441 world-CHR repair. No native process or installed file changes here.

The original CF pistol uses half extents6/8 and a strict comparator. Its visible art and source muzzle are retained. Native Goomba fireball boxes start below its visible body; the old origin-only adapter misses authentic shots. This child uses the genuine source radius table and a source-derived static native body rectangle for ordinary foes. It leaves native player/stomp boxes alone and retains the native defeat/score/SFX chain followed by original CF shot impact.

Four cold real-menu/Start/parser source histories earn native Goomba defeats with actual donor-allocated shots. Iron needs its authentic fresh Down+B startup; a fully settled Iron shot remains too high. All four positives face right.600 staged both-facing/page cases,18 exclusions,2852 strict-radius/phase cases,9280 exact mask cases,16 complete DrawAll/NMI output pairs and5400 actual interrupt cuts pass. These are finite CPU proofs, not native or full-level claims.

The adapter fits existing own A1/A3/C2 space with no new state. An exact mask-table factor saves45bytes. Original component source changes only by exporting its existing radius table. All232 donor chunks keep PCs/sizes;64 address operand bytes in15 chunks follow actual relocated private CfGate targets. The preparation's stronger byte-equality wording is explicitly corrected in coverage-corrections.json. Private suffix PCs may move; native/shared/public ROM PCs and every byte outside own expected cookies/carrier remain exact.

Earlier sizing, input-policy, bookkeeping and real contact failures are retained with their causes. Source-only.zip contains no NES/object/debug/executable payload or duplicate parent archive. The inherited parent handoff pins unchanged producers. Root owns review, any native capture, composition and publication.
''',encoding='utf8',newline='\n')
 tools=[p for p in (R/'tools/audit').glob('*projectile*1031*.py')if p.name!='freeze_contra_force_projectile_source_1031_v1.py']
 tools +=[R/'tools/audit'/n for n in['contra_force_shot_shape_audit_1031_v1.py','contra_force_standing_shot_probe_1031_v1.py','contra_force_startup_duck_shot_probe_1031_v1.py','contra_force_scroll_combat_diagnostic_1031_v2.py',Path(__file__).name]]
 extra=R/'build/contra-force-projectile-earned-startup-controls-1031-v1/controls.json';check(extra,True)
 files=set(tools+positive+negative+[audit,extra,P/'source-stage.json',R/'tools/reference/contra_force_projectile_contact_1031_v1.s',O/'coverage-corrections.json',O/'scope.json',O/'negative-ledger.json',O/'README.md'])
 files.update(p for p in P.iterdir()if p.is_file()and p.suffix=='.json')
 files.update(p for folder in(P/'kernel',P/'joint')for p in folder.iterdir()if p.is_file()and p.suffix in('.s','.cfg','.dep'))
 for folder in ['contra-force-projectile-contact-1031-v1','contra-force-projectile-contact-1031-v2']:
  files.update(p for p in(R/'build'/folder).glob('*.json'))
 for p in files:assert p.exists()and p.suffix.lower()not in('.nes','.o','.obj','.exe','.dbg','.bin','.zip'),p
 members={p.relative_to(R).as_posix():sha(p)for p in sorted(files)};save(O/'source-members.json',members)
 with zipfile.ZipFile(O/'source-only.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
 with zipfile.ZipFile(O/'source-only.zip')as z:assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in members.items())
 bindings=dict(parent['bindings']);bindings.update(stage['bindings'])
 for p in positive+negative+[audit,extra]:bindings.update(json.loads(p.read_text()).get('bindings',{}))
 bindings.update({str(p.resolve()):sha(p)for p in files|{H,O/'source-members.json',O/'source-only.zip'}})
 for f,h in bindings.items():assert sha(f)==h,('Final changed dependency',f)
 hand=dict(**scope,actual_link_recipe=str(P/'final-link.json'),actual_kernel_recipe=str(P/'kernel-link.json'),actual_config=str(P/'joint/candidate.cfg'),inherited_parent_handoff=str(H),inherited_parent_handoffSHA=sha(H),archive_members=len(members),archive_bytes=(O/'source-only.zip').stat().st_size,bindings=bindings)
 save(O/'handoff.json',hand)
 owned=tools+[R/'tools/reference/contra_force_projectile_contact_1031_v1.s']+[O/n for n in ['coverage-corrections.json','scope.json','negative-ledger.json','README.md','source-members.json','source-only.zip','handoff.json','owned-files.json']]
 save(O/'owned-files.json',dict(files=[p.relative_to(R).as_posix()for p in sorted(set(owned))],stage_or_commit=False))
 print(json.dumps(dict(path=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),candidate=stage['candidate'],bindings=len(bindings),members=len(members),bytes=hand['archive_bytes'])),flush=True)
if __name__=='__main__':main()
