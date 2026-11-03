"""Distinct finalhost successor; preserves the candidate-bound v24 packet."""
from pathlib import Path
import argparse,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import qualify_mini_final_cold_1103_v24 as Q
import build_storage_guard_v1 as G
O=Q.O


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--kernel',type=Path,required=True);ap.add_argument('--sha256',required=True);a=ap.parse_args()
    G.preflight(private_root=O,reserved_bytes=100000,reserved_files=3,fresh=True)
    before=Q.P.M.sha((O/'final-payload-v24.json').read_bytes())
    base,q=Q.qualify(a.kernel,a.sha256)
    fit=json.loads((O/'owner-fit-v15.json').read_text());source=(O/'owner-v15.s').read_text()
    old='MiniCookie:\n .byte '+','.join('$%02x'%v for v in bytes.fromhex(fit['Mini_cookie_placeholder']))
    new='MiniCookie:\n .byte '+','.join('$%02x'%v for v in bytes.fromhex(q['Mini_cookie']))
    assert source.count(old)==1
    (O/'owner-final-v28.s').write_text(source.replace(old,new))
    q['supersedes_private_kernel_only']='Finalhost30 adds9B exact native camera export. Sharedmanager/extra/selector/73BSh/commonmapper/113Bcopier andmetadata/art unchanged; no largeISR re-run per root. Existing23/25/26 source-bound shared IRQ/FF/nested proofs retained with their exact historical payload hashes.'
    q['bindings'][Path(__file__).relative_to(R).as_posix()]=Q.P.M.sha(Path(__file__).read_bytes())
    q['bindings'][(O/'owner-final-v28.s').relative_to(R).as_posix()]=Q.P.M.sha((O/'owner-final-v28.s').read_bytes())
    (O/'final-payload-v28.json').write_text(json.dumps(q,indent=2)+'\n')
    assert Q.P.M.sha((O/'final-payload-v24.json').read_bytes())==before
    print(json.dumps({k:v for k,v in q.items()if k not in ['patches','bindings','actual_to_from_current_owners']}))


if __name__=='__main__':main()
