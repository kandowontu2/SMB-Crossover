"""Measure the three-byte UI pruning with the unchanged native Bill controller."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import rogue_current_bill_cadence_v1 as native
import rogue_current_native_v1 as base

O=R/'build/rogue-current-menu-v8'


def main():
    controls=json.loads((O/'prune-controls.json').read_text())
    assert controls['passed']and controls['ROM_sha256']==base.sha(O/'candidate.nes')
    for p,h in controls['source_bindings'].items():assert base.sha(p)==h,p
    digest=base.sha(__file__)
    native.O=O
    sys.argv=[__file__,'candidate']
    try:
        native.main()
    except SystemExit as result:
        assert base.sha(__file__)==digest
        p=O/'native/bill-candidate-v1/binding.json'
        # Keep the underlying runner's binding intact; this extra receipt
        # identifies the actual configuration and verified source gates.
        extra=dict(driver_sha256=digest,runner_binding_sha256=base.sha(p),
                   CPU_controls_sha256=base.sha(O/'prune-controls.json'),exit_code=result.code)
        (p.parent/'driver-binding.json').write_text(json.dumps(extra,indent=2)+'\n')
        raise


if __name__=='__main__':main()
