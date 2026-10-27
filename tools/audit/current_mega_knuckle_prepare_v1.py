"""Prepare exact-input passive body diagnosis; no ROM/capture/engine writes."""
from pathlib import Path
import json,re,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
import current_mega_arsenal_prepare_v1 as parent
from check_tmnt_render_oa import address,location

def main():
    old=R/'build/current-9ea-megaman-hard-arsenal-v1';manifest=old/'prepared-not-run.json'
    assert parent.sha(manifest)=='4c063d01a891754c200a7617de46a65a505578a86681e65d678ae3637e3043f6'
    ready=json.loads(manifest.read_text())
    for x in ready['bindings']:
        p=Path(x['path']);assert p.stat().st_size==x['bytes'] and parent.sha(p)==x['sha256'],p
    native=old/'native';result=json.loads((native/'result.json').read_text())
    assert result['passed'] and result['wall']==2623 and result['cases'][3]['sample_wall']==1175
    rom=R/'build/bill_early_cache.nes';b=parent.scoped_load(rom);raw=b['raw']
    def hook(n,delta=0,size=3):
        p=location(b,n)+delta;k=(p-16)//8192;data=list(raw[p:p+size]);banks=[k]
        if k==127:
            o=(p-16)%8192;assert raw[16+125*8192+o:16+125*8192+o+size]==bytes(data);banks=[125,127]
        return dict(pc=address(b,n)+delta,banks=banks,bytes=data,symbol=n,delta=delta)
    def returns(owner,target):
        pos=location(b,owner);n=int(b['syms'][owner]['size'],0);pc=address(b,owner);dest=address(b,target)
        needle=bytes([32,dest&255,dest>>8]);bank=(pos-16)//8192
        found=[dict(pc=pc+i+3,bank=bank,callsite=pc+i,target=dest,callbytes=list(needle)) for i in range(n-2) if raw[pos+i:pos+i+3]==needle]
        assert found,(owner,target);return found
    dr=returns('DrawAllMetasprites','DrawMetasprite');rr=returns('DrawMetasprite','RlNativeRenderDispatch')
    assert len(rr)==1 and rr[0]['pc']==0xa4f1
    script=R/'tools/audit/current_mega_knuckle_observer_v1.lua';text=script.read_text()
    names=set(re.findall(r"\br\('([^']+)'",text))|set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))
    fields='CurrentBank CurrentBankC PlayerStatus PlayerOutlinesOff ObjectMetasprite SmChrBank PlayerChrBank CurrentOAMOffset GuestOamRotationActive RgOamPlayerStart RgOamUsed RgOamRotation SpriteShuffleOffset MegaManShotPose SsHeld SsFreeze SsBodyStop MmRenderPose GuestHurtTicks GuestHurtVisible InjuryTimer MmDeathFlag HpNativeDrawLo HpNativeDrawHi'.split()
    names|=set(fields)
    ram={n:address(b,n) for n in names};assert all(n in b['syms'] and isinstance(a,int) and 0<=a<=65535 for n,a in ram.items())
    cfg=dict(ROM_sha256=parent.EXPECTED,ram=ram,fields=fields,body_id=address(b,'METASPRITE_SAMUS_BODY'),
        expected=dict(bank=(location(b,'SsMegaFISTRight')-16)//8192,pc=address(b,'SsMegaFISTRight')),
        draw_returns=dr,render_returns=rr,return_dispatch=list({(q['pc'],q['bank']):q for q in dr+rr}.values()),
        hooks={n:hook(n) for n in ['DrawMetasprite','MetaspriteRenderLoop']})
    cfg['hooks']['DmaComplete']=json.loads((old/'config.json').read_text())['hooks']['DmaComplete']
    d=int(b['syms']['GameLoop']['size'],0)-1;assert raw[location(b,'GameLoop')+d]==96;cfg['hooks']['GameLoopFinish']=hook('GameLoop',d,1)
    assert cfg['expected']['bank']==33 and cfg['expected']['pc']==0xd09d and raw[location(b,'SsMegaFISTRight')]==36
    assert 'emu.write(' not in text and 'emu.setInput(' not in text and 'takeScreenshot' not in text and 'removeMemoryCallback' not in text
    assert all(n in cfg['hooks'] for n in re.findall(r"\bhook\('([^']+)'",text))
    trace=R/'build/current-9ea-mega-knuckle-draw-source-v1.json';proof=json.loads(trace.read_text())
    assert proof['source_CPU_only'] and not proof['native_match_claim'] and proof['ROM_sha256']==parent.EXPECTED
    body=[e for r in proof['rows'] for e in r['events'] if e['event']=='MetaspriteRenderLoop' and e['ptr']==0xd09d]
    assert body and all(e['Cbank']==12 and e['header']==50 and e['return']['OAMoffset']==e['OAMoffset'] and not(e['return']['P']&1) for e in body)
    out=R/'build/current-9ea-mega-knuckle-diagnostic-v1';assert not out.exists();out.mkdir()
    parent.put(out/'observer-config.json',cfg)
    original=(old/'run.lua').read_text();prefix='dofile([=['+script.as_posix()+']=])('+parent.lua(cfg)+')\n'
    (out/'run.lua').write_text(prefix+original,newline='\n');assert (out/'run.lua').read_text()[len(prefix):]==original
    argv=json.loads((old/'command.json').read_text())['argv'];argv=[str(out/'native') if x==str(old/'native') else str(out/'run.lua') if x==str(old/'run.lua') else x for x in argv]
    parent.put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    parent.put(out/'source-controls.json',dict(passed=True,native_run=False,source_scope='Exact full2195GameLoop source trace, real body renderer entry/return SP and wrong physicalC12/header50 versus immutable33/header36; not presumed actual native state.',
        raw_original_fixture_config_controller_guards_literal=True,actual_return_JSR_bytes=dr+rr,all_RAM_names_validated=sorted(names),dynamic_field_names_validated=fields,
        static_return_registration=True,no_outcome_poses_resources_or_game_writes=True,extra_PNGs=0,expect_original_six_PNGs_and_full_CSV_byte_exact=True,
        raw_hardware_and_CHR_dump='Source SpriteData256, all256 completed E008 hardware/writes, physicalCHR0/1 and actual endFrame palette32; actual PPU counters retained without label-offset inference.'))
    paths=[Path(__file__),script,manifest,old/'run.lua',old/'config.json',native/'result.json',native/'inventory.csv',trace,R/'tools/audit/current_mega_arsenal_draw_trace_v1.py']+sorted(native.glob('*.png'))+[out/n for n in ['observer-config.json','run.lua','command.json','source-controls.json']]
    parent.put(out/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',passed=False,native_run=False,ROM_sha256=parent.EXPECTED,
        original39=ready['bindings'],bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=parent.sha(p)) for p in paths],caps=ready['caps'],
        scope='One complete unchanged Mega Hard profile with a narrow passive Knuckle actual draw/source/header/return/DMA/CHR window. Original mechanics PASS remains, body fidelity open. No extra screenshots; original6 expected unchanged. No repair/adoption inferred.',requires_ROOT_new_grant=True))
    print(json.dumps(dict(ready=str(out/'prepared-not-run.json'),sha256=parent.sha(out/'prepared-not-run.json'),bindings=39+len(paths),native_run=False)))

if __name__=='__main__':main()
