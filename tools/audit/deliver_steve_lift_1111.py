"""Deliver Steve's verified lift controls and preserve the preceding nightly inverse."""

import argparse
from base64 import b85decode
import json
from types import SimpleNamespace
from unittest.mock import patch
from zlib import decompress

import check_steve_shatterhand_lift_live_1111 as Lift
import deliver_steve_laserbot_1111 as Previous
from deliver_manual_title_1110 import SOURCE_BASE, SOURCE_PIN, apply_ips, ips_for
from nightly_patch_guard_v1 import check


ROOT, NIGHTLY, Replay, digest = Previous.ROOT, Previous.NIGHTLY, Previous.Replay, Previous.digest
OUTPUT = ROOT / 'build/steve-lift-native-1111'
REPORT = Previous.REPORT
PARENT, OLD_PATCH, PIN = Previous.PIN, Previous.PATCH_PIN, Lift.QUALIFIED
PATCH_PIN = '46d745633a6c05cc9c69531c5cebf7a16ac82a92282534560b9f3d353989ba9b'
LIFT_RECEIPT = 'c6eeeb230c81c56ba86f401bb5844e50464360d816253f4dcf49303567c78c93'
STAGE_RECEIPT = 'e57d3fe797ea7ff5487271cb6aaf04b3a9a69695be3b4d2fae87262ea4a105e7'
LIFT_CONTROLLER = '1bff74ddb67198bf9d936408ae15f730a575bc1080124239592d37177dc8f233'
STAGE_CONTROLLER = '8f3cd1a21b2207452661ce380533230bc48242c05edcd5fcc5d7fe5e64ff31f9'
LIFT_SOURCE = 'd980b9a7b3f488d9526b788b2cfd6dc067f377dbf4f30fcc9e0ec69e07acab40'

# Preimages of the changed spans only, for reconstructing the previous nightly in RAM.
INVERSE = (
    'c-rlhZ)h839LImp<=-VsmUH;9(XQ*US!>wDYKNvPU6-'
    'Z}*BY_vM5fW6xYca_skQDOWo8TyO3Pv1IAJUp0~x!{a|JDKbvH6$;?qPqSm0Jk;-9(B&8|D4n_+_Zq%$w}#+Ul0-'
    '&YTxJMQ~@;rR3hwgv^Zu@&5%-'
    ')CR0Ipo{Za7=k%*#*npV8ziVz@~sKM^+?`0Fx=<j;nwk#z6}(a2^Mnpqal{S9xNxstq}L*@i^*7ejKWmko(kXAQ}zUNIzB(i&p>9'
    'U)i0b40&6i-X&tVN~FQ+4zH6Z^Y--83oCg4F02RbX>b=_^)3wOlHEPjp5)Z4EbV-'
    'F++jGS4QHZAx6i=6sR?XY}T0+v%x|*^s82rKeHy!yK<_V&~6W*-OCB>_7cg(|B&UqImIC_7@sZ}+MHnug0J0wb!E@-'
    ')1kb4%Q*dbUcPNaeHkYbw)N)aKa402{srh++=&4Fi90Re(GJs5+Q)R1_KAT74nmSs`+_c0ZYB*{e5d5Q1%o>wu3f*eEl<O?pmMnt'
    'm4R&ul%X|HF0*Zvv{y(QCGC`8;W^-j55!`D1H-Wx&}1@zg(#p57IuN-'
    '+MQtGZ417(l%*`??%;0^0h+>v4nQYyp$pJHTo?zm5f@Z=49@e%zE<l9Y1VD&<?<FHstf1z+v=@z1c_-cVfA@6Kuk+`>;ivsTK`F{'
    'CFZ6S;KF4<HMnpE>?BjM3@*&WrnB^9{l_=!a%X(GfAx*JnsAB5YV$BI`T%Xg#r3eW8_`?zC_9q5xK(*GS@{N^&4w4>Z$ctHQ!7sN'
    'ifLB2r(Fb@%qlTuo8-*Frh&<o#BJ^*cw)z7y^q)XCesAz+q6hT-'
    '#Y4Y9Zx%EBKCOq%uDu(&a@L3KLGS1E`A6N@wS;hdz{f9^@|FYR}<><IwIE-#hr*msDB9)cb9PSEQA%-'
    'V?z~(E3e3}BPA`rfs~)a&!cH>WR<9{t8BfmvbCYI^?tfFwdi$v(S!Ze?bG`2X@~!My+d-'
    'OSzKBMs1BDrVDWhgF5LrMoN<~GJL?i9%X?N)0bE)OR=d0l;Zh^~I906-pZe?}f1u}?NNzFgAeH7oMVf<DngbP$4pqremF%vP-Bq%'
    'mDVO(mP_mak+DqyG{-@4;4v52ZrvL$-'
    'p8~|=8yJ!YWA6^{8GLQ~3r`E1n;UDr@%QCXDYoyeS0hh#wQN|!nKyo$E#<%Y^2Cvmclx>?sr|37-SuSXZ^bxjs{'
)


def recover_parent(image):
    assert digest(image) == PIN
    inverse = decompress(b85decode(INVERSE))
    assert digest(inverse) == '7b98d08851e068ddb95f9f59b7c1367d9c6ab5d36709b70d2bac752c312d6e91'
    raw = apply_ips(image, inverse)[0]
    assert digest(raw) == PARENT
    return raw


def qualify(raw):
    assert digest(raw) == PARENT
    image, info = Lift.Laser.proposal(raw, lift=True)
    assert recover_parent(image) == raw
    base, ips = SOURCE_BASE.read_bytes(), ips_for(image)
    assert digest(base) == SOURCE_PIN and digest(ips) == PATCH_PIN
    assert apply_ips(base, ips)[0] == image
    return image, info


def install():
    assert check(NIGHTLY)['ROM_sha256'] == PARENT
    parent = NIGHTLY.read_bytes()
    image, info = qualify(parent)
    script, candidate = OUTPUT / 'controller.lua', OUTPUT / 'candidate.nes'
    assert candidate.read_bytes() == image
    stage = script.read_bytes()
    assert digest(stage) == STAGE_CONTROLLER
    groups = Replay.record(image, info, Lift.exercise)
    lift = Replay.controller(groups, info, lift=True).encode('utf-8')
    assert digest(lift) == LIFT_CONTROLLER
    punch = info['punch']['symbols']
    environment = {'SMB_STEVE_COOKIE': info['cookie'].hex(),
                   'SMB_STEVE_BIRTH': str(punch['StevePunchBirth']),
                   'SMB_STEVE_DRAW': str(punch['SteveDrawEmit'])}
    try:
        NIGHTLY.write_bytes(image)
        assert check(NIGHTLY)['ROM_sha256'] == PIN
        for name, source, receipt in (('lift', lift, LIFT_RECEIPT), ('stage', stage, STAGE_RECEIPT)):
            script.write_bytes(source)
            result = Replay.run(script, NIGHTLY, OUTPUT / ('downloads-'+name), PIN, 120, extra_env=environment)
            assert result['passed'] and result['receipt_SHA256'] == receipt, result['receipt']
        assert check(NIGHTLY)['ROM_sha256'] == PIN and NIGHTLY.read_bytes() == image
    except BaseException:
        NIGHTLY.write_bytes(parent)
        assert check(NIGHTLY)['ROM_sha256'] == PARENT
        raise
    finally:
        script.write_bytes(stage)
    print(json.dumps(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          downloads_receipts=(LIFT_RECEIPT, STAGE_RECEIPT), backup_files=0)), flush=True)


def publish():
    import publish_ff_corner_current_1110 as Publisher

    class Recipe:
        V1 = SimpleNamespace(BASE=SOURCE_BASE)

        @staticmethod
        def proposal(base):
            assert digest(base) == SOURCE_PIN
            return qualify(recover_parent(NIGHTLY.read_bytes()))

    def notes(head):
        return ('Current MMC5 WIP nightly. Apply the IPS to clean headered Super Mario Bros. (World).\n\n'
                f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
                'Highlight Mike Jones and press Select twice for Steve Hermann. With a robot equipped, '
                'crouch and hold A until the robot latches. Release Down while holding A to rise, '
                'and release A to drop. Mesen verified the earned first companion lift, and Laserbot '
                'again damaged a Goomba and cleared 1-1 with both lives. This build uses the existing '
                'sprites during the lift. The original lift poses, B throw, and cue remain in development.\n\n'
                'Sonic and Super Sonic are still under Mr. Gimmick at Select three and four.\n')

    with patch.multiple(Publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=OLD_PATCH,
                        RECEIPTS=(LIFT_RECEIPT, STAGE_RECEIPT), Fix=Recipe, CANDIDATE=OUTPUT / 'candidate.nes',
                        SCRIPT=Replay.LIFT_TAIL, SCRIPT_PIN=LIFT_SOURCE, REPORT=REPORT, release_body=notes):
        Publisher.main(report_sha=digest(REPORT.read_bytes()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install', 'publish'))
    args = parser.parse_args()
    (install if args.action == 'install' else publish)()


if __name__ == '__main__':
    main()
