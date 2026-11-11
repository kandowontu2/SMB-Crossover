"""Compose Jay's scrolling movement, pause weapons, ammo and native helpers."""

import argparse
import json
from pathlib import Path

import check_jay_silius_enemy_ammo_1111 as Ammo
import check_jay_silius_helpers_1111 as Helpers
import check_jay_silius_pause_ui_1111 as Pause
import check_jay_silius_shotgun_transport_1111 as T
import check_jay_silius_world_hit_1111 as WorldHit


def proposal(raw):
    for page in (T.CHR_PAGE, T.MOTION_PAGE, T.EXTRA_PAGE):
        T.carrier_ownership(raw, page)
    seed, trial, _ = T.Motion.parent(raw=raw, pin=T.PIN, cookie=T.Weapon.COOKIE)
    helper_origin = 0xbd20
    helper, _ = Helpers.assemble(trial, origin=helper_origin)
    helper_symbols = helper['symbols']
    template = bytes(seed.ram[3][0x88d:0x8c0])
    motion, fields = T.Motion.assemble_handoff(
        trial, template, origin=0xb800, control_tail=True, native_sync=True,
        native_helpers=(helper_symbols['StepHelpers'], helper_symbols['ResetHelpers']),
        pit_boundary=True,
    )
    stage, _ = T.Motion.pit_stage(raw, bytes(seed.ram[3][:0x8c0]), motion)
    ammo_roll, donor_symbols = Ammo.assemble()
    ammo_origin, draw_origin = 0xbaa8, 0xbca0
    ammo, _ = Ammo.assemble_host(ammo_roll, donor_symbols, origin=ammo_origin, draw_origin=draw_origin)
    targets = ammo['symbols']
    world_hit, _ = WorldHit.assemble(trial, native_defeat=targets['CaptureAmmoDefeat'])
    image, linked = T.proposal(raw, movement=motion, roll=ammo_roll['images']['AMMODROP'],
        extra_segments=(
            (ammo_origin, ammo['images']['AMMOHOST']),
            (draw_origin, ammo['images']['AMMODRAW']),
            (helper_origin, helper['images']['HELPERS']),
            (WorldHit.ORIGIN, world_hit['images']['WORLD_HIT']),
        ),
        service_hooks=(
            (0xb14e, 0xb154, targets['StepAmmoAndStock']),
            (0xb332, 0xb337, targets['DrawAmmoAndStock']),
        ),
        service_redirects=((0xb24a, WorldHit.OLD_HOOK, WorldHit.ORIGIN),),
        stage_override=stage,
    )
    linked.update(motion=motion, motion_fields=fields, ammo=ammo, helpers=helper, world_hit=world_hit)
    image, linked = Pause.add_pause(raw, image, linked)
    art = Ammo.ammo_art(Ammo.D.DONOR.read_bytes())
    at = T.C.CHR + Ammo.ART_PAGE * 1024 + Ammo.ART_OFFSET
    assert image[at:at+len(art)] == bytes(len(art))
    image = image[:at] + art + image[at+len(art):]
    linked['edits'].append((at, len(art)))
    return image, linked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', type=Path)
    parser.add_argument('--route', action='store_true')
    args = parser.parse_args()
    raw = T.H.ROM.read_bytes()
    image, linked = proposal(raw)
    trial = dict(T.W.Symbols.bundle(), raw=image)
    print(json.dumps(dict(image_SHA256=T.digest(image), cookie=linked['cookie'].hex(),
                          weapon_selection=linked['fields'][0xb8], spans=linked['edits'],
                          donor_flags=linked['motion_fields']['DonorFlags'],
                          movement=linked['motion']['used'], ammo=linked['ammo']['used'],
                          helpers=linked['helpers']['used']), sort_keys=True), flush=True)
    print('Cold cartridge transport', T.cold_checks(trial, linked), flush=True)
    print('Native paused Select', Pause.gameplay(trial, linked), flush=True)
    if args.route:
        motion = dict(linked['motion'], tile=T.C.Jay.build()['symbols']['JayHostTile'], status=0xc0f3)
        seed, _, _ = T.Motion.parent(raw=image, pin=T.digest(image), cookie=linked['cookie'])
        early = T.Motion.assisted_route(seed, linked['motion_fields'], motion)
        print('Native opening', {key: value for key, value in early.items() if key != 'trace'}, flush=True)
        assert early['terminal'] == (995, 176, 883) and early['lives'] == 2
        late = T.Motion.late_route(seed, linked['motion_fields'])
        print('Native late route', late, flush=True)
    if args.prepare:
        root = args.prepare.resolve()
        assert root.is_relative_to(T.H.ROOT / 'build') and root != T.H.ROOT / 'build'
        root.mkdir(parents=True, exist_ok=True)
        candidate = root / 'candidate.nes'
        with candidate.open('xb') as file:
            file.write(image)
        assert candidate.read_bytes() == image


if __name__ == '__main__':
    main()
