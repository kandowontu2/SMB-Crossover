"""Prepare actual native Easy contact and original bounce on the exact v7 ROM."""
from pathlib import Path
import copy,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import prepare_bub_menu_qualification_1102_v2 as N
O=N.O;B=R/'build/bubble-bobble-source-1101-v1';PIN='31c0de8d169c84a03465eea959961cb38da3666a1e3dffd4bda982efbac11f85'

def main():
    rom=O/'combined-stomp.nes';assert sha(rom)==PIN
    observer=B/'native-observer-bub-1102-v4.lua';observer_receipt=B/'native-observer-prepared-1102-v4.json'
    assert json.loads(observer_receipt.read_text())['ROM_sha256']==PIN
    b=scoped_load(rom);full=scoped_load(R/'build/wwf-death-1102-v2/candidate.nes')
    ordered=O/'ordered-input-v3/native-menu-plans.json';plan=copy.deepcopy(json.loads(ordered.read_text())['plans']['bub-start'])
    plan.update(maxFrames=4200,ROM_sha256=PIN)
    at=location(b,'GroundPaletteData');plan['restore']=list(b['raw'][at+24:at+27])
    source=R/'tools/audit/bub_menu_qualification_1102_v2.lua';body=source.read_text();extension=R/'tools/audit/bub_native_easy_1102_v7.lua'
    changes={
        "local log=assert(io.open(OUTPUT..'observations.csv','w'))":extension.read_text()+"\nlocal log=assert(io.open(OUTPUT..'observations.csv','w'))",
        " elseif phase=='route'and age<6 then for _,key in ipairs(Q.steps[at].keys)do keys[key]=true end end":" elseif phase=='route'and age<6 then for _,key in ipairs(Q.steps[at].keys)do keys[key]=true end\n elseif phase=='easy'then for _,key in ipairs(easy_keys())do keys[key]=true end end",
        " if done then return end;frame=frame+1;age=age+1":" if done then return end;frame=frame+1;age=age+1;BUB_OBSERVER.frame(easy_label(),easy_step)",
        "  shot('active-owner');finish()\n end":"  easy_begin()\n elseif phase=='easy'then easy_tick(finish)\n end"
    }
    for old,new in changes.items():assert body.count(old)==1;body=body.replace(old,new)
    names=['CrossoverMenuState','CrossoverMenuIndex','OperMode','OperMode_Task','SelectedCharacter','FmGroups','VRAM_Buffer1_Offset','VRAM_Buffer1','GameEngineSubroutine','Player_PageLoc','Player_X_Position','Player_Y_Position','Player_State','NumberofLives','Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','CrossoverBehaviorVersion']
    prefix='\n'.join(f'L[{json.dumps(n)}]={address(full,n)}'for n in names)+'\nlocal Q='+N.lua(plan)+'\n'
    controller=prefix+observer.read_text()+'\n'+body
    for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in controller
    refs={Path(__file__),source,extension,observer,observer_receipt,ordered,O/'combined-stomp.json',R/'docs/qa/allocations/bubble-stomp-1102-v7.json'}
    prepare(O/'native-stomp-bub-easy',rom,controller,refs,expected=PIN,timeout=210,
        scope='Exact31c0 v7 native Easy from actual cold menu. Natural first Goomba +original Right/A jump, actual physicalEnemyStomped/MegaBounce, subsequent originalD36B restart and supported landing; no B/bubble/statewrites/fullstage/install. Actual geometry controller first qualification pending.',allow_interactive=True)
    own=[p for p in O.rglob('*')if p.is_file()]
    assert sum(p.stat().st_size for p in own)<32000000 and len(own)<1000
    print(json.dumps(dict(prepared=True,ROM_SHA256=PIN,files=len(own),bytes=sum(p.stat().st_size for p in own))))

if __name__=='__main__':main()
