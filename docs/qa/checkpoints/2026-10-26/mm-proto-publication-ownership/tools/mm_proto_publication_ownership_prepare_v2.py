"""Audit/source-model and prepare ONE unlaunched731450 ownership diagnostic."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys

from check_tmnt_render_oa import address, location
from check_tmnt_audio_fallback_oc import qualified
from link_pit_rygar_sophia_audit_cpu import scoped_load
from observe_chip_committed_write import lua

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = D / 'mm-proto-clean-menu-candidates-v1/clean-menu-irq'
REFERENCE = D / 'root-presentation450-731-v1'
EXPECTED = '731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def put(p, value):
    Path(p).write_text(json.dumps(value, indent=2) + '\n')


def model():
    # One-byte design model, NOT compiled host execution/qualification.
    # phase0body/phase1shot; bit7 identifies a complete unconsumed source.
    # Busy corresponds to the existing Main NmiDisable negative ownership.
    # Construction is an observer/model field, not another proposed RAM byte.
    initial = (0, False, None, ())
    todo, visited, transitions, acknowledged = [initial], {initial}, 0, 0
    while todo:
        value, busy, construction, history = todo.pop()
        choices = [('begin', (value, True, None, history)),
                   ('reset/replacement', (0, busy, None, ())),
                   ('release/no-draw-catchup', (value, False, construction, history)),
                   ('partial-source-edit', (value, busy, construction, history))]
        if busy:
            choices += [('DrawAll-begin', (value & 1, True, value & 1, history))]
            if construction is not None:
                choices += [('DrawAll-complete', (construction | 128, True, None, history))]
            # A genuine lag NMI transfers no OAM and cannot advance state.
            choices += [('lag-NMI', (value, True, construction, history))]
        else:
            if value & 128:
                h = (history + (value & 1,))[-2:]
                assert len(h) < 2 or h[0] != h[1], h
                choices += [('completed-DMA-ack', (value ^ 129, False, construction, h))]
                acknowledged += 1
            else:
                choices += [('stale-DMA', (value, False, construction, history))]
        for _, z in choices:
            transitions += 1
            assert z[0] in (0, 1, 128, 129)
            if z not in visited:
                visited.add(z)
                todo.append(z)
    return dict(passed=True,source_model_only=True,compiled_game_patch=False,
                finite_states=len(visited),transitions=transitions,acknowledged_edges=acknowledged,
                property='Within an unreset lifecycle, acknowledged complete tagged images alternate priority. Lag/stale DMA and no-draw catchups do not advance it; overwritten complete constructions keep the same unconsumed phase.',
                limits='Interleaving/design model only. Partial OAM edits retain an allocation tag but do not prove an intact body/shot image. Real source writer/lifecycle instrumentation and later assembled/native qualification remain necessary.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    assert not a.output.exists() and not a.output.resolve().is_relative_to(R)
    assert sha(PARENT / 'candidate.nes') == EXPECTED
    command = [sys.executable, '-B', str(R / 'tools/audit/presentation_timing_prepare_v1.py'),
               '--candidate', str(PARENT), '--expected-ROM-sha256', EXPECTED, '--output', str(a.output)]
    z = subprocess.run(command, cwd=R, capture_output=True, text=True)
    if not a.output.exists():
        a.output.mkdir(parents=True)
    put(a.output / 'base-preparer.json', dict(command=command,exit=z.returncode,stdout=z.stdout,stderr=z.stderr))
    assert z.returncode == 0, z.stdout + z.stderr
    base = json.loads((a.output / 'readiness.json').read_text())
    shutil.copyfile(a.output / 'readiness.json', a.output / 'base-readiness.json')
    shutil.copyfile(a.output / 'run.lua', a.output / 'base-run.lua')
    cfg = json.loads((a.output / 'config.json').read_text())
    assert (a.output / 'prefix.csv').read_bytes() == (REFERENCE / 'prefix.csv').read_bytes()
    old = json.loads((REFERENCE / 'config.json').read_text())
    assert all(cfg[n] == old[n] for n in ['limit', 'hooks', 'ram', 'smc'])
    b = scoped_load(PARENT / 'candidate.nes')
    q = qualified(PARENT / 'candidate.nes')
    state_names = ['NmiDisable','NmiSkipped','ShouldSkipDrawSprites','FramesSinceLastSpriteDraw',
                   'FrameCounter','SelectedCharacter','ProtoVariant','OperMode','OperMode_Task',
                   'GameEngineSubroutine','CrossoverMenuState','DisableScreenFlag','GamePauseStatus',
                   'MmDeathFlag','MmSliding','ObjectMetasprite','SprObject_SprAttrib','Player_X_Position',
                   'Player_Y_Position','Player_PageLoc','Player_Y_HighPos','AreaPointer','WorldNumber',
                   'LevelNumber','NumberofLives','GuestOamRotationActive','RgOamFirst','RgOamRotation',
                   'RgOamUsed','RgOamPlayerStart','CurrentOAMOffset','SsDrawFirst','SpriteShuffleOffset',
                   'ReloadCHRBank','X5WideChrActive','CurrentBank','CurrentBankC']
    ordinary_names = ['MmBulletType','MmBulletAge','MmBulletX','MmBulletPage','MmBulletY','MmBulletDir']
    special_names = ['RgShotType','RgShotAge','RgShotX','RgShotPage','RgShotY','RgShotDir']
    hooks = {}
    for alias, name in [('GameLoopEntry','GameLoop'),('DrawAll','DrawAllMetasprites'),
                        ('RosterReady','RosterOamReady'),('MoveAll','MoveAllSpritesOffscreen'),
                        ('InitializeArea','InitializeArea'),('InitializeGame','InitializeGame'),
                        ('MegaClear','MegaManClearState')]:
        pc, off = address(b,name), location(b,name)
        hooks[alias] = dict(pc=pc,bank=(off-16)//8192,bytes=list(b['raw'][off:off+3]))
    # Preserve a genuine terminal RTS, rather than an invented alias.
    release = q[('GameLoop','PauseSkip')]
    goff = location(b,'GameLoop') + release - address(b,'GameLoop')
    assert release == 0x8350 and b['raw'][goff:goff+6] == bytes.fromhex('a9008d390160')
    hooks['GameLoopDone'] = dict(pc=release+5,bank=126,bytes=[0x60])
    hooks |= {n:cfg['hooks'][n] for n in ['NmiEntry','NmiReturn','DmaComplete']}
    ownership = dict(out=cfg['out'],limit=450,ROM_sha256=EXPECTED,hooks=hooks,
                     ram={n:address(b,n) for n in state_names+ordinary_names+special_names},
                     state_names=state_names,ordinary_names=ordinary_names,special_names=special_names)
    module = R / 'tools/audit/mm_proto_publication_ownership_observer_v1.lua'
    text = module.read_text()
    assert not re.search(r'\bemu\.(?:write\w*|setState|setInput|loadSavestate|reset)\s*\(',text)
    assert not re.search(r'\b(?:removeMemoryCallback|removeEventCallback)\b',text)
    literal_reads = set(re.findall(r"r\('([^']+)'\)",text))
    assert literal_reads <= ownership['ram'].keys()
    sys.path.insert(0,str(D/'final-tmnt-items-v1/lua-parser-deps-v1'))
    from luaparser import ast
    ast.parse(text)
    ast.parse((R/'tools/audit/presentation_timing_preflight_v1.lua').read_text())
    put(a.output / 'ownership-config.json',ownership)
    script = 'PUBLICATION_OWNERSHIP='+lua(ownership)+'\ndofile('+lua(module.as_posix())+')\n'+(a.output/'base-run.lua').read_text()
    ast.parse(script)
    (a.output / 'run.lua').write_text(script)
    put(a.output / 'design-state-model.json',model())
    source = PARENT / 'source'
    # This is a bounded declared-source ownership inventory, not a universal
    # assertion about all possible indirect-pointer reads/writes in every ROM.
    assert not [n for n,v in q.items() if len(n)==1 and v==0x5ff8]
    source_paths = [p for p in source.rglob('*') if p.suffix in ['.s','.inc']]
    refs = []
    for p in source_paths:
        for i,line in enumerate(p.read_text(errors='strict').splitlines(),1):
            if re.search(r'\$5ff8\b',line,re.I):
                refs.append(dict(file=str(p.relative_to(source)),line=i,text=line))
    assert not refs
    assert 'NativeStatusPending=$5ff6' in (source/'src/bill_native_rare.s').read_text()
    assert 'NativeStatusCursor=$5ff7' in (source/'src/bill_native_rare.s').read_text()
    profiles=(source/'src/x5_profiles.s').read_text()
    assert 'sta $5f00,x' in profiles and 'ldx #15' in profiles and 'cpx #16' in profiles
    parodius=(source/'src/parodius_adapter.s').read_text()
    assert 'ldx #223' in parodius and 'sta $5f00,x' in parodius
    facts = dict(ROM_sha256=EXPECTED,source_manifest_sha256=sha(PARENT/'source-manifest.json'),
                 Main_entry=hooks['GameLoopEntry'],Main_release=dict(pc=release,bank=126,bytes='a9008d390160',store_callback_pc=release+5),
                 actual_postDMA=hooks['DmaComplete'],new_byte_proposal=dict(address=0x5ff8,allocated=False,existing_named_aliases=0,literal_source_references=0,
                 prior_globals='5FF0..5FF5 bounce;5FF6/5FF7 NativeStatusPending/Cursor',
                 full_clear='X5ProfilesNewGame writes5F00..5FFF. Variant save/restore covers5FE0..5FEF only. PnEnsure persistent clear stops5FDF.',
                 cold_init_needed='X5ColdInit currently clears5FE0..5FEF only; a new lifecycle byte needs an explicit cold/reset clear.'),
                 existing_ack=False,source_page_protection='GameLoop entry FF -> complete Main release0; regularNMI DEC0->FF; lagNMI retainsFF and transfers noOAM.',
                 catchup='At most one immediate GameLoop. TerrainCatchupPending sets draw-skip unless queue6 is pending. GameCore still forcesDrawAll when FramesSinceLastSpriteDraw>=13.',
                 direct_writer_limit='RyuPlatformOriginalDrawVine and original DrawBrickChunks/DumpTwoSpr can write page2 before DrawAll. MoveAll/lives/title also replace OAM outside DrawAll. A DrawAll-only tag is therefore not a complete all-mode source provenance proof.',
                 observer='Additional static-startup callbacks only; original450 input/PPU capture, full256 DMA destination, masks, NMI/IRQ/SMC/register guards and finite thresholds unchanged.',
                 ack_cost_proposal=dict(inline_bytes=13,foreign_or_no_pending_cycles=7,pending_owned_cycles=16,placement='RegularNMI after AudioUpdate, before BankPRGA/ExitNMI, so no added preDMA/PPUMASK/HUD-arm work. No claim of zero common cost.'),
                 native_run=False,allocation=False,implementation=False)
    put(a.output / 'source-facts.json',facts)
    put(a.output / 'source-observer-controls.json',dict(passed=True,source_only=True,native_run=False,
        Lua_parse=True,literal_ram_bindings_complete=True,only_startup_callback_registration=True,observer_emulation_mutations=False,
        original_observer_module_sha256=sha(R/'tools/audit/presentation_timing_preflight_v1.lua'),
        original_config_hooks_RAM_SMC_limit_and_controller_prefix_exact=True,
        limits='Source/schema/AST controls only; actual callback lifecycle mocks and native observations are separate. No new byte/code is allocated or linked.'))
    plan = '''ONE UNLAUNCHED READ-ONLY OWNERSHIP DIAGNOSTIC, exact installed731.\nSame450actualPPU bound, same fixed controller prefix as actual731reference.\nThe original timing observer/module/guards and full raw275PPU captures remain\nunchanged. Additional all-mode observations record every actual page2write\n(value/address/callbackPC/physicalbank/PPU/Main/construction), initialsource,\ncompletedRoster/Main images and real release bank126at8355, every NMI's\nhardware-stacked interruptPC/P/SP and protected-source fields, actual live\nordinary/special slots, every DMA's full source/writer epochs and physical\nfull256destination, and visible cutoffs. Serialization precedes assertions.\nCallbacks install only at startup; no runtime registration/removal.\n\nThis is diagnosis, not qualification of an unimplemented alternator. It can\ndistinguish a normal completedDrawAll, noDraw catchup retaining that image,\nsource overwrite/replacement before release, stale transfer and Main interrupted\nafter source completion but before release. CallbackPC is labeled literally,\nnot fabricated as a proven instruction-startPC. All exact hardware assertions\nremain in the unchanged original module. No byte masks/phase/workload/clock\nchanges, source/default/settings mutation or native grant. At mostONE launch\nmay be requested later after ROOT review; no retries or gameplay extension.\n'''
    (a.output/'PLAN.txt').write_text(plan)
    # The source observer can be slower on the host; emulated450/input/control
    # scope is unchanged. This is recorded explicitly, never a hidden retry.
    cmd=base['command'][:]
    cmd[cmd.index('--timeout')+1]='1200'
    deps={Path(p) for p in base['bindings']}
    deps|={Path(__file__),module,a.output/'base-readiness.json',a.output/'base-run.lua',a.output/'base-preparer.json',
           a.output/'ownership-config.json',a.output/'design-state-model.json',a.output/'source-facts.json',
           a.output/'source-observer-controls.json',a.output/'PLAN.txt',REFERENCE/'readiness.json',REFERENCE/'native-receipt.json',REFERENCE/'prefix.csv'}
    deps|={p for p in a.output.iterdir() if p.is_file() and p.name!='readiness.json'}
    final=base|dict(command=cmd,native_grant=False,native_run=False,maximum_launches=1,maximum_workers=1,
                    diagnostics_only=True,publication_aware_alternator_implemented=False,
                    matched_reference_ROM_sha256=EXPECTED,extra_readonly_observer=True,emulated_input_scope_unchanged=True,
                    host_timeout_seconds=1200,bindings={str(p.resolve()):sha(p) for p in sorted(deps)},limits=plan)
    put(a.output/'readiness.json',final)
    catalog={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(a.output.iterdir()) if p.is_file()}
    put(a.output/'catalog.json',catalog)
    proof=dict(passed=True,prepared_only=True,diagnostic_only=True,native_run=False,native_grant=False,
               game_implementation=False,new_RAM_allocation=False,ROM_sha256=EXPECTED,
               original_input_and_guard_scope_exact=True,maximum_launches=1,readiness_sha256=sha(a.output/'readiness.json'),
               catalog_sha256=sha(a.output/'catalog.json'),binding_count=len(final['bindings']),
               source_fact_sha256=sha(a.output/'source-facts.json'),design_model_sha256=sha(a.output/'design-state-model.json'),
               actual_callback_mock_completed=False,preparer_sha256=sha(__file__),observer_sha256=sha(module),
               limits='Prepared diagnostic only, not native readiness qualification until the separate actual observer-callback mock passes. No common-cost waiver or displayed visibility guarantee.')
    put(a.output/'preparation.json',proof)
    print(json.dumps(proof,indent=2))


if __name__=='__main__':
    main()
