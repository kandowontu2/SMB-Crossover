"""Qualify the minimal native-cold outline observer correction; no gameplay."""
from hashlib import sha256
from pathlib import Path
import check_ff_stdout_controller_source_1110 as C

OLD_SHA = '1e11e26049e82ebe7db046dfc3a18a6e3e5927edb34985aabe325609bec68250'
OLD = C.LUA
C.LUA = C.R / 'tools/playthroughs/ff_full_stage_stdout_1110_v2.lua'
original_runtime = C.runtime


def runtime(*args, **kwargs):
    rt = original_runtime(*args, **kwargs)
    # API mock of actual CharactersInit cold policy, not an emulator RAM write.
    rt.globals().host.mem[0x7eb8] = 1
    return rt


def main():
    assert sha256(OLD.read_bytes()).hexdigest() == OLD_SHA
    expected = OLD.read_text().replace(
        " assert(r('PlayerOutlinesOff')==0,'Mandatory FF shadow disabled')",
        " assert(r('PlayerOutlinesOff')==1,'Natural cold extra-outline option changed')")
    expected = expected.replace(
        '-- Natural controller-only FF route. This source writes no emulated RAM/files.\n',
        '-- Natural controller-only FF route. This source writes no emulated RAM/files.\n'
        '-- v2 observer correction: real CharactersInit sets optional extra outlinesOFF=1.\n'
        '-- Frozen v1 SHA1e11e260... failed at natural frame340 on its false flag==0 assumption.\n'
        '-- This flag controls optional bit32 mask cells; it does not prove source black-pixel fidelity.\n')
    expected = expected.replace(
        "  entrance=r('PlayerEntranceCtrl'), area_type=r('AreaType'), pipe_timer=r('ChangeAreaTimer'),",
        "  entrance=r('PlayerEntranceCtrl'), area_type=r('AreaType'), pipe_timer=r('ChangeAreaTimer'),\n"
        "  optional_outlines_off=r('PlayerOutlinesOff'),")
    assert C.LUA.read_text() == expected
    init = (C.R / 'src/characters.s').read_text()
    assert 'lda #1\n  sta PlayerOutlinesOff        ; Extra black masks are opt-in' in init
    renderer = (C.R / 'src/final_fantasy_render.s').read_text()
    assert 'and #32\n beq Emit\n lda PlayerOutlinesOff\n bne Next' in renderer
    C.runtime = runtime
    C.main()
    assert sha256(OLD.read_bytes()).hexdigest() == OLD_SHA


if __name__ == '__main__':
    main()
