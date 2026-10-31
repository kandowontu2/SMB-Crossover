"""Compact source-only checkpoint for CF native jump/contact correction."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/contra-force-world-roles-1031-v2'
O=R/'docs/qa/checkpoints/2026-10-31/contra-force-jump-contact-source-v1'
H=R/'docs/qa/checkpoints/2026-10-31/bt-cf-coherent-source-v1/handoff.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8',newline='\n')
def check(p):
 q=json.loads(p.read_text());assert q.get('passed',True)
 for f,h in q.get('bindings',{}).items():assert sha(f)==h,f
 return q
def main():
 assert not O.exists();O.mkdir()
 stage=check(P/'source-stage.json');parent=check(H)
 assert stage['candidate']=='a12661c1ddad2e15a8ce0589e86b5510703fd390e6346a982b14a6be0b742e3c'
 controls=[R/'build/contra-force-world-roles-cold-controls-v2/controls.json',R/'build/contra-force-natural-jump-controls-1031-v1/controls.json',R/'build/contra-force-natural-jump-controls-1031-v1/jump-summary.json',R/'build/contra-force-contact-vector-controls-1031-v1/controls.json']
 for p in controls:check(p)
 names=['prepare_contra_force_world_roles_1031_v1.py','prepare_contra_force_world_roles_1031_v2.py','check_contra_force_natural_jump_1031_v1.py','check_contra_force_contact_vectors_1031_v1.py',Path(__file__).name]
 tools=[R/'tools/audit'/n for n in names]
 neg=[R/'build/contra-force-world-roles-cold-controls-v1/controls.json',R/'build/contra-force-world-roles-motion-diagnostic-v1/rows.json',R/'build/contra-force-world-roles-1031-v1/source-stage.json']
 native=R/'build/contra-force-firstlooks-native-1031-v3/burns'
 scope=dict(passed=True,source=True,native=False,installed=False,candidate=stage['candidate'],parent=stage['parent'],
     source_ready=74,menu_profiles=86,menu_readiness_proof='Scoped inheritance: every main/menu/readiness byte is exact to frozen e538, whose actual86 identities/74ready/688Start-A passed.',
     only_semantic_change='Own lives delta0 retained; world role0 empty/role1 solid; existing movement JSR Import becomes JSR AfterBG, whose first operation is the same Import. Original motion/table instructions and public PCs unchanged.',
     retained_native_negative='Burns v3 7b7 has180Main, visible body/blueBG/ground shots but0rise. Real source Main receipts also had0jump; horizontal/body claims remain valid but were not jump qualification. Role-only8401 proves ascent then frozen stale-ground contact; retained.',
     finite_controls=dict(real_cold_classes=4,lives_DMA_per_class=141,gameplay_Main_total=384,real_lag_NMI_and_IRQ_seams=32,
                          jump_rise=[80,72,64,76],landing_age=[74,72,70,73],landed_Y=176,
                          lives_bounds=[[89,119],[88,119],[88,119],[92,123]],all_33SMC_maps_live_page1_AXYP_restored=True),
     source_byte_oracle_equal=True,all_nonCF_bytes_and_public_PCs_preserved=True,
     retained_preparation_negatives=['All earlier preparation/observer/layout negatives remain immutable in parent lives-source handoff.',
        'Old world adapter reversed original role0 air/role1 solid. Original NativeInput removes A on role1; this was a genuine source defect.',
        'Role-only source8401 unmasked native ascent but retained07D2ground contact and froze atY144. New own import-first AfterBG consumes the previous native collision result before the next source update.'],
     remaining=['Root native firstlooks and visual review pending; no install from this lane.',
                'Normal eight-sprite crowding and performance limitations remain disclosed.'])
 save(O/'scope-and-negatives.json',scope)
 (O/'README.md').write_text('''# Contra Force jump and native-contact source correction

The previous7b7 native first look showed correct body/colors/ground weapons but no jump. The host world adapter reversed original CF role0 empty and role1 solid, causing the original input routine to remove A while standing in empty space. Correcting those two immediates permits authentic ascent, then exposes stale source ground contact after takeoff.

The existing movement call to Import now calls the existing AfterBG worker, whose first operation is exactly that Import. It consumes the previous native collision outcome before the next original input/body update. This preserves native landing/ceiling authority without a new shared hook, velocity workaround, code growth, state field or private-PC movement. The corrected lives delta0 is retained. The genuine source object images/carrier/full cookies are rebuilt; all non-CF bytes remain exact to frozen e538.

Four real cold/menu/parser cohorts and96Main each prove rises80/72/64/76 and actual native landings back atY176 (ages74/72/70/73).32 genuine public0 NMI/IRQ cuts cover the changed live call/world path and preserve AXYP/page1/all33SMC/maps. These are source CPU results; root native retry/visual approval and later full-route qualification remain pending. Original frozen receipts retain their finite valid horizontal/body/palette scopes; none is relabeled as jump success. No Git staging/commit or native launch was performed.
''',encoding='utf-8')
 files=set(tools+controls+neg+[P/'source-stage.json',O/'scope-and-negatives.json',O/'README.md'])
 files.update(p for p in P.iterdir()if p.is_file()and p.suffix=='.json')
 files.update(p for folder in[P/'kernel',P/'joint']for p in folder.iterdir()if p.is_file()and p.suffix in{'.s','.cfg','.dep'})
 files.update(native/'capture'/n for n in['binding.json','body-DMA.csv','trace.csv','candidate-controller.log','result.json','source-record.csv'])
 files.add(R/'docs/qa/checkpoints/2026-10-31/contra-force-lives-layout-source-v1/handoff.json')
 files.add(R/'build/contra-force-reproduction-v2/copy_bank_FF.asm')
 files.add(R/'build/contra-force-reproduction-v2/copy_bank_05.asm')
 members={p.relative_to(R).as_posix():sha(p)for p in sorted(files)}
 save(O/'source-members.json',members)
 with zipfile.ZipFile(O/'source-only.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
  for p in files:z.write(p,p.relative_to(R).as_posix())
 with zipfile.ZipFile(O/'source-only.zip')as z:
  for n,h in members.items():assert hashlib.sha256(z.read(n)).hexdigest()==h,n
 bindings=dict(parent['bindings']);bindings.update(stage['bindings'])
 for p in controls:bindings.update(json.loads(p.read_text()).get('bindings',{}))
 bindings.update({str(p.resolve()):sha(p)for p in files|{H,O/'source-only.zip',O/'source-members.json'}})
 handoff=dict(**scope,actual_link_recipe=str(P/'final-link.json'),actual_kernel_recipe=str(P/'kernel-link.json'),actual_config=str(P/'joint/candidate.cfg'),
     inherited_parent_handoff=str(H),inherited_parent_handoffSHA=sha(H),archive_members=len(members),archive_bytes=(O/'source-only.zip').stat().st_size,bindings=bindings)
 save(O/'handoff.json',handoff)
 owned=tools+[O/n for n in['scope-and-negatives.json','README.md','source-members.json','source-only.zip','handoff.json','owned-files.json']]
 save(O/'owned-files.json',dict(files=[p.relative_to(R).as_posix()for p in owned],agent_stage_or_commit=False))
 print(json.dumps(dict(path=str(O/'handoff.json'),sha256=sha(O/'handoff.json'),bindings=len(bindings),members=len(members),bytes=handoff['archive_bytes'])),flush=True)
if __name__=='__main__':main()
