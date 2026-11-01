"""Read-only installed-WIP menu access and practical input-edge investigation."""
from pathlib import Path
import copy,hashlib,itertools,json,sys,traceback
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
import check_hogan_current_bounded_v1 as C
import ff_wram_host_controls_v7 as H
from check_tmnt_render_oa import address
OUT=ROOT/'build/karnov-menu-access-1101-v3';BASE=ROOT/'build/karnov-host-resource-base-1101-v1'
INSTALLED=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
EXPECTED='be751275d00757ecaa51defcd2ccd5ea235921aa4b1f34337fa6c5c6e1877962'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    OUT.mkdir(exist_ok=True);q=dict(passed=False,read_only=True,native_emulator=False,installed_modified=False)
    try:
        assert sha(INSTALLED)==EXPECTED
        original=H.C.qualified(BASE/'candidate.nes');base_sha=sha(BASE/'candidate.nes');dbg_sha=sha(BASE/'candidate.dbg')
        b=copy.deepcopy(original);b['raw']=INSTALLED.read_bytes();seen=set();mismatches=set();equivalent_row_bound=set();calls=0
        def invoke(m,name,**kwargs):
            nonlocal calls
            c=H.start(m,name,**kwargs)
            def observe(mem,c,i):
                if c.pc<0x8000:return
                tag=mem.rawtags[(c.pc-0x8000)//8192]
                assert tag&128,'Cold menu unexpectedly executed RAM cache'
                at=16+(tag&127)*8192+(c.pc&8191)
                seen.add(at)
                if b['raw'][at:at+3]!=original['raw'][at:at+3]:
                    if at==0x3b910 and b['raw'][at:at+2]==bytes([0xc9,108])and original['raw'][at:at+2]==bytes([0xc9,111]):
                        # Installed36-row versus current37-row guard. All cold
                        # menu offsets are below108, with identical CMP NZC.
                        assert c.a<108
                        equivalent_row_bound.add(c.a)
                    else:mismatches.add(at)
            result,low=H.finish(m,c,observe);calls+=1;return result
        def fresh():
            # Real native PrimaryGameSetup, then the ordinary title/menu input
            # routine. No character/alt is assigned to reach Rygar/Karnov.
            m=C.fresh(b)
            H.put(m,CrossoverMenuState=0,CrossoverMenuButtons=0,CrossoverTitleDrawn=0,CrossoverOptionsFocus=0,CrossoverMenuIndex=0)
            return m
        def tick(m,p1=0,p2=0):
            state=H.get(m,'CrossoverMenuState')
            # Queue consumed between test inputs, matching a native frame's
            # visible/forced-blank menu phases; no timing claim is made.
            H.put(m,SavedJoypad1Bits=p1,SavedJoypad2Bits=p2,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,Mirror_PPUMASK=0 if state in [1,3,5,7]else 24)
            return invoke(m,'CrossoverMenuInput')
        def roster(m):
            tick(m);tick(m,16);assert H.get(m,'CrossoverMenuState')==1
            tick(m);assert H.get(m,'CrossoverMenuState')==2
            tick(m)
        def tap(m,key,pad=1):
            c=tick(m,key if pad==1 else 0,key if pad==2 else 0);tick(m);return c
        def snapshot(m):
            c=invoke(m,'FmPending')
            return dict(menu=H.get(m,'CrossoverMenuState'),slot=H.get(m,'CrossoverMenuIndex'),character=H.get(m,'SelectedCharacter'),alternate=H.get(m,'FmAlts')&1,pending=bool(c.p&1))
        ordinary=0;launches=0;routes={};contexts=[]
        # Both controllers, Easy/Hard, outline options, Fresh/Continue and both
        # A/Start. Held-input history is carried through each ordinary call.
        for pad,hard,outlines,continued,confirm in itertools.product([1,2],[0,1],[0,1],[0,128],[16,128]):
            m=fresh();H.put(m,CrossoverBehaviorVersion=hard,PlayerOutlinesOff=outlines)
            roster(m);H.put(m,CrossoverContinue=continued)
            tap(m,2,pad);assert snapshot(m)['slot']==7 and H.get(m,'SelectedCharacter')==7
            tap(m,32,pad);s=snapshot(m)
            assert s==dict(menu=2,slot=7,character=34,alternate=1,pending=False),s
            c=tick(m,confirm if pad==1 else 0,confirm if pad==2 else 0)
            assert H.get(m,'CrossoverMenuState')==0 and H.get(m,'SelectedCharacter')==34 and H.get(m,'FmAlts')&1
            assert c.a&16
            ordinary+=1;launches+=1
        # Alternate navigation and rehighlighting retain Karnov's bit before
        # returning to the title. Every step is a real menu input call.
        for name,path in [('left',[2]),('seven-right',[1]*7),('up-left-down',[8,2,4])]:
            m=fresh();roster(m)
            for key in path:tap(m,key)
            s=snapshot(m);routes[name]=s
            assert s['slot']==7,(name,s)
            tap(m,32);assert H.get(m,'SelectedCharacter')==34
            tap(m,1);tap(m,2);assert snapshot(m)['character']==34
        # Long holds do not oscillate the alternate; two separate Select
        # presses deliberately return to Rygar.
        m=fresh();roster(m);tap(m,2)
        for i in range(40):tick(m,32)
        held=snapshot(m);assert held['character']==34
        tick(m);tap(m,32);back=snapshot(m);assert back['character']==7
        tap(m,32);again=snapshot(m);assert again['character']==34
        contexts.append(dict(case='select-hold-release-toggle',held=held,second_press=back,third_press=again))
        # Practical input cases: confirmation has priority over alternate
        # switching, and B/title rebuild discards all folded-family bits.
        for confirm in [16,128]:
            m=fresh();roster(m);tap(m,2);c=tick(m,32|confirm)
            s=snapshot(m);assert s['menu']==0 and s['character']==7 and not s['alternate']
            contexts.append(dict(case='simultaneous-select-'+('start'if confirm==16 else'a'),result=s,returned_A=c.a))
        m=fresh();roster(m);tap(m,2);tap(m,32);before=snapshot(m)
        tap(m,64);assert H.get(m,'CrossoverMenuState')==0
        tick(m,16);tick(m);tick(m);after=snapshot(m)
        assert after['slot']==7 and after['character']==7 and after['alternate']==0
        contexts.append(dict(case='B-title-Start-reentry-clears-Karnov',before=before,after=after))
        # A Select edge arriving while the roster is still in forced-blank
        # BuildScreen is consumed there; hold into the ready state has no new
        # edge. Releasing/pressingSelect again works.
        m=fresh();tick(m);tick(m,16)
        tick(m,32);state=snapshot(m);assert state['menu']==2
        tick(m,32);assert H.get(m,'FmAlts')&1==0
        contexts.append(dict(case='Select-during-menu-construction-consumed',result=snapshot(m)))
        assert sha(BASE/'candidate.nes')==base_sha and sha(BASE/'candidate.dbg')==dbg_sha and sha(INSTALLED)==EXPECTED
        assert not mismatches,('Installed executed menu opcode differs from symbols',[hex(x)for x in sorted(mismatches)[:12]])
        q.update(passed=True,installed_ROM_sha256=EXPECTED,symbol_ROM_sha256=base_sha,symbol_dbg_sha256=dbg_sha,executed_menu_instruction_locations_verified_equal=len(seen)-bool(equivalent_row_bound),equivalent_36_37_row_guard_inputs=sorted(equivalent_row_bound),cold_menu_calls=calls,ordinary_fresh_continue_Easy_Hard_controller_A_Start_launches=launches,ordinary_contexts=ordinary,navigation_routes=routes,practical_cases=contexts,normal_input_instruction='On the character-select screen, highlight RYGAR, tap and release Select, verify KARNOV is highlighted, then press A or Start separately.',findings=[f'Separate Select then A/Start successfully launches Karnov in all{ordinary} tested ordinary modes.','Fresh simultaneous Select+A/Start confirms Rygar before the Select toggle; no Karnov launch occurs.','B/title/reentry clears FmAlts and restores Rygar at the same saved slot7; Select must be pressed again.','A Select edge during BuildScreen is consumed; a continued hold is not replayed after the menu becomes ready.','Holding Select on the ready roster toggles once and stays Karnov; a second separate press toggles back to Rygar.'],scope='Read-only CPU execution of actual installed be7512 ROM menu instructions using current stable5890debugsymbols. Executed opcode locations match except the known108/111row-range immediate, whose actual cold inputs have identical CMP flags. No runtimeID injection to reach Karnov, no ROM/source writes, native emulator/raster/controller-device proof or claim that the user report is resolved. Practical edge/reentry cases may explain inability but actual user input path remains unknown.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),INSTALLED,BASE/'candidate.nes',BASE/'candidate.dbg',ROOT/'tools/audit/check_hogan_current_bounded_v1.py',ROOT/'tools/audit/ff_wram_host_controls_v7.py',ROOT/'tools/audit/arthur_cache_host_controls_v1.py',ROOT/'build/hogan-thomas-current/src/character_select.s',BASE/'full_roster_menu.s']}
    (OUT/'result.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','practical_cases']}));assert q['passed']
if __name__=='__main__':main()
