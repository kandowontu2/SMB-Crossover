"""Record v6 cold visual scope and bind only the four affected regressions."""
from pathlib import Path
import argparse,copy,json,re,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import prepare_bub_menu_qualification_1102_v2 as N
O=N.O;ROM=O/'combined-visible.nes';PIN='4395ed57aaeccfd05ca743fc603f0d1b69b4991b072b55e68b49507cffc8c2ab'
MODES=['bt-start','cf-start','ex-regression','sh-regression']

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--modes',default=','.join(MODES));a=ap.parse_args()
    modes=a.modes.split(',');assert set(modes)<=set(MODES)
    own=[p for p in O.rglob('*')if p.is_file()]
    assert len(own)+3*sum(not(O/('native-visible-'+mode)).exists()for mode in modes)+int(not(O/'visible-cold-native-v6.json').exists())<=128,'Root scoped cleanup required before new packets'
    assert sha(ROM)==PIN and sha(ROM.with_suffix('.dbg'))=='a54fadb57dbd7bb620a6b37a0ba8324cecc698c32a0dc5e0cde5855a347f41b4'
    manifest=O/'combined-visible.json';grant=R/'docs/qa/allocations/bubble-visible-1102-v6.json'
    q=json.loads(manifest.read_text());assert q['ROM_SHA256']==PIN and q['private_native_only']
    for path,digest in q['bindings'].items():assert sha(R/path)==digest,path
    rows=[];inputs=[Path(__file__),ROM,manifest,grant]
    for label,folder,frames in[('Bub','native-visible-bub-cold',700),('Bob','native-visible-bob-cold',660)]:
        capture=O/folder/'capture';result=json.loads((capture/'result.json').read_text());binding=json.loads((capture/'binding.json').read_text())
        assert result['passed'] and result['gameplay_launch'] and not result['full_stage'] and result['frames']==frames
        assert binding['exit_code']==0 and binding['ROM_sha256']==PIN
        rows.append(dict(character=label,controller_only=True,frames=frames,Fresh_identity_ready_active8=True,
            actual_blue_backdrop_HUD_attributes_name_WORLD_TIME_source_RGB_passed=True,root_visual_review_passed=True))
        inputs +=[O/folder/'ready.json',capture/'result.json',capture/'binding.json',capture/'active-owner.png']
    receipt=O/'visible-cold-native-v6.json'
    record=dict(passed=True,private_visual_and_cold_only=True,ROM_SHA256=PIN,installed=False,production_admitted=False,
        source_controls_combat_Easy_stomp_full11_qualified=False,helpers_added=False,actual_cold_runs=rows,
        prior00971_global_palette_negative_preserved=True,
        next='Source controls/bubble contact/Easy policy/terrain/full1-1 and affected BT/CF/Ex/Sh native regressions',
        bindings={p.relative_to(R).as_posix():sha(p)for p in inputs})
    data=(json.dumps(record,indent=2)+'\n').encode()
    if receipt.exists():assert receipt.read_bytes()==data
    else:receipt.write_bytes(data)
    b=scoped_load(ROM);full=scoped_load(R/'build/wwf-death-1102-v2/candidate.nes')
    ordered=O/'ordered-input-v3/native-menu-plans.json';plans=json.loads(ordered.read_text())['plans'];outputs=[]
    for mode in modes:
        refs={Path(__file__),manifest,grant,receipt}
        if mode in['bt-start','cf-start']:
            plan=copy.deepcopy(plans[mode]);at=location(b,'GroundPaletteData');plan['restore']=list(b['raw'][at+24:at+27])
            source=R/'tools/audit/bub_menu_qualification_1102_v2.lua'
            names=['CrossoverMenuState','CrossoverMenuIndex','OperMode','OperMode_Task','SelectedCharacter','FmGroups','VRAM_Buffer1_Offset','VRAM_Buffer1','GameEngineSubroutine']
            controller='\n'.join(f'L[{json.dumps(n)}]={address(b,n)}'for n in names)+'\nlocal Q='+N.lua(plan)+'\n'+source.read_text()
            refs|={source,Path(N.__file__),ordered};timeout=120;scope=plan['scope']
        else:
            source=R/'build/excitebike-pose-1101-v3'/('native5'if mode=='ex-regression'else'shinobi-smoke')/'controller.lua'
            text=source.read_text();names=set(re.findall(r"\br\('([^']+)'\)",text))|set(re.findall(r"L\['([^']+)'\]",text))
            if mode=='sh-regression':names.update('CurrentCHRBank X5ChrMode SsChrActive X5WideChrActive ReloadCHRBank CurrentOAMOffset Mirror_PPUCTRL RgOamFirst RgOamUsed RgOamRotation'.split())
            controller='\n'.join(f'L[{json.dumps(n)}]={address(full,n)}'for n in sorted(names))+'\n'+text
            refs.add(source);timeout=150 if mode=='ex-regression'else 90
            scope='Unchanged delivered '+mode+' native controller, explicit current L globals, necessary shared loader/shot/bbox regression; no full-stage claim.'
        output=O/('native-visible-'+mode)
        prepare(output,ROM,controller,refs,expected=PIN,timeout=timeout,
            scope='Exact4395 v6 private source palette/HUD successor; current source-only dependencies. '+scope,allow_interactive=True)
        outputs.append(output.relative_to(R).as_posix())
    own=[p for p in O.rglob('*')if p.is_file()];assert sum(p.stat().st_size for p in own)<32000000 and len(own)<=128
    print(json.dumps(dict(prepared=outputs,ROM_SHA256=PIN,cold_visual_native_passed=True,files=len(own),bytes=sum(p.stat().st_size for p in own))))

if __name__=='__main__':main()
