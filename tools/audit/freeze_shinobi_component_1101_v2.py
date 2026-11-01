"""Make one compact review packet, excluding donor PRG/CHR and compiled objects."""
from pathlib import Path
import argparse, hashlib, json, zipfile

R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main(out):
    assembly=json.loads((out/'assembly.json').read_text())
    cpu=json.loads((out/'CPU-controls.json').read_text())
    assert assembly['passed'] and cpu['passed'] and cpu['differential_pairs']==2320
    for q in [assembly,cpu]:
        for p,h in q['bindings'].items():assert sha(p)==h,p
    selected={}
    for p in (out/'source').iterdir():
        if p.is_file():selected['source/'+p.name]=p
    for name in ['assembly.json','CPU-controls.json','pose-packets.json']:
        selected['proof/'+name]=out/name
    scripts=['recover_shinobi_component_1101_v2.py','check_shinobi_component_1101_v2.py',Path(__file__).name]
    for name in scripts:selected['tools/audit/'+name]=R/'tools/audit'/name
    contract=R/'tools/reference/shinobi_host_contract_1101_v2.inc'
    selected['tools/reference/'+contract.name]=contract
    manifest={name:dict(sha256=sha(p),bytes=p.stat().st_size) for name,p in selected.items()}
    archive=out/'source-proof.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,p in selected.items():z.writestr(name,p.read_bytes())
        z.writestr('packet-manifest.json',json.dumps(manifest,indent=2)+'\n')
    with zipfile.ZipFile(archive) as z:
        for name,row in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==row['sha256']
    report=dict(status='REVIEWABLE_PRIVATE_ORIGINAL_SOURCE_COMPONENT',native=False,installed=False,host_integrated=False,
        donor=assembly['donor'],donor_sha256=assembly['donor_sha256'],
        source_packet=dict(path=str(archive.resolve()),sha256=sha(archive),bytes=archive.stat().st_size,members=len(manifest)+1,
                           excludes='Donor ROM, full PRG/fixed-bank binary, CHR, objects, debug/link binaries and expanded original native snapshot. Regenerate exact inputs with pinned donor and indexed snapshot.'),
        source=dict(original_semantic_bytes=5568,recovered_instructions=2142,source_byte_exact=True,
                    original_spans=assembly['original_semantic_ranges'],runtime_code_bytes=cpu['code_end']-0x9000+1,
                    private_code=[0x9000,cpu['code_end']+1],private_state=[0x6000,0x6800],
                    original_fixed_bank_metadata_required=True,borrowed_ZP=[0,4],host_grant=False,
                    script_roots=assembly['script_roots'],relocated_pointer_words=len(assembly['relocated_pointer_words']),
                    pose_closure=assembly['art']),
        CPU=dict(pairs=cpu['differential_pairs'],counts=cpu['case_counts'],trace_sha256=cpu['trace_sha256'],
                 AXYP=True,full_state_with_declared_pointer_normalization=True,
                 source_instruction_coverage=cpu['executed_instruction_coverage'][0],
                 candidate_instruction_coverage=cpu['executed_instruction_coverage'][1],
                 normal_jump_fixture_rise=66,down_A_remains_crouched=True,
                 original_intro_idle_OAM_exact=True,original_body_CHR_exact=True),
        entrypoints=dict(player_states=assembly['original_player_states'],magic_targets=assembly['magic_targets'],
            motion='Sh_A196',animate_initialize='Sh_83AB',body_renderer='Sh_83FC',
            weapon_initialize='Sh_C880',weapon_update='Sh_C9DA',object_clear='Sh_8038',
            usage='Use portable.lbl addresses. Native-PC suffixes name source origins, not actual relocated addresses.'),
        callbacks=assembly['callbacks'],contract=str(contract.resolve()),
        required_before_admission=[
            'Adapt borrowed00..03 to authorized foreground scratch: SMB NMI owns00..02. Current lab pointers are not interrupt-safe. Prove real live IRQ/NMI, stack, maps and shared SMC restoration.',
            'Allocate selected-owner RAM/CHR/code resources; no host grant has been asserted. Original fixedE000 data is a lab dependency. Relocate the863-byte selected pose closure plus index table while preserving timer0000 behavior.',
            'Implement original-shaped head/feet/side queries, source callback class semantics and camera import/export in actual SMB Main; head query is feetY-48 and sides are X+/-11.',
            'Integrate native enemies, projectile/melee damage, health/injury, pickups, earned four weapon descriptors/six magic inventory effects and native audio/UI/scene leaves.',
            'Use native OAM allocator and display palette updates, then controller-driven menu/lives/gameplay qualification. Archived raw fixture is intro-only; it does not qualify palette/audio or original gameplay.',
            'Full1-1, shortcut, every upgrade and terrain/transitions remain untested.'
        ],
        tests='2,320 CPU pairs against equal synthetic floor/no-enemy/no-op audio/UI callbacks; no native or whole-stage claim.',
        reproduction=[
            'python tools/audit/run_bounded_build_v1.py --output build/shinobi-component-1101-v2 --resume --timeout120 -- python tools/audit/recover_shinobi_component_1101_v2.py',
            'python tools/audit/run_bounded_build_v1.py --output build/shinobi-component-1101-v2 --resume --timeout120 -- python tools/audit/check_shinobi_component_1101_v2.py',
            'python tools/audit/run_bounded_build_v1.py --output build/shinobi-component-1101-v2 --resume --timeout120 -- python tools/audit/freeze_shinobi_component_1101_v2.py'
        ])
    report['reproduction']=[x.replace('--timeout120','--timeout 120') for x in report['reproduction']]
    (out/'handoff.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,source_packet=report['source_packet'],CPU=report['CPU'],code_bytes=report['source']['runtime_code_bytes'],handoff=str((out/'handoff.json').resolve()))))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=R/'build/shinobi-component-1101-v2')
    main(p.parse_args().output.resolve())
