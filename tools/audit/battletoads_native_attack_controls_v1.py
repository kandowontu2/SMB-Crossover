"""Genuine controller B edge -> original E2 -> native immunity/defeat consumer."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_native_adapter_controls_v1 as T
O=R/'build/battletoads-native-adapter-v10';J=O/'joint'

def main():
    out=O/'attack-controls.json';assert not out.exists()
    q=dict(passed=False,native=False,rows=[])
    try:
        b=T.H.C.qualified(J/'candidate.nes')
        scenarios=['goomba','buzzy','bowser','podoboo','bullet','behind','near7','far','high','low','hidden','defeated','unused']
        for player,variant,face,script,case in itertools.product(range(2),range(2),[1,2],[0,2],scenarios):
            m=T.seed(b,player,variant)
            T.H.put(m,DisableScreenFlag=0,NmiDisable=0,Mirror_PPUMASK=30,Player_Rel_XPos=120,
                PlayerFacingDir=face,ObjectOffset=0,BowserHitPoints=5,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0)
            T.put(m,'BtSrc_RandomValue_1',script,player)
            for i in range(6):m[T.address(b,'Enemy_Flag')+i]=0
            kind={'buzzy':2,'bowser':45,'podoboo':12,'bullet':8}.get(case,6)
            x=140 if face==1 else 110
            if case=='behind':x=110 if face==1 else 140
            if case=='near7':x=115 if face==1 else 125
            if case=='far':x=180 if face==1 else 70
            bottom=150 if case=='high'else 206 if case=='low'else 192
            T.H.put(m,Enemy_Flag=0 if case=='unused'else 1,Enemy_ID=kind,
                Enemy_State=32 if case=='defeated'else 0,Enemy_Y_HighPos=1,Enemy_Y_Position=bottom-24,
                Enemy_X_Position=x,Enemy_PageLoc=0,EnemyOffscrBitsMasked=255 if case=='hidden'else 0)
            at=T.address(b,'BoundingBox_UL_Corner');m[at+4]=x;m[at+5]=bottom-24;m[at+6]=x+12;m[at+7]=bottom
            # Real controller input supplies direction plus a fresh B edge.
            T.H.put(m,SavedJoypadBits=64|face)
            sourcehits=[]
            def observe_source(mm,c,step):
                if c.pc==T.address(b,'BtHostHit')and mm.rawtags[1]==3:sourcehits.append(c.pc)
            c=T.H.start(m,'BtServiceVeneers');c,_=T.H.finish(m,c,observe_source)
            assert len(sourcehits)==1 and T.get(m,'BtPunchPending')==1 and T.get(m,'BtPunchEvents')==1
            assert T.get(m,'BtSrc_Objects_AnimID',player)==2+script
            hits=[];before=bytes(list.__getitem__(m,slice(3,11)))
            for service in[4,34]:
                c=T.H.start(m,'BtServiceVeneers',p=T.L.flags((player*32+variant*16+script*4+face)&63))
                pc=T.address(b,'BtServiceVeneers')+service*3
                m[T.address(b,'FarcallJmpTarget_SMC')+1]=pc&255;m[T.address(b,'FarcallJmpTarget_SMC')+2]=pc>>8
                def observe_native(mm,c,step):
                    if c.pc==T.address(b,'HandleEnemyFBallCol'):hits.append([c.x,T.H.get(mm,'R1')])
                c,low=T.H.finish(m,c,observe_native)
                assert(c.a,c.x,c.y,c.sp)==(85,7,91,224)
                assert bytes(list.__getitem__(m,slice(3,11)))==before
            expected=case in['goomba','buzzy','bowser','podoboo','bullet','near7']
            assert len(hits)==int(expected),(player,variant,face,script,case,hits)
            assert T.get(m,'BtPunchPending')==0 and T.get(m,'BtPendingHitsConsumed')==1
            state=T.H.get(m,'Enemy_State');hp=T.H.get(m,'BowserHitPoints')
            if case in['goomba','near7']:assert state&32
            elif case=='bowser':assert hp==4 and state==0
            elif case in['buzzy','podoboo','bullet']:assert state==0 and hp==5
            else:assert state==(32 if case=='defeated'else 0)and hp==5
            q['rows'].append(dict(player=player,variant=variant,face=face,original_script=2+script,case=case,
                real_source_E2=len(sourcehits),native_callback_count=len(hits),state=state,BowserHP=hp,
                genuine_source_event_consumed_once_across_both_weapon_hooks=True))
        q.update(passed=True,pairs=len(q['rows']),scope='Original source fresh B event, two real punch scripts and native current bounding-box/defeat/immunity/Bowser HP. Explicit enemy contact fixtures; not natural Main/cold/native route qualification.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):T.L.sha(p)for p in[Path(__file__),Path(T.__file__),J/'candidate.nes',J/'candidate.dbg',J/'bt/api.s',J/'bt/core.s',J/'bt/cache.bin',J/'bt/cookie.bin',O/'boundary-controls.json']}
    out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['rows','bindings','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
