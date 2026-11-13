"""Trace the actual authored-row pickup approach and original screen clamp."""

from collections import Counter
import contextlib
import io
import json

import compose_jay_head_bridge_1113 as P

B=P.B
N,W=B.Current.N,B.Current.W


def captured_approach(image):
    _,seed=P.cold(image,P.NEW_COOKIE,P.CANDIDATE_PIN)
    saved=[]
    def observe(m,epoch,pad):
        s=B.Current.state(m)
        if not saved and s['x']==351 and s['Player_Y_Position']==112 and s['donor_flags']&2:
            saved.append(B.Current.C.L.clone(m))
    with contextlib.redirect_stdout(io.StringIO()):
        result=B.Current.natural(seed,400,pad_observer=observe)
    assert result['passed'] and len(saved)==1
    return saved[0]


def trace(seed,camera):
    m=B.Current.C.L.clone(seed)
    N.put(m,ScreenLeft_PageLoc=camera>>8,ScreenLeft_X_Pos=camera&255,
          ScreenRight_PageLoc=(camera+255)>>8,ScreenRight_X_Pos=(camera+255)&255)
    linked=B.Gun.C.Jay.build()
    symbols=linked['symbols']
    names=('JayPositionSetup','ClampScreenX','XWorldFromScreen','SideBlocked','SnapToFloor')
    points={symbols[n]:n for n in names}
    fields=linked['ram']
    pending=None
    queries=[]
    counts=Counter()
    states=[]
    for epoch in range(6):
        def observe(m,c):
            nonlocal pending
            if pending and (c.pc,c.sp)==pending['return']:
                pending.update(result=c.a,status=m[0xc0f3],tile=m[0xc0f4],attributes=m[0xc0f5])
                del pending['return']
                queries.append(pending)
                pending=None
            if m.rawtags[1]!=3:return
            name=points.get(c.pc)
            if name:counts[name]+=1
            if c.pc==symbols['JayHostTile']:
                pending=dict(epoch=epoch,row=m[0xc0f0],column=m[0xc0f1],direction=m[0xc0f2],
                             return_pc=c.pc)
                pending['return']=(m[0x101+c.sp]+256*m[0x102+c.sp]+1,c.sp+2)
        m.controller_pad=2
        B.Current.Frames.frame(m,observe)
        state=B.Current.state(m)
        state.update(source_screen_x=m.ram[2][fields[0x16]-0xc000],
                     VX=m.ram[2][fields[0x14]-0xc000])
        states.append(state)
    assert counts['SideBlocked']==0
    side=[q for q in queries if q['direction']==4]
    assert side and all(q['status']==0 and q['tile']==0 and q['result']==0 for q in side)
    if camera==336:
        assert counts['ClampScreenX']==counts['XWorldFromScreen']==6
        assert all(s['x']==351 and s['Player_Y_Position']==112 and s['donor_control']&4 for s in states)
        assert states[-1]['JnHealth']==6
    else:
        assert states[-1]['x']==348 and states[-1]['JnHealth']==8
    return dict(camera=camera,counts=dict(counts),states=states,queries=queries,
                original_screen_minimum=17,side_probe_wall_contacts=0)


if __name__=='__main__':
    installed=B.Current.ROM.read_bytes()
    image=installed if P.digest(installed)==P.CANDIDATE_PIN else P.proposal(installed)[0]
    seed=captured_approach(image)
    print(json.dumps(dict(ROM_SHA256=P.CANDIDATE_PIN,source_CPU=True,output_files=0,
        declared_camera_data_fixture=True,authored_row=True,comparisons=[trace(seed,c)for c in(333,336)])),flush=True)
