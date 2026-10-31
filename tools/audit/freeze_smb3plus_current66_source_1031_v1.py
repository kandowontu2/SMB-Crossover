"""Compact immutable source/control handoff for genuine SMB3+ current66 join."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
P=R/'build/smb3plus-current66-source-1031-v2';J=P/'joint'
O=R/'docs/qa/checkpoints/2026-10-31/smb3plus-current66-source-v1'
ROOT=R/'docs/qa/checkpoints/2026-10-31/smb3plus-menu-controller-native-v1'
PLAN=R/'build/smb3plus-current66-adoption-plan-1031-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
def check(p):
    q=json.loads(p.read_text())
    if'passed'in q:assert q['passed'],p
    for n,h in q.get('bindings',{}).items():assert sha(n)==h,(p,n)
    return q


def main():
    assert not O.exists()
    assert sha(ROOT/'handoff.json')=='e83da0e0f7ba825cea380acd26ac6168cb0dcc5ab51ea3856997f131b85f9223'
    check(ROOT/'handoff.json')
    receipts=[P/n for n in['source-stage.json','regressions-v1.json','menu-controls-v1.json','vectors-v1.json']]
    receipts +=[R/'build/smb3plus-current66-whole-controller-1031-v1/probe.json',
               R/'build/smb3plus-current66-foreign-main-1031-v1/controls.json']
    checked=[check(p)for p in receipts]
    assert sha(J/'candidate.nes')=='01a40d4019ae00220c7279c9ab8d4f6f25afb44af1612a6a1483a257448f0fa9'
    assert checked[1]['foreign_movement_pairs']==1344 and checked[1]['exact_graphics_pairs']==9072
    assert checked[2]['foreign_menu_identities']==81 and checked[2]['status_ABI_cases']==768
    assert checked[3]['real_vectors']==3380
    O.mkdir(parents=True)
    source_names=['entrypoint.s','private.cfg','union.s','src/character_select.s','src/new_roster_dispatch.s',
        'src/smb3_mario_motion.s','src/smb3_mario_render.s','src/smb3_native_controller.inc',
        'src/smb3_mario_art.inc','src/smb3_mario_dispatch.s','smb3plus_body_host.s',
        'smb3plus_kick_host.s','smb3plus_float_state.inc','smb3plus_float_data.s','smb3plus_menu_name.s',
        'smb3plus-chr.s','toad-smb3plus-body.chr','peach-smb3plus-body.chr','main.dep']
    logs=[P/(n+'.json')for n in['main-build','union-build','chr-build','final-link']]
    for p in logs:
        q=json.loads(p.read_text());assert q['returncode']==0
        assert q['validation']['outputs_validated_before_execution']
    files=set(receipts+logs+[J/n for n in source_names])
    tools=[Path(__file__),R/'tools/audit/prepare_smb3plus_current66_source_1031_v1.py',
        R/'tools/audit/prepare_smb3plus_current66_source_1031_v2.py',
        R/'tools/audit/check_smb3plus_current66_source_1031_v1.py',
        R/'tools/audit/plan_smb3plus_current66_adoption_1031_v1.py',
        R/'tools/audit/plan_smb3plus_current66_adoption_1031_v2.py',
        R/'tools/audit/private_build_outputs_v1.py']
    files.update(tools)
    files.update(p for p in PLAN.iterdir()if p.is_file())
    files.update(p for p in ROOT.iterdir()if p.is_file())
    negative=R/'build/smb3plus-current66-source-1031-v1/final-link.json';files.add(negative)
    own=dict(private_source_root=str(P),native_emulator_launched=False,installed_ROM_edited=False,
        canonical_sources_edited=[],Git_index_or_commit_changed=False,
        actual_modified_source_files=[str(J/n)for n in source_names if n!='main.dep'],
        compressed_current_union_retained=True,source_only_graft=True,
        new_ROM_RAM_CHR_lease=False,global_RAM0_bytes=0,readiness_metadata_updated=False,
        actual_M3_variants='Existing raw17 four-way cycle0/1/2/3. Private child has new choices; no installed count/gate decision made.',
        root_checkpoint_preserved_SHA256=sha(ROOT/'handoff.json'),
        inherited_dependencies='Exact immutable current66 c663 source/objects/actual source recipes plus root e83 SMB3 donor source checkpoint; no executable/object/NES is archived here.',
        archive_excludes=['NES','objects','executables','large compiled DBG/map','new emulator captures'])
    write(O/'owned-files.json',own)
    text='''SMB3+ source-only composition onto installed current66

Candidate01a40d40 is genuinely assembled/linked from a new c663 clone and the
approved05b1 SMB3+ producers. Exact disjoint source-byte oracle matches all
2,097,168 ROM bytes; no oracle/patch bytes were used to build the cartridge.
The36451 changed bytes stay in66/81/90/91/92 and CHR969..<1019. All4621 resolved
actual object exports, public M3 PCs, current66 caches/cookies/header, fixed/DMC
banks and all other CHR are exact. Current compressed46-group union is retained.

Actual guarded current main/union producer recipes come from bowser-current64-v3;
the currentc663 final-link inputs and genuine new CHR object produce the child.
V1 linker-negative preserves stale donor UNALLOCATED_CHR_MEM usage. V2 uses the
actual current BW_STREAM_POST owner935..<1024, with only fixedF2400 new segment;
no MEMORY range or grant changes. M3 append endsAEFA/D3FD retain6B/3B audio gaps.

Rebound actual controls:2016 original whole-controller edge cases;1344 foreign
movement pairs;9072 graphics pairs;81 foreign menu identities;768 status ABI;
3380 real IRQ/normal/lag/paused NMI cases; current66 foreign wholeMain receipt.
Source readies/caches are never fabricated to qualify native rollout. The
source methods and limits remain explicit in each receipt. No Mesen was run.

Existing Mario3/Luigi3 variants remain, Toad/Peach use genuine donor art,
palettes, controller/float consumers and host native terrain. This is WIP:
ground pound, custom stomp delay, special art and kick SFX remain unfinished.
No perfect/final/full-campaign claim or installed/readiness update is made.
Root's exact500KB e83 donor/controller/native checkpoint is preserved unchanged
and included in this source archive as predecessor evidence, not a native pass
for this new composed hash. Root owns next native packet/run/install decision.
'''
    (O/'README.txt').write_text(text,encoding='utf-8');files.update([O/'owned-files.json',O/'README.txt'])
    manifest={p.relative_to(R).as_posix():sha(p)for p in sorted(files)}
    archive=O/'source-and-controls.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert len(z.namelist())==len(manifest)
        for n,h in manifest.items():assert hashlib.sha256(z.read(n)).hexdigest()==h
    write(O/'source-members.json',manifest)
    q=dict(status='FROZEN_GENUINE_SMB3PLUS_CURRENT66_SOURCE_CONTROLS_NO_NATIVE',
        candidate=sha(J/'candidate.nes'),base='c6635815711a624a02c4337cd9f1830ca9c43b14a824f2ea51963f796ad98c2a',
        source=True,native=False,installed=False,readiness_metadata_updated=False,
        original_root_e83_checkpoint_exact=True,exact_source_oracle=True,
        archive_members=len(manifest),archive_bytes=archive.stat().st_size,
        bindings={str(p.resolve()):sha(p)for p in sorted(files|{archive,O/'source-members.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl'})})
    write(O/'handoff.json',q);check(O/'handoff.json')
    print(json.dumps(dict(status=q['status'],handoff_sha256=sha(O/'handoff.json'),members=len(manifest),bindings=len(q['bindings']),archive_bytes=archive.stat().st_size)))


if __name__=='__main__':main()
