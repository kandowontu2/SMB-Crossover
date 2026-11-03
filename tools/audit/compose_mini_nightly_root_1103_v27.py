"""Root-reviewed Mini candidate; no installation or native-pass inference."""
from pathlib import Path
import hashlib,json,shutil
import prepare_mini_owner_payload_1103_v19 as P
import build_storage_guard_v1 as G
R=Path(__file__).resolve().parents[2]
O=R/'build/mini-mario-candidate-root-1103-v27'
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads((R/p).read_text())

def main():
    G.preflight(private_root=O,reserved_bytes=5000000,reserved_files=6,fresh=True)
    host=R/'build/mini-mario-host-1103-v22'
    kernel=(host/'mini-host-v26.bin').read_bytes()
    pin='eee8d1b557728fff864a0fe7ab38e7655b1308fa272c27df19db07786b1a8bc3'
    assert sha(kernel)==pin
    refs=['build/mini-mario-native-gates-1103-v23/receipt.json',
          'build/mini-mario-menu-1103-v14/menu-CPU-v17.json',
          'build/mini-mario-menu-1103-v14/source-audit-v18.json',
          'build/mini-mario-host-1103-v22/mini-host-CPU-v24.json',
          'build/mini-mario-host-1103-v22/mini-header-CPU-v27.json',
          'docs/qa/allocations/mini-mario-private-resources-1103-v24.json']
    for name in refs:
        q=read(name);assert q.get('passed',q.get('granted',False)),name
    art=R/'build/mini-mario-art-1103-v12'
    assert (art/'menu-portrait.chr').read_bytes()==(art/'body.chr').read_bytes()[:32]
    bundle,manifest=P.compose(kernel,(P.O/'metadata-v19.bin').read_bytes(),(art/'body.chr').read_bytes(),pin)
    raw=bytearray(bundle['raw']);extra=[]
    def patch(at,old,new,role):
        assert len(old)==len(new) and raw[at:at+len(old)]==old,(role,at,raw[at:at+len(old)].hex(),old.hex())
        raw[at:at+len(old)]=new
        extra.append(dict(file_offset=at,old_hex=old.hex(),new_hex=new.hex(),role=role))
    # Prince's private frontend has not passed graphics qualification. Restore
    # its exact public locked state; Mini's separate ninth Mario alt is retained.
    for q in read('docs/qa/allocations/prince-current-frontend-1103-v105.json')['approved_exact_patches']:
        patch(q['file_offset'],bytes.fromhex(q['new_hex']),bytes.fromhex(q['old_hex']),'Restore public Prince lock')
    menu=read('build/mini-mario-menu-1103-v14/proposal-v16.json')
    params={16+66*8192+0xa5b5-0xa000:0xc8,16+66*8192+0xb0b3-0xa000:3}
    used=set()
    for q in menu['patches']:
        at=q['file_offset'];new=bytearray.fromhex(q['new_hex'])
        for pos,value in params.items():
            if at<=pos<at+len(new):
                assert new[pos-at]==0;new[pos-at]=value;used.add(pos)
        patch(at,bytes.fromhex(q['old_hex']),bytes(new),q.get('role','Mini menu source'))
    assert used==set(params)
    for q in read(refs[0])['patches']:
        patch(q['file_offset'],bytes.fromhex(q['old_hex']),bytes.fromhex(q['new_hex']),q['role'])
    patch(16+65*8192+0xb01c-0xa000,b'\x03',b'\x05','Mini scene dispatch admits raw37..41')
    O.mkdir(exist_ok=False)
    rom=O/'mini-private.nes';rom.write_bytes(raw)
    parent=R/'build/combined-owner-auth-root-1103-v116/combined-auth-private.nes'
    for ext in ['.lbl','.dbg']:shutil.copyfile(parent.with_suffix(ext),rom.with_suffix(ext))
    manifest.update(ROM_emitted=True,native_qualified=False,installed=False,
        candidate_SHA256=sha(raw),candidate=str(rom),frontend_patches=extra,
        Mini_variant=8,Mini_identity=41,Prince_locked=True,CHR_art_page=968,
        retained_host_scope='Original ground/jump/fall/crouch/skid with explicit wall cling/jump adaptation. Actors/swim/climb remain deferred.',
        bindings={name:sha((R/name).read_bytes()) for name in [*refs,'build/mini-mario-menu-1103-v14/proposal-v16.json',str(Path(__file__).relative_to(R)),str((host/'mini-host-v26.bin').relative_to(R))]})
    (O/'candidate.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:manifest[k] for k in ['candidate','candidate_SHA256','native_qualified','installed','Mini_variant','Mini_identity','Prince_locked']}))

if __name__=='__main__':main()
