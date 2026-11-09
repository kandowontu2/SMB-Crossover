"""Stage and deliver the exact native-qualified Mega Giant Mario nightly."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from build_storage_guard_v1 import preflight
from deliver_helper_camera_render_1110 import bindings, mini_evidence, read, run
from deliver_shared_side_tank_1110 import same_mini
from deliver_shared_sparse_draw_1110 import ASSET, REPO, installer
from nightly_patch_guard_v1 import check
from prepare_selected_native_packet_v1 import R, prepare, sha
from prepare_shared_gameplay_cadence_1110 import NIGHTLY, SPARSE


PARENT = 'ba3cba071547402fd81398d8b69659fa1b7d20cef9dfcda4df3fe8554ec592de'
PIN = '94650fbc11ede25b9d08e579bdc6b1d6da81fca8f29c6b0c25dadad2e685ede1'
ROM = R/'build/mega-giant-current-native-1110/candidate.nes'
GIANT = ROM.parent/'native-end'
PREVIOUS = R/'build/shared-side-cadence-native-1110'
BASE = PREVIOUS/'candidate.nes'
LEASE = R/'build/mega-giant-chr-lease-1110/proof.json'
LEASE_SHA = 'ee31c25a0183cc18abd3af62a426cec78b0170daaf024c6b4034c5ff5ade989a'
GIANT_READY = '0c97dd51560cb7e5b87de8d875c230752dcbca864d0b8ae4192bbfb4f8303b40'
GIANT_CONTROLLER = '61edca1dd04761085c288ec577159fbb5a1297fd2f43698f1c9b7fd61148cc07'
GIANT_RESULT = 'd044caedc95b52ade6d11aa509c03476e99466963a081b7528f1436fa03b5ff7'
MINI_CONTROLLER = 'df7c04bd90051bddc62fe12147e9406d2d2184363ece7c73b9416da9ff515670'
SYMBOLS = (SPARSE.with_suffix('.lbl'),SPARSE.with_suffix('.dbg'))
HISTORICAL_PREPARER = R/'tools/audit/prepare_mega_giant_f33_native_1110.py'
HISTORICAL_REV = 'a9d0dd94'
HISTORICAL_SHA = 'be75ba43c4a609c206bae2e587a91c49b79cc8b8742ba285430b1b5b27715135'


def giant_evidence(packet, rom, historical=False):
    ready_file, capture = packet/'ready.json', packet/'capture'
    ready, bound, result = (read(p) for p in (ready_file,capture/'binding.json',capture/'result.json'))
    assert Path(ready['ROM']).resolve()==rom.resolve()
    assert ready['ROM_sha256']==bound['ROM_sha256']==result['ROM_sha256']==PIN
    assert ready['emulated_writes'] is False and bound['exit_code']==0 and bound['ready_sha256']==sha(ready_file)
    assert sha(packet/'controller.lua')==GIANT_CONTROLLER
    assert result['passed'] and result['controller_only'] and result['reason']=='active 1-2'
    end,body,flag=result['terminal'],result['body'],result['flag']
    assert (end['world'],end['level'],end['engine'],end['lives'])==(1,2,8,2)
    assert flag['world']==flag['level']==1 and flag['lives']==2 and 3150<=flag['x']<=3200
    assert body['control']&32 and body['chr']==[180,182] and body['sprite_parts']==46 and body['y_extent']==112
    assert all(result['milestones'][str(x)]['x']>=x for x in (482,640,768,944,1136,1424,2480))
    files = dict(ready['bindings'])
    if historical:
        assert sha(ready_file)==GIANT_READY and sha(capture/'result.json')==GIANT_RESULT
        assert files.pop(str(HISTORICAL_PREPARER))==HISTORICAL_SHA
        rel=HISTORICAL_PREPARER.relative_to(R).as_posix()
        historical_blob=subprocess.check_output(['git','show',f'{HISTORICAL_REV}:{rel}'],cwd=R)
        assert hashlib.sha256(historical_blob).hexdigest()==HISTORICAL_SHA
    bindings(files)
    return result


def source_evidence():
    assert sha(BASE)==PARENT and sha(ROM)==PIN and sha(LEASE)==LEASE_SHA
    lease=read(LEASE)
    assert lease['passed'] and lease['parent_SHA256']==PARENT and lease['candidate_SHA256']==PIN
    assert not lease['ROM_written'] and lease['native_clear_SHA256']==GIANT_RESULT
    assert lease['additions']['exact_modified_pages']==list(range(168,215,2))
    immutable={str(BASE) if Path(name)==NIGHTLY and digest==PARENT else name:digest
               for name,digest in lease['bindings'].items()}
    bindings(immutable)
    result=giant_evidence(GIANT,ROM,historical=True)
    prior=mini_evidence(PREVIOUS/'mini',PARENT)
    return result,prior,{Path(name) for name in immutable}


def prepare_mini(out):
    _,_,refs=source_evidence()
    packet=PREVIOUS/'mini'
    controller=packet/'controller.lua'
    assert sha(controller)==MINI_CONTROLLER
    source=controller.read_text(encoding='utf-8')
    assert source.count(PARENT)==1 and PIN not in source
    ready=read(packet/'ready.json')
    refs.update({LEASE,controller,packet/'ready.json',packet/'capture/binding.json',
                 GIANT/'ready.json',GIANT/'controller.lua',GIANT/'capture/binding.json',GIANT/'capture/result.json'})
    out.mkdir(exist_ok=True)
    prepare(out/'mini',ROM,source.replace(PARENT,PIN),refs,expected=PIN,timeout=ready['timeout'],
            allow_interactive=True,rom_symbols=SYMBOLS,
            scope='Exact Mini 1-1 route rebinding only the ROM digest on the Giant candidate.')


def checked_mini(packet, rom):
    ready=read(packet/'ready.json')
    assert Path(ready['ROM']).resolve()==rom.resolve() and ready['emulated_writes'] is False
    source=(PREVIOUS/'mini/controller.lua').read_text(encoding='utf-8')
    assert (packet/'controller.lua').read_text(encoding='utf-8')==source.replace(PARENT,PIN)
    return mini_evidence(packet,PIN)


def prepare_downloads_giant(out, metadata, refs):
    ready=read(GIANT/'ready.json')
    immutable={Path(p) for p in ready['bindings']} - {HISTORICAL_PREPARER}
    refs=refs|immutable|{metadata,LEASE,GIANT/'ready.json',GIANT/'capture/binding.json',
                         GIANT/'capture/result.json',GIANT/'controller.lua',Path(__file__)}
    prepare(out,NIGHTLY,(GIANT/'controller.lua').read_text(encoding='utf-8'),refs,
            expected=PIN,timeout=ready['timeout'],allow_interactive=True,rom_symbols=SYMBOLS,
            scope='Exact Downloads Mega Giant native menu, CHR/OAM, flagpole and full 1-1 into active 1-2.')


def install_and_verify(out, candidate_mini):
    giant,prior,refs=source_evidence()
    assert candidate_mini.name=='mini'
    mini=checked_mini(candidate_mini,ROM)
    same_mini(prior,mini)
    assert check(NIGHTLY)['ROM_sha256']==PARENT
    assert not any((out/name).exists() for name in ('delivery.json','verified-delivery.json','downloads-smoke','downloads-giant'))
    preflight(reserved_files=40,fresh=True)
    out.mkdir(exist_ok=True)
    metadata=out/'candidate-proof.json'
    metadata.write_text(json.dumps(dict(candidate_SHA256=PIN,parent_SHA256=PARENT,
                  CHR_lease_SHA256=LEASE_SHA,candidate_Giant_result_SHA256=GIANT_RESULT,
                  candidate_Mini_result_SHA256=sha(candidate_mini/'capture/result.json')),indent=2)+'\n')
    try:
        installer('install',out,ROM,candidate_mini.parent,PARENT,SPARSE,metadata)
        assert check(NIGHTLY)['ROM_sha256']==PIN
        giant_packet=out/'downloads-giant'
        prepare_downloads_giant(giant_packet,metadata,refs)
        run([str(giant_packet/'run.py')])
        actual=giant_evidence(giant_packet,NIGHTLY)
        assert actual==giant and sha(giant_packet/'capture/result.json')==GIANT_RESULT
        assert check(NIGHTLY)['ROM_sha256']==PIN
        mini_packet=out/'downloads-smoke'
        run([str(mini_packet/'run.py')])
        assert checked_mini(mini_packet,NIGHTLY)==mini
        assert read(mini_packet/'capture/timing.json')==read(candidate_mini/'capture/timing.json')
        installer('finalize',out,ROM,candidate_mini.parent,PARENT,SPARSE,metadata)
        path=out/'verified-delivery.json'
        receipt=read(path)
        assert receipt['ROM_SHA256']==check(NIGHTLY)['ROM_sha256']==PIN
        assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip'] and not receipt['backup_created']
        assert receipt['IPS_SHA256']==sha(out/ASSET)
        receipt.update(Giant_CHR_lease_SHA256=LEASE_SHA,Giant_candidate_result_SHA256=GIANT_RESULT,
                       Giant_Downloads_result_SHA256=sha(giant_packet/'capture/result.json'),
                       Giant_Downloads_binding_SHA256=sha(giant_packet/'capture/binding.json'),
                       Giant_active_missed_reads=actual['active_missed_reads'],Giant_terminal=actual['terminal'],
                       Mini_candidate_packet=str(candidate_mini),mini_active_cadence=mini['cadence'],native_lifts=mini['lifts'],
                       verification_scope='Exact Downloads Mega Giant variant9 with native menu, OAM/CHR and full 1-1. '
                                          'Mini reaches active 1-2 with all three lifts, both lives and zero active misses.')
        path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    except (Exception,KeyboardInterrupt):
        NIGHTLY.write_bytes(BASE.read_bytes())
        assert check(NIGHTLY)['ROM_sha256']==PARENT
        raise


def publish(out):
    path,ips=out/'verified-delivery.json',out/ASSET
    receipt=read(path)
    assert receipt['ROM_SHA256']==check(NIGHTLY)['ROM_sha256']==PIN
    assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip'] and not receipt['backup_created']
    assert receipt['IPS_SHA256']==sha(ips) and receipt['Giant_CHR_lease_SHA256']==sha(LEASE)==LEASE_SHA
    giant,prior,_=source_evidence()
    actual=giant_evidence(out/'downloads-giant',NIGHTLY)
    assert actual==giant and receipt['Giant_Downloads_result_SHA256']==GIANT_RESULT
    assert receipt['Giant_Downloads_binding_SHA256']==sha(out/'downloads-giant/capture/binding.json')
    candidate=checked_mini(Path(receipt['Mini_candidate_packet']),ROM)
    same_mini(prior,candidate)
    assert candidate==checked_mini(out/'downloads-smoke',NIGHTLY)

    notes=out/'release-notes.txt'
    notes.write_text('Current MMC5 work-in-progress nightly.\n\n'
                     'Apply this IPS to clean, headered Super Mario Bros. (World).\n'
                     f'Base SHA-256 {receipt["base_SHA256"]}\nPatched ROM SHA-256 {PIN}\n\n'
                     'Mega Giant Mario is available as a Mario alternate. Highlight Mario and press Select until '
                     'MEGA GIANT MARIO appears. The installed build cleared 1-1 with both lives and recorded '
                     f'{actual["active_missed_reads"]:,} missed controller reads during active play. '
                     'Mini Mario cleared 1-1 with all three lifts, both lives and zero active missed reads.\n',
                     encoding='utf-8')

    def release(endpoint):
        return json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/releases/{endpoint}'],encoding='utf-8'))

    current=release('tags/Current')
    existing,=current['assets']
    assert current['tag_name']=='Current' and existing['name']==ASSET
    digest='sha256:'+receipt['IPS_SHA256']
    if existing['digest']!=digest:
        subprocess.run(['gh','release','upload','Current',str(ips),'--clobber','--repo',REPO],check=True)
    subprocess.run(['gh','release','edit','Current','--latest','--notes-file',str(notes),'--repo',REPO],check=True)
    latest=release('latest')
    asset,=latest['assets']
    assert latest['tag_name']=='Current' and latest['id']==current['id']
    assert asset['name']==ASSET and asset['digest']==digest and asset['size']==ips.stat().st_size
    receipt.update(release_tag='Current',release_is_latest=True,sole_asset=ASSET,
                   release_asset_digest=digest,final_patch_guard=check(NIGHTLY))
    path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(f'Downloads and Current IPS verified for {PIN}',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','deliver','publish'))
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--mini-packet',type=Path,help='Reuse a completed candidate Mini packet on a delivery retry.')
    args=parser.parse_args()
    out=args.output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    if args.action=='prepare':
        prepare_mini(out)
    elif args.action=='deliver':
        mini=(args.mini_packet or out/'mini').resolve()
        assert mini.is_relative_to(R/'build')
        install_and_verify(out,mini)
        publish(out)
    else:
        publish(out)


if __name__=='__main__':
    main()
