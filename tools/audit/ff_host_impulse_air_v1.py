"""Close the native-to-source fractional bounce handoff over three air ticks."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_pickups_edges_v3 as T
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import location
C=T.C;put=T.put;get=T.get;run=T.run
O=R/'build/final-fantasy-host-impulse-air-v1'


if __name__=='__main__':
    assert not O.exists()
    h=json.loads((T.P/'build-proof.json').read_text())
    for p,d in h['bindings'].items():assert C.sha(p)==d,p
    b=C.bundle(T.P);native=qualified(C.E.P/'candidate.nes');rows=[]
    for name,keys in itertools.product(['X5StompDispatch','X5SpringDispatch'],[0,128]):
        m=T.T.setup(b)
        put(m,Player_State=2,Player_Y_Position=176,Player_Y_HighPos=1,
            SavedJoypadBits=keys,CrossoverBehaviorVersion=0,SwimmingFlag=0,
            MmUnderwater=0,FfJump=0,FfGPhase=31)
        physical=(location(native,name)-16)//8192
        T.T.V.direct(m,name,x=2,bank=physical|128)
        velocity=get(m,'MmVY',1)+256*get(m,'MmVY',2)
        low=get(m,'MmVY')
        m.raw_page(1,3);T.setv(m,'CurrentBank',3)
        run(m,'FfHostImpulseAccepted')
        phase=0
        for tick in range(1,4):
            # This is the actual dry source 28/36 remainder sequence, with
            # the genuine native fractional impulse used as its initial value.
            phase+=28;gravity=49
            if phase>=36:phase-=36;gravity=50
            velocity=(velocity+gravity)&65535
            put(m,Player_State=1,SavedJoypadBits=0)
            run(m,'FfMovement')
            actual=get(m,'MmVY',1)+256*get(m,'MmVY',2)
            assert actual==velocity,(name,keys,tick,hex(actual),hex(velocity))
            assert get(m,'MmVY')==low
            assert get(m,'FfGPhase')==phase and get(m,'FfJump')==1
            assert get(m,'Player_Y_Speed')==velocity>>8
            rows.append([name,keys,tick,velocity,phase])
    bindings={**h['bindings'],str((T.P/'build-proof.json').resolve()):C.sha(T.P/'build-proof.json')}
    for p in [Path(__file__).resolve(),Path(T.__file__).resolve(),T.O/'controls.json']:
        bindings[str(p)]=C.sha(p)
    report=dict(passed=True,image_sha256=C.sha(T.P/'ram3.bin'),
                genuine_native_to_source_air_ticks=len(rows),
                full_fraction_and_source_gravity_remainder_exact=True,
                cart_hooks=False,native=False,rows=rows,bindings=bindings)
    O.mkdir();(O/'controls.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k not in ['bindings','rows']}))
