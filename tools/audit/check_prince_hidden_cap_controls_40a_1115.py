"""Ordinary control-admission components from one genuinely reached cap.

No actor, terrain, position, health, ability or outcome state is seeded.
Branches clone the same actual full-cap continuation in memory. They are
control-admission diagnostics, not natural1UP or full-stage qualifications.
"""
from pathlib import Path
from unittest.mock import patch
import json
import check_prince_natural_stock_40a_1115 as Route
import replay_prince_hidden_fullcap_40a_1115 as Factory

C,N,Frames,Game=Factory.C,Route.N,Route.Frames,Route.Cold.Game

def run(raw):
    assert C.digest(raw)==Factory.PIN
    text=Factory.controller(raw);old="stockPhase('cap-run',1)"
    assert text.count(old)==1
    text=text.replace(old,"stockPhase('cap-observation',0);final=s;finish(false,'Genuine full-cap control-admission checkpoint');return true",1)
    model,opening=Route.Cold.cold(raw);actual=Frames.frame;receipts=[];loads=Game.json.loads
    def capture(*a,**k):
        q=loads(*a,**k)
        if isinstance(q,dict)and'natural_stock'in q:receipts.append(q)
        return q
    def frame(m,*a,**k):return actual(m,whole_pass=True)
    with patch.object(Game,'controller',lambda image:text),patch.object(Game.json,'loads',capture),patch.object(Game.Frames,'frame',frame):
        proof=Game.route(model,raw,2200)
    assert len(receipts)==1 and proof['reason']=='Genuine full-cap control-admission checkpoint'
    checkpoint=receipts[0];assert checkpoint['new_candidate_readback']['bytes']==4193
    assert model.ram[2][0x616]==42 and model.ram[2][0x618]==0 and N.get(model,'Player_Y_Position')==112
    rows=[];base=N.NesMPU;runtime=C.Packet.extract(raw)[1][0];point=0xaa51;pre=runtime[point-0xa000:point-0xa000+8]
    for name,mask in(('Up',8),('A',128),('RightA',129),('carefulRight',65)):
        m=N.fork(model);events=[];samples=[];last=None;epoch=0
        class CPU(base):
            def step(self):
                if self.pc==point and self.memory.rawtags[1]==3 and self.y==0 and len(events)<8:
                    assert bytes(self.memory[point:point+8])==pre
                    events.append(dict(epoch=epoch,PC=self.pc,SP=self.sp,requested=self.a,state=Route.Cold.Previous.state(m)))
                return super().step()
        with patch.object(N,'NesMPU',CPU):
            for epoch in range(80):
                m.controller_pad=mask if epoch<8 else 0;actual(m,whole_pass=True)
                s=Route.Cold.Previous.state(m);key=(s['action'],s['pose'],s['mode'])
                if key!=last and len(samples)<8:samples.append(dict(epoch=epoch,mask=m.controller_pad,state=s));last=key
                if s['HP']==0:break
        rows.append(dict(name=name,buttons_first8_Main=mask,later_buttons=0,actual_Main_updates=epoch+1,action_admissions=events,first_eight_changed_states=samples,terminal=Route.Cold.Previous.state(m)))
    q=dict(passed=True,scope='Actual reached-cap ordinary control-admission components only; not item acquisition',ROM_SHA256=C.digest(raw),checkpoint_Lua_SHA256=C.digest(text.encode()),opening=opening,checkpoint=checkpoint['natural_stock']['start'],first_BBC1=checkpoint['new_candidate_readback'],branches=rows,state_seeds=0,no_gameplay_patches=True,outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Cap control components attempted output/native launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
