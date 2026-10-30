"""Real resident foot/wall executions: native differential and actual ISR cuts."""
from pathlib import Path
import itertools, json, sys, traceback

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
import ff_joint_typed_controls_v1 as T
from ff_wram_host_isr_v4 import clone
import ff_host_pickups_vectors_v2 as V
from check_tmnt_render_oa import address, location

H, sha = T.H, T.sha
P = R / 'build/ff-joint-full-render-v2'
O = R / 'build/ff-joint-terrain-hooks-1030-v3'
H.O = O / 'joint'


def direct(m, name, a=0x55, x=0, y=0, flags=0x71, observer=None):
    c = H.NesMPU(memory=m, pc=address(m.bundle, name))
    c.a, c.x, c.y, c.p, c.sp = a, x, y, flags, 224
    c.stPushWord(0x5aff)
    live = bytes(m[0x1e1:0x200])
    c, low = H.finish(m, c, observer)
    assert c.sp == 224 and bytes(m[0x1e1:0x200]) == live
    return c, low


def sig(m, c):
    # Unused stack slots need not retain old values; live SMC/caller slots do.
    addresses = [*range(0x100), *range(0x15a, 0x17b), *range(0x1e1, 0x200),
                 *range(0x200, 0x800), *range(0x5c00, 0x8000)]
    excluded = set(range(0x100, 0x200)) | set(range(0x5114, 0x5118))
    excluded |= {address(m.bundle, n) for n in ['CurrentBank', 'CurrentBankC']}
    writes = [(a, v) for a, v in m.writes if a not in excluded]
    return (bytes(m[a] for a in addresses), writes,
            (c.a, c.x, c.y, c.p, c.sp), m.rawtags[:], m.ram[3][:])


def fixture(seed, selected, link=0, clearance=0, engine=8, tile=0):
    m = T.copy(seed)
    H.put(m, SelectedCharacter=selected, Z2Variant=link, SmClearance=clearance,
          GameEngineSubroutine=engine, Player_X_Position=112, Player_PageLoc=0,
          Player_Y_Position=160, Player_Y_HighPos=1, PlayerSize=0, PlayerStatus=0,
          RgCrouch=0, CrouchingFlag=0, R0=1, R1=0xa6, Local_eb=0,
          Player_X_Speed=25, Player_X_Scroll=3, MmVX=1, Player_CollisionBits=255)
    for at in range(address(m.bundle, 'Block_Buffer_1'), address(m.bundle, 'Block_Buffer_2') + 208):
        m[at] = tile
    m.writes.clear()
    m.ram_writes.clear()
    return m


def foreign(old, new):
    seeds = [T.base(b) for b in [old, new]]
    contexts = [(n, 0, 0) for n in range(33) if n != 22]
    contexts += [(4, 1, 0), (7, 0, 128)]
    flags = [0x30 | n for n in range(256) if n & 0x30 == 0 and n & ~0xcf == 0]
    # All64 live 6502flag combinations on every changed cold branch; native
    # identities get representative pairs, plus both real foot indices/cells.
    rows = []
    for selected, link, clearance in contexts:
        ps = flags if selected in [4, 7, 26, 28] else [0x30, 0x71]
        for y, tile, p in itertools.product([0, 1], [0, 0xc1], ps):
            states = []
            cycles = []
            for seed in seeds:
                m = fixture(seed, selected, link, clearance, tile=tile)
                c, _ = direct(m, 'GmFootResident', y=y, flags=p)
                states.append(sig(m, c))
                cycles.append(c.processorCycles)
            assert states[0] == states[1], ('foreign foot differential', selected, link, clearance, y, tile, p,
                 [(a,b) for a,b in zip(states[0][0],states[1][0]) if a!=b][:10], states[0][2],states[1][2])
            rows.append([selected, link, clearance, y, tile, p, cycles[1] - cycles[0]])
    return dict(cases=len(rows), all_returned_APXY_maps_application_writes_and_live_SMC_exact=True,
                additional_CPU_range=[min(x[-1] for x in rows), max(x[-1] for x in rows)], rows=rows)


def own(new):
    seed = T.base(new)
    rows = []
    for engine, paused, timer, dead, y, tile in itertools.product([4, 5, 8], [0, 1], [0, 1], [0, 1], [0, 1], [0, 0xc1]):
        active = engine == 8 and not (paused or timer or dead)
        pair = []
        for wrapped in [False, True]:
            m = fixture(seed, 22, engine=engine, tile=tile)
            H.put(m, GamePauseStatus=paused, TimerControl=timer, MmDeathFlag=dead)
            m.writes.clear()
            if wrapped:
                c, _ = direct(m, 'GmFootResident', y=y)
            else:
                # The selector's CMP#22/BEQ path leaves selected22,C1;
                # FF's wrapper restores this exact entryP before its consumer.
                c, _ = H.invoke(m, 'FwHostFeet' if active else 'BlockBufferColli_Feet', a=22, x=0, y=y, p=0x71)
            # Different legal SFC construction publishes different own target
            # operands, so compare actual application outputs, not those dead
            # dispatch addresses. Foreign old/new above includes all33 SMC.
            s = sig(m, c)
            pair.append((s[0][:0x100] + s[0][0x100+33:], s[1], s[2], s[3], s[4]))
            H.exact(m)
        assert pair[0] == pair[1], ('FF foot active/native guard', engine, paused, timer, dead, y, tile)
        rows.append([engine, paused, timer, dead, y, tile, active])
    return dict(cases=len(rows), actual_resident_selector_not_staged=True, rows=rows)


def wall(old, new):
    seeds = [T.base(b) for b in [old, new]]
    rows = []
    for selected, engine, side, p in itertools.product([0, 1, 2, 3, 4, 7, 9, 13, 17, 18, 19, 20, 21, 23, 26, 28, 32], [4, 5, 8], [1, 2], [0x30, 0x71]):
        pair, cycles = [], []
        for seed in seeds:
            m = fixture(seed, selected, engine=engine)
            H.put(m, R0=side)
            m.writes.clear()
            c, _ = direct(m, 'SamusStopAtWall', a=selected, flags=p)
            pair.append(sig(m, c))
            cycles.append(c.processorCycles)
        assert pair[0] == pair[1], ('foreign wall differential', selected, engine, side, p)
        rows.append([selected, engine, side, p, cycles[1] - cycles[0]])
    return dict(cases=len(rows), additional_CPU_range=[min(r[-1] for r in rows),max(r[-1] for r in rows)], rows=rows)


def isr(new):
    seed = T.base(new)
    targets = ['FarCallCommon', 'DkHostFeetUnionRouter', 'FwSvcFeet', 'FwSvcActive', 'FwHostFeet', 'FwCallEnter',
               'FfHostFeet', 'FwSvcWall', 'FwHostWall']
    points = {(address(new, n), ((location(new, n)-16)//8192)|128): n for n in targets if n != 'FfHostFeet'}
    points[(address(new, 'FfHostFeet'), 3)] = 'FfHostFeet'
    snapshots = []
    contexts = [('GmFootResident',22), ('GmFootResident',4), ('GmFootResident',7),
                ('GmFootResident',26), ('GmFootResident',28), ('SamusStopAtWall',22), ('SamusStopAtWall',4)]
    for entry, selected in contexts:
        m = fixture(seed, selected, link=1 if selected==4 else 0, tile=0xc1)
        seen = set()
        def observe(mem, c, step):
            tag = mem.rawtags[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
            key = (c.pc,tag)
            op = bytes(mem[c.pc:c.pc+3])
            if step<18 or key in points or op in [b'\x8d\x15\x51',b'\x8d\x16\x51']:
                reason=(key,op)
                if reason not in seen:
                    seen.add(reason);snapshots.append((entry,selected,step,clone(mem,c)))
        direct(m, entry, a=selected, observer=observe)
    rows=[]
    for entry, selected, step, (state,cpu) in snapshots:
        for kind, lag in itertools.product(['NMI','IRQ'],[0,255]):
            m,c=clone(state,cpu);H.put(m,NmiDisable=lag)
            if kind=='IRQ' and c.p&c.INTERRUPT:continue
            result=V.interrupt(m,c,kind)
            H.finish(m,c);H.exact(m)
            rows.append(dict(entry=entry,selected=selected,step=step,lag=lag,**result))
    return dict(real_interruptions=len(rows), snapshots=len(snapshots), all33SMC_live_page1_APXY_rawmaps_verified=True, rows=rows)


def main():
    out=O/'terrain-controls-v1.json';assert not out.exists()
    p=dict(passed=False,native=False,admitted=False,checks={})
    try:
        closure=json.loads((O/'source-closure.json').read_text())
        for f,h in closure['bindings'].items():assert sha(f)==h,f
        old=H.C.qualified(P/'joint/candidate.nes');new=H.C.qualified(O/'joint/candidate.nes')
        for name,fn in [('foreign_feet',lambda:foreign(old,new)),('FF_feet',lambda:own(new)),
                        ('foreign_walls',lambda:wall(old,new)),('actual_ISR',lambda:isr(new))]:
            p['checks'][name]=fn();print(name,'PASS',flush=True)
        p['passed']=True
    except Exception as e:p.update(error=repr(e),traceback=traceback.format_exc())
    p['bindings']={str(f.resolve()):sha(f)for f in [Path(__file__),Path(T.__file__),Path(H.__file__),Path(V.__file__),
       O/'source-closure.json',O/'joint/candidate.nes',O/'joint/candidate.dbg',P/'joint/candidate.nes',P/'joint/candidate.dbg']}
    target=out if p['passed']else O/'terrain-controls-negative-v1.json';assert not target.exists()
    target.write_text(json.dumps(p,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=p['passed'],error=p.get('error'),path=str(target))),flush=True)
    assert p['passed']


if __name__=='__main__':main()
