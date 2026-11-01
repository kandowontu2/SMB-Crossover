"""Save the tested conditional Doki implementation without admitting it early."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2]
B=R/'build/doki-current-component-1101-v1';A=R/'build/doki-original-art-1101-v1'
O=R/'build/doki-current-checkpoint-1101-v1';K=R/'docs/qa/checkpoints/2026-11-01/doki-current-physics-art-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def main():
    assert not(O/'source-stage.json').exists()and not(K/'published.json').exists()
    physics=json.loads((B/'physics-controls.json').read_text());art=json.loads((A/'asset-controls.json').read_text());port=json.loads((B/'port-assembly.json').read_text())
    for q in [physics,art,port]:
        assert q['passed']
        for p,h in q['bindings'].items():assert sha(p)==h,p
    assert physics['candidate']==port['candidate']==sha(B/'candidate.nes')
    dest=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');assert sha(dest)=='429b9f3c3fb551ec023d997f9e83515a2c68f1447a2d4a7cad43c029ff5ee3e2'
    O.mkdir(exist_ok=True);K.mkdir(parents=True,exist_ok=True)
    files={p for p in(B/'src').iterdir()if p.is_file()}
    files|={B/n for n in ['baseline-reproduction.json','exact-source-inputs.json','baseline-edited-inputs.json','assembly-controls.json','port-assembly.json','physics-controls.json','component-build.json','doki-component-build.json','link.json','doki-link.json','candidate.cfg']}
    files|={A/n for n in ['asset-controls.json','frames.bin','palettes.bin','doki-shared-pages.chr','original-poses.png']}
    files|={R/'tools/audit'/n for n in ['prepare_doki_current_component_1101_v1.py','port_doki_physics_current_1101_v1.py','check_doki_current_physics_1101_v1.py','prepare_doki_original_art_1101_v1.py','freeze_doki_current_port_1101_v1.py']}
    assert len(files)<100 and sum(p.stat().st_size for p in files)<4_000_000
    with zipfile.ZipFile(K/'source.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(K/'source.zip')as z:assert z.testzip()is None
    summary=dict(passed=True,source=True,source_CPU=True,native=False,admitted=False,installed=False,parent_nightly=sha(dest),private_candidate=physics['candidate'],
        previous_goal_turn_classification='progress',goal_complete=False,
        source_reproduction_payload_exact=True,source_bytes_recovered=288,source_bytes_free_after_physics=port['spare_core_bytes'],new_global_or_ZP_bytes=0,
        original_fidelity=physics['counts'],engine_executions=physics['engine_executions'],air_animation_contexts=physics['air_animation_contexts'],same_class_mode_switches=physics['same_class_mode_switches'],no_shrink_prefixes=len(physics['health_transition_prefixes']),
        original_renderer_cases=art['original_renderer_cases'],CHR_pages=art['CHR_pages'],shared_vegetable_bytes_unchanged=96,
        active_component=str(B.relative_to(R)),active_art=str(A.relative_to(R)),
        archive=dict(path=str((K/'source.zip').relative_to(R)),sha256=sha(K/'source.zip'),bytes=(K/'source.zip').stat().st_size,members=len(files)),
        next=['Finish the source-sized Doki drawing/palette/name integration; graphics packet and original frame table are ready','Extend SMB2 Select cycle to eight choices, with Imajin/Lina/Papa/Mama at variants4/5/6/7, and update menu admission/presentation totals90/85','Execute actual linked drawing against all128 original packets; preserve native vegetable rendering through shared CHR page804','Qualify cold selection/lives/controller combat/pipes/camera and menu transitions in Mesen before publishing a85-identity nightly','Continue all remaining original goal characters, full1-1 and shortcut/every-powerup audit'],
        limits=['Original full FDS-file reconstruction remains23/27 files exact; tested critical motion/render spans and asset files are taken from the original donor','Current new motion is linked in the private ROM, but Doki drawing and menu remain absent; manual variants would still use USA art','Neither this checkpoint nor the CPU/art proofs add identities to the installed81-character nightly','Baseline assembly-controls describes the pre-port stage; do not recursively validate its now-superseded mutable bindings as the current port. Use port-assembly and physics-controls.'])
    save(K/'handoff.json',summary)
    (K/'README.md').write_text('''# Doki quartet: current conditional physics and original art

The exact current SMB2 module was recovered as24 individually indexed source
inputs and rebuilt byte-for-byte against the installed81-character ROM.
Relaxing98 genuinely in-range relative branches freed288 bytes in its existing
bank. Conditional original Doki behavior is now assembled in that space:
Mama's six jump entries, no B speed boost, no Luigi airborne leg animation,
fixed carrying offsets and always-large/no USA shrink transitions. A bit in
the existing scene key distinguishes lineages with the same native class ID.
No global or zero-page bytes were added.119 source bytes remain in the core.

Actual original FDS instructions and the private port agree in192 jump,
32 movement, four lifting and720 carrying contexts. The old USA modes agree
with the installed81 parent in the same cases. Eight air-animation contexts,
12 health-transition prefixes and eight same-class lineage switches also pass.
These are finite declared CPU fixtures, not native level clears.

All four original character CHR files have been packed and compared against
the original renderer across128 pose/facing/carry cases. Pages804..807 suffice:
page804 preserves the three existing vegetable tile pairs, and its unused
tail holds Imajin. The following three pages were zero inside the already
allocated12KB S2 CHR segment before GB Pit; no CHR grant is enlarged.
Reindexing the body to tile6 and transparent tile58 preserves every
tested source pixel, position and flip. One small pose diagnostic is included.

Doki graphics, palettes, names, menu selection and native/controller checks
still need integration. The installed nightly remains81 identities and is
unchanged. This is progress toward the full active goal, not completion.
`source.zip` contains this compilation unit, recipes and compact CPU/art
evidence; no ROM, object, debugger, video or per-frame image forest is stored.
Do not recursively recover historical dependency trees. Continue in the
unqualified active component/art roots identified by the handoff.
''',encoding='utf-8')
    hand=R/'docs/qa/continuation-current.json';q=json.loads(hand.read_text());q.update(previous_goal_turn_classification='progress',goal_status='ACTIVE_INCOMPLETE',current_priority='Finish Doki original quartet graphics/palettes/names/menu and native qualification using the current tested conditional physics; preserve installed81 until a complete85-identity candidate passes.',Doki_current=summary)
    save(hand,q);save(O/'result.json',summary)
    print(json.dumps(dict(passed=True,checkpoint=str(K),private_candidate=physics['candidate'],installed_nightly_changed=False,archive_bytes=summary['archive']['bytes'])))


if __name__=='__main__':main()
