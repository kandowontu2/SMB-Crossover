"""Bounded ordinary-input ledge diagnosis on the historical f544 source image."""
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path

import dkjr_footer_source_input_1116 as Input
import replay_dkjr_platform_footer_current_1116 as F
import check_dkjr_carry_camera_route_1116 as R

H=lambda value:sha256(value).hexdigest()
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def execute(controller=None,limit=3400):
    public,binding=Input.normalize(ROM.read_bytes(),kind='bt91dc-reference-only')
    parent,_=F.C.Camera.proposal(public)
    raw,composition=F.C.proposal(parent)
    assert F.C.inverse(raw)==parent
    text=F.source_controller(raw) if controller is None else controller(raw,source=True)
    opening,m=R.cold(raw)
    tick=0;recent=[]
    def after(memory):
        nonlocal tick
        tick+=1
        s=R.B.state(memory)
        if 1120<=s['x']<=1240 and tick%4==0 and len(recent)<72:
            actors=[]
            for i in range(6):
                if R.N.get(memory,'Enemy_Flag',i):
                    actors.append(dict(slot=i,id=R.N.get(memory,'Enemy_ID',i),
                        x=R.N.get(memory,'Enemy_X_Position',i)+256*R.N.get(memory,'Enemy_PageLoc',i),
                        y=R.N.get(memory,'Enemy_Y_Position',i),state=R.N.get(memory,'Enemy_State',i)))
            recent.append(dict(tick=tick,**s,pad=memory.controller_pad,
                vx=R.N.get(memory,'Player_X_Speed'),vy=R.N.get(memory,'Player_Y_Speed'),
                previousAB=R.N.get(memory,'PreviousA_B_Buttons'),actors=actors))
    with redirect_stdout(io.StringIO()):
        result=R.B.route(m,raw,limit,controller_text=text,after_frame=after)
    q=result.get('receipt') or {}
    report=dict(passed=bool(result['passed']),binding=binding,composition=composition,
        controller_SHA256=H(text.encode()),opening=opening,terminal=R.B.state(m),
        reason=q.get('reason'),logical_source_updates=tick,
        events=q.get('events',[])[-8:],recent=recent,
        source_only=True,ordinary_inputs_only=True,game_state_seeds=0,outputs=0)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_LEDGE_DIAG '+encoded,flush=True)
    print('DKJR_LEDGE_DIAG_SHA256 '+H(encoded.encode()),flush=True)
    return report


if __name__=='__main__':execute()
