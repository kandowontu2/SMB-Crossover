"""Mounted native wave motion, sprite, block and enemy fixtures, stdout only."""

import argparse
import json
from unittest.mock import patch

import steve_armor_live_1113 as Live
import steve_armor_packet_1113 as Packet
import steve_armor_wave_1113 as Wave
from check_steve_armor_transport_1112 import call


def check(raw, *, fast_order=False,interrupts=False):
    if fast_order:
        with patch.object(Live,'order_blocks',lambda rows:rows):
            candidate, info = Live.proposal(raw)
    else:
        candidate, info = Live.proposal(raw)
    seed, cold_steps = Packet.load(candidate,info)
    C,N,W = Packet.Cold.C,Packet.Cold.N,Packet.Cold.W
    _, incumbent, _ = Wave.incumbent(raw)
    cuts = set()

    def wave_interrupt(current):
        bank = current.memory.rawtags[(current.pc-0x8000)//8192] if current.pc >= 0x8000 else -1
        key = (bank,current.pc)
        if not interrupts or key in cuts or not (
                bank == 1 or bank == 2 and (0xcd00 <= current.pc < 0xcd88 or
                                            0xc3bf <= current.pc < 0xc3fb)):
            return
        cuts.add(key)
        for kind in ('FF','IRQ'):
            _,branch = C.Vector.clone(current.memory,current)
            C.ColdVector.interrupt(branch,kind)

    def fresh(face, hero_x):
        m = C.Vector.clone(seed)
        m.raw_page(1,3)
        m.raw_page(2,2)
        N.put(m,CurrentBank=3,CurrentBankC=2,PlayerFacingDir=face,
              Player_X_Position=hero_x,Player_PageLoc=0,Player_Y_Position=176,
              Player_Y_HighPos=1,Player_State=0,GameEngineSubroutine=8,
              GamePauseStatus=0,JnHealth=6,JnHurt=0,MmDeathFlag=0,
              ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0)
        m[0xc1f0:0xc200] = bytes(16)
        m[0xc3fb:0xc400] = bytes(5)
        m[0xc1f2],m[0x5c85] = 127,127
        m[0x5c80],m[0x5c82] = 1,2
        for name in ('Block_Buffer_1','Block_Buffer_2'):
            address = W.address(m.bundle,name)
            m[address:address+208] = bytes(208)
        for slot in range(6):
            m[W.address(m.bundle,'Enemy_Flag')+slot] = 0
        cpu = N.NesMPU(memory=m)
        call(cpu,incumbent['StevePunchBirth'],x=0)
        assert m[0x5c87] == 15 and m[0xc97b] == face, (
            face,m[0x5c87],m[0xc97b],m[0xc1f2],m.rawtags,
            bytes(m[incumbent['StevePunchBirth']:incumbent['StevePunchBirth']+12]).hex())
        return m,cpu

    episodes = []
    sprite_cases = 0
    for face,hero_x in ((1,64),(2,220)):
        m,cpu = fresh(face,hero_x)
        origin = m[0x5c88]+256*m[0x5c89]
        positions = []
        for update in range(15):
            call(cpu,info['runtime']['symbols']['ArmorWaveGateway'],observe=wave_interrupt)
            x = m[0x5c88]+256*m[0x5c89]
            assert x == (origin+(4 if face == 1 else -4)*(update+1))&65535, (
                face,update,x,origin,m.rawtags)
            assert m[0x5c87] == 14-update
            positions.append(x)
            if update in (0,8,12):
                m[incumbent['CurrentOAMOffset']] = 0
                m[0x200:0x300] = bytes([248])*256
                m[0x5c83],m[0xc1f1] = 0xda,1
                C.Vector.call(m,'JnSetPose',x=0)
                body = bytes(m.ram[2][0x8c0:0x8dd])
                gate = bytes(m.ram[2][0x3bf:0x3fb])
                draw_trace = []
                points = {incumbent['SteveDraw'],
                          info['runtime']['symbols']['ArmorWaveDrawGateway'],
                          info['runtime']['symbols']['ArmorWaveDraw']}
                def draw_observe(model,current):
                    wave_interrupt(current)
                    if current.pc in points or (model.rawtags[1] == 0xde and
                                                0xb27f <= current.pc < 0xb300):
                        draw_trace.append((hex(current.pc),tuple(model.rawtags),current.a,
                                           current.x,current.y,current.p))
                C.Vector.call(m,'JnDraw',a=0,x=0,y=0,observe=draw_observe)
                C.Vector.call(m,'X5PublishChr')
                assert m.chr_latches[4:6] == [739,711], (
                    m.chr_latches,m[0x730b],m[0x5c80],m[0x5c82],m[0x5c87],draw_trace)
                assert m.chr_latches[0] == info['records'][0xda][0]
                assert bytes(m.ram[2][0x8c0:0x8dd]) == body
                assert bytes(m.ram[2][0x3bf:0x3fb]) == gate
                assert m.ram[2][0x3fb] == 0
                phase = 0 if update == 0 else 1 if update == 8 else 2
                record = info['wave_records'][Wave.POSES[phase]][face-1]
                expected = {( (m[0x5c8a]+record[at+2])&255,record[at],record[at+1],
                              (x+record[at+3])&255 ) for at in range(1,len(record),4)}
                rendered = {tuple(m[0x200+at:0x204+at]) for at in range(0,256,4)}
                assert expected <= rendered, (face,update,expected,rendered)
                sprite_cases += 1
                m.raw_page(1,3)
                m.raw_page(2,2)
                N.put(m,CurrentBank=3,CurrentBankC=2)
        episodes.append(dict(facing=face,motion_updates=15,positions=positions))

    kills = []
    for face,hero_x,targets in ((1,64,(103,143)),(2,220,(185,145))):
        m,cpu = fresh(face,hero_x)
        for slot,x in enumerate(targets):
            for name,value in (('Enemy_Flag',1),('Enemy_ID',6),('Enemy_State',0),
                               ('Enemy_X_Position',x),('Enemy_PageLoc',0),
                               ('Enemy_Y_Position',184),('Enemy_Y_HighPos',1),
                               ('JnEnemyHP',1),('JnEnemyHurt',0)):
                m[W.address(m.bundle,name)+slot] = value
        first_death = None
        for update in range(15):
            call(cpu,info['runtime']['symbols']['ArmorWaveGateway'])
            dead = [bool(m[W.address(m.bundle,'Enemy_State')+slot]&32) or
                    not m[W.address(m.bundle,'Enemy_Flag')+slot] for slot in range(2)]
            if dead[0] and first_death is None:
                first_death = update
                assert m[0x5c87] > 0
        assert all(dead), (face,dead)
        kills.append(dict(facing=face,placed_native_ground_Goombas=2,first_defeat_update=first_death,
                          both_native_defeats=True,wave_persisted_after_first=True))

    blocks = []
    for tile in (0x51,0xc1):
        m,cpu = fresh(1,64)
        C.Vector.call(m,'GetBlockBufferAddr',a=5)
        pointer = m[9]+256*m[10]
        cell = pointer+0x90
        m[cell] = tile
        control = N.get(m,'SprDataOffset_Ctrl')
        position = tuple(N.get(m,name) for name in ('Player_X_Position','Player_PageLoc',
                                                   'Player_Y_Position','Player_Y_HighPos'))
        call(cpu,info['runtime']['symbols']['ArmorWaveGateway'])
        assert m[cell] != tile and (control^N.get(m,'SprDataOffset_Ctrl'))&1
        assert m[0xc97d] == 0
        assert tuple(N.get(m,name) for name in ('Player_X_Position','Player_PageLoc',
                                               'Player_Y_Position','Player_Y_HighPos')) == position
        blocks.append(dict(placed_metatile=tile,result=m[cell],source_wave_age_reset=True,
                           native_player_coordinates_restored=True))
    tokens = []
    for face,hero_x,token_x in ((1,64,80),(2,220,190)):
        m,cpu = fresh(face,hero_x)
        for name,value in dict(Enemy_ID=46,Enemy_Flag=1,Enemy_State=128,PowerUpType=0,
                               Enemy_X_Position=token_x,Enemy_PageLoc=0,
                               Enemy_Y_Position=176,Enemy_Y_HighPos=1).items():
            m[W.address(m.bundle,name)+5] = value
        C.Vector.call(m,'JnPreparePickup',x=5)
        assert N.get(m,'InvPickup',5) == 0x8c
        m.raw_page(1,3)
        m.raw_page(2,2)
        N.put(m,CurrentBank=3,CurrentBankC=2)
        call(cpu,info['runtime']['symbols']['ArmorWaveGateway'],observe=wave_interrupt)
        assert (N.get(m,'InvPickup',5),m[0xc97d],m[0x5c87]) == (0x8d,0,14)
        call(cpu,info['runtime']['symbols']['ArmorWaveGateway'])
        assert (N.get(m,'InvPickup',5),m[0xc97d],m[0x5c87]) == (0x8d,1,13)
        tokens.append(dict(facing=face,actual_native_preparation=True,
                           explicit_mature_actor=True,flips=1,source_age_reset=True))

    crossings = []
    for face,hero_x in ((1,232),(2,32)):
        m,cpu = fresh(face,hero_x)
        if face == 2:
            m[0x5c89] = 1
        origin = m[0x5c88]+256*m[0x5c89]
        for update in range(15):
            call(cpu,info['runtime']['symbols']['ArmorWaveGateway'])
            assert m[0x5c88]+256*m[0x5c89] == (origin+(4 if face == 1 else -4)*(update+1))&65535
        crossings.append(dict(facing=face,origin=origin,motion_updates=15))
    return dict(parent=Packet.Entry.digest(raw),candidate=Packet.Entry.digest(candidate),cold_steps=cold_steps,
                runtime_bytes=len(info['runtime']['images']['STEVE_ARMOR_RUNTIME']),
                packed_bytes=info['packed_bytes'],spare=info['spare'],motion=episodes,
                native_wave_sprite_cases=sprite_cases,native_piercing=kills,native_blocks=blocks,
                native_token_flips=tokens,page_crossings=crossings,
                interrupt_cut_points=len(cuts),body_and_HUD_preserved=True,
                packet_order_optimized=not fast_order,
                fixture_scope='Native cold, source birth and live update/draw entries. Ground enemies and two terrain cells are placed explicitly.',
                release_qualified=False,output_files=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fast-order',action='store_true')
    parser.add_argument('--interrupts',action='store_true')
    parser.add_argument('--before-quick',action='store_true')
    args = parser.parse_args()
    print(json.dumps(check(Packet.qualification_parent(before_quick=args.before_quick),fast_order=args.fast_order,
                           interrupts=args.interrupts),
                     sort_keys=True),flush=True)
