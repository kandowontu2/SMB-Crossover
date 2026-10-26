"""Freeze the bounded ownership design, CPU stack proof and unlaunched sensor."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'mm-proto-publication-ownership-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p,v):
    Path(p).write_text(json.dumps(v,indent=2)+'\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True,exist_ok=False)
    prepared,mock,stack=[BASE/n for n in ['prepare-v2','mock-v2','stack-contract-v1']]
    ready=json.loads((prepared/'readiness.json').read_text())
    proof=json.loads((mock/'proof.json').read_text());abi=json.loads((stack/'proof.json').read_text())
    assert sha(prepared/'readiness.json')=='923ce9fa530bd2c879980ab410d84c14e09228cdcf322c072c6fc74ac19025d3'
    assert proof['passed'] and proof['mock_only'] and not proof['native_run']
    assert abi['passed'] and abi['actual_partial_NMI_paths']==512 and not abi['implementation']
    assert not list(prepared.glob('launch*')) and not (prepared/'result.json').exists()
    for p,h in ready['bindings'].items():assert sha(p)==h,p
    for data in [proof,abi]:
        for p,h in data['bindings'].items():assert sha(p)==h,p
    report=R/'docs/qa/mm-proto-publication-ownership-2026-10-26.txt'
    own=[R/'tools/audit'/n for n in ['mm_proto_publication_ownership_observer_v1.lua','mm_proto_publication_ownership_prepare_v1.py','mm_proto_publication_ownership_prepare_v2.py','mm_proto_publication_ownership_mock_v1.py','mm_proto_publication_ownership_mock_v2.py','mm_proto_publication_stack_contract_v1.py',Path(__file__).name]]
    (a.output/'tools').mkdir()
    for p in own:shutil.copyfile(p,a.output/'tools'/p.name)
    shutil.copyfile(report,a.output/'report.txt')
    for folder, label in [(prepared,'prepared'),(mock,'mock'),(stack,'stack')]:
        (a.output/label).mkdir()
        names=['readiness.json','preparation.json','source-facts.json','source-observer-controls.json','design-state-model.json','ownership-config.json','PLAN.txt'] if label=='prepared' else ['proof.json']
        for name in names:shutil.copyfile(folder/name,a.output/label/name)
    deps=set(own)|{report}
    for folder in [prepared,mock,stack,BASE/'prepare-v1',BASE/'mock-v1']:
        deps|={p for p in folder.rglob('*') if p.is_file()}
    deps|={Path(p) for p in ready['bindings']}
    for data in [proof,abi]:deps|={Path(p) for p in data['bindings']}
    bindings={str(p.resolve()):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(deps)}
    put(a.output/'bindings.json',bindings)
    put(a.output/'review-files.json',dict(report='report.txt',source_models_and_actual_stack_proof=['prepared','mock','stack'],exact_owned_tools='tools',all_external_prerequisites='bindings.json',
        unlaunched_native_packet=str(prepared),
        possible_parent_launcher=['C:/Users/kando/AppData/Local/Programs/Python/Python314/python.exe','-B',str(R/'tools/audit/presentation_timing_launch_v1.py'),'--packet',str(prepared),'--expected-grant-sha256','ROOT-must-provide-a-new-explicit-grant'],
        no_current_grant=True,actual_guard_module_unchanged=True,new_game_code_or_RAM=False,
        preserved_preparation_failure=str(BASE/'prepare-v1/failure.json'),preserved_mock_failure=str(BASE/'mock-v1/failure.json')))
    catalog={str(p.relative_to(a.output)).replace('\\','/'):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(a.output.rglob('*')) if p.is_file()}
    put(a.output/'catalog.json',catalog)
    final=dict(passed=True,freeze_verified=True,source_only=True,native_run=False,game_implementation=False,allocated_new_byte=False,
               actual_source_writer_closure_unproved=True,one_unlaunched_diagnostic_prepared=True,native_grant=False,
               ROM_sha256=ready['ROM_sha256'],new_byte_proposal=0x5ff8,
               source_model_states=24,source_model_edges=136,actual_NMI_partial_stack_cases=512,
               actual_Lua_callback_mock_Main_releases=6,actual_Lua_callback_mock_DMA_pairs=5,
               diagnostic_readiness_sha256=sha(prepared/'readiness.json'),mock_sha256=sha(mock/'proof.json'),stack_sha256=sha(stack/'proof.json'),
               original_full256_physical_guards_unchanged=True,maximum_later_native_launches=1,
               binding_count=len(bindings),bindings_sha256=sha(a.output/'bindings.json'),catalog_files=len(catalog),catalog_sha256=sha(a.output/'catalog.json'),
               report_sha256=sha(report),tool_sha256=sha(__file__),
               limits='Reviewable design plus fixed731 observer only. No alternator code, new allocation, native run, production/default/settings/Git change or hidden common-cost waiver. Source model/partial CPU stack proof/mock are distinct from physical publication/visibility/cadence acceptance.')
    put(a.output/'receipt.json',final)
    print(json.dumps(dict(receipt=str(a.output/'receipt.json'),receipt_sha256=sha(a.output/'receipt.json'),**final),indent=2))


if __name__=='__main__':main()
