"""Trace genuine Prince wall queries on translated authored1-1; stdout only.

No source inventory, native enemy outcome, physics, or terrain is changed by
the observer. The seed remains an explicitly translated CPU scene.
"""
from collections import Counter
import json
from unittest.mock import patch

import check_prince_floor_carrier_1110 as Q

C,N,I,F=Q.C,Q.N,Q.I,Q.Foot.F


def main():
    _,bundle,_,layout,_,_,_=Q.proposal()
    native=N.NesMPU;controls=C.Route.controls
    target=None;tick=-1;part='third';pending=[];queries=[];points=[];aligns=[];poses=[]
    watch={(3,0xbde5):'WorldTileY',(2,0xc40b):'WorldAlign',(3,0xb310):'ReadPoint'}
    def state(m):
        return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            y=N.get(m,'Player_Y_Position'),source_x=int.from_bytes(m.ram[2][0x60f:0x611],'little'),
            source_y=m.ram[2][0x611],foot=int.from_bytes(m.ram[2][0x84:0x86],'little'),
            action=m.ram[2][0x616],frame=m.ram[2][0x617],mode=m.ram[2][0x618],
            facing=m.ram[2][0x615],HP=m.ram[2][0x6cf])
    def world(m):
        return dict(raw=int.from_bytes(m.ram[2][0x78:0x7a],'little'),base=m.ram[2][0x7a],
            index=m.ram[2][0x7b],row=m.ram[2][0x7c],cell_x=int.from_bytes(m.ram[2][0x7d:0x7f],'little'),
            surface=int.from_bytes(m.ram[2][0x7f:0x81],'little'),surface_row=m.ram[2][0x81],
            room_rows=m.ram[2][0x82],current_row=m.ram[2][0x83],wall=m.ram[2][0x8c],
            floor=m.ram[2][0x8d],baseline=int.from_bytes(m.ram[2][0x9b:0x9d],'little'),
            material=m.ram[2][0x9f])
    class Trace(native):
        def step(self):
            if self.memory is not target:return super().step()
            m=target;pc=self.pc;tag=m.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
            for item in pending[:]:
                if (pc,self.sp)==item['return']:
                    item['out']=dict(regs=[self.a,self.x,self.y,self.p,self.sp],state=state(m),world=world(m))
                    if item['name']=='ReadPoint':points.append(item)
                    elif item['name']=='WorldAlign':aligns.append(item)
                    else:queries.append(item)
                    pending.remove(item)
            name=watch.get((tag,pc))
            if name:
                back=((m[0x101+self.sp]|m[0x102+self.sp]<<8)+1)&65535
                pending.append(dict(part=part,tick=tick,name=name,bank=tag,pc=pc,
                    caller=(back-3)&65535,**{'return':(back,self.sp+2)},
                    regs=[self.a,self.x,self.y,self.p,self.sp],state=state(m),world=world(m),
                    point=[int.from_bytes(m.ram[3][0x1369:0x136b],'little'),
                           int.from_bytes(m.ram[3][0x136b:0x136d],'little')]))
            return super().step()
    def run_controls(e,m,l,pad):
        nonlocal target,tick
        target=m;tick+=1
        result=controls(e,m,l,pad)
        if part=='fourth' and tick>=89:poses.append(dict(tick=tick,pad=pad,**state(m)))
        return result
    with patch.object(N,'NesMPU',Trace),patch.object(C.Route,'controls',run_controls):
        env,seed,labels=C.fixture(bundle)
        N.put(seed,CrossoverBehaviorVersion=0);N.consume(seed)
        F.REAL_NMI=True;_,model=F.authored(seed)
        part='fourth';tick=-1;stage='run';landed=None
        for epoch in range(143):
            row=F.sample(model,epoch);x,y=row['x'],row['y']
            if not row['hp'] or row['engine']!=8 or row['lives']!=2:break
            if stage=='run' and 745<=x<=752 and abs(y-112)<=2 and C.Recovery.running(model,row):stage='takeoff'
            if stage=='takeoff' and row['action']==4:stage='flight'
            if landed is None and N.get(model,'Enemy_State',1)==4:landed=epoch
            pad=129 if stage=='takeoff' else 1
            if landed is not None:pad=8
            C.Route.controls(env,model,labels,pad);N.consume(model)
    # Collapse identical query states, retaining first timing and multiplicity.
    unique={};counts=Counter()
    for q in queries:
        if not(q['part']=='fourth' and 91<=q['tick']<=141 or
               q['part']=='third' and q['state']['mode'] in (2,6)):
            continue
        key=json.dumps([q['part'],q['state']['action'],q['state']['mode'],q['regs'][2],q['out']['regs'][0],
            q['out']['world']['cell_x'],q['out']['world']['row'],q['out']['world']['surface']],sort_keys=True)
        counts[key]+=1;unique.setdefault(key,q)
    selected=[]
    for k,q in unique.items():
        selected.append(dict(count=counts[k],**{a:b for a,b in q.items() if a!='return'}))
    def clean(rows):return [{k:v for k,v in q.items() if k!='return'} for q in rows]
    pkeys=set();pselect=[]
    for q in points:
        if q['part']!='fourth' or not 91<=q['tick']<=141:continue
        key=tuple(q['point'])+(q['out']['regs'][0],q['out']['regs'][3]&1)
        if key in pkeys:continue
        pkeys.add(key);pselect.append(dict(tick=q['tick'],caller=q['caller'],point=q['point'],
            A=q['out']['regs'][0],C=q['out']['regs'][3]&1,action=q['state']['action'],mode=q['state']['mode']))
    print('WALL_TRACE '+json.dumps(dict(in_memory_SHA256=layout['in_memory_SHA256'],landing=landed,
        translated_CPU_scene=True,source_or_native_outcomes_seeded=False,ROM_written=False,outputs_written=0,
        poses=poses,world_queries=selected,aligns=clean(aligns),native_points=pselect),separators=(',',':')),flush=True)


if __name__=='__main__':main()
