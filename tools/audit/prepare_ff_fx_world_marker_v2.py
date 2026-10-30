"""Actual shared-parent marker, preserving the qualified FF lifecycle leaf."""
from pathlib import Path
import difflib,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_ff_joint_source_v1 as B
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/ff-fx-palette-lifecycle-v8';O=R/'build/ff-fx-world-marker-proposal-v2'
H=P/'handoff.json';S=R/'tools/reference/ff_fx_world_marker_v1.s'

def run(d,cmd,phase):
    B.save(d/(phase+'-validated-outputs.json'),validate(cmd,O,cwd=R));B.run(d,cmd,phase)

def main():
    assert not O.exists()
    files=B.validate(H,'2922f377c941cc3f4c41162acc31d16360298a1df6a2f15dee157cac44b38d32')
    O.mkdir();d=O/'joint';d.mkdir();patch=[]
    for f in(P/'joint').rglob('*'):
        if f.is_file()and f.suffix in['.s','.inc','.cfg','.chr','.bin']:
            q=d/f.relative_to(P/'joint');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(f.read_bytes())
    (d/'ff-world-marker.s').write_bytes(S.read_bytes())
    p=d/'src/metasprite_engine.s';old=p.read_text()
    a='''::FwNativeFlashProbe:
  cmp #22
  beq NativeFlash
  jmp SamusFreezeFlashOwner
  .res 4,$ea
'''
    z='''::FwNativeFlashProbe:
  cmp #22
  bne SamusFreezeFlashOwner
  jsr FfMuxWorldDraw
  rts
  .res 3,$ea
'''
    assert old.count(a)==1;new='.import FfMuxWorldDraw\n'+old.replace(a,z);B.write(p,new)
    patch+=list(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='parent/metasprite_engine.s',tofile='new/metasprite_engine.s'))
    p=d/'src/mmc5.s';old=p.read_text()
    a='(.bank(RcArtStart))|MMC5_PRG_ROM,$ff,(94)|MMC5_PRG_ROM'
    z='(.bank(RcArtStart))|MMC5_PRG_ROM,.lobyte(.bank(FfArtStart)|MMC5_PRG_ROM),(94)|MMC5_PRG_ROM'
    assert old.count(a)==1;new='.import FfArtStart\n'+old.replace(a,z);B.write(p,new)
    patch+=list(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='parent/mmc5.s',tofile='new/mmc5.s'))
    p=d/'entrypoint.s';entry=p.read_text()
    for n in['SmFreezeNativeFlashEnemy','CurrentOAMOffset','RgOamRotation','Sprite_Y_Position','Sprite_Attributes']:entry+='\n.export '+n
    B.write(p,entry+'\n')
    p=d/'private.cfg';cfg=p.read_text().replace((P/'joint').as_posix(),d.as_posix())
    needle='FF_FX_PREFLUSH_C:load=FF_ART_MEM,type=ro;';assert cfg.count(needle)==1
    B.write(p,cfg.replace(needle,needle+'\nFF_FX_WORLD_MARKER:load=FF_ART_MEM,type=ro;'))
    cmd=json.loads((P/'joint/main-build.json').read_text())['command']
    run(d,[v.replace(str(P/'joint'),str(d))for v in cmd],'main-build')
    cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'-g','--cpu','6502x','--create-full-dep',str(d/'ff-world-marker.dep'),'-o',str(d/'ff-world-marker.o'),str(d/'ff-world-marker.s')]
    run(d,cmd,'world-marker-build')
    cmd=json.loads((P/'joint/final-link.json').read_text())['command']
    cmd=[v.replace(str(P/'joint/candidate'),str(d/'candidate')).replace(str(P/'joint/private.cfg'),str(d/'private.cfg')).replace(str(P/'joint/main.o'),str(d/'main.o'))for v in cmd]+[str(d/'ff-world-marker.o')]
    run(d,cmd,'final-link');prepare(R,d/'candidate.nes')
    old=qualified(P/'joint/candidate.nes');new=qualified(d/'candidate.nes')
    for n in['FwMuxMenuResolve','FwMuxScene','FwMuxMenuA','FwMuxSceneA','FwPalettePreflush','FwPalettePreflushEnd',
        'FwNativeFlashProbe','SamusFreezeFlashOwner','SmFreezeNativeFlashEnemy','DrawAllMetasprites']:
        assert address(new,n)==address(old,n),n
    start=location(new,'FfMuxWorldDraw');end=location(new,'FfMuxWorldDrawEnd')
    assert address(new,'FfMuxWorldDraw')==0xdf76 and address(new,'FfMuxWorldDrawEnd')==0xdff8 and end-start==130
    assert set(old['raw'][start:end])=={255}
    probe=location(new,'FwNativeFlashProbe');row=location(new,'DwResidentGraphicsBanks')+22-6
    ranges=[(start,end,'own130Bworldmarker'),(probe,probe+11,'existing11BFFnativeflashprobe'),(row,row+1,'qualifiedraw22C93selector')]
    diff=[i for i,(a,z)in enumerate(zip(old['raw'],new['raw']))if a!=z]
    assert all(any(a<=i<z for a,z,n in ranges)for i in diff)
    for n in['ram3.bin','ff-stream.bin','ff-cookie.bin']:
        assert(d/n).read_bytes()==(P/'joint'/n).read_bytes()
    files|={Path(__file__),S,R/'tools/audit/private_build_outputs_v1.py',R/'build/ff-graphics-bank-proposal-v2/handoff.json'}
    files|={Path(v)for v in cmd if v.endswith('.o')}|{f for f in O.rglob('*')if f.is_file()}
    B.write(O/'source.patch',''.join(patch))
    B.save(O/'source-closure.json',dict(passed=True,native=False,admitted=False,metadata_only=True,scheduler=False,
        candidate_sha256=B.sha(d/'candidate.nes'),parent_sha256=B.sha(P/'joint/candidate.nes'),marker_bytes=130,
        tail_remaining=8,changed_bytes=len(diff),allowed_ranges=ranges,live_public_PCs_header_CHR_RAM3_cookie_exact=True,
        limits=['Source build only: genuine Main whole-object/ABI/ISR controls remain.','No palette epochs/readiness/native admission.'],
        bindings={str(f.resolve()):B.sha(f)for f in sorted(files)}))
    print(json.dumps(dict(passed=True,ROM=B.sha(d/'candidate.nes'),marker_bytes=130,remaining=8,changed_bytes=len(diff))),flush=True)

if __name__=='__main__':main()
