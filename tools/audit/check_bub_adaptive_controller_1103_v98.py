"""Replay the prepared Lua input gate against all measured source-clock traces."""
import json,sys
from pathlib import Path
import prepare_bub_adaptive_flower_1103_v97 as P
from prepare_selected_native_packet_v1 import R,sha


def main():
    O=P.P.O;source=O/'powered-bubble-CPU-v94.json';q=json.loads(source.read_text())
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    rows=[]
    for case in q['cases']:
        lua=LuaRuntime();identity=case['identity'];actor=0x42 if identity else 0x2e;oy=8 if identity else 0
        current={};lua.globals().Q=lua.table_from(dict(launch=lua.table_from(dict(bob=identity))))
        def state(at):
            s=current['row']
            if at==0x301:return s['keys']
            if at==actor+3:return s['selector']
            if at==0x1f:return s['clock']
            if at==0x103+oy:return s['sx']
            if at==0x100+oy:return s['sy']
            for b in s['bubbles']:
                if at==0x88+4*b['slot']:return b['kind']
                if at==0x188+8*b['slot']:return b['y']
                if at==0x18b+8*b['slot']:return b['x']
            return 0
        lua.globals().full_state=state
        lua.globals().full_x=lambda:current['row']['x']
        lua.globals().r=lambda n:current['row']['y']if n=='Player_Y_Position'else 0
        lua.globals().full_normal_jump_ready=lambda actor:current['row']['native_state']==0 and current['row']['selector']==0
        lua.globals().full_support_probe=lambda:lua.table_from(dict(native_state=current['row']['native_state']))
        growth=lua.execute(P.HELPER+'\nreturn powered_growth')
        event=lua.table_from(dict(Main=1,kind='original-bubble-launch',detail=lua.table_from(dict(flag=1,logical_slot=0))))
        events=lua.table_from([event]);base=lua.table_from(dict(completed_Main=0))
        launch=case['events'][0]['update'];checks=0;actual=None
        for index in range(launch):
            current['row']=case['trace'][index]
            summary=lua.table_from(dict(completed_Main=index+1,events=events))
            pad,takeoff=growth(summary,base,index+1)
            keys=(1 if pad['right']else 0)|(2 if pad['left']else 0)|(64 if pad['b']else 0)|(128 if pad['a']else 0)
            assert keys==case['trace'][index+1]['keys'],(identity,case['neutral_prefix'],index,keys,case['trace'][index+1]['keys'])
            checks+=1
            if takeoff:actual={n:takeoff[n]for n in['x','y','slot','bubble_kind','source_gap','source_vertical_gap','source_clock']}
        assert actual is not None
        rows.append(dict(identity=identity,neutral_prefix=case['neutral_prefix'],exact_input_decisions=checks,takeoff=actual))
    out=dict(passed=True,CPU_and_Lua_only=True,ROM_SHA256=P.P.PIN,cases=rows,
        source_contract=dict(shoes_flag=1,move_passes_per_source_player=2,
            takeoff_latch='OriginalD36B copies held&3; neutral latch0 cannot be steered into a ride afterward.',
            bubble_support='OriginalDC68 requires absolute axes<16, player above bubble, vertical10..15 and horizontal<10; bubble pass writes actor+9 after player movement.',
            restart='Next ordinary player step with selector2/3 and heldA consumes support, resets selector0 and calls originalD36B; Right latches forward1.',
            gate='A newly launched mature bubble30..36px ahead and16px above is intercepted after about20sourceupdates. All4 clock residues/both identities earn support1 and79px total rise.'),
        terrain_reuse=dict(path='powered-terrain-CPU-v95.json',scope='Both identities cross32/48px native solid columns.64px case reaches far side but prior180-update farlanding200 target ends too early; negative retained.'),
        terrain_completion=dict(path='powered-terrain-CPU-v96.json',scope='Only64px cases continued under220update bound; both pass actual far-supported landing beyond200.'),
        native_packet='bub-flower/run.py',native_has_not_run=True,emulated_writes=False,
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),Path(P.__file__),source,
            O/'powered-terrain-CPU-v95.json',O/'powered-terrain-CPU-v96.json',O/'bub-flower/controller.lua',O/'bub-flower/ready.json']})
    (O/'adaptive-controller-CPU-v98.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=len(rows),exact_input_decisions=sum(v['exact_input_decisions']for v in rows))))


if __name__=='__main__':main()
