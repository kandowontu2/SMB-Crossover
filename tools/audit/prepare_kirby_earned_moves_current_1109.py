"""Rebind the previously verified Kirby power and copy batches to current hardware."""
import argparse
import json
from pathlib import Path
import sys

from observe_chip_committed_write import lua
from prepare_kirby_contacts_current_1108_v1 import LUA_DEPS, PRIOR, plain
from prepare_selected_native_packet_v1 import R, prepare, sha


VERIFIED = R/'build/kirby-current-1109/contacts'
ROM = R/'build/mini-parser-lift-1109/candidate.nes'
UNITS = {'copies-low':'kirby-copies-low-1102-v5',
         'copies-high':'kirby-copies-high-1102-v5',
         'basics':'kirby-basics-1102-v6'}


def checked(path):
    ready=json.loads((path/'ready.json').read_text())
    binding=json.loads((path/'capture/binding.json').read_text())
    report=json.loads((path/'capture/result.json').read_text())
    controller=path/'controller.lua'
    assert binding['exit_code']==0 and report['passed']
    assert binding['ROM_sha256']==report['ROM_sha256']==ready['ROM_sha256']
    assert binding['ready_sha256']==sha(path/'ready.json')
    assert ready['bindings'][str(controller.resolve())]==sha(controller)
    return ready,report,controller


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    current,current_report,current_controller=checked(VERIFIED)
    prior,_,historical_controller=checked(PRIOR)
    for name,digest in current['bindings'].items():
        assert sha(name)==digest,name
    assert current['ROM_sha256']==sha(ROM) and current['mode']==1
    assert all(case['injuries']==0 for case in current_report['cases'])
    sys.path.insert(0,str(LUA_DEPS))
    from lupa.lua54 import LuaRuntime
    runtime=LuaRuntime(unpack_returned_tuples=True)
    parse=runtime.eval(r'function(s) local f,e=load(s.."\nreturn CURRENT_KIRBY_META_EARNED", "cfg", "t", {}); assert(f,e); return f() end')
    syntax=runtime.eval('function(s) local f,e=load(s); return f~=nil,e end')

    def parts(path):
        config,body=path.read_text().split('\n',1)
        return plain(parse(config)),body

    previous,previous_body=parts(historical_controller)
    config,_=parts(current_controller)
    assert config['hooks']==previous['hooks'] and config['ram']==previous['ram']
    assert config['mode']==1 and config['setup_allowed']==previous['setup_allowed']
    args.output.mkdir()
    for unit,folder in UNITS.items():
        origin=R/'build'/folder/'native'
        ready,report,controller=checked(origin)
        old,body=parts(controller)
        assert ready['ROM_sha256']==prior['ROM_sha256']
        assert old.keys()==previous.keys() and body==previous_body
        assert all(old[key]==value for key,value in previous.items() if key!='plan')
        assert len(report['cases'])==len(old['plan'])
        assert body.count("r('CrossoverBehaviorVersion')~=1 then menuPhase")==1
        assert body.count("r('CrossoverBehaviorVersion')==1")==2
        body=body.replace("r('CrossoverBehaviorVersion')~=1 then menuPhase",
                          "r('CrossoverBehaviorVersion')~=C.mode then menuPhase")
        body=body.replace("r('CrossoverBehaviorVersion')==1","r('CrossoverBehaviorVersion')==C.mode")
        config.update(plan=old['plan'],unit=unit)
        text='CURRENT_KIRBY_META_EARNED='+lua(config)+'\n'+body
        ok,error=syntax(text)
        assert ok,error
        prepare(args.output/unit,ROM,text,[Path(__file__),current_controller,VERIFIED/'ready.json',
                VERIFIED/'capture/binding.json',controller,origin/'ready.json',origin/'capture/binding.json'],
                expected=sha(ROM),timeout=220,allow_interactive=True,
                scope='Hard Kirby earned-copy and basic moves. Disclosed flat scene, actor and item setup; no ability, health or outcome seeds.')


if __name__=='__main__':
    main()
