"""Explicit source-only stair primitives; isolate reset without native BG."""
from hashlib import sha256
import json

import check_dkjr_final_stair_branches_1113 as B


def main():
    parent,raw=B.T.load_inputs();e73=B.T.Old.reverse(parent)
    _,seed=B.H.cold(e73,e73[B.P.B.COOKIE_AT:B.P.B.COOKIE_AT+16])
    seed=B.Q.mounted(seed,raw);labels=B.P.frozen_labels()
    phase,publish,land=(labels[n]for n in('DkjrNativeSourcePhase','DkjrNativePublishAnchor','DkjrLand'))
    rows=[]
    for name,x,facing in(('late-right',2974,1),('early-right',2964,1),('early-backward-right',2964,0)):
        m=B.L.clone(seed)
        B.N.put(m,SelectedCharacter=40,GameEngineSubroutine=8,TimerControl=0,
            Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=80,Player_Y_HighPos=1,
            ScreenLeft_X_Pos=80,ScreenLeft_PageLoc=11)
        for slot in range(6):m[B.W.address(m.bundle,'Enemy_Flag')+slot]=0
        for name_buffer in('Block_Buffer_1','Block_Buffer_2'):
            start=B.W.address(m.bundle,name_buffer);m[start:start+208]=bytes(208)
        attr=B.W.location(m.bundle,'MTileAttribute')
        assert raw[attr+0x61]&3==1
        for world_x,top in((2960,128),(2976,112),(2992,96),(3008,80)):
            buffer=B.W.address(m.bundle,'Block_Buffer_2'if(world_x>>8)&1 else'Block_Buffer_1')
            for y in range(top,224,16):m[buffer+((y-32)&240)+((world_x>>4)&15)]=0x61
        fields={0x49:0,0x4a:1,0x54:4,0x55:4,0x56:0,0x63:0,0x68:0,
            0x6b:1,0x6c:1,0x6d:facing,0x6f:0,0x70:0,0x71:0,0x75:0,
            0x76:95,0x78:4,0x7a:2,0x7b:24,0x7c:160,0x7e:0,
            0x7f:0,0x82:0,0x83:0,0x86:96,0x87:1,0x88:96,
            0x8a:0,0x8b:0,0x8c:0,0x210:95,0x213:x-2896-8,0x591:0,0x8da:1}
        for at,value in fields.items():m.ram[2][at]=value
        timeline=[];events=[];all_native_pcs=[]
        for tick in range(36):
            m.ram[2][0x14]=129 if tick<8 else 1
            m.ram[2][0x15]=129 if tick==0 else 1
            previous=None
            def observe(mem,c):
                nonlocal previous
                current=tuple(mem.ram[2][at]for at in(0x6b,0x210,0x213))
                if previous is not None and(current[0]!=previous['values'][0]or tick<5 and current[1]!=previous['values'][1]):
                    events.append(dict(tick=tick,writer_PC=previous['pc'],
                        opcode=previous['opcode'],before=previous['values'],after=current))
                if not(0xa000<=c.pc<0xc000 and mem.rawtags[1]==3):all_native_pcs.append((tick,c.pc,mem.rawtags[1]))
                if c.pc==land:
                    events.append(dict(tick=tick,event='original-Land',source_y=mem.ram[2][0x210],
                        rect=list(mem.ram[2][0x3e:0x46])))
                previous=dict(pc=c.pc,values=current,opcode=bytes(mem[c.pc:c.pc+3]).hex())
            B.H.call(m,phase,observe=observe)
            B.H.call(m,publish)
            state=B.state(m)
            if tick<8 or tick==35 or not timeline or state['source_state']!=timeline[-1]['source']:
                timeline.append(dict(tick=tick,x=state['x'],y=state['y'],
                    source=state['source_state'],prior=state['prior'],age=state['jump_age'],
                    source_y=state['source_y'],source_x=state['source_x'],
                    recoil_direction=m.ram[2][0x78],rect=state['source_rect']))
        rows.append(dict(name=name,start_native_x=x,start_facing=facing,timeline=timeline,
            source_field_writers=events,native_program_cuts=all_native_pcs[:8]))
        print('DKJR_STAIR_RESET_UNIT '+json.dumps(rows[-1],separators=(',',':')),flush=True)
    print('DKJR_STAIR_RESET_UNIT_SCOPE '+json.dumps(dict(candidate_SHA256=sha256(raw).hexdigest(),
        unit_field_and_tile_seeds=True,ROM_written=False,native_BG_or_ground_projection_executed=False,
        fixture_cells='61:2960/top128,2976/top112,2992/top96,3008/top80; lower rows solid',
        outputs_written=0,scope='Counterfactual compiled-source primitive fixtures, not a genuine Main/route/cadence proof.'),separators=(',',':')),flush=True)
    assert all(not row['native_program_cuts']for row in rows)
    assert rows[0]['timeline'][2]['source']==4 and rows[0]['timeline'][4]['source']==1
    assert rows[0]['timeline'][2]['age']==rows[0]['timeline'][4]['age']==2
    assert rows[1]['timeline'][-1]['y']==80
    assert rows[2]['timeline'][-1]['source']==1 and rows[2]['timeline'][-1]['y']==64


if __name__=='__main__':main()
