"""Observe Prince's camera at native publication and verify intermediate stores."""

import argparse
from pathlib import Path
import sys

from prepare_prince_camera_framing_native_1110 import PIN, R, SYMBOLS, checked, once, read
from prepare_prince_camera_framing_native_1110_v3 import OUT as PRIOR, ROM
from prepare_selected_native_packet_v1 import prepare, sha


OUT = R / 'build/prince-camera-framing-v4-native-1110'
PINS = {
    PRIOR / 'opening/ready.json': 'fae3dcb224c13b583a8dd8cb77e318298af0c1d1280f0b10db15e09a9e647fd8',
    PRIOR / 'opening/capture/binding.json': 'b92101c668d682af1ecc97107a0157965df034e4367a573d2a7d159c31096e39',
    PRIOR / 'opening/capture/camera-framing.json': '9d4c631c164f0ad43eb9f944614024d2baa9cf3defb0be3e4b499257ddb2296e',
    PRIOR / 'full11/ready.json': '244740144261a3bd26801e4ca41b8550e542648677dccb8c54cc6aecf48a6556',
    PRIOR / 'full11/controller.lua': '4261274d5bc921f9c2c007b5b5bea67a12bbd059412885fd553f29ccfd52080e',
    PRIOR / 'full11/capture/binding.json': 'cc625793325e6d35dd68447cca673418375f10c1785faf10e932d59b81ef3974',
    PRIOR / 'full11/capture/prince-diagnostic.json': '60497d242715d4c14b84b83d2738101e107db14509f1ffc0874d0b5a7e2090f4',
}


PUBLICATION = r'''
local cameraEdgeWindow
camera.edge_writes=0;camera.partial_samples=0;camera.edge_examples={};camera.committed_samples=0

local function physicalPC(pc,offset,signature,visit)
 emu.addMemoryCallback(function()
  if phase~='controls' or not sourceActive() or r('GameEngineSubroutine')~=8 then return end
  local mapped=emu.convertAddress(pc)
  if not mapped or mapped.memType~=emu.memType.nesPrgRom or mapped.address~=offset then return end
  equal(bytes(pc,#signature),signature,'Actual Prince camera publication opcode')
  visit()
 end,emu.callbackType.exec,pc)
end

local function checkEdge(ok,why,detail)
 if ok then return end
 camera.edge_failure=detail
 cameraWrite(false,why);require(false,why)
end

physicalPC(0xaa08,0x2a08,{0x98,0x8d,0x76,0x07,0x18,0x6d,0x40,0x07},function()
 local left,right=currentEdges()
 local step=emu.getState()['cpu.y']
 local p={native_main=camera.game_loops,Main=admitted,frame=frame,left=left,right=right,
  step=step,final_left=(left+step)&0xffff,partial={}}
 p.final_right=(p.final_left+255)&0xffff
 checkEdge(not cameraEdgeWindow and ((right-left)&0xffff)==255,
  'Native scroll starts with a complete camera edge pair',p)
 cameraEdgeWindow=p
end)

physicalPC(0xaa37,0x2a37,{0x4c,0x3f,0xaa},function()
 local p=cameraEdgeWindow
 local left,right=currentEdges()
 checkEdge(p and p.native_main==camera.game_loops and p.Main==admitted
   and left==p.final_left and right==p.final_right,
  'Native ScrollScreen returns with the exact new camera edge pair',
  {window=p,left=left,right=right,Main=admitted,frame=frame})
 cameraEdgeWindow=nil;camera.edge_writes=camera.edge_writes+1
 if #p.partial>0 and #camera.edge_examples<16 then
  p.completed={left=left,right=right,frame=frame};camera.edge_examples[#camera.edge_examples+1]=p
 end
end)

physicalPC(0x8350,0xfc350,{0xa9,0x00,0x4c,0x56,0x83},function()
 local left,right=currentEdges()
 checkEdge(not cameraEdgeWindow and ((right-left)&0xffff)==255,
  'Native GameLoop commits a complete camera edge pair',
  {window=cameraEdgeWindow,left=left,right=right,Main=admitted,frame=frame})
 camera.committed_samples=camera.committed_samples+1
 cameraSample()
end)

local function cameraCheckPhysicalFrame()
 if not sourceActive() or r('GameEngineSubroutine')~=8 then return end
 local left,right=currentEdges()
 if ((right-left)&0xffff)==255 then return end
 local p=cameraEdgeWindow
 local q={frame=frame,Main=admitted,PC=emu.getState()['cpu.pc'],left=left,right=right,
  native_main=camera.game_loops,nmi_disable=r('NmiDisable')}
 local legal=false
 if p and p.native_main==camera.game_loops and p.Main==admitted and q.nmi_disable==255 then
  local leftLow=(p.left&0xff00)|(p.final_left&0xff)
  local rightLow=(p.right&0xff00)|(p.final_right&0xff)
  legal=(left==leftLow and right==p.right)
     or (left==p.final_left and (right==p.right or right==rightLow))
 end
 checkEdge(legal,'Unequal camera edges outside the actual native publication sequence',{window=p,sample=q})
 camera.partial_samples=camera.partial_samples+1
 if #p.partial<4 then p.partial[#p.partial+1]=q end
end
'''


def validate():
    opening, full = PRIOR / 'opening/capture', PRIOR / 'full11/capture'
    passed, positive = map(read, (opening / 'camera-framing.json', opening / 'binding.json'))
    failed, negative = map(read, (full / 'prince-diagnostic.json', full / 'binding.json'))
    assert all(q['ROM_sha256'] == PIN for q in (passed, positive, failed, negative))
    assert positive['ready_sha256'] == PINS[PRIOR / 'opening/ready.json'] and positive['exit_code'] == 0
    assert negative['ready_sha256'] == PINS[PRIOR / 'full11/ready.json'] and negative['exit_code'] != 0
    assert passed['passed'] and passed['camera']['steady']['count'] == 18
    assert failed['reason'] == 'Actual camera right equals left plus 255'
    assert failed['first_pipe_route']['first_pipe_cleared'] and not failed['passed']
    assert (failed['admitted_phase_commits'], failed['state']['world_x'], failed['state']['HP']) == (590, 581, 5)


def controller(path):
    text = path.read_text(encoding='utf-8')
    anchor = 'local function completeCameraOpening(finish)'
    text = once(text, anchor, PUBLICATION + '\n' + anchor)
    text = once(text, 'local function controls_tick(finish)\n cameraSample()',
                'local function controls_tick(finish)\n cameraCheckPhysicalFrame()')
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
    validate()
    assert sha(ROM) == PIN
    prior = PRIOR / 'full11'
    ready = read(prior / 'ready.json')
    assert ready['ROM_sha256'] == PIN and not ready['emulated_writes']
    bindings = checked(ready['bindings'])
    prepare(out, ROM, controller(prior / 'controller.lua'), {Path(__file__), *direct, *bindings},
            expected=PIN, timeout=ready['timeout'], allow_interactive=ready['allow_interactive'], rom_symbols=SYMBOLS,
            scope=ready['scope'] + ' Check camera edges at exact native ScrollScreen return and GameLoop publication. '
            'Physical frame observations must match the legal partial-store sequence. Same inputs.')
    assert (out / 'run.py').read_bytes() == (prior / 'run.py').read_bytes()
    assert {path.name for path in out.iterdir()} == {'ready.json', 'controller.lua', 'run.py'}


if __name__ == '__main__':
    main()
