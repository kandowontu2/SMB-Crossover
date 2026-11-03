"""Four unchanged cf7 controller policies on granted80d3; prepare only."""
import json,re,sys,zipfile
from pathlib import Path
import build_storage_guard_v1 as G
from prepare_selected_native_packet_v1 import R,sha,prepare
import check_bub_combined_auth_contracts_1103_v84 as P
from check_tmnt_render_oa import location

O=R/'build/bub-combined-auth-native-1103-v91'
ROM=R/'build/combined-owner-auth-root-1103-v116/combined-auth-private.nes'
PIN='80d3ae95894f5ddb430c3e753dd95f3fc2eca6a87d8e1afdb4b8ce8376ec795a'
OLD='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
GRANT=R/'docs/qa/allocations/combined-owner-auth-1103-v116.json'
FROZEN=R/'docs/qa/checkpoints/2026-11-03/bub-earned-delivery-v99'


def main():
    G.preflight(private_root=O,reserved_bytes=1_000_000,reserved_files=13,fresh=True)
    O.mkdir(exist_ok=True);assert not any(O.iterdir())
    grant=json.loads(GRANT.read_text());assert grant['granted']and grant['expected_candidate_SHA256']==PIN==sha(ROM)
    old,new,parent,q=P.image();raw=ROM.read_bytes()
    previous=json.loads((FROZEN/'receipt.json').read_text());archive=FROZEN/'inputs.zip'
    assert previous['passed']and previous['ROM_SHA256']==OLD and previous['archive_SHA256']==sha(archive)
    native_labels={m[2]:int(m[1],16)for line in ROM.with_suffix('.lbl').read_text().splitlines()
        if(m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.([\w]+)',line))}
    private=(R/'build/bub-initial-tier-1103-v87/private-image.bin').read_bytes()
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    lua=LuaRuntime();prepared=[]
    profile=[]
    for name in ['GameCoreRoutine','PlayerBGCollision','BlockBufferCollision']:
        at=location(new,name);pc=P.P.address(new,name)
        assert raw[at:at+4]==new['raw'][at:at+4]
        profile.append(dict(name=name,pc=pc,physical=at-16,bytes=list(raw[at:at+4])))
    for name in ['CoCheckCode','CoCheckHeaders']:
        pc=q['labels'][name];at=16+65*8192+pc-0xa000
        profile.append(dict(name=name,pc=pc,physical=at-16,bytes=list(raw[at:at+4])))
    with zipfile.ZipFile(archive)as z:
        for identity,name in [(0,'bub'),(1,'bob')]:
            for task in ['full11','mushroom']:
                source=R/f'build/bub-earned-delivery-1103-v98/downloads-{name}-{task}/controller.lua'
                member=source.relative_to(R).as_posix();original=source.read_bytes()
                assert z.read(member)==original
                baseline=next(row for row in previous['downloads_rows']if row['identity']==identity and row['task']==task)
                old_packet=Path(baseline['packet'])
                observer=(json.loads(z.read((old_packet/'capture/bub-observer.json').as_posix()))if task=='full11'
                    else json.loads(z.read((old_packet/'capture/earned-mushroom.json').as_posix()))['observer'])
                assert observer['passed']and observer['identity']==identity and observer['failures']==0
                text=original.decode('utf-8');assert OLD in text
                text=text.replace(OLD,PIN)
                assert not re.search(r'\bemu\.(write|loadSavestate|saveSavestate)\s*\(',text)
                config_line=re.search(r'^local BUB_NATIVE_OBSERVER_CONFIG=(.*)$',text,re.M);assert config_line
                config=lua.eval(config_line[1]);assert config['identity']==identity
                cookie=bytes(int(config['cookie'][i])for i in range(1,17))
                assert cookie.hex()=='a72701f3691d419fd9ae7473840ce393'
                cookie_at=16+65*8192+q['labels']['CoBBCookie']-0xa000
                assert raw[cookie_at:cookie_at+16]==cookie
                for _,hook in config['hooks'].items():
                    pc=int(hook['pc']);actual=bytes(int(hook['bytes'][i])for i in range(1,5))
                    if hook['memory']=='nesWorkRam':
                        assert actual==private[pc-0xa000:pc-0xa000+4]
                        assert int(hook['physical'])==3*8192+pc-0xa000
                    else:
                        assert hook['memory']=='nesPrgRom'
                        at=16+int(hook['physical']);assert raw[at:at+4]==actual
                extra=[]
                existing={value for _,value in config['profile_names'].items()}
                for hook in profile:
                    if config['hooks'][hook['name']]is None:
                        extra.append('BUB_NATIVE_OBSERVER_CONFIG.hooks.'+hook['name']+'={memory="nesPrgRom",name="'+hook['name']+'",pc='+str(hook['pc'])+',physical='+str(hook['physical'])+',bytes={'+','.join(map(str,hook['bytes']))+'}}')
                    if hook['name']not in existing:
                        extra.append('table.insert(BUB_NATIVE_OBSERVER_CONFIG.profile_names,"'+hook['name']+'")')
                # Only passive aggregate additions. All original controller
                # decisions, inputs, assertion strings and observers remain.
                anchor='local BubNativeObserver=(function()';assert text.count(anchor)==1
                text=text.replace(anchor,'\n'.join(extra)+'\n'+anchor)
                before="perfStack[#perfStack+1]={name=name,ret=ret,sp=(sp+2)&255,memory=a.memType,physical=a.address,start=s['cpu.cycleCount']}"
                assert text.count(before)==1
                text=text.replace(before,before[:-1]+',entry_sp=sp}')
                before='local elapsed=s[\'cpu.cycleCount\']-q.start;p.calls=p.calls+1;'
                assert text.count(before)==1
                text=text.replace(before,"p.minimum_observed_entry_SP=math.min(p.minimum_observed_entry_SP or 255,q.entry_sp)\n  "+before)
                # Explicit passed labels are sufficient; no native debugger
                # tree or former run scaffold is copied into this task.
                explicit={n:int(value)for n,value in re.findall(r'L\["(\w+)"\]=(\d+)',text)}
                reader=text.index('local function r(n)return emu.read(assert(L[n],n)')
                needed=set(re.findall(r'\bL\.(\w+)',text))|set(re.findall(r"\br\(['\"](\w+)['\"]",text[reader:]))
                for label in needed:
                    assert label in explicit,label
                    assert label not in native_labels or native_labels[label]==explicit[label],label
                assert lua.eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
                output=O/f'{name}-{task}'
                prepare(output,ROM,text,[Path(__file__),source,GRANT,FROZEN/'receipt.json',archive,
                    R/'build/bub-menu-candidate-1102-v2/combined-auth-source-v89.json',
                    R/'build/bub-menu-candidate-1102-v2/combined-auth-v90-composition.json'],
                    expected=PIN,timeout=240 if task=='full11'else 180,allow_interactive=True,
                    scope='Exact granted80d3 private combined auth regression. Same actualcf7/v98/v99controller input policy and all assertions: natural menu/coldidentity, unseeded firstmushroom or separatefullnonshortcut1-1/noinjury/nolifeloss/nohelpers. Cookie/privatehookpreimages unchanged. Passive source/nativecollision/auth/Main inclusivecycle aggregates and sampledprofileentrySP added; not an all-instruction minimum or preclaimedperformance/fullstagepass. Rootaloneexecutes; no installation.')
                prepared.append(dict(identity=identity,task=task,packet=output.relative_to(R).as_posix(),
                    source_controller=member,source_controller_SHA256=sha(source),
                    baseline=dict(frames=baseline['frames'],completed_Main=baseline['completed_Main'],checks=baseline['checks'],
                        failures=baseline['failures'],lives=baseline['lives'],profile=observer['profile'],phases=observer['phases']),
                    sampled_SP_scope='minimum at physically qualified profiledroutine entries among returnedcalls; not full-instruction/IRQ minimum',
                    max_PNGs=4))
    result=dict(prepared=True,READY=True,native=False,ROM=ROM.relative_to(R).as_posix(),ROM_SHA256=PIN,
        grant=GRANT.relative_to(R).as_posix(),emulated_writes=False,ability_seeds=False,
        controller_policies_and_assertions_unchanged=True,Bub_private_cookie_and_source_preimages_unchanged=True,
        packets=prepared,added_passive_profiles=profile,comparison='Compare actual physical_frames/completed_Main/source_updates, phasegrosscycles and inclusive profiles. Different actor/control trajectories mustbe reported before attributing whole-route frames to speed; no minimumSP hardware claim from entry samples.',
        bindings={path.relative_to(R).as_posix():sha(path)for path in [Path(__file__),ROM,ROM.with_suffix('.lbl'),ROM.with_suffix('.dbg'),GRANT,FROZEN/'receipt.json',archive]})
    (O/'prepared.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(READY=True,packets=[row['packet']for row in prepared],ROM_SHA256=PIN,
        output_storage=G.inventory(O,G.TASK_BYTES,G.TASK_FILES))))


if __name__=='__main__':main()
