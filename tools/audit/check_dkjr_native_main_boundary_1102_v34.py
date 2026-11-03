"""Find actual Main ingress boundaries on the private unadmitted component.

An explicit legal flat CPU arena exposes unsupported native routes. Negative
findings are recorded, not converted into functional-admission assertions.
"""
import collections,json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O;W=A.W


def main():
    path=R/'tools/audit/check_dkjr_native_lifecycle_1102_v31.py'
    text=path.read_text().replace('native-lifecycle-v30','native-branches-v32').replace('native-lifecycle-','native-branches-').replace('-v30.bin','-v32.bin')
    env={'__name__':'dk_main_fixture','__file__':str(path)};exec(compile(text,str(path),'exec'),env)
    b,m,L,q=env['fixture']();env['direct'](m,L['DkConstruct'])
    N.put(m,CurrentPlayer=0,AreaParserTaskNum=7,GameTimerCtrlTimer=24,GameTimerExpiredFlag=0,DisableIntermediate=1,PlayerSize=1,Player_BoundBoxCtrl=1,PlayerFacingDir=1)
    for name in ['Block_Buffer_1','Block_Buffer_2']:
        for row in [11,12]:m[W.address(b,name)+row*16:W.address(b,name)+row*16+16]=[0x54]*16
    for i,v in enumerate([4,0,0]):m[W.address(b,'GameTimerDisplay')+i]=v
    ref=N.fork(m);counts=collections.Counter();trace=[];history=[];old=N.NesMPU
    points={}
    for i in range(37):
        for name in b['syms']:
            if name.startswith('Hu')and W.address(b,name)==0xb600+16*i:points[W.address(b,name),207]=name
    for name in ['GameCoreRoutine','PlayerCtrlRoutine','PlayerBGCollision','MegaManFullShotBank','BoundingBoxCore','DrawAllMetasprites']:
        points[W.address(b,name),((W.location(b,name)-16)//8192)|128]=name
    for name in ['DkNativeMain','DkjrNativeDrawBody','DkFullBox','DkGraphics','DkjrNativeTerrainHook']:
        points[L[name],2 if L[name]>=0xc000 else 3]=name
    class Trace(old):
        def step(self):
            if self.pc>=0x8000:
                name=points.get((self.pc,self.memory.rawtags[(self.pc-0x8000)//8192]))
                if name:
                    counts[name]+=1
                    if len(trace)<120:trace.append(name)
            return super().step()
    N.NesMPU=Trace;negative=None
    try:
        for epoch,pad in enumerate([0]*12+[1]*24+[129]+[1]*44+[0]*5):
            for mm in [m,ref]:N.put(mm,FrameCounter=epoch,SavedJoypadBits=pad,SavedJoypad1Bits=pad,VRAM_Buffer1_Offset=0)
            # The reference executes the complete identical donor phase; Main
            # adds native world/body/graphics/terrain channels around it.
            env['direct'](ref,L['DkNativeMain'])
            try:z=N.invoke(m,'GameCoreRoutine',a=85,x=0,y=0,p=0x31)
            except AssertionError as error:
                negative=dict(epoch=epoch,kind='actual-native-ingress-exception',detail=str(error));break
            got=[N.get(m,n)for n in ['Player_X_Position','Player_PageLoc','Player_Y_Position']]
            expected=[N.get(ref,n)for n in ['Player_X_Position','Player_PageLoc','Player_Y_Position']]
            history.append(dict(epoch=epoch,pad=pad,native=got,source_phase=expected,CPU=z['CPU'],source_state=m.ram[2][0x6b]))
            if got!=expected:
                negative=dict(epoch=epoch,kind='native-position-diverged-after-source-Main',native=got,source_phase=expected);break
    finally:N.NesMPU=old
    out=dict(passed=negative is None,qualified=False,ROM_written=False,native_owner_admitted=False,historical_v65_matching_header_fixture=True,
        epochs=len(history),negative=negative,actual_calls=dict(counts),bounded_first_ingress_trace=trace,history=history,
        scope='Actual GameCoreRoutine in isolated flat nativeBlockBuffer CPU fixture with all native loops/draw. This is a diagnostic admission boundary, not a claim that unimplemented rows/native gates are functional.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),path,O/'native-branches-v32-layout.json',O/'native-branches-v32.bin']})
    (O/'native-main-boundary-v34.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','epochs','negative','actual_calls']}))


if __name__=='__main__':main()
