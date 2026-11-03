"""Bind source-derived gravity512 and compose bounded ballistic motion episodes."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from py65.devices.mpu6502 import MPU
import port_mini_mario_ground_x_1103_v2 as G

ROOT = G.ROOT
OUT = ROOT/'build/mini-mario-motion-1103-v7'
Y = ROOT/'build/mini-mario-motion-1103-v5'
DEFAULTS = ROOT/'build/mini-mario-defaults-1103-v6'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    defaults = json.loads((DEFAULTS/'receipt.json').read_text())
    assert defaults['passed'] and defaults['default_hold_gravity'] == 512
    code = (Y/'motion-xy.bin').read_bytes()
    assert G.sha(code) == 'aadbb7eb45b0c00e92f1c39a4e16d10b8a6f7f21207e05a127a47f50d898d598'
    c = (Y/'original-air-y.c').read_bytes()
    (OUT/'original-air-y.c').write_bytes(c)
    subprocess.run(['C:/Strawberry/c/bin/gcc.exe','-std=c11','-O2','-Wall','-Wextra',
        str(OUT/'original-air-y.c'),'-o',str(OUT/'original-air-y.exe')],check=True)
    labels = {line.split()[2].lstrip('.'):int(line.split()[1],16)
        for line in (Y/'motion-xy.lbl').read_text().splitlines()}
    cpu = MPU()
    cpu.memory[0x8000:0x8000+len(code)] = code
    cases = bytearray()
    actuals = bytearray()
    bounds = [10**9,0]
    def invoke(entry):
        cpu.pc,cpu.sp,cpu.p = labels[entry],0xFD,0x20|((len(cases)&1)*0xC1)
        cpu.memory[0x1FE:0x200] = [0xFF,0x5A]
        start = cpu.processorCycles
        steps = 0
        while cpu.pc != 0x5B00:
            cpu.step()
            steps += 1
            assert steps < 220
        assert cpu.sp == 0xFF
        cycles = cpu.processorCycles-start
        bounds[0],bounds[1] = min(bounds[0],cycles),max(bounds[1],cycles)
    def test(x,y,dy,held,buttons,bounce,nc,mode,queued=13,attached=1):
        seed = struct.pack('<hhhBBBBBBhB',x,y,dy,held,buttons,bounce,nc,queued,attached,512,mode)
        cpu.memory[0x200:0x202] = seed[:2]
        cpu.memory[0x220:0x22C] = seed[2:14]
        cpu.memory[0x230] = mode
        invoke('air_y')
        actual = bytes(cpu.memory[0x220:0x225]+cpu.memory[0x228:0x22A])
        assert bytes(cpu.memory[0x200:0x202]) == seed[:2]
        cases.extend(seed)
        actuals.extend(actual)
        return struct.unpack('<hhBBB',actual)
    for mode in range(2):
        for y in range(-20480,8193):
            for held in range(2):
                for buttons in range(2):
                    for bounce in range(2):
                        test(5602 if y&1 else -5602,y,(-128,0,128)[y%3],held,buttons,bounce,0,mode)
    for x in range(-5602,5603):
        for bounce in range(2):
            test(x,0,0,1,1,bounce,0,1,attached=0)
    direct_cases = len(cases)//15
    episodes = []
    for movement,start_xvel,xbuttons in (('stationary',0,0),('walk_right',3665,2),
            ('run_right',5602,6),('run_left',-5602,5),('accelerate_run',0,6)):
        for hold_frames in (1,2,4,8,16,32,64):
            y,hold,mode,queued,attached = 0,1,1,13,0
            xvel = start_xvel
            position = minimum = 176*16
            mode_changed = False
            start_case = len(cases)//15
            for frame in range(1,161):
                y,dy,hold,queued,attached = test(xvel,y,0,hold,int(frame<=hold_frames),0,0,mode,queued,attached)
                position += dy
                minimum = min(minimum,position)
                mode = int(queued != 0)
                mode_changed |= mode == 0
                cpu.memory[0x200:0x208] = struct.pack('<hhBBBB',xvel,0,xbuttons,0,7,0)
                invoke('air_x')
                xvel = struct.unpack('<h',bytes(cpu.memory[0x200:0x202]))[0]
                if position >= 176*16 and y > 0:
                    break
            else:
                raise AssertionError(('No ballistic return',movement,hold_frames))
            assert mode_changed and attached == 0
            episodes.append(dict(movement=movement,held_frames=hold_frames,updates=frame,
                maximum_rise_subpixels=176*16-minimum,maximum_rise_pixels=(176*16-minimum)/16,
                source_fall_transition=True,cases=len(cases)//15-start_case))
    reference = subprocess.run([str(OUT/'original-air-y.exe')],input=cases,capture_output=True,check=True).stdout
    assert len(reference) == len(actuals)
    for offset in range(0,len(reference),7):
        assert reference[offset:offset+7] == actuals[offset:offset+7], (
            offset//7,cases[offset//7*15:offset//7*15+15].hex(),
            actuals[offset:offset+7].hex(),reference[offset:offset+7].hex())
    result = dict(passed=True,code_bytes=len(code),code_sha256=G.sha(code),changed_code_bytes=0,
        source_default_hold_gravity=512,source_default_receipt_SHA256=G.sha((DEFAULTS/'receipt.json').read_bytes()),
        direct_cases=direct_cases,total_Y_cases=len(cases)//15,ballistic_episodes=episodes,
        result_sha256=hashlib.sha256(actuals).hexdigest(),cycles=bounds,
        scope='Previously assembled842B component unchanged. Source-derived GB Studio default512 bound; literal C oracle matches all supported Y values and held/force/input branches plus full horizontal-boost velocity domain.35 composed Y-before-X ballistic episodes use original jump initialization values and original queued fall transition; actor/terrain collisions are absent. Ballistic return is not a native landing or platform crossing.',
        traversal_observation='Unscaled source motion tops below48px in these episodes. The native1-1 tall pipes require an intended traversal adaptation, likely the user-requested innate wall grab, before admission; no helper need or crossing is certified.',
        remaining='Actual GB machine-code reference, complete Main/caller and terrain/wall-grab/native lifecycle/render/audio/menu/full1-1. No ROM produced, installed bytes unchanged.')
    (OUT/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='ballistic_episodes'},indent=2))
    print('full-hold ballistic peaks:',[(e['movement'],e['maximum_rise_pixels']) for e in episodes if e['held_frames']==64])


if __name__ == '__main__':
    main()
