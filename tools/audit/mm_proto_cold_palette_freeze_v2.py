"""Freeze the minimal source repair and one unlaunched strict Proto profile."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import sys
from final_item_abilities_run import lua

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
C=D/'robot-cold-palette-candidate-v2';OLD=D/'proto-startup-budget-ready-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    from link_pit_rygar_sophia_audit_cpu import scoped_load
    b=scoped_load(C/'candidate.nes');romsha=sha(C/'candidate.nes')
    assert romsha=='0ba628a76f02d4610c2608acd63cdd2a877e6e9a9eb667496a3efa1c655c1927'
    proofs=[C/'proof.json',C/'cpu-v1/proof.json',C/'lifecycle-v2/proof.json',C/'build-controls-v1/proof.json',D/'proto-startup-budget-review-v1/proof.json']
    for f in proofs:
        z=json.loads(f.read_text());assert z.get('passed',z.get('built',z.get('diagnostic_completed',False)))
    original=json.loads((OLD/'native/config.json').read_text());cfg=json.loads(json.dumps(original));cfg['ROM_sha256']=romsha
    before=(OLD/'native/run.lua').read_text();prefix='FINAL_ITEM_PROGRESSIVE='+lua(original)+'\n';assert before.startswith(prefix)
    script='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+before[len(prefix):]
    assert prefix+script[len('FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'):]==before
    for group in[cfg['hooks'],cfg['diagnostic']['hooks']]:
        for name,h in group.items():
            off=16+h['physical_bank']*8192+h['address']%8192
            assert list(b['raw'][off:off+len(h['bytes'])])==h['bytes'],name
    native=a.output/'native';native.mkdir();(native/'run.lua').write_text(script);put(native/'config.json',cfg)
    command=json.loads((OLD/'command.json').read_text())
    command=[str(native)if x==str(OLD/'native')else str(native/'run.lua')if x==str(OLD/'native/run.lua')else str(C/'candidate.nes')if x.endswith('root-current-roster-composition-v1\\candidate.nes')or x.endswith('root-current-roster-composition-v1/candidate.nes')else x for x in command]
    assert str(C/'candidate.nes')in command
    put(a.output/'command.json',command)
    put(a.output/'source-profile-proof.json',dict(prepared=True,native_run=False,
        only_config_change='ROM_sha256',controller_mechanics_and_strict_guard_body_byte_exact=True,
        actual_hook_opcodes_banks_unchanged=True,actual_source_same_old_entry_addresses=True,
        profile_variant=cfg['identity']['variant'],actual_requested_mode=cfg['mode_value'],cases=cfg['cases'],
        old_diagnostic_readiness_sha256=sha(OLD/'readiness.json')))
    bindings=json.loads((OLD/'bindings.json').read_text())
    for name,h in bindings.items():assert sha(name)==h,name
    for rel,h in json.loads((C/'source-manifest.json').read_text()).items():
        path=C/'source'/rel;assert sha(path)==h,rel;bindings[str(path)]=h
    extra=[*proofs,C/'candidate.nes',C/'candidate.dbg',C/'candidate.map',C/'candidate.lbl',C/'source-manifest.json',C/'source.patch',
        C/'lifecycle-v1/failure.json',C/'lifecycle-v1/failed-tool.py',D/'robot-cold-palette-candidate-v1/failure.json',D/'robot-cold-palette-candidate-v1/failed-tool.py',
        C/'cpu-v1/cases.json',C/'cpu-v1/cold-producer-NMI.json',C/'lifecycle-v2/lifecycle-cases.json',C/'lifecycle-v2/interrupt-cases.json',
        R/'docs/qa/mm-proto-cold-palette-2026-10-26.txt',Path(sys.executable)]
    tools=[R/'tools/audit'/x for x in['mm_proto_cold_palette_candidate_v1.py','mm_proto_cold_palette_candidate_v2.py','mm_proto_cold_palette_cpu_v1.py','mm_proto_cold_palette_lifecycle_v1.py','mm_proto_cold_palette_lifecycle_v2.py','mm_proto_cold_palette_freeze_v1.py','mm_proto_startup_budget_prepare_v1.py','mm_proto_startup_budget_prepare_v2.py','mm_proto_startup_budget_run_v1.py','mm_proto_startup_budget_review_v1.py']]
    tools.append(Path(__file__));pending=tools[:];seen=set()
    while pending:
        f=pending.pop()
        if f in seen:continue
        seen.add(f);extra.append(f)
        for node in ast.walk(ast.parse(f.read_text())):
            mods=[node.module]if isinstance(node,ast.ImportFrom)else[x.name for x in node.names]if isinstance(node,ast.Import)else[]
            for name in mods:
                if name:
                    dep=R/'tools/audit'/(name.split('.')[0]+'.py')
                    if dep.is_file():pending.append(dep)
    extra += list(a.output.rglob('*'))
    for x in extra:
        if x.is_file():bindings[str(x.resolve())]=sha(x)
    put(a.output/'bindings.json',dict(sorted(bindings.items())))
    put(a.output/'readiness.json',dict(source_qualified=True,native_run=False,native_granted=False,
        candidate_ROM_sha256=romsha,parent_ROM_sha256='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287',
        changed_ROM_bytes=74,changed_banks=[78],source_proofs={str(f):sha(f)for f in proofs},
        source_manifest_sha256=sha(C/'source-manifest.json'),source_patch_sha256=sha(C/'source.patch'),
        bindings=len(bindings),bindings_sha256=sha(a.output/'bindings.json'),command_sha256=sha(a.output/'command.json'),
        script_sha256=sha(native/'run.lua'),source_profile_sha256=sha(a.output/'source-profile-proof.json'),
        maximum_native_launches=1,maximum_workers=1,wall_bound=4000,host_seconds=1200,
        exact_ProtoHard_six_components_with_original_strict_guards=True,diagnostic_focus_actual_PPU=[374,377],
        source_measured_preDMA_saving=624,foreign_warm_producer_foreground_overhead=43,
        no_new_RAM=True,NMI_code_unchanged=True,ordinary_builds_exact=True,
        limitations='Source fixture qualifies actual producer sequences and completeNMI, not fullGameLoop/native recovery. One unlaunched profile, separate ROOT grant required. Native original deadlineFALSEs and source capacity/IRQ-oracle negatives retained. Current default3b unchanged.',tool_sha256=sha(__file__)))
    print(json.dumps(dict(readiness=str(a.output/'readiness.json'),sha256=sha(a.output/'readiness.json'),bindings=len(bindings)),indent=2))


if __name__=='__main__':main()
