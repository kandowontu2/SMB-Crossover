"""Plan or bind small controller-only menu packets; root alone runs Mesen."""
from pathlib import Path
import argparse,json,sys,collections
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
O=R/'build/bub-menu-candidate-1102-v2';P=R/'build/bub-menu-integration-1102-v1'
MODES=['browse-blocked','browse-admitted','bub-start','bob-start','bt-start','cf-start']

def lua(x):
    if x is None:return 'nil'
    if x is True:return 'true'
    if x is False:return 'false'
    if isinstance(x,str):return json.dumps(x,ensure_ascii=True)
    if isinstance(x,(int,float)):return str(x)
    if isinstance(x,list):return '{'+','.join(lua(v)for v in x)+'}'
    if isinstance(x,dict):return '{'+','.join('['+lua(k)+']='+lua(v)for k,v in x.items())+'}'
    raise TypeError(type(x))

def plans():
    data=json.loads((P/'frontend-closure.json').read_text());profiles={(z['slot'],z['variant']):z for z in data['profiles']}
    nav=(R/'build/bub-menu-navigation-1102-v1/navigation.bin').read_bytes();directions={k:list(nav[i*33:(i+1)*33])for i,k in enumerate(['left','right','up','down'])}
    def path(source,target):
        pending=collections.deque([(source,[])]);seen={source}
        while pending:
            at,route=pending.popleft()
            if at==target:return route
            for key in ['down','right','up','left']:
                to=directions[key][at]
                if to not in seen:seen.add(to);pending.append((to,route+[(key,to)]))
        raise AssertionError('Connected real33slot graph')
    def step(keys,slot,variant=0,*,tag=None,state=2,kind='observe',shot=None):
        if slot==32:
            name=[36]*16;name[6:9]=[11,24 if variant else 30,11];raw=39
        else:
            row=profiles[slot,variant];raw=row['raw'];name=row['names'][-1]
        z=dict(keys=keys,slot=slot,variant=variant,tag=tag or f'slot{slot}-variant{variant}',state=state,kind=kind,wait=40,raw=raw,name=name if state==2 else None,shot=shot)
        if slot==32:z['bob']=variant
        if slot in[23,30]:z['family']='BT'if slot==23 else'CF'
        return z
    result={}
    snake=list(range(8))+list(range(15,7,-1))+list(range(16,24))+list(range(31,23,-1))+[32]
    for mode in ['browse-blocked','browse-admitted']:
        route=[step([],0,tag='initial-slot0')];current=0;seen={0}
        for target in snake[1:]:
            move=path(current,target);assert len(move)==1
            key,current=move[0];route.append(step([key],current));seen.add(current)
            if current in[23,30]:
                count=2 if current==23 else 4
                for v in range(1,count):route.append(step(['select'],current,v,shot='bt-zitz'if current==23 else'cf-beans'if v==3 else None))
                route.append(step(['select'],current,0,tag=f'family{current}-wrap-retains-other-flags'))
            if current==29:
                route.append(step(['select'],29,1,tag='prince-still-locked'))
                for key in['a','start']:route.append(step([key],29,1,tag='prince-'+key+'-blocked',kind='locked-confirm'))
                route.append(step(['select'],29,0,tag='excitebike-ready-retained'))
        assert seen==set(range(33))
        route[-1]['shot']='new-bub'
        route.append(step(['select'],32,1,tag='new-bob',shot='new-bob'))
        if mode=='browse-blocked':
            for keys in[['a'],['start'],['select','a'],['select','start']]:route.append(step(keys,32,1,tag='new-blocked-'+'+'.join(keys),kind='blocked-confirm'))
        # Rebuild the selector twice through real title/options controls.
        route +=[step(['b'],32,1,tag='title-return',state=0),step(['start'],32,1,tag='roster-rebuilt-Bob-retained'),
                 step(['b'],32,1,tag='title-again',state=0),step(['down'],32,1,tag='title-options-focus',state=0),
                 step(['a'],32,1,tag='ordinary-options',state=4),step(['b'],32,1,tag='options-title-return',state=0),
                 step(['start'],32,1,tag='options-roster-rebuilt-Bob-retained')]
        result[mode]=dict(mode=mode,steps=route,maxFrames=3600,launch=None,required_positions=33,scope='All33 real positions, bothBub/Bob, oldBT2/CF4 alternatives, Prince gate, title/options rebuild and actual source name/palette/CHR/DMA. No gameplay claim.')
    for mode,target,variant,keys,raw,groups,requires in[
        ('bub-start',32,0,['select','a'],39,0,False),('bob-start',32,1,['select','start'],39,128,False),
        ('bt-start',23,1,['select','a'],33,32,True),('cf-start',30,3,['select','start'],31,24,True)]:
        route=[step([],0,tag='initial-slot0')];current=0
        for key,current in path(0,target):route.append(step([key],current))
        for v in range(1,variant+1):route.append(step(['select'],target,v))
        route.append(step(keys,target,variant,tag='simultaneous-select-confirm',kind='launch'))
        result[mode]=dict(mode=mode,steps=route,maxFrames=1400,launch=dict(raw=raw,groups=groups,bob=variant if target==32 else None,requiresRestore=requires),required_positions=None,
            scope='Cold controller-only actual simultaneousSelect/confirm priority, original identity, shared P1 retirement and active owner handoff. Bub/Bob also requires actual authenticated Fresh identity/ready writes. No movement/fullstage claim.')
    for mode,q in result.items():
        assert sum(s['wait']for s in q['steps'])+180+(360 if q['launch']else 0)<q['maxFrames']
        assert sum(bool(s['shot'])for s in q['steps'])+(1 if q['launch']else 0)<=4
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--prepare',choices=MODES);ap.add_argument('--rom',type=Path,default=O/'candidate.nes');ap.add_argument('--sha256');a=ap.parse_args()
    O.mkdir(exist_ok=True);q=plans();source=R/'tools/audit/bub_menu_qualification_1102_v2.lua';text=source.read_text()
    for bad in['emu.write','emu.loadSavestate','emu.saveSavestate','emu.reset','emu.loadState','emu.saveState']:assert bad not in text,'Controller-only source'+bad
    # Plans stay unbound until a frozen exact candidate is supplied. This does
    # not create executable packets or claim unready backend acceptance.
    record=dict(passed=True,prepared=False,native=False,controller_only=True,plans=q,
        current_candidate_is_blocked=True,conditional_launch_modes=['bub-start','bob-start'],
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),source,P/'frontend-closure.json',R/'build/bub-menu-navigation-1102-v1/navigation.bin']})
    (O/'native-menu-plans.json').write_text(json.dumps(record,indent=2)+'\n')
    if a.prepare:
        rom=a.rom.resolve();actual=sha(rom);assert not a.sha256 or actual==a.sha256
        b=scoped_load(rom);blocked=b['raw'][16+66*8192+0xd64]==0x38
        if a.prepare=='browse-blocked':assert blocked,'Blocked packet must test actual SEC gate'
        if a.prepare in['browse-admitted','bub-start','bob-start']:assert not blocked,'Do not prepare raw39 launch until actual owning gate is approved/rebound'
        chosen=q[a.prepare];at=location(b,'GroundPaletteData');chosen['restore']=list(b['raw'][at+24:at+27])
        # Explicit symbols make the controller independent of future Downloads
        # sidecars. The normal isolated packet retains minimal debug as well.
        names=['CrossoverMenuState','CrossoverMenuIndex','OperMode','OperMode_Task','SelectedCharacter','FmGroups','VRAM_Buffer1_Offset','VRAM_Buffer1','GameEngineSubroutine']
        prefix='\n'.join(f'L[{json.dumps(n)}]={address(b,n)}'for n in names)+'\nlocal Q='+lua(chosen)+'\n'
        output=O/('native-menu'if a.prepare=='browse-blocked'else 'native-'+a.prepare)
        refs={Path(__file__),source,O/'native-menu-plans.json',O/'candidate.json',R/'docs/qa/allocations/bub-menu-static-1102-v3.json'}
        prepare(output,rom,prefix+text,refs,expected=actual,timeout=180 if a.prepare.startswith('browse')else 120,scope=chosen['scope'],allow_interactive=True)
    files=[p for p in O.rglob('*')if p.is_file()];assert sum(p.stat().st_size for p in files)<32000000 and len(files)<=128
    print(json.dumps(dict(passed=True,native=False,plans={k:dict(actions=len(v['steps']),global_frames=v['maxFrames'],PNG_cap=4)for k,v in q.items()},prepared=a.prepare,bytes=sum(p.stat().st_size for p in files),files=len(files))))
if __name__=='__main__':main()
