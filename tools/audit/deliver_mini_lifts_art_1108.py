"""Deliver a qualified Mini lifts and GBC fireball nightly with the shared guard."""
import argparse
import json
from pathlib import Path
import sys

import deliver_mini_nightly_root_1103_v30 as delivery
from prepare_mini_no_wall_1108 import CURRENT


def load(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('install','finalize'))
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--route',type=Path,required=True)
    parser.add_argument('--fire',type=Path,required=True)
    parser.add_argument('--idle',type=Path,required=True)
    parser.add_argument('--power',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    rom=args.candidate/'candidate.nes'
    manifest=args.candidate/'candidate.json'
    pin=delivery.sha(rom)
    art=load(manifest)
    assert art['candidate_SHA256']==pin and art['cold_loader_exact_attribute_table']
    route=delivery.proof(args.route,pin)
    assert route['full_stage'] and route['last']['lives']==2
    full=route['phases']['fullstage']
    assert full['wall_restarts']==0
    lifts=full['lifts']
    assert [(p['left'],p['center'],p['spawn_top'],p['width']) for p in lifts] == [
        (560,576,192,32),(688,704,192,32),(864,880,192,32)]
    assert all(p['boarded'] and p['departed'] for p in lifts)
    assert delivery.proof(args.power,pin)['earned_power']
    delivery.proof(args.idle,pin)
    idle=load(args.idle/'capture/timing.json')['cadence']
    for phase in ('idle','right','left','brake','jump','landing'):
        row=idle[phase]
        assert row['physical']==row['updates'] and row['lag_nmi']==row.get('no_controller_read',0)==0
    assert idle['idle']['updates']==180
    binding=load(args.fire/'capture/binding.json')
    fire=load(args.fire/'capture/result.json')
    assert binding['ROM_sha256']==fire['ROM_sha256']==pin
    assert binding['exit_code']==0 and binding['ready_sha256']==delivery.sha(args.fire/'ready.json')
    for path,digest in load(args.fire/'ready.json')['bindings'].items():
        assert delivery.sha(path)==digest,path
    assert fire['passed'] and fire['max_active_fireballs']==fire['max_visible_fireballs']==2
    assert all(fire['concurrent_DMA_by_direction'].values()) and fire['staged_goomba_hit']
    assert fire['moving_art_phases']=={str(i):True for i in range(4)}
    assert fire['impact_art_frames']==dict(C=True,D=True)

    delivery.O=args.output.resolve()
    delivery.PREVIOUS=CURRENT
    assert delivery.O.is_relative_to(delivery.R/'build')
    # The downloaded cartridge replays the identical full-stage controller.
    sys.argv=[sys.argv[0],args.action,'--rom',str(rom),'--packet',str(args.route),'--candidate',str(manifest)]
    delivery.main()
    if args.action=='finalize':
        p=delivery.O/'verified-delivery.json'
        receipt=load(p)
        assert receipt['downloads_smoke']['full_stage']
        assert receipt['downloads_smoke']['phases']['fullstage']['wall_restarts']==0
        cadence=load(args.route/'capture/timing.json')['cadence']['fullstage']
        receipt.update(native_lifts=lifts,active_11_cadence=cadence,idle_cadence=idle,
            fireball_art_SHA256=art['donor_SHA256'],moving_phases=fire['moving_art_phases'],
            impact_frames=fire['impact_art_frames'],earned_mushroom=True,
            verification_scope='Actual Downloads controller-only 1-1 into 1-2, all three native lifts, both lives. '
            'Exact candidate earned mushroom, zero-lag empty-area idle/movement, and a focused Fire Mini fixture '
            'with real two-shot controls and a staged Goomba impact. Busy-stage lag remains.')
        p.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
        (delivery.O/'release-notes.txt').write_text(
            'Current MMC5 work-in-progress nightly.\n\n'
            'Apply this IPS to clean, headered Super Mario Bros. (World).\n'
            f'Base SHA-256: {receipt["base_SHA256"]}\n'
            f'Patched ROM SHA-256: {pin}\n\n'
            'Mini Mario rides native vertical platforms in 1-1 at left edges X560, X688 and X864, '
            'each 32 pixels wide at initial top Y192. The wall grab has been removed. '
            'Mini clears 1-1 with both lives through the three assisted pipe crossings.\n\n'
            'Fire Mini retains two shots and 4x4 collision boxes. They use the original GBC 6x6 moving '
            'art and original impact tiles, timed to native projectile impact lifetime. '
            'Busy-stage lag remains. Reopen the ROM and start a fresh game.\n',encoding='utf-8')


if __name__=='__main__':
    main()
