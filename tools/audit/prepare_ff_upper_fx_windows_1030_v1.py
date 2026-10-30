"""Give FF spells existing upper sprite windows5..7 instead of native1..3."""
from pathlib import Path
import difflib,hashlib,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
from prepare_ff_current_component_v2 import qualified
from finalize_ff_current_component_v3 import dependencies
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/ff-joint-native-flash-1030-v1'
O=R/'build/ff-upper-fx-windows-1030-v1'
HP=R/'build/ff-joint-native-flash-qualified-1030-v1/handoff.json'


def rep(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)


def main():
    assert not O.exists()
    files=B.validate(HP,'802e29144ea73f3a4d2a2a68cebd881f9e93f27efe5c5e349c73b1947bb4e42d')
    O.mkdir();d=O/'joint';d.mkdir()
    for p in(P/'joint').rglob('*'):
        if p.is_file()and p.suffix in['.s','.inc','.cfg','.chr','.bin']:
            q=d/p.relative_to(P/'joint');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    source=(d/'ff-render.s').read_text()
    source=rep(source,' lda HSlot\n ldy #1\nWindow:',
        ' lda HSlot\n ldy #5                 ; existing upper sprite windows5/6/7.\nWindow:')
    source=rep(source,' .repeat 6\n asl\n .endrepeat\n sta FfTemp\n ldy #0',
        ' .repeat 6\n asl\n .endrepeat\n ora #1                  ;8x16 pattern-table1: biases41/81/C1.\n sta FfTemp\n ldy #0')
    B.write(d/'ff-render.s',source)
    cfg=(d/'private.cfg').read_text()
    cfg=rep(cfg,(P/'joint/ram3.bin').as_posix(),(d/'ram3.bin').as_posix())
    B.write(d/'private.cfg',cfg)
    before,after=str(P/'joint'),str(d)
    phases={p.stem:p for p in(P/'joint').glob('*-build.json')}
    for name,p in sorted(phases.items()):
        B.run(d,[v.replace(before,after)for v in json.loads(p.read_text())['command']],name)
    cmd=[v.replace(before,after)for v in json.loads((P/'joint/final-link.json').read_text())['command']]
    # Layout pass emits the new RAM3 payload. It is not a runnable/cookie-
    # authenticated candidate until its real carrier and ROM fingerprint agree.
    B.run(d,cmd,'layout-link')
    image=(d/'ram3.bin').read_bytes();oldimage=(P/'joint/ram3.bin').read_bytes()
    assert len(image)==8192 and image!=oldimage
    (d/'ff-stream.bin').write_bytes(image)
    cookie=bytes([167,22,0,6])+hashlib.sha256(image).digest()[:12]
    (d/'ff-cookie.bin').write_bytes(cookie)
    for name in['loader-build','stream-build']:
        B.run(d,[v.replace(before,after)for v in json.loads(phases[name].read_text())['command']],name+'-authenticated')
    B.run(d,cmd,'final-link');prepare(R,d/'candidate.nes')
    assert(d/'ram3.bin').read_bytes()==image
    new=qualified(d/'candidate.nes');old=qualified(P/'joint/candidate.nes')
    assert address(new,'FfHostRenderBegin')==0xa300
    assert address(new,'FfHostRenderEnd')==address(old,'FfHostRenderEnd')+2<=0xa700
    assert address(new,'FfHostDecodeFx')==address(old,'FfHostDecodeFx')
    moved={n:[address(old,n),address(new,n)]for n,v in old['syms'].items()
           if 'seg'in v and'::'not in n and address(old,n)!=address(new,n)}
    assert set(moved)=={'FfHostRenderEnd'},moved
    render=(address(old,'FfHostRenderBegin')-0xa000,address(new,'FfHostRenderEnd')-0xa000)
    outside=[i for i,(a,z)in enumerate(zip(oldimage,image))if a!=z and not render[0]<=i<render[1]]
    assert not outside,outside
    at=location(old,'FwCookie');cs=1048592
    ranges=[(at,at+16,'own_full_cache_cookie_v6'),(cs+893*1024,cs+901*1024,'own_existing_RAM3_carrier')]
    diff=[i for i,(a,z)in enumerate(zip(old['raw'],new['raw']))if a!=z]
    assert not[i for i in diff if not any(a<=i<z for a,z,n in ranges)],diff[:24]
    for n in['FfArtStart','FfArtEnd']:
        assert address(old,n)==address(new,n)
    patch=list(difflib.unified_diff((P/'joint/ff-render.s').read_text().splitlines(True),source.splitlines(True),
             fromfile='parent/joint/ff-render.s',tofile='candidate/joint/ff-render.s'))
    B.write(O/'source-hooks.patch',''.join(patch))
    for p in d.rglob('*.dep'):files.update(dependencies(p))
    files.update(p for p in O.rglob('*')if p.is_file());files.add(Path(__file__))
    files.update(Path(v)for v in cmd if v.endswith('.o'))
    B.save(O/'source-closure.json',dict(passed=True,native=False,admitted=False,
        candidate_sha256=B.sha(d/'candidate.nes'),parent_sha256=B.sha(P/'joint/candidate.nes'),
        RAM3_sha256=B.sha(d/'ram3.bin'),cookie=list(cookie),changed_ROM_bytes=len(diff),
        changed_RAM3_bytes=sum(a!=z for a,z in zip(oldimage,image)),host_render_bytes=render[1]-render[0],
        native_world_windows_preserved=[1,2,3,4],FF_FX_windows=[5,6,7],tile_biases=[0x41,0x81,0xc1],
        no_new_RAM_CHR_or_PRG_lease=True,original_CORE_ART_CHR_all_other_ROM_bytes_exact=True,
        all_existing_public_entry_PCs_exact=True,own_end_label_change=moved,
        limits=['Source only; exact source descriptors/PPU patterns/nativeworld coexistence/coldloader/ISR/Main controls pending.',
            'Mouse/other selectedFF upperwindow consumers must be excluded from actual source configuration, not assumed.',
            'FX palette ownership,optional ink,sharedpostBG/audio/readiness,native1-1 and earned upgrades remain open.'],
        bindings={str(p.resolve()):B.sha(p)for p in sorted(files)}))
    print('FF UPPER FX SOURCE',B.sha(d/'candidate.nes'),flush=True)


if __name__=='__main__':main()
