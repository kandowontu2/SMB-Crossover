"""Reached late sword branches on frozen f582 controls; no new input policy."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import inspect,json,re
import check_prince_body_transition_full_guard_1115 as Base
import current_prince_body_transition_1115 as Current

C,N,W=Base.C,Base.N,Base.Candidate.W


def run(raw):
    current=Current.normalize(raw,kind='prince-body-transition-16a');assert current.original==raw
    actor=C.R/'build/prince-actor-1101-v1'
    text=(actor/'native-battle-v145.lbl').read_text()+(actor/'contact-core.lbl').read_text()
    names={name:int(value,16)for value,name in re.findall(r'^al ([0-9a-fA-F]+) \.?(\S+)$',text,re.M)}
    watch={names[name]:name for name in('PpBattle_7_F090','PpBattle_7_F098','PpBattle_7_F0A5','PpBattle_7_F0A9',
        'PpBattle_7_F0D2','PpBattle_7_F0D7','PpBattle_7_F0E6','PpBattle_7_FE67','PpBattle_7_FE7A',
        'PpBattle_7_FE84','PpBattle_7_FE88','PpBattle_5_8972','PpBattle_5_8943','PpN_5_839F')}
    entry=names['PpBattle_7_F090'];setter=names['PpN_5_8735']
    counts=Counter();contexts=[];health=[];active=None;ticks=0;cpu_at=None;original_cpu=N.NesMPU;original_bus=W.ControllerBus
    def state(m):
        s=m.ram[2];x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
        return dict(Main=ticks,x=x,y=N.get(m,'Player_Y_Position'),source_x=int.from_bytes(s[0x60f:0x611],'little'),
            guard_x=int.from_bytes(s[0x61d:0x61f],'little'),hp=s[0x6cf],action=s[0x616],pose=s[0x617],mode=s[0x618],
            facing=s[0x615],guard_facing=s[0x623],sword=s[0x6ee],guard=s[0x6e0],uid=s[0x61c],marker=s[0x6de],
            requested=m.controller_pad,native=N.get(m,'SavedJoypad1Bits'),source_pad=s[0x40a],forward=s[0x3a],back=s[0x3b],
            phase=s[0xa6],lock=s[0x6c0],control_gate401=s[0x401])
    class Bus(original_bus):
        def __setitem__(self,at,value):
            if isinstance(at,int)and at==0xc6cf and self.rawtags[2]==2 and self.bundle.get('raw')==raw:
                before=self.ram[2][0x6cf]
                if value<before and state(self)['x']>=1800:
                    c=cpu_at;health.append(dict(before=before,after=value,PC=c.pc if c else None,
                        bytes=bytes(self[c.pc:c.pc+3]).hex()if c else None,SP=c.sp if c else None,
                        P=c.p if c else None,state=state(self)))
                    assert len(health)<=16
            return super().__setitem__(at,value)
    class CPU(original_cpu):
        def step(self):
            nonlocal active,cpu_at
            cpu_at=self;m=self.memory
            if hasattr(m,'bundle')and m.bundle.get('raw')==raw and hasattr(m,'ram'):
                x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
                if x>=1800:
                    tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                    if active is not None and self.pc==active['return_PC']and self.sp==active['return_SP']:
                        active['after']=state(m);contexts.append(active);active=None
                        assert len(contexts)<=96
                    expected=3 if self.pc<0xc000 else 2
                    if self.pc==entry and tag==2:
                        assert active is None
                        ret=(m[0x100+((self.sp+1)&255)]+256*m[0x100+((self.sp+2)&255)]+1)&65535
                        active=dict(before=state(m),return_PC=ret,return_SP=(self.sp+2)&255,reached=[],action_stores=[])
                    if self.pc in watch and tag==expected:
                        name=watch[self.pc];counts[name]+=1
                        if active is not None:active['reached'].append(name)
                    if self.pc==setter and tag==3 and self.y==0 and active is not None:
                        active['action_stores'].append(dict(value=self.a,state=state(m)))
            return super().step()
    frame=Base.Candidate.Frames.frame
    def advance(m,*args,**kwargs):
        nonlocal ticks
        ticks+=1;return frame(m,*args,**kwargs)
    source=inspect.getsource(Base.run)
    old='raw,_=C.proposal(parent);text=Replay.controller(raw);metadata=Replay.metadata(raw)'
    new="raw=Current.normalize(parent,kind='prince-body-transition-16a').original;text=Replay.controller(raw);metadata=Replay.metadata(raw)"
    assert source.count(old)==1;source=source.replace(old,new,1)
    space=dict(Base.__dict__,Current=Current);exec(compile(source,str(Path(__file__))+':actual16a-frozen-inputs','exec'),space)
    with patch.object(W,'ControllerBus',Bus),patch.object(N,'NesMPU',CPU),patch.object(Base.Candidate.Frames,'frame',advance):
        q=space['run'](raw)
    assert q['metadata']['Lua_SHA256']=='f5823b8c9d1cf1923289edf07985e9dc9c53dbd878f2341158d0b2a2ce5b69b5'
    assert not q['passed']and q['proof']['logical_updates']==4874
    result=dict(passed=False,diagnostic_complete=True,retained_route_receipt=q['receipt_SHA256'],
        ROM_SHA256=C.CANDIDATE,frozen_Lua_SHA256=q['metadata']['Lua_SHA256'],terminal=q['proof']['terminal'],
        reached_counts=dict(counts),late_control_contexts=contexts,HP_writes=health,
        actual_relocated_labels={name:pc for pc,name in watch.items()},
        no_input_changes=True,no_game_bytes_or_gameplay_seeds=True,Mesen=False,outputs=0,
        scope='Real reached branches on the frozen negative ordinary route, not another control experiment or full-stage pass')
    result['receipt_SHA256']=sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return result


if __name__=='__main__':
    def deny(*args,**kwargs):raise AssertionError('Sword admission trace attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
