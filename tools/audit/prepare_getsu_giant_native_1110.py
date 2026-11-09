"""Stage a controller-only Getsu idle or full-route replay against a qualified ROM."""

import argparse
from pathlib import Path

import check_getsu_giant_rebase_1110 as Rebase
import prepare_getsu_fuma_native_1110 as Native
from prepare_selected_native_packet_v1 import prepare, sha


def replace_once(source, before, after):
    assert source.count(before) == 1, before
    return source.replace(before, after, 1)


def idle_observer(source):
    source = replace_once(source, 'local controllerRead = false', '''local controllerRead = false
local idleStart, idleLastUpdate, idleWithoutMain = nil, 0, 0''')
    source = replace_once(source, 'active_frames=activeFrames,missed_reads=missedReads}', '''active_frames=activeFrames,missed_reads=missedReads,
   idle_start=idleStart,idle_without_main=idleWithoutMain,
   idle_main_updates=idleStart and updates-idleStart.updates or nil}''')
    source = replace_once(source, '  input=started and {right=true} or {};return', '''  if started then return finish(false,'left active idle state') end
  input={};return''')
    start = ' lastX=math.max(lastX,x)\n if firstAttack'
    end = 'end,emu.eventType.endFrame)'
    assert source.count(start) == source.count(end) == 1
    return source[:source.index(start)] + ''' lastX=math.max(lastX,x)
 input={}
 if not idleStart then
  if not (exterior and liveRender) then
   if activeFrames>=90 then return finish(false,'idle body or presentation never appeared') end
   return
  end
  idleStart=state()
  idleLastUpdate=updates
  activeFrames,missedReads=0,0
 else
  if updates==idleLastUpdate then idleWithoutMain=idleWithoutMain+1 end
  idleLastUpdate=updates
  if x~=idleStart.x or y~=idleStart.y or cameraX()~=idleStart.camera then
   return finish(false,'neutral input moved player or camera')
  end
 end
 if activeFrames==120 then
  return finish(updates>idleStart.updates,'120 neutral active frames')
 end
''' + source[source.index(end):]


def stage_packet(out, rom, source_proof, mode):
    proof = Rebase.O.Page.load_json(source_proof)
    parent = Rebase.BASE.read_bytes()
    assert Rebase.SHA(parent) == proof['parent_SHA256'] == Rebase.PIN
    assert proof['passed'] and proof['renderer_installed'] and proof['native_HUD']
    for path, digest in proof['bindings'].items():
        assert sha(Rebase.R / path) == digest, path
    raw = rom.read_bytes()
    digest = proof['expected_memory_only_SHA256']
    assert Rebase.SHA(raw) == digest
    assert Rebase.Getsu.install(parent, proof['patches']) == raw
    assert proof['public_vector_rows']['2'] == 0xa4be
    render_proof = Rebase.R / 'build/getsu-host-render-1110-v3/proof.json'
    rendering = Rebase.O.Page.load_json(render_proof)
    assert rendering['passed'] and rendering['draw_address'] == 0xa4be
    atlas = Native.Render.ART / 'atlas.chr'
    start = Rebase.O.Page.CHR + 990 * 1024
    art, code = raw[start:start + 1024], raw[start + 1024:start + 3072]
    assert art == atlas.read_bytes() and Rebase.SHA(code) == proof['kernel_SHA256']
    assert code[6:9] == bytes.fromhex('4cbea4')
    assert bytes.fromhex(proof['cookie']) == bytes((0xa7, 42, 1)) + bytes.fromhex(Rebase.SHA(code + art))[:13]
    b = Rebase.W.bundle(parent)
    for name, bank, pc in (('GameLoop', 126, 0x82d9), ('FlagpoleCollision', 126, 0x9e47)):
        at = Native.location(b, name)
        assert (at - 16) // 8192 == bank and Native.address(b, name) == pc and raw[at:at + 5] == parent[at:at + 5]
    ram = ','.join(f'{n}={Native.address(b, n)}' for n in Native.SYMBOLS)
    atlas_bytes = ','.join(map(str, art))
    config = (f'local C={{rom="{digest}",draw=0xa4be,main=0x82d9,flag=0x9e47,'
              f'tileAttribute={Native.address(b,"MTileAttribute")},presentation=true,'
              f'ram={{{ram}}},atlas={{{atlas_bytes}}}}}\n')
    source = Native.CONTROLLER.read_text(encoding='utf-8')
    if mode == 'idle':
        source = idle_observer(source)
    symbols = Rebase.R / 'build/shared-sparse-draw-native-1110/candidate.nes'
    prepare(out, rom, config + source, {Path(__file__), Path(Native.__file__), Path(Rebase.__file__),
            Native.CONTROLLER, source_proof, render_proof, atlas},
            expected=digest, timeout=180, allow_interactive=True,
            rom_symbols=(symbols.with_suffix('.lbl'), symbols.with_suffix('.dbg')),
            scope='Private Getsu from the actual menu, with native OAM/CHR and HUD. '
            + ('120 active neutral frames with controller polls and native Main counts.' if mode == 'idle'
               else 'Full 1-1 with native sword, four pipes, three gaps and flag into active 1-2.'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--mode', choices=('idle', 'route'), required=True)
    args = parser.parse_args()
    stage_packet(args.output.resolve(), args.rom.resolve(), args.proof.resolve(), args.mode)


if __name__ == '__main__':
    main()
