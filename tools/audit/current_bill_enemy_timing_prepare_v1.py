"""Prepare one passive Bill9ea enemy/background timing replay; never launch."""
from pathlib import Path
import argparse
import contextlib
import csv
import io
import json
import re
import sys

import current_bill_passive_timing_prepare_v1 as timing
import current_roster_compact_11_v1 as route

R=route.ROOT
B=R/'build'
EXPECTED='9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
ADDED=['EnemiesAndLoopsCore','Mmc5GroundGoombaTerrain','PlayerEnemyCollision','AreaParserTaskHandler']


def decoded_direct_JSRs(rom,raw,entries):
    """Actual3-byte source instruction spans; never raw data byte matches.

    A source JSR may cross a window whose physical callee is selected by a
    prior mapper write. Actual measured entry separately requires that exact
    callee bank/opcode. Its stacked return still must follow this real JSR
    and match the real caller bank. This is not a bank/PC wildcard.
    """
    segs={};spans=[]
    for line in rom.with_suffix('.dbg').read_text().splitlines():
        if line.startswith(('seg\t','span\t')):
            z=dict(v.split('=',1)for v in line.split('\t',1)[1].split(',')if '=' in v)
            if line.startswith('seg\t'):segs[z['id']]=z
            else:spans.append(z)
    found={h['name']:{}for h in entries}
    for z in spans:
        if 'type' in z or int(z['size'],0)!=3:continue
        g=segs[z['seg']]
        if 'ooffs' not in g:continue
        off=int(g['ooffs'],0)+int(z['start'],0);pc=int(g['start'],0)+int(z['start'],0)
        if not(16<=off<16+128*8192 and 0x8000<=pc<=0xfffc):continue
        code=list(raw[off:off+3])
        if code[0]!=0x20:continue
        operand=code[1]+256*code[2]
        for h in entries:
            if operand==h['pc']:
                owner=dict(bank=(off-16)//8192,bytes=code)
                owners=found[h['name']].setdefault(str(pc+3),[])
                if owner not in owners:owners.append(owner)
    return found


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args()
    out=a.output.resolve();assert out.is_relative_to(B.resolve()) and not out.exists()
    parent=B/'verification/bill-early-cache-pair-ready-v1/candidate9ea'
    parent_ready=json.loads((parent/'ready.json').read_text());parent_profile=json.loads((parent/'profile-config.json').read_text())
    result=json.loads((parent/'result.json').read_text());review=json.loads((parent/'review.json').read_text())
    assert result['passed'] and review['passed'] and result['ROM_sha256']==EXPECTED and result['frames']==6091
    inputs=parent/'inputs.csv';saved=list(csv.DictReader(inputs.open(newline='')))
    assert len(saved)==result['polls']==6090 and [int(q['poll'])for q in saved]==list(range(1,6091))
    rom=B/'bill_early_cache.nes';assert route.sha(rom)==EXPECTED
    observer=B/'bill_early_cache_timing_full.lua'
    assert route.sha(observer)==parent_ready['passive_timing']['observer_successor']['successor_sha256']
    options=argparse.Namespace(rom=rom,output=out,expected_sha256=EXPECTED,identity='bill',mode='hard',frames=8000,
        policy=R/'tools/playthroughs/roster_samus_contra.lua',replay=inputs)
    with contextlib.redirect_stdout(io.StringIO()):route.prepare(options)
    ready=json.loads((out/'ready.json').read_text());cfg=ready['config']
    assert cfg['replay']==inputs.as_posix() and cfg['limit']==8000
    assert cfg['character']==3 and cfg['variant']==0 and cfg['mode_value']==1
    raw,syms,address,location,hook=route.linked(rom)
    profile=json.loads(json.dumps(parent_profile));profile['output']=out.as_posix()+'/'
    assert profile['ROM_sha256']==EXPECTED and profile['first_frame']==3500 and profile['last_frame']==3560
    assert profile['dma_complete']==cfg['hooks']['dma_complete']
    def bound(name):
        off=location(name)
        return dict(name=name,symbol=name,pc=address(name),banks=[(off-16)//8192],bytes=list(raw[off:off+3]))
    entries=[bound(n)for n in ADDED]
    assert [(h['pc'],h['banks'])for h in entries]==[(0xa260,[0]),(0xbf3d,[0]),(0x9659,[126]),(0xa09b,[2])]
    callers,smc,closure=timing.source_call_closure(rom,raw,entries,address('JumpEngine'))
    closure['algorithm']='Same qualified decoded instruction/stack-neutral/tail/JumpEngine closure, freshly applied to4newentries. ActualsourceJSRcross-window candidates are explicitly added below and still require actualcalleeentrybank/opcodes.'
    direct=decoded_direct_JSRs(rom,raw,entries);added_direct=[]
    for name,rets in direct.items():
        for ret,owners in rets.items():
            for owner in owners:
                if owner not in callers[name].get(ret,[]):
                    callers[name].setdefault(ret,[]).append(owner)
                    added_direct.append(dict(function=name,return_pc=int(ret),owner=owner,
                        qualification='Compileduntyped3BJSRspan with literal measuredentryoperand. Runtimeactualentry provescalleephysicalbank; runtimecallerowner/SP/bytes remainstrict.'))
    assert all(callers[n]for n in ADDED)
    controls=0
    for name,rets in callers.items():
        assert '65535' not in rets and '65535' not in smc[name]
        for ret,owners in rets.items():
            for owner in owners:
                off=16+owner['bank']*8192+((int(ret)-3)&8191)
                assert list(raw[off:off+3])==owner['bytes'] and owner['bytes'][0]==0x20
                accept=lambda bank,code:any(q['bank']==bank and q['bytes']==code for q in owners)
                assert accept(owner['bank'],owner['bytes']) and not accept(-1,owner['bytes'])
                assert not accept(owner['bank'],[0x4c]+owner['bytes'][1:])
                changed=owner['bytes'][:];changed[1]^=1;assert not accept(owner['bank'],changed)
                controls+=1
    profile['functions']+=entries;profile['source_callers'].update(callers);profile['smc_targets'].update(smc)
    for rets in callers.values():
        for ret,owners in rets.items():
            for owner in owners:
                if owner not in profile['returns'].get(ret,[]):profile['returns'].setdefault(ret,[]).append(owner)
    assert len(profile['functions'])==21 and len({(q['pc'],tuple(q['banks']))for q in profile['functions']})==21
    # Actualresident GameCore loop: six real slots, including inactive loader paths.
    word=lambda v:[v&255,v>>8]
    loop=[0xa2,0,0x86,address('ObjectOffset'),0x20]+word(address('EnemiesAndLoopsCore'))+[0x20]+word(address('FloateyNumbersCore'))+[0xe8,0xe0,6,0xd0]
    start=location('GameCoreRoutine');body=raw[start:start+256]
    assert body.count(bytes(loop))==1
    at=start+body.index(bytes(loop));pc=address('GameCoreRoutine')+at-start
    tree=dict(GameLoop=bound('GameLoop'),GameCoreRoutine=bound('GameCoreRoutine'),
        six_actor_loop=dict(bank=126,pc=pc,bytes=loop,semantics='LDX0;STXObjectOffset;JSREnemiesCore;JSRFloatey;INX;CPX6;BNE. Countsincludeinactive slots/enemyloadwork.'),
        RunNormalEnemies=bound('RunNormalEnemies'),new_entries=entries,
        source_scope='EnemyCore contains AI/graphics/boundingboxes/loaders. Terrainwrapper andplayercontact are nested children; AreaParser is a separate main-threadtail. EnemyIDs are not individuallylogged, so terrainwrapper counts are not asserted allGoomba-fastpath.')
    text=observer.read_text();assert not re.search(r'emu\.(?:write\w*|setInput|setState|loadSavestate|reset|stop)\s*\(',text)
    assert text.count('emu.addMemoryCallback(')==6 and text.count('emu.addEventCallback(')==1
    original=(out/'run.lua').read_text();anchor='dofile('+route.lua(route.SCRIPT.as_posix())+')\n'
    insertion='BILL_PASSIVE_TIMING='+route.lua(profile)+'\n'+'dofile('+route.lua(observer.as_posix())+')\n'
    assert original.count(anchor)==1
    generated=original.replace(anchor,insertion+anchor);assert generated.replace(insertion,'',1)==original
    (out/'run.lua').write_text(generated,encoding='utf-8',newline='\n')
    (out/'profile-config.json').write_text(json.dumps(profile,indent=2)+'\n')
    (out/'command.json').write_text(json.dumps(ready['command'],indent=2)+'\n')
    prep=dict(passed=True,native_run=False,new_span_entries=4,total_span_entries=21,
        source_JSR_positive_negative_controls=controls,new_direct_cross_window_owners=added_direct,
        new_source_closure=closure,compiled_call_tree=tree,
        inherited17_binding='Exactsame9eaROM/parentprofilebindings; original17entry/caller/SMC/ISRmetadata inheritedbyte-for-byte. Onlyoutputpath and4entry/returntables added.',
        observer_body_unchanged_sha256=route.sha(observer),shared_route_body_unchanged_sha256=route.sha(route.SCRIPT),
        fixture_scope='Actualsaved9ea6090pollreplay,original8000limit/control1-2endpoint. Readonlyhooks; no game/resource/outcome seeds. Stillrequiresnativeexecution/equalityreview.',
        first_native_qualification='FutureROOTgrantonly; no native result implied by metadata controls.')
    (out/'prepare-controls.json').write_text(json.dumps(prep,indent=2)+'\n')
    ready['passive_enemy_timing']=dict(new_functions=ADDED,window=[3500,3560],expected_data_rows=61,
        CSV_max_rows=200,CSV_max_bytes=1048576,spans=21,startup_static=True,
        source_controls=str(out/'prepare-controls.json'),parent_recorded_result_sha256=route.sha(parent/'result.json'),
        parent_window_review_sha256=route.sha(parent.parent/'timing-review.json'),
        exact_saved6090polls=True,expected_route='Same9ea6091wall/5142updates/3823DMA/controlled1-2; actualtrace/input/PPUequalitymustbereviewed,notassumed.',
        labels='Fullroute replaywithboundedtiming,notdeliberate3560cutoff. Summaryaloneisnotroutepass. Samecensoring/warmup/ISR-nestinglimitsremain.',
        analysis_goal='Split existingMainexclusive43percent intonativeenemy/load/AI/terrain/playercontact/backgroundparser work. Staticcalltree alone cannotassignitscycles.',
        limitations='No individualEnemyID/per-callstate record; classifytiming byrealroutineonly. NetMainexclusive coverage needscensored/warmupaccounting. NoFPSclaim.',
        no_new_observer_module=True,no_dynamic_callback_registration=True,no_native_grant=True,
        owned_new_file='tools/audit/current_bill_enemy_timing_prepare_v1.py')
    dependencies={Path(p)for p in ready['bindings']}
    dependencies.update({Path(__file__).resolve(),Path(timing.__file__).resolve(),observer,
        out/'profile-config.json',out/'command.json',out/'prepare-controls.json',
        parent/'ready.json',parent/'profile-config.json',parent/'result.json',parent/'review.json',
        parent.parent/'timing-review.json',Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll'),Path('C:/Mesen2/settings.json')})
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f and ('py65' in str(f)or str(R/'tools/audit')in str(f))and Path(f).is_file():dependencies.add(Path(f))
    ready['bindings']={str(p):route.sha(p)for p in sorted(dependencies)}
    (out/'ready.json').write_text(json.dumps(ready,indent=2)+'\n')
    print(json.dumps(dict(prepared=True,native_run=False,ready=str(out/'ready.json'),ready_sha256=route.sha(out/'ready.json'),
        bindings=len(dependencies),return_PCs=len(profile['returns']),new_JSR_owner_controls=controls,
        direct_source_additions=added_direct,command=ready['command']),indent=2))


if __name__=='__main__':main()
