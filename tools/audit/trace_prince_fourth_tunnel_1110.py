"""Trace the first invalid fourth-pipe step, using real GameLoop and NMI.

Only stdout is produced. No ROM, state, receipt, image or capture is written.
"""
import json
from unittest.mock import patch

import check_prince_fourth_route_1110 as F

C,N,I=F.C,F.N,F.I


def main():
    raw=F.Exit.ROM.read_bytes();assert C.digest(raw)==F.Exit.PIN
    bundle=C.Start.W.bundle(raw);env,seed,labels=C.fixture(bundle)
    N.put(seed,CrossoverBehaviorVersion=0);N.consume(seed)
    F.REAL_NMI=True;_,seed=F.authored(seed)
    native=N.NesMPU;controls=C.Route.controls
    target=None;tick=-1;events=[];points=[];pending=[];frames=[];recent=[]
    source_x=lambda m:int.from_bytes(m.ram[2][0x60f:0x611],'little')
    native_x=lambda m:N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
    watch={(3,0xb310):'SourcePoint',(3,0xbde2):'WorldTile',(3,0xbde5):'WorldTileY',
           (2,0xc40b):'WorldAlign',(3,0xc383):'WorldExport'}
    watch[(3,0xbd3e)]='PpNativeAdder'
    for name in ('BlockBufferColli_Side','CrossoverSourceSideProbe','ImpedePlayerMove',
                 'GuestLandingWindow','RosterGuestFootContactSide',
                 'SamusStopAtWallBanked','SamusStopAtWallBanked::NativeGuest',
                 'SamusStopAtWallBanked::LeftClamp','SamusStopAtWallBanked::RightClamp'):
        if name in bundle['syms']:
            watch[((I.location(bundle,name)-16)//8192)|128,I.address(bundle,name)]=name
    class Done(Exception):pass
    def controls_tick(e,m,l,pad):
        nonlocal target,tick
        tick+=1;target=m
        if tick>112:raise Done()
        result=controls(e,m,l,pad)
        if tick>=90:
            left=C.Seam.xcamera(m)[0]
            box=[m[0x658+i]+(left if i%2==0 else 0) for i in range(4)]
            frames.append(dict(tick=tick,player=C.Recovery.sample(m,tick),world_box=box,
                               overlaps_pipe=box[0]<944 and box[2]>=912 and box[1]<208 and box[3]>144))
        return result
    class Trace(native):
        def step(self):
            if self.memory is not target or not 90<=tick<=112:return super().step()
            m=target;pc=self.pc;tag=m.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
            for item in pending[:]:
                if (pc,self.sp)==item['return']:
                    item['out']=dict(a=self.a,x=self.x,y=self.y,p=self.p,
                                     source_x=source_x(m),native_x=native_x(m),scratch=bytes(m[3:11]).hex())
                    points.append(item);pending.remove(item)
            name=watch.get((tag,pc))
            if name and name!='WorldExport':
                back=(m[0x101+self.sp]|m[0x102+self.sp]<<8)+1
                pending.append(dict(name=name,tick=tick,pc=pc,bank=tag,
                    regs=[self.a,self.x,self.y,self.p,self.sp],return_=[back&65535,self.sp+2],
                    **{'return':(back&65535,self.sp+2)},source_x=source_x(m),native_x=native_x(m),
                    point=[int.from_bytes(m.ram[3][0x1369:0x136b],'little'),
                           int.from_bytes(m.ram[3][0x136b:0x136d],'little')],
                    foot=int.from_bytes(m.ram[2][0x84:0x86],'little'),
                    oldfoot=int.from_bytes(m.ram[2][0x86:0x88],'little'),
                    dy=N.get(m,'Player_Y_Speed'),
                    world_query=bytes(m.ram[2][0x78:0x7b]).hex(),
                    source_fields=bytes(m.ram[2][0x615:0x619]).hex(),scratch=bytes(m[3:11]).hex()))
            before=(source_x(m),native_x(m))
            recent.append([tag,pc,self.a,self.x,self.y,self.p,self.sp])
            if len(recent)>16:recent.pop(0)
            result=super().step()
            after=(source_x(m),native_x(m))
            if before!=after:
                events.append(dict(tick=tick,pc=pc,bank=tag,before=before,after=after,
                    source_fields=bytes(m.ram[2][0x615:0x619]).hex(),trace=recent[:]))
            return result
    with patch.object(C.Route,'controls',controls_tick),patch.object(N,'NesMPU',Trace):
        try:F.trial(env,seed,labels,'roll-up')
        except Done:pass
    print('NATIVE_SYMBOLS '+json.dumps({name:dict(pc=pc,bank=tag) for (tag,pc),name in watch.items()}),flush=True)
    print('X_WRITES '+json.dumps([{k:v for k,v in q.items() if k!='trace' or 101<=q['tick']<=103} for q in events],separators=(',',':')),flush=True)
    selected=[]
    for q in points:
        if not 100<=q['tick']<=105:continue
        if q['name']=='SourcePoint' and not (q['out']['p']&1 and 880<=q['point'][0]<=960):continue
        selected.append({k:v for k,v in q.items() if k not in ('return','return_')})
    print('SOURCE_AND_NATIVE_QUERIES '+json.dumps(selected,separators=(',',':')),flush=True)
    print('FRAMES '+json.dumps([dict(tick=q['tick'],x=q['player']['x'],y=q['player']['y'],
        world_box=q['world_box'],overlap=q['overlaps_pipe']) for q in frames],separators=(',',':')),flush=True)


if __name__=='__main__':main()
