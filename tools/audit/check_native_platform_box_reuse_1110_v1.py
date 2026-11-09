"""Prove the prepared large-platform box can reuse unambiguous native X bits."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess

import check_native_platform_direct_1110_v1 as Direct
from check_mini_funded_actor_1108_v3 import install, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import cpu_at


D, N, P, R = Direct.D, Direct.N, Direct.P, Direct.R
ROM = R/'build/mini-platform-firebar-native-1110/candidate.nes'
PIN = '6bd5e4b1976e26ecccd9b7c0512944020d6eb7a6e2c8c35ab50c53d0441e7491'
SOURCE = R/'tools/reference/native_platform_box_reuse_1110_v1.s'
PROFILE = R/'build/mini-platform-actor-profile-1110/capture/instruction-sample.json'
OFFSCREEN = 0x05a1
GENERIC, PREPARED, TEST, VISIBLE, LEGACY = 0xb04b,0xb057,0xb05b,0xb05d,0xb060
HEIGHT = 0xaedf
SCRATCH = frozenset((8,9,10,0x016c))
STOP = 0x5b00
STOCK = bytes.fromhex('e8201a8bcac9fe90034c3b9f4caeaee8eaa001204e9fb51e2920f009b95806186910995a06'
                      'b95906186908995b064c909f')
RP_SAVE = bytes.fromhex('08488a489848a50348a50448a50548a50648a50748a50848a50948a50a48'
                        'ad656c48ad666c48ad676c48ad636c48ad646c48')
RP_RESTORE = bytes.fromhex('688d646c688d636c688d676c688d666c688d656c68850a688509688508688507'
                           '68850668850568850468850368a868aa6828')
PLATFORM_SAVE = RP_SAVE[:30]
PLATFORM_RESTORE = RP_RESTORE[20:]
X_BITS = (127,63,31,15,7,3,1,0,128,192,224,240,248,252,254,255)
SMC_SHADOW = 0x727a


def raw_x_bits(memory, slot):
    x, page = memory[0x76+slot], memory[0x5d+slot]
    for edge in (1,0):
        low, high = memory[0x071f+edge], memory[0x071d+edge]
        diff = (low-x)&255
        page_diff = (high-page-int(low<x))&255
        if page_diff&128:
            index = (7,15)[edge]
        elif page_diff or diff >= 56:
            index = (15,7)[edge]
        else:
            index = (diff >> 3)+(8 if edge == 0 else 0)
        if X_BITS[index]:
            return X_BITS[index]
    return 0


def at(bank, pc):
    return 16+8192*bank+(pc&8191)


def link(raw, output):
    b = P.bundle(raw)
    for name, pc in (('Enemy_OffscreenBits',OFFSCREEN), ('RunLargePlatform',D.ACTOR),
                     ('HpNativePlatformBBoxGate',0xbe6f), ('HpNativePlatformBBoxCold',GENERIC),
                     ('HpPrepareNativePointers',0xb07c), ('GetEnemyOffscreenBits',0x8ae9),
                     ('RelativeEnemyPosition',0x8aa0), ('GetXOffscreenBits',0x8b1a)):
        assert P.address(b,name) == pc, name
    ingress = bytes.fromhex('20e98a20a08a206fbe')
    assert raw[at(0,D.ACTOR):at(0,D.ACTOR)+len(ingress)] == ingress
    assert raw[at(0,0xa000):at(0,0xa000)+8192].count(bytes.fromhex('206fbe')) == 1
    assert raw[at(0,0xbe7f):at(0,0xbe88)] == bytes.fromhex('8d6a01a94ba0b0d007')
    assert raw[at(26,HEIGHT):at(26,HEIGHT)+14] == bytes.fromhex('186908995b064c909f4c5ab0eaea')
    assert raw[at(26,GENERIC):at(26,0xb07c)] == STOCK
    bank26 = raw[at(26,0xa000):at(26,0xa000)+8192]
    assert bank26.count(bytes.fromhex('4c5ab0')) == 1 and bytes.fromhex('205ab0') not in bank26
    assert not any(raw.count(bytes.fromhex(f'a9{lo:02x}8d6c01a9b08d6d01a99a')) for lo in (0x57,0x5a))
    output.mkdir(exist_ok=True)
    cfg, obj, binary = (output/f'platform-box-reuse.{ext}' for ext in ('cfg','o','bin'))
    cfg.write_text('MEMORY{B:start=$B04B,size=49,file=%O;I:start=$BE83,size=1,file=%O;'
                   'T:start=$AEE9,size=2,file=%O;}\n'
                   'SEGMENTS{BOX:load=B,type=ro;INGRESS:load=I,type=ro;LEGACY_TARGET:load=T,type=ro;}\n')
    cc = R/'tools/Windows/cc65/bin'
    subprocess.run([cc/'ca65.exe',SOURCE,'-o',obj],check=True)
    subprocess.run([cc/'ld65.exe','-C',cfg,obj,'-o',binary],check=True)
    obj.unlink()
    code = binary.read_bytes()
    assert len(code) == 52 and code[-3:] == bytes.fromhex('5760b0')
    assert code[12:21] == bytes.fromhex('ada1054ab0ee4caeae')
    rows = []
    for bank, pc, old, new in ((26,GENERIC,STOCK,code[:49]),
                               (0,0xbe83,b'\x4b',code[49:50]),
                               (26,0xaee9,bytes.fromhex('5ab0'),code[50:])):
        off = at(bank,pc)
        assert raw[off:off+len(old)] == old and len(old) == len(new)
        rows.append(dict(physical_PRG=bank,CPU_half_open=[pc,pc+len(old)],file_offset=off,
                         old_hex=old.hex(),new_hex=new.hex()))
    return install(raw,rows),rows


class WatchedBus(Direct.ObservedBus):
    """Treat the source RP_Save/Restore macro as transport, with stack taint."""

    saves = {}
    restores = {}
    smc_transfers = {}

    def __getitem__(self, address):
        if self.watch and isinstance(address,int):
            if address in self.stack_taint:
                assert self.restoring is not None and address == self.restoring[0], (self.point,hex(address))
            if address in self.pending and self.saves.get(self.point) == address:
                return super(Direct.ObservedBus,self).__getitem__(address)
            transfer = self.smc_transfers.get(self.point)
            if address in self.pending and transfer is not None and transfer[0] == address:
                value = super(Direct.ObservedBus,self).__getitem__(address)
                self.copying = ((self.point[0],self.point[1]+3),transfer[1],value)
                return value
        return super().__getitem__(address)

    def __setitem__(self, address, value):
        if self.watch and isinstance(address,int):
            if self.copying is not None and (self.point,address) == self.copying[:2]:
                assert value == self.copying[2]
                self.copy_writes[len(self.writes)] = (address,value)
                self.copying = None
                super().__setitem__(address,value)
                self.pending.add(address)
                return
            if self.saving is not None and (self.point,address) == self.saving[:2]:
                self.stack_taint[address] = self.saving[2]
                self.saving = None
            elif address in self.stack_taint:
                raise AssertionError(('Live source scratch save was overwritten',self.point,hex(address)))
            if self.restoring is not None and (self.point,address) == self.restoring[1:]:
                del self.stack_taint[self.restoring[0]]
                self.restoring = None
                super().__setitem__(address,value)
                self.pending.add(address)
                return
        super().__setitem__(address,value)


def macro_sites(raw, pattern, opcode):
    prg = raw[16:1048592]
    sites = {}
    offset = -1
    while (offset := prg.find(pattern,offset+1)) != -1:
        bank, low = divmod(offset,8192)
        mapped = 0x8000 if bank == 126 else 0xe000 if bank in (119,120,125,127) else 0xa000
        for addr in (8,9,10):
            target = bytes((opcode,addr))
            pc = mapped+low+pattern.index(target)-(opcode == 0x85)
            sites[(bank|128,pc)] = addr
    assert len(sites) >= 3
    return sites


def audio_shadow_sites(raw):
    # Each live user saves all five operands first. The private backup is
    # read only by its own inverse macro after actual audio processing.
    smc = (0x162,0x16a,0x16c,0x16d,0x179)
    backup = range(SMC_SHADOW-2,SMC_SHADOW+3)
    sites = {}
    for bank,save,restore in ((82,0xdf0f,0xdf2e),(63,0xb461,0xb507)):
        for start, pairs in ((save,list(zip(smc,backup,strict=True))),
                             (restore,list(zip(backup,smc,strict=True)))):
            expected = b''.join(bytes((0xad,src&255,src>>8,0x8d,dst&255,dst>>8)) for src,dst in pairs)
            pos = at(bank,start)
            assert raw[pos:pos+len(expected)] == expected,(bank,hex(start))
            sites[bank|128,start+12] = pairs[2]
    return sites


def begin(c, successor, carry_pending=False):
    m = c.memory
    m.first_reads, m.first_writes = {}, {}
    m.pending = m.pending if carry_pending and hasattr(m,'pending') else set()
    m.watch = successor and bool(m.pending)
    m.stack_taint, m.saving, m.restoring = {},None,None
    m.copying, m.copy_writes = None,{}
    m.stage, m.packed, m.fast, m.fallback, m.prepared, m.riders = 0,None,0,0,0,0
    m.writes.clear()


def observe(c, successor):
    m = c.memory
    m.point = D.point(c)
    if m.watch:
        addr = m.saves.get(m.point)
        if addr in m.pending:
            m.saving = ((m.point[0],m.point[1]+2),0x100+c.sp,addr)
        addr = m.restores.get(m.point)
        saved = 0x100+((c.sp+1)&255)
        if addr is not None and saved in m.stack_taint:
            assert addr == m.stack_taint[saved]
            m.restoring = (saved,(m.point[0],m.point[1]+1),addr)
    if m.point == (128,D.ACTOR):
        m.stage, m.packed = 1,None
    if m.point == (128,D.ACTOR+3) and m.stage == 1:
        m.stage, m.packed = 2,m[OFFSCREEN]
        assert m.packed&15 == raw_x_bits(m,c.x)>>4
    if successor and m.point == (154,PREPARED):
        assert m.stage == 2 and m[OFFSCREEN] == m.packed
        m.prepared += 1
        m.watch = True
        m.pending.add(0x016c)
    if successor and m.point == (154,TEST):
        assert m.packed is not None and bool(c.p&1) == bool(m.packed&1)
        if c.p&1:
            m.fallback += 1
        else:
            m.fast += 1
            m.pending.update((8,9,10))
    if m.point == (128,D.ACTOR+9):
        m.stage = 0
    if m.point == (128,0xb6f2):
        m.riders += 1


def finish(c, end, successor, carry_pending=False):
    begin(c,successor,carry_pending)
    run(c,end,lambda z:observe(z,successor))
    c.memory.watch = False
    assert not c.memory.first_reads, c.memory.first_reads
    assert not c.memory.stack_taint and c.memory.saving is c.memory.restoring is None
    assert c.memory.copying is None


def set_actor_geometry(c, relative, page, state, ctrl):
    m = c.memory
    camera = 0x90 if page == 0 else 0x1fa
    position = (camera+relative)&65535
    right = (camera+255)&65535
    N.put(m, ScreenLeft_X_Pos=camera&255, ScreenLeft_PageLoc=camera>>8,
          ScreenRight_X_Pos=right&255, ScreenRight_PageLoc=right>>8,
          Player_X_Position=(camera+108)&255,Player_PageLoc=(camera+108)>>8)
    for name,val in (('Enemy_X_Position',position&255), ('Enemy_PageLoc',position>>8),
                     ('Enemy_State',state), ('Enemy_BoundBoxCtrl',ctrl)):
        Direct.set_slot(m,name,5,val)


def actor_cases(images):
    seeds = [P.fixture(b,0,False,False) for b in images]
    cases, counts, timings = 0,Counter(),Counter()
    for owner, ident, relative, page, state, ctrl, p in product(
            range(42),(0x25,0x28),(-56,-48,-47,-22,106,248,255,256,282),
            (0,1),(0,0x40,0x60),(5,6,7),(0x21,0x65)):
        if owner not in (0,4,10,41) and (page or ctrl != 5 or relative not in (-48,-22,106,282) or p != 0x21):
            continue
        pair = [D.actor_setup(seed,owner,int(owner == 4),ident,state,'contact',0,p) for seed in seeds]
        for side,c in enumerate(pair):
            set_actor_geometry(c,relative,page,state,ctrl)
            finish(c,D.end,bool(side))
        old,new = pair
        m = new.memory
        key = owner,ident,relative,page,state,ctrl,p
        assert old.memory.riders == m.riders
        assert m.prepared == int(bool(state&0x40)) and m.prepared == m.fast+m.fallback
        scrubs = (SCRATCH if m.fast else {0x016c}) if m.prepared else ()
        assert Direct.state(old,scrubs) == Direct.state(new,scrubs), (key, m.packed, m.fast)
        counts['riders'] += m.riders
        mode = 'fast' if m.fast else 'ambiguous' if m.fallback else 'untagged'
        counts[mode] += 1
        timings[mode,old.processorCycles-new.processorCycles] += 1
        cases += 1
    return dict(cases=cases,counts=dict(counts),cycles=[[*k,n] for k,n in sorted(timings.items())])


def standalone(images):
    seeds = [P.fixture(b,0,False,False) for b in images]
    count = 0
    for relative,state,ctrl,stale in product((-49,-47,106,282),(0x40,0x60),(5,6,7),(0,15,255)):
        cpus = []
        for seed in seeds:
            m = slim_fork(seed)
            m.raw_page(1,154)
            N.put(m,CurrentBank=154,ObjectOffset=5,Enemy_Rel_XPos=relative&255,Enemy_Rel_YPos=173)
            m[OFFSCREEN] = stale
            c = cpu_at(m,GENERIC,232,0x61,x=5)
            set_actor_geometry(c,relative,1,state,ctrl)
            run(c,lambda z:(z.pc,z.sp) == (STOP,232))
            cpus.append(c)
        assert Direct.state(cpus[0]) == Direct.state(cpus[1]),(relative,state,ctrl,stale)
        count += 1
    return count


def with_bus(function, before, after):
    old_bus = N.Bus
    WatchedBus.saves = macro_sites(after,RP_SAVE,0xa5) | macro_sites(after,PLATFORM_SAVE,0xa5)
    WatchedBus.restores = macro_sites(after,RP_RESTORE,0x85) | macro_sites(after,PLATFORM_RESTORE,0x85)
    WatchedBus.smc_transfers = audio_shadow_sites(after)
    N.Bus = WatchedBus
    try:
        return function([P.bundle(b) for b in (before,after)])
    finally:
        N.Bus = old_bus


def whole(before, after):
    def exercise(images):
        rows = []
        for actors, mode in product((0,3),('normal','skip','transition','death')):
            pair = [D.scene_seed(b,3,actors) for b in images]
            saved, hits = [],Counter()
            for step in range(8):
                cpus = []
                for side,m in enumerate(pair):
                    key = 0 if step < 4 else 192
                    N.put(m,SavedJoypadBits=key,SavedJoypad1Bits=key,VRAM_Buffer1_Offset=0,
                          VRAM_Buffer_AddrCtrl=0,NmiDisable=0,ShouldSkipDrawSprites=int(mode == 'skip'),
                          FramesSinceLastSpriteDraw=step if mode == 'skip' else 0)
                    if mode == 'transition':
                        N.put(m,GamePauseStatus=int(step in (2,3)))
                    if mode == 'death' or mode == 'transition' and step >= 5:
                        N.put(m,GameEngineSubroutine=11)
                    c = cpu_at(m,P.address(m.bundle,'GameLoop'),252,0x21,x=0,y=0)
                    finish(c,lambda z:(z.pc,z.sp) == (STOP,252),bool(side),True)
                    cpus.append(c)
                old,new = cpus
                assert Direct.state(old) == Direct.state(new), (actors,mode,step)
                hits['fast'] += new.memory.fast
                hits['ambiguous'] += new.memory.fallback
                saved.append(old.processorCycles-new.processorCycles)
            rows.append(dict(ordinary=actors,mode=mode,updates=len(saved),hits=dict(hits),savings=[min(saved),max(saved)]))
        assert any(row['hits']['fast'] for row in rows)
        return rows
    return with_bus(exercise,before,after)


def qualify_vectors(before, after):
    def exercise(images):
        old,new = images
        seed = D.scene_seed(new,3,3)
        lag, regular = Direct.lag_pcs(seed)
        counts, deepest, sites = Counter(),{},set()
        minimum = [255,255]

        def inject(c, kind, nested=False):
            results = []
            owner = N.get(c.memory,'SelectedCharacter')
            live = set(c.memory.pending) if c.memory.watch else set()
            for original in (False,True):
                q = Direct.fork_cpu(c,old if original else None)
                m = q.memory
                if original:
                    for addr in live:
                        previous = 0x4b if addr == 0x016c else list.__getitem__(m,addr)^255
                        list.__setitem__(m,addr,previous)
                m.first_reads = {}
                m.copy_writes = {}
                before_state = Direct.interrupt_checkpoint(q)

                def see(z):
                    minimum[1] = min(minimum[1],z.sp)
                    if original or kind != 'lag_FF' or z.p&4:
                        return
                    key = owner,bool(m.watch and m.pending)
                    if key not in deepest or z.sp < deepest[key].sp:
                        deepest[key] = Direct.fork_cpu(z)

                Direct.interrupt(q,kind,lag,regular,see)
                assert Direct.interrupt_checkpoint(q) == before_state
                assert not m.first_reads, (kind,owner,D.point(c),m.first_reads)
                assert m.copying is None
                m.watch = False
                normalization = live | ({SMC_SHADOW} if SMC_SHADOW in m.pending else set())
                writes = m.writes[:]
                for index,(addr,value) in m.copy_writes.items():
                    assert addr in (0x016c,SMC_SHADOW) and writes[index] == (addr,value)
                    writes[index] = (addr,0)
                if m.copy_writes and not original:
                    counts['audio_shadow_transports'] += len(m.copy_writes)
                results.append((Direct.state(q,normalization),writes,m.ram_writes[:],q.processorCycles))
            assert results[0] == results[1], (kind,owner,D.point(c),live)
            name = 'nested_IRQ' if nested else kind
            counts[name] += 1
            if live:
                counts[f'poisoned_{name}'] += 1

        def visit(c,end):
            begin(c,True)
            seen = set()

            def at_cut(z):
                observe(z,True)
                bank,pc = D.point(z)
                if not (bank == 154 and (GENERIC <= pc < 0xb07c or 0xaeae <= pc < 0xaeed)
                        or bank == 128 and 0xbe7f <= pc < 0xbe88):
                    return
                key = bank,pc,z.sp,z.p&4
                if key in seen:
                    return
                seen.add(key)
                sites.add((bank,pc))
                minimum[0] = min(minimum[0],z.sp)
                inject(z,'lag_FF')
                if not z.p&4:
                    inject(z,'IRQ')

            run(c,end,at_cut)
            assert seen and not c.memory.first_reads

        for owner, relative in product(range(42),(-22,282)):
            c = D.actor_setup(seed,owner,int(owner == 4),0x25,0x40,'distant',0,0x21)
            set_actor_geometry(c,relative,1,0x40,5)
            visit(c,D.end)
            assert c.memory.fast == (relative == -22)
        for p in (0x21,0x65):
            m = slim_fork(seed)
            N.put(m,NmiDisable=0,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
            c = cpu_at(m,P.address(new,'GameLoop'),252,p,x=0,y=0)
            visit(c,lambda z:(z.pc,z.sp) == (STOP,252))
        for c in deepest.values():
            inject(c,'IRQ',nested=True)
        assert all(counts[k] for k in ('IRQ','lag_FF','nested_IRQ','poisoned_IRQ','poisoned_lag_FF',
                                      'poisoned_nested_IRQ','audio_shadow_transports')),counts
        assert minimum[1] > 0x7a
        return dict(cuts=dict(counts),changed_sites=len(sites),minimum_SP=minimum,
                    actual_lag_PC=lag,forbidden_regular_PC=regular)
    return with_bus(exercise,before,after)


def resumed_vectors(before, after):
    def exercise(images):
        results = []
        for owner,kind in ((41,'lag_FF'),(41,'IRQ'),(25,'lag_FF')):
            pair = []
            for side,b in enumerate(images):
                if owner == 41:
                    m = D.scene_seed(b,3,3)
                    N.put(m,NmiDisable=0,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                    c = cpu_at(m,P.address(b,'GameLoop'),252,0x21,x=0,y=0)
                    end = lambda z:(z.pc,z.sp) == (STOP,252)
                else:
                    c = D.actor_setup(P.fixture(b,0,False,False),owner,0,0x25,0x40,'distant',0,0x21)
                    set_actor_geometry(c,-22,1,0x40,5)
                    m = c.memory
                    end = D.end
                lag,regular = Direct.lag_pcs(m)
                armed = True
                begin(c,bool(side))

                def cut(z):
                    nonlocal armed
                    observe(z,bool(side))
                    if armed and D.point(z) == (154,PREPARED if side else GENERIC):
                        armed = False
                        assert list.__getitem__(m,0x016c) == (0x57 if side else 0x4b)
                        saved = Direct.interrupt_checkpoint(z)
                        Direct.interrupt(z,kind,lag,regular)
                        assert Direct.interrupt_checkpoint(z) == saved

                run(c,end,cut)
                assert not armed and not m.first_reads and not m.stack_taint,(owner,kind,side,armed,m.first_reads)
                m.watch = False
                pair.append(c)
            old,new = pair
            left,right = old.memory,new.memory
            # Rogue retains the exact private backup copy until its next
            # save. No intervening foreground reader can consume that copy.
            old_backup,new_backup = left[SMC_SHADOW],right[SMC_SHADOW]
            shadow_differs = old_backup != new_backup
            if shadow_differs:
                assert owner == 25 and (old_backup,new_backup) == (0x4b,0x57)
                assert SMC_SHADOW in right.pending
            masks = (SCRATCH if owner == 25 else frozenset()) | ({SMC_SHADOW} if shadow_differs else set())
            assert Direct.state(old,masks) == Direct.state(new,masks),(owner,kind)
            hardware = lambda m:[(addr,val) for addr,val in m.writes if 0x2000 <= addr < 0x6000]
            assert hardware(left) == hardware(right),(owner,kind)
            results.append(dict(owner=owner,vector=kind,full_GameLoop=owner == 41,
                                exact_hardware_writes=True,private_shadow_retained=shadow_differs))
        assert any(r['private_shadow_retained'] for r in results)
        return results
    return with_bus(exercise,before,after)


def profile_cost(raw):
    profile = json.loads(PROFILE.read_text())
    scene = profile['scene']
    camera = scene['camera_left']
    lifts = [a for a in scene['actors'] if a['id'] == 0x25 and a['state'] == 0x40]
    assert len(lifts) == 3 and profile['foreground_opcodes']['26:b04b'] == 6
    base = P.fixture(P.bundle(raw),0,False,False)
    rows = []
    for actor in lifts:
        m = slim_fork(base)
        slot = actor['slot']
        right = camera+255
        N.put(m,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,
              ScreenRight_X_Pos=right&255,ScreenRight_PageLoc=right>>8)
        Direct.set_slot(m,'Enemy_X_Position',slot,actor['x']&255)
        Direct.set_slot(m,'Enemy_PageLoc',slot,actor['x']>>8)
        c = cpu_at(m,0x8b1a,232,0x21,x=slot+1)
        run(c,lambda z:(z.pc,z.sp) == (STOP,232))
        assert c.a == raw_x_bits(m,slot)
        fast = not (c.a>>4)&1
        # Only the admitted X leaf and its caller's admission instructions
        # differ. All three records are the source's optimized 32px type.
        saved = c.processorCycles+15-8 if fast else -9
        rows.append(dict(slot=slot,x=actor['x'],raw_x_bits=c.a,fast=fast,saved_cycles=saved))
    assert sum(row['fast'] for row in rows) == 2
    return dict(frame=scene['frame'], camera_left=camera, actors=rows,
                saved_cycles=sum(row['saved_cycles'] for row in rows))


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    raw = ROM.read_bytes()
    assert P.sha(raw) == PIN
    image, rows = link(raw,args.output)
    actor = with_bus(actor_cases,raw,image)
    print('Actor comparisons',actor,flush=True)
    generic = standalone([P.bundle(b) for b in (raw,image)])
    loops = whole(raw,image)
    print('Whole GameLoop',loops,flush=True)
    resumed = resumed_vectors(raw,image)
    print('Real resumed vectors',resumed,flush=True)
    vectors = qualify_vectors(raw,image)
    print('Real vectors',vectors,flush=True)
    paths = (Path(__file__),SOURCE,PROFILE,R/'src/object.s',R/'src/common.s',R/'src/native_platform16.s',
             R/'src/ryu_platform.s',R/'src/ryu_source_body.s',R/'src/zelda2_link_platform.s',
             R/'src/collision.s',R/'src/reset.s',R/'src/rogue_dawn_audio_scheduler_hooks_v5.s',
             R/'src/smb2_roster_common_audio_v9.s',R/'tools/reference/native_platform_box_1110_v1.s',
             R/'tools/reference/native_platform_direct_1110_v1.s')
    result = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(image),
                  patches=rows,actor=actor,standalone_cases=generic,whole_GameLoop=loops,vectors=vectors,
                  resumed_vectors=resumed,
                  native_peak=profile_cost(raw),
                  bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes()) for p in paths})
    (args.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
