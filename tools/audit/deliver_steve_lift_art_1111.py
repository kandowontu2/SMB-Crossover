"""Deliver the verified Steve lift artwork and recover its exact parent in memory."""

import argparse
from base64 import b85decode
import json
from types import SimpleNamespace
from unittest.mock import patch
from zlib import decompress

import deliver_steve_lift_1111 as Previous
from deliver_manual_title_1110 import SOURCE_BASE, SOURCE_PIN, apply_ips, ips_for
from nightly_patch_guard_v1 import check


ROOT, NIGHTLY, Replay, digest = Previous.ROOT, Previous.NIGHTLY, Previous.Replay, Previous.digest
OUTPUT = ROOT / 'build/steve-pose-native-1111'
REPORT = ROOT / 'docs/qa/steve-live-lift-art-native-1111.md'
ART_SOURCE = ROOT / 'tools/playthroughs/steve_lift_art_native_1111.lua'
PARENT, OLD_PATCH = Previous.PIN, Previous.PATCH_PIN
PIN = '80e6aa3e32574f38b23fa6da6ab3c94bbe7b5ae11b29339b32b11a624fe6f1ed'
PATCH_PIN = 'c05dd20cd818d6683a520c983bf53fa563b3a2dce1db445771bfc4de07f28be9'
LIFT_RECEIPT = '419f9eb10237870f7149a03f73b7752e23c87aea5d5f65537c7314b733178430'
STAGE_RECEIPT = '205d84b12328cccafe048785d4b78ffcfdb6c59f1e2594ebe32275ac2875dda6'
LIFT_CONTROLLER = '80bb8bf4a304bf4c2ee797ea7c8d1baecb064663d38778f4443e20d45c31aece'
STAGE_CONTROLLER = '8f3cd1a21b2207452661ce380533230bc48242c05edcd5fcc5d7fe5e64ff31f9'
ART_SOURCE_PIN = 'e29187abfd088669f406b3c2fe58f7ba1978b5ae375756abec7a9917f60338dd'
INVERSE_PIN = '93da8e1c888afcd87367b2eb2cfaefaa26042a6b6be0ec0ce0654fce81e9170c'

# Preserve the exact verified physical input groups if another replay takes
# over the shared controller.lua path.
STAGE_GROUPS = (
    '134:1 150:0 1:64 6:0 87:1 7:0 9:128 53:0 28:2 9:0 9:129 23:1 12:0 84:1 9:129 115:1 '
    '9:129 66:1 1:65 1:1 1:65 41:1 9:129 141:1 9:129 152:1 9:129 98:1 7:0 9:128 53:0 '
    '26:2 9:0 9:129 24:1 30:0 98:1 9:129 79:1 1:65 1:1 1:65 1:1 1:65 9:129 6:1 1:65 '
    '1:1 1:65 1:1 1:65 1:1 9:129 94:1 1:65 1:1 1:65 67:1 7:0 9:129 17:1 20:0 9:128 '
    '55:0 69:2 7:0 9:129 16:1 21:0 9:129 9:1 3:65 7:1 84:0 84:64 1:2 1:4 84:68'
)

# Compressed reverse IPS containing only the preimages of changed spans.
INVERSE = (
    'c-pO2Z%k8H6hF7GeSMSyMSBrZ;Aw}-f=h$Ou@Q#IWLRHI5o4mOv(e4r=7vbnu(*ktRkN&1XBM}8AmU3pd2COcEIM_vzy~uQ'
    'w&eL|aU`@=KalBy)+|%hO!wYv3!S#B`*S|rchB$q&OPUzd*02p*Q~6qhl5)I5!Br00Uf61R)St^6Ybl+uJvc1*6+={@JNC)'
    'FA|TzcaOl7db;YUC#!iL7jhqZUmEfnGw%+7sd*lA{JVY-3wV_?k|!WBmk+i@)ZBom;tokng?9_kO}z@kdXZqJv88I|!-4xM'
    '>14rMB&oAmmf$rGX=Y)MWI3+rA_Vh-gfXwP63nUv(kIVZjWl?RBJ$i@Cn{#bVX>4Fy?t-8z05XNuj&P&Z*jk#wnO&7Uqo*@'
    '4Abkc5FVYhf|^x}Di)e87EAu7OWokiDccLG1x-f30T3AdQ$Y(+G5TjHNFfl4HcQb=ppF{nB@oSusXRtpq-Yg!VpV*y1XS{8'
    'sbYR5sw|IwY;jIgR9_X>9Z`K<Z0QYgycx)N@D^pgR%L8c#`dUFNA$BJ=Gz(fbxrzytnfckMvpS?k2)Oy3MRI9Fj46N13V^1'
    '|H)X4K9~l{#pwSD%<vDz7$9LG{0lJ#DpO|?Xo8}2?pr5MH}IZZn81!$`2xFON-~en5{eY)N^ti=!QVyd2Rr=FVjRkyj6YNW'
    'Q<HL@leaZwhMXrXD<&Fb=vBx~;`*-Qx+RJ0=Zd9!a)BPu#AZGydCKg6j+J^S0>x>_xRwC)0j`xYvf$dCfWE@DrvT;R+Vg-$'
    'aqT5QdAQyrBlUA+q`p)}m?`lLF*75{7BMql{tqxyKFO;DW6}(m_0e=O^LEtd$+}?1lLYf6!Neq3WU{j`a}V-TRKjXV;8~}q'
    '$kr+!JGPd`a<*0~Ia}?CzN=Hm*pkTWfUL*N`(me!t)BEpXZ0nky!F~d$*sRCxsEB93%02y47N<!V9SEp>Dvk0%utwyVN;f~'
    'L-l|B@vzMkFM#cfScPrAgp%1#rZ0<a80hqY?gLJ4X)r)Wf>w}{XHK6=gZ(Kui7nC4k+O9fJc+z7Q}Yt*)o?O3PfX+ur@Zd*'
    'NH3sDJi^QO#K>hR<ZA@!9kKr+eSA>7%FhrYFS5WF2tvQ~E>Pi--vRxANA5w6x{MGE=$F1{{in@-Iu{2sU^cH8Tv|R$a8Z1='
    ';L6~01ecB;JxAyH`I&;Di!T&#unaT{A_w@zI9Lw)Wyrl)uyC8Z{T?+ARs(9s!6iV^xqkY>IVKMWmxD=iH6y2_)0T5SyVFaF'
    'q*o`Ph$`R7YK|Eqt>zXSY=N9<f<CfIz`i$*6_?WDIvm^ygjYZ~_#s$V_c<Km%8zuq9<O%TL3)-Azef6A_GS#PB|TNc>qw7E'
    'TvXxYuzRK;y}t?tcd@|fyBv-_yF*ZU^dY;0qp~!}twBz10}e`;=Vlzd2=h6w`yIqxW7eQS!@hhcZ<6=_jJ*F6dH-{y{j=&i'
    'YNJ-lxD$sEWa&0$42rkC+KRDatqX^8Alplg6>3X!1j?hzh)7ToyfmtFx`^FsCkHOl{TAX*xi=#v6m#O+Mb-6<Yc}{5p<2=S'
    'cncZ_s<mbuT586}sWvo@Lu(;dLEGYJyNtHP(Dpdmp_0&DKy@sU(CsqiBQR~3to#~5P)jdMIKw{}sJLz}t&U^~w2vHmFu)x2'
    '-^8J#K(VNg61wyP4xIp`!=dj1W#dpEWDFW^^Y;hbgk<><C}|}!qU9YpBmybeeI@)#9J&lfk>;C(itFEa@-032Qnz&6^1E?p'
    '475_ybVTI&9ndhVF3X;OfPp&$k2)WAJ~ThPp$HBe0oCDf9w0jo=K~UPxBw8w;X*)FI9v>91rE;w;u0faC6MjX>>>B4yJ0s$'
    'TLUZ(FN77mmj0ADD~^w<2gTpKq)RPZ)Dn805Ort8J2HN|!kO>nklWno)woTKQgfIa%TzR{cayZFkhDa1-iXW6hPpoiK<{4Z'
)


def recover_parent(image):
    assert digest(image) == PIN
    inverse = decompress(b85decode(INVERSE))
    assert digest(inverse) == INVERSE_PIN
    parent = apply_ips(image, inverse)[0]
    assert digest(parent) == PARENT
    return parent


def qualify(parent):
    import check_steve_shatterhand_pose_live_1111 as Pose

    assert digest(parent) == PARENT
    image, info = Pose.proposal(parent)
    assert recover_parent(image) == parent
    base, ips = SOURCE_BASE.read_bytes(), ips_for(image)
    assert digest(base) == SOURCE_PIN and digest(ips) == PATCH_PIN
    assert apply_ips(base, ips)[0] == image
    return image, info


def controllers(image, info):
    assert digest(ART_SOURCE.read_bytes()) == ART_SOURCE_PIN
    lift_groups = Replay.record(image, info, Previous.Lift.exercise)
    lift = Replay.controller(lift_groups, info, lift=True, lift_art=True).encode('utf-8')
    stage_groups = [tuple(map(int, group.split(':'))) for group in STAGE_GROUPS.split()]
    stage = Replay.controller(stage_groups, info, laser=True, laser_stage=True).encode('utf-8')
    assert digest(lift) == LIFT_CONTROLLER and digest(stage) == STAGE_CONTROLLER
    return lift, stage


def install():
    assert check(NIGHTLY)['ROM_sha256'] == PARENT
    parent = NIGHTLY.read_bytes()
    image, info = qualify(parent)
    script, candidate = OUTPUT / 'controller.lua', OUTPUT / 'candidate.nes'
    assert candidate.read_bytes() == image
    saved_controller = script.read_bytes()
    lift, stage = controllers(image, info)
    punch = info['punch']['symbols']
    environment = {'SMB_STEVE_COOKIE': info['cookie'].hex(),
                   'SMB_STEVE_BIRTH': str(punch['StevePunchBirth']),
                   'SMB_STEVE_DRAW': str(punch['SteveDrawEmit'])}
    try:
        NIGHTLY.write_bytes(image)
        assert check(NIGHTLY)['ROM_sha256'] == PIN and NIGHTLY.read_bytes() == image
        for name, source, receipt in (('lift', lift, LIFT_RECEIPT), ('stage', stage, STAGE_RECEIPT)):
            script.write_bytes(source)
            result = Replay.run(script, NIGHTLY, OUTPUT / ('downloads-'+name), PIN, 120, extra_env=environment)
            assert result['passed'] and result['receipt_SHA256'] == receipt, result['receipt']
        assert check(NIGHTLY)['ROM_sha256'] == PIN and NIGHTLY.read_bytes() == image
    except BaseException:
        NIGHTLY.write_bytes(parent)
        assert check(NIGHTLY)['ROM_sha256'] == PARENT and NIGHTLY.read_bytes() == parent
        raise
    finally:
        script.write_bytes(saved_controller)
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
                'crouch and hold A until it latches. Release Down while holding A to rise, '
                'and release A to drop. The lift uses the original Shatterhand player and robot poses. '
                'Projectiles already in flight stay visible. Mesen verified the earned Alpha lift '
                'and Laserbot damaged a Goomba and cleared 1-1 with both lives.\n\n'
                'Sonic and Super Sonic are under Mr. Gimmick at Select three and four.\n')

    with patch.multiple(Publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=OLD_PATCH,
                        RECEIPTS=(LIFT_RECEIPT, STAGE_RECEIPT), Fix=Recipe,
                        CANDIDATE=OUTPUT / 'candidate.nes', SCRIPT=ART_SOURCE, SCRIPT_PIN=ART_SOURCE_PIN,
                        REPORT=REPORT, release_body=notes):
        Publisher.main(report_sha=digest(REPORT.read_bytes()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('qualify', 'install', 'publish'))
    args = parser.parse_args()
    if args.action == 'qualify':
        qualify(NIGHTLY.read_bytes())
        print(json.dumps(dict(passed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN)), flush=True)
    elif args.action == 'install':
        install()
    else:
        publish()


if __name__ == '__main__':
    main()
