"""Emit only the qualified Prince payload and exact existing unlock spans."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
from prepare_selected_native_packet_v1 import R, sha
import build_storage_guard_v1 as G

O=R/'build/prince-body-current-candidate-root-1103-v186'
PIN='ca90e8be125c55e7ae12413964ecf766c9b890525751ea1e0ad6ce225613f4db'

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--proof',type=Path,required=True)
    p.add_argument('--ref',type=Path,action='append',default=[])
    a=p.parse_args()
    G.preflight(private_root=O,reserved_bytes=6_000_000,reserved_files=5,fresh=True)
    q=json.loads(a.manifest.read_text());proof=json.loads(a.proof.read_text())
    assert q['passed'] and proof['passed']
    assert proof.get('memory_SHA256',proof.get('expected_memory_only_SHA256'))==q['expected_memory_only_SHA256']
    extra=[json.loads(t.read_text()) for t in a.ref]
    assert all(t['passed'] for t in extra)
    for row in [q,proof,*extra]:
        for name,h in row.get('bindings',{}).items(): assert sha(R/name)==h,name
    parent=R/q['parent_ROM'];original=parent.read_bytes()
    assert sha(parent)==q['parent_SHA256']==PIN
    raw=bytearray(original);allowed=set();patches=[]
    for patch in q['patches']:
        at=patch['file_offset'];old=bytes.fromhex(patch['old_hex']);new=bytes.fromhex(patch['new_hex'])
        assert len(old)==len(new) and raw[at:at+len(old)]==old
        raw[at:at+len(new)]=new;allowed.update(range(at,at+len(new)));patches.append(patch)
    assert hashlib.sha256(raw).hexdigest()==q['expected_memory_only_SHA256']
    front=R/'docs/qa/allocations/prince-current-frontend-1103-v105.json'
    f=json.loads(front.read_text());assert len(f['approved_exact_patches'])==9
    for patch in f['approved_exact_patches']:
        at=patch['file_offset'];old=bytes.fromhex(patch['old_hex']);new=bytes.fromhex(patch['new_hex'])
        assert len(old)==len(new) and raw[at:at+len(old)]==old
        assert not allowed.intersection(range(at,at+len(new)))
        raw[at:at+len(new)]=new;allowed.update(range(at,at+len(new)));patches.append(patch)
    assert len(raw)==len(original)
    assert all(x==y or i in allowed for i,(x,y) in enumerate(zip(original,raw)))
    # Mini's full five-page code, metadata and atlas remain byte exact.
    lo=1048592+962*1024;hi=1048592+969*1024
    assert raw[lo:hi]==original[lo:hi]
    O.mkdir(exist_ok=False);rom=O/'prince-body-current.nes';rom.write_bytes(raw)
    for ext in ['.lbl','.dbg']: shutil.copyfile(parent.with_suffix(ext),rom.with_suffix(ext))
    receipt=dict(passed=True,private_candidate=True,native_qualified=False,installed=False,
        parent_SHA256=PIN,candidate_SHA256=sha(rom),candidate=str(rom),
        payload_memory_SHA256=q['expected_memory_only_SHA256'],
        Mini_code_metadata_art_unchanged=True,all_out_of_recipe_bytes_exact=True,
        changed_bytes=sum(x!=y for x,y in zip(original,raw)),patches=patches,
        source_proof=str(a.proof),manifest=str(a.manifest),
        scope='Current five-owner Prince body reservation and existing nine-span character unlock. No other owner or shared manager changes.',
        bindings={str(t.resolve().relative_to(R)):sha(t) for t in [Path(__file__),a.manifest,a.proof,front,*a.ref]})
    (O/'candidate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in ['patches','bindings']}))

if __name__=='__main__':main()
