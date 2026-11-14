"""Declared native-descent/floor primitive; isolate clipping and fall origin."""
from hashlib import sha256
import json
from unittest.mock import patch

import compose_dkjr_direct_platform_1113 as T
import check_dkjr_direct_platform_1113 as Gate


def run(seed,candidate,floor):
    C,Q,H,N,W,L=Gate.C,Gate.Q,Gate.H,Gate.N,Gate.W,Gate.L
    C.SLOT=5;m=C.setup(Q.mounted(seed,candidate))
    # Component terrain, not a natural route or a recovered final-stair map.
    for name in('Block_Buffer_1','Block_Buffer_2'):
        at=W.address(m.bundle,name);m[at:at+208]=bytes(208)
        if floor:
            for y in(208,224):m[at+((y-32)&240):at+((y-32)&240)+16]=bytes([0x54])*16
    C.field(m,'Enemy_Y_Speed',1)
    history=[];writers=[];handoff=[];previous=None;Base=N.NesMPU
    class Probe(Base):
        def step(self):
            nonlocal previous
            fields=tuple(m.ram[2][a]for a in(0x6b,0x6c,0x76,0x210))
            if previous is not None and fields!=previous['fields']:
                if fields[0]!=previous['fields'][0]or fields[2]!=previous['fields'][2]:
                    writers.append(dict(PC=previous['PC'],bank=previous['bank'],before=previous['fields'],after=fields))
            previous=dict(PC=self.pc,bank=m.rawtags[(self.pc-32768)//8192]if self.pc>=32768 else-1,fields=fields)
            return super().step()
    first=C.native_contact(m,1,False)
    assert first['passenger']==5,first
    initial=C.view(m)
    with patch.object(N,'NesMPU',Probe):
        for age in range(110):
            C.source_step(m)
            before=C.view(m)
            if before['source']==5:break
            N.put(m,ObjectOffset=5)
            r=Q.direct(m,Gate.entry(candidate),x=5)
            flag=N.get(m,'PlatformCollisionFlag',5)
            C.field(m,'Enemy_Y_Position',N.get(m,'Enemy_Y_Position',5)+1)
            if flag<128:N.invoke(m,'PositionPlayerOnVPlat',x=5)
            after=C.view(m)
            if after['top']in(188,194,195,196,197,207,208,209,213)or after['source']!=before['source']:
                history.append(dict(age=age,before=before,passenger_after_actual_dispatch=flag,after=after))
            if floor and after['top']==195:
                N.invoke(m,'EraseEnemyObject',x=5)
                for release in range(32):
                    C.source_step(m)
                    state=C.view(m)
                    if release<5 or state['source']!=4:handoff.append(dict(release_update=release,state=state))
                    if state['source']==5 or state['source']==1 and state['nativeY']==176:break
                break
            if after['top']>=213:break
    return dict(floor_at208=floor,initial=initial,history=history,final=C.view(m),
        source_transition_and_origin_writers=writers,handoff_after_explicit_actor_removal_at195=handoff)


def main():
    parent,candidate=T.load_inputs();e73=T.Old.reverse(parent);P,H=Gate.P,Gate.H
    _,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    rows=[run(seed,candidate,floor)for floor in(False,True)]
    assert all(r['passenger_after_actual_dispatch']==5 for r in rows[0]['history'])
    assert rows[1]['final']['source']==1 and rows[1]['final']['nativeY']==176,rows[1]
    assert rows[1]['final']['fallStart']==178 and rows[1]['final']['fallLimit']==24,rows[1]
    print('DKJR_FINAL_DESCENT_COMPONENT '+json.dumps(dict(candidate_SHA256=sha256(candidate).hexdigest(),
        rows=rows,unit_actor_terrain_and_motion_delta_inputs=True,compiled_native_sampler_executed=True,
        source_or_native_ROM_writes=False,outputs_written=0,
        scope='Declared component based on earlier944carry fixture, source/native instructions with1px actor delta. Not actual final3040 geometry, a genuine route, or physical cadence.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
