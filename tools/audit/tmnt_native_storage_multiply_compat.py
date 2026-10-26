"""Fresh existing compatibility suites using real MMC5 product-read semantics."""
from pathlib import Path
import argparse
import importlib
import json
import sys
from tmnt_native_storage_driver import ROOT, sha
from tmnt_native_storage_multiply import MathMemory
import check_tmnt_render_oa
import check_tmnt_audio_fallback_oc


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', choices=['outer', 'shared', 'owners', 'irq', 'cost'], required=True)
    for name in ['baseline', 'candidate', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    check_tmnt_render_oa.Memory = MathMemory
    check_tmnt_audio_fallback_oc.Memory = MathMemory
    modules = dict(outer='tmnt_native_storage_outer_cpu', shared='vehicles_audio_wiring_cpu',
                   owners='tmnt_native_storage_owners_cpu', irq='tmnt_native_storage_irq_cpu',
                   cost='tmnt_native_storage_cost_cpu')
    module = importlib.import_module(modules[a.check])
    sys.argv = [module.__file__, '--candidate', str(a.candidate), '--output', str(a.output)]
    if a.check != 'irq': sys.argv += ['--baseline', str(a.baseline)]
    module.main()
    path = a.output / 'proof.json'
    result = json.loads(path.read_text())
    assert result['passed']
    result.update(actual_MMC5_product_read_model_on_both_comparands=True,
                  product_model_sha256=sha(Path(__file__).with_name('tmnt_native_storage_multiply.py')),
                  wrapper_sha256=sha(Path(__file__)))
    path.write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
