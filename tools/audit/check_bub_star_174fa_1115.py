"""Ordinary actual174fa Star source controller; stdout only."""
import argparse,json
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import replay_bub_star_174fa_1115 as F

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--identity',type=int,choices=(0,1),default=0);ap.add_argument('--hurt-observer',action='store_true');a=ap.parse_args()
    raw,actual=F.load_current()
    hurt=[];saved=[];old_cold=F.B.cold;old_cpu=F.N.NesMPU
    labels=json.loads((F.R/'build/bub-upgrades-root-1102-v48/proposal.json').read_text())['labels']
    def cold(image,who):
        out=old_cold(image,who);saved.append(out[0]);return out
    class Passive(old_cpu):
        def step(self):
            m=self.memory
            if a.hurt_observer and self.pc==labels['BbNativeHurtChoose']and m.rawtags[1]==3 and len(hurt)<4:
                slot=m.ram[2][0x3c0];s=F.B.state(m)
                fields=('Enemy_ID','Enemy_State','Enemy_Flag','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_MovingDir')
                target={n:F.N.get(m,n,slot)for n in fields}
                hurt.append(dict(state=s,slot=slot,target=target,PC=self.pc,SP=self.sp,
                    original_hurt_scratch=list(m.ram[2][0x140:0x148]),
                    body=[m[F.W.address(m.bundle,'BoundingBox_UL_Corner')+i]for i in range(4)],
                    camera=F.N.get(m,'ScreenLeft_X_Pos')+256*F.N.get(m,'ScreenLeft_PageLoc')))
            return super().step()
    def forbid(*args,**kw):raise AssertionError('Star source attempted file output')
    with patch.object(Path,'write_text',forbid),patch.object(Path,'write_bytes',forbid),patch.object(F.B,'cold',cold),patch.object(F.N,'NesMPU',Passive):
        try:q=F.source_check(raw,a.identity)
        except AssertionError as e:
            assert len(e.args)==1 and isinstance(e.args[0],dict)and'receipt'in e.args[0];q=e.args[0]
    r=q.get('receipt')or{};star=r.get('natural_star')or{}
    digest=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(dict(passed=q['passed'],input_SHA256=actual,executed_SHA256=F.PIN,identity=a.identity,
        Lua_SHA256=q['controller_SHA256'],receipt_SHA256=digest,Main=r.get('Main_updates'),moves=r.get('source_updates'),
        star=star,hurt=hurt,terminal=r.get('terminal'),reason=r.get('reason'),output_files=0),separators=(',',':')),flush=True)
    assert q['passed'],'Natural Star remains source-unqualified'
