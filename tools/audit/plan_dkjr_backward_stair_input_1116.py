"""Detached original-ability proof: Left facing plus fresh Right+A, no patch."""
from hashlib import sha256
import json
import re

import compose_dkjr_footer_bt91dc_current_1116 as C
import check_dkjr_stair_query_contract_1116 as Query
import check_dkjr_carry_camera_route_1116 as R

N,H=R.N,lambda value:sha256(value).hexdigest()


def detached(raw):
    assert H(raw)==C.CANDIDATE
    whole,labels=C.Camera.Plan.source_inputs();proof,complete=Query.Source.closure(raw)
    body=C.Camera.payload(raw)
    records={}
    for name,expected in(('DData_c379',[7,0,24,15]),('DData_c389',[9,0,25,15]),('DData_c38d',[5,0,24,15])):
        pc=complete[name];at=Query.Source.H.T.offset(pc);assert list(body[at:at+4])==expected
        records[name]=dict(PC=pc,bytes=expected)
    pointers={}
    for name,target in(('DData_c369','DData_c379'),('DData_c36b','DData_c379'),('DData_c371','DData_c389'),('DData_c373','DData_c38d')):
        at=Query.Source.H.T.offset(complete[name]);value=int.from_bytes(body[at:at+2],'little')
        assert value==complete[target];pointers[name]=dict(PC=complete[name],target=target,target_PC=value)
    # Ground-left sets the original facing; rightward jump reads direction
    # independently and never writes that facing byte.
    left=whole[whole.index('D_d6d7:'):whole.index('D_d6f5:')]
    assert 'lda #$00\n'in left and 'sta $c06d\n'in left
    jump=whole[whole.index('D_d913:'):whole.index('D_d955:')]
    assert 'ldx $c054'in jump and 'cpx #$03'in jump and 'adc $c000'in jump
    assert 'sta $c06d'not in jump and re.search(r'lda \$c06d\s+[^\n]*\n eor #\$01',jump)
    input_code=whole[whole.index('D_ce6c:'):whole.index('D_cea2:')]
    assert 'sty $c054'in input_code and 'sta $c06b'in input_code and 'sta $c06d'not in input_code
    transition=whole[whole.index('D_d291:'):whole.index('D_d2a4:')]
    assert 'sta $c07e'in transition and 'sta $c06d'not in transition
    phase=whole[whole.index('DkjrNativeSourcePhase:'):whole.index('DkjrNativePhaseEnd:')]
    assert phase.index('jsr DkjrInput')<phase.index('jsr DkjrTransition')<phase.index('jsr DkjrMove')
    opening,m=R.cold(raw);rows=[]
    for name,pad in(('anchor',0),('acknowledged-Right',1),('acknowledged-Left',2),('neutral',0),('fresh-Right-A',129),('continued-Right-A',129)):
        N.put(m,SavedJoypadBits=pad)
        result=N.invoke(m,'HuMovement',a=0,x=0,y=0,p=0x31)
        N.invoke(m,'HuFullBox',a=40,x=0,y=0,p=0x31)
        r=m.ram[2]
        rows.append(dict(step=name,pad=pad,source=r[0x6b],facing=r[0x6d],direction=r[0x54],
            special_pose=r[0x71],sourceX=r[0x213],sourceY=r[0x210],age=r[0x7e],
            held=r[0x14],fresh=r[0x15],box=list(m[0x658:0x65c]),
            nativeX=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),movement_C=result['P']&1))
    assert rows[1]['source']==1 and rows[1]['facing']==1
    assert all(r['source']==1 and r['facing']==0 for r in rows[2:4])
    assert all(r['source']==3 and r['direction']==4 and r['facing']==0 and r['special_pose']!=2 for r in rows[4:])
    assert rows[4]['fresh']&128 and not rows[5]['fresh']&128
    assert all(r['box'][2]==r['sourceX']+24 for r in rows[4:])
    return dict(passed=True,actual_CPU_ROM_SHA256=H(raw),actual_compiled_cold=opening,
        left_facing_value=0,right_facing_value=1,ground_pointer_pairs=pointers,records=records,
        source_byte_exact_fragment_receipts=[r for r in proof['assembled_exact_current_fragments']if r['first']in('D_ce6c','D_d251','D_d913','DkjrNativeSourcePhase')],
        declared_ordinary_input_components=rows,
        conclusion='Obtain actual grounded C06D=0, release A, then fresh Right+A together. Original direction4 advances right while retaining facing0; its jump right edge equals ground right edge, eliminating the demonstrated one-pixel pose retraction without changing code or geometry.',
        limits='Public-callback input components at real opening floor; no natural stair traversal or native qualification. Root must exercise its separately frozen ordinary controller on the real prefix. Special pose C071=2 is outside this ordinary-table contract.',
        new_game_code_bytes=0,new_controls_generated=False,new_helper_or_geometry=False,outputs=0)


if __name__=='__main__':
    raw,_=C.proposal(C.BT.ROM.read_bytes());q=detached(raw)
    encoded=json.dumps(q,sort_keys=True,separators=(',',':'))
    print('DKJR_BACKWARD_STAIR_INPUT '+encoded,flush=True);print('DKJR_BACKWARD_STAIR_INPUT_SHA256 '+H(encoded.encode()),flush=True)
