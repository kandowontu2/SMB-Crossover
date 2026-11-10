"""Separate Prince's native camera approach and settled framing observations."""

import argparse
from pathlib import Path
import sys

from prepare_prince_camera_framing_native_1110 import OUT as PRIOR, PIN, R, SYMBOLS, checked, once, read
from prepare_selected_native_packet_v1 import prepare, sha


OUT = R / 'build/prince-camera-framing-v2-native-1110'
ROM = PRIOR / 'prince-private.nes'
PINS = {
    PRIOR / 'opening/ready.json': '924e42b447fad84e00a8eae7fcb4b0eba7c8d96cd964de0a565ebcbad444d63f',
    PRIOR / 'opening/controller.lua': '7e14e46b81f7f1eb60470a37b104cebd55b4fda21f7f740306721862d8c661c3',
    PRIOR / 'opening/capture/binding.json': '2829a0606dbf6e48999ea33276dccec73735fc0450a78d35399601c70216643c',
    PRIOR / 'opening/capture/prince-diagnostic.json': 'dae84afd4efc3ec842d39443503308eb90ffb10a3115cf54db2767f66ca9a1d0',
    PRIOR / 'full11/ready.json': 'c6a60dd39132c059374083184dac1b3a863cb93ec0b55eaa00d8d7a56aa0091f',
    PRIOR / 'full11/controller.lua': '1a695d5db441ad6201ca52a43015d656634c1058feac0b85f055211b6e9e6faf',
}


OPENING_SAMPLES = r''' if not camera.opening_passed and part=='travel' and s.pad&3==1 and s.source_action==1
     and nativeFloor() and left>=16 and s.world_x<256 then
  local first=camera.first_catchup
  local settled=first and left-first.left>=24
  local window=settled and camera.steady or camera.approach
  window.count=window.count+1
  window.min=math.min(window.min,screen);window.max=math.max(window.max,screen)
  if #window.rows<128 then window.rows[#window.rows+1]=q end
 end
 if not camera.opening_passed and s.world_x>=210 and camera.steady.count>=18
     and left>=70 and screen>=112 and screen<=128 and camera.zero_sample_catchups>0 then
  local stable=camera.steady.min>=105 and camera.steady.max<=139
  if not stable then
   cameraWrite(false,'Settled grounded opening is outside the ordinary host follow point')
   require(false,'Settled grounded opening is outside the ordinary host follow point')
  end
  camera.opening_passed=true;camera.opening_terminal=q
 end
'''


def validate_negative():
    capture = PRIOR / 'opening/capture'
    old, binding = map(read, (capture / 'prince-diagnostic.json', capture / 'binding.json'))
    assert old['ROM_sha256'] == binding['ROM_sha256'] == PIN
    assert binding['ready_sha256'] == PINS[PRIOR / 'opening/ready.json'] and binding['exit_code'] != 0
    assert not old['passed'] and old['reason'] == 'Grounded opening stays around the ordinary host follow point'
    assert (old['admitted_phase_commits'], old['state']['world_x'], old['state']['HP'], old['final_lives']) == (138, 224, 5, 2)


def controller(path):
    text = path.read_text(encoding='utf-8')
    text = once(text, ' opening_grounded=0,opening_min=255,opening_max=0,opening_passed=false}',
                ' approach={count=0,min=255,max=0,rows={}},steady={count=0,min=255,max=0,rows={}},opening_passed=false}')
    start = text.index(" if not camera.opening_passed and part=='travel'")
    end = text.index('\nend\n\nlocal function completeCameraOpening', start)
    text = text[:start] + OPENING_SAMPLES.rstrip() + text[end:]
    assert 'emu.write(' not in text and text.count(PIN) == 1
    sys.path.insert(0, str(R / 'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    assert LuaRuntime().eval('function(s) local f,e=load(s); assert(f,e); return true end')(text)
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out == OUT and not out.exists(), out
    direct = checked(PINS)
    validate_negative()
    assert sha(ROM) == PIN
    out.mkdir()
    for name in ('opening', 'full11'):
        prior = PRIOR / name
        ready = read(prior / 'ready.json')
        assert ready['ROM_sha256'] == PIN and not ready['emulated_writes']
        bindings = checked(ready['bindings'])
        prepare(out / name, ROM, controller(prior / 'controller.lua'), {Path(__file__), *direct, *bindings},
                expected=PIN, timeout=ready['timeout'], allow_interactive=ready['allow_interactive'],
                rom_symbols=SYMBOLS, scope=ready['scope'] + ' Separate initial scroll from the settled '
                'window after 24 actual camera pixels beyond first zero-sample correction. Same controller input.')
        assert (out / name / 'run.py').read_bytes() == (prior / 'run.py').read_bytes()
    assert sum(path.is_file() for path in out.rglob('*')) == 6


if __name__ == '__main__':
    main()
