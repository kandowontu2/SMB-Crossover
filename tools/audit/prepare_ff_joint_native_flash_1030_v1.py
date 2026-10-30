"""Wire FF native enemy flash using only the existing90B renderer island."""
from pathlib import Path
import difflib,json,re,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
from prepare_ff_current_component_v2 import qualified
from finalize_ff_current_component_v3 import dependencies
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/ff-joint-body-palette-1030-v2'
O=R/'build/ff-joint-native-flash-1030-v1'
H=R/'build/ff-joint-body-palette-qualified-1030-v1/handoff.json'
S=R/'tools/reference/final_fantasy_host_palette_v3.s'


def rep(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)


def main():
    assert not O.exists()
    files=B.validate(H,'3a02596a1393a52e624ac68af20cf00624a94e28049ab4cb8e62ad47b5624913')
    O.mkdir();d=O/'joint';d.mkdir()
    for p in(P/'joint').rglob('*'):
        if p.is_file()and p.suffix in['.s','.inc','.cfg','.chr','.bin']:
            q=d/p.relative_to(P/'joint');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    (d/'ff-palette.s').write_bytes(S.read_bytes())
    src=d/'src/metasprite_engine.s';s=src.read_text()
    old='''::SamusFreezeDrawAll:
  lda SmFreezeRenderState
  beq NativeDraw
  jsr DrawAllMetasprites
  farcall SamusFreezeRenderFinish, jmp
NativeDraw:
  jmp DrawAllMetasprites
::SamusFreezeFlashOwner:
'''
    new='''::SamusFreezeDrawAll:
  farcall FwNativeDrawAll, jmp
::FwNativeFlashProbe:
  cmp #22
  beq NativeFlash
  jmp SamusFreezeFlashOwner
  .res 4,$ea
::SamusFreezeFlashOwner:
'''
    s=rep(s,old,new)
    s=rep(s,'  jmp SamusFreezeFlashOwner\n  nop','  jmp FwNativeFlashProbe\n  nop')
    B.write(src,'.import FwNativeDrawAll\n'+s)
    entry=(d/'entrypoint.s').read_text()
    for n in['DrawAllMetasprites','SmFreezeRenderState','SamusFreezeRenderFinish']:
        if not re.search(r'^\.export(?:zp)? [^\n]*\b'+n+r'\b',entry,re.M):entry+='\n.export '+n
    B.write(d/'entrypoint.s',entry+'\n')
    cfg=(d/'private.cfg').read_text()
    cfg=rep(cfg,(P/'joint/ram3.bin').as_posix(),(d/'ram3.bin').as_posix())
    cfg=rep(cfg,'FF_PALETTE_BRIDGE:load=X5_NEW_3E,type=ro,start=$b336;',
            'FF_PALETTE_BRIDGE:load=X5_NEW_3E,type=ro,start=$b336;\nFF_NATIVE_DRAW_BRIDGE:load=X5_NEW_3E,type=ro,start=$b3c5;')
    B.write(d/'private.cfg',cfg)
    before,after=str(P/'joint'),str(d)
    for phase in sorted((P/'joint').glob('*-build.json')):
        B.run(d,[v.replace(before,after)for v in json.loads(phase.read_text())['command']],phase.stem)
    cmd=[v.replace(before,after)for v in json.loads((P/'joint/final-link.json').read_text())['command']]
    B.run(d,cmd,'final-link');prepare(R,d/'candidate.nes')
    old=qualified(P/'joint/candidate.nes');new=qualified(d/'candidate.nes')
    assert address(new,'FwNativeDrawAll')==0xb3c5
    assert address(new,'FwNativeDrawAllEnd')==0xb400
    assert address(new,'FfHostPaletteAEnd')==address(new,'FwNativeDrawAll')
    assert(d/'ram3.bin').read_bytes()==(P/'joint/ram3.bin').read_bytes()
    assert(d/'ff-cookie.bin').read_bytes()==(P/'joint/ff-cookie.bin').read_bytes()
    moved={n:[address(old,n),address(new,n)]for n,v in old['syms'].items()
           if 'seg'in v and'::'not in n and n in new['syms']and address(old,n)!=address(new,n)}
    allowed_moved={'FwPaletteHaveMode','FwPaletteMapC','FwPaletteForeign','FwPaletteRestore','FfHostPaletteAEnd'}
    assert not(set(moved)-allowed_moved),moved
    for n in['SamusFreezeDrawAll','SamusFreezeFlashOwner','HuMaaRenderLegacy','DrawBrickDebris::PositionReady',
             'DrawAllMetasprites','SmFreezeNativeFlashEnemy','SmFreezeNativeFlashDone']:
        assert address(new,n)==address(old,n),n
    ranges=[(location(new,'SamusFreezeDrawAll'),location(new,'SamusFreezeFlashOwner'),'own_existing29B_drawall_island'),
            (location(new,'FfHostPaletteAStart'),location(new,'FwNativeDrawAllEnd'),'own_existing202B_palette_alignment')]
    at=location(old,'DrawMetasprite')
    needle=bytes([0x4c,address(old,'SamusFreezeFlashOwner')&255,address(old,'SamusFreezeFlashOwner')>>8,0xea])
    positions=[i for i in range(at,at+1300)if old['raw'][i:i+4]==needle];assert len(positions)==1,positions
    hook=positions[0];assert new['raw'][hook]==0x4c
    assert int.from_bytes(new['raw'][hook+1:hook+3],'little')==address(new,'FwNativeFlashProbe')
    ranges.append((hook+1,hook+3,'existing_native_flash_probe_operand'))
    diff=[i for i,(a,z)in enumerate(zip(old['raw'],new['raw']))if a!=z]
    assert not[i for i in diff if not any(a<=i<z for a,z,n in ranges)]
    patch=[]
    for n in['src/metasprite_engine.s','entrypoint.s','private.cfg','ff-palette.s']:
        patch.extend(difflib.unified_diff((P/'joint'/n).read_text().splitlines(True),(d/n).read_text().splitlines(True),
                     fromfile='parent/joint/'+n,tofile='candidate/joint/'+n))
    B.write(O/'source-hooks.patch',''.join(patch))
    for p in d.rglob('*.dep'):files.update(dependencies(p))
    files.update(p for p in O.rglob('*')if p.is_file());files|={Path(__file__),S}
    files.update(Path(v)for v in cmd if v.endswith('.o'))
    B.save(O/'source-closure.json',dict(passed=True,native=False,admitted=False,
        candidate_sha256=B.sha(d/'candidate.nes'),parent_sha256=B.sha(P/'joint/candidate.nes'),changed_bytes=len(diff),
        native_draw_bridge_bytes=59,palette_bridge_bytes=143,all_existing_native_public_entry_PCs_exact=True,
        all_header_CHR_RAM3_cookie_and_other_ROM_bytes_exact=True,owned_moved_labels=moved,allowed_ranges=ranges,
        limits=['Source only; actual FF flashes and native foreign DrawAll/Samusfreeze/ISR controls pending.',
            'Adds one extra DrawAll fartrip and7CPU per native NPC flash-owner probe; actual cost pending.',
            'FF FX palette allocation,postBG,audio,menu admission,native1-1 and earned upgrades remain open.'],
        bindings={str(p.resolve()):B.sha(p)for p in sorted(files)}))
    print('FF NATIVE FLASH SOURCE',B.sha(d/'candidate.nes'),flush=True)


if __name__=='__main__':main()
