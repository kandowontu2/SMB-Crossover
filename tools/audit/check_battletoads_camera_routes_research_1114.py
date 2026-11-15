"""Ordinary BT full-route investigation with explicit RAM-only camera code."""
from hashlib import sha256
import argparse,json
from pathlib import Path
from unittest.mock import patch

import check_battletoads_camera_handoff_1114 as Research

Cold,Route=Research.Cold,Research.Route


def run(raw,key,limit,flag_jump=False):
    b,cache,spans,proposal=Research.recipe(raw);original=Cold.cold;arenas=[]
    dependencies={str(Path(m.__file__).name):sha256(Path(m.__file__).read_bytes()).hexdigest()
        for m in(Research,Cold,Route)}
    def cold(image,identity):
        m=original(image,identity);Research.install_ram(m,spans);arenas.append(m)
        return m
    original_controller=Route.controller
    def controller(image,identity):
        text=original_controller(image,identity)
        if flag_jump:
            old='if c.x>3120 then b.right=true end'
            new='if c.x>3120 then b.right=true;b.b=false;if c.grounded and not c.lastA then b.a=true end end'
            assert text.count(old)==1;text=text.replace(old,new,1)
            Route.Parent.Frozen.LuaRuntime().compile(text)
        return text
    def forbid(*args,**kwargs):raise RuntimeError('RAM-only BT research attempted file/Mesen output')
    with patch.object(Cold,'cold',cold),patch.object(Route,'controller',controller),patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Cold.Runner.Native,'run',forbid):
        q=Cold.run(raw,key,limit)
    assert len(arenas)==1
    retained=all(bytes(arenas[0].ram[3][pc&8191:(pc&8191)+len(code)])==code for pc,code in spans)
    return dict(proposal=proposal,dependencies=dependencies,identity=key,route=q,ordinary_final_flag_jump=flag_jump,
        RAM_code_installed_after_genuine_cold=True,RAM_recipe_retained_at_terminal=retained,
        source_RAM_research_only=True,production_candidate_qualified=False,native_qualified=False,
        composed_ROM=False,outputs=0,Mesen_run=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',required=True,choices=('rash','zitz'));p.add_argument('--limit',type=int,default=10000);p.add_argument('--flag-jump',action='store_true');a=p.parse_args()
    raw,actual=Research.load_current();q=run(raw,a.identity,a.limit,a.flag_jump);q['actual_input_SHA256']=actual
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
