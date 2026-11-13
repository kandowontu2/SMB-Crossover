"""Prepare one hash-bound Karnov Mesen controller for the root queue."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import zipfile

from check_metal_flower_1112 import Host
from check_hogan_current_bounded_v1 import address
from run_stdout_mesen_1110 import R, run

STAGE_PACKET = R / 'docs/qa/checkpoints/2026-11-02/karnov-full11-v6/inputs.zip'
STAGE_PACKET_SHA = '776b98638773c91cfe9e9554959f29523469d090aba1c03d71bcfb3a818742cf'
STAGE_MEMBER = 'build/karnov-crouch-route-1102-v1/native-stair/controller.lua'
STAGE_SHA = '8729472aa6af71c2e2a38054f865ff6dcf54f2e1b6ce3a02d039eb1f57730483'
FIXTURE = R / 'tools/reference/karnov_bomb_fixture_1112.lua'


def stage_source():
    assert sha256(STAGE_PACKET.read_bytes()).hexdigest() == STAGE_PACKET_SHA
    with zipfile.ZipFile(STAGE_PACKET) as archive:
        source = archive.read(STAGE_MEMBER)
    assert sha256(source).hexdigest() == STAGE_SHA
    text = source.decode().splitlines()
    text = '\n'.join(line for line in text if not line.startswith((
        'local trace=assert(io.open', 'local function shot(', '  if gameFrames%10==0 then trace:write')))
    text = text.replace(";shot('karnov-selected');", ';')
    first = text.index("   trace:close();shot('stage-endpoint')")
    last = text.index('\n  end', first)
    text = text[:first] + '''   print('SMB_NATIVE_RECEIPT '..string.format(
    '{"passed":%s,"ROM_SHA256":"%s","stage_complete":%s,"died":%s,"max_world_x":%d,"game_frames":%d,"lives":%d,"controller_only":true}',
    tostring(won),ROM_SHA,tostring(won),tostring(dead),maxX,gameFrames,r('NumberofLives')))
   done=true;emu.stop(won and 0 or 1)''' + text[last:]
    assert 'io.open' not in text and 'emu.write' not in text and 'takeScreenshot' not in text
    return 'local L={}\n' + text + '\n'


def controller(raw, mode):
    digest = sha256(raw).hexdigest()
    if mode == 'stage':
        text = stage_source()
    else:
        names = ('CurrentBank', 'CurrentBankC', 'CrossoverMenuState', 'CrossoverMenuIndex',
                 'SelectedCharacter', 'GameEngineSubroutine', 'OperMode_Task', 'NumberofLives',
                 'FrameCounter', 'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position',
                 'Player_State', 'Enemy_X_Position', 'Enemy_PageLoc', 'Enemy_Y_Position',
                 'Enemy_State', 'Enemy_Flag', 'Enemy_ID', 'ScreenLeft_X_Pos', 'ScreenLeft_PageLoc',
                 'ObjectOffset', 'HandleEnemyFBallCol', 'AreaType')
        bundle = Host.C.Start.W.bundle(raw)
        table = 'local L={' + ','.join(f'{name}={address(bundle,name)}' for name in names) + '}\n'
        contact_tail = raw[1048592+1019*1024+0x479:1048592+1019*1024+0x497]
        contact = b'\x20' + address(bundle, 'HandleEnemyFBallCol').to_bytes(2, 'little')
        assert contact_tail.count(contact) == 1
        return_address = 0xcd79 + contact_tail.index(contact) + 2
        text = table + f'local BOMB_CONTACT_RETURN={return_address}\n' + FIXTURE.read_text(encoding='utf-8')
    return f'local ROM_SHA="{digest}"\n' + text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('stage', 'fixture'), required=True)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--run-stage', action='store_true')
    args = parser.parse_args()
    raw = args.rom.read_bytes()
    script = args.output / 'controller.lua'
    script.parent.mkdir(parents=True, exist_ok=True)
    assert not script.exists(), script
    script.write_text(controller(raw, args.mode), encoding='utf-8', newline='\n')
    if args.run_stage:
        assert args.mode == 'stage'
        result = run(script, args.rom, args.output / 'capture', sha256(raw).hexdigest(), 240)
        print(json.dumps({k: result[k] for k in ('passed', 'receipt', 'receipt_SHA256', 'script_SHA256')}, separators=(',', ':')))
        assert result['passed']
    else:
        print(json.dumps(dict(controller=str(script), ROM_SHA256=sha256(raw).hexdigest(),
              controller_SHA256=sha256(script.read_bytes()).hexdigest(), fixture=args.mode == 'fixture')))


if __name__ == '__main__':
    main()
