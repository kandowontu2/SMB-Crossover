"""Source-link actual FF body/world palette composition in existing leases."""
from pathlib import Path
import hashlib,json,re,sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
from prepare_ff_current_component_v2 import qualified
from finalize_ff_current_component_v3 import dependencies
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare

P=R/'build/ff-joint-combat-hooks-1030-v5'
O=R/'build/ff-joint-body-palette-1030-v2'
H=R/'build/ff-joint-combat-hooks-qualified-1030-v1/handoff.json'
S=R/'tools/reference/final_fantasy_host_palette_v2.s'


def rep(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)


def main():
    assert not O.exists()
    files=B.validate(H,'c930c8844047da9a8feeb307f97265991b9a09c74617a237c10c4b5438f0f25f')
    O.mkdir();d=O/'joint';d.mkdir()
    for p in(P/'joint').rglob('*'):
        if p.is_file()and p.suffix in['.s','.inc','.cfg','.chr','.bin']:
            q=d/p.relative_to(P/'joint');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    (d/'ff-palette.s').write_bytes(S.read_bytes())
    v=(d/'veneers.s').read_text()
    v='.import FwForceColors,FwPaletteTick,FwSvcWorldPalette\n'+v
    v=rep(v,'; 26 Colors typed_source_gate_only\n jmp FwPalettePointer',
          '; 26 Colors actual_native_queue_compositor\n jmp FwForceColors')
    v=rep(v,'; 29 UI explicit_unimplemented_reject\n jmp FwServiceUnavailable',
          '; 29 UI cached_body_palette_tick\n jmp FwPaletteTick')
    v=rep(v,'; 32 WorldPalette explicit_unimplemented_reject\n jmp FwServiceUnavailable',
          '; 32 WorldPalette genuine_native_area_donor\n jmp FwSvcWorldPalette')
    B.write(d/'veneers.s',v)
    entry=(d/'entrypoint.s').read_text()
    # Only genuine definitions are exported; never stale DBG numeric aliases.
    names=[]
    for m in re.finditer(r'^\.import (.+)$',S.read_text(),re.M):
        names +=[n.strip()for n in m[1].split(',')if not n.strip().startswith(('Fw','Ff','Hu'))]
    for n in sorted(set(names)):
        if not re.search(r'^\.export(?:zp)? [^\n]*\b'+re.escape(n)+r'\b',entry,re.M):entry+='\n.export '+n
    B.write(d/'entrypoint.s',entry+'\n')
    cfg=(d/'private.cfg').read_text()
    cfg=rep(cfg,(P/'joint/ram3.bin').as_posix(),(d/'ram3.bin').as_posix())
    cfg=rep(cfg,'FF_DRAW_BRIDGE:load=X5_NEW_3E,type=ro,start=$b31c;',
        'FF_DRAW_BRIDGE:load=X5_NEW_3E,type=ro,start=$b31c;\nFF_PALETTE_BRIDGE:load=X5_NEW_3E,type=ro,start=$b336;')
    cfg=rep(cfg,'FF_SERVICE_ADAPTERS:load=X5_NEW_3E,type=ro,start=$b46e;',
        'FF_SERVICE_ADAPTERS:load=X5_NEW_3E,type=ro,start=$b46e;\nFF_WORLD_PALETTE_BRIDGE:load=X5_NEW_3E,type=ro,start=$b67d;')
    cfg=rep(cfg,'FINAL_FANTASY_ART:load=FF_ART_MEM,type=ro;',
        'FINAL_FANTASY_ART:load=FF_ART_MEM,type=ro;\nFF_HOST_PALETTE_C:load=FF_ART_MEM,type=ro;')
    B.write(d/'private.cfg',cfg)
    before,after=str(P/'joint'),str(d)
    for phase in sorted((P/'joint').glob('*-build.json')):
        B.run(d,[v.replace(before,after)for v in json.loads(phase.read_text())['command']],phase.stem)
    B.run(d,[str(R/'tools/Windows/cc65/bin/ca65.exe'),'-g','--cpu','6502x','-I',str(d),
        '--create-full-dep',str(d/'ff-palette.dep'),'-o',str(d/'ff-palette.o'),str(d/'ff-palette.s')],'ff-palette-build')
    cmd=[v.replace(before,after)for v in json.loads((P/'joint/final-link.json').read_text())['command']]+[str(d/'ff-palette.o')]
    B.run(d,cmd,'final-link');prepare(R,d/'candidate.nes')
    new=qualified(d/'candidate.nes');old=qualified(P/'joint/candidate.nes')
    assert(d/'ram3.bin').read_bytes()==(P/'joint/ram3.bin').read_bytes(),'Body palette must not change the RAM3 code/cache/cookie'
    assert(d/'ff-cookie.bin').read_bytes()==(P/'joint/ff-cookie.bin').read_bytes()
    assert address(new,'FfHostPaletteAEnd')<=0xb400
    assert address(new,'FwSvcWorldPalette')==0xb67d
    span=address(new,'FwSvcWorldPaletteEnd')-address(new,'FwSvcWorldPalette')
    assert span==14
    at=location(old,'HuNativeWorldPalette');fp=location(new,'FwSvcWorldPalette')
    assert new['raw'][fp:fp+span]==old['raw'][at:at+span],'World donor arithmetic differs from genuine native source body'
    assert address(new,'FfHostPaletteCEnd')<=0xe000
    moved={n:[address(old,n),address(new,n)]for n,s in old['syms'].items()
           if 'seg'in s and '::'not in n and address(old,n)!=address(new,n)}
    assert not moved,moved
    allowed=[(location(new,'FfHostPaletteAStart'),location(new,'FfHostPaletteAEnd'),'own_A62_alignment'),
       (location(new,'FwSvcWorldPalette'),location(new,'FwSvcWorldPaletteEnd'),'own_A62_native_world_tail'),
       (location(new,'FfHostPaletteCStart'),location(new,'FfHostPaletteCEnd'),'own_ART93_tail')]
    for a,z,n in allowed:
        assert old['raw'][a:z]==bytes([255])*(z-a),(n,'not verified FF owned filler')
    for i,target in[(26,'FwForceColors'),(29,'FwPaletteTick'),(32,'FwSvcWorldPalette')]:
        at=location(old,'FwServiceVeneers')+i*3
        assert old['raw'][at]==new['raw'][at]==0x4c
        assert int.from_bytes(new['raw'][at+1:at+3],'little')==address(new,target)
        allowed.append((at+1,at+3,'own_existing_veneer'+str(i)))
    diffs=[i for i,(a,z)in enumerate(zip(old['raw'],new['raw']))if a!=z]
    outside=[i for i in diffs if not any(a<=i<z for a,z,n in allowed)]
    assert not outside,outside[:24]
    for dep in d.rglob('*.dep'):files.update(dependencies(dep))
    files.update(p for p in O.rglob('*')if p.is_file());files|={Path(__file__),S}
    files.update(Path(v)for v in cmd if v.endswith('.o'))
    B.save(O/'source-closure.json',dict(passed=True,native=False,admitted=False,
        candidate_sha256=B.sha(d/'candidate.nes'),parent_sha256=B.sha(P/'joint/candidate.nes'),changed_bytes=len(diffs),
        own_A_bridge_bytes=address(new,'FfHostPaletteAEnd')-address(new,'FfHostPaletteAStart'),
        own_C_bridge_bytes=address(new,'FfHostPaletteCEnd')-address(new,'FfHostPaletteCStart'),allowed_ranges=allowed,
        all_existing_public_PCs_exact=True,all_header_CHR_RAM3_cookie_common_gameplay_exact=True,
        palette_roles=dict(body=0,world_mushrooms=2,world_area=3),
        limits=['Source only; actual nativequeue/NMI/Main/coldmenu controls pending.',
           'FF projectile palette allocation and optionalblack ink remain separate; this packet claims only body/world ownership.',
           'Actual sharedpostBG/audio/selectable readiness and native1-1/earnedprogression remain open.'],
        bindings={str(p.resolve()):B.sha(p)for p in sorted(files)}))
    print('FF BODY PALETTE SOURCE',B.sha(d/'candidate.nes'),flush=True)


if __name__=='__main__':main()
