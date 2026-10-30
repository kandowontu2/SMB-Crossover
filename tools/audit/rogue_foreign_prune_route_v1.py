"""Replay the source-pruned Rogue candidate with the proven finite route bound."""
from pathlib import Path
import json
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import rogue_current_native_v1 as route

O=R/'build/rogue-current-menu-v8'


def main():
    controls=json.loads((O/'prune-controls.json').read_text())
    assert controls['passed']and controls['ROM_sha256']==route.sha(O/'candidate.nes')
    for p,h in controls['source_bindings'].items():assert route.sha(p)==h,p
    # The same7000frame policy previously reached6513frames normally but
    # needed202hostseconds. Reuse its qualified300s allowance directly.
    reference=R/'build/rogue-current-menu-v5/native/route-retry-v1'
    previous=json.loads((reference/'result.json').read_text())
    assert previous['passed']and previous['frames']==6513
    original_run=route.run
    def timed(*args,**kwargs):
        assert kwargs['timeout']==180
        kwargs['timeout']=300
        return original_run(*args,**kwargs)
    route.run=timed
    route.O=O
    digest=route.sha(__file__)
    sys.argv=[__file__,'route']
    try:
        route.main()
    except SystemExit as result:
        assert route.sha(__file__)==digest
        out=O/'native/route'
        extra=dict(driver_sha256=digest,runner_binding_sha256=route.sha(out/'binding.json'),
            CPU_controls_sha256=route.sha(O/'prune-controls.json'),exit_code=result.code,
            host_timeout_seconds=300,reference_result_sha256=route.sha(reference/'result.json'),
            frame_bound=7000,unchanged_route_policy=True)
        (out/'driver-binding.json').write_text(json.dumps(extra,indent=2)+'\n')
        raise


if __name__=='__main__':main()
