"""Replay, verify and deliver the source-qualified Getsu nightly."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

import check_getsu_giant_current_1110 as Current
from deliver_giant_impact_1110 import NIGHTLY, SMALL, SYMBOLS, packet_result
from deliver_manual_title_1110 import ASSET, REPO, ips_for, mini_evidence, same_mini
from nightly_patch_guard_v1 import check
from prepare_selected_native_packet_v1 import prepare, sha


R, PARENT = Current.R,Current.PIN
PIN = '095c164a574479401f284c1669264034404b83cb2e1d6cdc4a1f5ef37dcafe79'
PROOF = R/'build/getsu-giant-current-1110/proof.json'
NATIVE = R/'build/getsu-current-native-1110'
OLD = Current.BASE.parent
REGRESSIONS = ('contact','full11','mini')
GETSU = ('idle','route')


def qualified(rom, proof):
    q = Current.Public.read(proof)
    assert q['passed'] and not q['ROM_written']
    assert q['parent_SHA256']==PARENT and q['expected_memory_only_SHA256']==PIN
    Current.Public.check_paths(q['bindings'])
    parent = Current.BASE.read_bytes()
    raw = rom.read_bytes()
    assert Current.SHA(parent)==PARENT and Current.SHA(raw)==PIN
    assert len(q['patches'])==60 and Current.Public.apply(parent,q['patches'])==raw
    return raw


def checked_packet(packet,rom,pin):
    q = packet_result(packet,rom,pin)
    assert q['controller_only'] and not q.get('script_RAM_writes',False)
    return q


def stage(output, native, proof):
    rom = native/'candidate.nes'
    qualified(rom,proof)
    assert not output.exists()
    output.mkdir()
    for name in REGRESSIONS:
        prior = OLD/name
        checked_packet(prior,Current.BASE,PARENT)
        source = (prior/'controller.lua').read_text(encoding='utf-8')
        assert source.count(PARENT)==1
        refs = {Path(__file__),proof,prior/'controller.lua',prior/'ready.json',
                prior/'capture/binding.json',prior/'capture/result.json'}
        ready = Current.Public.read(prior/'ready.json')
        prepare(output/name,rom,source.replace(PARENT,PIN),refs,expected=PIN,
                timeout=ready['timeout'],allow_interactive=True,rom_symbols=SYMBOLS,
                scope=f'Unchanged delivered {name} controller on exact Getsu candidate.')


def getsu_checks(root, rom, *, prefix=''):
    idle, route = [checked_packet(root/(prefix+name),rom,PIN) for name in GETSU]
    for q in (idle,route):
        assert (q['terminal']['raw'],q['terminal']['world'],q['terminal']['lives'],q['terminal']['engine'])==(42,1,2,8)
        assert q['live_render']['hardware_chr_bank']==990 and len(q['live_render']['parts'])==5
        assert q['exterior']['name'].strip()=='GETSU' and q['exterior']['backdrop']==34
    assert idle['active_frames']==idle['idle_main_updates']==120 and idle['idle_without_main']==0
    assert idle['terminal']['level']==1 and (idle['terminal']['x'],idle['terminal']['y'])==(40,176)
    assert route['terminal']['level']==2 and route['flag'] and route['underground']
    assert len(route['caps'])==4 and len(route['pits'])==3
    assert route['first_attack'] and route['sword_hit']['target']['id']==6
    assert route['sword_hit']['target']['state']&0x20
    assert all(0<=q['missed_reads']<q['active_frames'] for q in (idle,route))
    return {name:dict(active_frames=q['active_frames'],missed_reads=q['missed_reads'],
                      updates=q['terminal']['updates'],draws=q['terminal']['draws'],
                      terminal_level=q['terminal']['level'],lives=q['terminal']['lives'],
                      result_SHA256=sha(root/(prefix+name)/'capture/result.json'))
            for name,q in zip(GETSU,(idle,route),strict=True)}


def candidate_evidence(native, regressions, proof):
    rom = native/'candidate.nes'
    raw = qualified(rom,proof)
    getsu = getsu_checks(native,rom)
    contact,full,mini = [checked_packet(regressions/name,rom,PIN) for name in REGRESSIONS]
    for name in REGRESSIONS:
        old=(OLD/name/'controller.lua').read_text(encoding='utf-8')
        assert (regressions/name/'controller.lua').read_text(encoding='utf-8')==old.replace(PARENT,PIN)
    combat = contact['combat']
    assert contact['terminal']['lives']==2 and contact['terminal']['x']>=400 and not contact['jumps']
    assert any(e['id']==6 for e in combat['defeats']) and combat['injury_calls']==0
    assert len(combat['shatters'])>=7 and {0x51,0xc0,0xc1}<=set(e['metatile'] for e in combat['original_materials'])
    assert full['terminal']['level']==2 and full['terminal']['lives']==2 and full['terminal']['engine']==8
    assert full['flag'] and all(str(x) in full['milestones'] for x in (944,1136,1424,2480))
    assert mini['full_stage']
    mini_proof = mini_evidence(regressions/'mini',PIN)
    same_mini(mini_evidence(OLD/'mini',PARENT),mini_proof)
    return raw,dict(Getsu=getsu,Giant=dict(shatters=len(combat['shatters']),lives=full['terminal']['lives'],
                    terminal_level=full['terminal']['level']),Mini_cadence=mini_proof['cadence'],
                    regression_SHA256={n:sha(regressions/n/'capture/result.json') for n in REGRESSIONS})


def deliver(output, native, regressions, proof):
    raw,evidence = candidate_evidence(native,regressions,proof)
    before=check(NIGHTLY)
    assert before['ROM_sha256']==PARENT
    assert not any(NIGHTLY.with_suffix(ext).exists() for ext in ('.lbl','.dbg','.dbg.gz'))
    output.mkdir(exist_ok=True)
    assert not any((output/p).exists() for p in (ASSET,'verified-delivery.json','downloads-idle','downloads-route'))
    patch=ips_for(raw)
    try:
        NIGHTLY.write_bytes(raw)
        assert check(NIGHTLY)['ROM_sha256']==PIN and NIGHTLY.read_bytes()==raw
        for name in GETSU:
            packet=output/f'downloads-{name}'
            Current.stage_packet(packet,NIGHTLY,proof,name)
            assert (packet/'controller.lua').read_bytes()==(native/name/'controller.lua').read_bytes()
            subprocess.run([sys.executable,'-B',str(SMALL),'--files','10',str(packet/'run.py')],check=True)
        actual=getsu_checks(output,NIGHTLY,prefix='downloads-')
        for name in GETSU:
            old,new=(tuple(q[k] for k in ('active_frames','missed_reads','updates','draws','terminal_level','lives'))
                     for q in (evidence['Getsu'][name],actual[name]))
            assert old==new,(name,old,new)
        (output/ASSET).write_bytes(patch)
        q=dict(installed=True,Downloads_launch_verified=True,backup_created=False,IPS_roundtrip=True,
               ROM_SHA256=PIN,previous_ROM_SHA256=PARENT,IPS_SHA256=sha(output/ASSET),before=before,
               after=check(NIGHTLY),proof=str(proof),proof_SHA256=sha(proof),candidate=evidence,actual_Downloads=actual)
        (output/'verified-delivery.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    except (Exception,KeyboardInterrupt):
        NIGHTLY.write_bytes(Current.BASE.read_bytes())
        assert check(NIGHTLY)['ROM_sha256']==PARENT
        raise
    print('Verified exact Getsu Downloads ROM and clean-base IPS',PIN,flush=True)


def publish(output, native, regressions, proof):
    raw,evidence=candidate_evidence(native,regressions,proof)
    receipt=output/'verified-delivery.json'
    q=Current.Public.read(receipt)
    patch=output/ASSET
    assert q['Downloads_launch_verified'] and q['IPS_roundtrip'] and not q['backup_created']
    assert q['proof_SHA256']==sha(proof) and q['candidate']==evidence
    assert q['ROM_SHA256']==check(NIGHTLY)['ROM_sha256']==PIN and NIGHTLY.read_bytes()==raw
    assert q['actual_Downloads']==getsu_checks(output,NIGHTLY,prefix='downloads-')
    assert q['IPS_SHA256']==sha(patch) and patch.read_bytes()==ips_for(raw)
    idle,route=(evidence['Getsu'][name] for name in GETSU)
    notes=output/'release-notes.txt'
    notes.write_text('Current MMC5 work-in-progress nightly.\n\n'
                     'Apply this IPS to clean, headered Super Mario Bros. (World).\n'
                     'Getsu Fuma is available after the Castlevania III alternatives in Simon’s Select cycle. '
                     'His donor movement, sword, and sprites are integrated. The verified native route cleared '
                     '1-1 with both lives, and the Mini Mario and Mega Giant routes passed regression.\n'
                     f'Getsu still missed {idle["missed_reads"]} input reads during {idle["active_frames"]} idle frames '
                     f'and {route["missed_reads"]} during {route["active_frames"]} active 1-1 frames.\n'
                     f'Patched ROM SHA-256 {PIN}\n',encoding='utf-8')

    def release(endpoint):
        return json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/releases/{endpoint}'],encoding='utf-8'))

    current=release('tags/Current')
    existing,=current['assets']
    assert current['tag_name']=='Current' and existing['name']==ASSET
    digest='sha256:'+q['IPS_SHA256']
    if existing['digest']!=digest:
        subprocess.run(['gh','release','upload','Current',str(patch),'--clobber','--repo',REPO],check=True)
    subprocess.run(['gh','release','edit','Current','--latest','--notes-file',str(notes),'--repo',REPO],check=True)
    latest=release('latest')
    asset,=latest['assets']
    assert latest['tag_name']=='Current' and latest['id']==current['id']
    assert (asset['name'],asset['digest'],asset['size'])==(ASSET,digest,patch.stat().st_size)
    q.update(release_tag='Current',release_is_latest=True,sole_asset=ASSET,release_asset_digest=digest,
             final_patch_guard=check(NIGHTLY))
    receipt.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print('Verified sole Current asset and Latest status',digest,flush=True)


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('action',choices=('stage','verify','deliver','publish'))
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--native',type=Path,default=NATIVE)
    cli.add_argument('--proof',type=Path,default=PROOF)
    cli.add_argument('--regressions',type=Path)
    args=cli.parse_args()
    out,native,proof=args.output.resolve(),args.native.resolve(),args.proof.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    if args.action=='stage':
        assert args.regressions is None
        stage(out,native,proof)
        return
    regressions=args.regressions.resolve() if args.regressions else out
    if args.action=='verify':
        _,evidence=candidate_evidence(native,regressions,proof)
        print(json.dumps(evidence),flush=True)
    else:
        assert args.regressions
        (deliver if args.action=='deliver' else publish)(out,native,regressions,proof)


if __name__=='__main__':
    main()
