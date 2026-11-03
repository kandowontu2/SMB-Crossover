"""Change only Mini's five code pages and its payload-derived cookie."""
from pathlib import Path
import argparse,hashlib,json,shutil
import prepare_mini_owner_payload_1103_v19 as P
import build_storage_guard_v1 as G
R=Path(__file__).resolve().parents[2]
O=R/'build/mini-mario-end-candidate-root-1103-v49'
PIN='8daf59cc958e2a3a645882ea53c6bd75e9a7c641793054f8ce534358f369a7d7'
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
    a=argparse.ArgumentParser();a.add_argument('--kernel',type=Path,required=True);a.add_argument('--proof',type=Path,required=True);q=a.parse_args()
    G.preflight(private_root=O,reserved_bytes=5000000,reserved_files=5,fresh=True)
    parent=R/'build/mini-mario-candidate-root-1103-v44/mini-private.nes'
    original=parent.read_bytes();assert sha(original)==PIN
    installed=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert sha(installed.read_bytes())==PIN
    proof=json.loads(q.proof.read_text());assert proof['passed']
    kernel=q.kernel.read_bytes();assert sha(kernel)==proof['SHA256']
    for name,h in proof.get('bindings',{}).items():assert sha((R/name).read_bytes())==h,name
    at=lambda page:1048592+page*1024
    meta=original[at(967):at(968)];art=original[at(968):at(969)]
    old=(R/'build/mini-mario-host-1103-v22/mini-host-v43.bin').read_bytes()
    previous=P.component(old,meta,art,sha(old));images=P.component(kernel,meta,art,sha(kernel))
    assert original[at(962):at(967)]==previous['code']
    cookie_at=16+65*8192+0xb003-0xa000
    assert original[cookie_at:cookie_at+16]==previous['cookie']
    # Original arithmetic/world/tile/OAM/animation, Fresh and active Main all
    # remain byte-identical. Only vectors and later native integration differ.
    assert kernel[114:44966-0xa000]==old[114:44966-0xa000]
    assert kernel[44966-0xa000:45483-0xa000]==old[44966-0xa000:45483-0xa000]
    raw=bytearray(original);patches=[]
    def change(pos,before,after,role):
        assert len(before)==len(after) and raw[pos:pos+len(before)]==before
        raw[pos:pos+len(after)]=after
        patches.append(dict(file_offset=pos,old_hex=before.hex(),new_hex=after.hex(),role=role))
    change(at(962),previous['code'],images['code'],'Existing exclusively owned Mini code962..966')
    change(cookie_at,previous['cookie'],images['cookie'],'Existing Mini complete16B payload cookie')
    allowed=set(range(at(962),at(967)))|set(range(cookie_at,cookie_at+16))
    assert all(a==b or i in allowed for i,(a,b)in enumerate(zip(original,raw)))
    O.mkdir(exist_ok=False);rom=O/'mini-end.nes';rom.write_bytes(raw)
    for ext in ['.lbl','.dbg']:shutil.copyfile(parent.with_suffix(ext),rom.with_suffix(ext))
    receipt=dict(passed=True,private_candidate=True,native_qualified=False,installed=False,
        parent_SHA256=PIN,candidate_SHA256=sha(raw),candidate=str(rom),
        kernel_SHA256=sha(kernel),kernel_bytes=len(kernel),Mini_cookie=images['cookie'].hex(),
        metadata_and_art_unchanged=True,source_motion_and_active_Main_unchanged=True,
        shared_native_frontend_and_all_foreign_bytes_unchanged=True,changed_bytes=sum(a!=b for a,b in zip(original,raw)),
        patches=patches,scope='Engine8-only source solid filtering; native ending and intermediate-screen sprite coordinates. No new resources or helper platforms.',
        bindings={str(p.relative_to(R)):sha(p.read_bytes())for p in [Path(__file__),q.kernel.resolve(),q.proof.resolve(),R/'tools/audit/prepare_mini_owner_payload_1103_v19.py']})
    (O/'candidate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k]for k in ['candidate','candidate_SHA256','kernel_bytes','changed_bytes','native_qualified']}))

if __name__=='__main__':main()
