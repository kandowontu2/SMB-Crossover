"""Install the verified Steve Laserbot nightly and refresh the single Current IPS."""

import argparse
from base64 import b85decode
from hashlib import sha256
import json
from types import SimpleNamespace
from unittest.mock import patch
from zlib import decompress

import check_steve_shatterhand_laser_live_1111 as Laser
from deliver_manual_title_1110 import SOURCE_BASE, SOURCE_PIN, apply_ips, ips_for
from nightly_patch_guard_v1 import check
import replay_steve_companion_native_1111 as Replay


ROOT, NIGHTLY = Laser.Live.H.ROOT, Laser.Live.DONOR.HOST
OUTPUT = ROOT / 'build/steve-laserbot-native-1111'
REPORT = ROOT / 'docs/qa/steve-shatterhand-lift-and-laserbot-1111.md'
PARENT = 'c4568faf4f472d4d6c3915c9b4258d5c04d6dcbb562b3e5602a5d580bb3046a2'
OLD_PATCH = 'ff95f659cb60da74c888f34197a7a186c6868a26909052546b3fda9575b9e9bd'
PIN = Laser.QUALIFIED
PATCH_PIN = 'fa17ebd6e7da0f9c5616456e2d543cb7b475881fa3222a612f72086041e648f8'
CONTROLLER_PIN = 'a268a5ce195a3aca29c0e41300635b3fc31d541ea48d6b9f176dcf1e9ba82ddc'
STAGE_SOURCE_PIN = 'a5462727f378dcd4be06b61c886a9781bb0dee5da5bf0f2d06a55e1728e03e5f'
STAGE_RECEIPT = '44974889026db10ae469cf6e8a2538bff40a59676e15edeb88b5baf234aac008'

# Compressed reverse IPS containing only the preimages of changed spans.
INVERSE = (
    'c-rk)T}&KR6#j-'
    ';*jd=J1IxAO5N2u0E~TZd^`})xc7e853b7Jf6EK04nl3htwlqzRu^<VNnAU&~)oMt5Q0SsnV$ugp>tcB+kzF>LnAmK#YWmO+el{j'
    'GZIq6)Gdnx8KXm!aijng$=iGbFz31FJbH01#9;ke&dLLtTff5+&m!QfR>kz11#`=x)yb8+9Sg%X+I1DbFe`3UGx!%E8f5!GfXGyc'
    'Oq}DoQ5&C<IzrD7e8XNR+*Yc^ceqY{u`K^z3Ww@v=y{ov3aSe1Cb}=?R`26O}Y0b6t*Wz=G^<`epYHQ^;ImR5#`OS=uy2;pVpaP6'
    '-6VmTs68jn3Hc+*U?Qzh43^2B*k;7Ut8_(R`c*=dR|DC^j4^2)o+j2ln7=njEf7do{2zG{fAE@Jo;HOA$4Yjj=qG8kyG+LTK-'
    '8B~d4T>@D?FHR;_-*5J2SLA||BCVXIb@GfK7;FK7w!7KmL9xhY??!^5J#phozNekBr-'
    'c$=v<C2+U(qow2=Yx;B91${O+q66M}T@k5|lJY)0A+H*v6d6{#TNI1N6j%>`^&$W+6~NznTPHZClZAhs_${K^f;pI=#y3`MNMQ%l'
    '>R$}?C$udWBjkxC+!4{#(Uj;dO)bID^r0i!lPLt!%eQEXY9gCNX_`m1#)S@0y)WoSvoPFD9KE2`axHl&`&J{F~mF)xQs7921}Yw8'
    'qDJ+fm*9YI=%IYEif*Jvx&XpPn=S+<R{;hY*LXry&v_@woWj+P`nop4;5B1Eax@j7LEI;}W5fx4(EsK`*7ikqJ{nF<S(MnR#;L`P'
    'icd6|=OH|lx2Jx}tfaEaW4pm0I3OCX}~5Sav7Z<6bzQCTl@5Kk`jFxl<x?V|jc2%(bP-fp*>h{uX`fFy^P<#|%V9nVggJqtr5M&j'
    '8m*CkQ05znDWwW7os>UBaNj*)oYK&IvudEOFnP>EUU=!Py7FY)xiuGus>=rC!5lwTw-'
    'D%D9s3l>dy;_)Rq(!{0SMzOdiaS9V;9!(Whf-oyoRe*T2kk(K`yxAe>^|G+Z26l(aJ30V|UFEV1?=IzlGO>V#c=sS3tmuh&_rqa<'
    'Bm=yqNm&&wxZOf~lZ8KOvmK?AeA?b~p_dV9U68{2Xi;a8cNDcNnr;(pstdP?vv_gkXZ5q8M9`!>@fRXX0~^F&s(c7Zp@aDA@yx^F'
    '1M@=%@t;FcQurYLuc(u;5Tajs_)xP@g^dK+sEs4eKjPpa%71JeG5(i>2Kod@fCZrd&`=ZURa2h?im*9x`m>tU59hkYLIQOn*lF^f'
    '1RBBzRG<ktarsXICt`}kz*)^dK;T_`{@*x<Z<V2ZS>sz{_TkoPe7uU+JH?9MMRd*Zu$qHRRlvHix`Rx$;NU{RV^MVnnHt8ae*-'
    'wk^j0{Q3m#<p^_VLQZA~%VjqGR;A=4k?{Hg(x5O|Q8Vi5~O03kD_csV(kEUADXGo5kKk(m#0ES1?Y^8m^YlGzOW`9J+RnVplW>Y('
    '@{V|5(IqI<Oj%5fKCFC;kbl5z*gaYO2n#Bsy%rZ-empVssjwf|RDydzf0vJ})B-'
    '^U~KL|2eAzp6wtMWJ@S!utuYx;TDa=$&x9S&4!#NO1eg@ms}mo8xyx!sg47moNmrUbShAOFfQ1CZGQte^Rx3Gy1UO`0fN>2!C<jW'
    '%F001BBzRDwE%k!u>7W9ob_355?e~x;J}X*!vH9q5BE'
)


def digest(data):
    return sha256(data).hexdigest()


def recover_parent(image):
    assert digest(image) == PIN
    inverse = decompress(b85decode(INVERSE))
    assert digest(inverse) == '04a45908e3dcd91a475e3e8bd122857b172906353a72648dbdc5d6b4350e3216'
    parent = apply_ips(image, inverse)[0]
    assert digest(parent) == PARENT
    return parent


def qualify(parent):
    assert digest(parent) == PARENT
    image, info = Laser.proposal(parent)
    assert recover_parent(image) == parent
    base, ips = SOURCE_BASE.read_bytes(), ips_for(image)
    assert digest(base) == SOURCE_PIN and digest(ips) == PATCH_PIN
    assert apply_ips(base, ips)[0] == image
    return image, info


def install():
    assert check(NIGHTLY)['ROM_sha256'] == PARENT
    parent = NIGHTLY.read_bytes()
    image, info = qualify(parent)
    script, candidate = OUTPUT / 'controller.lua', OUTPUT / 'candidate.nes'
    assert candidate.read_bytes() == image and digest(script.read_bytes()) == CONTROLLER_PIN
    punch = info['punch']['symbols']
    try:
        NIGHTLY.write_bytes(image)
        assert check(NIGHTLY)['ROM_sha256'] == PIN and NIGHTLY.read_bytes() == image
        result = Replay.run(script, NIGHTLY, OUTPUT / 'downloads-capture', PIN, 120, extra_env={
            'SMB_STEVE_COOKIE': info['cookie'].hex(),
            'SMB_STEVE_BIRTH': str(punch['StevePunchBirth']),
            'SMB_STEVE_DRAW': str(punch['SteveDrawEmit']),
        })
        assert result['passed'] and result['receipt_SHA256'] == STAGE_RECEIPT, result['receipt']
        assert check(NIGHTLY)['ROM_sha256'] == PIN and NIGHTLY.read_bytes() == image
    except BaseException:
        NIGHTLY.write_bytes(parent)
        assert check(NIGHTLY)['ROM_sha256'] == PARENT and NIGHTLY.read_bytes() == parent
        raise
    print(json.dumps(dict(installed=True, ROM_SHA256=PIN, IPS_SHA256=PATCH_PIN,
                          downloads_receipt=result['receipt_SHA256'], backup_files=0)), flush=True)


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
                'Highlight Mike Jones and press Select twice for Steve Hermann. Three Alpha tokens earn his '
                'first companion. Punch the exposed third token to change it to Beta and earn Laserbot instead. '
                'Hold B to charge and fire Laserbot. The Mesen replay earned it, damaged a Goomba with the beam, '
                'and reached underground 1-2 with both lives. The lift, original cue, and other companion '
                'attacks are still in development.\n\n'
                'Sonic and Super Sonic are still under Mr. Gimmick at Select three and four.\n')

    with patch.multiple(Publisher, PIN=PIN, PATCH_PIN=PATCH_PIN, OLD_PATCH=OLD_PATCH,
                        RECEIPTS=(STAGE_RECEIPT,), Fix=Recipe, CANDIDATE=OUTPUT / 'candidate.nes',
                        SCRIPT=Replay.LASER_STAGE, SCRIPT_PIN=STAGE_SOURCE_PIN, REPORT=REPORT,
                        release_body=notes):
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
