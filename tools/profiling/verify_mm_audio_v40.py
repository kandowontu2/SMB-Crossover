"""Actual compiled Mega Man native driver lifecycle and ordered APU receipts.

Seeded CPU streams, not traversal. C000/A000 mapper writes execute normally in
the model; the MMC5 multiplier is the only intentionally changed device state.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/profiling'))
from probe_mm3_multiplier_v40 import MultiplyMemory, native


class AudioMemory(MultiplyMemory):
    def __init__(self, original):
        super().__init__(original)
        self.apu_writes = []

    def __setitem__(self,key,value):
        if isinstance(key,int):
            if key == 0x5116:
                physical=value&0x7f
                offset=16+physical*8192
                assert offset+8192<=16+self.rom[4]*16384
                super().__setitem__(slice(0xc000,0xe000),self.rom[offset:offset+8192])
                return
            if 0x4000<=key<=0x4017 or 0x5000<=key<=0x5015:
                self.apu_writes.append((key,value))
        super().__setitem__(key,value)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('before',type=Path)
    p.add_argument('after',type=Path)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--outer',action='store_true',help='Execute full AudioUpdate including both shared mixers')
    a=p.parse_args()
    b,B=native.load(a.before)
    c,C=native.load(a.after)
    assert all(C[n]==v for n,v in B.items() if v<0x8000 and n in C),'Native/private RAM ABI'
    for cpu in (b,c):cpu.memory=AudioMemory(cpu.memory)
    count,multiply_calls=0,0
    stats={}

    def call(entry,number):
        nonlocal count,multiply_calls
        results,clocks=[],[]
        for cpu,L in ((b,B),(c,C)):
            cpu.memory.apu_writes.clear()
            cpu.memory.multiplies.clear()
            cpu.a,cpu.x,cpu.y,cpu.p=number&255,(number*17)&255,(number*31)&255,(number*59)&255
            cpu.sp=0xfd-2*(number%8)
            cpu.stPushWord(0x7eff)
            cpu.pc,cpu.processorCycles=L[entry],0
            steps=0
            while cpu.pc!=0x7f00:
                cpu.step();steps+=1
                assert cpu.sp>=0x85,'Live audio stack stays above the executing SMC image'
                assert steps<15000,(entry,number,hex(cpu.pc))
            results.append((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,
                bytes(cpu.memory[:0x186])+bytes(cpu.memory[0x200:0x8000]),list(cpu.memory.apu_writes)))
            clocks.append(cpu.processorCycles)
        assert results[0]==results[1],{'entry':entry,'case':number,'registers':[r[:5] for r in results],
            'writes':[r[-1] for r in results],
            'memory_differences':[(hex(i),b.memory[i],c.memory[i])for i in range(0x8000)
                if not 0x100<=i<0x200 and b.memory[i]!=c.memory[i]][:16]}
        assert not b.memory.multiplies
        multiply_calls+=len(c.memory.multiplies)//2
        st=stats.setdefault(entry,{'cases':0,'min_delta':10000,'max_delta':-10000})
        st['cases']+=1
        st['min_delta']=min(st['min_delta'],clocks[1]-clocks[0])
        st['max_delta']=max(st['max_delta'],clocks[1]-clocks[0])
        count+=1

    for stream in range(8):
        for cpu,L in ((b,B),(c,C)):
            cpu.memory[:0x8000]=[0]*0x8000
            cpu.memory[L['SMCCODE']:L['SMCCODE']+len(cpu.memory.smc)]=cpu.memory.smc
            for n,v in (('SelectedCharacter',1),('OperMode',1),('CurrentBank',128),('BankShadow',0x47),('CurrentBankC',13),('GameEngineSubroutine',8)):
                if n in L:cpu.memory[L[n]]=v
            for i in range(0x36):cpu.memory[0xc0+i]=(stream*53+i*17)&255
        call('MegaManAudioInit',stream)
        for tick in range(2000):
            for cpu,L in ((b,B),(c,C)):
                put=lambda n,v:cpu.memory.__setitem__(L[n],v)
                put('FrameCounter',tick&255)
                put('PlayerStatus',stream%3)
                put('Player_State',0 if tick%120<60 else 1)
                put('AreaMusicQueue',(1,2,4,8,16,32,64,128)[stream] if tick in (0,768,1408) else 0)
                put('EventMusicQueue',(1,2,4,8,16,32,64,128)[stream] if tick in (512,1024) else 0)
                active=(tick//128)&1
                put('Square1SoundQueue',(1<<((tick+stream)%8)) if active and tick%5==0 else 0)
                put('Square2SoundQueue',(1<<((tick//3+stream)%8)) if active and tick%7==0 else 0)
                put('MmAudioShotType',(tick//32)%6)
                put('MmChargeFrames',min(90,tick%128-48) if tick%128>=81 else 0)
                # Actual encoded requests used by the current special weapons
                # and inventory, including the source stop-SFX command F1+1.
                put('SsAudioRequest',(26,62,63,65,66,0xf2,64,22,61,67)[(tick//29+stream)%10] if active and tick%29==0 else 0)
                put('GamePauseStatus',1 if 1600<=tick<1604 else 0)
                put('OperMode',0 if tick==1800 else 1)
            call('AudioUpdate' if a.outer else 'MegaManAudioUpdate',stream*2000+tick)
    report={'result':'passed','cases':count,'stats':stats,'hardware_multiply_calls':multiply_calls,
            'before_sha256':hashlib.sha256(a.before.read_bytes()).hexdigest(),
            'after_sha256':hashlib.sha256(a.after.read_bytes()).hexdigest(),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope':('Actual compiled full AudioUpdate and shared mixers' if a.outer else 'Actual compiled native wrapper')+': eight2000-update coherent streams across both song engines, effect queues, actual special requests, charge, landing, pause, title and restart',
            'compared':'A/X/Y/allP/SP, every RAM byte below8000 including live SMC except discarded upper stack186..1FF, ordered4000..4017 and5000..5015 writes',
            'limits':['CPU model only; no PPU, NMI/IRQ, sampled waveform, DMC playback or traversal.',
                      'Hardware multiplier latch state deliberately differs and is not RAM. Separate actual-mapper interrupt ownership tests remain required.']}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',count,stats,'multiply_calls',multiply_calls,flush=True)


if __name__=='__main__':main()
