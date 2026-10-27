"""Freeze the finite base-cache source packet and unchanged unlaunched profile."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import sys
from final_item_abilities_run import lua
from link_pit_rygar_sophia_audit_cpu import scoped_load

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
C=D/'robot-base-palette-candidate-v2';OLD=D/'robot-cold-palette-budget-ready-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:Path(p).write_text(json.dumps(z,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    romsha=sha(C/'candidate.nes');assert romsha=='dfbdca24019776262c4388e3ea782fb989e24b8fc0e3cf0bfe0bbb84a9f480ad'
    b=scoped_load(C/'candidate.nes');proofs=[C/x for x in['proof.json','cpu-v2/proof.json','lifecycle-v2/proof.json','build-controls-v1/proof.json']]
    for f in proofs:
        z=json.loads(f.read_text());assert z.get('passed',z.get('built',False))
    original=json.loads((OLD/'native/config.json').read_text());cfg=json.loads(json.dumps(original));cfg['ROM_sha256']=romsha
    before=(OLD/'native/run.lua').read_text();prefix='FINAL_ITEM_PROGRESSIVE='+lua(original)+'\n';assert before.startswith(prefix)
    script='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+before[len(prefix):]
    assert prefix+script[len('FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'):]==before
    for group in[cfg['hooks'],cfg['diagnostic']['hooks']]:
        for name,h in group.items():
            off=16+h['physical_bank']*8192+h['address']%8192
            assert list(b['raw'][off:off+len(h['bytes'])])==h['bytes'],name
    native=a.output/'native';native.mkdir();put(native/'config.json',cfg);(native/'run.lua').write_text(script)
    command=json.loads((OLD/'command.json').read_text())
    command=[str(native)if x==str(OLD/'native')else str(native/'run.lua')if x==str(OLD/'native/run.lua')else str(C/'candidate.nes')if x==str(D/'robot-cold-palette-candidate-v2/candidate.nes')else x for x in command]
    assert str(C/'candidate.nes')in command;put(a.output/'command.json',command)
    put(a.output/'source-profile-proof.json',dict(prepared=True,native_run=False,only_config_delta='ROM_sha256',
        full_postconfig_Lua_controller_mechanics_guards_callbacks_byte_exact=True,
        actual_original_hook_opcodes_banks_exact=True,actual_mode=cfg['mode_value'],actual_variant=cfg['identity']['variant'],
        case_names=[x['name']for x in cfg['cases']],diagnostic_focus=[cfg['diagnostic']['first_frame'],cfg['diagnostic']['last_frame']],
        original_readiness_sha256=sha(OLD/'readiness.json')))
    bindings=json.loads((OLD/'bindings.json').read_text())
    for f,h in bindings.items():assert sha(f)==h,f
    for rel,h in json.loads((C/'source-manifest.json').read_text()).items():
        f=C/'source'/rel;assert sha(f)==h,rel;bindings[str(f.resolve())]=h
    extras=[*proofs,C/'candidate.nes',C/'candidate.dbg',C/'candidate.lbl',C/'candidate.map',C/'source-manifest.json',C/'incremental-source.patch',
        C/'cpu-v1/proof.json',C/'cpu-v2/direct.json',C/'cpu-v2/flows.json',C/'lifecycle-v2/cases.json',C/'lifecycle-v2/scratch-read-ownership.json',
        C/'lifecycle-v1/failure.json',C/'lifecycle-v1/failed-tool.py',D/'robot-base-palette-candidate-v1/failure.json',D/'robot-base-palette-candidate-v1/failed-tool.py',
        R/'docs/qa/mm-proto-base-palette-2026-10-26.txt',R/'docs/qa/mm-proto-cold-palette-native-2026-10-26.txt',Path(sys.executable)]
    extras += [OLD/x for x in ['ROOT-grant.json','ROOT-grant-v1-schema-negative.json','prelaunch-failure-v1.json','launch-binding-v1.json','launch-outcome-v1.json']]
    extras += [D/'robot-cold-palette-budget-review-v1'/x for x in ['proof.json','external-manifest.json','actual-378-evidence.json']]
    tools=[R/'tools/audit'/x for x in ['mm_proto_base_palette_candidate_v1.py','mm_proto_base_palette_candidate_v2.py','mm_proto_base_palette_cpu_v1.py',
        'mm_proto_base_palette_cpu_v2.py','mm_proto_base_palette_lifecycle_v1.py','mm_proto_base_palette_lifecycle_v2.py',
        'mm_proto_cold_palette_budget_review_v1.py','mm_proto_cold_palette_diagnostic_run_v1.py']]+[Path(__file__)]
    pending=tools[:];seen=set()
    while pending:
        f=pending.pop()
        if f in seen:continue
        seen.add(f);extras.append(f)
        for node in ast.walk(ast.parse(f.read_text())):
            names=[node.module]if isinstance(node,ast.ImportFrom)else[x.name for x in node.names]if isinstance(node,ast.Import)else[]
            for name in names:
                if name:
                    dep=R/'tools/audit'/(name.split('.')[0]+'.py')
                    if dep.is_file():pending.append(dep)
    extras+=list(a.output.rglob('*'))
    for f in extras:
        if f.is_file():bindings[str(f.resolve())]=sha(f)
    put(a.output/'bindings.json',dict(sorted(bindings.items())))
    put(a.output/'readiness.json',dict(source_qualified=True,native_run=False,native_granted=False,
        candidate_ROM_sha256=romsha,source_parent_ROM_sha256='0ba628a76f02d4610c2608acd63cdd2a877e6e9a9eb667496a3efa1c655c1927',
        installed_parent_ROM_sha256='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287',
        source_proofs={str(f):sha(f)for f in proofs},source_manifest_sha256=sha(C/'source-manifest.json'),
        bindings=len(bindings),bindings_sha256=sha(a.output/'bindings.json'),command_sha256=sha(a.output/'command.json'),
        script_sha256=sha(native/'run.lua'),source_profile_sha256=sha(a.output/'source-profile-proof.json'),
        maximum_native_launches=1,maximum_workers=1,wall_bound=4000,host_seconds=1200,no_retry=True,
        exact_original_ProtoHard_sixcases_and_all_strict_guards=True,diagnostic_focus=[374,380],
        source_NMI_parser_saving=152,additional_producer_cycles_vs_0ba=[0,60],NMI_code_changed=False,new_RAM_bytes=0,
        deliberate_scratch_dead_result='tier2 firstcachehitMmPaletteIndex1vsolduncachedappend2; exactreader/caller/poisonproof bound',
        no_current_or_native_recovery_claim=True,tool_sha256=sha(__file__)))
    print(json.dumps(dict(readiness=str(a.output/'readiness.json'),sha256=sha(a.output/'readiness.json'),bindings=len(bindings)),indent=2))


if __name__=='__main__':main()
