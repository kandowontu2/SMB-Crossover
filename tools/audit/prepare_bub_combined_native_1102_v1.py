"""Bind small cold-confirm and affected-family packets; root alone runs them."""
from pathlib import Path
import copy,json,re,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
import prepare_bub_menu_qualification_1102_v2 as N

O=N.O;ROM=O/'combined.nes'
PIN='00971c9fa4906440e1f52d37ca76b7adde287e902a31e72982dee171b35bfa60'

def main():
    assert sha(ROM)==PIN
    manifest=O/'combined.json';q=json.loads(manifest.read_text())
    assert q['ROM_written'] and q['native_candidate_granted'] and not q['menu_admitted']
    assert q['ROM_SHA256']==PIN and q['WWF3B_preserved']
    for path,digest in q['bindings'].items():assert sha(R/path)==digest,path
    grant=R/'docs/qa/allocations/bubble-shared-native-1102-v5.json'
    assert sha(grant)==q['grant_SHA256'] and json.loads(grant.read_text())['private_native_candidate_allowed']
    b=scoped_load(ROM);full=scoped_load(R/'build/wwf-death-1102-v2/candidate.nes')
    assert b['raw'][16+66*8192+0xd64]==0x18
    ordered=O/'ordered-input-v3/native-menu-plans.json'
    plans=json.loads(ordered.read_text())['plans'];source=R/'tools/audit/bub_menu_qualification_1102_v2.lua'
    body=source.read_text();packets=[]
    for mode,label in[('bub-start','bub-cold'),('bob-start','bob-cold'),('bt-start','bt-start'),('cf-start','cf-start')]:
        plan=copy.deepcopy(plans[mode]);at=location(b,'GroundPaletteData');plan['restore']=list(b['raw'][at+24:at+27])
        names=['CrossoverMenuState','CrossoverMenuIndex','OperMode','OperMode_Task','SelectedCharacter','FmGroups','VRAM_Buffer1_Offset','VRAM_Buffer1','GameEngineSubroutine']
        prefix='\n'.join(f'L[{json.dumps(n)}]={address(b,n)}'for n in names)+'\nlocal Q='+N.lua(plan)+'\n'
        output=O/('native-combined-'+label)
        prepare(output,ROM,prefix+body,{Path(__file__),source,Path(N.__file__),manifest,grant,ordered},expected=PIN,timeout=120,
            scope='Exact1966 plus granted frontend/backend private candidate. '+plan['scope']+' Initial cold confirm only; separate source controls/hardware observer follows.',allow_interactive=True)
        packets.append(output.relative_to(R).as_posix())
    for label,path,timeout,scope in[
        ('ex-regression','build/excitebike-pose-1101-v3/native5/controller.lua',150,'Unchanged actual native5 Ex controller: cold menu, original motor/61px jump/landing and hardware CHR/palette/HUD/alignedOAM. Necessary common dispatcher/loader regression; no full-stage claim.'),
        ('sh-regression','build/excitebike-pose-1101-v3/shinobi-smoke/controller.lua',90,'Unchanged delivered Sh cold/idle/walk/OAM controller. Necessary shot/bbox shared-gate regression; no full-stage claim.')]:
        original=R/path;text=original.read_text()
        names=set(re.findall(r"\br\('([^']+)'\)",text))|set(re.findall(r"L\['([^']+)'\]",text))
        if label.startswith('sh'):
            names.update('CurrentCHRBank X5ChrMode SsChrActive X5WideChrActive ReloadCHRBank CurrentOAMOffset Mirror_PPUCTRL RgOamFirst RgOamUsed RgOamRotation'.split())
        assert names
        prefix='\n'.join(f'L[{json.dumps(n)}]={address(full,n)}'for n in sorted(names))+'\n'
        for bad in['emu.write','emu.loadSavestate','emu.reset','emu.loadState']:assert bad not in text
        output=O/('native-combined-'+label)
        prepare(output,ROM,prefix+text,{Path(__file__),original,manifest,grant},expected=PIN,timeout=timeout,
            scope=scope+' Explicit L addresses, no Downloads sidecars or emulated writes.',allow_interactive=True)
        packets.append(output.relative_to(R).as_posix())
    result=dict(prepared=True,executed=False,native=False,ROM_SHA256=PIN,packets=packets,
        no_ROM_changes=True,root_owns_Mesen=True,production_admitted=False,installed=False,
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),ROM,manifest,grant,*[R/p/'ready.json'for p in packets]]})
    dest=O/'combined-native-packets-v1.json';assert not dest.exists()
    dest.write_text(json.dumps(result,indent=2)+'\n')
    own=[p for p in O.rglob('*')if p.is_file()]
    assert sum(p.stat().st_size for p in own)<32000000 and len(own)<=128
    print(json.dumps(dict(prepared=packets,ROM_SHA256=PIN,bytes=sum(p.stat().st_size for p in own),files=len(own))))

if __name__=='__main__':main()
