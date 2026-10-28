"""Compile only the dedicated Rogue kinematics leaf and compare actual ROM CPU.

No emulator, host game, PPU, native IRQ, collision adapter or live dispatch.
All original-vs-port differences use an explicit address projection. The source
07A0/0AA9 overlapping BIT reads are represented, not silently masked flags.
"""
from pathlib import Path
import argparse
import itertools
import json
import re
import subprocess
from py65.devices.mpu6502 import MPU
import rogue_dawn_map_v1 as ref
import rogue_dawn_leaf_controls_v1 as original

ROOT = Path(__file__).resolve().parents[1]
PROJECTION = {**{0x0300+i: 0x5c00+i for i in range(32)},
              **{0x0680+i: 0x5c20+i for i in range(7)},
              0x6878:0x5fb0, 0x6879:0x5fb1, 0x687a:0x5fb2, 0x6877:0x5fb3,
              0x0106:0x5fb4, 0x0107:0x5fb5, 0x010e:0x5c27,
              0x12:0x5c28, 0x14:0x5c29, 0xcd:0x5c2a, 0x780e:0x5c2b,
              0x4d:0x5c2c, 0x7d:0x5c2d, 0x2d:0x5c2e, 0x4b:0x5c2f,
              0:0x5c30, 1:0x5c31, 2:0x5c32, 3:0x5c33, 0x16:0x5c34,
              0x07a0:0x5c38, 0x0aa9:0x5c39}


def build(directory):
    directory.mkdir(parents=True, exist_ok=True)
    cfg = directory/'kernel.cfg'
    cfg.write_text('MEMORY { K: start=$B000,size=$1000,file=%O; }\nSEGMENTS { ROGUE_DAWN_CORE: load=K,type=ro; }\n')
    ca = ROOT/'tools/Windows/cc65/bin/ca65.exe'
    ld = ROOT/'tools/Windows/cc65/bin/ld65.exe'
    subprocess.run([str(ca), '-g', '-I', str(ROOT/'src'), str(ROOT/'src/rogue_dawn.s'),
                    '-o', str(directory/'kernel.o')], check=True, cwd=ROOT)
    subprocess.run([str(ld), '-C', str(cfg), '-o', str(directory/'kernel.bin'),
                    '-Ln', str(directory/'kernel.lbl'), '--dbgfile', str(directory/'kernel.dbg'),
                    str(directory/'kernel.o')], check=True, cwd=ROOT)
    labels = {}
    for line in (directory/'kernel.lbl').read_text().splitlines():
        m = re.match(r'al ([0-9A-Fa-f]+) \.(\S+)', line)
        if m:
            labels[m[2]] = int(m[1], 16)
    return (directory/'kernel.bin').read_bytes(), labels


def port_call(code, labels, name, source_state, a=0, x=0, y=0, p=0x30, stop=None):
    m = bytearray(65536)
    m[0xb000:0xb000+len(code)] = code
    for address, value in source_state.items():
        assert address in PROJECTION, f'unprojected input {address:04X}'
        m[PROJECTION[address]] = value
    before = bytes(m)
    c = MPU(memory=m, pc=labels[name])
    c.a, c.x, c.y, c.p, c.sp = a, x, y, p, 0xfd
    c.stPushWord(0x5aff)
    for _ in range(10000):
        if c.pc == (labels[stop] if stop else 0x5b00):
            permitted = set(PROJECTION.values()) | set(range(0x100, 0x200))
            assert all(v == before[i] for i, v in enumerate(m[:0x8000]) if i not in permitted), 'foreign RAM write'
            return c, m
        assert m[c.pc] != 0, f'port BRK {c.pc:04X}'
        c.step()
    raise AssertionError(f'port did not return {name}: {c.pc:04X}')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=ROOT/'build/rogue-dawn-kernel-v1/controls.json')
    args = ap.parse_args()
    proof = dict(passed=False, source_only=True, native_run=False, scope=__doc__)
    try:
        code, labels = build(args.output.parent)
        raw = ref.ROM.read_bytes()
        assert ref.digest(raw) == ref.EXPECTED
        proof.update(rom=ref.binding(ref.ROM), kernel_bytes=len(code), kernel_start='B000',
                     kernel_end_exclusive=f'{0xb000+len(code):04X}', projection={f'{k:04X}': f'{v:04X}' for k,v in PROJECTION.items()},
                     inputs=[ref.binding(ROOT/p) for p in ['src/rogue_dawn.s','src/rogue_dawn_core.s','src/rogue_dawn_state.inc',
                              'tools/rogue_dawn_map_v1.py','tools/rogue_dawn_leaf_controls_v1.py','tools/rogue_dawn_kernel_controls_v1.py']],
                     binary=ref.binding(args.output.parent/'kernel.bin'))
        costs = {}
        count = 0
        def compare(name, pc, state, **kw):
            nonlocal count
            c, m = original.call(raw, pc, state, **kw)
            d, n = port_call(code, labels, name, state, **kw)
            assert all(v == state.get(i,0) for i,v in enumerate(m[:0x8000])
                       if i not in PROJECTION and not 0x100 <= i < 0x200), 'unprojected source RAM write'
            for source, target in PROJECTION.items():
                assert m[source] == n[target], f'{name} RAM {source:04X}->{target:04X}: {m[source]:02X}!={n[target]:02X}; {state}'
            assert (c.a,c.x,c.y,c.p,c.sp) == (d.a,d.x,d.y,d.p,d.sp), f'{name} AXYP/SP mismatch {(c.a,c.x,c.y,c.p,c.sp)} {(d.a,d.x,d.y,d.p,d.sp)}'
            costs.setdefault(name, []).append([c.processorCycles, d.processorCycles])
            count += 1
        for gear, env, action, carry, probe in itertools.product([0,2,8,10], [0,64,128,192], [0,1,2,3], [0,1], [0,64,128,255]):
            compare('RdStartJump', 0xcfc3, {0x6878:gear,0x780e:env,0x0300:action,0x07a0:probe}, p=0x30|carry)
        for function,pc in [('RdSetGravity',0xdc3e),('RdSetMaxSpeed',0xdc61)]:
            for a,env,probe in itertools.product([0,7,18,24,26,56,255], [0,64,128,192], [0,64,128,255]):
                compare(function,pc,{0x780e:env,0x0aa9:probe},a=a)
        for vy,gravity,linear,phase in itertools.product([0,1,4,5,6,0xf9,0xfa,0xfb,0xfc,0xfe,0xff], [0,5,7,18,24,26,56,255], [0,1,127,255], [0,1,127,255]):
            compare('RdVerticalAccelerate',0xe3a5,{0x0308:vy,0x0314:gravity,0x0312:linear,0x0310:phase})
        for vx,accel,maximum,linear,phase in itertools.product([0,1,3,0xfc,0xfe,0xff], [0,0x30,0xd0], [0,0xa,0x12,0x18,0xff], [0,1,127,255], [0,255]):
            compare('RdHorizontalAccelerate',0xe3e5,{0x0309:vx,0x0315:accel,0x0316:maximum,0x0313:linear,0x0311:phase})
        for gear,env,held,previous,vy in itertools.product([0,16,18], [0,128], [0,128], [0,128], [0xfc,0xfe,0,2]):
            compare('RdSpringAdmitted',0xa2ba,{0x6878:gear,0x780e:env,0x14:held,0xcd:previous,0x0308:vy})
        for held,previous,vy,distance in itertools.product([0,128], [0,128], [0xfc,0xfe,0,2], [0,31,32,64]):
            compare('RdSpringRelease',0xa2de,{0x14:held,0xcd:previous,0x0308:vy,0x030f:distance})
        for current,maximum in itertools.product([0,1,249,250,251,254,255], repeat=2):
            compare('RdAddMissileTank',0xdd97,{0x6879:current,0x687a:maximum},a=5)
        for vy,fraction in itertools.product([0,0xfc,1,255],[0,255]):
            compare('RdStopVertical',0xd147,{0x0308:vy,0x0312:fraction})
        for pose in [0,7,12,22,255]:
            compare('RdSetAnimation',0xcf6b,{},a=pose)
        for held,facing,action,pose in itertools.product(range(16), [0,1], [0,2,6], [0,12,53]):
            compare('RdAirControl',0xd055,{0x14:held,0x4d:facing,0x0300:action,0x0305:pose})
        for facing in [0,1]:
            compare('RdSetGroundAcceleration',0xccb7,{},x=facing)
        # Genuine original D015 continuation versus newly callable prefix RTS.
        # Source stop is BEFORE the next native air-control call. The adapter
        # function adds its own RTS; compare both real stack endpoints explicitly.
        cut = []
        for held,vy,distance,fraction in itertools.product([0,128], [0xfc,0xfe,0,2], [0,31,32,64], [0,255]):
            state={0x14:held,0x0308:vy,0x030f:distance,0x0312:fraction}
            c,m=original.call(raw,0xd002,state,stop=0xd015)
            d,n=port_call(code,labels,'RdCutOrdinaryJump',state)
            assert c.sp==0xfb and d.sp==0xfd
            assert (c.a,c.x,c.y,c.p)==(d.a,d.x,d.y,d.p)
            assert all(m[s]==n[t] for s,t in PROJECTION.items())
            cut.append([c.processorCycles,d.processorCycles])
        proof['ordinary_jump_cut_prefix_cases'] = len(cut)
        proof['ordinary_jump_cut_cost'] = {'source_to_D015_min':min(v[0] for v in cut),'source_to_D015_max':max(v[0] for v in cut),
                                         'port_including_RTS_min':min(v[1] for v in cut),'port_including_RTS_max':max(v[1] for v in cut)}
        ground = []
        for action,vy,fraction,gravity in itertools.product([0,1,2,3,6], [0,1,2,3,4,5], [0,1,127,255], [0,24]):
            state={0x0300:action,0x0308:vy,0x0312:fraction,0x0314:gravity}
            c,m=original.call(raw,0xe2e8,state,stop=0xe31a)
            d,n=port_call(code,labels,'RdGroundCollisionResponse',state)
            assert c.sp==0xfb and d.sp==0xfd
            assert (c.a,c.x,c.y,c.p)==(d.a,d.x,d.y,d.p)
            assert all(m[s]==n[t] for s,t in PROJECTION.items())
            ground.append([c.processorCycles,d.processorCycles])
        proof['ground_collision_prefix_cases'] = len(ground)
        proof['ground_collision_cost'] = {'source_to_E31A_min':min(v[0] for v in ground),'source_to_E31A_max':max(v[0] for v in ground),
                                         'port_including_RTS_min':min(v[1] for v in ground),'port_including_RTS_max':max(v[1] for v in ground)}
        proof['cases'] = count
        proof['total_differential_cases'] = count+len(cut)+len(ground)
        proof['integration_limits'] = ['No host whole-caller/IRQ or NMI/PPU timing yet; standalone source component only.',
                                      'Input Dflag clear. Original helper incoming Carry is observable and tested bothways atJump.',
                                      'Logical0AA9 read is hardwaremirror02A9; the flags-probe projection supplies that byte explicitly.',
                                      'No collision probes, player pixel movement/camera, wall admission, full weapon/contact/render or actual audio playback.']
        proof['whole_leaf_costs'] = {name: dict(cases=len(v),original_min=min(x[0] for x in v),original_max=max(x[0] for x in v),
                                              port_min=min(x[1] for x in v),port_max=max(x[1] for x in v),
                                              delta_min=min(x[1]-x[0] for x in v),delta_max=max(x[1]-x[0] for x in v))
                                     for name,v in costs.items()}
        proof['passed'] = True
    except Exception as e:
        proof['error'] = repr(e)
        raise
    finally:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:proof[k] for k in ['passed','kernel_bytes','kernel_end_exclusive','cases','whole_leaf_costs']}))


if __name__ == '__main__':
    main()
