"""Build a private MMC5 sound-test proposal without changing the installed ROM."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE = D/'root-current-roster-composition-v1/source'


def replace(text, before, after):
    assert text.count(before) == 1, before
    return text.replace(before, after, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--reuse-existing', required=True, action='store_true',
                        help='Reuse the existing unbound sound-test draft; fresh source clones are prohibited.')
    parser.add_argument('--base-source', type=Path, default=BASE)
    parser.add_argument('--rebind-existing-baseline', action='store_true',
                        help='Verify unchanged draft inputs before using an existing source alias.')
    args = parser.parse_args()
    assert not args.output.resolve().is_relative_to(R)
    target = args.output/'source'
    assert target.is_dir(), 'Use the existing sound-test draft; no source tree is created.'
    previous = json.loads((args.output/'preparation.json').read_text())
    assert previous['source_only'] and not previous['native_run'] and not previous['installed']
    base = args.base_source.resolve()
    assert base.is_dir(), 'Baseline source is absent; deleted snapshots are not recreated.'
    rebind = None
    if Path(previous['base']).resolve() != base:
        assert args.rebind_existing_baseline, 'Review a changed source base explicitly.'
        manifest = json.loads((args.output/'source-manifest.json').read_text())
        rebind = dict(previous_base=previous['base'], current_base=str(base), exact_files=0,
                      cfg_eol_only=[], restored_or_copied_files=0)
        for name, expected in manifest.items():
            if name in previous['changed_files'] or '__pycache__' in Path(name).parts:
                continue
            original = base/name
            assert original.is_file(), name
            if hashlib.sha256(original.read_bytes()).hexdigest() == expected:
                rebind['exact_files'] += 1
            else:
                assert name == 'smb1base-mmc5-expanded.cfg' and original.read_text() == (target/name).read_text(), name
                rebind['cfg_eol_only'].append(name)
    changed = []

    def edit(name, transform):
        path = target/name
        original = (base/name).read_text()
        new = transform(original)
        path.write_text(new, newline='\n')
        changed.append(name)
        return ''.join(difflib.unified_diff(original.splitlines(True), new.splitlines(True),
                                           fromfile='a/'+name, tofile='b/'+name))

    def menu(s):
        s = replace(s, '  cmp #6\n  jeq CheatsInput\n',
                    '  cmp #6\n  jeq CheatsInput\n.if ::ENABLE_MMC5_EXPANDED\n'
                    '  cmp #7\n  jeq BuildOptions\n  cmp #8\n  jeq SoundInput\n.endif\n')
        s = replace(s, 'OpenPage:\n  sta CrossoverMenuState',
                    'OpenPage:\n.if ::ENABLE_MMC5_EXPANDED\n  ldx #0\n  stx CrossoverOptionsFocus\n.endif\n  sta CrossoverMenuState')
        s = replace(s, '  jsr DrawOptionsPage\n  lda CrossoverMenuState\n  cmp #5',
                    '.if ::ENABLE_MMC5_EXPANDED\n  farcall DrawOptionsPage\n.else\n  jsr DrawOptionsPage\n.endif\n.if ::ENABLE_MMC5_EXPANDED\n'
                    '  lda CrossoverMenuState\n  cmp #7\n  bne :+\n'
                    '  farcall SoundTestBuildPage\n  lda #8\n  jmp OptionsBuilt\n:\n.endif\n'
                    '  lda CrossoverMenuState\n  cmp #5')
        s = replace(s, '  sta GuestOamRotationActive\n  sta CrossoverOptionsFocus\n',
                    '  sta GuestOamRotationActive\n.if !::ENABLE_MMC5_EXPANDED\n  sta CrossoverOptionsFocus\n.endif\n')
        s = replace(s, '  cmp #6\n  beq CheatsReady\n  farcall QueueOptions',
                    '  cmp #6\n  beq CheatsReady\n.if ::ENABLE_MMC5_EXPANDED\n'
                    '  cmp #8\n  bne :+\n  farcall SoundTestQueue\n  jmp ScreenReady\n:\n.endif\n'
                    '  farcall QueueOptions')
        s = replace(s, '  cmp #3\n  bcc OptionsFocusReady',
                    '.if ::ENABLE_MMC5_EXPANDED\n  cmp #4\n.else\n  cmp #3\n.endif\n  bcc OptionsFocusReady')
        s = replace(s, '  lda #2\nOptionsFocusReady:',
                    '.if ::ENABLE_MMC5_EXPANDED\n  lda #3\n.else\n  lda #2\n.endif\nOptionsFocusReady:')
        s = replace(s, '  lda CrossoverOptionsFocus\n  cmp #2\n  beq OpenCheats',
                    '  lda CrossoverOptionsFocus\n.if ::ENABLE_MMC5_EXPANDED\n'
                    '  cmp #3\n  beq OpenSoundTest\n.endif\n  cmp #2\n  beq OpenCheats')
        s = replace(s, 'OpenCheats:\n  lda #5',
                    '.if ::ENABLE_MMC5_EXPANDED\nOpenSoundTest:\n'
                    '  farcall SoundTestEnter\n  jmp MenuIdle\nSoundInput:\n'
                    '  farcall SoundTestInput\n  jmp MenuIdle\n.endif\n'
                    'OpenCheats:\n.if ::ENABLE_MMC5_EXPANDED\n  lda #0\n  sta CrossoverOptionsFocus\n.endif\n  lda #5')
        s = replace(s, '  .byte $22,$ca,8,"B - BACK"',
                    '.if ::ENABLE_MMC5_EXPANDED\n  .byte $22,$c5,22,"AUDIO TEST            "\n'
                    '  .byte $23,$4a,8,"B - BACK"\n.else\n  .byte $22,$ca,8,"B - BACK"\n.endif')
        s = replace(s, '  lda #3\n  sta R4\n  jmp QueueOptionCursor',
                    '.if ::ENABLE_MMC5_EXPANDED\n  lda #4\n.else\n  lda #3\n.endif\n'
                    '  sta R4\n  jmp QueueOptionCursor')
        s = replace(s, 'CursorHi:.byte $21,$22,$22\nCursorLo:.byte $63,$03,$63',
                    'CursorHi:.byte $21,$22,$22\n.if ::ENABLE_MMC5_EXPANDED\n  .byte $22\n.endif\n'
                    'CursorLo:.byte $63,$03,$63\n.if ::ENABLE_MMC5_EXPANDED\n  .byte $c3\n.endif')
        s = replace(s, '.proc DrawOptionsPage\n',
                    '.if ::ENABLE_MMC5_EXPANDED\n.pushseg\n.segment "X5_MENU_UI"\n.endif\n.proc DrawOptionsPage\n')
        s = replace(s, '.endproc\n\n.pushseg\n.segment "CHEATS_MENU_COLD"\n.proc QueueOptions',
                    '.endproc\n.if ::ENABLE_MMC5_EXPANDED\n.popseg\n.endif\n\n.pushseg\n.segment "CHEATS_MENU_COLD"\n.proc QueueOptions')
        s = replace(s, 'MenuCharacters: .byte 0,1,2,3,4,5,6,7,12,9,10,11',
                    '.if !::ENABLE_MMC5_EXPANDED\nMenuCharacters: .byte 0,1,2,3,4,5,6,7,12,9,10,11\n.endif')
        return s

    patch = edit('src/character_select.s', menu)
    patch += edit('src/music_drivers/vanilla_music.s', lambda s: replace(s,
                  '         sta SND_MASTERCTRL_REG    ;if so, disable sound and leave\n         rts\n',
                  '.if ::ENABLE_MMC5_EXPANDED\n         jmp SoundTestAudioGate\n         nop\n.else\n'
                  '         sta SND_MASTERCTRL_REG    ;if so, disable sound and leave\n         rts\n.endif\n'))
    patch += edit('src/entrypoint.s', lambda s: s+'\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.include "sound_test.s"\n.endif\n')
    template = R/'tools/audit/proposals/sound-test-v1/sound_test.s'
    shutil.copyfile(template, target/'src/sound_test.s')
    changed.append('src/sound_test.s')
    tables, catalog = make_tables()
    (target/'src/sound_test_tables.inc').write_text(tables, newline='\n')
    changed.append('src/sound_test_tables.inc')
    (args.output/'sound-catalog.json').write_text(json.dumps(catalog, indent=2)+'\n')
    (args.output/'implementation.patch').write_text(patch)
    manifest = {str(p.relative_to(target)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(target.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    (args.output/'source-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    (args.output/'preparation.json').write_text(json.dumps(dict(source_only=True, native_run=False,
        installed=False, reused_existing_source=True, base=str(base), baseline_rebind=rebind,
        source_files=len(manifest), changed_files=changed,
        state='Twelve menu-only bytes HpDrawBuffer+11..22; no new allocation. HpValid invalidated on entry/exit.',
        controls='Up/Down character; Left/Right track; Select music/SFX; A play; Start stop; B Options.'), indent=2)+'\n')
    print(json.dumps(dict(output=str(args.output), source_files=len(manifest), changed_files=changed)))


def make_tables():
    # One identity per selectable character, including all Select alternates.
    heroes = [
        ('MARIO',0,'MarioVariant',0), ('LUIGI',8,'MarioVariant',1),
        ('MEGA MAN',1,'ProtoVariant',0), ('PROTO MAN',1,'ProtoVariant',1),
        ('SAMUS',2,None,0), ('BILL',3,'BillVariant',0), ('LANCE',3,'BillVariant',1),
        ('LINK',4,'Z2Variant',0), ('ZELDA II LINK',4,'Z2Variant',1),
        ('SIMON',5,'Cv3Variant',0), ('GRANT',5,'Cv3Variant',1),
        ('SYPHA',5,'Cv3Variant',2), ('ALUCARD',5,'Cv3Variant',3),
        ('PIT',6,None,0), ('RYGAR',7,None,0), ('SCROOGE',12,'DarkwingVariant',0),
        ('DARKWING DUCK',12,'DarkwingVariant',1), ('BASS',9,'RlVariant',0),
        ('ROLL',9,'RlVariant',1), ('RYU',10,None,0), ('SOPHIA',11,None,0),
        ('KIRBY',13,'KbVariant',0), ('META KNIGHT',13,'KbVariant',1),
        ('CHIP',14,'CdVariant',0), ('DALE',14,'CdVariant',1),
        ('LITTLE MAC',15,None,0), ('MIKE JONES',16,None,0),
        ('SMB3 MARIO',17,'M3Variant',0), ('SMB3 LUIGI',17,'M3Variant',1),
        ('VIC VIPER',18,'VvVariant',0), ('OCTOPUS',18,'VvVariant',1),
        ('TWINBEE',18,'VvVariant',2), ('PENTAROU',18,'VvVariant',3),
        ('LEONARDO',19,'TnVariant',0), ('RAPHAEL',19,'TnVariant',1),
        ('MICHELANGELO',19,'TnVariant',2), ('DONATELLO',19,'TnVariant',3)]
    # Cue kinds:1 square1,2 square2,3 noise,4 typed source effect,5 MM/Bass source,
    #6 Metroid native flags,7 Contra/Link/Simon primary weapon.
    common = [('JUMP',1,'Sfx_SmallJump'),('PRIMARY ATTACK',7,'1'),
              ('ENEMY HIT',1,'Sfx_EnemySmack'),('TAKE DAMAGE',1,'Sfx_PipeDown_Injury'),
              ('BUMP BLOCK',1,'Sfx_Bump'),('BREAK BRICK',3,'Sfx_BrickShatter'),
              ('COIN',2,'Sfx_CoinGrab'),('ITEM REVEAL',2,'Sfx_GrowPowerUp'),('EXTRA LIFE',2,'Sfx_ExtraLife')]
    native = {
        1:[('CHARGE START',5,'58'),('CHARGE LOOP',5,'59'),('CHARGED SHOT',5,'60'),
           ('DEATH',5,'24'),('METAL BLADE',5,'64'),('HARD KNUCKLE',5,'22'),('PHARAOH SHOT',5,'61'),
           ('CHARGED PHARAOH',5,'62'),('CHARGE KICK',5,'65'),('FLAME SHOT',5,'22'),
           ('SHIELD EXPAND',5,'66'),('WATER SHIELD',5,'67')],
        2:[('MORPH BALL',6,'2'),('BOMB SET',6,'4'),
           ('BOMB EXPLOSION',6,'8'),('WALK',6,'16'),('DEFLECT',6,'32'),('DEATH',6,'64'),
           ('MISSILE',4,'AV_SFX_SAMUSSHOOTMISSILE'),('SCREW ATTACK',4,'AV_SFX_SAMUSSCREWATTACK'),('PICKUP',2,'Sfx_PowerUpGrab')],
        3:[('MACHINE GUN',8,'1'),('SPREAD',8,'2'),('LASER',4,'AV_SFX_BILLLASER'),('FLAME',4,'AV_SFX_BILLFLARE'),('PICKUP',2,'Sfx_PowerUpGrab')],
        4:[('ARROW',4,'AV_SFX_LINKSHOOTARROW'),('SET BOMB',4,'AV_SFX_LINKSETBOMB'),('BOMB EXPLOSION',4,'AV_SFX_LINKBOMBEXPLODE')],
        5:[('DAGGER',4,'AV_SFX_SIMONTHROWDAGGER'),('HOLY WATER',4,'AV_SFX_SIMONHOLYWATEREXPLODE'),
           ('CROSS',4,'AV_SFX_SIMONCROSS'),('STOPWATCH',4,'AV_SFX_SIMONSTOPWATCH')],
        9:[(name,5,str(request+1)) for name,request in [
            ('LAND',19),('LIFE OR POWERUP',20),('BUSTER',21),('HURT',22),('DEATH',23),
            ('HIT ENEMY',24),('DEFLECT',25),('ENERGY',28),('PHARAOH SHOT',60),
            ('CHARGED PHARAOH',61),('ENERGY REFILL LOOP',62),('METAL OR KNUCKLE',63),
            ('CHARGE KICK',64),('SHIELD EXPAND',65),('WATER SHIELD',66),('TELEPORT',67)]],
        10:[('FIRE WHEEL',4,'AV_SFX_RYUARTOFFIREWHEEL'),('FIRE DRAGON',4,'AV_SFX_RYUFIREDRGONBALL'),
            ('JUMP SLASH',4,'AV_SFX_RYUJUMPSLASH'),('SMALL STAR',4,'AV_SFX_RYUTHROWSMALLSTAR'),
            ('BIG STAR',4,'AV_SFX_RYUTHROWBIGSTAR'),('NINJA HURT',4,'AV_SFX_RYUTAKEDAMAGE')],
        11:[('MISSILE',4,'AV_SFX_SOPHIAMISSILE'),('SHOT EXPLOSION',4,'AV_SFX_SOPHIABULLETEXPLODE'),
            ('HIT ENEMY',4,'AV_SFX_SOPHIAHITENEMY'),('KILL ENEMY',4,'AV_SFX_SOPHIAKILLENEMY'),('LAND',4,'AV_SFX_SOPHIALAND')]
    }
    out = ['; Generated from actual host audio cue APIs; labels describe usage, not invented song titles.\n']
    out += ['SoundTestHeroCount='+str(len(heroes))+'\n', 'SoundTestHeroIds: .byte '+','.join(str(h[1])for h in heroes)+'\n']
    out += ['SoundTestMusicBits: .byte 1,2,4,8,16,32,64,1,2,4,8,16,32,64\n',
            'SoundTestVariantLo: .byte '+','.join('<'+h[2]if h[2]else'0'for h in heroes)+'\n',
            'SoundTestVariantHi: .byte '+','.join('>'+h[2]if h[2]else'0'for h in heroes)+'\n',
            'SoundTestVariantValue: .byte '+','.join(str(h[3])for h in heroes)+'\n']
    out += ['SoundTestNameLo: .byte '+','.join('<SoundTestName'+str(i)for i in range(len(heroes)))+'\n',
            'SoundTestNameHi: .byte '+','.join('>SoundTestName'+str(i)for i in range(len(heroes)))+'\n']
    for i,h in enumerate(heroes):out += [f'SoundTestName{i}: .byte "{h[0]:22}"\n']
    roles=['OVERWORLD','UNDERWATER','UNDERGROUND','CASTLE','SKY BONUS','PIPE INTRO','STAR POWER',
           'DEATH','GAME OVER','VICTORY','CASTLE CLEAR','ALT GAME OVER','LEVEL CLEAR','TIME LOW']
    out += ['SoundTestMusicCount=14\n','SoundTestMusicNames:\n']
    for name in roles:out += [f' .byte "{name:24}"\n']
    catalogs = []
    groups = {}
    common_labels = []
    native_labels = []
    for name, owner, variable, variant in heroes:
        base = common
        extra = native.get(owner, [])
        if owner in (3,4,5,9,18):
            base = common[1:]  # These native actors do not emit a jump sound.
        elif owner == 1:
            base = [('LAND',5,'20')]+common[1:]
        elif owner == 2:
            base = [('JUMP',6,'1')]+common[1:]
        elif owner == 10:
            base = [('JUMP',4,'AV_SFX_RYUJUMP')]+common[1:]
        if owner == 5 and variant:
            extra = {1:[('DAGGER',9,'1'),('AXE',9,'2')],
                     2:[('FIRE',9,'4'),('ICE',9,'5'),('LIGHTNING',9,'6')],
                     3:[('FIREBALL',9,'6'),('BAT CHANGE',9,'7')]}[variant]
        for cues, labels in [(base, common_labels), (extra, native_labels)]:
            key = tuple(cues)
            if key not in groups:
                label='SoundTestCueGroup'+str(len(groups));groups[key]=label
                out += [label+':\n']
                for cue,kind,val in cues:out += [f' .byte {kind},{val},"{cue:24}"\n']
            labels.append(groups[key])
        catalogs.append(dict(character=name,owner=owner,variant_variable=variable,variant=variant,
                             music_roles=roles,sfx=[dict(name=n,kind=k,value=v)for n,k,v in base+extra],common_count=len(base)))
    out += ['SoundTestSfxCounts: .byte '+','.join(str(len(c['sfx']))for c in catalogs)+'\n',
            'SoundTestCommonCounts: .byte '+','.join(str(c['common_count'])for c in catalogs)+'\n',
            'SoundTestCommonLo: .byte '+','.join('<'+v for v in common_labels)+'\n',
            'SoundTestCommonHi: .byte '+','.join('>'+v for v in common_labels)+'\n',
            'SoundTestSfxLo: .byte '+','.join('<'+v for v in native_labels)+'\n',
            'SoundTestSfxHi: .byte '+','.join('>'+v for v in native_labels)+'\n']
    return ''.join(out), dict(identities=catalogs,source='Actual current host cue APIs; shared SFX remain explicitly common, absent native jump cues omitted.',music_title_policy='Scene usage labels, not guessed source song titles.')


if __name__ == '__main__':
    main()
