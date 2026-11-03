"""Read-only 6c9e native draw/DMA and original phase/turn diagnostic."""
from pathlib import Path
import hashlib,json,sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit')]
import check_prince_backdrop_native_1103_v160 as C
from prepare_selected_native_packet_v1 import prepare,sha
from prepare_bub_menu_qualification_1102_v2 import lua
import build_storage_guard_v1 as G

O=R/'build/prince-native-followup-1103-v176'
ROM=R/'build/prince-live-root-candidate-1103-v113/prince-live-private.nes'
OLD=R/'build/prince-live-root-controls-1103-v114/native/controller.lua'
EXPECTED='6c9e85a94d34a4623d21789d5293c61af2ad14d214f5780f57613a51ae6bb25a'


def main():
    G.preflight(private_root=O,reserved_bytes=250000,reserved_files=6,fresh=True)
    assert sha(ROM)==EXPECTED
    base,_=C.M.image()
    runtime,meta,state=C.M.B.images()
    raw=ROM.read_bytes()
    hooks={}
    for name,pc in dict(PpPhaseCommit=0xb37c,PpPhase0Call=0xb396,
                        PpAdvanceActor=0xac3f,PpAdvanceReturn=0xb399,
                        PpControls=0xab92,PpControlsReturn=0xb3ac).items():
        hooks[name]=dict(pc=pc,memory='nesWorkRam',physical=3*8192+pc-0xa000,
                         bytes=list(runtime[pc-0xa000:pc-0xa000+4]))
    assert bytes(hooks['PpPhaseCommit']['bytes'])==bytes.fromhex('eea6c029')
    assert bytes(hooks['PpPhase0Call']['bytes'])==bytes.fromhex('203fac20')
    assert bytes(hooks['PpControlsReturn']['bytes'])==bytes.fromhex('4c83c3a9')
    for name,pc,bank in [('DmaComplete',0xe008,127),('MetaspriteRenderLoop',0xa5ba,4)]:
        at=16+bank*8192+(pc&8191)
        hooks[name]=dict(pc=pc,memory='nesPrgRom',physical=at-16,bytes=list(raw[at:at+4]))
    # E008 is after STA4014 and the real LDA Mirror_PPUMASK, before STA2001.
    assert raw[16+127*8192:16+127*8192+11]==bytes.fromhex('a9028d1440ad7a078d0120')
    extra={n:C.I.address(base,n)for n in ['FrameCounter','NmiDisable','ScreenLeft_X_Pos','ScreenLeft_PageLoc','CurrentOAMOffset','GuestOamRotationActive','RgOamRotation']}
    source=OLD.read_text()
    a=source.index('-- Read-only observations and physical controller input; never emulated writes.')
    z=source.index("local log=assert(io.open(OUTPUT..'observations.csv','w'))",a)
    ext=R/'tools/audit/prince_render_turn_1103_v176.lua'
    source=source[:a]+ext.read_text()+'\n'+source[z:]
    # Keep the already-qualified physical menu/handoff template unchanged.
    first,second,body=source.split('\n',2)
    additions='\nfor n,h in pairs('+lua(hooks)+')do Q.hooks[n]=h end\nfor n,a in pairs('+lua(extra)+')do L[n]=a end\nQ.mode="Prince-render-turn176";Q.maxFrames=5000\n'
    controller=first+'\n'+second+additions+body
    for bad in ['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:
        assert bad not in controller,bad
    refs={Path(__file__),ext,OLD,C.O/'backdrop-manifest-v159.json',C.O/'native-labels-v153.json',
          C.O/'native-runtime-v153.bin',C.O/'native-services-v157.s',
          R/'tools/reference/prince_host_lifecycle_1102_v12.s',R/'tools/reference/prince_host_render_1102_v1.s',
          R/'docs/qa/allocations/prince-live-lifetime-1103-v113.json'}
    O.mkdir(exist_ok=True)
    prepare(O/'native',ROM,controller,refs,expected=EXPECTED,timeout=240,allow_interactive=True,
            scope='Read-only unchanged6c9e candidate. Actual menu SelectPrince38; first8 Y176/high1; separate B36E wrapper entries, admitted phase commits, phase0 B396 and original AC3F advances/returns, original AB92 controls. Neutral until actual body draw/return, full256byte hardware DMA and a subsequent full display frame; one hardwareOAM/CHR/palette evidence object and gameplayPNG. Right only until +16px, then bounded original Left until actual worldX reverses below the Left-startX; unchanged lives/HP. No RAM seeds, code/physics changes, jump/fullstage/helper/armed/audio claim. Maximum3PNG and compactCSV/JSON.')
    result=dict(prepared=True,native_run=False,ROM_sha256=EXPECTED,output=str(O/'native'),
                separate_phase_counters=True,strict_reverse_assertion=True,source_changes=False,
                old_v114_negative_preserved=True,PNG_cap=3,additional_cartridges=0,
                bindings={str(p.relative_to(R)):sha(p)for p in refs})
    (O/'preparation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k!='bindings'}))


if __name__=='__main__':main()
