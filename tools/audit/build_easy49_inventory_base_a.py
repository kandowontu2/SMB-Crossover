"""Build an isolated legacy-inventory boundary on the frozen user baseline.

This is an integration foundation, not a claim that all Easy character rules
are implemented. Classic intrinsic weapons will be supplied by their own gates.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
import zipfile

R=Path(__file__).resolve().parents[2]
B=R/'build/verification/root49-easy-hard-user-baseline-a'
H=R/'build/verification/root49-easy-inventory-base-a'
S=H/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    sys.dont_write_bytecode=True
    assert not H.exists()
    assert sha(B/'baseline.json')=='1b7fef1ea3279fc21dcb8ffca4db551b4285cfb7ad9566711db978dffa2861f1'
    baseline=json.loads((B/'baseline.json').read_text())
    cat=baseline['current_source_hashes']
    assert len(cat)==412 and all(sha(R/n)==h for n,h in cat.items())
    H.mkdir();S.mkdir()
    archive=R/'build/checkpoints/roster-audit-v49-ryu-head-t/source-v49-ryu-head-t.zip'
    assert sha(archive)==baseline['parent_T_source_archive_sha256']
    with zipfile.ZipFile(archive)as z:
        for n in z.namelist():assert (S/n).resolve().is_relative_to(S.resolve())
        z.extractall(S)
    assert sha(B/'user-source-overlay.zip')==baseline['source_overlay_sha256']
    with zipfile.ZipFile(B/'user-source-overlay.zip')as z:
        for n in baseline['source_changes_from_T']:
            (S/n).write_bytes(z.read(n))
    assert all(sha(S/n)==h for n,h in cat.items())
    inventory=S/'src/inventory.s'
    text=inventory.read_text()
    marker='.proc InventorySupported'
    assert text.count(marker)==1
    helper='''; Easy uses the linked six-character build's native three power tiers.
; Carry=classic guest in Easy, X clobbered, A/Y preserved. Mario has no2.02
; inventory in either mode. Later additions retain their own current systems.
.proc InventoryLegacyClassic
  ldx CrossoverBehaviorVersion
  bne No
  ldx SelectedCharacter
  cpx #CHARACTER_MEGAMAN
  bcc No
  cpx #CHARACTER_SIMON+1
  bcs No
  sec
  rts
No:
  clc
  rts
.endproc

'''
    text=text.replace(marker,helper+marker)
    for name in ['InventorySupported','InventoryHasRaw','InventorySpend']:
        needle='.proc '+name+'\n'
        assert text.count(needle)==1
        text=text.replace(needle,needle+'''  jsr InventoryLegacyClassic
  bcc ModernRules
  clc                           ; No2.02 ownership, ammo or UI in classic Easy.
  rts
ModernRules:
''')
    inventory.write_text(text)
    drops=S/'src/inventory_drops.s'
    text=drops.read_text()
    needle='::InventoryDropCheckCharacter:\n'
    assert text.count(needle)==1
    text=text.replace(needle,needle+'''  jsr InventoryLegacyClassic
  jcs Done                      ; Original guests have no2.02 ammo/energy drops.
''')
    drops.write_text(text)
    expected=dict(cat)
    for n in ['src/inventory.s','src/inventory_drops.s']:expected[n]=sha(S/n)
    report=dict(status='BUILDING_PRIVATE_LEGACY_INVENTORY_BOUNDARY',script_sha256=sha(__file__),
        frozen_user_baseline_sha256=sha(B/'baseline.json'),baseline_source_hashes=cat,
        candidate_source_hashes=expected,source_changes=['src/inventory.s','src/inventory_drops.s'],
        mode_contract=dict(Easy_classic_guest_IDs=[1,2,3,4,5],Hard_retains_202=True,
            later_characters_retain_their_current_inventory=True,
            native_classic_powerup_tiers=True,classic_202_world_pickups_UI_ammo_and_drops_disabled=True,
            classic_intrinsic_weapon_implementation='Separate pending character gates; HasRaw intentionally returnsfalse here, not synthetic ownership.'),
        complete_Easy_behavior=False,main_changed=False,accepted_release=False,goal_complete=False,builds=[])
    def save():(H/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    compiler=R/'tools/Windows/cc65/bin/cl65.exe';compiler_hash=sha(compiler)
    code=(S/'tools/build.py').read_text()
    code=code.replace('ROOT = Path(__file__).resolve().parents[1]','ROOT = Path('+repr(str(S))+')')
    code=code.replace("bundled = ROOT / 'tools/Windows/cc65/bin/cl65.exe'",'bundled = Path('+repr(str(compiler))+')')
    listing="'-l', f'build/{name}.lst', '-m', f'build/{name}.map',"
    assert code.count(listing)==1
    code=code.replace(listing,"'-m', f'build/{name}.map',")
    driver=H/'compact-build-driver.py';driver.write_text(code)
    report['private_driver_sha256']=sha(driver);save()
    parser=R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py'
    assert sha(parser)=='54fef35b891a96d5d0e36ca6cdeec9ee90b990666395714bc32e80cd1cabb0fb'
    spec=importlib.util.spec_from_file_location('legacy_inventory_image',parser)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    for mapper in ['mmc3','mmc5']:
        log=H/(mapper+'-build.log')
        with log.open('wb')as f:
            rc=subprocess.run([sys.executable,str(driver),'--mapper',mapper],cwd=R,stdout=f,stderr=subprocess.STDOUT).returncode
        row=dict(mapper=mapper,exit=rc,log_sha256=sha(log));report['builds'].append(row);save()
        assert rc==0,mapper
        rom=S/('build/smb-crossover-'+mapper+'.nes')
        im=module.Image(rom);old=module.Image(R/('build/smb-crossover-'+mapper+'.nes'))
        assert im.ram==old.ram,'No new state or old RAM relocation'
        assert im.raw[16+64*8192:]==old.raw[16+64*8192:],'Graphics retained'
        ds=next(q for q in im.segs.values()if q['name']=='BASS_DPCM')
        assert im.raw[ds['ooffs']:ds['ooffs']+ds['size']]==old.raw[ds['ooffs']:ds['ooffs']+ds['size']]
        row.update(artifacts={ext:dict(path=str(rom.with_suffix('.'+ext).relative_to(R)),sha256=sha(rom.with_suffix('.'+ext)))for ext in ['nes','dbg','lbl','map']},
            RAM_exact=True,CHR_exact=True,DPCM_exact=True,
            inventory_segment=next(q for q in im.segs.values()if q['name']=='INVENTORY'))
        save()
    assert sha(compiler)==compiler_hash
    assert all(sha(S/n)==h for n,h in expected.items())
    assert all(sha(R/n)==h for n,h in cat.items()),'User source untouched'
    report['status']='PASS_PRIVATE_LEGACY_INVENTORY_BOUNDARY_BUILD_ONLY'
    report['limits']='Layout/build foundation only. Actual source-mode helpers, pickups, drop rejection and Hard regression need execution; full per-characterEasy behavior is pending.'
    save();print(report['status'],sha(H/'report.json'),flush=True)


if __name__=='__main__':main()
