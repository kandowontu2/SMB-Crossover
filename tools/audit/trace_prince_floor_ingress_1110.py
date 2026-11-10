"""Trace the first old/new native floor ingress difference; stdout only."""
import json
import sys
from unittest.mock import patch

import check_prince_floor_carrier_1110 as Q

C,N,I=Q.C,Q.N,Q.I


def main():
    _,trial,_,layout,_,_,_=Q.proposal(admission='--unconditional' not in sys.argv)
    env,seed,labels,_=C.Failure.Roof.Climb.Earned.fixture(trial)
    C.Seam.terrain(seed,C.Failure.Roof.terrain);C.Seam.layout(seed,811-255,678,scroll=0)
    C.Route.install_group(seed)
    old,new=N.fork(seed),N.fork(seed)
    old.ram[3][0x1d3e:0x1d42]=bytes.fromhex('a0063860')
    native=N.NesMPU;target=None;kind=None;tick=0;points=[];pending=[];writes=[]
    watch={(3,0xbd3e):'SourceAdder',(2,0xd4d7):'FrozenFloor',(3,0xb310):'SourcePoint'}
    for name in ('BlockBufferColli_Feet','CrossoverSourceFootProbe','GuestLandingWindow',
                 'RosterGuestFootContactSide','SamusStopAtWallBanked'):
        if name in trial['syms']:
            watch[((I.location(trial,name)-16)//8192)|128,I.address(trial,name)]=name
    def state(m):
        return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            y=N.get(m,'Player_Y_Position'),native=N.get(m,'Player_State'),
            source_x=int.from_bytes(m.ram[2][0x60f:0x611],'little'),source_y=m.ram[2][0x611],
            foot=int.from_bytes(m.ram[2][0x84:0x86],'little'),delta=m.ram[2][0x88],
            action=m.ram[2][0x616],frame=m.ram[2][0x617],mode=m.ram[2][0x618])
    class Trace(native):
        def step(self):
            if self.memory is not target:return super().step()
            m=target;pc=self.pc;tag=m.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
            if True:
                for item in pending[:]:
                    if (self.pc,self.sp)==item['return']:
                        item['out']=dict(regs=[self.a,self.x,self.y,self.p,self.sp],state=state(m),scratch=bytes(m[3:11]).hex())
                        points.append(item);pending.remove(item)
                name=watch.get((tag,pc))
                if name:
                    back=(m[0x101+self.sp]|m[0x102+self.sp]<<8)+1
                    pending.append(dict(kind=kind,tick=tick,name=name,return_=[back&65535,self.sp+2],
                        **{'return':(back&65535,self.sp+2)},regs=[self.a,self.x,self.y,self.p,self.sp],
                        state=state(m),scratch=bytes(m[3:11]).hex(),
                        point=list(m.ram[3][0x1369:0x136d]),dy=N.get(m,'Player_Y_Speed')))
            before=(m[0x75]+256*m[0x5c],m[0xbd],m[0x1e]);result=super().step()
            triple=(m[0x75]+256*m[0x5c],m[0xbd],m[0x1e])
            if before!=triple:
                after=state(m);before=dict(after,x=before[0],y=before[1],native=before[2])
                writes.append(dict(kind=kind,tick=tick,bank=tag,pc=pc,before=before,after=after))
            return result
    pad=0;first=None;rows=[]
    with patch.object(N,'NesMPU',Trace):
        for tick in range(6 if '--short' in sys.argv else 172):
            pad={0:1,8:0,51:8,106:9,112:8}.get(tick,pad)
            for kind,target in (('old',old),('new',new)):
                C.Route.controls(env,target,labels,pad)
            a,b=state(old),state(new)
            if a!=b and first is None:first=dict(tick=tick,old=a,new=b)
            if a!=b and (tick<12 or tick%4==3):rows.append(dict(tick=tick,old=a,new=b))
    print('FIRST_DIFFERENCE '+json.dumps(first),flush=True)
    interesting={first['tick']-1,first['tick']} if first else {0}
    print('CALLS '+json.dumps([{k:v for k,v in p.items() if k not in ('return','return_')} for p in points if p['tick'] in interesting]),flush=True)
    print('NATIVE_WRITES '+json.dumps([p for p in writes if p['tick'] in interesting]),flush=True)
    print('TRAJECTORY '+json.dumps(rows),flush=True)


if __name__=='__main__':main()
