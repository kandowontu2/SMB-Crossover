"""Ordinary hidden60 approach with the first actual source failure retained."""
from collections import Counter,deque
from pathlib import Path
from unittest.mock import patch
import argparse,json,struct
import audit_sonic_stock_foundation_1327_1116 as F
import sonic_natural_stock_policy_1327_1116 as Policy
from check_ff_stdout_controller_source_1110 import LuaRuntime

GRANT=F.R/'docs/qa/allocations/sonic-natural-stock-source-root-1116.json'


def run(raw,form='sonic',limit=900):
    lease=json.loads(GRANT.read_text());assert lease['ROM_SHA256']==F.PIN and lease['source_in_memory_gameplay_authorized']
    assert not lease['modified_game_bytes_or_physical_ROM_native_Downloads_authorized']
    q=F.bindings(raw);m,cold=F.cold(raw,form);N,W=F.N,F.W
    lua=LuaRuntime();lua.globals().SONIC_READ=lambda name,index=0:N.get(m,name,index)
    lua.globals().SONIC_MEMORY=lambda at:m[at]
    policy=lua.execute(Policy.text()).new('life')
    counts=Counter();objects=[];rejects=[];heads=[];births=[];workers=[];ring=[];tail=deque(maxlen=8);changes=[]
    finished=False;fault=None;ctx={'inside':False};lastphase=None;oldring=m.ram[2][0x340]
    framepc=struct.unpack('<H',q['metadata'][10:12])[0];assert framepc==0xbbb0
    points={(q['hooks']['GameLoop']['tag'],q['hooks']['GameLoop']['PC']):'Main',(3,framepc):'OriginalFrame',
        (3,q['hooks']['SonicHostMain']['PC']):'HostMain',
        (q['hooks']['PlayerHeadCollision']['tag'],q['hooks']['PlayerHeadCollision']['PC']):'Head'}
    def tag(pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    def signed(at):
        v=int.from_bytes(bytes(m.ram[2][at:at+3]),'little');return v-(1<<24)if v&(1<<23)else v
    def state():
        r=lambda n:N.get(m,n)
        return dict(x=r('Player_X_Position')+256*r('Player_PageLoc'),y=r('Player_Y_Position'),state=r('Player_State'),
            source_flags=m.ram[2][0x30],source_vy=list(m.ram[2][0x60:0x63]),vx=signed(0x20),vy=signed(0x60),
            frame_status=m.ram[2][0x116],source_tick=m.ram[2][0x92],status=r('PlayerStatus'),rings=m.ram[2][0x340],
            lives=r('NumberofLives'),engine=r('GameEngineSubroutine'),Main=counts['Main_return'],motor=counts['accepted_original'],
            saved=r('SavedJoypadBits'),source_input=m.ram[2][0xa8],native_yhigh=r('Player_Y_HighPos'),
            camera=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc'))
    def actors():
        result=[]
        for i in range(6):
            r=lambda n:N.get(m,n,i)
            if r('Enemy_Flag'):result.append(dict(slot=i,flag=r('Enemy_Flag'),id=r('Enemy_ID'),state=r('Enemy_State'),kind=r('PowerUpType'),
                x=r('Enemy_X_Position')+256*r('Enemy_PageLoc'),y=r('Enemy_Y_Position')))
        return result
    def after_main():
        nonlocal finished,lastphase,oldring
        s=state();aa=actors()
        assert N.get(m,'SelectedCharacter')==43 and m[0x5ffe]==F.FORMS[form][0]
        assert s['lives']==2 and s['engine']!=11 and N.get(m,'WorldNumber')==N.get(m,'LevelNumber')==0,('Ordinary route failed',s)
        assert N.get(m,'CheatStartLevel')==N.get(m,'CheatInvincible')==0
        assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(q['cookie'],)*2
        if s['rings']!=oldring:
            if len(ring)<8:ring.append(dict(before=oldring,after=s['rings'],state=s))
            oldring=s['rings']
        for a in aa:
            if a['id']==46 and not births:births.append(dict(actor=a,state=s))
        if rejects and counts['rejected_original']:
            finished=True;return
        pad=policy.decide(policy,lua.table_from(s),lua.table_from([lua.table_from(a)for a in aa]))
        assert isinstance(pad,int)and 0<=pad<=255
        phase=policy.phase
        if phase!=lastphase:
            assert len(changes)<16;changes.append(dict(phase=phase,state=s,pad=pad));lastphase=phase
        tail.append(dict(state=s,phase=phase,pad=pad));m.controller_pad=pad
    base=N.NesMPU
    class CPU(base):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self.pending=[];objects.append(self)
        def settle(self):
            while self.pending and(self.pc,self.sp,tag(self.pc))==self.pending[-1][1]:
                name,_=self.pending.pop();counts[name+'_return']+=1
                if name=='OriginalFrame':
                    counts['accepted_original'if self.p&1 else'rejected_original']+=1
                    if rejects and len(workers)<4:workers.append(dict(PC=self.pc,tag=tag(self.pc),SP=self.sp,P=self.p,C=self.p&1,state=state()))
                elif name=='Main':after_main()
        def step(self):
            self.settle();t=tag(self.pc);name=points.get((t,self.pc))
            if(t,self.pc)==(3,0xb842)and m.ram[2][0x104]==0x60 and not rejects:
                rejects.append(dict(PC=self.pc,tag=t,SP=self.sp,A=self.a,X=self.x,Y=self.y,P=self.p,state=state(),
                    phase=policy.phase,requested_pad=m.controller_pad,query=dict(axis=m.ram[2][0xb7],negative=m.ram[2][0xb8],
                    worldX=int.from_bytes(bytes(m.ram[2][0x100:0x102]),'little'),screenY=int.from_bytes(bytes(m.ram[2][0x102:0x104]),'little'),
                    tile=m.ram[2][0x104],attributes=m.ram[2][0x105],cellX=int.from_bytes(bytes(m.ram[2][0x106:0x108]),'little'),
                    cellY=int.from_bytes(bytes(m.ram[2][0x108:0x10a]),'little'),buffer_index=m.ram[2][0x10b],buffer_page=m.ram[2][0x10c]),
                    source_position=list(m.ram[2][0x70:0x76]),first12=bytes(m[self.pc:self.pc+12]).hex()))
            if name=='Head':
                if len(heads)<8:heads.append(dict(tile=self.a,PC=self.pc,tag=t,SP=self.sp,state=state()))
            elif name:
                counts[name+'_entry']+=1;sp=self.sp
                pc=(m[0x100+((sp+1)&255)]+256*m[0x100+((sp+2)&255)]+1)&65535
                self.pending.append((name,(pc,(sp+2)&255,tag(pc))))
            ctx.update(PC=self.pc,tag=t,SP=self.sp,opcode=m[self.pc])
            return super().step()
    try:
        with patch.object(N,'NesMPU',CPU):
            for _ in range(limit):
                F.Frames.frame(m,whole_pass=True)
                for c in objects:c.settle();assert not c.pending
                objects.clear()
                if finished:break
    except Exception as error:fault=dict(error=repr(error),context=dict(ctx),state=state())
    if fault is None:
        assert all(counts[n+'_entry']==counts[n+'_return']for n in('Main','OriginalFrame','HostMain'))
    out=dict(passed=fault is None and finished,diagnostic_only=True,natural_life_qualified=False,fault=fault,
        ROM_SHA256=F.PIN,form=form,cold=cold,Main=counts['Main_return'],counts=dict(counts),
        first_actual_60_rejection=rejects,actual_original_returns_after_rejection=workers,head=heads,births=births,
        ring_changes=ring,phase_changes=changes,tail=list(tail),terminal=state(),
        policy_SHA256=F.H(Policy.text().encode()),policy_module_SHA256=F.H(Path(Policy.__file__).read_bytes()),
        source_SHA256=F.H(Path(__file__).read_bytes()),modified_game_or_actor_or_resource_or_helper_bytes=False,
        outputs=0,native=False)
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--form',choices=tuple(F.FORMS),default='sonic');p.add_argument('--limit',type=int,default=900);a=p.parse_args()
    assert 100<=a.limit<=1200;raw=F.ROM.read_bytes();assert F.H(raw)==F.PIN
    def deny(*a,**kw):raise AssertionError('Sonic source diagnostic attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(raw,a.form,a.limit)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
