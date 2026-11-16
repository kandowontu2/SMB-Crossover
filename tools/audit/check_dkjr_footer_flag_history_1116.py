"""Read-only old-LPC writer induction; no invented near-apex occurrence."""
from hashlib import sha256
import json
from pathlib import Path

import compose_dkjr_platform_footer_current_1116 as C

H=lambda value:sha256(value).hexdigest()


def check(raw):
    assert H(raw)==C.CANDIDATE
    source=(C.R/'src/object.s').read_text()
    start=source.index('LargePlatformCollision:')
    end=source.index(';--------------------------------',start)
    lpc=source[start:end]
    assert lpc.index('lda #$ff')<lpc.index('sta PlatformCollisionFlag,x')<lpc.index('lda TimerControl')
    assert raw[16+0x1453:16+0x1458]==bytes.fromhex('a9ff9d6605')
    collision=(C.R/'src/collision.s').read_text()
    begin=collision.index('ChkForTopCollision:');finish=collision.index('PlatformSideCollisions:',begin)
    top=collision[begin:finish]
    assert top.index('cmp #$06')<top.index('lda Player_Y_Speed')<top.index('bmi PlatformSideCollisions')<top.index('SetCollisionFlag:')<top.index('sta PlatformCollisionFlag,x')
    linked=C.Plan.Funding.H.T.assemble(C.Plan.SOURCE,C.Plan.LAYOUT)
    # Exact new bytes contain no absolute/indexed write to the six flag slots.
    images=linked['images'];opcodes=(0x8d,0x9d,0x99,0x8e,0x8c,0xee,0xfe,0xce,0xde)
    assert all(not any(data[i]in opcodes and data[i+1:i+3]==bytes.fromhex('6605')for i in range(len(data)-2))for data in images.values())
    census=[]
    for path in sorted((C.R/'src').rglob('*')):
        if path.suffix not in('.s','.inc'):continue
        lines=path.read_text(errors='replace').splitlines()
        for i,line in enumerate(lines):
            text=line.split(';',1)[0].strip()
            if ':'in text:text=text.rsplit(':',1)[-1].strip()
            if ('PlatformCollisionFlag'in text or 'HammerThrowingTimer'in text)and any(text.startswith(op+' ')for op in('sta','stx','sty','inc','dec')):
                census.append(dict(path=path.relative_to(C.R).as_posix(),line=i+1,instruction=text))
    expected={'src/object.s','src/collision.s','src/zelda2_small_platform_native.inc','src/crossover_helpers.s','src/darkwing_weapons.s','src/level_variants.s'}
    actual={r['path']for r in census}
    assert actual==expected,('Flag/alias named-writer census changed',actual)
    return dict(passed=True,source_image_SHA256=H(raw),CPU_executed=False,old_LPC_resets_FF_before_all_exits=True,
        new_footer_never_writes_passenger=True,named_flag_alias_writer_census=census,
        source_hashes={p:H((C.R/p).read_bytes())for p in sorted(expected)},
        admitted_writer='Original native large collision after actual body collision, top difference<6, nonnegative nativeVY, and Ryu admission; it independently sets same-slot passenger.',
        induction='Actual candidate first-jump proof observes nativeVY negative and old same-slot flag at first LPC, then FF. Until the original native collision independently writes contact, the new footer predicate cannot admit because it requires previousFlag==slot. Fractional-zero nativeVY cannot by itself restore the flag.',
        other_domains='Small-platform writers are on IDs2B/2C and excluded from RunLargePlatform. Hammer alias is EnemyID5. Darkwing and shared helper constructors are foreign owner paths; DK normal large births use its forward256..287 window. Actual reuse18 fixtures prove first offscreen LPC clears retained flags. Cold raw clears and retirement are covered separately.',
        limitations='Named source-writer census plus exact large-platform control-flow and actual typed owner/caller induction; no arbitrary raw-address writes, poisoned memory, or universal dynamic near-apex-zero occurrence claimed.',
        actual_new_seed_near_apex_zero_not_required=True,outputs=0,native_claim=False)


if __name__=='__main__':
    import dkjr_footer_source_input_1116 as Input
    parent,_=Input.normalize(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes(),kind='bt91dc-reference-only')
    camera,_=C.Camera.proposal(parent);raw,_=C.proposal(camera);q=check(raw)
    encoded=json.dumps(q,sort_keys=True,separators=(',',':'))
    print('DKJR_FOOTER_FLAG_HISTORY '+encoded,flush=True);print('DKJR_FOOTER_FLAG_HISTORY_SHA256 '+H(encoded.encode()),flush=True)
