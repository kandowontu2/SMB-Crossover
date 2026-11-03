"""Small current-source standing-A contract/height measurement; no ROM/native run."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit')]
import check_prince_pose_reservation_1103_v186 as A
import build_storage_guard_v1 as G
M,N,I=A.M,A.N,A.I
O=R/'build/prince-control-recipe-1103-v190'


def row(m,epoch):
    s=m.ram[2]
    return dict(Main=epoch,action=s[0x616],pose=s[0x617],mode=s[0x618],
                phase=s[0xa6]&3,A_lock=s[0x6c0],sourceY=s[0x611],poseDelta=s[0x88],
                foot=int.from_bytes(s[0x84:0x86],'little'),nativeY=N.get(m,'Player_Y_Position'),
                nativeState=N.get(m,'Player_State'),X=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'))


def main():
    G.preflight(private_root=O,reserved_bytes=30000,reserved_files=1,fresh=True)
    O.mkdir(exist_ok=True)
    base,q=M.image();e,m,lab=A.first8(base)
    rows=[];advances=0;controls=0;begun=None;start=None;last=None
    # Only actual controller bits change after native entrance. Terrain is the
    # existing explicit flat CPU fixture from first8; no source outcome writes.
    stage='settle'
    for epoch in range(180):
        s=m.ram[2]
        if stage=='settle' and epoch>=4 and s[0x618]==0 and s[0x617]==15 and s[0x6c0]==0:
            stage='A';start=row(m,epoch)
        pad=128 if stage=='A' else 0
        m.controller_pad=pad;N.put(m,SavedJoypad1Bits=pad,SavedJoypadBits=pad)
        phase=s[0xa6]&3
        e['run'](m,'GameLoop',lab)
        if phase==0:advances+=1
        if phase==2:controls+=1
        now=row(m,epoch)
        if stage=='A' and now['action']==3:
            begun=dict(now,A_held_controls=controls,A_held_advances=advances);stage='flight'
        if stage!='settle' and (last is None or (now['pose'],now['sourceY'],now['foot'],now['nativeY'])!=last):
            rows.append(now);last=(now['pose'],now['sourceY'],now['foot'],now['nativeY'])
        assert N.get(m,'GameEngineSubroutine')==8 and N.get(m,'NumberofLives')==2 and s[0x6cf]==5
        if stage=='flight' and epoch>begun['Main']+8 and now['mode']==0 and now['pose']==15 and now['A_lock']==0:
            break
    assert start and begun and stage=='flight' and rows[-1]['pose']==15
    ymin=min(r['sourceY'] for r in rows);footmin=min(r['foot'] for r in rows);native_min=min(r['nativeY'] for r in rows)
    assert ymin<start['sourceY'] and footmin<start['foot'] and native_min<start['nativeY']
    assert rows[-1]['foot'] in range(start['foot']-1,start['foot']+2)
    out=dict(passed=True,CPU_only=True,ROM_written=False,Mesen_run=False,
             memory_SHA256=q['expected_memory_only_SHA256'],initial=start,original_action3_started=begun,
             source_Y_range=[ymin,max(r['sourceY'] for r in rows)],physical_foot_range=[footmin,max(r['foot'] for r in rows)],
             completed_Main_nativeY_range=[native_min,max(r['nativeY'] for r in rows)],
             actual_source_y_lift=start['sourceY']-ymin,actual_foot_lift=start['foot']-footmin,
             actual_nativeY_lift=start['nativeY']-native_min,completed_Mains=epoch+1,trace=rows,
             recipe='Neutral until original mode0/pose15/A-lock06C0=0; holdA until realaction3 admission, then release and await source mode0/pose15 and foot support. Original standinghop is not Mario jumpheight.',
             pipe_recipe='Existing v8 compiled-source CPU: facingpipe, stop roughly32..40px before edge, wait mode0/pose15, holdUp for64nativeMain epochs, retainUp through original hanging/climbing modes2/6, then Right after above/through pipe. Existing flat16/32/48/64Up cases are CPU-only; A-only32pipe negative, actualnative firstpipe remains pending.',
             scope='One actual currentca90+185 source-backed cold/entrance/fullGameLoop, flat terrain CPU fixture, genuine inputonly through original four phases. No code/source state/outcome injection, native emulator, ability/helper/fullstage claim.',
             bindings={p.relative_to(R).as_posix():M.sha(p) for p in [Path(__file__),Path(A.__file__),
                    M.O/'pose-manifest.json',R/'build/prince-actor-1101-v1/contact-core.s',
                    R/'build/prince-actor-1101-v1/core-CPU.json',
                    R/'tools/audit/check_prince_host_world_compiled_1102_v8.py']})
    (O/'control-recipe.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['trace','bindings']}))


if __name__=='__main__':
    try:main()
    except Exception as error:
        p=O/'control-negative.json'
        if not p.exists():p.write_text(json.dumps(dict(passed=False,error=repr(error)),indent=2)+'\n')
        raise
