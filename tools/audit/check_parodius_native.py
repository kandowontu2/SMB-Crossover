"""Differential CPU oracle for the retargeted Parodius component.

The original cartridge instructions are the reference. Terrain/audio/scene
callbacks are controlled fixtures, not claims about SMB gameplay integration.
Both proposed mapper RAM layouts are exercised, with poisoned neighboring
memory and explicit equipment, motion, animation and projectile comparisons.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import random
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('parodius_builder', ROOT/'tools/reference/build_parodius_native.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
from py65.devices.mpu6502 import MPU

VIC = {0x76: ('VvGun',0xdb),0x77: ('VvRingCursor',0xa4),0x78: ('VvMeter',0xda),
       0x79: ('VvFlags',0xe6),0x7a: ('VvSpeed',0xd8),0x40: ('VvFresh',0xe4),
       0x42: ('VvHeld',0xe3),0x23: ('VvClock',0x0f)}


def compile_fixture(out, mapper):
    target = out/mapper
    target.mkdir(parents=True, exist_ok=True)
    builder.generate(target)
    native = (target/'parodius_native.s').read_text()
    base = 0x5d00 if mapper == 'mmc5' else 0x6100
    # This is precisely the proposed $5D -> second RgAudioRam page relocation;
    # the canonical MMC3 preparer is changed only when integration is ready.
    if mapper == 'mmc3':
        native = re.sub(r'\$5d([0-9a-f]{2})', lambda m:f'${base+int(m[1],16):04x}', native)
        native = native.replace('$5fea','$73cf')
        (target/'parodius_native.s').write_text(native)
    constants = ['.setcpu "6502"','.macpack longbranch',
                 f'MAPPER_MMC5={int(mapper=="mmc5")}',
                 'RgAudioRam=$6000','MmAudioRamStart=$6400',
                 'M0=$a0','M1=$a1','R0=$a2','R1=$a3',
                 'R4=$a4','R5=$a5','R6=$a6','R7=$a7']
    constants += [f'{name}=${base+offset:04x}' for name,offset in VIC.values()]
    constants += ['.include "parodius_native.s"','.include "parodius_data.inc"',
                  '.segment "VIC_CORE"']
    for native_address,name in builder.EXTERNALS.items():
        constants += [f'{name}:rts',f'.export {name}']
    for native_address in (0x916d,0x918d,0x91ad,0x91cd,0x91ed):
        constants.append(f'.export Pn{native_address:04x}')
    constants += ['.segment "VIC_GFX"','FixtureDataEnd:','.export FixtureDataEnd']
    (target/'fixture.s').write_text('\n'.join(constants)+'\n')
    (target/'fixture.cfg').write_text('''MEMORY {
 A: start=$8000,size=$2000,type=ro,file=%O,fill=yes;
 C: start=$C000,size=$2000,type=ro,file=%O,fill=yes;
}
SEGMENTS { VIC_CORE:load=A,type=ro; VIC_GFX:load=C,type=ro; }
''')
    compiler = ROOT/'tools/Windows/cc65/bin'
    logs=[]
    for command in ([str(compiler/'ca65.exe'),'-g','-o','fixture.o','fixture.s'],
                    [str(compiler/'ld65.exe'),'-C','fixture.cfg','-Ln','fixture.lbl',
                     '-m','fixture.map','-o','fixture.bin','fixture.o']):
        process=subprocess.run(command,cwd=target,capture_output=True,text=True)
        logs.append(process.stdout+process.stderr)
        (target/'compile.log').write_text('\n'.join(logs))
        assert process.returncode==0, process.stderr[:4000]
    labels = {m[2]:int(m[1],16) for line in (target/'fixture.lbl').read_text().splitlines()
              if (m:=re.fullmatch(r'al ([0-9a-fA-F]+) \.(\S+)',line))}
    cpu = MPU()
    raw = (target/'fixture.bin').read_bytes()
    cpu.memory[0x8000:0xa000] = raw[:8192]
    cpu.memory[0xc000:0xe000] = raw[8192:]
    ram = {}
    _, symbols = builder.mappings()
    zero = {'M0':0xa0,'M1':0xa1,'R0':0xa2,'R1':0xa3,
            'R4':0xa4,'R5':0xa5,'R6':0xa6,'R7':0xa7}
    for address, name in symbols.items():
        root, _, add = name.partition('+')
        if root in zero:
            destination = zero[root]
        elif address in VIC:
            destination = base+VIC[address][1]
        else:
            destination = labels[root]
        ram[address] = destination+(int(add) if add else 0)
    return target,cpu,labels,ram


def run_call(cpu, entry, ends, callbacks, events, terrain, max_steps=100000):
    cpu.pc = entry
    cpu.sp = 0xfd
    cpu.memory[0x1fe]=0xef
    cpu.memory[0x1ff]=0x7f
    steps = 0
    while cpu.pc not in ends and cpu.pc != 0x7ff0:
        if cpu.pc in callbacks:
            name = callbacks[cpu.pc]
            if name == 'PnSoundEvent':
                events.append(cpu.a)
            elif name == 'PnTerrainQuery':
                cpu.a = terrain
                cpu.FlagsNZ(cpu.a)
            # callbacks preserve everything else; emulate an RTS explicitly
            # rather than changing the original ROM, which is hashed evidence.
            cpu.pc = cpu.stPopWord()+1
        else:
            cpu.step()
        steps += 1
        assert steps < max_steps, ('nonterminating native component',hex(entry),hex(cpu.pc))
    return steps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'build/verification/parodius-native-ni/differential')
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    _,source = builder.source_cpu()
    report = dict(source_sha256=builder.SHA,playable=False,callbacks='Controlled CPU fixtures',mappers={})
    for mapper in ('mmc5','mmc3'):
        folder,port,labels,ram = compile_fixture(out,mapper)
        original_callbacks=builder.EXTERNALS
        port_callbacks={labels[name]:name for name in builder.EXTERNALS.values()}
        # Fields 0..27 include all player/Option/shield/projectile actors.
        compare = []
        for address in builder.ORIGINAL_FIELDS:
            compare.extend((address+i,ram[address]+i) for i in range(28))
        compare.extend((0x0640+i,ram[0x0640]+i) for i in range(128))
        compare.extend((0x6620+i,ram[0x6620]+i) for i in range(28))
        compare.extend((0x66b0+i,ram[0x66b0]+i) for i in range(28))
        globals_ = [a for a in ram if a<256 and a not in range(0x00,0x19)]
        compare.extend((a,ram[a]) for a in globals_)
        compare.extend((a,ram[a]) for a in (0x6590,0x65c0,0x65f0))
        compare = sorted(set(compare))
        state_map=dict(compare)
        # None of the state aliases may collide: also check entire owned
        # intervals, not just bases, including history and native punch flags.
        destinations=[destination for _,destination in compare]
        assert len(destinations)==len(set(destinations)), 'aliased native state'
        allowed = set(destinations)
        allowed.update(ram[a] for a in range(4,16))
        allowed.update(ram[a] for a in (0x15,0x17,0x18))
        allowed.update(range(ram[0x6530],ram[0x6530]+6))
        allowed.update(range(0xa0,0xa8))
        allowed.update(range(0x100,0x200))
        cases = []
        total_steps = 0
        def clear(variant):
            for address in range(0x8000):
                if address not in range(0x100,0x200):
                    source.memory[address]=0
                    port.memory[address]=0xa5
            for native,destination in compare:
                source.memory[native]=0
                port.memory[destination]=0
            for address,destination in ram.items():
                if address<256 or address in (0x6530,):
                    source.memory[address]=0
                    port.memory[destination]=0
            for i in range(6):
                source.memory[0x6530+i]=0
                port.memory[ram[0x6530]+i]=0
            seed(0x8f,variant)
            seed(0x87,variant)
            seed(0x6200,1)
            seed(0x6500,0x80)
            seed(0x63e0,1)
            seed(0x6260,64)
            seed(0x62c0,112)
            for i in range(64):
                seed(0x0640+i*2,64)
                seed(0x0641+i*2,112)
            source.a=source.x=source.y=port.a=port.x=port.y=0
            source.p=port.p=0x30
        def seed(address,value):
            if address in ram:
                destination=ram[address]
            elif address in state_map:
                destination=state_map[address]
            else:
                field=max(a for a in builder.ORIGINAL_FIELDS if a<=address)
                assert address-field<28,(hex(address),'no array mapping')
                destination=ram[field]+address-field
            source.memory[address]=value&255
            port.memory[destination]=value&255
        def execute(entry, *, terrain=0, case=''):
            nonlocal total_steps
            before=port.memory[:0x8000]
            first,second=[],[]
            ends={0x83b2} if entry in (0x8191,0x824c) else {0x8493} if entry==0x83b2 else set()
            source.x=port.x=0
            total_steps+=run_call(source,entry,ends,original_callbacks,first,terrain)
            total_steps+=run_call(port,labels[builder.ENTRY[entry]],set(),port_callbacks,second,terrain)
            differences=[(hex(a),hex(b),source.memory[a],port.memory[b])
                         for a,b in compare if source.memory[a]!=port.memory[b]]
            assert not differences,(mapper,case,hex(entry),differences[:12])
            assert first==second,(case,'sound/skin/scene callback sequence')
            unexpected=[hex(i) for i,(old,new) in enumerate(zip(before,port.memory))
                        if i<0x8000 and old!=new and i not in allowed]
            assert not unexpected,(case,'writes outside owned overlay',unexpected[:12])
            return first
        for variant in range(4):
            # Every speed, direction and clamp, including canceled opposites.
            for speed in range(5):
                clear(variant)
                seed(0x7a,speed)
                for frame in range(512):
                    direction=[1,2,4,8,5,9,6,10,0,3,12,15][(frame//17)%12]
                    seed(0x42,direction)
                    seed(0x40,direction if frame%17==0 else 0)
                    seed(0x23,frame)
                    execute(0x824c,case=f'motion v{variant} speed{speed} frame{frame}')
                cases.append(dict(name='motion',variant=variant,speed=speed,frames=512))
            # Source gear behavior/caps and mutual exclusion, including !?.
            for bit in (1,2,4,8,16,32,64):
                clear(variant)
                for purchase in range(7):
                    seed(0x78,bit);seed(0x40,0x80)
                    execute(0x83b2,case=f'gear v{variant} bit{bit} purchase{purchase}')
                cases.append(dict(name='equipment',variant=variant,cell=bit,purchases=7))
            # All equipment combinations exercise source gun, missile, Option
            # and shield state machines. Terrain/contact fixtures occur after
            # stable flight, including source enemy reaction classifications.
            for loadout in (0,8,0x40,0x80,0x48,0x88,0x20,0x2b,0x6b,0xab):
                clear(variant)
                seed(0x76,loadout)
                if variant<2 and loadout&3:
                    seed(0x76,loadout+1) # four Options for Vic/Octopus
                maximum=0
                for frame in range(384):
                    seed(0x23,frame)
                    seed(0x42,0x40|(4 if frame%80<20 else 8 if frame%80<40 else 0))
                    seed(0x40,0x40 if frame%7==0 else 0)
                    execute(0x824c,case=f'weapon motion v{variant} {loadout:x} f{frame}')
                    for index in range(1,28):
                        seed(0x6230+index, 1 if frame>160 and frame%31==0 else 0)
                    execute(0x8493,terrain=int(frame>220 and frame%13==0),
                            case=f'weapon v{variant} {loadout:x} f{frame}')
                    maximum=max(maximum,sum(bool(source.memory[0x6500+i]) for i in range(6,28)))
                cases.append(dict(name='weapons',variant=variant,loadout=loadout,frames=384,max_projectiles=maximum))
            # Native Big transition, timeout, restricted firing, and normal
            # sprite-bank restoration are tested through the whole duration.
            clear(variant)
            seed(0x7b,2);seed(0x76,0x6b)
            for frame in range(1536):
                seed(0x23,frame)
                seed(0x42,0x41 if frame%100<50 else 0x42)
                seed(0x40,0x40 if frame%9==0 else 0)
                execute(0x8191 if source.memory[0x7b]&2 else 0x824c,
                        case=f'big v{variant} f{frame}')
                execute(0x8493,case=f'big weapons v{variant} f{frame}')
            assert source.memory[0x6590]==0 and source.memory[0x87]==variant
            cases.append(dict(name='big-timeout',variant=variant,frames=1536))
        report['mappers'][mapper]=dict(cases=cases,instruction_steps=total_steps,
                                      compared_state_bytes=len(compare),
                                      component_sha256=hashlib.sha256((folder/'fixture.bin').read_bytes()).hexdigest(),
                                      passed=True)
        print('PASS',mapper,len(cases),'native differential cases',total_steps,'instructions',flush=True)
        (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
