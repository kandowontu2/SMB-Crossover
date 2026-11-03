"""Complete actual powerup ingress with an owning native-collector callback."""
import inspect,json
from pathlib import Path
import check_bub_powerup_ingress_1102_v53 as P
import compose_bub_collecting_gate_1102_v57 as G
import prepare_bub_collecting_upgrades_1102_v56 as U
from prepare_selected_native_packet_v1 import sha
R=P.R;O=R/'build/bub-upgrades-root-ingress-1102-v58'
def main():
    text=inspect.getsource(P.main);old=P.Q.bundles
    def loader():
        P.Q.bundles=old
        try:return G.bundles()
        finally:P.Q.bundles=loader
    P.Q.bundles=loader
    try:
        env=dict(P.__dict__,U=U,O=O,__file__=str(Path(__file__)));exec(compile(text,str(Path(__file__)),'exec'),env);env['main']()
    finally:P.Q.bundles=old
    path=O/'receipt.json';q=json.loads(path.read_text());q['joint_native_classifier']=str((G.O/'proposal.json').relative_to(R));q['bindings'][str(Path(P.__file__).relative_to(R))]=sha(Path(P.__file__));q['bindings'][str((G.O/'proposal.json').relative_to(R))]=sha(G.O/'proposal.json');path.write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':main()
