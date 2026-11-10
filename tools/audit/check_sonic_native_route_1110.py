"""Read-only native terrain cues for the frozen actual-Main Sonic controller.

Only the controller policy changes. The frozen producer, image, original
motor and native buffers remain intact; unavailable queries stop the route.
"""
from hashlib import sha256
import json
from pathlib import Path

import check_sonic_native_controller_1110 as Prefix
import check_sonic_native_point_read_1110 as Point

PIN='a666114414cdb8276b70e0cc96bc85ea6a311b67ab7dca2231b0ccc04417e245'


def run(image,p,*,goal_x=800,max_epochs=1500,full_stage=False):
    source=Path(Prefix.__file__).read_text()
    assert sha256(Path(Prefix.__file__).read_bytes()).hexdigest()==PIN
    old='''                    if near:last_jump=active
'''
    new='''                    foot=s['y']+32
                    wall=any(solid(s['x']+ahead,foot-1) for ahead in(24,36,48))
                    ledge=not any(solid(s['x']+36,y)for y in range(foot+1,240,16))
                    if near or wall or ledge:
                        last_jump=active
                        jumps.append(dict(reason='enemy'if near else'wall'if wall else'ledge',state=s))
'''
    assert source.count(old)==1;source=source.replace(old,new)
    old="near=any(a['flag']and a['kind']<21 and a['state']<2 and 0<=a['x']-s['x']<=56 for a in actors())"
    new="near=any(a['flag']and a['kind']<21 and a['state']<2 and 0<=a['x']-s['x']<=56 and abs(a['y']-s['y']-8)<24 for a in actors())"
    assert source.count(old)==1;source=source.replace(old,new)
    old="                if s['state']==0 and active-last_jump>24:"
    new="                if s['state']==0 and s['flags']&8 and active-last_jump>24:"
    assert source.count(old)==1;source=source.replace(old,new)
    needle='''    try:
        for epoch in range(max_epochs):'''
    replacement='''    jumps=[];best_x=0;advanced_at=0
    native_flag=None;native_castle=None;native_entrance=None
    def solid(x,y):
        status,q=Point.expected(m,x,y)
        assert status==0,('Controller lookahead unavailable',x,y,status)
        return bool(q['attribute']&1)
    try:
        for epoch in range(max_epochs):'''
    assert source.count(needle)==1;source=source.replace(needle,replacement)
    needle="                        assert label!='KillPlayer',('Sonic native opening injury/death',s,actors())"
    replacement="                        assert label not in('KillPlayer','MetaDeath'),('Sonic native route injury/death',s,actors(),jumps[-5:])"
    assert source.count(needle)==1;source=source.replace(needle,replacement)
    needle="calls=dict(hits),tail=list(tail),terminal=state(epoch)"
    assert source.count(needle)==1;source=source.replace(needle,"calls=dict(hits),jump_events=jumps,tail=list(tail),terminal=state(epoch)")
    needle='''                if active>3:pad=1'''
    replacement='''                if s['x']>best_x:best_x=s['x'];advanced_at=active
                assert active-advanced_at<120,('Sonic native route stalled',s,jumps[-4:])
                if active>3:pad=1'''
    assert source.count(needle)==1;source=source.replace(needle,replacement)
    needle="                        calls=dict(hits),minimum_SP=minimum,maximum_logical_camera_step=max_camera,"
    replacement="                        calls=dict(hits),jump_events=jumps,minimum_SP=minimum,maximum_logical_camera_step=max_camera,"
    assert source.count(needle)==1;source=source.replace(needle,replacement)
    if full_stage:
        needle="            s=state(epoch);pad=0"
        replacement="""            s=state(epoch);pad=0
            if cold is not None:
                if s['level']==0 and s['engine']==4 and s['x']>=3000 and native_flag is None:native_flag=s
                if s['level']==0 and s['engine']==5 and s['x']>=3000 and native_castle is None:native_castle=s
                if s['level']==1 and s['engine']==7 and native_entrance is None:native_entrance=s
            if cold is not None and s['level']==1 and(s['mode'],s['task'],s['engine'])==(1,3,8):
                assert s['lives']==2 and hits['FlagpoleCollision']>0 and native_flag and native_castle and native_entrance
                return dict(passed=True,source_CPU_controller_only=True,Mesen_run=False,ROM_written=False,
                    ROM_SHA256=sha256(image).hexdigest(),menu=title,cold=cold,terminal=s,active_updates=active,
                    full_native_1_1=True,active_1_2=True,calls=dict(hits),jump_events=jumps,
                    native_flag=native_flag,native_castle=native_castle,native_entrance=native_entrance,
                    minimum_SP=minimum,maximum_logical_camera_step=max_camera,
                    scope='Actual native GameLoop/parsing/actors/source-motor/native flag/score/castle and active1-2. Afterconfirmationcontroller/NMIonly; no physicalcadence/fullart/audio claim.'),m"""
        assert source.count(needle)==1;source=source.replace(needle,replacement)
        needle="                if s['x']>=goal_x:"
        assert source.count(needle)==1;source=source.replace(needle,"                if False:")
    namespace=dict(Prefix.__dict__,Point=Point,__name__=__name__)
    exec(compile(source,str(Path(__file__))+'::frozen-controller-policy-derivative','exec'),namespace)
    return namespace['run'](image,p,goal_x=goal_x,max_epochs=max_epochs)
