"""Pure native-controller and explicitly private level-fixture APIs."""

import json

import audit_current_roster_powerups_1110 as Roster
import steve_armor_live_1113 as Live
import steve_armor_packet_1113 as Packet


PARENT = '4641ca4fb72699c0478e31b831d4c4ea0ffd2227be7f8446666092d2cc26e1d3'
CANDIDATE = 'f9d58305a3e2d820eb38df41c01649af335c41981e32393b0ac9b042802316ae'
PARENTS = {
    PARENT:CANDIDATE,
    'aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1':
        '2aa5096391ddc303c4dc346293db1b628ddee36222fb3a7eaa20649c003b6cea',
}
POINTS = (80,192,304,416,528,640)
SCRIPT = Packet.Entry.ROOT/'tools/playthroughs/steve_armor_native_1113.lua'


def proposal(raw):
    expected = PARENTS[Packet.Entry.digest(raw)]
    candidate,info = Live.proposal(raw)
    assert Packet.Entry.digest(candidate) == expected
    return candidate,info


def fixture(candidate):
    """Replace only 1-1 level/enemy data for a declared private test ROM."""
    assert Packet.Entry.digest(candidate) in PARENTS.values()
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
    from check_ff_stdout_controller_source_1110 import LuaRuntime,DLL,DLL_SHA
    assert Packet.Entry.digest(DLL.read_bytes()) == DLL_SHA
    assert Packet.Entry.digest(candidate) in PARENTS.values()
    assert mode in ('armor_fixture','ingress','full_stage')
    if mode == 'full_stage':
        lua = full_stage_controller(candidate,info)
        LuaRuntime().compile(lua)
        return lua
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
    counts = sorted({record[0] for pair in info['wave_records'].values() for record in pair})
    lua = lua.replace('STEVE_WAVE_COUNTS',','.join(f'[{count}]=true' for count in counts))
    lua = lua.replace('STEVE_WAVE_RENDER',str(info['runtime']['symbols']['ArmorWaveNativeRender']))
    assert 'emu.write' not in lua and 'emu.setState' not in lua
    LuaRuntime().compile(lua)
    return lua


def full_stage_controller(candidate,info):
    import compose_steve_full_route_1111 as Full
    import check_steve_shatterhand_move_live_1111 as Movement

    model,_ = Packet.load(candidate,info)
    movement = Movement.link()
    bundle = dict(model.bundle,syms=dict(model.bundle['syms']))
    bundle['syms']['CurrentOAMOffset'] = dict(val='0x06de')
    punch = Movement.S.link(bundle)
    draw = punch['images']['DRAW']
    assert bytes(model.ram[2][0x1bd4:0x1bd4+len(draw)]) == draw
    for name in ('SteveLiveMovement','SteveMotionProject'):
        pc = movement['symbols'][name]
        segment = next(key for key,(origin,size) in Movement.LAYOUT.items()
                       if origin <= pc < origin+size)
        offset = pc-Movement.LAYOUT[segment][0]
        expected = movement['images'][segment][offset:offset+8]
        assert bytes(model.ram[2][pc-0xc000:pc-0xc000+8]) == expected,name
    lua = Full.controller()
    values = {
        "assert(os.getenv('SMB_STEVE_COOKIE'))":json.dumps(info['cookie'].hex()),
        "assert(tonumber(os.getenv('SMB_STEVE_BIRTH')))":str(info['wave_hooks'][0][0]),
        "assert(tonumber(os.getenv('SMB_STEVE_DRAW')))":str(punch['symbols']['SteveDrawEmit']),
        "assert(tonumber(os.getenv('SMB_STEVE_MOVE_ENTRY')))":str(movement['symbols']['SteveLiveMovement']),
        "assert(tonumber(os.getenv('SMB_STEVE_MOVE_PROJECT')))":str(movement['symbols']['SteveMotionProject']),
    }
    for before,after in values.items():
        assert lua.count(before) == 1,before
        lua = lua.replace(before,after)
    before = "  if level==1 and engine==8 and read(0x753)==2 then\n"
    after = before+"    pad=0\n    if wy~=176 or read(0x1e)~=0 then return end\n"
    assert lua.count(before) == 1
    lua = lua.replace(before,after)
    lua = lua.replace('Steve cleared 1-1 and entered underground 1-2',
                      'Steve cleared 1-1 and landed grounded in underground 1-2')
    assert 'emu.write' not in lua and 'emu.setState' not in lua
    return lua


def jay_controller(candidate,info, *, mode='pickup'):
    """Bind delivered Jay controls after strict shared-owner normalization."""
    import compose_jay_head_bridge_1113 as Head
    import compose_jay_pickup_helper_1113 as Helper
    import compose_quick_climb_material_1113 as Quick
    import replay_jay_pickup_helper_1113 as Replay
    from check_ff_stdout_controller_source_1110 import LuaRuntime,DLL,DLL_SHA

    assert Packet.Entry.digest(candidate) == PARENTS[
        'aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1']
    assert mode in ('pickup','stage')
    cookie = candidate[Packet.Entry.prg(94,0xb2ef):Packet.Entry.prg(94,0xb2ef)+16]
    assert cookie == info['cookie'] and cookie[:4] == bytes.fromhex('aa10200c')
    parent = Live.reverse(candidate)
    base = Head.inverse(Helper.inverse(Quick.inverse(parent)))
    assert Packet.Entry.digest(base) == Packet.QUALIFICATION_PARENT
    head = Head.proposal(base)[0]
    normalized = Helper.proposal(head)[0]
    assert Quick.transform(normalized)[0] == parent
    for page in (232,234,331,332):
        assert Live.Art.page(candidate,page) == Live.Art.page(normalized,page),page
    lua = Replay.controller(normalized) if mode == 'pickup' else Replay.stage_controller(normalized)
    assert lua.count(Helper.COOKIE.hex()) == (1 if mode == 'pickup' else 2)
    lua = lua.replace(Helper.COOKIE.hex(),cookie.hex())
    assert 'emu.write' not in lua and 'emu.setState' not in lua
    assert Packet.Entry.digest(DLL.read_bytes()) == DLL_SHA
    LuaRuntime().compile(lua)
    return lua


if __name__ == '__main__':
    candidate,info = proposal(Live.Art.D.HOST.read_bytes())
    private,proof = fixture(candidate)
    lua = controller(candidate,info)
    print(json.dumps(dict(**proof,controller_SHA256=Packet.Entry.digest(lua.encode()),
                          controller_bytes=len(lua.encode()),output_files=0),sort_keys=True),flush=True)
