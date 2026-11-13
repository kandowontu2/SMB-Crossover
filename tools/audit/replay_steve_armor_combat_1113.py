"""Separate private native-data combat fixture and readonly controller."""

import json

import replay_steve_armor_native_1113 as Native


BASE_FIXTURE = Native.fixture
SOURCE = Native.Packet.Entry.ROOT/'tools/playthroughs/steve_armor_combat_native_1113.lua'
NPC_X = (1120,1152)


def fixture(candidate):
    image,proof = BASE_FIXTURE(candidate)
    bundle = Native.Roster.W.Symbols.bundle()
    bundle['raw'] = candidate
    at = Native.Roster.W.location(bundle,'E_GroundArea6')
    before = bytes.fromhex('1ec2006b068b86')
    after = bytes.fromhex('0f046b068b06ff')
    assert candidate[at:at+len(before)] == before
    output = bytearray(image)
    output[at:at+len(after)] = after
    allowed = set(range(proof['edits'][0]['offset'],proof['edits'][0]['offset']+15))|set(range(at,at+7))
    assert all(a == b or index in allowed for index,(a,b) in enumerate(zip(candidate,output)))
    return bytes(output),proof|dict(fixture=Native.Packet.Entry.digest(output),
        edits=[proof['edits'][0],dict(offset=at,before=before.hex(),after=after.hex())],
        enemy_stream_terminated=False,
        expected_native_Goomba_constructor_positions=[dict(x=x,y=176) for x in NPC_X],
        scope='Separate private level-data-only combat fixture. Six native powerup questions precede two native page4 Goomba records. Runtime code and runtime state remain untouched.')


def controller(candidate,info):
    from check_ff_stdout_controller_source_1110 import LuaRuntime,DLL,DLL_SHA
    lua = Native.controller(candidate,info,mode='armor_fixture')
    assert Native.Packet.Entry.digest(candidate) in (Native.IDLE_CANDIDATE,
        '2aa5096391ddc303c4dc346293db1b628ddee36222fb3a7eaa20649c003b6cea')

    def change(before,after):
        nonlocal lua
        assert lua.count(before) == 1,before
        lua = lua.replace(before,after)

    bundle = Native.Roster.W.Symbols.bundle()
    bundle['raw'] = candidate
    W = Native.Roster.W
    names = ('Enemy_ID','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position',
             'Enemy_Y_HighPos','JnSavedX','InitEnemyObject','JnInjury','JnDefeat')
    fields = {name:W.address(bundle,name) for name in names}
    for name in ('InitEnemyObject','JnInjury','JnDefeat'):
        fields[name+'Bank'] = (W.location(bundle,name)-16)//8192
    fields |= {name:info['runtime']['symbols'][name] for name in ('ArmorDamage','ArmorDamageProtected')}
    tail = SOURCE.read_text().replace('STEVE_COMBAT_FIELDS',
        ','.join(f'{name}={value}' for name,value in fields.items()))
    change('local mode="armor_fixture"','local mode="combat_fixture"')
    change("mode=='armor_fixture'","mode=='combat_fixture'")
    change('local expected,pending={},{}',
           'local expected,pending={},{}\nlocal combat={spawns={},defeats={},defeated={},contacts={},injuryCalls=0,retained=false}')
    change('"exit_seen":%s,',
           '"exit_seen":%s,"native_goomba_spawns":%d,"native_defeats":%d,"accepted_armor_contacts":%d,"native_injury_calls":%d,"piercing_wave_retained":%s,')
    change('tostring(exitSeen),x(),field',
           'tostring(exitSeen),#combat.spawns,#combat.defeats,#combat.contacts,combat.injuryCalls,tostring(combat.retained),x(),field')
    change('local function tick()',tail+'\nlocal function tick()\n  if phase:sub(1,7)=="combat-" then combatTick();return end')
    change("then transition('attack-right',64)end",
           "then transition('combat-approach',1)end")
    change('Private native six-question fixture, armor waves and natural clock exit',
           'Private native questions, actual Goomba armor contact, piercing wave defeats and natural exit')
    assert Native.Packet.Entry.digest(DLL.read_bytes()) == DLL_SHA
    assert 'emu.write' not in lua and 'emu.setState' not in lua
    LuaRuntime().compile(lua)
    return lua


if __name__ == '__main__':
    candidate,info = Native.proposal(Native.Live.Art.D.HOST.read_bytes())
    image,proof = fixture(candidate)
    lua = controller(candidate,info)
    print(json.dumps(proof|dict(controller_SHA256=Native.Packet.Entry.digest(lua.encode()),
                                Lua_compiled=True,output_files=0),sort_keys=True),flush=True)
