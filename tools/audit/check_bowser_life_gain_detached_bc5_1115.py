"""Flat detached CPU semantics only; no source-game overlay or ROM candidate."""
from pathlib import Path
from unittest.mock import patch
from collections import Counter
import itertools,json
import plan_bowser_life_gain_bc5_1115 as Plan

def run(raw):
    b,before,after,row=Plan.proposal(raw);address=lambda n:Plan.Current.W.address(b,n)
    names=('BwConstruct','BwEnsure','BwReady','BwPlayerKey','BwPersistent','BwHP','BwTier','BwVariant',
        'CurrentPlayer','FmAlts','NumberofLives','SelectedCharacter','Player_X_Position','Player_PageLoc',
        'Player_Y_Position','Player_Y_HighPos','Player_State')
    a={n:address(n)for n in names};base=bytearray(65536);base[0xa000:0xc000]=before
    base[0xbe00:0xbe40]=bytes((i*13+7)&255 for i in range(64))
    base[0x100:0x200]=bytes((i*7+17)&255 for i in range(256))
    startSP=219;sentinel=0x5b00;base[0x100+startSP+1]=(sentinel-1)&255;base[0x100+startSP+2]=(sentinel-1)>>8
    realflags=(1,2,4,8,64,128);counts=Counter();cycles={};minSP=255
    scopes=('equal','increase','decrease','death','ready-invalid','player-change','newgame')
    cases=0
    class Memory(bytearray):
        def __setitem__(self,at,value):
            if isinstance(at,int)and hasattr(self,'writes'):self.writes.append((at,value))
            return super().__setitem__(at,value)
    for scope,variant,player,tier,injured,flag in itertools.product(scopes,(0,1),(0,1),(0,1,2),(False,True),range(64)):
        seed=bytearray(base);key=player*4;active=key if scope!='player-change'else(1-player)*4
        hp=(5 if variant else 34)-(1 if injured else 0)
        if scope=='death':hp=0
        seed[a['BwReady']]=0 if scope in('ready-invalid','newgame') else 0xb7
        seed[a['BwPlayerKey']]=active;seed[a['BwVariant']]=variant;seed[a['BwHP']]=hp;seed[a['BwTier']]=tier
        seed[a['CurrentPlayer']]=player;seed[a['FmAlts']]=0x45|(variant*8);seed[a['SelectedCharacter']]=27
        seed[a['NumberofLives']]=3 if scope=='increase' else 1 if scope in('decrease','death') else 2
        for member in(0,4):
            seed[a['BwPersistent']+member:a['BwPersistent']+member+4]=bytes((hp if member==active else(max(1,hp-1)),tier if member==active else(2-tier),2,0 if scope=='newgame' else 0xb7))
        for name,value in(('Player_X_Position',93),('Player_PageLoc',4),('Player_Y_Position',123),('Player_Y_HighPos',1),('Player_State',2)):seed[a[name]]=value
        p=0x30|sum(bit for i,bit in enumerate(realflags)if flag>>i&1);results=[]
        for proposed in(False,True):
            memory=Memory(seed)
            if proposed:memory[row['start']:row['end']]=row['new']
            memory.writes=[];c=Plan.NesMPU(memory=memory,pc=a['BwConstruct']if scope=='newgame'else a['BwEnsure'])
            c.sp=startSP;c.a=0xa9;c.x=0x6d;c.y=0x87;c.p=p;low=startSP;ctors=0
            for _ in range(1000):
                if c.pc==sentinel:break
                assert 0xa000<=c.pc<0xaa37,('Unexpected foreign primitive read/exec',hex(c.pc))
                if c.pc==a['BwConstruct']:ctors+=1
                c.step();low=min(low,c.sp)
            else:raise AssertionError(('Detached bounded call',scope,variant,player))
            assert c.sp==startSP+2
            results.append((memory,(c.a,c.x,c.y,c.p,c.sp),c.processorCycles,low,ctors))
        old,new=results;oldmem,oldregs,oldcycles,_,oldctors=old;newmem,newregs,newcycles,low,newctors=new
        assert oldregs==newregs,('Caller AXYP/SP',scope,variant,player,tier,hex(p),oldregs,newregs)
        if scope=='increase':
            assert oldctors==1 and newctors==0
            saved=a['BwPersistent']+2+key
            assert newmem[saved]==3
            assert newmem.writes==[(saved,3)],('Only active saved-life write',newmem.writes)
            assert all(x==y for at,(x,y)in enumerate(zip(seed,newmem))if not row['start']<=at<row['end']and at!=saved)
        else:
            assert oldctors==newctors
            assert all(x==y for at,(x,y)in enumerate(zip(oldmem,newmem))if not row['start']<=at<row['end']),('Original reset path changed',scope)
            assert oldmem.writes==newmem.writes,('Ordered writer fidelity',scope)
        counts[scope]+=1;cases+=1;minSP=min(minSP,low)
        values=cycles.setdefault(scope,dict(old=set(),new=set()));values['old'].add(oldcycles);values['new'].add(newcycles)
    q=Plan.inspect_plan(raw);q.update(detached_flat=dict(passed=True,cases=cases,scope_counts=dict(counts),real_flag_combinations=64,
        variants=2,players=2,tiers=3,HP_cases='full and genuinely representable injured (primitive seeds only)',
        caller_AXYP_SP_exact=True,equal_and_all_original_reset_ordered_writes_exact=True,
        increased_life_writes_only_active_existing_snapshot=True,pose_motion_currentHP_tier_all_other_bytes_preserved=True,
        minimum_SP=minSP,cycles={k:{kk:sorted(vv)for kk,vv in v.items()}for k,v in cycles.items()},
        scope='Flat memory CPU primitive with declared source state seeds, NOT gameplay or candidate qualification'))
    q['receipt_SHA256']=Plan.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    raw=Plan.Current.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Detached Bowser proof attempted files/native')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
