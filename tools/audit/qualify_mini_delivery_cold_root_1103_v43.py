"""Qualify exact delivery kernel without rewriting frozen earlier proofs."""
from pathlib import Path
import argparse,json,hashlib
import qualify_mini_final_cold_1103_v24 as Q
import build_storage_guard_v1 as G
R=Path(__file__).resolve().parents[2]
O=R/'build/mini-mario-delivery-cold-root-1103-v43'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    a=argparse.ArgumentParser();a.add_argument('--kernel',type=Path,required=True);a.add_argument('--sha',required=True);args=a.parse_args()
    G.preflight(private_root=O,reserved_bytes=100000,reserved_files=3,fresh=True)
    roots=[R/'build/mini-mario-owner-1103-v15',R/'build/mini-mario-final-owner-1103-v29',R/'build/mini-mario-final-owner-1103-v40']
    before={str(p):sha(p) for root in roots for p in root.iterdir()if p.is_file()}
    bundle,q=Q.qualify(args.kernel,args.sha)
    assert all(sha(p)==h for p,h in before.items())
    O.mkdir(exist_ok=False)
    q.update(frozen=True,earlier_frozen_files_unchanged=len(before),
        root_source=str(Path(__file__).relative_to(R)),root_source_SHA256=sha(__file__))
    (O/'receipt.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps(dict(passed=q['passed'],memory_SHA256=q['memory_SHA256'],kernel_SHA256=args.sha,earlier_files_unchanged=len(before))))

if __name__=='__main__':main()
