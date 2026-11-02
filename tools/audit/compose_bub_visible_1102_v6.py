"""Compose the exact granted palette/HUD successor and cold native packets."""
from pathlib import Path
import copy,hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from plan_bub_combined_frontend_1102_v1 import fold_patches
import prepare_bub_menu_qualification_1102_v2 as N
O=N.O;BACK=R/'build/bubble-bobble-source-1101-v1'
BASE=O/'combined2.nes';PIN='00971c9fa4906440e1f52d37ca76b7adde287e902a31e72982dee171b35bfa60'
NEW='4395ed57aaeccfd05ca743fc603f0d1b69b4991b072b55e68b49507cffc8c2ab'
MPIN='eb4050468e969dd1dc99783871c60b539e40be083b2a4528496c2b22ebe420eb'

def main():
    manifest=BACK/'native-visible-successor-00971.json';freeze=BACK/'native-visible-qualified-1102-v6.json'
    grant=R/'docs/qa/allocations/bubble-visible-1102-v6.json'
    assert sha(BASE)==PIN and sha(manifest)==MPIN
    g=json.loads(grant.read_text());m=json.loads(manifest.read_text());f=json.loads(freeze.read_text())
    assert g['granted'] and g['private_native_testing_only'] and not g['production_admitted']
    assert g['base_ROM_SHA256']==PIN and g['candidate_SHA256']==NEW and g['proposal_SHA256']==MPIN
    assert f['manifest_SHA256']==MPIN and m['base_ROM_SHA256']==PIN
    archive=R/f['archive'];assert sha(archive)==f['archive_SHA256']
    with zipfile.ZipFile(archive)as z:
        assert set(z.namelist())==set(f['files']) and z.testzip()is None
        for path,row in f['files'].items():
            assert sha(R/path)==row['SHA256'],path
            assert hashlib.sha256(z.read(path)).hexdigest()==row['SHA256'],path
    cpu=R/m['CPU_receipt']['path'];assert sha(cpu)==m['CPU_receipt']['SHA256'] and json.loads(cpu.read_text())['passed']
    raw=BASE.read_bytes();out,owned,changed=fold_patches(raw,m['patches'])
    assert len(m['patches'])==10 and len(changed)==g['actual_changed_bytes']==220
    assert hashlib.sha256(out).hexdigest()==m['in_memory_candidate_SHA256']==NEW
    assert out[792580:792583]==bytes.fromhex('3aaf88') and out[544116]==0x18
    rom=O/'combined-visible.nes';assert not rom.exists(),'No overwrite of a native-bound candidate'
    rom.write_bytes(out)
    assert sha(BASE.with_suffix('.dbg'))=='a54fadb57dbd7bb620a6b37a0ba8324cecc698c32a0dc5e0cde5855a347f41b4'
    for ext in['.dbg','.lbl']:rom.with_suffix(ext).write_bytes(BASE.with_suffix(ext).read_bytes())
    receipt=O/'combined-visible.json'
    q=dict(passed=True,private_native_only=True,native=False,installed=False,production_admitted=False,
        base_ROM_SHA256=PIN,ROM=rom.relative_to(R).as_posix(),ROM_SHA256=NEW,
        source_manifest_SHA256=MPIN,grant=grant.relative_to(R).as_posix(),grant_SHA256=sha(grant),
        exact_patch_records=10,changed_bytes=220,shared_changed_bytes=13,
        no_other_current_bytes_changed=True,WWF_Metal_Arthur_Ex_frontend_preserved=True,
        debug_exact_native_passed=True,helpers_added=False,
        prior_cold_scope='00971 actual Bub/Bob Fresh handoff passes; its globalpalette/HUD remains negative, preserved',
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),BASE,manifest,freeze,archive,cpu,grant,rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl')]})
    receipt.write_text(json.dumps(q,indent=2)+'\n')
    ordered=O/'ordered-input-v3/native-menu-plans.json';plans=json.loads(ordered.read_text())['plans']
    source=R/'tools/audit/bub_menu_qualification_1102_v2.lua';body=source.read_text()
    anchor="  shot('active-owner');finish()";assert body.count(anchor)==1
    assertion='''  assert(ppu(0x3f00)==0x22,'Actual native1-1 blue backdrop')
  assert(ppu(0x23c0)==0xaa and ppu(0x23c2)==0xea,'Actual native HUD attributes retained')
  local hud={11,Q.launch.bob==1 and 24 or 30,11,36,36,36,36}
  for i,v in ipairs(hud)do assert(ppu(0x2042+i)==v,'Exact seven-byte source HUD identity')end
  for i,v in ipairs({32,24,27,21,13,36,36,29,18,22,14})do assert(ppu(0x2051+i)==v,'Native WORLD/TIME labels retained')end
  local rgb=Q.launch.bob==1 and{44,35,48}or{42,38,48};local base=Q.launch.bob==1 and 0x3f11 or 0x3f1d
  for i,v in ipairs(rgb)do assert(ppu(base+i-1)==v,'Actual source body RGB retained')end
  shot('active-owner');finish()'''
    body=body.replace(anchor,assertion);b=scoped_load(rom);packets=[]
    for mode in['bub-start','bob-start']:
        p=copy.deepcopy(plans[mode]);at=location(b,'GroundPaletteData');p['restore']=list(b['raw'][at+24:at+27])
        names=['CrossoverMenuState','CrossoverMenuIndex','OperMode','OperMode_Task','SelectedCharacter','FmGroups','VRAM_Buffer1_Offset','VRAM_Buffer1','GameEngineSubroutine']
        prefix='\n'.join(f'L[{json.dumps(n)}]={address(b,n)}'for n in names)+'\nlocal Q='+N.lua(p)+'\n'
        output=O/('native-visible-'+('bub-cold'if mode=='bub-start'else'bob-cold'))
        prepare(output,rom,prefix+body,{Path(__file__),source,Path(N.__file__),ordered,receipt,grant,manifest,freeze,cpu},
            expected=NEW,timeout=120,scope='Exact granted4395v6 private native cold'+mode+': true simultaneous Select/confirm/Fresh identity/ready/active8 plus actual blue backdrop/native HUD attributes/name/WORLD/TIME/source RGB. OnePNG; no movement/combat/full-stage or install claim.',allow_interactive=True)
        packets.append(output.relative_to(R).as_posix())
    own=[p for p in O.rglob('*')if p.is_file()];assert sum(p.stat().st_size for p in own)<32000000 and len(own)<=128
    print(json.dumps(dict(passed=True,ROM_SHA256=NEW,packets=packets,bytes=sum(p.stat().st_size for p in own),files=len(own))))

if __name__=='__main__':main()
