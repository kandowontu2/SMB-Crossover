"""Replay the exact nested IRQ regression with the native tail successor."""
import inspect,json
from pathlib import Path
import check_bub_nested_lag_1102_v64 as P
import compose_bub_tail_gateways_1102_v66 as G
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-upgrades-root-nested-1102-v68'
def main():
    env=dict(P.__dict__,G=G,O=O,__file__=str(Path(__file__)));exec(compile(inspect.getsource(P.main),str(Path(__file__)),'exec'),env);env['main']()
    p=O/'receipt.json';q=json.loads(p.read_text());q['bindings'][str(Path(P.__file__).relative_to(R))]=sha(Path(P.__file__));p.write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':
    try:main()
    except Exception as e:
        O.mkdir(exist_ok=True);(O/'negative.json').write_text(json.dumps(dict(passed=False,exception=repr(e)),indent=2)+'\n');raise
