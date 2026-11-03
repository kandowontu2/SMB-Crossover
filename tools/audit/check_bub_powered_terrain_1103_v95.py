"""Exercise measured rising-bubble interception against real native collision."""
import json
from pathlib import Path
import check_bub_powered_bubble_1103_v92 as P
from prepare_selected_native_packet_v1 import R,sha
O,N,Q,address=P.O,P.N,P.Q,P.address


def main():
    b,route,q,_,_,_=P.C.bundle();b=dict(b,raw=P.ROM.read_bytes());assert sha(P.ROM)==P.PIN
    previous=json.loads((O/'powered-bubble-CPU-v94.json').read_text())
    assert len(previous['cases'])==8 and all(c['minimum_native_y']==97 and any(e['support']&127 for e in c['events'])for c in previous['cases'])
    native=N.NesMPU;rows=[]
    for identity in[0,1]:
        for top in[176,160,144]:
            m=P.earn_shoes(b,route,identity);actor=0x42 if identity else 0x2e
            # Explicit legal solid-column arena, not a claim of natural parser birth.
            for wx in[160,176]:
                for yy in range(top,208,16):
                    at=address(b,'Block_Buffer_1')+((wx//256)&1)*208+((yy-32)//16)*16+(wx%256)//16
                    m[at]=0x54
            phase='grow';chosen=None;events=[];trace=[];epoch=-1;takeoff=None
            class Trace(native):
                def step(self):
                    if self.pc==q['labels']['BbOriginal_D36B']and self.memory.rawtags[1]==3:
                        events.append(dict(update=epoch,held=self.memory.ram[2][actor+1],**P.sample(self.memory,identity)))
                    return native.step(self)
            N.NesMPU=Trace
            try:
                for epoch in range(180):
                    s=P.sample(m,identity);bubble=next((v for v in s['bubbles']if chosen is None or v['slot']==chosen),None)
                    if chosen is None and bubble:chosen=bubble['slot']
                    if epoch<4:keys=65
                    elif phase=='grow':
                        keys=1 if bubble and bubble['gap']>34 else 0
                        if bubble and bubble['kind']==2 and 30<=bubble['gap']<=36 and bubble['dy']<=-16:
                            takeoff=dict(update=epoch,**s);phase='forward';keys=129
                    else:keys=129
                    N.put(m,FrameCounter=epoch,SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                    N.invoke(m,'GameCoreRoutine',x=0,y=0)
                    after=P.sample(m,identity);trace.append(dict(update=epoch,keys=keys,**after))
                    assert m.ram[2][actor+2]==1 and N.get(m,'NumberofLives')==2
            finally:N.NesMPU=native
            landings=[v for v in trace if v['x']>=200 and v['y']==176 and v['native_state']==0]
            passed=bool(takeoff and any(e['support']&127 for e in events)and landings and min(v['y']for v in trace)<=top-32)
            row=dict(identity=identity,top=top,left=160,right_exclusive=192,passed=passed,
                takeoff=takeoff,source_D36B=events,minimum_y=min(v['y']for v in trace),
                maximum_x=max(v['x']for v in trace),far_supported_landing=landings[0]if landings else None,
                samples=[v for v in trace if v['update']%8==0])
            rows.append(row);print(json.dumps({k:row[k]for k in['identity','top','passed','minimum_y','maximum_x','source_D36B']}),flush=True)
    result=dict(passed=all(v['passed']for v in rows),CPU_only=True,ROM_written=False,ROM_SHA256=P.PIN,cases=rows,
        source_clock_reuse=dict(path='build/bub-powered-trajectory-1103-v92/powered-bubble-CPU-v94.json',
            SHA256=sha(O/'powered-bubble-CPU-v94.json'),scope='All8 actual trajectories earned support and79px rise. That receipt retains its negative80px target; this terrain test uses the real authored column height and far supported landing.'),
        scope='Actual complete native Main, original source movement/support and native side/head/foot consumers. Both identities earn shoes through real item collection in a deliberately initialized legal CPU arena and cross32/48/64px columns at160..192, then genuinely land beyond200. No natural flower/emulator/fullstage claim.',
        bindings={str(p.relative_to(R)):sha(p)for p in[Path(__file__),Path(P.__file__),P.ROM]})
    (O/'powered-terrain-CPU-v95.json').write_text(json.dumps(result,indent=2)+'\n')
    assert result['passed'],'Native solid-column crossing failed'


if __name__=='__main__':main()
