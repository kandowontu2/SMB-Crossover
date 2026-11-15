"""Ordinary fourth-pipe inputs from a genuinely executed three-pipe prefix.

Checkpoint branches clone that actual Main-return state. They never install
positions, actors, health, power, terrain or abilities. This is a CPU input
component, not a standalone native/full-stage qualification.
"""
from hashlib import sha256
import argparse,json
from unittest.mock import patch
import check_prince_body_world_1114 as Game
import current_prince_body_research_input_1114 as Current

C,P,N=Game.C,Game.P,Game.N


def state(m):
    s=m.ram[2]
    actors=[]
    for slot in range(6):
        if N.get(m,'Enemy_Flag',slot):
            actors.append(dict(slot=slot,id=N.get(m,'Enemy_ID',slot),state=N.get(m,'Enemy_State',slot),
                x=N.get(m,'Enemy_X_Position',slot)+256*N.get(m,'Enemy_PageLoc',slot),y=N.get(m,'Enemy_Y_Position',slot)))
    return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
        high=N.get(m,'Player_Y_HighPos'),ground=N.get(m,'Player_State'),lives=N.get(m,'NumberofLives'),
        engine=N.get(m,'GameEngineSubroutine'),hp=s[0x6cf],sword=s[0x6ee],power=N.get(m,'PlayerStatus'),
        sx=int.from_bytes(s[0x60f:0x611],'little'),sy=s[0x611],action=s[0x616],pose=s[0x617],
        mode=s[0x618],lock=s[0x6c0],facing=s[0x615],foot=int.from_bytes(s[0x84:0x86],'little'),
        donor_raw_x=int.from_bytes(s[0x78:0x7a],'little'),
        surface=int.from_bytes(s[0x7f:0x81],'little'),native_pad=N.get(m,'SavedJoypad1Bits'),actors=actors)


def run(parent,*,edges=(880,888,892,896),jump=False,trace_queries=False,third_cap=False):
    raw,info=C.proposal(parent);model,opening=Game.cold(raw)
    text=Game.Factory.controller(raw,mode='earned')
    old="          switch('third-park',65)"if third_cap else"    switch('fourth-recovery',1)"
    assert text.count(old)==1
    text=text.replace(old,"    final=s;finish(true,'Actual played third-pipe descent checkpoint');return",1)
    with patch.object(P,'controller',lambda image:text):prefix=P.route(model,raw,2500)
    assert prefix['passed'] and prefix['terminal']['x']>=(720 if third_cap else 784),prefix
    assert model.ram[2][0x6cf]>0
    base_cpu=N.NesMPU;cases=[];active={};commits=0;pending=[];queries=[];query_keys=set()
    head=P.W.address(model.bundle,'BlockBufferColli_Head')
    head_tag=((P.W.location(model.bundle,'BlockBufferColli_Head')-16)//8192)|128
    def query_entry(cpu,kind):
        m=cpu.memory;s=m.ram[2];sp=cpu.sp
        ret=((m[0x100+((sp+1)&255)]|m[0x100+((sp+2)&255)]<<8)+1)&65535
        row=dict(kind=kind,commit=commits,PC=cpu.pc,caller=ret-3,A=cpu.a,X=cpu.x,Y=cpu.y,
            x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),y=N.get(m,'Player_Y_Position'),
            sx=int.from_bytes(s[0x60f:0x611],'little'),sy=s[0x611],action=s[0x616],pose=s[0x617],mode=s[0x618],
            donor_raw_x=int.from_bytes(s[0x78:0x7a],'little'),body_row=s[0x83],row_index=s[0x4b1],foot=int.from_bytes(s[0x84:0x86],'little'))
        if kind=='native-collision-entry':
            xadd=P.W.address(m.bundle,'BlockBuffer_X_Adder');yadd=P.W.address(m.bundle,'BlockBuffer_Y_Adder')
            head_index=N.get(m,'Local_eb')
            row.update(sample_x=row['x']+m[xadd+cpu.y],sample_y=row['y']+m[yadd+cpu.y],index=cpu.y,
                probe='head'if cpu.y==head_index else'foot'if cpu.y in(head_index+1,head_index+2)else'other')
        pending.append((ret,(sp+2)&255,m.rawtags[(ret-0x8000)//8192]if ret>=0x8000 else None,row))
    class CPU(base_cpu):
        def step(self):
            nonlocal commits
            m=self.memory
            if m is active.get('model'):
                if self.pc==0xb37c and m.rawtags[1]==3:commits+=1
                if trace_queries:
                    tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else None
                    if pending and(self.pc,self.sp,tag)==pending[-1][:3]:
                        row=pending.pop()[3];s=m.ram[2]
                        row.update(result=self.a,carry=self.p&1,query_row=s[0x7c],surface=int.from_bytes(s[0x7f:0x81],'little'),
                            last_native_point_x=int.from_bytes(m.ram[3][0x1369:0x136b],'little'),
                            last_native_point_y=int.from_bytes(m.ram[3][0x136b:0x136d],'little'),R4=m[7],R5=m[8])
                        key=tuple(row[k]for k in('kind','caller','action','pose','result','query_row'))
                        if key not in query_keys:
                            queries.append(row);query_keys.add(key)
                            if len(queries)>96:queries.pop(32)
                    if active.get('phase')!='approach'and m.ram[2][0x616]in(3,4,8,28,47):
                        # The BDE2 public entry falls through BDE5 at the
                        # same stack depth; observe the common body once.
                        if self.pc==0xbde5 and tag==3:query_entry(self,'WorldMaterial')
                        elif self.pc==head and tag==head_tag:query_entry(self,'native-collision-entry')
            return super().step()
    assert all((723 if third_cap else 844)<=edge<=896 for edge in edges)and 1<=len(edges)<=4
    for edge in edges:
        m=N.fork(model);active['model']=m;commits=0;mode='approach';changed=0;rows=[];previous=None;hang=top=False
        pending.clear();queries.clear();query_keys.clear()
        for tick in range(540):
            s=state(m)
            running=s['action']==1 and s['mode']==1 and 6<=s['pose']<=13 and s['lock']==0
            if mode=='approach' and s['x']>=edge and(not third_cap or running):
                mode='takeoff'if jump else'up';changed=commits
            if jump and mode=='takeoff'and s['action']==4:mode='flight'
            if jump and s['mode']in(2,6):mode='up'
            active['phase']=mode
            pad=1 if mode in('approach','flight')else 129 if mode=='takeoff'else 8
            key=(mode,s['x'],s['y'],s['action'],s['pose'],s['hp'])
            if key!=previous:
                rows.append(dict(Main=tick,commits=commits,pad=pad,**s));previous=key
                if len(rows)>80:rows.pop(8)
            hang|=s['mode']in(2,6)
            top|=s['high']==1 and abs(s['y']+32-144)<=1 and s['ground']==0 and s['x']+13>=912 and s['x']<944
            if third_cap and top:break
            if s['hp']==0 or s['lives']!=2 or s['engine']!=8:break
            if mode!='approach' and commits-changed>=240:break
            m.controller_pad=pad
            with patch.object(N,'NesMPU',CPU):P.Frames.frame(m)
        cases.append(dict(edge=edge,jump=jump,third_cap=third_cap,mode=mode,Main_frames=tick,admitted_source_commits=commits,
            post_trigger_commits=commits-changed if mode!='approach'else 0,hang=hang,top=top,terminal=state(m),
            trace=rows[::4],trace_SHA256=sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest(),
            returned_queries=list(queries),unreturned_observer_calls=len(pending)))
    return dict(composition=info,opening=opening,prefix=prefix,prefix_terminal=state(model),
        checkpoint='Actual ordinary-input Main-return state, cloned without gameplay writes',
        cases=cases,gameplay_seeds=0,outputs=0,Mesen=False,scope='Source input component; native cadence separate')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--edges',default='880,888,892,896');parser.add_argument('--jump',action='store_true');parser.add_argument('--trace-queries',action='store_true');parser.add_argument('--third-cap',action='store_true');args=parser.parse_args()
    current=Current.load(Game.Factory.ROM)
    q=run(current.reference1daca,edges=tuple(map(int,args.edges.split(','))),jump=args.jump,trace_queries=args.trace_queries,third_cap=args.third_cap)
    q['public_input']=current.metadata()
    digest=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    q['prefix'].pop('events',None)
    for case in q['cases']:case['trace']=case['trace'][::2]
    q['full_receipt_SHA256']=digest
    print(json.dumps(q,separators=(',',':')),flush=True)
