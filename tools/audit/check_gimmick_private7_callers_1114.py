"""Read-only current Gimmick private7 owner/reader/retirement proposal gates."""
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import replay_gimmick_world_sprite_images_1114 as F
import check_mr_gimmick_full11_current_1114 as Stage
import check_gimmick_world_sprite_images_1114 as Art
import check_bub_current_budget_1113 as Frames

W,N=F.W,F.N


def run(raw):
    assert sha256(raw).hexdigest()==F.PIN
    m=Stage.cold(raw);b=m.bundle;cases=0;mode=W.address(b,'X5ChrMode');banks=W.address(b,'CurrentCHRBank')
    for owner in range(256):
        if owner==26:continue
        for name in('GmGraphics','GmDraw','GmPortrait'):
            mm=N.fork(m);N.put(mm,SelectedCharacter=owner)
            before=(bytes(mm[0x5c00:0x5c80]),bytes(mm[512:768]),bytes(mm[mode:mode+15]),bytes(mm[banks:banks+12]))
            W.clear_logs(mm);N.invoke(mm,name,a=83,x=71,y=109,p=0xe1)
            assert before==(bytes(mm[0x5c00:0x5c80]),bytes(mm[512:768]),bytes(mm[mode:mode+15]),bytes(mm[banks:banks+12]))
            assert not[(at,value)for at,value in mm.writes if 0x5120<=at<=0x5130]
            cases+=1
    # Real selected-owner proof for the other current temporal7 publisher.
    # DkHostDraw maps its C-window before tail-jumping; generic invoke only
    # supplies A transport. Reproduce that real map for this foreign leaf unit.
    m.raw_page(2,140);N.put(m,CurrentBankC=140)
    W.clear_logs(m);N.invoke(m,'DkDraw',a=83,x=71,y=109,p=0x61)
    assert not[(at,value)for at,value in m.writes if at in(mode+7,banks+7,0x5127)]
    # Declared old Gimmick7 lease fixture followed by all real family Select
    # choices. A cleared mode may retain a harmless legacy low byte in menus;
    # each real Start must rebuild it before any ordinary gameplay consumer.
    menu_states=[]
    for cycles in(1,2,3,4):
        with patch.object(N,'Bus',W.ControllerBus):menu=W.UI.seed(b,0)
        for pad in F.bindings(raw)['navigation']:W.UI.key(menu,pad)
        assert N.get(menu,'SelectedCharacter')==26
        N.invoke(menu,'X5SetPhysicalChr',a=50,x=3,y=7)
        assert menu[mode+7]==131
        for _ in range(cycles):W.UI.key(menu,32)
        next_owner=N.get(menu,'SelectedCharacter');next_name=W.UI.menu_name(menu)[0]
        assert next_owner!=26
        N.invoke(menu,'X5PublishChr',a=0,x=0,y=0)
        menu_state=dict(from_owner=26,to_owner=next_owner,to_name=next_name,Select_cycle=cycles,
            old_page=818,old_window=7,new_mode7=menu[mode+7],new_published_page7=menu.chr_latches[7])
        visible_windows=sorted({(menu[513+4*i]&1)*4+(menu[513+4*i]>>6)for i in range(64)if menu[512+4*i]<240})
        assert 7 not in visible_windows,menu_state
        menu_state['visible_menu_OAM_windows']=visible_windows
        s=W.UI.key(menu,16)
        N.invoke(menu,'NativeRareGameMenuRoutineCore::ChkContinue',a=s['A'],x=s['X'],y=s['Y'],p=s['P'])
        N.invoke(menu,'PauseRoutine',a=0)
        for tick in range(700):
            if tuple(N.get(menu,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
            menu.controller_pad=0;Frames.frame(menu,cold=True)
        else:raise AssertionError(('Real family constructor after lease fixture',next_name))
        for _ in range(4):menu.controller_pad=0;Frames.frame(menu,whole_pass=True)
        assert menu[mode+7]==0 and menu.chr_latches[7]==21,(next_name,menu[mode+7],menu.chr_latches)
        menu_state['post_start_mode7']=menu[mode+7];menu_state['post_start_page7']=menu.chr_latches[7]
        menu_states.append(menu_state)
    # Structural bounds in actual current code: GmStarRecord validates66;
    # body validates22; effect nibble>>2 indexes only0..3; trail validates21.
    star=W.location(b,'GmStarRecord');assert raw[star:star+2]==bytes.fromhex('c942')
    begin,end=W.location(b,'GmDraw'),W.location(b,'GmArtStart')
    # Draw and art occupy different physical banks; exact routine ends at its
    # restored-AXYP RTS within its source-bounded512B region.
    draw=raw[begin:begin+512]
    for code in('c915','c916','4a4a4a4a4a4a0a'):
        assert bytes.fromhex(code)in draw,('Current reader bound',code)
    # The three candidate metadata-reader routes are private and source-bound.
    src=F.R/'src/gimmick_render.s';text=src.read_text()
    assert text.count('jsr GmEmitRecord')==2 and text.count('GmFar GmEmitRecord,24')==1 and text.count('jmp GmEmitRecord')==1
    return dict(ROM_SHA256=F.PIN,defensive_foreign_selected_cases=cases,
        private_overlay_OAM_modes_and_banks_exact=True,no_foreign_CHR_publication=True,
        current_DK28_publisher_rejects_Gimmick26=True,
        actual_UI_retirement_fixtures=menu_states,
        actual_current_reader_bounds=dict(hero=22,star=66,effect=4,history=21),
        current_renderer_source_SHA256=sha256(src.read_bytes()).hexdigest(),
        proposal_flag_liveness='Retargeted tile LDA changes only N; STA does not read it, following INY and LDA attribute overwrite NZ before any branch. Carry/V unaffected.',
        candidate_not_composed=True,allocation_granted=False,Mesen_run=False,outputs=0)


if __name__=='__main__':
    raw=F.ROM.read_bytes()
    def forbid(*args,**kwargs):raise RuntimeError('Read-only private7 audit attempted file output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid):q=run(raw)
    print(json.dumps(q,separators=(',',':')),flush=True)
