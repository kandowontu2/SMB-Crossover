"""Build a separate current counterpart from exact reviewed component patches.

The old prototype candidate is untouched. This private candidate admits only
Excitebike for controller qualification; public installation remains root-owned.
"""
from pathlib import Path
import hashlib,json,os,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
from prepare_excitebike_host_1101_v1 import BASE,PIN
from prepare_excitebike_dispatch_1101_v1 import O,sha,labels,save

def compose(*,require_cpu=True):
    assert sha(BASE)==PIN;b=scoped_load(BASE);raw=bytearray(b['raw']);patches=[]
    receipts=['router-assembly.json','scene-assembly.json','host-assembly.json','dispatch-assembly.json','dispatch-lease.json']
    if require_cpu:receipts+=['router-CPU.json','host-CPU.json','dispatch-CPU.json','cold-CPU.json','current-CPU.json','terrain-CPU.json']
    for name in receipts:
        q=json.loads((O/name).read_text());assert q['passed'],name
        if name in ['router-CPU.json','host-CPU.json','cold-CPU.json','current-CPU.json','terrain-CPU.json']:assert q['base_ROM_SHA256']==PIN
    def patch(at,old,new,role):
        assert len(old)==len(new)and raw[at:at+len(old)]==old,(role,hex(at),raw[at:at+len(old)].hex(),old.hex())
        raw[at:at+len(new)]=new;patches.append(dict(role=role,offset=at,old=old.hex(),new=new.hex()))
    for p in json.loads((O/'router-assembly.json').read_text())['patches']:
        patch(p['offset'],bytes.fromhex(p['old']),bytes.fromhex(p['new']),p['role'])
    for off,name in [(0x740,'dispatch-body.bin'),(0x7e9,'scene-gate.bin'),(0x7fa,'menu-gate.bin'),
                     (0xe00,'dispatch-loader.bin'),(0x1031,'dispatch-foreign.bin'),(0x1105,'dispatch-foreign-bank.bin'),
                     (0x1062,'scene-own.bin'),(0x1077,'menu-body.bin'),
                     (0x108c,'dispatch-veneers.bin'),(0x10fb,'menu-done.bin')]:
        data=(O/name).read_bytes();patch(16+65*8192+off,bytes([255])*len(data),data,name)
    lab=labels(O/'scene.lbl');at=16+65*8192+lab['ExCookie']-0xa000
    patch(at,(O/'excitebike-cookie.bin').read_bytes(),(O/'host-cookie.bin').read_bytes(),'Complete owning kernel/metadata/body cookie')
    at=16+65*8192+0x108c+3*19;target=lab['ExReset']
    patch(at,bytes([76,lab['ExDispatch']&255,lab['ExDispatch']>>8]),bytes([76,target&255,target>>8]),'ROM-only authenticated cache retirement row19')
    payload=(O/'host-kernel.bin').read_bytes()+(O/'host-metadata.bin').read_bytes()+(O/'body-native.chr').read_bytes()
    for i,page in enumerate(range(728,739)):
        patch(1048592+page*1024,bytes(1024),payload[i*1024:i*1024+1024],f'Granted Ex page{page}')
    # v30 moved the private menu wrapper by30B; real scene address staysAC1D.
    for pc in [0xac2c,0xad88]:
        at=16+65*8192+pc-0xa000;target=lab['ExRetireBoth']
        patch(at,bytes.fromhex('2049a8'),bytes([32,target&255,target>>8]),'Retire both exact owners before foreign scene/menu')
    at=location(b,'InitScreen')+8
    old=bytes.fromhex('8d6a01a91d8d6c01a9ac8d6d01a9c1205a01');new=bytearray(old)
    new[4]=lab['ExScene']&255;new[9]=lab['ExScene']>>8
    patch(at,old,new,'Cold forced-blank Ex scene wrapper')
    at=16+66*8192+0x1969
    old=bytes.fromhex('8d6a01a9888d6c01a9ad8d6d01a9c14c5a01');new=bytearray(old)
    new[4]=lab['ExMenuResolve']&255;new[9]=lab['ExMenuResolve']>>8
    patch(at,old,new,'Native menu resolver Ex wrapper')
    # Actual source-valid pending domain across all90 profiles is3,4,24,25.
    # Both consumers read carry only;25 remains the sole pending/locked owner.
    at=16+76*8192+0x1ff3
    patch(at,bytes.fromhex('2079b9900538e903c90260eaea'),bytes.fromhex('2079b99002c91960eaeaeaeaea'),'Private menu admission: pending24 only')
    if require_cpu:
        digest=hashlib.sha256(raw).hexdigest()
        for name in ['cold-CPU.json','current-CPU.json']:
            assert json.loads((O/name).read_text())['memory_candidate_SHA256']==digest,(name,'Stale exact-image CPU proof')
    return bytes(raw),patches,receipts

def main():
    raw,patches,receipts=compose();dest=O/'current.nes';dest.write_bytes(raw)
    for suffix in ['.lbl','.dbg']:
        target=dest.with_suffix(suffix)
        if not target.exists():os.link(BASE.with_suffix(suffix),target)
        assert target.read_bytes()==BASE.with_suffix(suffix).read_bytes()
    q=dict(passed=True,private_candidate=True,ROM_SHA256=sha(dest),base_ROM_SHA256=PIN,
           candidate=dest.relative_to(R).as_posix(),preserves_latest_Sh_bbox_Arthur_Metal=True,
           all_preimages_exact=True,private_Excitebike_admission=True,Prince_locked=True,
           native_verified=False,installed=False,patches=patches,
           scope='Current counterpart for exact-hash native qualification. Source/CPU components passed; real Main/controller/PPU/full1-1 still required.',
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),BASE,*[O/n for n in receipts]]})
    save('current-composition.json',q);print(json.dumps({k:v for k,v in q.items()if k not in ['patches','bindings']}))

if __name__=='__main__':main()

