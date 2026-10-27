"""Prepare one corrected additive Proto default-handoff diagnosis. Never launches Mesen."""
from pathlib import Path
import hashlib,json,re,sys

R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import current_mega_arsenal_prepare_v1 as parent
from check_tmnt_render_oa import address,location

def main():
    old=R/'build/current-9ea-proto-hard-arsenal-v1';ready=json.loads((old/'prepared-not-run.json').read_text())
    assert parent.sha(old/'prepared-not-run.json')=='a0b8d2936eb8de8ed026e84ee637e270f6bacb03e3828c764b2df0fd03a16c0e'
    for x in ready['bindings']:
        p=Path(x['path']);assert p.stat().st_size==x['bytes'] and parent.sha(p)==x['sha256'],p
    native=old/'native';assert not(native/'result.json').exists()
    csv=native/'inventory.csv';log=native/'bill_early_cache-run.log'
    assert 'Actual NMI render enable deadline' in log.read_text()
    last=csv.read_text().splitlines()[-1].split(',');assert last[0:6]==['update','2593','2190','9','hud','1']
    rom=R/'build/bill_early_cache.nes';b=parent.scoped_load(rom);raw=b['raw']
    cfg=json.loads((old/'config.json').read_text());extra=json.loads(json.dumps(cfg))
    for n in ['ReloadCHRBank','VRAM_Buffer1','VRAM_Buffer2','VRAM_Buffer1_Offset','VRAM_Buffer2_Offset','VRAM_Buffer_AddrCtrl','NmiR0','NmiR1','CurrentCHRBank','X5ChrMode']:
        extra['ram'][n]=address(b,n)
    def hook(n,delta=0,size=3):
        p=location(b,n)+delta;k=(p-16)//8192;bs=list(raw[p:p+size]);banks=[k]
        if k==127:
            o=(p-16)%8192;assert raw[16+125*8192+o:16+125*8192+o+size]==bytes(bs);banks=[125,127]
        return dict(pc=address(b,n)+delta,banks=banks,bytes=bs,symbol=n,delta=delta)
    for n in ['UpdateScreen','BankSwitchCHR','InventoryHud','ProtoQueueBasePalette','ProtoFixQueuedPalette','SamusFreezeUpdateScreen']:extra['hooks'][n]=hook(n)
    delta=int(b['syms']['BankSwitchCHR']['size'],0)-1;assert raw[location(b,'BankSwitchCHR')+delta]==96
    extra['hooks']['BankSwitchCHRReturn']=hook('BankSwitchCHR',delta,1)
    extra.update(first=2520,last=2640)
    observer=R/'tools/audit/current_mega_arsenal_timing_observer_v2.lua';text=observer.read_text()
    assert 'emu.write(' not in text and 'emu.setInput(' not in text and 'takeScreenshot' not in text and 'removeMemoryCallback' not in text
    assert text.count('emu.addMemoryCallback')==6 and '10000' in text and '8000000' in text
    # Every literal read and direct callback/array base is resolved against
    # actual linked symbols, including the three omitted v1 logger fields.
    literal=set(re.findall(r"\br\('([^']+)'",text))
    direct=set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))
    for n in literal|direct:
        assert n in b['syms'] and 0<=address(b,n)<=65535,n
        extra['ram'][n]=address(b,n)
    for n in literal|direct:assert extra['ram'][n]==address(b,n),n
    assert all(n in extra['hooks'] for n in re.findall(r"\bhook\('([^']+)'",text))
    dynamic_hooks=['InventoryHud','ProtoQueueBasePalette','ProtoFixQueuedPalette','SamusFreezeUpdateScreen']
    assert all(n in extra['hooks'] for n in dynamic_hooks)
    # All calls to r() outside its definition are literal. The dynamic s[k]
    # list is emulator-state provenance, never a RAM alias/zero fallback.
    assert not re.search(r'(?<!function )\br\(\s*(?![\"\'])\w+',text.replace('local function r(n,i)',''))
    assert extra['ram']['InvDirty']==0x7d8e and extra['ram']['InvHudActive']==0x7d9e and extra['ram']['InvHudPhysical']==0x7d9f
    failed=R/'build/current-9ea-proto-arsenal-diagnostic-v1'
    fail_log=failed/'native/bill_early_cache-run.log';assert 'FAIL InvDirty' in fail_log.read_text()
    assert not(failed/'native/result.json').exists()
    assert observer.read_bytes()==(R/'tools/audit/current_mega_arsenal_timing_observer_v1.lua').read_bytes(),'v2 observer algorithms byte-exact; only metadata binding repaired'
    out=R/'build/current-9ea-proto-arsenal-diagnostic-v2';assert not out.exists();out.mkdir()
    parent.put(out/'observer-config.json',extra)
    original=(old/'run.lua').read_text()
    prefix='dofile([=['+observer.as_posix()+']=])('+parent.lua(extra)+')\n'
    # Appended prefix only. Original controller, mechanics and all six guard
    # modules/config bytes remain literal and run in their original order.
    script=prefix+original;assert script[len(prefix):]==original
    (out/'run.lua').write_text(script,newline='\n')
    command=json.loads((old/'command.json').read_text())['argv']
    command=[str(out/'native') if v==str(old/'native') else str(out/'run.lua') if v==str(old/'run.lua') else v for v in command]
    reverse=[str(old/'native') if v==str(out/'native') else str(old/'run.lua') if v==str(out/'run.lua') else v for v in command]
    assert reverse==json.loads((old/'command.json').read_text())['argv']
    parent.put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=command))
    parent.put(out/'source-controls.json',dict(passed=True,native_run=False,observer_only=True,
        original39bindings_reverified=True,original_run_suffix_exact=True,original_config_exact=True,all_RAM_reads_verified=sorted(literal),all_direct_bases_verified=sorted(direct),all_dynamic_hook_names_verified=dynamic_hooks,observer_v1_bytes_exact=True,old_diagnostic_v1_FALSE='Logger requested real InvDirty but config omitted it plus InvHudActive/Physical; no original deadline reached, output0bytes',
        original_mechanics_controller_seeds_guard_order_caps=True,new_emulated_state_writes=0,
        extra_screenshots=0,all_registrations_startup_static=True,genuine_hooks=extra['hooks'],
        actual_original_last_event=last,original_deadline_FALSE=True,
        expected='Same original firstFALSE and semantically exact CSV/PNG prefix; diagnostic records actual PPUMASK/parser/CHR events before unchanged failure assertion. Compare saved outputs offline; no native clearance from preparation.',
        limitation='Static source/linked hook qualification only, not Lua VM/native timing proof; current native snapshot lacked exact unsafe line/dot and raw packet.'))
    paths=[Path(__file__),observer,failed/'prepared-not-run.json',failed/'observer-config.json',fail_log,failed/'native/inventory.csv',old/'prepared-not-run.json',old/'config.json',old/'run.lua',csv,log]+[native/x for x in ['item-01.png','item-03.png','item-05.png','item-06.png','item-07.png','item-08-rush.png']]+[out/n for n in ['observer-config.json','run.lua','command.json','source-controls.json']]
    parent.put(out/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,
        ROM_sha256=parent.EXPECTED,purpose='One same-input Proto default-HUD/BALANCE transition diagnosis, not retry clearance.',
        original39=ready['bindings'],bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=parent.sha(p)) for p in paths],
        scope='Window2520..2640, raw Buffer1/2, actual parser commands/source producers, default/HUD/font/reload/CHR chronology, NMI/PPU/CPU/physical banks, all256 E008 source/hardware. No additional images or mechanics changes.',
        caps=ready['caps'],requires_new_ROOT_grant=True))
    print(json.dumps(dict(ready=str(out/'prepared-not-run.json'),sha256=parent.sha(out/'prepared-not-run.json'),bindings=len(paths)+39,native_run=False)))

if __name__=='__main__':main()
