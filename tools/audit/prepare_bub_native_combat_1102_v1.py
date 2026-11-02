"""Bind an actual cold start to one bounded, naturally earned bubble encounter."""
from pathlib import Path
import argparse,copy,json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import prepare_bub_menu_qualification_1102_v2 as N
O=N.O;BACK=R/'build/bubble-bobble-source-1101-v1';ROM=O/'combined-visible.nes'
PIN='4395ed57aaeccfd05ca743fc603f0d1b69b4991b072b55e68b49507cffc8c2ab'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['timeout','pop'],default='timeout');a=ap.parse_args()
    assert sha(ROM)==PIN
    observer=BACK/'native-observer-bub-1102-v3.lua';observer_receipt=BACK/'native-observer-prepared-1102-v3.json'
    assert json.loads(observer_receipt.read_text())['ROM_sha256']==PIN
    b=scoped_load(ROM);full=scoped_load(R/'build/wwf-death-1102-v2/candidate.nes')
    ordered=O/'ordered-input-v3/native-menu-plans.json';plan=copy.deepcopy(json.loads(ordered.read_text())['plans']['bub-start'])
    plan.update(maxFrames=6500,ROM_sha256=PIN)
    at=location(b,'GroundPaletteData');plan['restore']=list(b['raw'][at+24:at+27])
    source=R/'tools/audit/bub_menu_qualification_1102_v2.lua';body=source.read_text();extension=R/'tools/audit/bub_native_combat_1102_v1.lua'
    replacements={
        "local log=assert(io.open(OUTPUT..'observations.csv','w'))":extension.read_text()+"\nlocal log=assert(io.open(OUTPUT..'observations.csv','w'))",
        " elseif phase=='route'and age<6 then for _,key in ipairs(Q.steps[at].keys)do keys[key]=true end end":" elseif phase=='route'and age<6 then for _,key in ipairs(Q.steps[at].keys)do keys[key]=true end\n elseif phase=='combat'then for _,key in ipairs(combat_keys())do keys[key]=true end end",
        " if done then return end;frame=frame+1;age=age+1":" if done then return end;frame=frame+1;age=age+1;BUB_OBSERVER.frame(combat_label(),combat_step)",
        "  shot('active-owner');finish()\n end":"  combat_begin()\n elseif phase=='combat'then combat_tick(finish)\n end"
    }
    for old,new in replacements.items():assert body.count(old)==1;body=body.replace(old,new)
    names=['CrossoverMenuState','CrossoverMenuIndex','OperMode','OperMode_Task','SelectedCharacter','FmGroups','VRAM_Buffer1_Offset','VRAM_Buffer1','GameEngineSubroutine','Player_PageLoc','Player_X_Position','Player_Y_Position','Player_State','NumberofLives','ScreenLeft_X_Pos','ScreenLeft_PageLoc','Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position']
    prefix='\n'.join(f'L[{json.dumps(n)}]={address(full,n)}'for n in names)+'\nlocal Q='+N.lua(plan)+'\nlocal COMBAT_MODE='+json.dumps(a.mode)+'\n'
    controller=prefix+observer.read_text()+'\n'+body
    for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in controller
    refs={Path(__file__),source,extension,observer,observer_receipt,ordered,O/'combined-visible.json',
          R/'docs/qa/allocations/bubble-visible-1102-v6.json',R/'docs/qa/checkpoints/2026-11-02/bub-controls-native-v1/manifest.json'}
    prepare(O/('native-earned-bub-'+a.mode),ROM,controller,refs,expected=PIN,timeout=230,
        scope='Actual Bub cold confirm, naturally parsed positive Goomba, genuine freshB source bubble then earned '+a.mode+'. Actual Main/headers/CHR/RGB/draw-pair observer, source clock/native flag restoration or physical native defeat. No statewrites, helpers/fullstage/install; geometry first native qualification pending.',allow_interactive=True)
    own=[p for p in O.rglob('*')if p.is_file()]
    print(json.dumps(dict(mode=a.mode,prepared=True,ROM_SHA256=PIN,files=len(own),bytes=sum(p.stat().st_size for p in own))))

if __name__=='__main__':main()
