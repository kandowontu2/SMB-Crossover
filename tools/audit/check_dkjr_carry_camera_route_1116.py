"""Actual owning candidate cold and ordinary full route; no game-state seeds."""
import argparse
import ast
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
from unittest.mock import patch

import replay_dkjr_carry_camera_current_1116 as F
import check_dkjr_public_first_pipe_67_1115 as Cold

C, B, N = F.C, Cold.B, Cold.N
H = lambda value: sha256(value).hexdigest()


def cold(raw):
    """Same compiled constructor/zero-input endpoint, owning cookie explicit."""
    module = B.C.Starts
    path = C.R/'tools/audit/check_current_roster_stage_ingress_1110.py'
    tree = ast.parse(path.read_text())
    fn = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='stage')
    hits=0
    for node in ast.walk(fn):
        if (isinstance(node,ast.Compare) and isinstance(node.left,ast.Name) and node.left.id=='ticks'
            and len(node.ops)==1 and isinstance(node.ops[0],ast.GtE)
            and len(node.comparators)==1 and isinstance(node.comparators[0],ast.Constant)
            and node.comparators[0].value==60):
            node.comparators[0].value=0;hits+=1
    assert hits==1
    scope=dict(module.__dict__)
    exec(compile(ast.Module(body=[fn],type_ignores=[]),str(path),'exec'),scope)
    with patch.object(module,'stage',scope['stage']):
        opening,memory=Cold.H.cold(raw,raw[534485:534501])
    assert opening['opening_updates']==0 and memory.bundle['raw']==raw
    opening['scope']='Actual owning compiled Select/Start/parser/cold; zero extra opening inputs'
    return opening,memory


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent', type=Path, required=True)
    ap.add_argument('--limit', type=int, default=15000)
    ap.add_argument('--cold-only', action='store_true')
    args = ap.parse_args()
    parent = args.parent.read_bytes()
    candidate, composition = C.proposal(parent)
    assert C.inverse(candidate) == parent
    print('DKJR_CAMERA_ROUTE_PHASE frozen-composition '+C.CANDIDATE, flush=True)
    native_text = F.controller(candidate)
    text = F.source_controller(candidate)
    print('DKJR_CAMERA_ROUTE_PHASE native-Lua '+H(native_text.encode()),flush=True)
    opening, memory = cold(candidate)
    assert memory.bundle['raw'] == candidate and H(memory.bundle['raw']) == C.CANDIDATE
    cookie = candidate[534485:534501]
    assert all(bytes(memory.ram[i][0x1fe0:0x1ff0]) == cookie for i in (2,3))
    print('DKJR_CAMERA_ROUTE_PHASE actual-cold '+json.dumps(opening,separators=(',',':')),flush=True)
    if args.cold_only:
        print('DKJR_CAMERA_COLD '+json.dumps(dict(passed=True, composition=composition, opening=opening,
            Lua_SHA256=H(native_text.encode()), source_Lua_SHA256=H(text.encode()),
            CPU_execution_input=C.CANDIDATE, reference_execution=False, outputs=0),separators=(',',':')),flush=True)
        return
    body = C.payload(candidate)
    source_writers = {0xa000+i for i in range(0x1fde) if body[i:i+3] == bytes.fromhex('8d6bc0')}
    counts = Counter()
    first_bad = None
    fourth = {}
    tick = 0
    slot944 = None
    def view(m,c):
        s=m.ram[2]
        return dict(tick=tick,PC=c.pc,SP=c.sp,A=c.a,X=c.x,Y=c.y,P=c.p,**B.state(m),
            sourceX=s[0x213],sourceY=s[0x210],origin=s[0x76],limit=s[0x7b],
            prior=s[0x6c],camera_saved=s[0x435]+256*s[0x436],delta=s[0x438],
            box=list(m[0x658:0x65c]),query=list(s[0x3e:0x42]),window=list(s[0x8e8:0x8ec]))
    def observe(m,c):
        nonlocal first_bad, slot944
        tag=m.rawtags[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
        if tag==3 and c.pc in source_writers and c.a==5 and first_bad is None:
            first_bad=view(m,c)
        if (tag,c.pc)==(3,0xb770):counts['accepted_import_helper']+=1
        if (tag,c.pc)==(3,0xb773):counts['shift_return_success' if c.p&1 else 'shift_return_reject']+=1
        if (tag,c.pc)==(199,0xac29):
            slot=c.x
            if slot<6 and N.get(m,'Enemy_ID',slot)==37 and (
                N.get(m,'Enemy_X_Position',slot)+256*N.get(m,'Enemy_PageLoc',slot)==944):
                slot944=slot;counts['native_944_position_returns']+=1
                fourth.setdefault('first_position',view(m,c))
                fourth['last_position']=view(m,c)
        if slot944 is not None and tag==3 and c.pc==0xb5c8 and m.ram[2][0x8f0]==slot944:
            counts['944_plane_candidates']+=1
            if 'first_plane' not in fourth:
                row=view(m,c);row['plane']=c.a
                row['candidate']=list(m.ram[2][0x8e4:0x8e8])
                fourth['first_plane']=row
    output=__import__('sys').stdout
    def after(m):
        nonlocal tick
        tick+=1
        if tick%1000==0:
            print('DKJR_CAMERA_ROUTE_PROGRESS '+json.dumps(dict(tick=tick,**B.state(m)),separators=(',',':')),file=output,flush=True)
    with redirect_stdout(io.StringIO()):
        result=B.route(memory,candidate,args.limit,controller_text=text,observe_extra=observe,after_frame=after)
    receipt=result.get('receipt') or {}
    report=dict(passed=result['passed'],owning_parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,
        composition=composition,opening=opening,native_Lua_SHA256=H(native_text.encode()),
        source_Lua_SHA256=H(text.encode()),logical_updates=result['logical_updates'],
        terminal=result['final'],reason=receipt.get('reason'),first_source5=first_bad,
        counts=dict(counts),fourth=fourth,crossings=receipt.get('crossings'),
        carries={k:dict(count=v.get('count'),first=v.get('first'),last=v.get('last')) for k,v in receipt.get('carries',{}).items()},
        grounded_12_motor_returns=receipt.get('grounded_12_return_count'),
        total_12_motor_returns=receipt.get('actual_12_returns'),
        first_grounded_12_return=receipt.get('first_grounded_12_return'),last_grounded_12_return=receipt.get('last_grounded_12_return'),
        last_events=receipt.get('events',[])[-8:],ordinary_controls_unchanged=True,
        game_state_seeds=False,native_claim=False,output_files=0)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_CAMERA_ROUTE '+encoded,flush=True)
    print('DKJR_CAMERA_ROUTE_SHA256 '+H(encoded.encode()),flush=True)
    assert result['passed'], report['reason']


if __name__=='__main__':main()
