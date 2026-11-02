"""Bind source-epoch controls to the real cold-confirm path and passive observer."""
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
    ap=argparse.ArgumentParser();ap.add_argument('--identity',choices=['bub','bob'],default='bub');a=ap.parse_args()
    assert sha(ROM)==PIN
    observer=BACK/('native-observer-'+a.identity+'-1102-v2.lua');observer_receipt=BACK/'native-observer-prepared-1102-v2.json'
    oq=json.loads(observer_receipt.read_text());assert oq['ROM_sha256']==PIN
    b=scoped_load(ROM);full=scoped_load(R/'build/wwf-death-1102-v2/candidate.nes')
    ordered=O/'ordered-input-v3/native-menu-plans.json';plan=copy.deepcopy(json.loads(ordered.read_text())['plans'][a.identity+'-start'])
    plan.update(maxFrames=4200,ROM_sha256=PIN)
    at=location(b,'GroundPaletteData');plan['restore']=list(b['raw'][at+24:at+27])
    source=R/'tools/audit/bub_menu_qualification_1102_v2.lua';body=source.read_text()
    extension=R/'tools/audit/bub_native_controls_1102_v1.lua'
    anchor="local log=assert(io.open(OUTPUT..'observations.csv','w'))";assert body.count(anchor)==1
    body=body.replace(anchor,extension.read_text()+'\n'+anchor)
    old=" elseif phase=='route'and age<6 then for _,key in ipairs(Q.steps[at].keys)do keys[key]=true end end"
    new=" elseif phase=='route'and age<6 then for _,key in ipairs(Q.steps[at].keys)do keys[key]=true end\n elseif phase=='controls'then for _,key in ipairs(control_keys())do keys[key]=true end end"
    assert body.count(old)==1;body=body.replace(old,new)
    old=" if done then return end;frame=frame+1;age=age+1";assert body.count(old)==1
    body=body.replace(old,old+';BUB_OBSERVER.frame(control_label(),control_step)')
    old="  shot('active-owner');finish()\n end";assert body.count(old)==1
    body=body.replace(old,"  controls_begin()\n elseif phase=='controls'then controls_tick(finish)\n end")
    names=['CrossoverMenuState','CrossoverMenuIndex','OperMode','OperMode_Task','SelectedCharacter','FmGroups','VRAM_Buffer1_Offset','VRAM_Buffer1','GameEngineSubroutine','Player_PageLoc','Player_X_Position','Player_Y_Position','Player_State','NumberofLives']
    prefix='\n'.join(f'L[{json.dumps(n)}]={address(full,n)}'for n in names)+'\nlocal Q='+N.lua(plan)+'\n'
    controller=prefix+observer.read_text()+'\n'+body
    for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in controller
    refs={Path(__file__),source,extension,observer,observer_receipt,ordered,O/'combined-visible.json',O/'visible-cold-native-v6.json',R/'docs/qa/allocations/bubble-visible-1102-v6.json'}
    output=O/('native-source-'+a.identity+'-controls')
    prepare(output,ROM,controller,refs,expected=PIN,timeout=210,
        scope='Actual cold'+a.identity+' simultaneousSelect/confirm and authenticated Fresh, then source-epoch idle/right/left/43pxjump/freshBbubble/rest. Passive original source+bothheaders/hardwareCHR441/RGB/OAM observer; trap/pop/release reported only when observed. FourPNG, no statewrites/fullstage/install claim. Observerfirstnativeuse not yet runtime-qualified.',allow_interactive=True)
    own=[p for p in O.rglob('*')if p.is_file()];assert sum(p.stat().st_size for p in own)<32000000 and len(own)<=128
    print(json.dumps(dict(prepared=output.relative_to(R).as_posix(),ROM_SHA256=PIN,native=False,files=len(own),bytes=sum(p.stat().st_size for p in own))))

if __name__=='__main__':main()
