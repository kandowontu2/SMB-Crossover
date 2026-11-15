"""Passive exact-bb51 source roof/collision observer; no changed controls."""
from collections import deque
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import check_dk_full11_latched_current_1114 as Common
import replay_dk_full11_all_latched_current_1114 as Factory


def run(raw):
    N,W=Factory.N,Factory.W;base=N.NesMPU;old_cold=Common.Cold.cold
    ctx=dict(arena=None,main=0,points={},terrain=None,prior=None)
    rows=[];events=[];heads=deque(maxlen=8)
    def row(m):
        names=('Player_Y_Position','Player_Y_HighPos','Player_State','Player_X_Speed','Player_Y_Speed',
            'Player_Y_MoveForce','Player_YMoveForceFractional','SavedJoypadBits','A_B_Buttons',
            'PreviousA_B_Buttons','DkPrevious','Player_CollisionBits','GameEngineSubroutine')
        return dict(Main=ctx['main'],x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            pad=m.controller_pad,**{n:N.get(m,n)for n in names})
    def geometry(m):
        block=W.address(m.bundle,'Block_Buffer_1');attrs=W.location(m.bundle,'MTileAttribute')
        out=[]
        for x in range(1440,1761,16):
            for y in range(48,209,16):
                at=block+(x//256%2)*208+((y-32)//16)*16+(x%256//16)
                tile=m[at]
                if tile and tile!=0x23:out.append([x,y,tile,raw[attrs+tile]])
        return out
    def actors(m):
        return [dict(slot=i,flag=N.get(m,'Enemy_Flag',i),id=N.get(m,'Enemy_ID',i),state=N.get(m,'Enemy_State',i),
            x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),
            y=N.get(m,'Enemy_Y_Position',i))for i in range(6)if N.get(m,'Enemy_Flag',i)]
    class CPU(base):
        def step(self):
            m=self.memory
            if m is ctx['arena']:
                bank=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                name=ctx['points'].get((bank,self.pc))
                if name=='GameLoop':ctx['main']+=1
                elif name and name.startswith('GameLoopReturn'):
                    r=row(m)
                    if 1480<=r['x']<=1750:
                        r['actors']=actors(m);prior=ctx['prior']
                        if ctx['terrain']is None and r['Player_State']==0 and r['Player_Y_Position']<=112:
                            ctx['terrain']=geometry(m)
                        rows.append(r)
                        if len(rows)>32:del rows[16]
                        if prior is None or r['Player_State']!=prior['Player_State']or(
                            r['Player_State']==1 and r['Player_Y_Speed']>=128 and prior['Player_Y_Speed']<128):
                            events.append(r)
                            if len(events)>24:del events[12]
                        ctx['prior']=r
                elif name=='BumpBlock'and 1408<=row(m)['x']<=1750:
                    heads.append(dict(**row(m),PC=self.pc,bank=bank,
                        scratch={n:N.get(m,n)for n in('R2','R3','R4','R5','R6','R7')}))
                elif name=='InjurePlayer'and len(events)<25:
                    box=W.address(m.bundle,'BoundingBox_UL_Corner');enemy=W.address(m.bundle,'EnemyBoundingBoxCoord')
                    events.append(dict(**row(m),event=name,actors=actors(m),
                        actual_player_box=list(m[box:box+4]),
                        actual_enemy_boxes=[list(m[enemy+4*i:enemy+4*i+4])for i in range(6)]))
            return super().step()
    def cold(image,key):
        m=old_cold(image,key);ctx['arena']=m
        for name in('GameLoop','GameLoopReturn0','GameLoopReturn1','BumpBlock','InjurePlayer'):
            if name.startswith('GameLoopReturn'):
                h=Factory.bindings(image,key)['hooks'][name];at=16+h['offset'];pc=h['pc']
            else:at=W.location(m.bundle,name);pc=W.address(m.bundle,name)
            ctx['points'][(((at-16)//8192)|128,pc)]=name
        return m
    with patch.object(N,'NesMPU',CPU),patch.object(Common.Cold,'cold',cold),patch.object(Common,'Factory',Factory):
        q=Common.run(raw,delayed_polls=True)
    q['passive_roof_geometry']=dict(trajectory=rows,transitions_and_first_injury=events,
        native_head_bumps=list(heads),actual_first_supported_roof_nonempty_cells=ctx['terrain'],
        selected_controller_SHA256=sha256(Factory.controller(raw).encode()).hexdigest(),
        unchanged_selected_controls=True,gameplay_seeds=0,outputs=0)
    return q


if __name__=='__main__':
    raw=Factory.ROM.read_bytes()
    def forbid(*a,**kw):raise RuntimeError('Passive DK source observer attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Common.Runner.Native,'run',forbid):
        q=run(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
