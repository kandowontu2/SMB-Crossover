"""Pair Prince's camera callbacks by native GameLoop and source epoch."""

import argparse
from pathlib import Path
import sys

from prepare_prince_camera_framing_native_1110 import PIN, R, SYMBOLS, checked, once, read
from prepare_prince_camera_framing_native_1110_v2 import OUT as PRIOR, ROM
from prepare_selected_native_packet_v1 import prepare, sha


OUT = R / 'build/prince-camera-framing-v3-native-1110'
PINS = {
    PRIOR / 'opening/ready.json': 'a0d6b9a9f675189d59e06b3bf67a4bebd0b3ac7ab811ca8fe2cca93b4077bb38',
    PRIOR / 'opening/controller.lua': '7eb5e9a8ba75bb1dd4c2b7c734801eb938da3c7aaa9b253ecc188582f2d16522',
    PRIOR / 'opening/capture/binding.json': '4b916e5ddb18f1923c4f22fa4864d2ac81699f2e88cffe0ad9fda5103e5e47d9',
    PRIOR / 'opening/capture/camera-framing.json': '21a6c02a0493870cb3035f4b88d6b4a8da38fe64332a0346351d3ac1caa1a05e',
    PRIOR / 'opening/capture/prince-diagnostic.json': '09e3b2156f1f2f3ce165716d96c3c0bb5f2db525a08f292492f66c0acdd54377',
    PRIOR / 'full11/ready.json': 'a1d04ff27740457752777d02ded669309ba99a18bb0dd276362328c0fea8341c',
    PRIOR / 'full11/controller.lua': '4446ffbd2ffee31b7dd18f880192be7b5a328822f81838e6e0e3a37b8b060ee3',
}


CALLBACKS = r'''
emu.addMemoryCallback(function()
 if phase~='controls' then return end
 local mapped=emu.convertAddress(0x82d9)
 if not mapped or mapped.memType~=emu.memType.nesPrgRom or mapped.address~=0xfc2d9 then return end
 equal(bytes(0x82d9,8),{0xa9,0xff,0x8d,0x39,0x01,0x20,0x56,0x83},'Actual native GameLoop entry')
 camera.game_loops=camera.game_loops+1
 if cameraPending then
  camera.workers_without_scroll=camera.workers_without_scroll+1
  cameraPending=nil
 end
end,emu.callbackType.exec,0x82d9)

emu.addMemoryCallback(function()
 if phase~='controls' or not sourceActive() or r('GameEngineSubroutine')~=8 then return end
 local mapped=emu.convertAddress(0xd622)
 if not mapped or mapped.memType~=emu.memType.nesWorkRam or mapped.address~=0x5622 then return end
 equal(bytes(0xd622,9),{0xad,0x26,0x07,0x0d,0x82,0x07,0x0d,0x65,0x05},'Cold-loaded Prince camera worker')
 require(camera.game_loops>0 and not cameraPending,'At most one Prince camera worker per actual GameLoop')
 local left,right=currentEdges()
 camera.worker_calls=camera.worker_calls+1
 cameraPending={frame=frame,Main=admitted,native_main=camera.game_loops,
  source_updates=sourceUpdates,source_ticks=sourceTicks,source_epoch=ps(0xa9),
  native_frame=r('FrameCounter'),owner=r('SelectedCharacter'),world_x=wx(),left=left,right=right,
  source_x=ps(0x60f)+256*ps(0x610),sample=ram(0x701)}
end,emu.callbackType.exec,0xd622)

emu.addMemoryCallback(function()
 local p=cameraPending
 if not p then return end
 local mapped=emu.convertAddress(0xa9d4)
 if not mapped or mapped.memType~=emu.memType.nesPrgRom or mapped.address~=0x29d4 then return end
 equal(bytes(0xa9d4,10),{0xad,0x01,0x07,0x18,0x6d,0x65,0x05,0x8d,0x01,0x07},'Native scroll ingress')
 cameraPending=nil
 if not sourceActive() or r('SelectedCharacter')~=p.owner or r('GameEngineSubroutine')~=8 then
  camera.workers_without_scroll=camera.workers_without_scroll+1
  return
 end
 require(p.native_main==camera.game_loops and p.Main==admitted and p.source_updates==sourceUpdates
  and p.source_ticks==sourceTicks and p.source_epoch==ps(0xa9) and p.native_frame==r('FrameCounter'),
  'Camera worker and scroll belong to one actual native and donor update')
 local left,right=currentEdges()
 require(left==p.left and right==p.right and wx()==p.world_x and ps(0x60f)+256*ps(0x610)==p.source_x,
  'Camera sample leaves world position and viewport unchanged before native ScrollHandler')
 camera.native_calls=camera.native_calls+1
 local span=frame-p.frame
 camera.max_physical_frame_span=math.max(camera.max_physical_frame_span,span)
 if span>0 then camera.cross_frame_pairs=camera.cross_frame_pairs+1 end
 local sample=ram(0x701)
 if p.sample==0 and sample>0 and sample<=5 then
  camera.zero_sample_catchups=camera.zero_sample_catchups+1
  if span>0 then camera.cross_frame_catchups=camera.cross_frame_catchups+1 end
  if not camera.first_catchup then
   p.published=sample;p.scroll_frame=frame;p.screen_x=(p.world_x-left)&0xffff;camera.first_catchup=p
  end
 end
end,emu.callbackType.exec,0xa9d4)
'''


def validate_negative():
    capture = PRIOR / 'opening/capture'
    old, binding, diag = map(read, (capture / 'camera-framing.json', capture / 'binding.json', capture / 'prince-diagnostic.json'))
    assert old['ROM_sha256'] == diag['ROM_sha256'] == binding['ROM_sha256'] == PIN
    assert binding['ready_sha256'] == PINS[PRIOR / 'opening/ready.json'] and binding['exit_code'] != 0
    assert not old['passed'] and not diag['passed'] and old['Main'] == 217 and old['state']['HP'] == 5
    camera = old['camera']
    assert (camera['worker_calls'], camera['native_calls'], camera['steady']['count']) == (217, 186, 0)
    first = camera['first_catchup']
    assert (first['Main'], first['world_x'], first['left']) == (138, 224, 101)
    early = [row for row in camera['approach']['rows'] if 182 <= row['world_x'] <= 224]
    assert min(row['screen_x'] for row in early) == 119 and max(row['screen_x'] for row in early) == 124


def controller(path):
    text = path.read_text(encoding='utf-8')
    text = once(text, 'local camera={worker_calls=0,native_calls=0,zero_sample_catchups=0,rows={},',
                'local camera={worker_calls=0,native_calls=0,zero_sample_catchups=0,rows={},\n'
                ' game_loops=0,workers_without_scroll=0,cross_frame_pairs=0,cross_frame_catchups=0,max_physical_frame_span=0,')
    anchor = 'local cameraPending,cameraLast,cameraWrite'
    start = text.index(anchor) + len(anchor)
    end = text.index('cameraWrite=function(ok,why)', start)
    text = text[:start] + '\n' + CALLBACKS + '\n' + text[end:]
    assert 'p.frame~=frame' not in text and 'emu.write(' not in text and text.count(PIN) == 1
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
                rom_symbols=SYMBOLS, scope=ready['scope'] + ' Pair the camera worker with ScrollHandler in the same '
                'actual GameLoop and authenticated source update, including lag across physical frames.')
        assert (out / name / 'run.py').read_bytes() == (prior / 'run.py').read_bytes()
    assert sum(path.is_file() for path in out.rglob('*')) == 6


if __name__ == '__main__':
    main()
