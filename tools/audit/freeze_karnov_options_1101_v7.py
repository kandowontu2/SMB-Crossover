"""Freeze compact option source/proof, excluding ROMs, full PRG and objects."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[2];O=R/'build/karnov-options-component-1101-v7'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assembly=json.loads((O/'assembly.json').read_text());cpu=json.loads((O/'CPU-controls.json').read_text())
    assert assembly['passed']and cpu['passed']and cpu['native']is False
    for q in[assembly,cpu]:
        for p,h in q['bindings'].items():assert sha(p)==h,p
    own=[R/'tools/audit'/n for n in['prepare_karnov_options_1101_v7.py','check_karnov_options_1101_v7.py','freeze_karnov_options_1101_v7.py']]
    own+=[R/'tools/reference'/n for n in['karnov_options_1101_v7.inc','karnov_options_1101_v7.md']]
    # These exact five existing source inputs are sufficient for the actor/
    # weapon differential fixture. No reference directory is copied/restored.
    fixture=[R/'build/karnov-original-source-1101-v1/source'/n for n in['portable_actor.inc','portable_dispatch.inc','original_dispatch.inc']]
    fixture+=[R/'build/karnov-original-weapons-1101-v1/source'/n for n in['portable_weapon.inc','portable_clear.inc']]
    generated=[p for p in O.iterdir()if p.is_file()and p.suffix in['.s','.cfg','.inc','.bin','.dbg','.lbl','.json']and p.name not in['handoff.json']]
    files=own+fixture+generated
    handoff=dict(passed=True,component_only=True,native=False,installed=False,code_lease_granted=False,
        source_component_bytes=assembly['source_component_bytes'],test_fixture_bytes=assembly['existing_actor_weapon_test_fixture_bytes'],
        base_ROM_sha256=assembly['base_ROM_sha256'],donor_sha256=assembly['donor_sha256'],
        new_private_scratch=[0xc865],borrowed_ZP=[3,4],supported_host_options=[0,3,7],
        source_pairs=cpu['source_pairs'],engine_executions=cpu['engine_executions'],
        converter_cases=cpu['input_edges']['actual_assembled_previous_current_cases'],
        source_trace_sha256=cpu['source_trace_sha256'],contract='tools/reference/karnov_options_1101_v7.md',
        input_hook='tools/audit/prepare_karnov_options_1101_v7.py:transform_terrain',kernel_hook_net_bytes=4,
        host_controls='Fresh Select cycles owned0/3/7/NONE. Down+freshB activates a supported selection. Existing source effects continue when NONE is selected.',
        clock_adaptation=assembly['host_clock'],production_callbacks=assembly['production_callback_imports'],
        limits=cpu['limits'],files={p.relative_to(R).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))for p in files})
    (O/'handoff.json').write_text(json.dumps(handoff,indent=2)+'\n');files.append(O/'handoff.json')
    with zipfile.ZipFile(O/'source-proof.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in files:z.write(p,p.relative_to(R).as_posix())
    print(json.dumps(dict(passed=True,packet=str(O/'source-proof.zip'),sha256=sha(O/'source-proof.zip'),bytes=(O/'source-proof.zip').stat().st_size,members=len(files))))
if __name__=='__main__':main()
