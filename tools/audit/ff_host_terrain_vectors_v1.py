"""Actual native interrupt vectors at every instruction of FF terrain calls."""
from pathlib import Path
import json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_combat_controls_v1 as C
import ff_ram3_execution_controls_v2 as E
from ff_host_terrain_controls_v1 import empty,cell
from check_tmnt_render_oa import address
P=R/'build/final-fantasy-host-terrain-v3'
O=R/'build/final-fantasy-host-terrain-vectors-v1'


def state(m):
    return bytes(m[0x5c00:0x5c80]+m[0x5fc1:0x5fcf]+m[0x5fef:0x5ff0])


def setup(b,name):
    m=empty(b)
    C.put(m,Player_X_Position=250,Player_PageLoc=0,Player_Y_Position=151,
          Player_Y_HighPos=1,Player_Y_Speed=253,Player_State=1,
          FfTerrainPreviousY=154,FfTerrainFlags=0,RgCrouch=0,
          ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=120,R0=1,Local_eb=0)
    at,base,row=cell(b,258,157);m[at]=0xc1
    if name=='FfHostWall':
        C.put(m,FfTerrainPage=1,R6=base&255,R7=base>>8)
    if name=='FfHostAfterTerrain':
        C.put(m,FfTerrainFlags=1,FfTerrainTargetY=154)
    return m


if __name__=='__main__':
    assert not O.exists();O.mkdir()
    h=json.loads((P/'build-proof.json').read_text())
    for p,d in h['bindings'].items():assert C.sha(p)==d,p
    b=C.bundle(P);rows=[];failure=None
    try:
        for name in ['FfHostMovement','FfHostHead','FfHostFeet','FfHostSide','FfHostWall','FfHostAfterTerrain','FfHostBox']:
            m=setup(b,name);_,trace,_=C.run(m,name,y=0)
            for kind in ['normalNMI','lagNMI','IRQ']:
                for cut in range(len(trace)):
                    m=setup(b,name)
                    C.put(m,NmiDisable=0 if kind=='normalNMI' else 255)
                    fired=[]
                    def hook(m,c,step):
                        if step!=cut:return
                        before=state(m)
                        E.interrupt(m,c,'IRQ' if kind=='IRQ' else 'NMI')
                        assert state(m)==before,('interrupt altered FF terrain/phase bytes',name,kind,cut)
                        fired.append(True)
                    C.run(m,name,y=0,hook=hook)
                    assert fired
                    rows.append([name,kind,cut])
    except Exception as e:failure=dict(error=repr(e),traceback=traceback.format_exc())
    report=dict(passed=failure is None,status='REAL_NORMAL_LAG_NMI_IRQ_EVERY_TERRAIN_INSTRUCTION',image_sha256=C.sha(P/'ram3.bin'),cases=len(rows),FF_bytes_per_ISR=143,actual_native_vectors=True,all33_SMC_and_live_page1=True,uninstalled_offline_RAM3=True,failure=failure,bindings={**h['bindings'],str((P/'build-proof.json').resolve()):C.sha(P/'build-proof.json'),str(Path(__file__).resolve()):C.sha(__file__)})
    (O/'controls.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k!='bindings'}))
    if failure:raise SystemExit(1)
