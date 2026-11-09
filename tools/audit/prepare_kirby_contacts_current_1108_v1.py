"""Rebind the earned Kirby inhale and grounded shell controller without launching Mesen."""

import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import re
import sys

import check_hogan_current_bounded_v1 as N
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from observe_chip_committed_write import lua
from prepare_selected_native_packet_v1 import R, prepare, sha


CURRENT = R/'build/mini-busy-pipeline-final-1108/candidate.nes'
PIN = '37bb9c1a69b993edda540c75cbe256aeac75396d55d34d9daf3d4de86deebeeb'
PRIOR = R/'build/kirby-current-native-1102-v4/native'
PRIOR_CONTROLLER = '97d60f7ec1d66f6e5e7ec72bcc11091c32399d330ee2946cd893e766c91078f3'
PRIOR_ROUTE = R/'build/kirby-full11-1102-v7/native'
PRIOR_ROUTE_CONTROLLER = '3cff4618d0f8451a6773d4e383eb6c9861827b98009b6cd857d401c7e614d744'
ROUTE_POLICY = R/'tools/playthroughs/full_roster_policy_og.lua'
AUTHORITY = R/'build/kirby-approach-owner-1101-v3/candidate.nes'
AUTHORITY_ROM = '367266d2ec4e62fcefc15fffb3a05095a16060ad52f9d68348f213d94b31268c'
AUTHORITY_DBG = 'cada90f529ff56f943eed27979a51d723f4273c2a077274a35eee5d115fa1e54'
LUA_DEPS = R/'build/smb2-final62-observer-lua-deps-v1'
SLOT = 12
BUTTONS = dict(left=2,right=1,up=8,down=4)


def plain(value):
    if not hasattr(value,'items'):
        return value
    rows = dict(value.items())
    if rows and set(rows)==set(range(1,len(rows)+1)):
        return [plain(rows[i]) for i in range(1,len(rows)+1)]
    return {key:plain(item) for key,item in rows.items()}


def exact_once(source,before,after):
    assert source.count(before)==1,before
    return source.replace(before,after)


def menu_routes(b,mode):
    seed=N.fresh(b)
    N.put(seed,OperMode=0,OperMode_Task=3,CrossoverMenuState=2,
          CrossoverBehaviorVersion=mode,KbVariant=0)
    edges={}
    pending=[0]
    while pending:
        slot=pending.pop()
        if slot in edges:
            continue
        assert 0<=slot<64, ('Bounded menu index',slot)
        state=N.fork(seed)
        N.put(state,CrossoverMenuIndex=slot,VRAM_Buffer1_Offset=0)
        N.invoke(state,'MenuResolveCharacter')
        edges[slot]={}
        for key,bits in BUTTONS.items():
            m=N.fork(state)
            N.put(m,CrossoverMenuButtons=0,VRAM_Buffer1_Offset=0,
                  SavedJoypad1Bits=bits,SavedJoypad2Bits=0)
            N.invoke(m,'CrossoverMenuInput')
            to=N.get(m,'CrossoverMenuIndex')
            assert N.get(m,'CrossoverMenuState')==2 and N.get(m,'OperMode')==0
            edges[slot][key]=to
            pending.append(to)
        if slot==SLOT:
            assert N.get(state,'SelectedCharacter')==13 and N.get(state,'KbVariant')==0
            for bits in (0x10,0x80):
                m=N.fork(state)
                N.put(m,CrossoverMenuButtons=0,VRAM_Buffer1_Offset=0,
                      SavedJoypad1Bits=bits,SavedJoypad2Bits=0)
                N.invoke(m,'CrossoverMenuInput')
                assert N.get(m,'CrossoverMenuState')==0 and N.get(m,'SelectedCharacter')==13
    assert set(edges)==set(range(len(edges))) and SLOT in edges
    routes={}
    for start in sorted(edges):
        seen={start}; q=deque([(start,[])])
        while q:
            node,route=q.popleft()
            if node==SLOT:
                routes[start]=route
                break
            for key,to in edges[node].items():
                if to not in seen:
                    seen.add(to);q.append((to,[*route,key]))
        else:
            raise AssertionError(('Actual menu target unreachable',start))
    return edges,routes


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,default=CURRENT)
    parser.add_argument('--expected',default=PIN)
    parser.add_argument('--mode',choices=('hard','easy'),default='hard')
    parser.add_argument('--suite',choices=('contacts','full11','both'),default='contacts')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();rom=args.rom.resolve();mode=int(args.mode=='hard')
    assert sha(rom)==args.expected
    target=scoped_load(rom)
    raw=target['raw']
    assert raw[:4]==b'NES\x1a' and len(raw)==2097168 and (raw[6]>>4)==5
    assert sha(AUTHORITY)==AUTHORITY_ROM and sha(AUTHORITY.with_suffix('.dbg'))==AUTHORITY_DBG
    b=scoped_load(AUTHORITY)
    linked=b['raw']

    prior=PRIOR/'controller.lua'
    assert sha(prior)==PRIOR_CONTROLLER
    prior_ready=json.loads((PRIOR/'ready.json').read_text())
    binding=json.loads((PRIOR/'capture/binding.json').read_text())
    assert binding['exit_code']==0 and binding['ROM_sha256']==prior_ready['ROM_sha256']
    assert binding['ready_sha256']==sha(PRIOR/'ready.json')
    sys.path.insert(0,str(LUA_DEPS));from lupa.lua54 import LuaRuntime
    runtime=LuaRuntime(unpack_returned_tuples=True)
    config,body=prior.read_text().split('\n',1)
    assert config.startswith('CURRENT_KIRBY_META_EARNED=')
    parse=runtime.eval('function(s) local f,e=load(s.."\\nreturn CURRENT_KIRBY_META_EARNED", "config", "t", {}); assert(f,e); return f() end')
    c=plain(parse(config))
    assert c['ROM_sha256']==binding['ROM_sha256'] and c['character']==13 and c['variant']==0

    owners={}
    for name in ('KbWeapons','KbBodyContact','KbMovement','KbInjuryStart','KbEnsure',
                 'KbAreaReset','MkWeapons','GameLoop','NonMaskableInterrupt','IrqScrollSplit','OAMandReadJoypad'):
        start=location(b,name);size=int(b['syms'][name]['size'],0)
        assert size>0 and raw[start:start+size]==linked[start:start+size],name
        owners[name]=dict(bank=(start-16)//8192,pc=address(b,name),bytes=size,
                          sha256=hashlib.sha256(raw[start:start+size]).hexdigest())
    for name,h in c['hooks'].items():
        symbol=h['source_symbol'];delta=h['source_delta']
        assert address(b,symbol)+delta==h['pc']
        for bank in h['banks']:
            start=16+bank*8192+(h['pc']&8191)
            assert raw[start:start+len(h['bytes'])]==bytes(h['bytes']),name
        if symbol in target['syms']:
            assert address(target,symbol)==address(b,symbol),(name,'supplied public address moved')
    for name,at in c['ram'].items():
        assert address(b,name)==at or name in target['syms'],(name,at)
        if name in target['syms']:
            assert address(target,name)==at,(name,'supplied RAM address moved')
    defeat=address(b,'ShellOrBlockDefeat')
    for row in c['defeat_returns']:
        start=16+row['bank']*8192+((row['pc']-3)&8191)
        assert raw[start:start+3]==bytes([0x20,defeat&255,defeat>>8]),row

    b['raw']=raw
    edges,routes=menu_routes(b,mode)
    c['ROM_sha256']=args.expected
    c['navigation']=[route[0] if route else '' for route in routes.values()]
    c['mode']=mode
    c['unit']='held-first-inhale-and-ground-shells-current'
    common=[Path(__file__),prior,PRIOR/'ready.json',PRIOR/'capture/binding.json',AUTHORITY,AUTHORITY.with_suffix('.dbg')]
    if args.suite=='both':
        assert args.output.resolve().is_relative_to(R/'build')
        args.output.mkdir(exist_ok=True)

    def publish(kind,code,refs,scope,timeout):
        code=exact_once(code,"r('CrossoverBehaviorVersion')~=1 then menuPhase", "r('CrossoverBehaviorVersion')~=C.mode then menuPhase")
        assert code.count("r('CrossoverBehaviorVersion')==1")== (2 if kind=='contacts' else 1)
        code=code.replace("r('CrossoverBehaviorVersion')==1","r('CrossoverBehaviorVersion')==C.mode")
        controller='CURRENT_KIRBY_META_EARNED='+lua(c)+'\n'+code
        ok,error=runtime.eval('function(s)local f,e=load(s);return f~=nil,e end')(controller)
        assert ok,error
        output=args.output/kind if args.suite=='both' else args.output
        prepare(output,rom,controller,[*common,*refs],expected=args.expected,timeout=timeout,
                allow_interactive=True,scope=f'{args.mode.title()} Kirby. {scope} Prepared only.')
        ready=output/'ready.json';q=json.loads(ready.read_text())
        q.update(emulated_writes=kind=='contacts',mode=mode,menu_slot=SLOT,actual_navigation_cases=4*len(edges),
                 route_from_slot_zero=routes[0],exact_component_owners=owners,hooks=c['hooks'],
                 prior_native_positive_SHA256=binding['ROM_sha256'])
        if kind=='contacts':
            q.update(declared_setup=sorted(c['setup_allowed']),forbidden_tested_state=c['forbidden'])
        ready.write_text(json.dumps(q,indent=2)+'\n')
        print(json.dumps(dict(ROM=args.expected,mode=mode,slots=len(edges),route_from_zero=routes[0],output=str(ready))))

    if args.suite in ('contacts','both'):
        body=exact_once(body,"   transaction(function()actor(task.enemy or 6,world()+((task.face or 1)==1 and 2 or -2),184,0)end)",
            "   local first=r('SavedJoypadBits');local want=64+((task.face or 1)==1 and 1 or 2)\n"
            "   assert(first&67==want and r('KbPrevious')&64==0,'Actual fresh B and held forward at first inhale')\n"
            "   rec.first_inhale_input=first\n"
            "   transaction(function()actor(task.enemy or 6,world()+((task.face or 1)==1 and 2 or -2),184,0)end)")
        body=body.replace('Cold real Hard-mode selection, freshB close enemy inhale','Cold real selected mode, freshB plus held-forward close enemy inhale')
        publish('contacts',body,[],'Disclosed flat scene/actor setup. Native held-forward first inhale, spit, '
                'earned green/red shell hits against normally grounded Goombas. No health, ability, shot, '
                'input edge or outcome seeds.',220)

    if args.suite in ('full11','both'):
        old_route=PRIOR_ROUTE/'controller.lua'
        route_binding=json.loads((PRIOR_ROUTE/'capture/binding.json').read_text())
        assert sha(old_route)==PRIOR_ROUTE_CONTROLLER and route_binding['exit_code']==0
        assert route_binding['ROM_sha256']==binding['ROM_sha256'] and route_binding['ready_sha256']==sha(PRIOR_ROUTE/'ready.json')
        route_config,route=old_route.read_text().split('\n',1)
        assert route_config==config
        extra=re.match(r'for n,a in pairs\((\{[^\n]+\})\)do ',route)[1]
        for name,at in plain(runtime.eval(extra)).items():
            assert address(b,name)==at
            if name in target['syms']:
                assert address(target,name)==at
        assert f'local POLICY={lua(ROUTE_POLICY.as_posix())}' in route
        assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate)\s*\(',route+ROUTE_POLICY.read_text())
        publish('full11',route,[old_route,PRIOR_ROUTE/'ready.json',PRIOR_ROUTE/'capture/binding.json',ROUTE_POLICY],
                'Controller-only natural 1-1 to active 1-2 without life loss. Compact input CSV and one endpoint PNG.',240)


if __name__=='__main__':
    main()
