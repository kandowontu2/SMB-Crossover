"""Actual current native wall and source ground-order contracts, no route."""
from collections import Counter
from hashlib import sha256
import json
import re
from unittest.mock import patch

import compose_dkjr_footer_bt91dc_current_1116 as C
import check_dkjr_carry_camera_route_1116 as Route
import check_dkjr_footer_ryu_1116 as Support
import check_dkjr_stair_query_contract_1116 as Query

N,W,L=Support.N,Support.W,Support.L
H=lambda value:sha256(value).hexdigest()


def main():
    parent=C.BT.ROM.read_bytes();raw,composition=C.proposal(parent);assert C.inverse(raw)==parent
    whole,base_labels=C.Camera.Plan.source_inputs();proof,labels=Query.Source.closure(raw)
    body=C.Camera.payload(raw)
    fragments=[]
    for begin,end in(('D_d412','D_d56e'),('D_d56e','D_d58c'),('D_d681','D_d6b9'),('D_d6b9','D_d6f5')):
        source=whole[whole.index(begin+':'):whole.index(end+':')]
        defined=set(re.findall(r'^(\w+):',source,re.M))
        prefix=C.Camera.Plan.numeric(whole)+''.join(f'{n}=${v:x}\n'for n,v in labels.items()if n not in defined)
        pc=labels[begin];endpc=labels[end]
        linked=C.Footer.Plan.Funding.H.T.assemble(prefix+'.segment "CHECK"\n'+C.Camera.Plan.Source.expand_branches(source),dict(CHECK=(pc,endpc-pc)))
        code=linked['images']['CHECK'];at=Query.Source.H.T.offset(pc)
        assert code==body[at:at+len(code)]
        fragments.append(dict(first=begin,end=end,PC=pc,bytes=len(code),SHA256=H(code)))
    ground=whole[whole.index('D_d56e:'):whole.index('D_d58c:')]
    assert ground.index('jsr D_e89f')<ground.index('sta $c06b')<ground.index('D_d585:')<ground.index('jsr D_d681')
    move=whole[whole.index('D_d681:'):whole.index('D_d6b9:')]
    assert move.index('jsr D_d6b9')<move.index('jsr D_e9ee')
    shape=Query.contract(raw)['shape_records']
    opening,seed=Route.cold(raw);native=[];watched={}
    names=('PlayerCtrlRoutine','PlayerMovementSubs','MegaManCollisionAdder','CrossoverSourceSideProbe',
        'BlockBufferColli_Side','BlockBufferCollision','StopPlayerMove','SamusStopAtWall',
        'SamusStopAtWallBanked','CrossoverSourceWallDispatch','LmWallGate','Z2WallLegacy',
        'ImpedePlayerMove','GuestFootContactSide','HuAdder','HuSide')
    for name in names:
        at=W.location(seed.bundle,name);pc=W.address(seed.bundle,name);bank=((at-16)//8192)|128
        native.append(dict(name=name,PC=pc,bank=bank,file_offset=at,preimage16=raw[at:at+16].hex()))
        watched.setdefault((bank,pc),[]).append(name)
    caller_at=W.location(seed.bundle,'PlayerCtrlRoutine');caller_pc=W.address(seed.bundle,'PlayerCtrlRoutine')
    caller=raw[caller_at:caller_at+512];order=[]
    for name in('PlayerMovementSubs','VvScrollBridge','RelativePlayerPosition','RdNativeBGGate'):
        pc=W.address(seed.bundle,name);needle=bytes((0x20,pc&255,pc>>8))
        hits=[i for i in range(len(caller)-2)if caller[i:i+3]==needle]
        assert len(hits)==1,(name,hits)
        order.append(dict(name=name,caller_PC=caller_pc+hits[0],file_offset=caller_at+hits[0],target_PC=pc))
    assert [r['file_offset']for r in order]==sorted(r['file_offset']for r in order)
    between=raw[order[2]['file_offset']+3:order[3]['file_offset']]
    assert between==bytes.fromhex('a200')
    gate_at=W.location(seed.bundle,'RdNativeBGGate')
    gate_preimage=raw[gate_at:gate_at+13]
    assert gate_preimage==bytes.fromhex('a9a78d6c01a9af8d6d01a9dd4c')
    # Actual resident fusion differs from the retained source's direct JSRs.
    # Exercise that existing public gate after one actual owning movement;
    # this is an explicitly declared component, not a natural stair contact.
    bg=L.clone(seed);N.invoke(bg,'HuMovement',a=0,x=0,y=0,p=0x31)
    phase=[];Base=N.NesMPU
    bg_tag=((W.location(bg.bundle,'PlayerBGCollision')-16)//8192)|128
    bg_pc=W.address(bg.bundle,'PlayerBGCollision')
    class GateCPU(Base):
        def step(self):
            tag=bg.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if(tag,self.pc)==(2,labels['DkFullBox']):phase.append('actual_DK_full_box')
            if(tag,self.pc)==(bg_tag,bg_pc):phase.append('actual_native_BG')
            return super().step()
    with patch.object(N,'NesMPU',GateCPU):bg_result=N.invoke(bg,'RdNativeBGGate',a=40,x=0,y=0,p=0x31)
    assert phase==['actual_DK_full_box','actual_native_BG'],('Current fused native BG gate order',phase)
    entries=Counter();rows=[]
    for x in(2127,2128,2129,2130,2143):
        m=L.clone(seed);N.put(m,SelectedCharacter=40,GameEngineSubroutine=8,Player_X_Position=x&255,
            Player_PageLoc=x>>8,Player_Y_Position=160,Player_Y_HighPos=1,Player_State=0,
            Player_X_Speed=16,Player_CollisionBits=255,GuestHurtTicks=0)
        m[3]=1;seen=[];stores=[];Base=N.NesMPU
        class CPU(Base):
            def step(self):
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                for name in watched.get((tag,self.pc),[]):
                    entries[name]+=1
                    if not seen or seen[-1]!=name:seen.append(name)
                if bytes(m[self.pc:self.pc+2])==bytes((0x85,0x75)):
                    stores.append(dict(PC=self.pc,bank=tag,SP=self.sp,A=self.a,P=self.p,
                        preceding12=bytes(m[self.pc-12:self.pc]).hex()))
                return super().step()
        with patch.object(N,'NesMPU',CPU):result=N.invoke(m,'StopPlayerMove',a=97,x=0,y=1,p=0x31)
        rows.append(dict(input_worldX=x,R0=1,output_worldX=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            output_speed=N.get(m,'Player_X_Speed'),side_timer=N.get(m,'SideCollisionTimer'),
            path=seen,actual_nativeX_stores=stores,result=result))
    m=L.clone(seed);adder=N.invoke(m,'HuAdder',a=40,x=0,y=85,p=0x31)
    assert adder['Y']==2 and adder['P']&1
    table=W.location(seed.bundle,'BlockBufferAdderData');index=raw[table+2]
    dx=W.location(seed.bundle,'BlockBuffer_X_Adder');dy=W.location(seed.bundle,'BlockBuffer_Y_Adder')
    profile=dict(index=index,x_adders=list(raw[dx+index:dx+index+7]),y_adders=list(raw[dy+index:dy+index+7]))
    side=[]
    for offset in range(3,7):
        m=L.clone(seed);calls=Counter();Base=N.NesMPU
        side_pc=W.address(m.bundle,'BlockBufferColli_Side')
        side_tag=((W.location(m.bundle,'BlockBufferColli_Side')-16)//8192)|128
        class SideCPU(Base):
            def step(self):
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                if(tag,self.pc)==(side_tag,side_pc):calls['actual_native_side_leaf']+=1
                return super().step()
        with patch.object(N,'NesMPU',SideCPU):r=N.invoke(m,'CrossoverSourceSideProbe',a=1,x=0,y=index+offset,p=0x31)
        assert calls['actual_native_side_leaf']==1 and r['A']==m[6]
        side.append(dict(index=index+offset,x_offset=profile['x_adders'][offset],y_offset=profile['y_adders'][offset],
            actual_leaf_calls=dict(calls),returned_A=r['A'],raw_tile_R3=m[6],query_X_low=m[8],query_row=m[5]))
    report=dict(passed=True,composition=composition,actual_CPU_ROM_SHA256=H(raw),opening=opening,
        source_fragments=fragments,shape_records=shape,native_entries=native,
        actual_PlayerCtrl_call_order=order,between_relative_and_fused_gate=between.hex(),
        fused_BG_gate_preimage=gate_preimage.hex(),declared_fused_gate_component=dict(order=phase,result=bg_result),
        actual_HuAdder_result=adder,actual_native_profile=profile,declared_native_side_query_components=side,
        declared_right_contact_components=rows,actual_component_path_counts=dict(entries),
        original_ground_order='Move first builds bounds for the current phase. Ground then queries vine and support BEFORE D_d681/GroundMove. A support miss writes phase4 and returns without advancing horizontal X. On a support hit, D_da14 then D_d681 computes horizontal origin and publishes pose through D_e9ee.',
        scope='Actual current code, genuine compiled cold only, and explicitly declared wall-contact component inputs. No natural stair/side contact, terrain mutation, controller route, new code mount, native run or game repair claimed.',
        outputs=0)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_STATIC_ORDER '+encoded,flush=True);print('DKJR_STATIC_ORDER_SHA256 '+H(encoded.encode()),flush=True)


if __name__=='__main__':main()
