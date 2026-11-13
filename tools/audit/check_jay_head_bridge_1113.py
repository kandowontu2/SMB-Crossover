"""Inspect the live Jay ceiling cancel and source-owned retired movement tail."""

import argparse
from hashlib import sha256
import json
import inspect
import contextlib
import io
from collections import Counter

import check_jay_powerups_current_1113 as Current
import check_jay_silius_machinegun_1111 as Gun

SOURCE = Current.W.R/'tools/reference/jay_head_bridge_1113.s'


def bindings(model):
    original = Gun.C.Jay.build()
    cancel = original['symbols']['CancelUpwardVelocity']
    start = cancel-0xa000
    body = original['images']['PRIVATE'][start:start+6]
    assert len(body) == 6 and bytes(model.ram[3][start:start+6]) == body
    _, fields, aliases = Gun.T.Weapon.assemble(model.bundle)
    declarations = ''.join(f'{name}=${at:04x}\n' for name, at in aliases.items())
    alternate = Gun.H.assemble(declarations+Gun.T.Weapon.SOURCE.read_text(), Gun.T.ALT_LAYOUT)
    pause = Gun.Pause.assemble(aliases, update=0xb800)
    gun = Gun.assemble(dict(aliases=aliases, alternate=alternate, pause=pause), origin=Gun.LIVE_ORIGIN)
    worker = gun['images']['MACHINE_GUN']
    assert bytes(model.ram[3][0x785:0x785+len(worker)]) == worker
    tail_start, tail_end = Gun.LIVE_ORIGIN+len(worker), Gun.TEMPLATE
    tail = bytes(model.ram[3][tail_start-0xa000:tail_end-0xa000])
    # The machine-gun recipe replaces its whole retired movement grant and
    # explicitly pads this remaining suffix with NOPs.
    assert tail == bytes([0xea])*len(tail)
    direct = []
    for offset in range(8190):
        if model.ram[3][offset] in (0x20, 0x4c):
            target = int.from_bytes(model.ram[3][offset+1:offset+3], 'little')
            if tail_start <= target < tail_end:
                direct.append((0xa000+offset, target))
    assert not direct, direct
    import check_jay_silius_helpers_1111 as Helpers
    import check_jay_silius_enemy_ammo_1111 as Ammo
    import check_jay_silius_world_hit_1111 as Hit
    helper, _ = Helpers.assemble(model.bundle, origin=0xbd20)
    roll, linked = Ammo.assemble()
    ammo, _ = Ammo.assemble_host(roll, linked, origin=0xbaa8, draw_origin=0xbca0)
    world, _ = Hit.assemble(model.bundle, native_defeat=ammo['symbols']['CaptureAmmoDefeat'])
    owned = ((0xb800, bytes(model.ram[3][0x1800:0x1aa8])),
             (0xbaa8, ammo['images']['AMMOHOST']), (0xbca0, ammo['images']['AMMODRAW']),
             (0xbd20, helper['images']['HELPERS']), (Hit.ORIGIN, world['images']['WORLD_HIT']))
    gaps = []
    for (pc, code), (next_pc, _) in zip(owned, owned[1:]):
        assert bytes(model.ram[3][pc-0xa000:pc-0xa000+len(code)]) == code
        stop = pc+len(code)
        gap = bytes(model.ram[3][stop-0xa000:next_pc-0xa000])
        assert gap == bytes([0xea])*len(gap)
        gaps.append((stop, next_pc, len(gap)))
    world_start, world_code = owned[-1]
    assert bytes(model.ram[3][world_start-0xa000:world_start-0xa000+len(world_code)]) == world_code
    world_end = world_start+len(world_code)
    suffix = bytes(model.ram[3][world_end-0xa000:Gun.Steve.MOVEMENT_FALLBACK-0xa000])
    suffix_info = dict(start=world_end, stop=Gun.Steve.MOVEMENT_FALLBACK, size=len(suffix),
                       source_padding=suffix == bytes([0xea])*len(suffix), bytes=suffix.hex())
    return dict(cancel=cancel, cancel_bytes=body.hex(), gun_bytes=len(worker), tail_start=tail_start,
                tail_end=tail_end, tail_bytes=len(tail), tail_SHA256=sha256(tail).hexdigest(),
                fields={name: original['ram'][name] for name in (0x0b, 0x15, 0x19)},
                host_tile=original['symbols']['JayHostTile'], extra_source_gaps=gaps, world_suffix=suffix_info)


def assemble(model, fields, *, text=None, shift=0):
    names = ('R2', 'R3', 'R6', 'R7', 'AreaType', 'BlockBounceTimer', 'GuestHurtTicks', 'PlayerHeadCollision', 'GetBlockBufferAddr')
    aliases = {name: Current.W.address(model.bundle, name) for name in names}
    aliases.update(QueryIndex=0xc0f7, QueryX=0xc0f1, QueryStatus=0xc0f3, QueryTile=0xc0f4,
                   QueryAttributes=0xc0f5, DonorVY=fields['fields'][0x15])
    declarations = ''.join(f'{name}=${at:04x}\n' for name, at in aliases.items())
    filter_at, filter_end, filter_size = fields['extra_source_gaps'][-1]
    call_at, call_end, call_size = fields['extra_source_gaps'][1]
    cancel_at, cancel_end, cancel_size = fields['extra_source_gaps'][2]
    layout = {'REDIRECT': (fields['cancel'], 6), 'BRIDGE': (fields['tail_start']+shift, fields['tail_bytes']-shift),
              'FILTER': (filter_at, filter_size), 'HEAD_CALL': (call_at, call_size), 'CANCEL_RETURN': (cancel_at, cancel_size)}
    code = Gun.H.assemble(declarations+(SOURCE.read_text() if text is None else text), layout)
    code['layout'] = layout
    runtime = bytearray(model.ram[3][:0x8c0])
    for name in ('REDIRECT', 'BRIDGE'):
        at = layout[name][0]
        body = code['images'][name]
        runtime[at-0xa000:at-0xa000+len(body)] = body
    current, sizes = Gun.staged(bytes(model.ram[3][:0x8c0]))
    assert current == Gun.T.page(model.bundle['raw'], 331)+Gun.T.page(model.bundle['raw'], 332)
    packed = Gun.T.Motion.Cold.pack(bytes(runtime))
    used = sizes['decoder']+len(packed)+3
    return code, bytes(runtime), dict(current=sizes, proposed_packed=len(packed), proposed_total=used,
                                     capacity=2048, spare=2048-used)


def direct(model, pc, *, a=85, x=0, y=74, p=0x71, observe=None):
    model.raw_page(1, 3)
    model.raw_page(2, 2)
    Current.N.put(model, CurrentBank=3, CurrentBankC=2)
    cpu = Current.N.NesMPU(memory=model, pc=pc)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = a, x, y, p, 224
    cpu.stPushWord(0x5aff)
    for steps in range(100000):
        if cpu.pc == 0x5b00:
            assert cpu.sp == 224
            return (cpu.a, cpu.x, cpu.y, cpu.p), steps
        if observe:
            observe(model, cpu)
        assert model[cpu.pc] != 0, ('BRK', hex(cpu.pc), model.rawtags)
        cpu.step()
    raise AssertionError(('Bounded bridge', hex(cpu.pc)))


def caller_tiles(seed, fields):
    """Run the genuine donor QueryVertical continuation for every native tile."""
    W,N = Current.W,Current.N
    original = Gun.C.Jay.build()
    ram = original['ram']
    cancel_at = fields['cancel']-0xa000
    old_cancel = original['images']['PRIVATE'][cancel_at:cancel_at+6]
    native = W.address(seed.bundle,'PlayerHeadCollision')
    native_tag = ((W.location(seed.bundle,'PlayerHeadCollision')-16)//8192)|128
    attr_at = W.address(seed.bundle,'MTileAttribute')
    attrs = bytes(seed[attr_at:attr_at+256])
    assert attrs == seed.bundle['raw'][W.location(seed.bundle,'MTileAttribute'):W.location(seed.bundle,'MTileAttribute')+256]
    cases = [(tile,1,0,0,False) for tile in range(256)]
    cases += [(0xc1,*gate) for gate in ((0,0,0,False),(1,1,0,False),(1,0,1,False),
                                      (1,0,0,True),(2,0,0,False),(3,0,0,False))]
    counts, admitted, excluded = Counter(),[],[]
    for tile,area,bounce,hurt,bad_parser in cases:
        seed_case = Current.C.L.clone(seed)
        seed_case.raw_page(1,3)
        seed_case.raw_page(2,2)
        N.put(seed_case,CurrentBank=3,CurrentBankC=2,AreaType=area,BlockBounceTimer=bounce,
              GuestHurtTicks=hurt,Player_X_Position=77,Player_PageLoc=1,Player_Y_Position=161,
              Player_Y_Speed=253,Player_State=1)
        seed_case[0x445] = tile
        for logical,value in {0x0b:253,0x0e:10,0x0f:0,0x10:21,0x11:128,0x19:4,0x1c:0,0x32:0}.items():
            seed_case[ram[logical]] = value
        if bad_parser:
            N.put(seed_case,ColumnSets=0)
        eligible = attrs[tile]&7 == 1 and tile not in (0xc2,0xc3) and area and not(bounce or hurt or bad_parser)
        seen_native = False
        for flags in (0x30,0x31,0x74,0x79):
            old,trial = Current.C.L.clone(seed_case),Current.C.L.clone(seed_case)
            old.ram[3][cancel_at:cancel_at+6] = old_cancel
            wanted,_ = direct(old,original['symbols']['QueryVertical'],x=0,y=0,p=flags)
            calls = Counter()
            def observe(m,c):
                if m.rawtags[1] == 3:
                    if c.pc == fields['cancel']:calls['cancel'] += 1
                    if c.pc == fields['host_tile']:calls['query'] += 1
                if c.pc == native and m.rawtags[(c.pc-0x8000)//8192] == native_tag:
                    assert c.a == tile
                    calls['native'] += 1
            got,_ = direct(trial,original['symbols']['QueryVertical'],x=0,y=0,p=flags,observe=observe)
            assert got == wanted,(tile,area,flags,got,wanted)
            assert calls['query'] in (1,2)
            assert calls['native'] == bool(eligible),(tile,attrs[tile],area,calls)
            assert trial[0xc0f0:0xc0fb] == old[0xc0f0:0xc0fb],(tile,'source query')
            assert trial.ram[2][:0xf0] == old.ram[2][:0xf0],(tile,'original donor motor')
            assert tuple(N.get(trial,n)for n in ('Player_X_Position','Player_PageLoc','Player_Y_Position','Player_State')) == (77,1,161,1)
            if not eligible:
                assert trial[0x300:0x4a0] == old[0x300:0x4a0],(tile,'excluded native buffer')
            if calls['cancel']:
                assert trial[ram[0x15]] == 0
            counts.update(calls)
            counts['cases'] += 1
            seen_native |= bool(calls['native'])
        if area == 1 and not(bounce or hurt or bad_parser):
            (admitted if seen_native else excluded).append(tile)
    return dict(counts=dict(counts),admitted=admitted,excluded_count=len(excluded),
        attribute_table_SHA256=sha256(attrs).hexdigest(),genuine_caller=True,
        AXYP_query_motor_and_native_position_exact=True,excluded_buffers_unchanged=True)


def vectors(seed, info):
    """Real lag NMI and IRQ at reached changed/native-call ABI instructions."""
    fields, code = info['fields'],info['code']
    cuts,counts = set(),Counter()
    floor = 224
    spans = [(pc,pc+len(code['images'][name])) for name,(pc,_) in code['layout'].items()]
    head = Current.W.address(seed.bundle,'PlayerHeadCollision')
    for tile,area,bounce,hurt,status in ((0xc1,1,0,0,0),(0x51,1,0,0,0),(0xc4,1,0,0,0),
                                        (0xc1,0,0,0,0),(0xc1,1,1,0,0),(0xc1,1,0,1,0),(0xc1,1,0,0,1)):
        model = Current.C.L.clone(seed)
        model.raw_page(1,3)
        model.raw_page(2,2)
        Current.N.put(model,CurrentBank=3,CurrentBankC=2,AreaType=area,BlockBounceTimer=0,
                      GuestHurtTicks=0,Player_X_Position=77,Player_PageLoc=1,Player_Y_Position=161)
        model[0x445] = tile
        model[0xc0f0:0xc0f3] = [9,21,0]
        query,_ = direct(model,fields['host_tile'])
        model[0xc0f0],model[0xc0f3] = query[0],status
        Current.N.put(model,BlockBounceTimer=bounce,GuestHurtTicks=hurt,DisableScreenFlag=1,NmiDisable=255)
        def observe(m,c):
            nonlocal floor
            tag = m.rawtags[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
            used = (tag == 3 and any(lo<=c.pc<hi for lo,hi in spans)) or 0x15a<=c.pc<0x17b or (tag==254 and head<=c.pc<head+7)
            key = tag,c.pc
            if not used or key in cuts:
                return
            cuts.add(key)
            for kind in ('FF',) if c.p&4 else ('FF','IRQ'):
                _, branch = Gun.C.Vector.clone(m,c)
                floor = min(floor,Gun.C.ColdVector.interrupt(branch,kind))
                counts[kind] += 1
        returned,_ = direct(model,fields['cancel'],x=37,y=query[2],p=0x31,observe=observe)
        assert returned == (0,37,query[2],0x33)
    return dict(reached_instruction_cuts=len(cuts),interrupts=dict(counts),minimum_SP=floor,
                real_vectors=True,forced_blank_lag_NMI=True,exact_CPU_stack_RAM_and_mapper_restoration=True)


def cold_guards(raw, info, parent):
    """Actual typed cold entry, warm cache, readback failures and decoder cuts."""
    import check_steve_shatterhand_companion_transport_1111 as Cold
    import check_steve_shatterhand_upgrade_transport_1111 as Upgrade
    wrapper = Cold.compact_cold(info['cookie'],extended=True,upgrade=Upgrade.descriptor(371))
    at = Gun.C.offset(65,Gun.T.COLD)
    assert raw[at:at+Gun.T.COLD_SIZE] == wrapper['images']['COLD65'].ljust(Gun.T.COLD_SIZE,b'\xea')
    bundle = dict(Current.W.Symbols.bundle(),raw=raw)
    target = wrapper['symbols']['JaySceneOrRetire']
    cuts = set()
    floors = []
    # The existing 25-byte Jay/Steve descriptor reaches SP=$7a already.
    # Retain every generic restoration assertion and compare the exact old
    # depth explicitly instead of applying Getsu's shorter-descriptor $7b.
    original = Gun.C.ColdVector.interrupt
    source = inspect.getsource(original)
    needle = 'assert floor >= 0x7b'
    assert source.count(needle) == 1
    scope = dict(original.__globals__)
    exec(compile(source.replace(needle,'assert floor >= 0x7a'),'<current shared decoder lag NMI>', 'exec'),scope)
    def fresh(variant):
        m = Gun.C.Common.blank(bundle)
        Gun.C.Common.scene(m,16)
        m[0x730b] = variant<<5
        return m
    def load(m,interrupts=False):
        cpu = Gun.C.ColdVector.entry(m)
        m[0x16c],m[0x16d] = target&255,target>>8
        def observe(m,c):
            if not interrupts or m.rawtags[2] != 2 or not 0xd000<=c.pc<0xd101:
                return
            key = c.pc,c.p&1
            if key in cuts:return
            cuts.add(key)
            assert c.p&4
            _,branch = Gun.C.Vector.clone(m,c)
            floors.append(scope['interrupt'](branch,'FF'))
        Gun.C.Vector.finish(m,cpu,(0x5b00,224),observe)
        assert (cpu.a,cpu.x,cpu.y,cpu.p&0xef,cpu.sp) == (83,71,109,0x21,224)
    result = {}
    for variant in (1,2):
        m = fresh(variant)
        load(m,interrupts=variant==1)
        assert Gun.C.Common.headers(m) == (info['cookie'],)*2
        assert m.ppu_reads == 32800,(variant,m.ppu_reads)
        for name,(pc,_) in info['code']['layout'].items():
            body = info['code']['images'][name]
            assert bytes(m.ram[3][pc-0xa000:pc-0xa000+len(body)]) == body
        reads=m.ppu_reads
        load(m)
        assert m.ppu_reads == reads
        result[variant] = dict(cold_reads=reads,warm_reads=0)
    faults = ((3,0x400),(3,0x7ff),(3,0x1c98),(3,0x1d1c),(3,0x1e17))
    for fault in faults:
        m=fresh(1)
        m.corrupt_at=fault
        load(m)
        assert not any(header[0] for header in Gun.C.Common.headers(m)),fault
    candidate_cuts,candidate_floor = len(cuts),min(floors)
    old_wrapper = Cold.compact_cold(Current.COOKIE,extended=True,upgrade=Upgrade.descriptor(371))
    assert old_wrapper['symbols']['JaySceneOrRetire'] == target
    bundle = dict(bundle,raw=parent)
    cuts.clear();floors.clear()
    old=fresh(1)
    load(old,interrupts=True)
    assert Gun.C.Common.headers(old) == (Current.COOKIE,)*2
    assert old.ppu_reads == 32800
    assert min(floors) == candidate_floor == 0x7a
    return dict(cold_and_warm=result,forced_blank_decoder_NMI_cuts=candidate_cuts,
                parent_decoder_NMI_cuts=len(cuts),parent_and_candidate_minimum_SP=candidate_floor,
                readback_faults_rejected=len(faults),full_generic_restoration_checks_retained=True)


def foreign(parent, candidate, info):
    W,N=Current.W,Current.N
    old_bundle=dict(W.Symbols.bundle(),raw=parent)
    new_bundle=dict(old_bundle,raw=candidate)
    result={}
    pads=[0]*6+[64]*12+[1]*19+[129]*9+[2]*15+[0]*10+[64]*9
    for variant,name in enumerate(('MIKE JONES','JAY MCCRAY','STEVE HERMANN')):
        row=dict(name=name,slot=15,cycle=variant,raw=16)
        a,b=Current.C.cold(old_bundle,row)[1],Current.C.cold(new_bundle,row)[1]
        def compare():
            old,new=Gun.C.Vector.app(a),Gun.C.Vector.app(b)
            assert old[:3]+old[4:] == new[:3]+new[4:],(name,'native state')
            assert a.ram[2][:0x1000] == b.ram[2][:0x1000],(name,'live donor state')
            assert a.ram[0] == b.ram[0] and a.ram[1] == b.ram[1]
            assert a.vram == b.vram and a.chr_latches == b.chr_latches
        compare()
        for pad in pads:
            a.controller_pad=b.controller_pad=pad
            Current.Frames.frame(a)
            Current.Frames.frame(b)
            compare()
        assert N.get(a,'NumberofLives') == N.get(b,'NumberofLives') == 2
        if variant:
            assert Gun.C.Common.headers(a) == (Current.COOKIE,)*2
            assert Gun.C.Common.headers(b) == (info['cookie'],)*2
        else:
            assert a.ram == b.ram
        result[name]=dict(paired_updates=len(pads),lives=2,exact_native_state_and_live_donor=True,
                          PPU_reads=(a.ppu_reads,b.ppu_reads))
    return result


def lua_parity(seed, image):
    """Compare generated Lua decisions with every actual CPU route input."""
    import replay_jay_powerups_1113 as Replay
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    script = Replay.controller(image,expect='earned')
    prefix = script.split('local function pause(n)',1)[0]
    assert len(prefix)<len(script)
    lua=LuaRuntime()
    current=[seed]
    def read(at,kind):
        return current[0][at] if kind==0 else current[0].ram[at//8192][at%8192]
    emu=lua.table()
    emu['read']=read
    emu['memType']=lua.table_from(dict(nesDebug=0,nesWorkRam=1))
    lua.globals()['emu']=emu
    lua.globals()['os']['getenv']=lambda name:sha256(image).hexdigest()
    lua.execute(prefix+'''\nfunction jayBegin() game=true;opening=60 end
function jayDrive() drive();return pad end''')
    lua.globals().jayBegin()
    compared=[]
    def check(model,epoch,pad):
        current[0]=model
        actual=lua.globals().jayDrive()
        assert actual==pad,(epoch,pad,actual,Current.state(model))
        compared.append(pad)
    with contextlib.redirect_stdout(io.StringIO()):
        result=Current.natural(seed,400,pad_observer=check)
    assert result['passed']
    return dict(compared_logical_inputs=len(compared),actual_CPU_route=result,
                script_SHA256=sha256(script.encode()).hexdigest(),prefix_controller_logic_exact=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--route', action='store_true')
    parser.add_argument('--section',choices=('footprint','tiles','vectors','cold','foreign','route','all'),default='all')
    args = parser.parse_args()
    import compose_jay_head_bridge_1113 as P
    raw=Current.ROM.read_bytes()
    parent=P.inverse(raw) if sha256(raw).hexdigest()==P.CANDIDATE_PIN else raw
    image,info=P.proposal(parent)
    assert P.inverse(image)==parent
    _,model=P.cold(image,info['cookie'],info['candidate_SHA256'])
    section='route' if args.route else args.section
    result=dict(parent_SHA256=P.PARENT_PIN,candidate_SHA256=P.CANDIDATE_PIN,output_files=0,
                bridge_bytes=info['code']['used'],compressed=info['compressed'],exact_inverse=True)
    for name,call in (
        ('tiles',lambda:caller_tiles(model,info['fields'])),
        ('vectors',lambda:vectors(model,info)),
        ('cold',lambda:cold_guards(image,info,parent)),
        ('foreign',lambda:foreign(parent,image,info)),
        ('route',lambda:lua_parity(model,image)),
    ):
        if section in (name,'all'):
            result[name]=call()
            print(json.dumps(dict(section=name,passed=True,result=result[name],output_files=0)),flush=True)
    print(json.dumps(result),flush=True)


if __name__ == '__main__':
    main()
