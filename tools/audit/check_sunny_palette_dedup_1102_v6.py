"""Qualify palette-cache/queue semantics, then prepare native full-stage replay."""
import itertools,json
from pathlib import Path
import audit_current_menu_indicators_1102_v1 as A
import check_hogan_current_bounded_v1 as M
from check_tmnt_render_oa import address
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/sunny-palette-qualification-1102-v6'
ROM=R/'build/sunny-palette-dedup-1102-v5/candidate.nes'

def main():
    O.mkdir(exist_ok=True);original=A.bundle();original['raw']=(R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes').read_bytes()
    new=dict(original,raw=ROM.read_bytes());seeds=[M.fresh(b)for b in [original,new]];cases=0;duplicates=0
    for engine,form,active,star,cache,offset,carry in itertools.product([8,9,10],range(3),range(2),range(2),[0,1,255],[0,78],range(2)):
        pair=[]
        for seed in seeds:
            m=M.fork(seed);M.put(m,SelectedCharacter=23,GameEngineSubroutine=engine,PlayerStatus=form,GuestPowerupActive=active,GuestPowerupDisplay=form,StarInvincibleTimer=star,SunnyPalette=cache,VRAM_Buffer1_Offset=offset)
            out=M.invoke(m,'SunnyColorsIntegrated',p=0x30|carry)
            pair.append((m,out))
        m,out=pair[1];valid=cache if engine==9 else 255;target=int(form==2)
        append=not star and valid!=target and offset<78
        wanted_cache=(target if append else valid)
        assert M.get(m,'SunnyPalette')==wanted_cache and M.get(m,'VRAM_Buffer1_Offset')==offset+6*append
        if append:
            at=address(new,'VRAM_Buffer1')+offset
            assert [m[at+i]for i in range(7)]==[63,17,3,4,42 if form==2 else 38,54,0]
        if engine!=9:
            old,oldout=pair[0]
            assert [out[k]for k in ['A','X','Y','P']]==[oldout[k]for k in ['A','X','Y','P']]
            assert M.get(old,'SunnyPalette')==M.get(m,'SunnyPalette') and M.get(old,'VRAM_Buffer1_Offset')==M.get(m,'VRAM_Buffer1_Offset')
        if engine==9 and not star and offset==0:
            before=M.get(m,'VRAM_Buffer1_Offset');M.invoke(m,'SunnyColorsIntegrated',p=0x30|carry)
            assert M.get(m,'VRAM_Buffer1_Offset')==before;duplicates+=1
        cases+=1
    q=dict(passed=True,native=False,cases=cases,duplicate_calls_suppressed=duplicates,ROM_sha256=sha(ROM),scope='Actual assembled SunnyColorsIntegrated; grow/non-grow, all3forms, active display, star, cache states, full buffer and C0/1. Non-grow complete AXY/P return equality. No shared or foreign ROM byte changed.',bindings={str(p):sha(p)for p in [Path(__file__),R/'tools/audit/prepare_sunny_palette_dedup_1102_v5.py',ROM]})
    (O/'CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
    source=R/'build/sunny-current-full11-1102-v1/native/controller.lua';text=source.read_text().replace('22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19',sha(ROM))
    deps=[R/'tools/playthroughs'/n for n in ['sunny_11_v3.lua','sunny_11_v1.lua','mario_luigi_scrooge_policy.lua','mario_luigi_scrooge_nav.lua']]
    prepare(O/'native',ROM,text,[Path(__file__),source,O/'CPU.json',*deps],expected=sha(ROM),timeout=240,scope='Sunny same cold Hard controller-only mushroom/full1-1 on private palette-dedup candidate; original failing actual DMA/NMI deadline assertions unchanged.',allow_interactive=True)
if __name__=='__main__':main()
