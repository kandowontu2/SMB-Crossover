"""Actual installed FF side query -> real wall entry, including page seams."""
from pathlib import Path
import json, sys, traceback

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_joint_terrain_hooks_controls_1030_v1 as T
from ff_host_terrain_controls_v1 import cell
H=T.H;O=T.O;sha=T.sha


def main():
    out=O/'actual-FF-walls-v1.json';assert not out.exists()
    p=dict(passed=False,native=False,admitted=False,actual_cart_hooks=True,
           observer_changes_no_PC_registers_or_SMC=True,rows=[])
    try:
        b=H.C.qualified(O/'joint/candidate.nes');seed=T.T.base(b)
        for side in[1,2]:
            for blockwx in[0,16,240,256,272,496,512,65520]:
                wx=(blockwx-12 if side==1 else blockwx+14)&65535
                m=T.fixture(seed,22,tile=0xc1)
                H.put(m,Player_X_Position=wx&255,Player_PageLoc=wx>>8,
                      Player_Y_Position=176,R0=side)
                query_y=5 if side==1 else 3
                c,_=H.invoke(m,'CrossoverSourceSideProbe',a=22,x=0,y=query_y,p=0x71)
                point=(wx+(14 if side==1 else 1))&65535
                at,base,row=cell(b,point,184)
                assert c.a==0xc1
                assert [H.get(m,n)for n in['R6','R7','R2','FfTerrainPage']]==[base&255,base>>8,row,point>>8]
                c,low=T.direct(m,'SamusStopAtWall',a=22)
                expected=(blockwx-15 if side==1 else blockwx+15)&65535
                actual=H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc')
                assert actual==expected and c.p&1,('source wall clamp',side,blockwx,actual,expected)
                assert H.get(m,'Player_CollisionBits')==255^side
                assert all(H.get(m,n)==0 for n in['Player_X_Speed','Player_X_Scroll'])
                assert all(m[H.address(b,'MmVX')+i]==0 for i in range(3))
                H.exact(m)
                p['rows'].append(dict(side=side,block_world_X=blockwx,player_before=wx,
                     actual_source_query_Y=query_y,tuple=[base&255,base>>8,row],
                     player_after=actual,minimum_SP=low,CPU=c.processorCycles))
        p['passed']=True
    except Exception as e:p.update(error=repr(e),traceback=traceback.format_exc())
    p['bindings']={str(f.resolve()):sha(f)for f in[Path(__file__),Path(T.__file__),O/'source-closure.json',
       O/'joint/candidate.nes',O/'joint/candidate.dbg']}
    target=out if p['passed']else O/'actual-FF-walls-negative-v1.json';assert not target.exists()
    target.write_text(json.dumps(p,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=p['passed'],cases=len(p['rows']),error=p.get('error'),path=str(target))),flush=True)
    assert p['passed']


if __name__=='__main__':main()
