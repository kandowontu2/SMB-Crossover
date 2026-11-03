"""Actual Main successor and full fixed-probe parity for native DK terrain."""
import contextlib,io,itertools,json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O;W=A.W


def main():
    boundary=R/'tools/audit/check_dkjr_native_main_boundary_1102_v34.py'
    text=boundary.read_text().replace('native-branches','native-terrain').replace('v32','v36').replace('native-main-boundary-v34.json','native-terrain-v37-Main.json')
    env={'__name__':'dk_native_terrain_main','__file__':str(boundary)}
    with contextlib.redirect_stdout(io.StringIO()):exec(compile(text,str(boundary),'exec'),env);env['main']()
    actual=json.loads((O/'native-terrain-v37-Main.json').read_text());assert actual['passed'],actual['negative']
    path=R/'tools/audit/check_dkjr_native_lifecycle_1102_v31.py'
    text=path.read_text().replace('native-lifecycle-v30','native-terrain-v36').replace('native-lifecycle-','native-terrain-').replace('-v30.bin','-v36.bin')
    env={'__name__':'dk_native_terrain_fixture','__file__':str(path)};exec(compile(text,str(path),'exec'),env)
    b,seed,L,q=env['fixture']();env['direct'](seed,L['DkConstruct']);cases=0
    for head,x,y,page,probe,tile,flags in itertools.product([True,False],[0,15,127,240,255],[32,80,176],[0,1],[14,17,18,19,20],[0,0x54,0x61],[0x31,0xa9]):
        if(head and probe!=14)or(not head and probe==14):continue
        m=N.fork(seed);N.put(m,Player_X_Position=x,Player_PageLoc=page,Player_Y_Position=y,Player_Y_HighPos=1)
        for name in ['Block_Buffer_1','Block_Buffer_2']:
            m[W.address(b,name):W.address(b,name)+208]=[tile]*208
        ref=N.fork(m)
        a=N.invoke(m,'HuHead'if head else'HuSide',a=176,x=0,y=probe,p=flags)
        c=N.invoke(ref,'BlockBufferColli_Head'if head else'BlockBufferColli_Side',a=176,x=0,y=probe,p=flags)
        assert [a[k]for k in ['A','X','Y']]==[c[k]for k in ['A','X','Y']]and a['P']&0xef==c['P']&0xef,(head,x,y,page,probe,tile,flags,a,c)
        assert bytes(m[:11])==bytes(ref[:11])and m.ram==ref.ram
        cases+=1
    sizes=(N.get(seed,'PlayerSize'),N.get(seed,'PlayerStatus'))
    for public,value in [('MegaManCollisionAdder',2),('MegaManCollisionBox',1)]:
        z=N.invoke(seed,public,a=40,x=0,y=91,p=0x31);assert z['Y']==value
    assert sizes==(N.get(seed,'PlayerSize'),N.get(seed,'PlayerStatus'))
    assert min(h['native'][2]for h in actual['history'])==161 and actual['history'][-1]['native'][2]==176
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        native_Main_epochs=actual['epochs'],native_fixed_query_full_AXYP_ZP_private_parity_cases=cases,P_comparison='All architectural flags exact; emulated nonexistent B bit ignored across public PHP/PLP frame versus direct fixed call.',
        actual_Main_position_source_parity=True,actual_original_jump_rise=15,original_native_power_state_unchanged=True,
        native_Main_actual_ingresses=actual['actual_calls'],mean_Main_CPU=sum(h['CPU']for h in actual['history'])/actual['epochs'],
        corrected_negative=dict(path='native-main-boundary-v34.json',first_bad_contract='Unfinished metatile-return Head/Side CLCRTS leaves incomingA, causing native wall resolution.',private_fix='Genuine fixed native query vectors, explicit16tall native effect probe profile; donor terrain/twohand/movement instructions unchanged.'),
        scope='Complete actual native GameCore in isolated legal flatBlockBuffer arena; epoch count is exact native_Main_epochs, no authored level/parser/emulator proof. Existing shared fullbox/contact/rare gates still lack raw40 admission and need separate final grant/rebind.',
        remaining=q['remaining'],bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),path,boundary,O/'native-terrain-v36-layout.json',O/'native-terrain-v36.bin',O/'native-terrain-v37-Main.json']})
    (O/'native-terrain-v37-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','native_Main_epochs','native_fixed_query_full_AXYP_ZP_private_parity_cases','actual_original_jump_rise','mean_Main_CPU']}))


if __name__=='__main__':main()
