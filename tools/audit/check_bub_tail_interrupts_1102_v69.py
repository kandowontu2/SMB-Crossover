"""Full native pickup IRQ/FF lag-NMI replay over the final tail gateway body."""
import inspect,json
from pathlib import Path
import check_bub_collecting_interrupts_1102_v59 as P
import compose_bub_tail_gateways_1102_v66 as G
import prepare_bub_tail_gateways_1102_v65 as U
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-upgrades-root-interrupts-1102-v69'
def main():
    text=inspect.getsource(P.main);old="build/bub-upgrades-root-ingress-1102-v58/receipt.json";assert text.count(old)==1
    text=text.replace(old,'build/bub-upgrades-root-lifecycle-1102-v67/receipt.json')
    env=dict(P.__dict__,G=G,U=U,O=O,__file__=str(Path(__file__)));exec(compile(text,str(Path(__file__)),'exec'),env);env['main']()
    p=O/'receipt.json';q=json.loads(p.read_text());q['bindings'][str(Path(P.__file__).relative_to(R))]=sha(Path(P.__file__));p.write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':
    try:main()
    except Exception as e:
        O.mkdir(exist_ok=True);(O/'negative.json').write_text(json.dumps(dict(passed=False,exception=repr(e)),indent=2)+'\n');raise
