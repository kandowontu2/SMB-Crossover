"""Current owning CF costs with frozen observers; no new opcodes/ROM/native."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,ast,json
import current_contra_force_readonly_1327_1116 as M

P,N,W,Frames=M.Previous,M.N,M.W,M.Frames
OUTSIDE=M.R/'tools/audit/inspect_contra_force_caller_union_1116.py'
OUTSIDE_SHA='ad1b2d1d03781987542c08e462bb90d45f05136a0d7c2dce05feb668a9ab324c'


def outside(raw):
    # Extract only the retained read-only observer, never its old ffbb default
    # loader/composer. It executes ordinary actual current game bytes.
    assert M.H(OUTSIDE.read_bytes())==OUTSIDE_SHA
    text=OUTSIDE.read_text();tree=ast.parse(text)
    node=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='run')
    ns=dict(Counter=Counter,patch=patch,M=M,C=M,N=N,W=W,Frames=Frames)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(OUTSIDE),'exec'),ns)
    out=ns['run'](raw);out['retained_observer_source_SHA256']=M.H(OUTSIDE.read_bytes());return out


def run(raw,busy=False):
    q=M.bindings(raw)
    wrong=0
    for image in(M.reference(raw)[0],raw[:-1],raw[:100]+bytes((raw[100]^1,))+raw[101:]):
        try:M.bindings(image)
        except AssertionError:wrong+=1
        else:raise AssertionError('Historical/dirty/unknown input admitted as current')
    with patch.object(P,'bindings',M.bound):timed=P.profile(raw,busy)
    rows=[]
    for phase in timed['phases']:
        assert phase['calls']==phase['returns']and not phase['nonlocal_unwinds']and not phase['unclosed_scopes']
        main=phase['calls']['GameLoop'];total=phase['inclusive_excluding_ISR']['GameLoop']
        exclusive=phase['innermost_exclusive'];assert sum(exclusive.values())>=total
        # ISR scopes are present in the same aggregate; only the acknowledged
        # GameLoop column and its named innermost children form the Main sum.
        rows.append(dict(phase=phase['phase'],Main=main,total_Main_cycles=total,cycles_per_Main=total/main,
            innermost_exclusive=exclusive,inclusive=phase['inclusive_excluding_ISR'],calls=phase['calls'],
            actual_Main_classes=phase['main_classes'],ISR=phase['ISR'],minimum_SP=phase['minimum_SP'],
            final_x=phase['final_x'],final_y=phase['final_y']))
    result=dict(passed=True,bindings=q['current_proof'],wrong_roles_rejected=wrong,profile=rows,
        outside_one_ordinary_idle_Main=None if busy else outside(raw),
        source_only_no_native_cadence_or_current30Hz_claim=True,
        old_bc5_native_witness='c95fafe9a703dff44b018a845639d508c99eda40a2296b6f1b79b5070f3aaac7',
        historical_native_witness_remains_bc5_versioned=True,proposed_game_bytes_executed=False,
        no_ROM_files_or_captures_or_gameplay_seeds=True,outputs=0)
    result['receipt_SHA256']=M.H(json.dumps(result,sort_keys=True,separators=(',',':')).encode());return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--busy',action='store_true');a=p.parse_args()
    raw=M.load_current_image();reader=Path.read_bytes
    def read(path):
        assert path.resolve()!=M.ROM.resolve(),'No second mutable Nightly read'
        return reader(path)
    def deny(*a,**k):raise AssertionError('Read-only CF attribution attempted file/native work')
    with patch.object(Path,'read_bytes',read),patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(raw,a.busy)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
