"""Install/publish the physically verified Steve throw WIP, with exact recovery."""
import argparse
from base64 import b85decode
import json
from types import SimpleNamespace
from unittest.mock import patch
from zlib import decompress
import deliver_steve_lift_art_1111 as Previous

PIN = '464c8f1af0401ba7d5393e331833af5bdd68882c536dfc3c77534b71508213c0'
PATCH_PIN = '508ac358f5d8476e3b33ae6e92b649a9954f457cf33734c57b283e65c1ac0a88'
INVERSE_PIN = '29b422c4a9f6079258f6c2e6454fd5c2d419edeae4af3ce969fb71d0922fc50c'
OUTPUT = Previous.ROOT/'build/steve-combat-native-1112'
REPORT = Previous.ROOT/'docs/qa/steve-combat-delivery-1112.md'
THROW_SCRIPT = 'fccbdf72f986998351d896d6c04ae60f18c8f6ac5e86578619f6fa129a4d9318'
RECEIPTS = ('7bb20e43fbf248c1353e245a9a8796f377f505efe71fef9082b8bc8686770c5e',
            'b26c99c95c2116bb9ac7a67773691bb1aa80d84024930d7d039480a998f6da81')
INVERSE = 'c-qZZZA@EL7=F%edugG|Iy@K3fbIf*Fx+C}en?^^tn7mo6e`n9BG@s*kiq<cAAc5SmNAzsO-9tjWYMuk67HlE66fZ}l)|!bX)o<EX6D2d6qk$`!A#v2f8c2^AdHW}WXv}=ectnao%ii|?>Xlduiu)NuYcr87!&NP9LMXdM{Zoce9JIW0ntN-8sV-c((CRTB6-}kMEXW7B`vWpeo-4Rzrq<t_QN>T$WNFUMjDVg*{m*LK0Oo(6LVXb!cr1<K{ItuV|p6MOUCqvK(@z!<iXmZg;4y_HjwQ2qdt&K+HL{?ZI8!BEC$i`ZAhL|{~8izQyqdZi{=>kakd#5^U5PIYp|cdMc@}KpQic~TX7GF`W#qySAK6HeLiN#rq|+Yn?dHAL3SQ1W{CJRtP9SzgQ6BoNwi}h-oSk!+Hnh;7AaI`E>h+;D1%|rXlJy6JFD@+y(_QtEa=RN?_r!OxC%`ahi+HgK+^0JbeXVwiI=QvFP^w--%~h<{|Qk!7mqH;z6O>%nH)mQ1pn^*_E`DUB%g0lu$U!w$Kjbp{@1!oCr**>?a2AB(Hc>`giG#^gYzClErV&g@KyDN_Sa$aqD}Pm<Q>d^?%&4o_e3rr{?OQ*y@;FQ*FPp7#L79s2N2y716pX+u|ahUEQ<sW41n{N(!d~MW$odevc7dk({dUZhDjeP^One>GkEwpN$<{+sR9raRXC6hRMBA>PUPtNxezDiy6sH+0G7Acb5d8mMyv`-?QVV-RWd-jsKTydF;vL}xki;Na05J5)`FB!<uPRGceyu{s;VjvX@pcV{eD+<oXPw0B`KdOrASN6mj((u-u4)N{IX|6*KN9KcAYufQxB=9o@Bck(MFX$sA%At+pxwi7wfi+W?zdj*XGF$+`%@OYd5IO({>fvPw1k{TPm~Ki&*Ui-fhu}^CYl}-5X@DMs}=@)F<^%)Yim(tf5L6*2I8EbH*sYAH(txfAxzg0q=Twgcr|UC>#!oN&ak?*){ocNrR@jcKu)$#5*=iumHL-&WWrAbXjoEEQeOG0kM;ZACC1&&=c*OV3P{XDtw~C2^HE@I60BiSF=qL8jpHWb-AR%4=P+yVL*k!sfVRt{|y=uAtBESU39I4Egj%?$b!QFF6leLu?(EZU?sRT1|qn02CLay#Ty07gI0Zw;8=%L=xcIYFxrAx_OxQO72N0GP6PaBd&>oflU>gFa=x7KF2Yxk(F($`=Vb!El68aNsDsA)hfi?$z>E8OSsp^cJ1|TvuF#jrvdhuQoY0rf@_pPV^nE&>Z{H=5Bf^#USP149rXWQ^cqNEM2&aN<62hxMiiI%yatR6HjHvu!?0!mm*3(;PQR;OE_ygKT?AM6TD;}*kMr_b@g>GKec89Jv@%7qq>3K~kwkz~kME-lE_ax%BI-7Lv3@0nV>RiK#lF`kJY`}}m+%@&nM+kp_H;3*I3BxCmFtaK-btKXi$*I@DYf{AAT*m$lW0Vzbl@5EQE!m<65tA*k(3)*FbFyUx;%)YQTBbz=VYWrBGQru*8;dsm1IN*b{{'


def recover_parent(image):
    assert Previous.digest(image) == PIN
    inverse = decompress(b85decode(INVERSE))
    assert Previous.digest(inverse) == INVERSE_PIN
    parent = Previous.apply_ips(image, inverse)[0]
    assert Previous.digest(parent) == Previous.PIN
    return parent


def qualify(parent):
    import check_steve_throw_controls_live_1111 as Controls
    assert Previous.digest(parent) == Previous.PIN
    image, info = Controls.proposal(parent, combat_active=True)
    assert Previous.digest(image) == PIN and recover_parent(image) == parent
    ips = Previous.ips_for(image)
    assert Previous.digest(ips) == PATCH_PIN
    assert Previous.apply_ips(Previous.SOURCE_BASE.read_bytes(), ips)[0] == image
    return image, info


def install():
    nightly = Previous.NIGHTLY
    assert Previous.check(nightly)['ROM_sha256'] == Previous.PIN
    parent = nightly.read_bytes()
    image, info = qualify(parent)
    assert (OUTPUT/'candidate.nes').read_bytes() == image
    script = OUTPUT/'controller.lua'
    throw = script.read_bytes()
    assert Previous.digest(throw) == THROW_SCRIPT
    groups = [tuple(map(int, group.split(':'))) for group in Previous.STAGE_GROUPS.split()]
    stage = Previous.Replay.controller(groups, info, laser=True, laser_stage=True).replace('\n', '\r\n').encode()
    assert Previous.digest(stage) == '714edb4457af658cf796106c134681eb429b85be8676813d1bf1ea41a9c4de32'
    punch = info['punch']['symbols']
    environment = dict(SMB_STEVE_COOKIE=info['cookie'].hex(), SMB_STEVE_BIRTH=str(punch['StevePunchBirth']),
                       SMB_STEVE_DRAW=str(punch['SteveDrawEmit']))
    try:
        nightly.write_bytes(image)
        assert Previous.check(nightly)['ROM_sha256'] == PIN
        for name, source, receipt in zip(('throw','stage'), (throw,stage), RECEIPTS):
            script.write_bytes(source)
            result = Previous.Replay.run(script, nightly, OUTPUT/('downloads-'+name), PIN, 120, extra_env=environment)
            assert result['passed'] and result['receipt_SHA256'] == receipt, result['receipt']
        assert Previous.check(nightly)['ROM_sha256'] == PIN and nightly.read_bytes() == image
    except BaseException:
        nightly.write_bytes(parent)
        assert Previous.check(nightly)['ROM_sha256'] == Previous.PIN
        raise
    finally:
        script.write_bytes(throw)
    print(json.dumps(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          downloads_receipts=RECEIPTS, backup_files=0)), flush=True)


def publish():
    import publish_ff_corner_current_1110 as Publisher
    class Recipe:
        V1 = SimpleNamespace(BASE=Previous.SOURCE_BASE)
        @staticmethod
        def proposal(base):
            assert Previous.digest(base) == Previous.SOURCE_PIN
            return qualify(recover_parent(Previous.NIGHTLY.read_bytes()))
    def notes(head):
        return ('Current MMC5 WIP. Apply IPS to clean headered Super Mario Bros. (World).\n\n'
                f'ROM SHA-256: {PIN}\nIPS SHA-256: {PATCH_PIN}\nSource commit: {head}\n\n'
                'Steve Hermann: highlight Mike Jones and press Select twice. With a robot equipped, '
                'hold Down+A to latch; press B while latched or lifting to throw. '
                'Includes recovery, robot return, enemy contact damage and destruction animation. '
                'Mesen verified an earned Laserbot throw/return and a 1-1 clear with both lives, '
                'including the installed Downloads ROM.\n\n'
                'WIP limitations: original throw/hit/explosion sound cues are not yet audible; '
                'additional robot attacks, armor and full roster/powerup review remain unfinished.\n')
    with patch.multiple(Publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=Previous.PATCH_PIN,
                        RECEIPTS=RECEIPTS, Fix=Recipe, CANDIDATE=OUTPUT/'candidate.nes',
                        SCRIPT=OUTPUT/'controller.lua', SCRIPT_PIN=THROW_SCRIPT,
                        REPORT=REPORT, release_body=notes):
        Publisher.main(report_sha=Previous.digest(REPORT.read_bytes()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install','publish'))
    args = parser.parse_args()
    (install if args.action == 'install' else publish)()
