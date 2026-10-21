"""Actual full idle draw callers with exact state, initialized CPU units."""
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
    def actual_bank(path,entry):
        debug=path.with_suffix('.dbg').read_text()
        symbol=re.search(r'sym\s+[^\n]*name="'+entry+r'",[^\n]*val=(0x[0-9A-Fa-f]+),seg=(\d+)',debug)
        assert symbol,entry
        segment=re.search(r'seg\s+id='+symbol[2]+r',name="[^"]+",start=(0x[0-9A-Fa-f]+),[^\n]*ooffs=(\d+)',debug)
        assert segment and int(segment[1],16)==0xa000,(entry,segment)
        return (int(segment[2])-16)//8192
    banks={entry:actual_bank(a.before,entry)for entry in('RemainingDraw','SamusDrawShots')}
    assert banks=={entry:actual_bank(a.after,entry)for entry in banks}
    ignored=set(range(0x100,0x200))|set(range(B['SMCCODE'],B['SMCCODE']+len(b.memory.smc)))
    stats={};count=0
    for entry,char,parity,first,active,physical,last,wrap in itertools.chain(
        (('RemainingDraw',*v)for v in itertools.product(range(13),range(2),(0,),range(2),(0,63),(0,1),(0,255))),
        (('SamusDrawShots',2,*v)for v in itertools.product(range(2),(0,1,2,3,4,5,6,255),range(2),(0,63),(0,1),(0,255)))):
        result=[];clocks=[]
        bank=banks[entry]
        for cpu,L in ((b,B),(c,C)):
            cpu.memory[:0x8000]=[0]*0x8000
            cpu.memory[L['SMCCODE']:L['SMCCODE']+len(cpu.memory.smc)]=cpu.memory.smc
            cpu.memory.switch(bank)
            for n,v in (('CurrentBank',bank|(128 if cpu.memory.rom[6]>>4==5 else 0)),('BankShadow',0x47),('SelectedCharacter',char),('FrameCounter',parity),('SsDrawFirst',first),('SsChrActive',active),('SsChrPhysical',physical),('SsLastChrActive',last),('SsLastChrPhysical',physical if count%2 else 255),('ReloadCHRBank',wrap)):
                if n in L:cpu.memory[L[n]]=v
            for i in range(8):cpu.memory[L['R0']+i]=(count*13+i*47)&255
            cpu.a,cpu.x,cpu.y,cpu.p=count&255,(count*17)&255,(count*31)&255,(count*59)&255
            cpu.sp=0xfd;cpu.stPushWord(0x7eff);cpu.pc=L[entry];cpu.processorCycles=0
            steps=0
            while cpu.pc!=0x7f00:
                cpu.step();steps+=1
                assert steps<6000,(entry,count,hex(cpu.pc))
            result.append((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,bytes(v for i,v in enumerate(cpu.memory[:0x8000]) if i not in ignored)))
            clocks.append(cpu.processorCycles)
        assert result[0]==result[1],{'entry':entry,'case':count,'character':char,'first':first,
            'registers':[r[:5]for r in result],
            'memory_differences':[(hex(i),b.memory[i],c.memory[i])for i in range(0x8000) if i not in ignored and b.memory[i]!=c.memory[i]][:12]}
        delta=clocks[1]-clocks[0];s=stats.setdefault(entry,{'cases':0,'min_delta':10000,'max_delta':-10000})
        s['cases']+=1;s['min_delta']=min(s['min_delta'],delta);s['max_delta']=max(s['max_delta'],delta);count+=1
    sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    report={'result':'passed','cases':count,'entries':stats,'before_sha256':sha(a.before),'after_sha256':sha(a.after),
        'script_sha256':sha(Path(__file__)),'actual_linked_entry_banks':banks,'compared':'A/X/Y/allP/SP and every byte below8000 except discarded stack/farcall SMC target scratch',
        'scope':'Actual whole RemainingDraw and SamusDrawShots initialized units; idle pools/world pickups/HUD/death; publication state variations and rotation edge values',
        'caller_contract':'A000 entry is reached through normal farcall; MMC3 BankShadow is47 on entry. No interrupts/PPU or traversal.',
        'limits':['Active beams/bombs/inventory sprites/death rendering and actual CHR/NMI hardware timing require separate emulator checks.']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n');print('PASS',count,stats)


if __name__=='__main__':main()
