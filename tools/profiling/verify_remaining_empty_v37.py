"""Before/after compiled empty-pool admission with live nonprojectile state."""
from pathlib import Path
import argparse, hashlib, importlib.util, itertools, json, re
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('native_unit',ROOT/'tools/audit/verify_native_relocation.py')
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('before',type=Path);p.add_argument('after',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    b,B=native.load(a.before);c,C=native.load(a.after)
    assert all(C[n]==v for n,v in B.items() if v<0x8000 and n in C)
    for path in(a.before,a.after):
        debug=path.with_suffix('.dbg').read_text()
        symbol=re.search(r'sym\s+[^\n]*name="RemainingWeapons",[^\n]*seg=(\d+)',debug)
        segment=re.search(r'seg\s+id='+symbol[1]+r',name="[^"]+",[^\n]*ooffs=(\d+)',debug)
        assert (int(segment[1])-16)//8192==6,'Actual linked RemainingWeapons bank'
    ignored=set(range(0x100,0x200))|set(range(B['SMCCODE'],B['SMCCODE']+len(b.memory.smc)))
    rows=[]
    for char,timer,engine,select,pool,power in itertools.product(range(13),range(2),(8,9),(0,32),(-1,0,9),(0,2)):
        rows.append({'kind':'fallback-controls','char':char,'timer':timer,'engine':engine,'select':select,'pool':pool,'power':power,'flip':0,'state':0,'owned':0,'sound':0,'freeze':0,'stop':0})
    for flip,state,power,owned,sound,freeze,stop in itertools.product((0,1,2),range(4),range(3),(0,64),range(2),(0,1,256,65535),(0,1,255)):
        rows.append({'kind':'samus-empty-live-timers','char':2,'timer':0,'engine':8,'select':0,'pool':-1,'power':power,'flip':flip,'state':state,'owned':owned,'sound':sound,'freeze':freeze,'stop':stop})
    stats={}
    for count,row in enumerate(rows):
        outputs=[];clocks=[]
        for cpu,L in((b,B),(c,C)):
            cpu.memory[:0x8000]=[0]*0x8000
            cpu.memory[L['SMCCODE']:L['SMCCODE']+len(cpu.memory.smc)]=cpu.memory.smc
            cpu.memory.switch(6)
            for n,v in (('CurrentBank',6|(128 if cpu.memory.rom[6]>>4==5 else 0)),('BankShadow',0x47),('SelectedCharacter',row['char']),('TimerControl',row['timer']),('GameEngineSubroutine',row['engine']),('InvFresh',row['select']),('PlayerStatus',row['power']),('SmFlip',row['flip']),('Player_State',row['state']),('AvScrewSound',row['sound']),('AvStopwatch',row['stop']),('FrameCounter',count&255)):
                if n in L:cpu.memory[L[n]]=v
            cpu.memory[L['InvOwnedLo']+2]=row['owned']
            for i in range(6):
                cpu.memory[L['AvFrozen']+i]=row['freeze']&255
                cpu.memory[L['AvFrozenHi']+i]=row['freeze']>>8
            if row['pool']>=0:cpu.memory[L['RgShotType']+row['pool']]=(1,31,47,255)[count%4]
            for i in range(8):cpu.memory[L['R0']+i]=(count*13+i*47)&255
            cpu.a,cpu.x,cpu.y,cpu.p=count&255,(count*17)&255,(count*31)&255,(count*59)&255
            cpu.sp=0xfd;cpu.stPushWord(0x7eff);cpu.pc=L['RemainingWeapons'];cpu.processorCycles=0
            steps=0
            while cpu.pc!=0x7f00:
                cpu.step();steps+=1;assert steps<8000,(count,row,hex(cpu.pc))
            outputs.append((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,bytes(v for i,v in enumerate(cpu.memory[:0x8000])if i not in ignored)))
            clocks.append(cpu.processorCycles)
        assert outputs[0]==outputs[1],{'case':count,'arena':row,'registers':[r[:5]for r in outputs],
            'memory_differences':[(hex(i),b.memory[i],c.memory[i])for i in range(0x8000)if i not in ignored and b.memory[i]!=c.memory[i]][:15]}
        key=row['kind'];s=stats.setdefault(key,{'cases':0,'min_delta':10000,'max_delta':-10000})
        d=clocks[1]-clocks[0];s['cases']+=1;s['min_delta']=min(s['min_delta'],d);s['max_delta']=max(s['max_delta'],d)
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    report={'result':'passed','cases':len(rows),'stats':stats,'actual_entry_bank':6,
        'before_sha256':sha(a.before),'after_sha256':sha(a.after),'script_sha256':sha(Path(__file__)),
        'compared':'A/X/Y/allP/SP and all bytes below8000 except discarded stack/farcall SMC scratch',
        'scope':'Initialized whole RemainingWeapons CPU units; empty-pool Samus with live freeze/stopwatch/Screw/input/power states, all-character guard/fallback controls',
        'limits':['Nonzero unsupported pool types exercise conservative fallback. Active damaging projectiles, actor contacts, interrupts/PPU and routes need separate emulator checks.']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS',len(rows),stats)


if __name__=='__main__':main()
