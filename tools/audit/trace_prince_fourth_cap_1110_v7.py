"""Trace the first real fourth-cap careful-support rejection; zero artifacts."""
import contextlib
import io
import json
import sys
from unittest.mock import patch
import check_prince_wall_sweep_1110_v6 as V
import check_prince_wait_pose_route_1110_v3 as Route


def main():
    result=V.proposal();N,I,F,Q=V.N,V.I,V.F,V.Q
    native=N.NesMPU;sample=F.sample;target=None;tick=-1;last=[];calls=[];pending=[];actions=[]
    def state(m):
        foot=int.from_bytes(m.ram[2][0x84:0x86],'little');delta=m.ram[2][0x88]
        return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            y=N.get(m,'Player_Y_Position'),native_ground=N.get(m,'Player_State'),
            dy=N.get(m,'Player_Y_Speed'),source_x=int.from_bytes(m.ram[2][0x60f:0x611],'little'),
            foot=foot,oldfoot=int.from_bytes(m.ram[2][0x86:0x88],'little'),delta=delta,
            logical_anchor=(foot-delta+3)&65535,action=m.ram[2][0x616],frame=m.ram[2][0x617],
            mode=m.ram[2][0x618],surface=int.from_bytes(m.ram[2][0x7f:0x81],'little'),
            raw=int.from_bytes(m.ram[2][0x78:0x7a],'little'),
            query=list(m.ram[3][0x1369:0x136d]))
    def observer(m,epoch):
        nonlocal target,tick
        target,tick=m,epoch
        return sample(m,epoch)
    class Trace(native):
        def step(self):
            if self.memory is not target or not 608<=tick<=623:return super().step()
            m=target;pc=self.pc;tag=m.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
            for q in pending[:]:
                if (pc,self.sp)==q['return']:
                    q['out']=dict(A=self.a,P=self.p,state=state(m),last_worker_instructions=list(last))
                    calls.append({k:v for k,v in q.items() if k!='return'});pending.remove(q)
            if tag==2 and 0xd6d1<=pc<0xd755:
                last.append(dict(pc=pc,op=bytes(m[pc:pc+3]).hex(),A=self.a,P=self.p))
                last[:]=last[-6:]
                if pc==0xd6d1:
                    back=((m[0x101+self.sp]|m[0x102+self.sp]<<8)+1)&65535
                    pending.append(dict(tick=tick,state=state(m),**{'return':(back,self.sp+2)}))
                if pc==0xd6d4 and pending:pending[-1]['WorldTile_return']=dict(A=self.a,P=self.p,state=state(m))
            if tag==3 and pc==0xa34d and self.y==0:
                actions.append(dict(tick=tick,admitted=self.a,state=state(m)))
            return super().step()
    with patch.object(Q,'proposal',lambda:result),patch.object(F,'sample',observer),patch.object(N,'NesMPU',Trace),\
         patch.object(sys,'argv',[Route.__file__,'--park','careful','--approach','careful']):
        with contextlib.redirect_stdout(io.StringIO()) as buffer:Route.main()
    route=json.loads(buffer.getvalue().split('WAIT_POSE_ROUTE ',1)[1])
    print('FOURTH_CAP_CAUSE '+json.dumps(dict(SHA256=result[3]['in_memory_SHA256'],calls=calls,actions=actions,
        outcome=route['outcome'],terminal=route['terminal'],helpers_added=0,outputs_written=0),separators=(',',':')),flush=True)


if __name__=='__main__':main()
