"""One compact earned-bat/both-facing native rendering packet; never launches."""
from pathlib import Path
import hashlib,json,re,sys
R=Path(__file__).resolve().parents[2];B=R/'build';sys.path.insert(0,str(R/'tools/audit'))
import current_mike_bat_candidate_v1 as candidate
import current_mike_earned_remainder_prepare_v2 as previous
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from current_roster_compact_11_v1 import lua,navigation,BASE
sha=candidate.sha;put=candidate.put

def main():
    out=B/'current-bdf9-mike-bat-render-v1';assert not out.exists()
    rom=B/'mike_bat.nes';build=json.loads((B/'mike_bat_build.json').read_text());cpu=json.loads((B/'mike_bat_controls.json').read_text())
    assert build['passed']and cpu['passed']and sha(rom)==build['candidate_sha256']==cpu['candidate_sha256']
    b=scoped_load(rom)
    ns={'__file__':str(previous.OLD),'__name__':'_bat_render_prepare'}
    exec(compile(previous.change(previous.OLD.read_text(),previous.PY_PAIRS),str(previous.OLD),'exec'),ns)
    h,_=ns['hooks_for'](b)
    def hook(n,delta=0):
        off=location(b,n)+delta;return dict(pc=address(b,n)+delta,banks=[(off-16)//8192],bytes=list(b['raw'][off:off+3]),source_symbol=n,source_delta=delta)
    for n,v in dict(Collect='JnCollectPickup',Injury='JnInjury',Defeat='JnDefeat',Reflect='JnReflectMagic',DropCollect='JnUpdateDrops::Collect').items():h[n]=hook(v)
    h['RenderShotCall']=hook('JnDraw::Next',-3);h['RenderShotReturn']=hook('JnDraw::Next')
    off=location(b,'JnDraw::Next');dest=address(b,'JnDraw::Draw');assert b['raw'][off-3:off]==bytes([32,dest&255,dest>>8])
    plan=[
        dict(name='physical-flower-earned-tier2',kind='pickup',health=6,limit=240,pickup=1,item=2,afterHP=6,afterStock=2),
        dict(name='physical-flower-earned-tier3',kind='pickup',health=6,limit=240,pickup=1,item=3,afterHP=6,afterStock=3),
        dict(name='physical-flower-native-bat',kind='pickup',health=6,limit=240,pickup=1,item=4,afterHP=6,afterStock=3,picture='01-earned-bat.png'),
        dict(name='source-bat-right-whole-animation',kind='weapon',health=6,limit=240,weapon=4,face=1,attacks=1,wait=90,picture='02-right-terminal.png'),
        dict(name='source-bat-left-whole-animation',kind='weapon',health=6,limit=240,weapon=4,face=2,attacks=1,wait=90,picture='03-left-terminal.png')]
    proof=ns['campaign'](b,False,plan,h,address(b,'BulletBill_CannonVar'));assert proof['passed']and len(proof['components'])==5
    def records(lo,hi,count):
        rows=[]
        for i in range(count):
            ptr=b['raw'][location(b,lo)+i]+256*b['raw'][location(b,hi)+i];pos=16+97*8192+ptr-0xc000
            size=b['raw'][pos];assert size%4==0 and size<128
            rows.append(dict(pointer=ptr,bank=97,header=size,record_sha256=hashlib.sha256(b['raw'][pos:pos+size+1]).hexdigest()))
        return rows
    original=R/'tools/audit/current_mike_live_render_diagnostic_v1.lua';helper=original.read_text()
    a=" local record=assert(D.records[pose+1]);local ptr=r('R0')+256*r('R1')"
    z=" local left=vx>=128 or vx==0 and r('PlayerFacingDir')==2\n local record=assert(kind==4 and age>=1 and age<=30 and D.bat_records[age+(left and 30 or 0)]or D.records[pose+1]);local ptr=r('R0')+256*r('R1')"
    assert helper.count(a)==1;helper=helper.replace(a,z);assert helper.replace(z,a)==original.read_text()
    assert 'emu.write'not in helper and 'removeMemoryCallback'not in helper
    fixture=previous.NEW.read_text();marker='-- All callback registration is startup-static. No callback adds/removes callbacks.'
    assert fixture.count(marker)==1
    text=fixture.replace(marker,helper+'\n'+marker);assert text.replace(helper+'\n','')==fixture
    # Every literal and bare callback RAM address resolves before registration.
    old=json.loads((B/'current-ab221-mike-live-render-diagnostic-v1/config.json').read_text());cfg=old.copy()
    names=set(old['ram'])|set(re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text))|set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))
    names|=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))&set(b['syms'])
    cfg.update(ROM_sha256=sha(rom),plan=plan,hooks=h,ram={n:address(b,n)for n in names},
        render_diagnostic=dict(old['render_diagnostic'],records=records('JnShotAllLo','JnShotAllHi',52),bat_records=records('JnBatRecordLo','JnBatRecordHi',60)),
        navigation=navigation(b['raw'],lambda n:location(b,n),BASE['mike'][0]),dma_store_return=address(b,'PostDmaMaskEnable'),
        scope='Currentbdf9 private source-timed bat only: real mature classified tier2/tier3/bat flower pickups, actual right/left B attacks and stock debit/contact/cleanup. Complete active render stream has real draw→Main→physical256DMA provenance. Original palette/visible-line fidelity and SMB-adapted reach/record origin remain open. No allweapon native or FPS claim.')
    assert cfg['mode']==1 and cfg['character']==16 and cfg['menu']==BASE['mike'][0]
    cfg['smc']=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2]
    cfg['metatiles']={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in cfg['metatiles']}
    out.mkdir();profile=B/'mike_bat_profile.lua';profile.write_text(text,newline='\n')
    put(out/'config.json',cfg);put(out/'source-controls.json',proof)
    (out/'run.lua').write_text('CURRENT_MAC_MIKE_POWERUPS='+lua(cfg)+'\ndofile([=['+profile.as_posix()+']=])\n',newline='\n')
    argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out/'native'),str(out/'run.lua'),str(rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false','--option=--nes.removeSpriteLimit=false']
    put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    paths={Path(__file__),original,previous.NEW,previous.OLD,Path(previous.__file__),rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),profile,
        B/'mike_bat_build.json',B/'mike_bat_controls.json',B/'mike_bat.patch',Path(candidate.__file__),
        R/'tools/audit/current_mike_bat_cpu_v1.py',R/'tools/audit/current_shared_star_life_prepare_v1.py',R/'tools/audit/current_roster_compact_11_v1.py',
        R/'tools/audit/final_inventory_compact_capture_v1.lua',R/'tools/audit/final_inventory_compact_capture_v1.py',R/'tools/audit/run_mesen_isolated.py',R/'tools/audit/capture_budget.py',R/'tools/run_mesen.py',
        B/'current-ab221-mike-live-render-diagnostic-v1/prepared-not-run.json',B/'current-ab221-mike-live-render-diagnostic-v1/live-render-offline-review.json',
        Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll'),Path('C:/Mesen2/settings.json')}
    paths|={Path(d['path'])for d in build['changed_source'].values()}
    paths|={out/n for n in ['run.lua','config.json','source-controls.json','command.json']}
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f and('py65'in f or str(R/'tools/audit')in f)and Path(f).is_file():paths.add(Path(f))
    ready=dict(status='PREPARED_NATIVE_UNRUN',passed=False,native_run=False,Lua_VM_executed=False,ROM_sha256=sha(rom),parent_ROM_sha256=candidate.EXPECTED,
        scope=cfg['scope'],cases=5,source_GameLoop_calls=proof['full_GameLoop_calls'],observer_delta='Only source-derived bat record selection; old normal52records, all lifecycle/hardware guards and original fixture body otherwise exact.',
        caps=dict(wall_frames=8000,updates=4000,host_seconds=1200,files=64,bytes=2000000000,PNGs=3,perframe_files=0,compact_stream_bytes=134217728,compact_records=3000),
        bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)])
    put(out/'prepared-not-run.json',ready)
    print(json.dumps(dict(ready=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),bindings=len(paths),ROM=sha(rom),native_run=False)))

if __name__=='__main__':main()
