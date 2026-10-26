"""Preserve the source-only body-order candidate without installing its assets."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'root-parodius-body-order-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    prepared=json.loads((P/'proof.json').read_text())
    assert sha(P/'candidate.nes')==prepared['candidate_ROM_sha256']=='7e52b78d6be39cf5315f937c0af4705fbd8c38b03416c7b66bc44cfc0cf37979'
    assert sha(ROOT/'build/smb-crossover-mmc5-expanded.nes')==prepared['baseline_ROM_sha256']
    assert prepared['all_old_addresses_exact'] and prepared['existing_symbols_exact']==72221
    assert prepared['changed_ROM_bytes']==3534 and prepared['changed_banks']==[76,116,117]
    assert not prepared['native_run'] and not prepared['adopted']
    assert all(sha(P/'source'/name)==value for name,value in prepared['changed_source'].items())
    cpu=json.loads((P/'body-emitter-cpu-proof.json').read_text())
    pixels=json.loads((P/'exact-body-pixels-tool-v1.json').read_text())
    assert cpu['passed'] and cpu['complete_body_emitter_cases']==11790
    assert cpu['cycle_delta']==dict(min=-9,max=8) and cpu['coordinate_ADC_return_V_difference_cases']==0
    assert pixels['passed'] and pixels['body_poses']==131 and pixels['screen_edge_and_facing_cases']==2096
    assert cpu['candidate_ROM_sha256']==pixels['candidate_ROM_sha256']==prepared['candidate_ROM_sha256']
    original=json.loads((P/'original-pixel-proof.json').read_text())
    original_bindings=json.loads((P/'original-pixel-bindings.json').read_text())
    assert original['native_pose_pixels_equal'] and len(original['cases'])==662
    assert sha(P/'original-pixel-proof.json')==original_bindings['proof_sha256']
    frozen=json.loads((D/'tmnt-native-storage-current50b5-v1/current-baseline-v1/frozen-source.json').read_text())['source_files']
    assert all(sha(ROOT/name)==value for name,value in frozen.items())
    out=ROOT/'docs/qa/checkpoints/2026-10-25/parodius-body-order-7e52-source'
    out.mkdir(parents=True,exist_ok=False)
    for name in ['proof.json','body-emitter-cpu-proof.json','exact-body-pixels-tool-v1.json',
                 'original-pixel-proof.json','original-pixel-bindings.json','review.patch',
                 'preparation-tool-before-symbol-check-repair.py']:
        shutil.copyfile(P/name,out/name)
    for name in prepared['changed_source']:
        target=out/'changed-source'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(P/'source'/name,target)
    tools={f'tools/audit/{name}.py':sha(ROOT/f'tools/audit/{name}.py') for name in [
        'trial_parodius_body_order_v1','check_parodius_body_order_cpu_v1',
        'check_parodius_body_pixels_v1','checkpoint_parodius_body_order_v1']}
    manifest=dict(adopted=False,native_run=False,production_changes=False,goal_complete=False,
                  candidate_ROM_sha256=prepared['candidate_ROM_sha256'],
                  installed_ROM_sha256=prepared['baseline_ROM_sha256'],external_archive=P.as_posix(),
                  tools=tools,files={p.relative_to(out).as_posix():sha(p) for p in out.rglob('*') if p.is_file()},
                  frozen_ROOT_production_inputs_unchanged=len(frozen),
                  limits='Immutable source/CPU/pixel study. Original visuals/colors remain exact '
                         'without the hardware sprite limit. Native eight-sprite fairness, '
                         'readability and cadence are unqualified. The separate HUD scroll '
                         'repair is not included. Keep the retained symbol-check harness error.')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=out.as_posix(),source_review_passed=True,adopted=False)))


if __name__=='__main__':main()
