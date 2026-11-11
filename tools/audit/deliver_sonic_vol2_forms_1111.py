"""Install the physically qualified Sonic forms and publish the matching Current IPS."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import check_super_sonic_roster_1111 as Selector
from deliver_manual_title_1110 import SOURCE_BASE, SOURCE_PIN, apply_ips, ips_for
from nightly_patch_guard_v1 import check
import prepare_sonic_vol2_art_1111 as Art
import replay_sonic_vol2_forms_1111 as Replay


PARENT = '2d7fb6e63ea55f2d0eb9ef3af4efc467233da013dc70e295952a4adcdd14ecdb'
PARENT_IPS = '566a1ab2789c7a15c75485d1198c0f6742f23385b72000c4ebf65bde93910ce0'
PIN = 'c4568faf4f472d4d6c3915c9b4258d5c04d6dcbb562b3e5602a5d580bb3046a2'
PATCH_PIN = 'ff95f659cb60da74c888f34197a7a186c6868a26909052546b3fda9575b9e9bd'
RECEIPTS = {
    'sonic-portrait': '45048ee287136395659d62583701f69fff8fa432d5a31d244616ccf55f26b627',
    'sonic-stage': 'efcf0d862663c551918f62276507e73de5b99d1e9fb7c440ada6f837cd4cdee7',
    'sonic-rings': 'e7d99c07f0937c4b6de598bb427ccc81323d07fd104480b19806aa1241862b74',
    'sonic-mushroom': '4946618eaa39c6572c90fc899f1639ed10752fb8632571f22eeed032fc493f85',
    'super-portrait': 'e18c98ee94428b25b68e6c90e0a088fdf8eb40c1d2059635ab1830ef53557a60',
    'super-stage': 'ae4816c16c20f09bc170d593d8b2005f76d11bd3bebdef226b720c05cc74a20c',
    'super-rings': 'c4ae5790c3b81bdd341d487a95716720e3f18d3b261eaee882dada77d5b2d8aa',
    'super-mushroom': '6f7a4777f247198e6f3a1c70ad6e5386b706e3067e103b23e7e1a2986179d12d',
}
STOCK_226 = '70609cd421e55cd94aa2402f7dd40add3b12c8e454b20a206d93d81d540101a1'
STOCK_BODY = bytes.fromhex(
    '000002030300000100030d0e060f0f1f01010103030301041f3f0f0c0d1d0207'
    '000010100000b0f00010e0e0f0f0f0f0505050f0c0f0b0e0f0f0f08070f0e0c0'
    '0c190d070f0d00000b06060d1d0e070700000606010f0f000e0a0f0f0f03010f'
    '40a0f0e08000000080e0d0e0c0c080800000004060b0fc00c0c040e090dce0fc')
R, NIGHTLY = Replay.R, Art.NIGHTLY
OUTPUT = R / 'build/sonic-vol2-forms-1111'
CANDIDATE = OUTPUT / 'candidate.nes'
REPORT = R / 'docs/qa/sonic-vol2-delivery-1111.md'


def digest(data):
    return sha256(data).hexdigest()


def proposal(stock):
    assert digest(stock) == PARENT
    return Art.apply_art(stock, Art.SHEET.read_bytes(),
                         candidate=Selector.proposal(stock), super_sonic=True)


def recover_parent(image):
    assert digest(image) == PIN
    assert image[Art.COOKIE_AT:Art.COOKIE_AT+16] == Art.transport_cookie(image, super_sonic=True)
    stock = bytearray(Selector.recover_selector(image))
    mirror = Art.chr_page(stock, 230)
    assert digest(mirror) == STOCK_226
    start = Art.CHR_START + 1024*Art.SUPER_CHR
    stock[start:start+1024] = mirror
    for index, tile in enumerate(Art.BODY_TILES):
        at = Art.CHR_START + 1024*Art.NORMAL_CHR + 16*tile
        stock[at:at+32] = STOCK_BODY[index*32:(index+1)*32]
    stock[Art.COOKIE_AT:Art.COOKIE_AT+16] = Art.transport_cookie(stock)
    assert digest(stock) == PARENT
    return bytes(stock)


def qualify():
    parent = NIGHTLY.read_bytes()
    image = proposal(parent)
    assert digest(image) == PIN and recover_parent(image) == parent
    assert CANDIDATE.read_bytes() == image
    patch_bytes = ips_for(image)
    base = SOURCE_BASE.read_bytes()
    assert digest(base) == SOURCE_PIN and digest(patch_bytes) == PATCH_PIN
    assert apply_ips(base, patch_bytes)[0] == image
    return parent, image


def install():
    assert check(NIGHTLY)['ROM_sha256'] == PARENT
    parent, image = qualify()
    try:
        NIGHTLY.write_bytes(image)
        assert NIGHTLY.read_bytes() == image and check(NIGHTLY)['ROM_sha256'] == PIN
        runs = Replay.replays(NIGHTLY, OUTPUT, forms=tuple(Replay.FORMS))
        receipts = {f'{form}-{test}': result['receipt_SHA256'] for (form, test), result in runs.items()}
        assert receipts == RECEIPTS, receipts
        assert check(NIGHTLY)['ROM_sha256'] == PIN and NIGHTLY.read_bytes() == image
    except BaseException:
        NIGHTLY.write_bytes(parent)
        assert NIGHTLY.read_bytes() == parent and check(NIGHTLY)['ROM_sha256'] == PARENT
        raise
    print(json.dumps(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          backup_files=0, receipts=receipts), sort_keys=True), flush=True)


def publish(report_sha):
    import publish_ff_corner_current_1110 as Publisher

    assert digest(ips_for(NIGHTLY.read_bytes())) == PATCH_PIN

    class Recipe:
        V1 = SimpleNamespace(BASE=SOURCE_BASE)

        @staticmethod
        def proposal(base):
            assert digest(base) == SOURCE_PIN
            return (proposal(recover_parent(NIGHTLY.read_bytes())),)

    def notes(head):
        return ('Current MMC5 WIP nightly. Apply the IPS to clean headered Super Mario Bros. (World).\n\n'
                f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
                'Highlight Mr. Gimmick in row 4, column 2. Press Select three times for Sonic '
                'or four times for Super Sonic. Both use new standing art from Sonic the Hedgehog '
                'Improvement Vol. 2 1.7. Both cleared 1-1 and passed the ring and mushroom replays '
                'in Mesen. Super Sonic currently shares Sonic’s movement and ring rules.\n')

    with patch.multiple(Publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=PARENT_IPS,
                        RECEIPTS=tuple(RECEIPTS.values()), Fix=Recipe, CANDIDATE=CANDIDATE,
                        SCRIPT=Replay.Original.STAGE, SCRIPT_PIN=Replay.Original.STAGE_PIN,
                        REPORT=REPORT, release_body=notes):
        Publisher.main(report_sha=report_sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('qualify')
    commands.add_parser('install')
    release = commands.add_parser('publish')
    release.add_argument('report_sha')
    args = parser.parse_args()
    if args.command == 'qualify':
        qualify()
        print(json.dumps(dict(passed=True, parent=PARENT, candidate=PIN, IPS_SHA256=PATCH_PIN)), flush=True)
    elif args.command == 'install':
        install()
    else:
        publish(args.report_sha)


if __name__ == '__main__':
    main()
