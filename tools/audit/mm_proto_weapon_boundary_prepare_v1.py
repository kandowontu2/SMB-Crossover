"""Prepare one source-bound MegaHard support/primary profile; no native option."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import re
import sys
import traceback
from final_item_abilities_run import lua
from final_item_abilities_current731_prepare_v1 import protocol, dma_mocks
from final_item_abilities_static_prepare_v2 import core_tests, old_core
from parodius_visibility_hud_static_startup_v1 import MOCK
from link_pit_rygar_sophia_audit_cpu import scoped_load, Arena
from check_tmnt_render_oa import address, location

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
B = D/'root-current-roster-composition-v1'
OLD = D/'current3b112-bass-semantic-cleanup-ready-v1'
SHA = '3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p, z: Path(p).write_text(json.dumps(z, indent=2)+'\n')


def component_cpu(b):
    rows = []
    for variant in [0, 1]:
        for hold, expected in [(1, 1), (48, 2), (87, 3)]:
            q = Arena(b, 1)
            q.put(ProtoVariant=variant, CrossoverBehaviorVersion=1, PlayerStatus=1,
                  Player_X_Position=64, Player_PageLoc=0, Player_Y_Position=176,
                  Player_Y_HighPos=1, PlayerFacingDir=1, GameEngineSubroutine=8)
            q.set('InvOwnedLo', 1, 1);q.set('InvOwnedHi', 7, 1)
            for tick in range(hold+1):
                q.set('A_B_Buttons', 64 if tick < hold else 0)
                q.set('PreviousA_B_Buttons', 64 if tick else 0)
                c, _ = q.invoke('MegaManWeapons')
            types = [q.get('MmBulletType', i) for i in range(4)]
            assert expected in types and q.get('MmChargeFrames') == 0, (variant, hold, types)
            rows.append(dict(kind='actual-primary-hold-release', variant=variant, held_updates=hold, types=types, calls=hold+1))
        for stock in [3, 4, 20]:
            q = Arena(b, 1);q.put(ProtoVariant=variant, PlayerFacingDir=1, Player_X_Position=112, Player_PageLoc=0)
            q.set('InvAmmo', stock, 24);c, _ = q.invoke('MegaManRushAttack')
            types = [q.get('RgShotType', i) for i in range(10)]
            assert q.get('InvAmmo', 24) == stock
            assert (20 in types) == (stock >= 4)
            if stock >= 4:
                slot = types.index(20)
                assert q.get('RgShotX', slot) == 140 and q.get('RgShotY', slot) == 0 and q.get('RgShotYHigh', slot) == 1
            rows.append(dict(kind='actual-rush-summon-gate', variant=variant, stock=stock, types=types, cycles=c.processorCycles))
        for stock in [0, 4, 20, 112]:
            q = Arena(b, 1);q.set('InvAmmo', stock, 24)
            c, _ = q.invoke('MegaManRushBounce')
            assert q.get('InvAmmo', 24) == max(0, stock-12)
            assert [q.get(n) for n in ['MmFrictionYActive', 'MmJumpReleased', 'MmRushLandRequest']] == [0, 1, 1]
            rows.append(dict(kind='actual-direct-rush-bounce-consumer', variant=variant, before=stock, after=q.get('InvAmmo', 24), cycles=c.processorCycles))
        q = Arena(b, 1);q.set('InvOwnedLo', 7, 1);q.set('InvOwnedHi', 7, 1)
        for index, stock in [(17, 60), (18, 4), (24, 8)]:q.set('InvAmmo', stock, index)
        c, _ = q.invoke('InventoryRefillAmount', a=8)
        assert [q.get(n) for n in ['InvRefill', 'InvRefillRemain', 'InvRefillTick']] == [18, 8, 3]
        assert q.get('InvAmmo', 18) == 4
        rows.append(dict(kind='actual-passive-balancer-choice', variant=variant, selected=0, target=18, immediate_credit=0, cycles=c.processorCycles))
        q = Arena(b, 1);q.set('InvOwnedLo', 1, 1);q.set('InvOwnedHi', 7, 1)
        choices = []
        for wanted in [8, 0]:
            c, _ = q.invoke('InventoryCycle');choices.append(q.get('InvSelected', 1));assert choices[-1] == wanted
        rows.append(dict(kind='actual-select-skips-passives', variant=variant, choices=choices))
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(R)
    a.output.mkdir(parents=True, exist_ok=False)
    try:
        assert sha(B/'candidate.nes') == SHA
        assert sha(OLD/'proof.json') == '95eb297447cb811065c0da80b307b94d9ac12d553307b29d73a810462bfa6d0f'
        source = json.loads((B/'source-manifest.json').read_text())
        for rel, h in source.items():assert sha(B/'source'/rel) == h, rel
        b = scoped_load(B/'candidate.nes')
        cpus = component_cpu(b)
        put(a.output/'assembled-controls.json', dict(passed=True, native_run=False, rows=cpus,
            limits='Isolated configured CPU routines/button fields, both presentation variants. Direct bounce consumer includes states not admitted by summon. No physical contact/controller/NMI/pixels/acquisition claim.'))
        oldout = OLD/'profiles/bass-hard/native'
        cfg = json.loads((oldout/'config.json').read_text())
        original = (oldout/'run.lua').read_text()
        prefix = 'FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n';assert original.startswith(prefix)
        body = original[len(prefix):]
        first = body.index('-- Controlled B-only gallery.')
        last = body.index('\nlocal saved=nil', first)
        head, tail = body[:first], body[last:]
        old_variant = "if r('RlVariant')~=0 then return{select=true}end"
        new_variant = "if r(C.identity.variant_ram)~=C.identity.variant then return{select=true}end"
        assert head.count(old_variant) == 1;head = head.replace(old_variant, new_variant)
        # New profile emits valid numeric object keys directly; old outputs stay exact.
        assert head.count("string.format('%q',k)") == 1
        head = head.replace("string.format('%q',k)", "string.format('%q',tostring(k))")
        assert tail.count('native-bass-gallery.json') == 1
        tail = tail.replace('native-bass-gallery.json', 'native-mm-weapon-profile.json')
        assert tail.count("wall<22000,'Bounded controlled Bass gallery '") == 1
        tail = tail.replace("wall<22000,'Bounded controlled Bass gallery '", "wall<4000,'Bounded robot primary/support profile '")
        owner = address(b, 'CHARACTER_MEGAMAN');assert owner == 1
        at = location(b, 'X5MenuCharacters');slots = list(b['raw'][at:at+19]);assert slots.count(owner) == 1
        indices = list(b['raw'][location(b, 'InvAmmoIndex')+owner*16:location(b, 'InvAmmoIndex')+owner*16+9])
        assert indices == [255,17,18,19,20,21,22,23,24]
        selectable = list(b['raw'][location(b, 'InvSelectable')+owner*16:location(b, 'InvSelectable')+owner*16+11])
        assert selectable[8] == 1 and selectable[9:] == [0, 0]
        cfg.update(family='megaman',character=owner,slot=slots.index(owner),hard=True,mode_value=1,ROM_sha256=SHA)
        cfg['identity'] = dict(owner=owner, inventory_base=owner*16, variant_ram='ProtoVariant', variant=0,
            passive_alternates=[0,1], ammo_indices=indices, rush_item=8, balancer=9, charge_item=10)
        cfg['charge'] = dict(weak=48,full=87)
        cfg['rush'] = dict(summon_gate=4,bounce_cost=b['raw'][location(b,'InvCosts')+24])
        assert cfg['rush']['bounce_cost'] == 12 and b['raw'][location(b,'InvItemCount')+owner] == 10
        cfg['cases'] = [dict(name='basic-tier1',kind='primary',item=0,stock=20,release=10,finish=90,expected_primary=[1]),
            dict(name='weak-tier1',kind='primary',item=0,stock=20,release=62,finish=145,expected_primary=[1,2]),
            dict(name='full-tier1',kind='primary',item=0,stock=20,release=102,finish=190,expected_primary=[1,3]),
            dict(name='rush-lifecycle',kind='rush',item=8,stock=20),
            dict(name='rush-gate3',kind='rush-refusal',item=8,stock=3),
            dict(name='passive-balance-small',kind='balance',item=0,stock=8)]
        cfg['drop_arrays'] = ['InvDropKind','InvDropX','InvDropPage','InvDropY','InvDropVY','InvDropVYMid','InvDropVYHi','InvDropFraction','InvDropFractionHi','InvDropAge','InvDropAgeHi','AvDropItem']
        lengths = list(b['raw'][location(b,'ProtoLegacyDrawShotsCold::ShotLengths'):location(b,'ProtoLegacyDrawShotsCold::ShotLengths')+6])
        starts = list(b['raw'][location(b,'ProtoLegacyDrawShotsCold::ShotStarts'):location(b,'ProtoLegacyDrawShotsCold::ShotStarts')+6])
        base = address(b,'METASPRITE_MM_BULLET_1')
        records = []
        for start, length in zip(starts, lengths):
            frames = []
            for frame in range(length):
                faces=[]
                for side in ['Right','Left']:
                    i=start+frame-base
                    ptr=b['raw'][location(b,'ProtoShot'+side+'Lo')+i]+256*b['raw'][location(b,'ProtoShot'+side+'Hi')+i]
                    bank=(location(b,'ProtoShot'+side+'Lo')-16)//8192
                    off=16+bank*8192+ptr%8192
                    faces.append(dict(address=ptr,bank=bank,bytes=list(b['raw'][off:off+1+b['raw'][off]])))
                frames.append(faces)
            records.append(frames)
        cfg['primary'] = dict(lengths=lengths,starts=starts,records=records)
        assert lengths == [1,2,4,3,2,3]
        hooks = ['MegaManWeapons::Spawn','MegaManRushAttack','MegaManRushBounce','InventoryRefillAmount','InventoryUiTick']
        for name in hooks:
            off=location(b,name);cfg['hooks'][name]=dict(address=address(b,name),physical_bank=(off-16)//8192,bytes=list(b['raw'][off:off+3]))
        name='ProtoLegacyDrawShotsCold::Pointer';off=location(b,name)
        assert b['raw'][off] == 0x85
        cfg['hooks']['PrimaryArtReady']=dict(address=address(b,name)+2,physical_bank=(off-16)//8192,bytes=list(b['raw'][off+2:off+5]))
        cfg['primary_art_hook_binding']=dict(genuine_label=name,delta=2,reason='After actual STA R1; never a fake callable symbol')
        module=R/'tools/audit/mm_proto_weapon_boundary_v1.lua'
        for name in re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",module.read_text()):
            if name in b['syms']:cfg['ram'][name]=address(b,name)
        cfg['ram']['ProtoVariant']=address(b,'ProtoVariant')
        assert cfg['dma_protocol']==protocol(b)
        script='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n'+head+module.read_text()+tail
        direct=set(re.findall(r"\b[wr]\('([A-Za-z_][A-Za-z_0-9]*)'",script))
        assert not direct-set(cfg['ram']),direct-set(cfg['ram'])
        assert not any(x in module.read_text()for x in ["w('InvSelected'","w('SelectedCharacter'","w('ProtoVariant'","w('CrossoverBehaviorVersion'"])
        native=a.output/'native';native.mkdir();(native/'run.lua').write_text(script);put(native/'config.json',cfg)
        sys.path.insert(0,str(D/'final-tmnt-items-v1/lua-parser-deps-v1'));from luaparser import ast as last
        last.parse(script)
        sys.path.insert(0,str(D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
        mock=MOCK+'\nL={};OUTPUT="mock/";emu.memType.nesPaletteRam=5;emu.memType.nesChrRom=6;emu.write=function()error("Unexpected startup write")end;emu.getScreenBuffer=function()local t={};for i=1,61440 do t[i]=0xff000000 end;return t end\n'
        rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(mock+script)
        count=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')
        rt.execute('emu.addMemoryCallback=function()error("Runtime registration")end;emu.removeMemoryCallback=function()error("Runtime removal")end')
        for frame in [1,2,3]:rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.startFrame);runevents(emu.eventType.endFrame)")
        assert rt.eval('#callbacks')==count
        models=[]
        for expression,expected in [('checkPrimary(2,48)',True),('checkPrimary(2,47)',False),('checkPrimary(3,87)',True),('checkPrimary(3,86)',False),('checkRushDebit(20,8)',True),('checkRushDebit(4,0)',True),('checkRushDebit(20,9)',False)]:
            z=LuaRuntime(unpack_returned_tuples=True).execute(mock+script+'\nlocal ok,e=pcall(function()'+expression+' end);return ok,tostring(e)')
            assert bool(z[0])==expected,(expression,z)
            models.append(dict(expression=expression,expected_accept=expected,control_passed=True))
        encoded=LuaRuntime().execute(mock+script+'\nreturn json({[0]=true,[4]={stock=20}})')
        assert json.loads(encoded)=={'0':True,'4':{'stock':20}}
        returns=core_tests(LuaRuntime,old_core((R/'tools/audit/final_item_abilities_native.lua').read_text()),(R/'tools/audit/final_item_abilities_static_return_v1.lua').read_text())
        dma=dma_mocks(LuaRuntime,(R/'tools/audit/final_item_abilities_dma731_v1.lua').read_text(),dict(dma_protocol=cfg['dma_protocol']))
        put(a.output/'source-controls.json',dict(passed=True,native_run=False,callbacks=count,dispatcher_last=True,no_runtime_registration=True,numeric_object_key_JSON_passed=True,threshold_debit_models=models,return_controls=returns,DMA_controls=dma,guard_prefix_changes=['Source-bound menu variant predicate','JSON numeric key tostring'],guard_tail_changes=['New profile result filename','Stricter4000wallbound'],all_other_prefix_tail_bytes_preserved=True))
        env=json.loads((OLD/'environment.json').read_text());emu=Path(env['emulator'])
        for path,h in [(emu,env['emulator_sha256']),(emu.parent/'MesenCore.dll',env['core_sha256']),(emu.parent/'settings.json',env['worker_settings_sha256']),(Path('C:/Mesen2/settings.json'),env['user_context_sha256'])]:assert sha(path)==h,path
        command=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(native),'--emulator',str(emu),str(native/'run.lua'),str(B/'candidate.nes'),'--timeout','1200']+['--option='+x for x in env['actual_command_overrides']]
        put(a.output/'command.json',command)
        files={Path(__file__),module,B/'candidate.nes',B/'candidate.dbg',B/'candidate.lbl',B/'candidate.map',B/'source-manifest.json',B/'ROOT-source-readiness.json',OLD/'proof.json',OLD/'manifest.json',oldout/'run.lua',oldout/'config.json',OLD/'isolated-module.lua',OLD/'source-controls.json',R/'tools/audit/run_mesen_isolated.py',R/'tools/run_mesen.py',Path(sys.executable),emu,emu.parent/'MesenCore.dll',emu.parent/'settings.json',Path('C:/Mesen2/settings.json')}
        files|={B/'source'/p for p in source};files|={p for p in a.output.rglob('*')if p.is_file()}
        pending=[Path(__file__)];seen=set()
        while pending:
            f=pending.pop()
            if f in seen:continue
            seen.add(f);files.add(f)
            for node in ast.walk(ast.parse(f.read_text())):
                mods=[node.module]if isinstance(node,ast.ImportFrom)else [q.name for q in node.names]if isinstance(node,ast.Import)else []
                for name in mods:
                    if name:
                        dep=R/'tools/audit'/(name.split('.')[0]+'.py')
                        if dep.is_file():pending.append(dep)
        put(a.output/'bindings.json',{str(p.resolve()):sha(p)for p in sorted(files)})
        proof=dict(prepared=True,native_run=False,native_granted=False,ROM_sha256=SHA,identity=cfg['identity'],mode_numeric=1,profile='mega-hard-primary-support',cases=6,maximum_native_launches=1,maximum_workers=1,wall_frames=4000,host_seconds=1200,bindings=len(files),bindings_sha256=sha(a.output/'bindings.json'),script_sha256=sha(native/'run.lua'),assembled_controls_sha256=sha(a.output/'assembled-controls.json'),source_controls_sha256=sha(a.output/'source-controls.json'),tool_sha256=sha(__file__),limits='Prepared only: staged powered tier/owned resources/arenas and a complete small energy capsule; real selection/primary/Rush movement/direct debit/refill intended but unrun. Descending-player contact is an explicit before-subphase setup, not a natural jump. No Bass shared seven-special-gallery duplication, acquisition, actual damage contact, tier2, Easy, Proto native/presentation/audio or full-pool native coverage. No game/settings/default changes. Native grant required.')
        put(a.output/'readiness.json',proof);print(json.dumps(proof,indent=2))
    except BaseException as error:
        put(a.output/'failure.json',dict(native_run=False,error=repr(error),traceback=traceback.format_exc(),tool_sha256=sha(__file__)))
        (a.output/'failed-tool.py').write_bytes(Path(__file__).read_bytes());raise


if __name__=='__main__':
    main()
