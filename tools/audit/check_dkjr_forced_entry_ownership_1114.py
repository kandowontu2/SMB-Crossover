"""Declared real-native entrance lifecycle; optional CPU-only ownership arm.

The diagnostic arm redirects a pending first anchor to its existing reject
path while native Player_State is airborne. No instruction or ROM is edited.
This is not a source fix, route qualification or native emulator evidence.
"""
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import compose_dkjr_oneway_current_1114 as Current
import check_dkjr_platform_query_lifecycle_1114 as Life

S=Current.S;F=S.Replay;G=F.Gate
Q,P,H,N,W,L=G.Q,G.P,G.H,G.N,G.W,G.L


def view(m):
    r=m.ram[2]
    return dict(x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
        y=N.get(m,'Player_Y_Position'),high=N.get(m,'Player_Y_HighPos'),
        native_state=N.get(m,'Player_State'),engine=N.get(m,'GameEngineSubroutine'),
        source=r[0x6b],prior=r[0x6c],source_y=r[0x210],origin=r[0x76],
        limit=r[0x7b],ready=r[0x8fe],lives=N.get(m,'NumberofLives'))


def main():
    parent=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes()
    raw,private,_=Current.source_projection(parent,kind='hidden-421')
    _,old=F.load_inputs();_,labels=Life.closure(old)
    _,seed=H.cold(raw,raw[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    results=[]
    for entrance in (1,2):
      for arm in ('current','defer-only','defer-native-vertical'):
        defer=arm!='current'
        m=Q.mounted(seed,raw)
        for slot in range(6):N.invoke(m,'EraseEnemyObject',x=slot)
        N.put(m,SelectedCharacter=40,OperMode=1,OperMode_Task=3,
            ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,
            WorldNumber=0,LevelNumber=1 if entrance==1 else 0,AreaNumber=2 if entrance==1 else 0,
            AreaType=1,AreaPointer=0xc2 if entrance==1 else 0x25,
            PlayerEntranceCtrl=entrance,AltEntranceControl=0,JoypadOverride=0,
            TimerControl=0,GameTimerSetting=0,SwimmingFlag=0,
            Player_X_Speed=0,Player_X_MoveForce=0,Player_X_Scroll=0,
            Player_Y_Speed=0,Player_Y_MoveForce=0,GameEngineSubroutine=7,
            SavedJoypadBits=0,SavedJoypad1Bits=0,FamilyMainCommit=1,NmiDisable=255)
        # One declared ordinary native floor, not a copied/seeded endpoint.
        for name in ('Block_Buffer_1','Block_Buffer_2'):
            at=W.address(m.bundle,name);m[at:at+208]=bytes(208)
            m[at+176:at+208]=bytes((0x54,))*32
        N.invoke(m,'HuFresh')
        N.invoke(m,'Entrance_GameTimerSetup')
        initial=view(m);rows=[];redirects=[];first_anchor=None;first_injury=None;grounded=0
        assert initial['y']==(32 if entrance==1 else 176)and initial['engine']==7
        vertical_calls=0
        base=N.NesMPU
        class Probe(base):
          def step(self):
            nonlocal first_anchor,first_injury
            memory=self.memory
            tag=memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1
            if (tag,self.pc)==(3,labels['DkNativeAnchorReady']) and memory.ram[2][0x8fe]==1:
                s=view(memory)
                if s['engine']==8 and first_anchor is None:first_anchor=s
                if defer and s['engine']==8 and s['native_state']!=0:
                    if len(redirects)<4:redirects.append(s)
                    self.pc=labels['DkAnchorNo']
            if tag==3 and bytes(memory[self.pc:self.pc+3])==bytes.fromhex('8d6bc0') and self.a==5 and first_injury is None:
                first_injury=dict(PC=self.pc,before=view(memory))
            return base.step(self)
        with patch.object(N,'NesMPU',Probe):
            for tick in range(240):
                if arm=='defer-native-vertical'and m.ram[2][0x8fe]==1 and N.get(m,'GameEngineSubroutine')==8 and N.get(m,'Player_State')!=0:
                    N.invoke(m,'MovePlayerVertically',x=0);vertical_calls+=1
                Q.frame(m,0)
                s=view(m)
                if len(rows)<8 or tick%16==0 or s['source']==5:rows.append(dict(update=tick+1,**s))
                healthy=s['engine']==8 and s['native_state']==0 and s['y']==176 and s['high']==1 and s['source']==s['prior']==1 and s['source_y']==191 and s['lives']==2
                grounded=grounded+1 if healthy else 0
                if s['source']==5 or grounded>=25:break
        if entrance==1 and arm=='current':assert first_injury and first_injury['PC']==labels['D_da31']and m.ram[2][0x76]==63
        elif entrance==1 and arm=='defer-only':assert tick==239 and m.ram[2][0x8fe]==1 and N.get(m,'Player_Y_Position')==48 and first_injury is None
        else:assert grounded>=25 and first_injury is None
        results.append(dict(entrance_control=entrance,diagnostic_arm=arm,
            deferred_pending_airborne_owner=defer,declared_extra_native_vertical_calls=vertical_calls,
            native_setup_initial=initial,first_engine8_pending_anchor=first_anchor,
            first_diagnostic_redirect=redirects[0]if redirects else None,first_injury=first_injury,
            updates=tick+1,consecutive_grounded_updates=grounded,
            bounded_trajectory=rows[:2]+rows[-2:],final=view(m)))
    print('DKJR_FORCED_ENTRY_OWNERSHIP '+json.dumps(dict(passed=True,ROM_SHA256=Current.PIN,
        existing_private_SHA256=S.PIN,declared_component_only=True,results=results,
        outputs_written=0,ROM_written=False,source_code_changed=False,native_claim=False,
        scope='Real current Entrance_GameTimerSetup and complete scheduled native Main on a declared flat floor; CPU-PC redirection is an explicit ownership counterfactual, not a repair or route qualification.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
