"""Freeze the one actual731 ownership diagnostic and additive source contract."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'mm-proto-publication-ownership-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p,z):Path(p).write_text(json.dumps(z,indent=2)+'\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True,exist_ok=False)
    native=BASE/'prepare-v2';review=BASE/'native-review-v3'
    ready=json.loads((native/'readiness.json').read_text());grant=json.loads((native/'ROOT-grant.json').read_text())
    run=json.loads((native/'native-receipt.json').read_text());proof=json.loads((review/'proof.json').read_text())
    assert sha(native/'ROOT-grant.json')=='0505ced393f3237203d96254737fba81c8b94560d6f43e6f0a5eb144bf3e2e28'
    assert run['passed'] and run['launches']==1 and run['retries']==0 and run['worker_released']
    assert proof['passed'] and proof['original_five_named_observations_byte_exact'] and not proof['game_implementation']
    bind=ready['bindings']|grant['qualification_bindings']
    for p,h in bind.items():assert sha(p)==h,p
    original=json.loads((review/'bindings.json').read_text())
    for p,z in original.items():assert sha(p)==z['sha256'],p
    deps={Path(p) for p in bind}|{Path(p) for p in original}
    for folder in [native,review,BASE/'native-review-v1',BASE/'native-review-v2']:
        deps|={p for p in folder.rglob('*') if p.is_file()}
    deps|={BASE/'freeze-v1/receipt.json',BASE/'freeze-v1/bindings.json',BASE/'freeze-v1/catalog.json'}
    report=R/'docs/qa/mm-proto-publication-ownership-native-2026-10-26.txt';deps.add(report)
    own=[R/'tools/audit'/name for name in ['mm_proto_publication_ownership_review_v1.py','mm_proto_publication_ownership_review_v2.py','mm_proto_publication_ownership_review_v3.py',Path(__file__).name]]
    deps|=set(own);(a.output/'tools').mkdir()
    for p in own:shutil.copyfile(p,a.output/'tools'/p.name)
    shutil.copyfile(report,a.output/'report.txt')
    for p,label in [(native/'native-receipt.json','actual-native-receipt.json'),(native/'ownership-result.json','actual-observer-result.json'),(review/'proof.json','actual-review-proof.json'),(BASE/'freeze-v1/receipt.json','source-design-freeze.json')]:shutil.copyfile(p,a.output/label)
    bindings={str(p.resolve()):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(deps)}
    put(a.output/'all-actual-bindings.json',bindings)
    catalog={str(p.relative_to(a.output)).replace('\\','/'):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(a.output.rglob('*')) if p.is_file()}
    put(a.output/'catalog.json',catalog)
    receipt=dict(passed=True,freeze_verified=True,native_run=True,unchanged_ROM_diagnostic=True,game_implementation=False,new_byte_allocated=False,
                 ROM_sha256=run['ROM_sha256'],launches=1,retries=0,worker_released=True,
                 baseline_original_inputs_PPU_timing_result_all_byte_exact=True,hardware_DMA_256_exact=402,
                 Main_releases=432,complete_Rosters=51,actual_no_draw_carry_images=26,
                 actual_stale_source_epoch_transfers=343,protected_lag_NMI=40,eligible_transferred_Rosters=49,pending_terminal_Roster=51,
                 raw_RAM_SMC_converter_bank_limitation_preserved=True,reviewer_v1_v2_negatives_retained=True,
                 all_actual_artifact_bindings=len(bindings),bindings_sha256=sha(a.output/'all-actual-bindings.json'),
                 catalog_files=len(catalog),catalog_sha256=sha(a.output/'catalog.json'),report_sha256=sha(report),
                 review_sha256=sha(review/'proof.json'),tool_sha256=sha(__file__),
                 limits='Observation-only native731 evidence. Does not adopt or qualify an unimplemented publication-aware body/shot alternator, death/later areas/Proto, exact00fb causal Main instruction, or universal source-writer closure. No new native launch/retry or production/default/settings/Git mutation.')
    put(a.output/'receipt.json',receipt)
    print(json.dumps(dict(receipt_sha256=sha(a.output/'receipt.json'),**receipt),indent=2))


if __name__=='__main__':main()
