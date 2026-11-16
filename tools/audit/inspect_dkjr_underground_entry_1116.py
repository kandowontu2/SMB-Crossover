"""Passive source1-2 first-writer scope over unchanged F8716 ordinary inputs."""
from collections import Counter
from hashlib import sha256
import json
from unittest.mock import patch

import check_dkjr_pipe5_depart_defense_1116 as Check

F,Root=Check.F,Check.Previous
R,C,N=Root.Route,F.C,Root.Route.N
H=lambda value:sha256(value).hexdigest()


def main():
    original=R.B.route
    def route(memory,raw,*args,**kwargs):
        assert H(raw)==C.CANDIDATE
        old_observe=kwargs.get('observe_extra');old_after=kwargs.get('after_frame')
        tick=0;watching=False;ready=None;previous=None;pending=None
        events={};counts=Counter();body=C.Camera.payload(raw)
        origin_writers={0xa000+i for i in range(0x1fde)if body[i:i+3]==bytes.fromhex('8d76c0')}
        phase_writers={0xa000+i for i in range(0x1fde)if body[i:i+3]==bytes.fromhex('8d6bc0')}
        area=N.address(memory.bundle,'AreaType');level=N.address(memory.bundle,'LevelNumber');world=N.address(memory.bundle,'WorldNumber')
        def view(m,c=None):
            r=m.ram[2];row=dict(host_update=tick,**R.B.state(m),ready=r[0x8fe],phase=r[0x6b],prior=r[0x6c],
                origin=r[0x76],limit=r[0x7b],facing=r[0x6d],age=r[0x7e],source_y=r[0x210],
                source_x=r[0x213],source_held=r[0x14],source_fresh=r[0x15],pad=m.controller_pad,
                nativeVY=N.get(m,'Player_Y_Speed'),query_kind=r[0x8db],query=list(r[0x3e:0x42]),
                contact=list(r[0x42:0x46]),window=list(r[0x8e8:0x8ec]),native_body=list(m[0x658:0x65c]),
                area_type=m[area],level=m[level],world=m[world])
            if c is not None:row.update(PC=c.pc,SP=c.sp,A=c.a,X=c.x,Y=c.y,P=c.p,writer=previous)
            return row
        def first(name,m,c=None):
            if name not in events:
                assert len(events)<8
                events[name]=view(m,c)
        def observe(m,c):
            nonlocal ready,previous,pending
            if old_observe:old_observe(m,c)
            if not watching:return
            r=m.ram[2];tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
            if r[0x8fe]==2 and ready!=2:first('first-anchored-ready2',m,c)
            ready=r[0x8fe]
            if(tag,c.pc)==(2,0xd65e):
                counts['actual_motor_entries']+=1;first('first-1-2-motor-entry',m,c)
                assert pending is None
                ret=(m[0x100+((c.sp+1)&255)]+256*m[0x100+((c.sp+2)&255)]+1)&65535
                pending=(ret,(c.sp+2)&255)
            if pending==(c.pc,c.sp):
                counts['actual_motor_returns']+=1;pending=None
                if r[0x6b]==5:first('first-phase5-motor-return',m,c)
            if(tag,c.pc)==(3,0xbd93):counts['native_injury_BD93']+=1
            if(tag,c.pc)==(3,0xbd9f):counts['native_deathstart_BD9F']+=1
            if tag==3 and c.pc in origin_writers:first('first-original-origin-store',m,c)
            if(tag,c.pc)==(3,0xa8ce):first('first-original-landing-decision',m,c)
            if tag==3 and c.pc in phase_writers and c.a==5:first('first-original-phase5-store',m,c)
            previous=dict(PC=c.pc,tag=tag,A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,
                bytes=bytes(m[(c.pc+i)&65535]for i in range(3)).hex())
        def after(m):
            nonlocal tick,watching,ready
            if old_after:old_after(m)
            tick+=1
            active=m[area]==2 and m[level]==1 and m[world]==0
            if active and not watching:
                watching=True;ready=m.ram[2][0x8fe];first('first-completed-1-2-entry-frame',m)
            if watching:
                counts['completed_1-2_host_updates']+=1
                counts['engine_'+str(N.get(m,'GameEngineSubroutine'))]+=1
        kwargs.update(observe_extra=observe,after_frame=after)
        result=original(memory,raw,*args,**kwargs)
        q=dict(controller_native_SHA256=H(F.controller(raw).encode()),source_image_SHA256=H(raw),
            original_strong_gameplay_passed=bool(result['passed']),counts=dict(counts),events=events,
            reason=(result.get('receipt')or{}).get('reason'),terminal=R.B.state(memory),
            witness_bound=8,source_controls_unchanged=True,new_game_bytes=0,outputs=0,
            scope='Passive actuala3fb source first completed1-2 entry frame onward; motor entry/return and first real writers. Not native or a full-route positive.')
        encoded=json.dumps(q,sort_keys=True,separators=(',',':'))
        print('DKJR_UNDERGROUND_ENTRY '+encoded,flush=True);print('DKJR_UNDERGROUND_ENTRY_SHA256 '+H(encoded.encode()),flush=True)
        return result
    with patch.object(R.B,'route',route):Check.main()


if __name__=='__main__':main()
