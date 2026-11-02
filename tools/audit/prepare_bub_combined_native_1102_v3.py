"""Bind current packets without superseded unexecuted-scaffold dependencies."""
from pathlib import Path
import argparse,copy,json,re,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import prepare_bub_menu_qualification_1102_v2 as N
O=N.O;ROM=O/'combined2.nes'
PIN='00971c9fa4906440e1f52d37ca76b7adde287e902a31e72982dee171b35bfa60'
MODES=['bob-cold','bt-start','cf-start','ex-regression','sh-regression']

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--modes',default=','.join(MODES));a=ap.parse_args()
    modes=a.modes.split(',');assert set(modes)<=set(MODES)
    assert sha(ROM)==PIN and sha(ROM.with_suffix('.dbg'))=='a54fadb57dbd7bb620a6b37a0ba8324cecc698c32a0dc5e0cde5855a347f41b4'
    manifest=O/'combined.json';grant=R/'docs/qa/allocations/bubble-shared-native-1102-v5.json'
    repair=O/'combined-metadata-repair-v2.json';q=json.loads(manifest.read_text())
    assert q['ROM_SHA256']==PIN and q['native_candidate_granted'] and not q['installed']
    assert sha(grant)==q['grant_SHA256'] and json.loads(grant.read_text())['private_native_candidate_allowed']
    b=scoped_load(ROM);full=scoped_load(R/'build/wwf-death-1102-v2/candidate.nes')
    ordered=O/'ordered-input-v3/native-menu-plans.json';plans=json.loads(ordered.read_text())['plans']
    outputs=[];same_bob=None
    for mode in modes:
        refs={Path(__file__),manifest,grant,repair}
        if mode in['bob-cold','bt-start','cf-start']:
            plan=copy.deepcopy(plans['bob-start'if mode=='bob-cold'else mode])
            at=location(b,'GroundPaletteData');plan['restore']=list(b['raw'][at+24:at+27])
            source=R/'tools/audit/bub_menu_qualification_1102_v2.lua'
            names=['CrossoverMenuState','CrossoverMenuIndex','OperMode','OperMode_Task','SelectedCharacter','FmGroups','VRAM_Buffer1_Offset','VRAM_Buffer1','GameEngineSubroutine']
            controller='\n'.join(f'L[{json.dumps(n)}]={address(b,n)}'for n in names)+'\nlocal Q='+N.lua(plan)+'\n'+source.read_text()
            refs|={source,Path(N.__file__),ordered};timeout=120
            scope=plan['scope']+' Cold confirm/active owner only; no source combat or full-stage claim.'
            if mode=='bob-cold':
                previous=O/'native-combined2-bob-cold/controller.lua'
                expected=json.loads((previous.parent/'ready.json').read_text())['bindings'][str(previous.resolve())]
                assert sha(previous)==expected
                import hashlib
                assert hashlib.sha256(controller.encode()).hexdigest()==expected
                same_bob=expected
        else:
            relative='build/excitebike-pose-1101-v3/'+('native5'if mode=='ex-regression'else'shinobi-smoke')+'/controller.lua'
            source=R/relative;text=source.read_text()
            names=set(re.findall(r"\br\('([^']+)'\)",text))|set(re.findall(r"L\['([^']+)'\]",text))
            if mode=='sh-regression':names.update('CurrentCHRBank X5ChrMode SsChrActive X5WideChrActive ReloadCHRBank CurrentOAMOffset Mirror_PPUCTRL RgOamFirst RgOamUsed RgOamRotation'.split())
            controller='\n'.join(f'L[{json.dumps(n)}]={address(full,n)}'for n in sorted(names))+'\n'+text
            refs.add(source);timeout=150 if mode=='ex-regression'else 90
            scope='Unchanged delivered '+mode+' controller, explicit current L globals, necessary shared loader/shot/bbox regression; no full-stage claim.'
        for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in controller
        output=O/('native-combined3-'+mode)
        prepare(output,ROM,controller,refs,expected=PIN,timeout=timeout,
            scope='Exact00971ROM, exactpassed a54f DBG, current source-only dependencies. '+scope,allow_interactive=True)
        ready=json.loads((output/'ready.json').read_text())
        assert all('native-combined-'not in name for name in ready['bindings'])
        outputs.append(output.relative_to(R).as_posix())
    receipt=dict(prepared=True,executed=False,ROM_changed=False,ROM_SHA256=PIN,
        packets=outputs,Bob2_controller_exact_SHA256=same_bob,
        no_superseded_scaffold_or_archive_dependencies=True,native=False,installed=False,
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),manifest,grant,*[R/p/'ready.json'for p in outputs]]})
    dest=O/'combined-native-packets-v3.json';assert not dest.exists()
    dest.write_text(json.dumps(receipt,indent=2)+'\n')
    own=[p for p in O.rglob('*')if p.is_file()]
    assert sum(p.stat().st_size for p in own)<32000000 and len(own)<=128
    print(json.dumps(dict(prepared=outputs,bytes=sum(p.stat().st_size for p in own),files=len(own))))

if __name__=='__main__':main()
