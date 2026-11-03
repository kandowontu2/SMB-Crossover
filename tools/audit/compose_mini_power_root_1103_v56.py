"""Emit the source-qualified38B Mini pickup bridge over the delivered nightly."""
from pathlib import Path
import argparse,json,hashlib,shutil
from prepare_selected_native_packet_v1 import R,sha
import build_storage_guard_v1 as G
O=R/'build/mini-power-candidate-root-1103-v56'
PIN='ca90e8be125c55e7ae12413964ecf766c9b890525751ea1e0ad6ce225613f4db'

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--ref',type=Path,action='append',default=[]);a=p.parse_args()
    q=json.loads(a.manifest.read_text());assert q['passed'] and q['bytes']<=5120
    assert q['parent_ROM_SHA256']==PIN
    for proof in [q,*[json.loads(t.read_text()) for t in a.ref]]:
        assert proof['passed']
        for name,h in proof.get('bindings',{}).items():assert sha(R/name)==h,name
    parent=R/'build/mini-mario-end-candidate-root-1103-v49/mini-end.nes'
    original=parent.read_bytes();assert sha(parent)==PIN
    raw=bytearray(original);allowed=set()
    assert len(q['patches'])==2
    spans={(1048592+962*1024,5120),(16+65*8192+0xb003-0xa000,16)}
    for row in q['patches']:
        at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex'])
        assert (at,len(old)) in spans and len(old)==len(new)
        assert raw[at:at+len(old)]==old
        raw[at:at+len(new)]=new;allowed.update(range(at,at+len(new)))
    assert hashlib.sha256(raw).hexdigest()==q['expected_memory_only_ROM_SHA256']
    assert len(raw)==len(original) and all(x==y or i in allowed for i,(x,y) in enumerate(zip(original,raw)))
    G.preflight(private_root=O,reserved_bytes=6_000_000,reserved_files=5,fresh=True)
    O.mkdir(exist_ok=False);rom=O/'mini-power.nes';rom.write_bytes(raw)
    for ext in ['.lbl','.dbg']:shutil.copyfile(parent.with_suffix(ext),rom.with_suffix(ext))
    receipt=dict(passed=True,private_candidate=True,native_qualified=False,installed=False,
        candidate=str(rom),parent_SHA256=PIN,candidate_SHA256=sha(rom),kernel_SHA256=q['SHA256'],
        kernel_bytes=q['bytes'],changed_bytes=sum(x!=y for x,y in zip(original,raw)),
        all_foreign_native_menu_metadata_art_bytes_exact=True,
        scope='Only Mini pickup and power-animation update routing; source movement, native ending fixes and all other characters unchanged. Generic native timing remains an adaptation.',
        bindings={str(t.resolve().relative_to(R)):sha(t) for t in [Path(__file__),a.manifest,*a.ref]})
    (O/'candidate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__':main()
