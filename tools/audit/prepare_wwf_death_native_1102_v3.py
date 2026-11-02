"""Observe the final death-age store even when native life loss runs before DMA."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R, prepare, sha
from prepare_wwf_death_native_1102_v2 import CONTACT

P = R / 'build/wwf-death-1102-v2'
O = P / 'native-v3'
ROM = P / 'candidate.nes'
WATCH = r'''
-- The final INC can switch engine11→6 before endFrame. Observe the real bus
-- store so the final tick is not lost by the end-frame state filter.
emu.addMemoryCallback(function(_,v)
 if phase=='play' and deathSeen and r('GameEngineSubroutine')==11 then
  maxDeathAge=math.max(maxDeathAge,v)
 end
end,emu.callbackType.write,assert(L.MmDeathAge))
'''


def main():
    O.mkdir(exist_ok=True)
    refs = [Path(__file__), R / 'tools/audit/prepare_wwf_death_native_1102_v2.py',
            P / 'assembly.json', P / 'CPU.json']
    marker = 'emu.addEventCallback(function()'
    for variant in range(6):
        text = CONTACT.replace('VARIANT_VALUE', str(variant))
        text = text.replace(marker, WATCH + '\n' + marker, 1)
        prepare(O / f'contact-{variant}', ROM, text, refs, expected=sha(ROM),
                timeout=90, allow_interactive=True,
                scope=f'Exact WWF{variant} real contact-death→active1-1 recovery; '
                      'final native death-age store is observed directly, no state writes, one PNG. '
                      'Retains final duration, identity and one-life-loss assertions.')
    source = P / 'pit/controller.lua'
    text = source.read_text(encoding='utf-8').replace(marker, WATCH + '\n' + marker, 1)
    prepare(O / 'pit', ROM, text, refs + [source], expected=sha(ROM),
            timeout=150, allow_interactive=True,
            scope='Exact retained first-pit failure route; real150-tick pit death must recover '
                  'to active1-1 with exactly one life lost. Final tick bus observation, '
                  'no writes, one PNG; not a full-stage clear.')


if __name__ == '__main__':
    main()
