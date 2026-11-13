"""Pure native-controller and explicitly private level-fixture APIs."""

import json

import audit_current_roster_powerups_1110 as Roster
import steve_armor_live_1113 as Live
import steve_armor_packet_1113 as Packet


PARENT = '4641ca4fb72699c0478e31b831d4c4ea0ffd2227be7f8446666092d2cc26e1d3'
CANDIDATE = 'f9d58305a3e2d820eb38df41c01649af335c41981e32393b0ac9b042802316ae'
POINTS = (80,192,304,416,528,640)
SCRIPT = Packet.Entry.ROOT/'tools/playthroughs/steve_armor_native_1113.lua'


def proposal(raw):
    assert Packet.Entry.digest(raw) == PARENT
    candidate,info = Live.proposal(raw)
    assert Packet.Entry.digest(candidate) == CANDIDATE
    return candidate,info


def fixture(candidate):
    """Replace only 1-1 level/enemy data for a declared private test ROM."""
    assert Packet.Entry.digest(candidate) == CANDIDATE
    bundle = Roster.W.Symbols.bundle()
    bundle['raw'] = candidate
    level = Roster.W.location(bundle,'L_GroundArea6')
    enemies = Roster.W.location(bundle,'E_GroundArea6')
    before = bytes.fromhex('502107814724570063017701c97168')
    assert candidate[level:level+len(before)] == before
    assert candidate[enemies:enemies+5] == bytes.fromhex('1ec2006b06')
    stage = bytearray((0x50,0x21))
    page = 0
    for x in POINTS:
        next_page = x//256
        assert next_page-page in (0,1)
        stage.extend((((x//16)&15)*16+7,0x80 if next_page != page else 0))
        page = next_page
    stage.append(0xfd)
    assert len(stage) == len(before)
    image = bytearray(candidate)
    image[level:level+len(stage)] = stage
    image[enemies] = 255
    allowed = set(range(level,level+len(stage)))|{enemies}
    assert all(a == b or at in allowed for at,(a,b) in enumerate(zip(candidate,image)))
    return bytes(image),dict(candidate=Packet.Entry.digest(candidate),
                             fixture=Packet.Entry.digest(image),private_test_ROM=True,
                             code_bytes_changed=0,
                             edits=[dict(offset=level,before=before.hex(),after=stage.hex()),
                                    dict(offset=enemies,before='1e',after='ff')],
                             question_blocks=[dict(world_x=x,top_y=144) for x in POINTS],
                             enemy_stream_terminated=True,
                             scope='Private flat 1-1 native level-data fixture. Six powerup question blocks use the ordinary parser, head collision, emergence, native preparation and collection. No runtime state writes or source inventory seeds.')


def controller(candidate,info, *, mode='armor_fixture'):
    assert Packet.Entry.digest(candidate) == CANDIDATE
    assert mode in ('armor_fixture','ingress')
    bundle = Roster.W.Symbols.bundle()
    bundle['raw'] = candidate
    names = ('Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos',
             'SelectedCharacter','OperMode','OperMode_Task','GameEngineSubroutine',
             'NumberofLives','JnHealth','PlayerFacingDir','Enemy_Flag','Enemy_State',
             'InvPickup','ScreenLeft_X_Pos','ScreenLeft_PageLoc')
    fields = {name:Roster.W.address(bundle,name) for name in names}
    lua = SCRIPT.read_text()
    lua = lua.replace('STEVE_FIELDS',','.join(f'{name}={value}' for name,value in fields.items()))
    lua = lua.replace('STEVE_COOKIE',json.dumps(info['cookie'].hex()))
    lua = lua.replace('STEVE_MODE',json.dumps(mode))
    lua = lua.replace('STEVE_POINTS',','.join(map(str,POINTS)))
    lua = lua.replace('STEVE_WAVE_RENDER',str(info['runtime']['symbols']['ArmorWaveNativeRender']))
    assert 'emu.write' not in lua and 'emu.setState' not in lua
    return lua


if __name__ == '__main__':
    candidate,info = proposal(Live.Art.D.HOST.read_bytes())
    private,proof = fixture(candidate)
    lua = controller(candidate,info)
    print(json.dumps(dict(**proof,controller_SHA256=Packet.Entry.digest(lua.encode()),
                          controller_bytes=len(lua.encode()),output_files=0),sort_keys=True),flush=True)
