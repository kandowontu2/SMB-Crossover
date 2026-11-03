"""Finalhost39 cold-only rebind; all earlier frozen roots remain untouched."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import qualify_mini_final_cold_1103_v24 as Q
import build_storage_guard_v1 as G
O=R/'build/mini-mario-final-owner-1103-v40'
HOST=R/'build/mini-mario-host-1103-v22'
PIN='3cb231ae339b0b24be459abf516b08aecc3afa0b44da12bd1a0022884bbede05'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def snapshot(root):
    return {p.relative_to(root).as_posix():sha(p)for p in root.rglob('*')if p.is_file()}


def main():
    G.preflight(private_root=O,reserved_bytes=100000,reserved_files=3,fresh=True)
    O.mkdir(exist_ok=True);assert not(O/'source-stage.json').exists()
    roots=[Q.O,R/'build/mini-mario-final-owner-1103-v29'];before={p:snapshot(p)for p in roots}
    host=json.loads((HOST/'mini-host-v39.json').read_text());assert host['bytes']==5020 and host['SHA256']==PIN
    base,q=Q.qualify(HOST/'mini-host-v39.bin',PIN)
    assert all(snapshot(p)==before[p]for p in roots),'Earlier frozen roots changed'
    fit=json.loads((Q.O/'owner-fit-v15.json').read_text());source=(Q.O/'owner-v15.s').read_text()
    old='MiniCookie:\n .byte '+','.join('$%02x'%v for v in bytes.fromhex(fit['Mini_cookie_placeholder']))
    new='MiniCookie:\n .byte '+','.join('$%02x'%v for v in bytes.fromhex(q['Mini_cookie']))
    assert source.count(old)==1
    owner=O/'owner-final-v40.s';owner.write_text(source.replace(old,new))
    q.update(final_host_revision=39,final_host_source=HOST.relative_to(R).as_posix()+'/mini-host-v39.s',
        previous_frozen_roots_preserved=True,
        interrupt_reuse='Per root, no fullISR rerun: sharedmanager/selector/commonmapper/113Bcoldcopier unchanged. Existing23cold/25liveauth/26nested receipts retain their exact historical payload bindings. This rebind qualifies host39 copy/readback/owner transitions/authentication only, not new private Draw/Main interrupt execution.',
        source_scope='Root host39 uses existing Ss specialoverride because the real unconditional legacy fullshotbank writer follows Draw. Kernel5020B plus100B explicitFF code padding; metadata/art/currentfourpayloads/sharedcode exact. Root owns actual fivelegacyvalue graphics proof, native candidate and nightly qualification.')
    q['bindings'].update({p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),owner,HOST/'mini-host-v39.s',HOST/'mini-host-v39.json',*[p/'source-stage.json'for p in roots]]})
    manifest=O/'final-payload-v40.json';manifest.write_text(json.dumps(q,indent=2)+'\n')
    stage=dict(passed=True,status='FINAL_HOST39_COLD_QUALIFIED_FROZEN',ROM_written=False,emulator_run=False,
        kernel_SHA256=PIN,kernel_bytes=5020,code_bytes=5120,declared_FF_padding=100,
        memory_SHA256=q['memory_SHA256'],Mini_cookie=q['Mini_cookie'],parent_SHA256=q['parent_SHA256'],
        qualification='Actual Mini cold238682CPU/minSP190;5120code/1024metadata exact;C000..C900zero;8to/fromcurrentowner transitions;32individualownheaderpoisons;8copy/readback/protectionfaults;foreignselectedretire. Existing sharedinterruptproofs reused only under explicit unchanged-source scope.',
        previous_roots_verified_unchanged={p.relative_to(R).as_posix():len(before[p])for p in roots},
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),manifest,owner,HOST/'mini-host-v39.bin',HOST/'mini-host-v39.s',HOST/'mini-host-v39.json',*[p/'source-stage.json'for p in roots]]})
    (O/'source-stage.json').write_text(json.dumps(stage,indent=2)+'\n')
    files=list(O.iterdir());assert len(files)==3 and all(p.is_file()for p in files)
    print(json.dumps({k:v for k,v in stage.items()if k!='bindings'}|dict(output_files=3,output_bytes=sum(p.stat().st_size for p in files))))


if __name__=='__main__':main()
