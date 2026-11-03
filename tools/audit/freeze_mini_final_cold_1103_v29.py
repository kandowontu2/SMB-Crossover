"""Host32 cold-only successor; never mutates the completed shared source root."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import qualify_mini_final_cold_1103_v24 as Q
import build_storage_guard_v1 as G
O=R/'build/mini-mario-final-owner-1103-v29'
HOST=R/'build/mini-mario-host-1103-v22'
PIN='fdf4de887c86f898609e8094257cd3d2e62e1879dd0471a24e1e8c62ad825600'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def snapshot():
    return {p.relative_to(Q.O).as_posix():sha(p)for p in Q.O.rglob('*')if p.is_file()}


def main():
    G.preflight(private_root=O,reserved_bytes=100000,reserved_files=5,fresh=True)
    O.mkdir(exist_ok=True);assert not(O/'source-stage.json').exists()
    before=snapshot()
    host=json.loads((HOST/'mini-host-v32.json').read_text());assert host['bytes']==5010 and host['SHA256']==PIN
    base,q=Q.qualify(HOST/'mini-host-v32.bin',PIN)
    assert snapshot()==before,'The completed previous source root must remain exact'
    fit=json.loads((Q.O/'owner-fit-v15.json').read_text());source=(Q.O/'owner-v15.s').read_text()
    old='MiniCookie:\n .byte '+','.join('$%02x'%v for v in bytes.fromhex(fit['Mini_cookie_placeholder']))
    new='MiniCookie:\n .byte '+','.join('$%02x'%v for v in bytes.fromhex(q['Mini_cookie']))
    assert source.count(old)==1
    owner=O/'owner-final-v29.s';owner.write_text(source.replace(old,new))
    q.update(final_host_revision=32,final_host_source=HOST.relative_to(R).as_posix()+'/mini-host-v32.s',
        previous_frozen_source_root_preserved=True,
        interrupt_reuse='Per root, no fullISR rerun: sharedmanager/selector/commonmapper/113Bcoldcopier unchanged. Existing23cold/25liveauth/26nested receipts retain their original exact payload bindings. This rebind qualifies host32 copy/readback/owner transitions/authentication only, not new private Draw/Main interrupt execution.',
        source_scope='Root host32 graphics repair clears all12 modes at Fresh and republishes source art in Draw; kernel5010B plus110B explicitFF code padding. Metadata/art/currentfourpayloads/sharedcode exact. Root owns native graphics/scene/frontend and nightly qualification.')
    q['bindings'].update({p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),owner,HOST/'mini-host-v32.s',HOST/'mini-host-v32.json',Q.O/'source-stage.json']})
    manifest=O/'final-payload-v29.json';manifest.write_text(json.dumps(q,indent=2)+'\n')
    stage=dict(passed=True,status='FINAL_HOST32_COLD_QUALIFIED_FROZEN',ROM_written=False,emulator_run=False,
        kernel_SHA256=PIN,kernel_bytes=5010,code_bytes=5120,declared_FF_padding=110,
        memory_SHA256=q['memory_SHA256'],Mini_cookie=q['Mini_cookie'],parent_SHA256=q['parent_SHA256'],
        qualification='Actual Mini cold238682CPU/minSP190;5120code/1024metadata exact;C000..C900zero;8to/fromcurrentowner transitions;32individualownheaderpoisons;8copy/readback/protectionfaults;foreignselectedretire. Existingsharedinterruptproofs reused only under their explicit unchanged-source scope.',
        old_root_files_verified_unchanged=len(before),old_root=Q.O.relative_to(R).as_posix(),
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),manifest,owner,HOST/'mini-host-v32.bin',HOST/'mini-host-v32.s',HOST/'mini-host-v32.json',Q.O/'source-stage.json']})
    (O/'source-stage.json').write_text(json.dumps(stage,indent=2)+'\n')
    print(json.dumps({k:v for k,v in stage.items()if k!='bindings'}))


if __name__=='__main__':main()
