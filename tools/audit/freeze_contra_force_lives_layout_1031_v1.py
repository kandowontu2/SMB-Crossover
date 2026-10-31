"""Compact source-only checkpoint for the genuine CF lives positioning fix."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/contra-force-lives-position-1031-v3'
O=R/'docs/qa/checkpoints/2026-10-31/contra-force-lives-layout-source-v1'
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
 assert stage['candidate']=='7b7f37eec12caf75fdccce29281d0cafb517c2c9e7d8d81e48aa5dbbd2927143'
 controls=[R/'build/contra-force-lives-position-controls-1031-v1/controls.json',R/'build/contra-force-lives-position-controls-1031-v1/lives-layout.json',R/'build/contra-force-lives-vector-controls-1031-v2/controls.json']
 for p in controls:check(p)
 names=['prepare_contra_force_lives_position_1031_v1.py','prepare_contra_force_lives_position_1031_v2.py','prepare_contra_force_lives_position_1031_v3.py',
        'check_contra_force_lives_position_1031_v1.py','check_contra_force_lives_vectors_1031_v1.py','check_contra_force_lives_vectors_1031_v2.py',Path(__file__).name]
 tools=[R/'tools/audit'/n for n in names]
 neg=[R/'build/contra-force-lives-position-1031-v1/negative.json',R/'build/contra-force-lives-position-1031-v2/negative.json',R/'build/contra-force-lives-vector-controls-1031-v1/controls.json']
 native=R/'build/contra-force-firstlooks-native-1031-v1/burns'
 scope=dict(passed=True,source=True,native=False,installed=False,candidate=stage['candidate'],parent=stage['parent'],
     source_ready=74,menu_profiles=86,menu_readiness_proof='Scoped inheritance: every main/menu/readiness byte is exact to frozen e538, whose actual86 identities/74ready/688Start-A passed.',
     only_semantic_change='Own CfHostPortrait ADC #56 -> #0; original source +16 body center retained. Same instructions and all public PCs.',
     retained_native_negative='Burns v1 e538 stopped on arbitrary static lives descriptor age. Its authentic body y145..175 independently exposed the real +56 layout defect. No native success is claimed for this source successor.',
     finite_controls=dict(real_cold_classes=4,lives_DMA_per_class=141,gameplay_Main_total=128,real_lag_NMI_and_IRQ_seams=32,
                          lives_bounds=[[89,119],[88,119],[88,119],[92,123]],all_33SMC_maps_live_page1_AXYP_restored=True),
     source_byte_oracle_equal=True,all_nonCF_bytes_and_public_PCs_preserved=True,
     retained_preparation_negatives=['v1 output guard rejected the inherited old map path BEFORE linking; no old output changed.',
        'v2 source oracle passed but PC observer incorrectly requested file offset for BSS symbols. v3 preserves all symbol addresses and physical offsets for ROM symbols.',
        'Vectorv1 passed numeric PC to a label-only helper and stopped before a vector. v2 uses the genuine public17 shared builder.'],
     remaining=['Root native firstlooks and visual review pending; no install from this lane.',
                'Normal eight-sprite crowding and performance limitations remain disclosed.'])
 save(O/'scope-and-negatives.json',scope)
 (O/'README.md').write_text('''# Contra Force lives placement source correction

The original direct-emitter portrait already uses the native PlayerY88 plus a16-pixel center. Its additional lives-only56-pixel delta placed the body below the life count. This child changes only that immediate to0, with no instruction/public-PC movement or global coordinate edit.

The genuine renderer is reassembled, source A1/C2/A3 images linked, the24KB carrier fingerprint recomputed, and the actual ROM loader/guard/carrier producers rebuilt. The exact cart oracle is one owned A3 byte plus its two fingerprint copies. All BT/main/menu/CHR-art/M3/shared59/restore67 bytes remain exact to frozen e538.

Four real source menu/Start/parser/lives cohorts pass141 lives DMA checks each and128 gameplay Main updates total.32 genuine public17 live-frame NMI/IRQ cuts preserve AXYP/page1/all33SMC/maps. Actual source y-bounds are89..119,88..119,88..119,92..123. Native proof and visual approval remain pending. Parent archives and binary artifacts are excluded from this compact ZIP; all actual producer/assets are bound by hash. No Git staging/commit or native launch was performed.
''',encoding='utf-8')
 files=set(tools+controls+neg+[P/'source-stage.json',O/'scope-and-negatives.json',O/'README.md'])
 files.update(p for p in P.iterdir()if p.is_file()and p.suffix=='.json')
 files.update(p for folder in[P/'kernel',P/'joint']for p in folder.iterdir()if p.is_file()and p.suffix in{'.s','.cfg','.dep'})
 files.update(native/'capture'/n for n in['binding.json','body-DMA.csv','trace.csv','candidate-controller.log'])
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
