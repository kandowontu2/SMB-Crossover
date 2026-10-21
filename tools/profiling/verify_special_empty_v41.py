"""Compare whole compiled special callers; empty-pool optimization only.

Seeded CPU cases, not traversal. Every ordinary RAM byte and register must
match the unoptimized ROM; only discarded stack/farcall target scratch differ.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, itertools, json, re

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('native_unit', ROOT/'tools/audit/verify_native_relocation.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


class Memory(native.NesMemory):
    def __init__(self, old):
        super().__init__(list(old), old.rom, old.smc)
        self.bank_c = 13

    def __setitem__(self, key, value):
        if isinstance(key, int) and key == 0x5116:
            self.bank_c = value & 127
            base = 16+self.bank_c*8192
            super().__setitem__(slice(0xc000,0xe000), self.rom[base:base+8192])
            return
        super().__setitem__(key,value)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('before',type=Path);p.add_argument('after',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    b,B=native.load(a.before);c,C=native.load(a.after)
    assert all(C[n]==v for n,v in B.items() if v<0x8000 and n in C),'Unchanged RAM ABI'
    for cpu in (b,c):cpu.memory=Memory(cpu.memory)
    for path in (a.before,a.after):
        debug=path.with_suffix('.dbg').read_text()
        for entry in ('SpecialWeapons','SpecialDrawShots'):
            sym=re.search(r'sym\s+[^\n]*name="'+entry+r'",[^\n]*seg=(\d+)',debug)
            seg=re.search(r'seg\s+id='+sym[1]+r',name="[^"]+",[^\n]*ooffs=(\d+)',debug)
            assert (int(seg[1])-16)//8192==60,'Actual compiled entry bank'
    ignored=set(range(0x100,0x200))|set(range(B['SMCCODE'],B['SMCCODE']+len(b.memory.smc)))
    rows=[]
    # Empty pools with live clocks, input, inventory selection and palette work.
    for char,selected,phase,state,timers in itertools.product((1,9),range(9),range(4),(0,1,3),range(4)):
        rows.append(dict(entry='SpecialWeapons',kind='empty-live-state',char=char,selected=selected,phase=phase,state=state,timers=timers,pool=-1,type=0))
    # Every occupied slot must conservatively retain the ordinary loop even
    # when its nonzero type belongs to another weapon batch.
    for char,slot,kind,phase in itertools.product((1,9),range(10),(1,4,8,10,32,47,255),range(2)):
        rows.append(dict(entry='SpecialWeapons',kind='occupied-fallback',char=char,selected=0,phase=phase,state=0,timers=1,pool=slot,type=kind))
    # All rotating starts, both draw parities and publication transitions.
    for char,first,phase,active,last,death in itertools.product((1,9),range(10),range(2),range(2),range(2),range(2)):
        rows.append(dict(entry='SpecialDrawShots',kind='empty-draw-publication',char=char,first=first,phase=phase,active=active,last=last,death=death,pool=-1,type=0))
    for char,slot,kind,first in itertools.product((1,9),range(10),(1,10,32,255),(0,9)):
        rows.append(dict(entry='SpecialDrawShots',kind='occupied-draw-fallback',char=char,first=first,phase=1,active=0,last=0,death=0,pool=slot,type=kind))
    stats={}
    for number,row in enumerate(rows):
        results=[];clocks=[]
        for cpu,L in ((b,B),(c,C)):
            cpu.memory[:0x8000]=[0]*0x8000
            cpu.memory[L['SMCCODE']:L['SMCCODE']+len(cpu.memory.smc)]=cpu.memory.smc
            cpu.memory.switch(60)
            cpu.memory[0x5116]=13|128
            def put(n,v,i=0):cpu.memory[L[n]+i]=v&255
            for n,v in (('CurrentBank',188),('BankShadow',0x47),('CurrentBankC',13),('SelectedCharacter',row['char']),('GameEngineSubroutine',8),('OperMode',1),('Player_Y_HighPos',1),('Player_Y_Position',176),('Player_X_Position',64),('FrameCounter',row['phase']),('PlayerFacingDir',1),('SsLastPalette',1)):
                if n in L:put(n,v)
            for i in range(8):put('R0',number*13+i*47,i)
            put('MmBulletType',number&255)
            for i,n in enumerate(('MmBulletX','MmBulletPage','MmBulletY','MmBulletDir')):put(n,number+i*17)
            for i in range(6):
                put('Enemy_ID',6,i);put('Enemy_X_Position',180+i*8,i);put('Enemy_Y_Position',192,i);put('Enemy_Y_HighPos',1,i)
                put('Enemy_Flag',1 if number%3 and i<number%6 else 0,i)
            if row['entry']=='SpecialWeapons':
                put('InvSelected',row['selected'],row['char'])
                put('InvOwnedLo',255,row['char']);put('InvOwnedHi',255,row['char'])
                for i in range(9):put('InvAmmo',99,row['char']*16+i)
                put('Player_State',row['state']);put('PlayerStatus',number%3)
                put('SsBodyStop',row['timers']);put('SsFreeze',row['timers'])
                put('XgDash',row['phase']&1);put('MmSliding',(row['phase']>>1)&1)
                put('InvFresh',64 if row['phase']==3 else 0);put('SavedJoypadBits',64 if row['phase']>=2 else 0)
                put('GuestPowerupActive',1 if number%7==0 else 0)
                put('StarInvincibleTimer',1 if number%11==0 else 0)
                put('SsWaterExpand',number%2);put('SsWaterRadius',number%40);put('SsWaterFraction',number%2)
                if row['pool']>=0:
                    slot=row['pool'];put('RgShotType',row['type'],slot);put('RgShotX',120,slot);put('RgShotY',100,slot);put('RgShotYHigh',1,slot)
                    put('RgShotDir',1,slot);put('RgShotVXHi',1,slot);put('SsArt',1,slot)
            else:
                put('SsDrawFirst',row['first']);put('SsChrActive',row['active']);put('SsLastChrActive',row['last'])
                put('SsChrPhysical',63);put('SsLastChrPhysical',63 if number%2 else 0)
                put('MmDeathFlag',row['death']);put('ReloadCHRBank',number&255)
                if row['pool']>=0:
                    slot=row['pool'];put('RgShotType',row['type'],slot);put('RgShotX',120,slot);put('RgShotY',100,slot);put('RgShotYHigh',1,slot)
                    put('RgShotDir',1,slot);put('SsArt',1,slot)
            cpu.a,cpu.x,cpu.y,cpu.p=number&255,(number*17)&255,(number*31)&255,(number*59)&255
            cpu.sp=0xfd;cpu.stPushWord(0x7eff);cpu.pc=L[row['entry']];cpu.processorCycles=0
            steps=0
            while cpu.pc!=0x7f00:
                cpu.step();steps+=1
                assert steps<20000,(number,row,hex(cpu.pc))
            results.append((cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.memory.bank_c,bytes(v for i,v in enumerate(cpu.memory[:0x8000])if i not in ignored)))
            clocks.append(cpu.processorCycles)
        assert results[0]==results[1],{'case':number,'arena':row,'registers':[r[:6]for r in results],
            'memory_differences':[(hex(i),b.memory[i],c.memory[i])for i in range(0x8000)if i not in ignored and b.memory[i]!=c.memory[i]][:16]}
        delta=clocks[1]-clocks[0];st=stats.setdefault(row['kind'],{'cases':0,'min_delta':10000,'max_delta':-10000})
        st['cases']+=1;st['min_delta']=min(st['min_delta'],delta);st['max_delta']=max(st['max_delta'],delta)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    report={'result':'passed','cases':len(rows),'stats':stats,'before_sha256':sha(a.before),'after_sha256':sha(a.after),'script_sha256':sha(Path(__file__)),
        'compared':'A/X/Y/allP/SP, C000 physical bank, all RAM below8000 except discarded stack/farcall SMC target scratch',
        'scope':'Whole compiled SpecialWeapons and SpecialDrawShots; empty live clocks/input/inventory, every occupied slot fallback, rotating draw start and publication transitions',
        'limits':['Seeded CPU units, no interrupts/PPU/audio hardware/traversal. Active contacts and sprite overload require separate Mesen fixtures.']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',len(rows),stats,flush=True)


if __name__=='__main__':main()
