"""Cold controller-only full roster browse with actual compiled-name oracle."""
import argparse,json
from pathlib import Path
import audit_current_menu_indicators_1102_v1 as A
import check_hogan_current_bounded_v1 as M
from inventory_playable_menu_1101_v3 import menu_name
from check_tmnt_render_oa import address
from prepare_selected_native_packet_v1 import prepare,sha
from observe_chip_committed_write import lua
R=A.R

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--launch',choices=['mr-gimmick','bub','bob'])
    args=ap.parse_args()
    b=A.bundle();b['raw']=args.rom.read_bytes()
    screen=M.fresh(b);M.put(screen,CrossoverMenuState=1,Mirror_PPUMASK=0,DisableScreenFlag=1)
    M.invoke(screen,'CrossoverMenuInput')
    silhouette=[[(12+y)*32+25+x,screen.vram[0x2000+(12+y)*32+25+x]]for y in range(4)for x in range(3)]
    assert any(cell[1]!=36 for cell in silhouette),'Battletoads silhouette must be populated'
    m=M.fresh(b);M.put(m,CrossoverMenuIndex=0);M.invoke(m,'MenuResolveCharacter');M.invoke(m,'QueueSelection')
    plans=[];seen=[];launch_states={}
    def action(key=None):
        if key:
            bits={'right':1,'left':2,'down':4,'up':8,'start':16,'select':32,'b':64,'a':128}
            M.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=bits[key],SavedJoypad2Bits=0)
            M.invoke(m,'CrossoverMenuInput')
        name,cells=menu_name(m);slot=M.get(m,'CrossoverMenuIndex');raw=M.get(m,'SelectedCharacter')
        assert (63 in cells)==('PRINCE' in name),(slot,name)
        shot=None
        if name in ['RASH','MR GIMMICK','BUB','BOB'] and name not in seen:shot=name.lower().replace(' ','-')
        plans.append(dict(keys=[key]if key else[],slot=slot,variant=0,tag=name,state=2,kind='observe',wait=40,raw=raw,name=cells,shot=shot,groups=M.get(m,'FmGroups')))
        seen.append(name)
        if name in ['MR GIMMICK','BUB','BOB'] and name not in launch_states:
            launch_states[name]=M.fork(m)
        return name,raw
    snake=list(range(8))+list(range(15,7,-1))+list(range(16,24))+list(range(31,23,-1))
    previous=0
    for slot in snake:
        if slot==0:initial=action()
        else:
            key='down'if slot//8!=previous//8 else'right'if slot>previous else'left'
            initial=action(key)
        assert M.get(m,'CrossoverMenuIndex')==slot
        for cycle in range(16):
            result=action('select')
            if result==initial:break
        else:raise AssertionError(('alternate cycle bound',slot))
        previous=slot
    assert all(n in seen for n in ['MR GIMMICK','BUB','BOB','RASH','ZITZ'])
    assert sum(bool(s['shot'])for s in plans)==4
    launch=None
    if args.launch:
        target=args.launch.upper().replace('-',' ')
        end=next(i for i,s in enumerate(plans)if s['tag']==target)
        plans=plans[:end+1]
        for step in plans:step['shot']=None
        plans[-1]['shot']='selected-owner'
        selected=plans[-1]
        launched=launch_states[target]
        M.put(launched,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=128,SavedJoypad2Bits=0)
        M.invoke(launched,'CrossoverMenuInput')
        assert M.get(launched,'CrossoverMenuState')==0
        assert M.get(launched,'SelectedCharacter')==selected['raw']
        launch=dict(raw=selected['raw'],groups=M.get(launched,'FmGroups'),bob=1 if target=='BOB'else 0,requiresRestore=False)
        plans.append(dict(selected,keys=['a'],kind='launch',shot=None,tag='confirm-selected-owner'))
    text=(R/'tools/audit/bub_menu_qualification_1102_v2.lua').read_text()
    old="  for _,cell in ipairs({{676,245},{677,246},{708,247},{709,248}})do assert(ppu(0x2000+cell[1])==cell[2],'Actual same-span NT copy/icon survives rebuild')end"
    assert old in text;text=text.replace(old,"  for _,cell in ipairs(Q.silhouette)do assert(ppu(0x2000+cell[1])==cell[2],'Battletoads silhouette survives all selections')end")
    start=text.index('  if s.slot==32 then');end=text.index("  if s.family=='BT'",start)
    text=text[:start]+text[end:]
    text=text.replace("assert(n==33,'All33 positions actually visited')","assert(n==32,'All32 positions actually visited')")
    symbols=['OperMode','OperMode_Task','CrossoverMenuState','CrossoverMenuIndex','SelectedCharacter','FmGroups','GameEngineSubroutine','VRAM_Buffer1','VRAM_Buffer1_Offset']
    # The existing observer consumes L/Q supplied through its documented globals.
    config=dict(mode='launch-'+args.launch if args.launch else 'mr-gimmick-family-and-ready-indicators',steps=plans,maxFrames=len(plans)*40+800,launch=launch,required_positions=32,silhouette=silhouette)
    prefix='local L='+lua({n:address(b,n)for n in symbols})+'\nlocal Q='+lua(config)+'\n'
    scope='Controller-only cold selection and A launch for '+args.launch+'; actual source identity and active owner. No movement/fullstage claim.' if args.launch else 'Controller-only all32 roster slots and complete Select cycles; exact emitted names, current ready markers, four native screenshots. No gameplay/fullstage claim.'
    prepare(args.output,args.rom,prefix+text,[Path(__file__),Path(A.__file__),R/'tools/audit/bub_menu_qualification_1102_v2.lua'],expected=sha(args.rom),timeout=240,scope=scope,allow_interactive=True)

if __name__=='__main__':main()
