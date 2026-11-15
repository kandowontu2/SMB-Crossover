"""Actual native Star/1UP/death dispatch, explicit callback component inputs."""
from pathlib import Path
from unittest.mock import patch
import json
import compose_prince_sword_tier2_1115 as C
import check_prince_sword_tier2_earned_1115 as Earned

N,W,Frames=Earned.N,Earned.W,Earned.Frames

def invoke(m,target,slot=5):
    b=m.bundle;m[W.address(b,'SafecallA_SMC')+1]=83
    at=W.address(b,'FarcallJmpTarget_SMC');m[at+1]=target&255;m[at+2]=target>>8
    c=N.NesMPU(memory=m,pc=W.address(b,'FarCallCommon'));c.a,c.x,c.y,c.p,c.sp=3,slot,0,0x21,224;c.stPushWord(0x5aff)
    entries=[]
    for steps in range(500000):
        if c.pc==0x5b00:break
        if c.pc==0xaf71 and m.rawtags[1]==131:
            entries.append(dict(PC=c.pc,tag=m.rawtags[1],P=c.p,bytes=bytes(m[c.pc:c.pc+16]).hex()))
        assert m[c.pc],('Native dispatch BRK',hex(c.pc),m.rawtags);c.step()
    else:raise AssertionError('Native dispatch return bound')
    assert c.sp==224 and c.p&1
    return dict(regs=[c.a,c.x,c.y,c.p,c.sp],CPU=c.processorCycles,native_pickup_entries=entries)

def run(parent):
    raw,composition=C.proposal(parent);a,_=Earned.cold(raw)
    def owning(image):assert image==parent;return parent
    with patch.object(Earned.Game,'proof_parent',owning):b,_=Earned.Game.cold(parent)
    for m in(a,b):
        for _ in range(8):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    rows=[]
    for kind in(2,3):
      for tier in(0,1,2):
       trials=[]
       for seed in(b,a):
        m=N.fork(seed);N.put(m,PlayerStatus=tier,ObjectOffset=5)
        for name,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,PowerUpType=kind).items():m[W.address(m.bundle,name)+5]=value
        before=dict(lives=N.get(m,'NumberofLives'),Star=N.get(m,'StarInvincibleTimer'))
        call=invoke(m,0xc7b3)
        after=dict(lives=N.get(m,'NumberofLives'),Star=N.get(m,'StarInvincibleTimer'),tier=N.get(m,'PlayerStatus'),
            flag=N.get(m,'Enemy_Flag',5),HP=m.ram[2][0x6cf],Sword=m.ram[2][0x6ee],score=bytes(m[W.address(m.bundle,'Player1ScoreDisplay'):W.address(m.bundle,'Player1ScoreDisplay')+6]).hex())
        trials.append((m,before,after,call))
       assert trials[0][2]==trials[1][2]and trials[0][3]['regs']==trials[1][3]['regs']
       assert bytes(trials[0][0][:0x800])==bytes(trials[1][0][:0x800]),'Native callback effects differ'
       assert trials[1][2]['flag']==0 and trials[1][2]['tier']==tier
       if kind==2:assert trials[1][2]['Star']>0
       else:assert trials[1][2]['lives']==trials[1][1]['lives']+1
       rows.append(dict(kind=kind,tier=tier,before=trials[1][1],after=trials[1][2],parent_call=trials[0][3],candidate_call=trials[1][3]))
    # Exercise the actual public caller of the moved private death entry.
    source=C.Packet.extract(raw)[1][1];target=0xdf7b
    assert source[target-0xc800:target-0xc800+3]==bytes.fromhex('4cebc7')
    deaths=[]
    for seed in(b,a):
        m=N.fork(seed);call=invoke(m,target);deaths.append(dict(call=call,tier=N.get(m,'PlayerStatus'),engine=N.get(m,'GameEngineSubroutine'),HP=m.ram[2][0x6cf]))
    assert deaths[0]==deaths[1]
    q=dict(passed=True,candidate_SHA256=C.CANDIDATE,callback_cases=rows,actual_moved_death_caller=deaths,
        all_native_RAM_and_public_regs_exact_parent=True,
        scope='Explicit native actor/status inputs and direct existing callbacks; not naturally earned Star/1UP or physical collision',
        native_dispatch_gameplay_seeds_declared=True,outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Native dispatch source components attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
