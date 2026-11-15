"""Genuine classic DK current full-route source CPU qualification."""
import argparse
from collections import deque
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import replay_dk_full11_current_1114 as Factory
import check_smb1_alts_full11_1114 as Runner
import check_shared_world_sprite_images_1114 as Cold


def cold(raw,key='donkey_kong'):
    with patch.object(Cold,'Factory',Factory):return Cold.cold(raw,key)


def run(raw,*,metadata=False):
    with patch.object(Runner,'Factory',Factory),patch.object(Runner,'cold',cold):
        return Runner.strict_metadata(raw,'donkey_kong')if metadata else Runner.run(raw,'donkey_kong',9000)


def contact(raw):
    """Passive source observer: exact frozen controller and ordinary cold."""
    N,W=Factory.N,Factory.W;original_cpu=N.NesMPU
    ctx=dict(arena=None,main=0,cpu=None,pc=-1,points={},injury=None,death=None)
    recent=deque(maxlen=24);heads=deque(maxlen=8)
    def view(m):
        fields=('Player_Y_Position','Player_Y_HighPos','Player_State','Player_X_Speed','Player_Y_Speed',
            'Player_Y_MoveForce','Player_YMoveForceFractional','A_B_Buttons','PreviousA_B_Buttons',
            'SavedJoypadBits','PlayerStatus','PlayerSize','DkTier','DkAttack','DkAge','GameEngineSubroutine',
            'NumberofLives','ObjectOffset','Player_CollisionBits')
        return dict(Main=ctx['main'],x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            pad=m.controller_pad,**{n:N.get(m,n)for n in fields})
    def actors(m):
        return [dict(slot=i,flag=N.get(m,'Enemy_Flag',i),id=N.get(m,'Enemy_ID',i),state=N.get(m,'Enemy_State',i),
            x=N.get(m,'Enemy_X_Position',i)+256*N.get(m,'Enemy_PageLoc',i),y=N.get(m,'Enemy_Y_Position',i),
            high=N.get(m,'Enemy_Y_HighPos',i))for i in range(6)if N.get(m,'Enemy_Flag',i)]
    def causal(m,c,name):
        box=W.address(m.bundle,'BoundingBox_UL_Corner');enemy=W.address(m.bundle,'EnemyBoundingBoxCoord')
        return dict(event=name,PC=ctx['pc'],bank=m.rawtags[(ctx['pc']-0x8000)//8192],
            X=c.x,Y=c.y,A=c.a,P=c.p,SP=c.sp,**view(m),actors=actors(m),
            actual_player_box=list(m[box:box+4]),actual_enemy_boxes=[list(m[enemy+4*i:enemy+4*i+4])for i in range(6)],
            camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc'),
            recent_completed_Main=list(recent),recent_native_head_bumps=list(heads))
    class CPU(original_cpu):
        def step(self):
            m=self.memory
            if m is ctx['arena']:
                ctx['cpu']=self;ctx['pc']=self.pc
                bank=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                name=ctx['points'].get((bank,self.pc))
                if name=='GameLoop':ctx['main']+=1
                elif name and name.startswith('GameLoopReturn'):
                    recent.append(dict(**view(m),actors=actors(m)))
                elif name=='BumpBlock':
                    heads.append(dict(PC=self.pc,bank=bank,**view(m),
                        scratch={n:N.get(m,n)for n in('R2','R3','R4','R5','R6','R7')}))
                elif name=='InjurePlayer'and ctx['injury']is None:
                    ctx['injury']=causal(m,self,name)
                    print('DK_FIRST_INJURY '+json.dumps(ctx['injury'],separators=(',',':')),flush=True)
                elif name=='DkHostDeathStart'and ctx['death']is None:
                    ctx['death']=causal(m,self,name)
            return super().step()
    def retained_cold(image,key):
        m=cold(image,key);ctx['arena']=m
        names=('GameLoop','GameLoopReturn0','GameLoopReturn1','InjurePlayer','DkHostDeathStart','BumpBlock')
        for name in names:
            if name.startswith('GameLoopReturn'):
                h=Factory.bindings(image,key)['hooks'][name];at=16+h['offset'];pc=h['pc']
            else:at=W.location(m.bundle,name);pc=W.address(m.bundle,name)
            ctx['points'][(((at-16)//8192)|128,pc)]=name
        return m
    with patch.object(N,'NesMPU',CPU),patch.object(Runner,'Factory',Factory),patch.object(Runner,'cold',retained_cold):
        q=Runner.run(raw,'donkey_kong',9000)
    summary=dict(injury=ctx['injury'],death=ctx['death'],last_completed_Main=list(recent)[-8:],recent_native_head_bumps=list(heads),
        exact_frozen_controller_SHA256=sha256(Factory.controller(raw).encode()).hexdigest(),
        controls_and_game_bytes_unchanged=True,outputs=0)
    q['passive_contact']=summary
    return q


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true');p.add_argument('--contact',action='store_true');a=p.parse_args()
    raw=Factory.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('DK source route attempted files/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Runner.Native,'run',forbid):
        q=contact(raw)if a.contact else run(raw,metadata=a.metadata)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not a.metadata:assert q['passed'],'Classic DK full source route remains unqualified'
