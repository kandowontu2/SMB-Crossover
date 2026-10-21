"""Audit obtainable Samus 2.02 upgrades separately from dormant declarations.

This is a pinned-source/data check. It does not patch or run either game.
"""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'reference/crossover2/extracted/scripts/com/smbc'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    swf = ROOT / 'reference/crossover2/source.swf'
    samus_file = SOURCE / 'characters/Samus.as'
    assert sha(swf) == '6374c72426556bfc3cc16f7594ce4443a5867fe2d367514136c99cc8458b70af'
    assert sha(samus_file) == '1f2e577a62b339def01f1e7c8fea0b773184a6039a2e78ad48eca6e6a651986b'
    samus = samus_file.read_text()
    character = (SOURCE / 'characters/Character.as').read_text()
    stats = (SOURCE / 'managers/StatManager.as').read_text()

    def array(name):
        value = re.search(r'const\s+' + name + r':Array\s*=\s*([^;]+);', samus)
        assert value, name
        return re.findall(r'SAMUS_[A-Z_]+', value[1])

    expected = ['SAMUS_MORPH_BALL', 'SAMUS_MISSILE', 'SAMUS_ICE_BEAM',
                'SAMUS_WAVE_BEAM', 'SAMUS_VARIA_SUIT', 'SAMUS_SCREW_ATTACK']
    obtainable = array('OBTAINABLE_UPGRADES_ARR')
    mushroom = array('MUSHROOM_UPGRADES')
    replacement = array('REPLACEABLE_UPGRADES_ARR')
    assert obtainable == expected
    assert mushroom == ['SAMUS_LONG_BEAM'] and replacement == []
    assert 'SAMUS_HIGH_JUMP' not in obtainable + mushroom + replacement
    assert 'SAMUS_HIGH_JUMP' in array('ICON_ORDER_ARR')
    assert re.search(r'JUMP_PWR_NORMAL:int\s*=\s*500;', samus)
    assert re.search(r'JUMP_PWR_HIGH:int\s*=\s*580;', samus)
    jump = samus[samus.index('private function setJumpPwr()'):
                 samus.index('override protected function movePlayer()')]
    assert 'upgradeIsActive(SAMUS_HIGH_JUMP)' in jump
    assert 'jumpPwr = JUMP_PWR_HIGH;' in jump and 'jumpPwr = JUMP_PWR_NORMAL;' in jump

    available = character[character.index('public static function getAvailableUpgrades('):
                          character.index('public static function getSingleObjVec(')]
    all_upgrades = character[character.index('public static function getAllUpgradesDct('):
                             character.index('public static function getAmmoVec(')]
    assert 'OBTAINABLE_UPGRADES_ARR_PROPERTY_NAME' in available
    assert 'ICON_ORDER_ARR_PROP_NAME' not in available + all_upgrades
    assert 'OBTAINABLE_UPGRADES_ARR_PROPERTY_NAME' in all_upgrades
    assert 'MUSHROOM_UPGRADES_PROP_NAME' in all_upgrades
    debug = stats[stats.index('if(GameSettings.DEBUG_MODE && GameSettings.allUpgrades)'):]
    assert 'Character.getAllUpgradesDct(_loc3_)' in debug[:500]

    generated = (ROOT / 'src/inventory_data.inc').read_text()
    def table(name):
        body = re.search(r'^' + name + r':\n((?:  \.byte [^\n]+\n)+)', generated, re.M)
        assert body, name
        return [int(v) for v in re.findall(r'\d+', body[1])]
    assert table('InvItemCount')[2] == 7
    assert table('InvMushroomLo')[2] == 0x80 and table('InvMushroomHi')[2] == 0
    assert table('InvAvailability')[32:48] == [0] + [255] * 6 + [0] * 9

    report = dict(
        source_swf_sha256=sha(swf), samus_source_sha256=sha(samus_file),
        source_modified=False, runtime_changed=False, chr_bytes_changed=0,
        obtainable=obtainable, mushroom_grants=mushroom,
        normal_jump_source_units=500,
        dormant_high_jump=dict(source_units=580, icon_declared=True,
                               obtainable=False, debug_all_upgrades_grants=False,
                               automatic_or_replacement_grants=False),
        current_local_ids=dict(MORPH=1, MISSILE=2, ICE=3, WAVE=4,
                               VARIA=5, SCREW=6, LONG=7),
        conclusion='Default 2.02 never supplies High Jump; retain the six separate pickups and mushroom Long Beam.',
        source_references=['Samus.as:73..83 (upgrade arrays)',
                           'Samus.as:155..157 and490..499 (dormant jump branch)',
                           'Character.as:671..698 (normal pool)',
                           'Character.as:727..766 (debug all-upgrades pool)',
                           'StatManager.as:412..419 (debug grant caller)'])
    out = ROOT / 'docs/reference/samus-upgrade-pool.json'
    out.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS Samus 2.02 six obtainable upgrades / mushroom Long / dormant High Jump exclusion; no runtime or CHR changes')


if __name__ == '__main__':
    main()
