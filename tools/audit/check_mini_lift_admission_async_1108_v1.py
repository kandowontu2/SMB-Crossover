"""Exercise actual IRQ and FF lag-NMI at reached fc7d lift admission boundaries."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_mini_lift_admission_fast_1108_v1 as F
from check_mini_busy_fire_interrupts_1108_v3 import lag_pcs


N = F.N
CPU = N.NesMPU
BASE_BUS = N.Bus
MANIFEST = F.ROOT/'build/mini-lift-admission-fast-1108/proof.json'
KERNEL = F.ROM.with_name('mini-lift.bin')
INGRESS_CALL = bytes.fromhex('a9cf8d6c01a9bb8d6d01a998205a01')
INGRESS_TEST = bytes.fromhex('a55c38e902c902')


def clone(c):
    # The proof examines events from the current cut onwards. Omit the cold
    # loader's accumulated write log from each independent fork.
    src = c.memory
    logs = {name:getattr(src,name) for name in ('writes','ram_writes','ppu_log','blocked')}
    try:
        for name in logs:
            setattr(src,name,[])
        m = N.fork(src)
    finally:
        for name, value in logs.items():
            setattr(src,name,value)
    z = CPU(memory=m, pc=c.pc)
    z.a, z.x, z.y, z.p, z.sp = c.a, c.x, c.y, c.p, c.sp
    z.processorCycles = c.processorCycles
    return z


def tags(c):
    return c.memory.rawtags[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1


def registers(c):
    return c.pc, c.a, c.x, c.y, c.p&0xef, c.sp


def actor_fields(bus):
    names = ('Enemy_Flag', 'Enemy_ID', 'Enemy_State', 'Enemy_X_Position', 'Enemy_PageLoc',
             'Enemy_Y_Position', 'Enemy_Y_HighPos', 'Enemy_Y_Speed', 'Enemy_Y_MoveForce',
             'Enemy_BoundBoxCtrl', 'PlatformCollisionFlag')
    return tuple(bytes(bus[F.address(bus.bundle,n):F.address(bus.bundle,n)+6]) for n in names)


def live(c):
    m = c.memory
    return (registers(c), tuple(m.rawtags), N.get(m, 'CurrentBank'), N.get(m, 'CurrentBankC'),
            bytes(m[3:11]), bytes(m[0x15a:0x17b]), bytes(m[0x101+c.sp:0x200]),
            bytes(m[0x200:0x304]), tuple(bytes(z) for z in m.ram), actor_fields(m))


def final(c):
    m = c.memory
    return (registers(c), tuple(m.rawtags), N.get(m, 'CurrentBank'), N.get(m, 'CurrentBankC'),
            bytes(m[0x15a:0x17b]), bytes(m[0x200:0x304]), tuple(bytes(z) for z in m.ram), actor_fields(m))


class Bus(BASE_BUS):
    in_handler = False

    def __getitem__(self, at):
        if self.in_handler and isinstance(at, int):
            assert not (self.rawtags[2]==2 and 0xc30b<=at<=0xc30d), ('ISR reads lift handshake', hex(at))
        return super().__getitem__(at)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--baseline', action='store_true', help='Bind the installed predecessor instead of the fast patch')
    parser.add_argument('--native-stack', action='store_true', help='Enter via the linked IdleLoop and GameLoop')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(exist_ok=True)
    receipt = json.loads(MANIFEST.read_text())
    raw = bytearray(F.ROM.read_bytes())
    assert F.sha(raw) == F.PIN == receipt['parent_SHA256']
    if not args.baseline:
        for patch in receipt['patches']:
            start = patch['file_offset']
            before, after = (bytes.fromhex(patch[key]) for key in ('old_hex','new_hex'))
            assert raw[start:start+len(before)] == before
            raw[start:start+len(after)] = after
        assert F.sha(raw) == receipt['expected_memory_only_SHA256']
    b = F.bundle(raw)
    idle, game_loop, game_core = (F.address(b,n) for n in ('IdleLoop','GameLoop','GameCoreRoutine'))
    fixed = raw[16+127*8192:16+128*8192]
    boot_sig = bytes((0x20,idle&255,idle>>8))
    boot_calls = [0xe000+i for i in range(len(fixed)-2) if fixed[i:i+3]==boot_sig]
    boot_jsr, = boot_calls
    game_return = idle+12 if args.native_stack else 0x5b00
    kernel = KERNEL.read_bytes()
    native_gate = kernel.index(INGRESS_CALL)
    assert kernel[native_gate-9:native_gate-2] == INGRESS_TEST
    ingress, epoch = 0xa000+native_gate-9, 0xa000+native_gate+len(INGRESS_CALL)
    spans = [(0x80|bank, pc, pc+size, role) for role, bank, pc, size, _ in F.SPANS]
    for name, size in (('InitEnemyObject', 20), ('CrossoverLevelEnemyInit', 16),
                       ('CheckpointEnemyID', 54), ('InitVertPlatform', 34)):
        row = b['syms'][name]
        segment = b['segs'][row['seg']]
        pc = F.address(b,name)
        offset = int(segment['ooffs'],0)+pc-int(segment['start'],0)
        spans.append((0x80|((offset-16)//8192), pc, pc+size, name))
    cuts = Counter()
    min_handler = 255
    min_foreground = 255
    nested_contexts = {}
    nested_failures = []
    outcomes = {}
    early_map_commits = Counter()

    def run_handler(c, kind, scenario, role, nested_origin=None):
        nonlocal min_handler
        m = c.memory
        at = (c.pc, c.sp)
        before = live(c)
        skipped = N.get(m,'NmiSkipped')
        log = len(m.writes)
        if kind == 'lag_FF':
            assert N.get(m,'NmiDisable') == 255
            c.nmi()
        else:
            assert not c.p&4
            c.irq()
            assert c.pc == 0x8000 and tags(c) == 254
        lag_hits = 0
        m.in_handler = True
        for _ in range(16000):
            if (c.pc,c.sp)==at:
                break
            min_handler = min(min_handler,c.sp)
            if kind == 'lag_FF':
                assert c.pc != regular
                lag_hits += c.pc == lag
                if not c.p&4:
                    key = tags(c),c.pc
                    if key not in nested_contexts or c.sp<nested_contexts[key][0].sp:
                        nested_contexts[key] = (clone(c),dict(scenario=scenario,role=role,foreground_pc=at[0],foreground_SP=at[1]))
            assert m[c.pc], (kind,scenario,role,at,hex(c.pc))
            CPU.step(c)
        else:
            raise AssertionError(('ISR bound',kind,scenario,role,at,hex(c.pc)))
        m.in_handler = False
        after = live(c)
        changed = [i for i,(x,y) in enumerate(zip(before,after)) if x!=y]
        if nested_origin is not None and changed:
            smc_bytes = [dict(address=0x15a+i,before=x,after=y) for i,(x,y) in
                         enumerate(zip(before[5],after[5])) if x!=y]
            nested_failures.append(dict(origin=nested_origin,handler_pc=at[0],handler_SP=at[1],
                                        state_sections_changed=changed,smc_bytes=smc_bytes,
                                        exact_IRQ_overwrites=[[a,v] for a,v in m.writes[log:] if 0x15a<=a<0x17b]))
            return False
        early_commit = bool(changed)
        if early_commit:
            # The genuine lag audio owner restores hardware from CurrentBank.
            # The only allowed mismatch is one instruction after foreground
            # has updated that shadow but just before the same STA $5115.
            assert kind=='lag_FF' and role=='SMC_transport' and changed==[1], (kind,scenario,role,at,changed)
            assert bytes(m[c.pc:c.pc+3])==b'\x8d\x15\x51', (scenario,at)
            assert before[1][1]!=before[2] and after[1][1]==before[2]==c.a, (scenario,at,before[1:3],after[1:3],c.a)
            assert before[1][:1]+before[1][2:] == after[1][:1]+after[1][2:]
            early_map_commits[(c.pc,before[1][1],after[1][1])] += 1
        assert N.get(m,'NmiSkipped') == (skipped+(kind=='lag_FF'))&255
        assert lag_hits == (kind=='lag_FF')
        assert not any(0x200<=at<0x304 or at==0x4014 for at,_ in m.writes[log:])
        cuts[('nested_IRQ' if nested_origin is not None else kind,role)] += 1
        return early_commit

    def complete(c):
        for _ in range(35000):
            if c.pc==game_return:
                return final(c)
            assert c.memory[c.pc], hex(c.pc)
            CPU.step(c)
        raise AssertionError(('GameCore bound',hex(c.pc)))

    N.Bus = Bus
    try:
        seed = F.fixture(b,0,False,False)
        lag, regular = lag_pcs(seed)
        scenarios = [('seen_left',560,1,5,0,False,False,0x31),
                     ('seen_right_I1',864,4,5,1,False,False,0x35),
                     ('spawn_left',560,0,5,0,False,False,0x31),
                     ('retarget_right',864,3,5,1,False,True,0x31),
                     ('all_slots_busy',688,1,5,1,True,False,0x31),
                     ('wrong_area',560,0,0,0,False,False,0x31),
                     ('outside_window',608,1,5,0,False,False,0x31)]
        for scenario, px, seen, area, mode, busy, retarget, p in scenarios:
            base = N.fork(seed)
            F.setup_main(base,px,seen,mode,area)
            N.put(base,NmiDisable=255)
            for slot in range(6 if busy else 1 if retarget else 0):
                for name,value in dict(Enemy_Flag=1,Enemy_ID=0x25 if retarget else 6,
                        Enemy_State=0x40 if retarget else 0,Enemy_X_Position=688&255,
                        Enemy_PageLoc=688>>8,Enemy_Y_Position=168,Enemy_Y_HighPos=1,
                        Enemy_BoundBoxCtrl=5 if retarget else 3).items():
                    base[F.address(b,name)+slot] = value
            if retarget:
                base.ram[2][0x30b] = 1
            reached = {}
            resume = []
            active = False
            terminal = []
            entries = {}

            class Trace(CPU):
                def step(self):
                    nonlocal active, min_foreground
                    tag, pc = tags(self),self.pc
                    if pc in (game_loop,game_core) and tag==254:
                        entries['GameLoop' if pc==game_loop else 'GameCoreRoutine'] = self.sp
                    if tag==3 and pc==ingress:
                        active = True
                    if tag==3 and pc==epoch:
                        active = False
                    if active:
                        role = ('kernel_ingress' if tag==3 and ingress<=pc<epoch else
                                'SMC_transport' if 0x15a<=pc<0x17b else
                                next((role for t,a,z,role in spans if t==tag and a<=pc<z),None))
                        if role:
                            key = (tag,pc,tuple(self.memory.rawtags),N.get(self.memory,'CurrentBank'),self.p&4)
                            if key not in reached:
                                reached[key] = role
                                min_foreground = min(min_foreground,self.sp)
                                for kind in ('lag_FF','IRQ'):
                                    if kind=='IRQ' and self.p&4:
                                        continue
                                    fork = clone(self)
                                    early_commit = run_handler(fork,kind,scenario,role)
                                    first = not any(r==role and k==kind for r,k,_ in resume)
                                    if first or early_commit or (role=='SPAWN' and self.memory[self.pc] in (0x95,0x8e)):
                                        resume.append((role,kind,fork))
                    result = CPU.step(self)
                    if self.pc==game_return:
                        terminal.append(final(self))
                    return result

            if args.native_stack:
                loop_call = bytes((0x20,game_loop&255,game_loop>>8))
                assert bytes(base[idle+9:idle+12])==loop_call
                cpu = Trace(memory=base,pc=idle)
                cpu.sp,cpu.p = 255,p
                cpu.stPushWord(boot_jsr+2)       # Actual reset JSR IdleLoop return word.
                for _ in range(35000):
                    if cpu.pc==game_return:
                        break
                    assert base[cpu.pc], hex(cpu.pc)
                    cpu.step()
                else:
                    raise AssertionError(('native GameLoop bound',scenario,hex(cpu.pc)))
                assert cpu.sp==252 and entries['GameLoop']==250, (scenario,entries,cpu.sp)
            else:
                N.NesMPU = Trace
                try:
                    N.invoke(base,'GameCoreRoutine',x=0,y=0,p=p)
                finally:
                    N.NesMPU = CPU
            assert len(terminal)==1 and reached
            for role,kind,fork in resume:
                assert complete(fork)==terminal[0], ('resumed gameplay changed',scenario,role,kind)
            outcomes[scenario] = dict(cuts=len(reached),resumed=len(resume),
                                      roles=sorted(set(reached.values())),entry_SP=entries)
    finally:
        N.Bus = BASE_BUS

    for cut,origin in nested_contexts.values():
        run_handler(cut,'IRQ','nested','lag_handler',nested_origin=origin)
    assert any(k[0]=='nested_IRQ' for k in cuts)
    result = dict(passed=not nested_failures, single_level_passed=True, source_CPU_only=True,
                  ROM_written=False, parent_SHA256=F.PIN,baseline=args.baseline,
                  stack_entry='actual reset JSR return + linked IdleLoop/GameLoop' if args.native_stack
                              else 'deliberately deep synthetic N.invoke initial SP $E0',
                  boot_jsr=boot_jsr, game_return=game_return,
                  memory_image_SHA256=F.sha(raw), scenarios=outcomes,
                  cuts={kind:{role:n for (k,role),n in cuts.items() if k==kind}
                        for kind in ('lag_FF','IRQ','nested_IRQ')},
                  min_foreground_SP=min_foreground,min_ISR_SP=min_handler,
                  actual_lag_PC=lag,forbidden_regular_NMI_PC=regular,
                  nested_failures=nested_failures,
                  early_A_window_commits=[dict(pc=pc,from_tag=old,to_tag=new,cuts=count)
                                          for (pc,old,new),count in early_map_commits.items()],
                  retained_negative='The first run required instantaneous rawtags equality and failed at seen_left '
                                    'lag FF, PC $0166 and SP $B5, with a hardware map difference only. '
                                    'The exact STA $5115 successor and the unchanged whole return are qualified '
                                    'for each permitted early publish in this receipt.',
                  bindings={str(f):F.sha(f.read_bytes()) for f in
                            (Path(__file__),MANIFEST,F.ROM,KERNEL,F.ROOT/'src/reset.s')},
                  scope='Actual GameCore instruction boundaries through lift admission and native construction, '
                        'real vector/RTI, published lift handshake unread by handlers. No native video qualification.')
    name = ('baseline' if args.baseline else 'proof')+('-native-stack' if args.native_stack else '')
    destination = out/(name+'.json')
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=result['passed'], totals={kind:sum(group.values()) for kind,group in result['cuts'].items()},
                          resumed=sum(q['resumed'] for q in outcomes.values()), min_ISR_SP=min_handler,
                          nested_failures=nested_failures[:3], nested_failure_count=len(nested_failures))))


if __name__=='__main__':
    main()
