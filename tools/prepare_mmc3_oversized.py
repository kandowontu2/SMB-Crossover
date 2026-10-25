"""Prepare the isolated, reproducible oversized MMC3 source candidate.

Copy current prepared sources to a private build tree before applying the port.
No release is installed. The guarded repair recipe includes current native art,
CHR caching, audio banking, pause restoration and all37 menu identities.
"""
from pathlib import Path
import argparse, json, re, shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/oversized-mmc3-nf/source'

def main():
    global ROOT, OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-rom',type=Path,default=ROOT/'build/smb-crossover-mmc5-expanded.nes',
                        help='Built MMC5 reference whose prepared CHR must match byte for byte')
    parser.add_argument('--source-root',type=Path,default=ROOT,help='Project source root; defaults to this tools directory parent')
    parser.add_argument('--output',type=Path,help='Prepared source directory; use a fresh external directory for audit builds')
    args=parser.parse_args()
    ROOT=args.source_root.resolve()
    if args.output: OUT=args.output.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    for name in ('src','inc','chr','audio','build/generated'):
        shutil.copytree(ROOT/name,OUT/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.o','__pycache__'))
    for name in ('build_options.ini','smb1base-mmc5-expanded.cfg'):
        shutil.copyfile(ROOT/name,OUT/name)
    state_aliases = {}
    for path in (OUT/'src').rglob('*'):
        if path.suffix not in ('.s', '.inc'): continue
        s = path.read_text()
        if path.name not in ('options.s', 'mmc5.s'):
            s = s.replace('ENABLE_MMC5_EXPANDED', 'ENABLE_FULL_ROSTER')
        # Native game state overlays inactive, mutually exclusive sound drivers.
        # Menu choices and shared bounce state never overlap a sound driver.
        def state(m):
            n = int(m[0][1:], 16)
            if n < 0x5e80: base, delta = 'RgAudioRam', n & 255
            elif n < 0x5ea0: base, delta = 'MmAudioRamStart', 64+n-0x5e80
            elif n < 0x5f00: base, delta = 'MmAudioRamStart', n-0x5ea0
            elif n < 0x5fe0: base, delta = 'MmAudioRamStart', 128+n-0x5f00
            elif n < 0x5ff0: base, delta = '$73c5', n-0x5fe0
            else: base, delta = '$73d5', n-0x5ff0
            alias=f'M3State_{n:04x}'
            state_aliases[alias]=f'{base}+${delta:02x}'
            return alias
        if path.name != 'mmc5_expanded.s':
            s = re.sub(r'\$5[c-f][0-9a-f]{2}\b', state, s, flags=re.I)
        path.write_text(s)
    p=OUT/'src/options.s'; s=p.read_text().replace('bool_option ENABLE_MMC5_EXPANDED, 0',
        'bool_option ENABLE_MMC5_EXPANDED, 0\nbool_option ENABLE_MMC3_OVERSIZED, 0\nENABLE_FULL_ROSTER = ENABLE_MMC5_EXPANDED .or ENABLE_MMC3_OVERSIZED')
    p.write_text(s)
    p=OUT/'src/mmc3.s'; s=p.read_text()
    s=s.replace('.if I = 0\n', '''.if I = 2
    bit X5ChrMode
    bpl :+
      lda CurrentCHRBank+2
    :
.endif
.if I = 2
    sta M3HardwareBody
.endif
.if I = 0
''',1)
    s=s.replace('    sta BANK_DATA\n  .if I <> 5', '.if I = 1\n    sta M3HardwareSpecial\n.endif\n    sta BANK_DATA\n  .if I <> 5',1)
    p.write_text(s)
    p=OUT/'src/character_select.s'; s=p.read_text()
    # Keep all selection portraits resident. Full family transfers happen only
    # behind the ordinary scene transition when the player confirms a hero.
    s=s.replace('  ; Rendering is off; the lag-NMI path leaves the PPU address alone.',
                '  farcall M3MenuLoad\n  ; Rendering is off; the lag-NMI path leaves the PPU address alone.',1)
    a=s.index('.proc QueueSelection\n'); b=s.index('  jsr QueueSelectName',a)
    s=s[:a]+'.proc QueueSelection\n  farcall M3MenuSelect\n'+s[b:]
    a=s.index('.proc QueueSelection\n'); b=s.index('.endproc',a)
    selection=s[a:b].replace('  jsr QueueVariantHint\n','')
    s=s[:a]+selection+s[b:]
    # Keep the paired palette/CHR/OAM packet inside VBlank. The decorative
    # control hint can follow on an idle frame without delaying the portrait.
    s=s.replace('SelectInput:\n', '''SelectInput:
  lda CrossoverMenuPressed
  bne M3NoHintUpdate
  lda CurrentOAMOffset
  bpl M3NoHintUpdate
  ldx VRAM_Buffer1_Offset
  bne M3NoHintUpdate
  and #$7f
  sta CurrentOAMOffset
  jsr QueueVariantHint
M3NoHintUpdate:
''',1)
    a=s.index('.proc DrawSelectionPreview\n'); b=s.index('.endproc',a)+len('.endproc')
    s=s[:a]+'.proc DrawSelectionPreview\n  farcall M3MenuDrawPreview,jmp\n.endproc'+s[b:]
    anchor='  farcall MoveAllSpritesOffscreen\n  lda #Sfx_CoinGrab'
    assert s.count(anchor)==1
    s=s.replace(anchor,'  farcall MoveAllSpritesOffscreen\n  farcall M3CacheEnsure\n  lda #Sfx_CoinGrab',1)
    p.write_text(s)
    p=OUT/'src/entrypoint.s'; s=p.read_text(); s=s.replace('.include "memory.s"', '\n'.join(f'{k}={v}' for k,v in sorted(state_aliases.items()))+'\n.include "memory.s"'); p.write_text(s)
    p=OUT/'src/entrypoint.s'; s=p.read_text()
    start=s.index('.if ::MAPPER_MMC5 .and ::ENABLE_FULL_ROSTER')
    end=s.index('.if ::ENABLE_CROSSOVER\nnes2wram',start)
    s=s[:start]+'''nes2prg $200000
nes2chr 0
nes2chrram $40000
'''+s[end:]
    s=s.replace('.if ::MAPPER_MMC5 .and ::ENABLE_FULL_ROSTER', '.if ::ENABLE_FULL_ROSTER')
    s=s.replace('.include "mmc5_expanded.s"', '.include "mmc3_oversized.s"\n.include "mmc3_menu.s"')
    s+='\n.segment "M3_RAW_CHR"\n.incbin "chr/characters/oversized-raw.chr"\n'
    p.write_text(s)
    # Extra MMC5-only audio register values must never set PRG address bit7.
    p=OUT/'src/mmc3.s'; s=p.read_text().replace('PRG_FIXED_8 =', 'MMC5_PRG_ROM = 0\nPRG_FIXED_8 =')
    # Carry the expanded dispatcher leaves into the MMC3 fixed segment.
    m5=(OUT/'src/mmc5.s').read_text()
    leaves=m5[m5.index('::DwResidentGraphicsSelector:'):m5.index('  .res 136-(*-StartPublication)')]
    leaves=leaves.replace('  sta MMC5_PRG_BANK_C','  BankPRGC a')
    s+='\n.segment "LOWCODE"\n'+leaves
    s=s.replace('  ; disable scanline counter, and IRQ', '  ; disable scanline counter, and IRQ')
    s=s.replace('  sta RAM_PROTECT\n\n  rts','''  sta RAM_PROTECT
  lda CurrentBank
  pha
  lda #.bank(X5ColdInit)
  sta CurrentBank
  BankPRGA a
  jsr X5ColdInit
  pla
  sta CurrentBank
  BankPRGA a
  rts''')
    # Six physical banks remain the genuine MMC3 layout.
    p.write_text(s)
    # Preserve the proven MMC3 HUD IRQ rather than invoking MMC5's $5128 path.
    p=OUT/'src/reset.s'; s=p.read_text().replace('.if ::ENABLE_FULL_ROSTER\n  pha', '.if ::MAPPER_MMC5 .and ::ENABLE_FULL_ROSTER\n  pha',1); p.write_text(s)
    s=s.replace('  lda NmiDisable\n  bpl ContinueNMI', '  jsr M3NmiCacheBridge\n  bcs M3UploadHold\n  lda NmiDisable\n  bpl ContinueNMI')
    s=s.replace('    inc NmiSkipped\n', '    inc NmiSkipped\n::M3UploadHold:\n',1)
    # The old Mario-only lag exception must not publish a new menu portrait's
    # CHR page while hardware OAM still contains the previous portrait.
    s=s.replace('    lda SelectedCharacter\n    bne KeepLagChr',
                '    lda CrossoverMenuState\n    cmp #2\n    beq KeepLagChr\n    lda SelectedCharacter\n    bne KeepLagChr',1)
    p.write_text(s)
    # The NMI bridge must not use foreground farcall SMC.
    p=OUT/'src/megaman_audio.s'; s=p.read_text()
    a=s.index('  lda #.bank(ProtoNmiAudioCore)'); b=s.index(' .else',a)
    s=s[:a]+'''  lda CurrentBank
  pha
  BankPRGA #.bank(ProtoNmiAudioCore)
  jsr ProtoNmiAudioCore
  pla
  BankPRGA a
  jmp CrossoverGraphicsBank
'''+s[b:]; p.write_text(s)
    # Four ExRAM pages are mutually exclusive transient overlays; persistent
    # records occupy separate inactive MM sound state, menu choices stay resident.
    p=OUT/'src/x5_profiles.s'; s=p.read_text(); a=s.index('.proc X5ProfilesNewGame'); b=s.index('.endproc',a)+len('.endproc')
    s=s[:a]+'''.proc X5ProfilesNewGame
  lda #0
  tax
Clear:
  sta RgAudioRam,x
  sta MmAudioRamStart,x
  inx
  bne Clear
  lda SelectedCharacter
  cmp #CHARACTER_MEGAMAN
  bne Done
  jsr MegaManAudioInit
Done:rts
.endproc'''+s[b:]; p.write_text(s)
    p=OUT/'src/zelda2_link_motion.s'; s=p.read_text().replace(' sta $5104', ' ;sta $5104'); p.write_text(s)
    p=OUT/'src/megaman_physics.s'; s=p.read_text().replace('.segment "PLAYER"\n.macro MmMultiplyRoutine', '.segment "M3_MATH"\n.macro MmMultiplyRoutine'); p.write_text(s)
    p=OUT/'src/metasprite_engine.s'; s=p.read_text().replace('.segment "METASPRITE"\n.proc GuestHudOamOrder', '.segment "M3_COLD"\n.proc GuestHudOamOrder').replace('jsr GuestHudOamOrder','farcall GuestHudOamOrder')
    s=s.replace('    farcall GuestHudOamOrder', '    farcall M3ResolveOam\n    farcall GuestHudOamOrder')
    s=s.replace('PlayerBankReady:\n', 'PlayerBankReady:\n      bit X5ChrMode\n      bmi M3KeepDirectBody\n')
    s=s.replace('      jsr DrawMetasprite\n  DoneDrawingPlayer:', 'M3KeepDirectBody:\n      jsr DrawMetasprite\n  DoneDrawingPlayer:')
    p.write_text(s)
    p=OUT/'src/megaman_weapons.s'; s=p.read_text().replace('.segment "LOWCODE"\n.proc MegaManCollisionAdder','.segment "M3_COLD"\n.proc MegaManCollisionAdder').replace('.proc CrossoverBlockSize','.segment "LOWCODE"\n.proc CrossoverBlockSize'); p.write_text(s)
    p=OUT/'src/samus_crouch_collision.s'; s=p.read_text().replace('.segment "SAMUS_CROUCH_BODY"','.segment "M3_COLD"'); p.write_text(s)
    for name in ('collision.s','player.s','samus_legacy_bomb.s'):
        p=OUT/'src'/name; s=p.read_text().replace('jsr MegaManCollisionAdder','farcall MegaManCollisionAdder').replace('jsr MegaManCollisionBox','farcall MegaManCollisionBox'); p.write_text(s)
    p=OUT/'src/zelda2_link_state.inc'; s=p.read_text().replace('Z2TransientEnd=M3State_5e80','Z2TransientEnd=RgAudioRam+$80'); p.write_text(s)
    p=OUT/'src/guest_injury.s'; s=p.read_text().replace('  .res 7,$ea\n  .assert *-GuestPlayerVisible=25,error,"fixed original span"',''); p.write_text(s)
    # Pointers assembled as separate immediate bytes need the same relocation.
    for name,old in (('kirby_draw.s',0x90),('tmnt_draw.s',0xa0)):
        p=OUT/'src'/name; s=p.read_text()
        s=s.replace(f'lda #${old:02x}\n',f'lda #<(RgAudioRam+${old:02x})\n').replace('lda #$5c\n',f'lda #>(RgAudioRam+${old:02x})\n')
        p.write_text(s)
    # Native OAM records that carry literal tile bytes need the same pattern
    # table conversion as MetaspriteVramOffset. Validate complete record sizes.
    records=[]
    def tile(n):
        return (n|1) if not n&1 else (0xc0 if n<64 else 0x80)|(n&62)
    for name in ('kirby_art.inc','meta_knight_art.inc','tmnt_art.inc','mike_jones_art.inc','smb3_mario_art.inc','smb3_mario_world_art.inc','vic_art.inc'):
        p=OUT/'src'/name; s=p.read_text()
        def record(m):
            head,body=m.groups()
            try:
                values=[int(v.strip().replace('$','0x'),0) for line in body.splitlines() for v in line.split('.byte',1)[1].split(',')]
            except (ValueError,IndexError):return m[0]
            if not values or values[0]%4 or len(values)!=values[0]+1:return m[0]
            for i in range(1,len(values),4):
                if values[i]&1:values[i+1]|=16
                values[i]=tile(values[i])
            records.append(dict(file=name,label=head.split(':')[0],sprites=values[0]//4))
            return head+'\n .byte '+','.join(map(str,values))+'\n'
        s=re.sub(r'(^[A-Za-z_][A-Za-z_0-9]*:\s*)(\.byte [^\n]+\n(?:[ \t]*\.byte [^\n]+\n)*)',record,s,flags=re.M)
        for table in ('KbHealthTiles','TnHealthTiles'):
            s=re.sub(r'('+table+r':\s*\.byte )([0-9,]+)',lambda m:m[1]+','.join(str(tile(int(n)))for n in m[2].split(',')),s)
        p.write_text(s)
    for p in (OUT/'src').glob('*art.inc'):
        if p.name.startswith(('protoman','ordinary','bass','rygar','samus')):continue
        s=p.read_text()
        s=re.sub(r'(\{SPRITE_BANK_[45]\},)\s*([^,\n]+),',r'\1 (\2 | $10),',s)
        p.write_text(s)
    # MMC3 uses the native font for the six Gradius bar labels. Ownership,
    # highlight, equipment and capsule progression keep the original behavior.
    p=OUT/'src/vic_render.s'; s=p.read_text()
    s=s.replace(' lda #<394\n sta InvHudPhysical\n lda #>394\n sta X5HudChrUpper',' lda #0\n sta InvHudActive')
    s=s.replace(':lda #1\n sta InvHudActive',':lda #0\n sta InvHudActive')
    s=s.replace(' lda #1\n sta InvHudActive',' lda #0\n sta InvHudActive')
    s=s.replace('.include "vic_hud.inc"','VvHudCells: .byte "SPD MSL DBL LSR OPT SHD     "')
    p.write_text(s)
    (OUT.parent/'literal-oam-conversion.json').write_text(json.dumps(records,indent=2)+'\n')
    # Bank growth is allowed in this separate port. Old fixed-footprint padding
    # exists to preserve previous binary PCs, not as an engine requirement.
    for name in ('expanded.s',):
        p=OUT/'src'/name; s=p.read_text()
        s=re.sub(r'^\s*\.assert .*?,error,"(original graphics bank span|Original collision leaf span)".*$', '',s,flags=re.M)
        # These bytes follow unconditional exits and only preserved old PCs.
        # The oversized port resolves calls through labels, so retain room for
        # the NMI queue ownership guard instead of dead NOP padding.
        s=re.sub(r'^\s*\.res (?:6|3|7),\$ea\s*$', '',s,flags=re.M)
        p.write_text(s)
    cfg=(OUT/'smb1base-mmc5-expanded.cfg').read_text()
    cfg=re.sub(r'    X5_NEW_(?:6[4-9A-F]|7[0-9A-D]):[^\n]*\n', '', cfg)
    # Original graphics stay at100..227; additional music uses free231..253.
    # Linker-derived .bank pointers follow these placements automatically.
    for bank in range(23):
        cfg=cfg.replace(f'load=X5_NEW_{100+bank:02X},type=ro;',f'load=M3_FREE_{231+bank:02X},type=ro;')
    at=cfg.index('    PRGLow:')
    extra='    M3_RAW: start=$0000,size=$100000,type=ro,file=%O,fill=yes,fillval=$00,bank=$64;\n'
    extra+=''.join(f'    M3_FREE_{n:02X}: start=$a000,size=$2000,type=ro,file=%O,fill=yes,fillval=$ff,bank=${n:02x};\n' for n in range(228,254))
    cfg=cfg[:at]+extra+cfg[at:]
    cfg=cfg.replace('bank = $7e','bank = $fe').replace('bank = $7f','bank = $ff')
    # Non-emitting graphics segments retain original physical label arithmetic.
    lines=cfg.splitlines()
    for i,line in enumerate(lines):
        if re.match(r'\s*(CHR|X5_CHR_MORE|\w+_CHR_MEM|TMNT_CHR_TAIL):',line):
            lines[i]=line.replace('file = %O','file = ""').replace('file=%O','file=""')
    cfg='\n'.join(lines)+'\n'
    cfg=cfg.replace('SEGMENTS {','SEGMENTS {\n    M3_RAW_CHR: load=M3_RAW,type=ro;\n    M3_CACHE: load=M3_FREE_E4,type=ro;')
    cfg=cfg.replace('SEGMENTS {','SEGMENTS {\n    M3_MENU: load=M3_FREE_F7,type=ro;')
    cfg=cfg.replace('    M3_CACHE:', '    M3_MATH: load=M3_FREE_E5,type=ro;\n    M3_CACHE:')
    cfg=cfg.replace('    M3_CACHE:', '    M3_COLD: load=M3_FREE_E6,type=ro;\n    M3_CACHE:')
    cfg=cfg.replace('M3_FREE_E4: start=$a000','M3_FREE_E4: start=$c000')
    cfg=cfg.replace('ROSTER:          load = ROSTER_MEM, type = ro,','ROSTER:          load = ROSTER_MEM, type = ro, align=2,')
    for segment in ('DARKWING_DRAW_GUARD','Z2_DRAW_GATE','X5_DRAW_GATE'):
        cfg=re.sub(r'('+segment+r':[^\n]*?),\s*start=\$[0-9a-fA-F]+',r'\1',cfg)
    # The old bank4 tail now has room after moving the resident IRQ OAM policy.
    (OUT/'smb1base-mmc3-oversized.cfg').write_text(cfg)
    raw=bytearray(1048576)
    prepared=OUT/'chr/characters'
    assets=[(0,('packed-mmc5-expanded.chr',)),(256,('protoman.chr',)),(276,('darkwing.chr',)),
        (308,('zelda2-link-body.chr','zelda2-link-items.chr')),(340,('kirby.chr',)),(380,('vic-viper.chr',)),
        (412,('chip-dale.chr',)),(460,('cv3.chr',)),(524,('smb3-mario.chr',)),(604,('tmnt.chr',)),
        (668,('little-mac.chr',)),(708,('mike-jones.chr',))]
    for page,names in assets:
        data=b''.join((prepared/n).read_bytes()for n in names)
        raw[page*1024:page*1024+len(data)]=data
    # Native linked assets added after the initial oversized packing list.
    roll=(prepared/'roll.chr').read_bytes();assert len(roll)==24576
    raw[364*1024:380*1024]=roll[:16384]
    raw[304*1024:308*1024]=roll[16384:20480]
    raw[336*1024:340*1024]=roll[20480:24576]
    ui=(prepared/'zelda2-pause-font.chr').read_bytes();assert len(ui)==1024
    raw[395*1024:396*1024]=ui
    # Graphical Parodius fonts share the verified unused gap before Chip412.
    hud=prepared/'parodius-hud.chr'
    if hud.exists():
        data=hud.read_bytes();assert len(data)==3072
        raw[396*1024:399*1024]=data
    parodius=(prepared/'parodius.chr').read_bytes();assert len(parodius)==192*1024
    raw[832*1024:1024*1024]=parodius
    released=args.reference_rom.resolve()
    assert released.is_file(), 'Build the MMC5 reference before preparing this port'
    assert raw==released.read_bytes()[16+1048576:],'Prepared art and specified MMC5 reference must agree before porting'
    base=(OUT/'chr/characters/packed-mmc3.chr').read_bytes()
    # Full-roster UI font/grid replaces the four existing menu pages.
    base=bytearray(base.ljust(262144,b'\0')); base[4*1024:8*1024]=raw[4*1024:8*1024]
    packed=bytearray(bytes(base)+raw[262144:])
    menu=(ROOT/'chr/characters/mmc3-menu-previews.chr').read_bytes()
    assert len(menu)==66*1024 and not any(packed[756*1024:822*1024])
    packed[756*1024:822*1024]=menu
    (OUT/'chr/characters/oversized-raw.chr').write_bytes(packed)
    for name in ('mmc3_oversized.s',):
        (OUT/'src'/name).write_text((ROOT/'ports/mmc3-oversized'/name).read_text())
    (OUT/'src/mmc3_menu.s').write_bytes((ROOT/'ports/mmc3-oversized/menu.s').read_bytes())
    (OUT/'src/mmc3_menu_art.inc').write_bytes((ROOT/'ports/mmc3-oversized/menu_art.inc').read_bytes())
    print(OUT)

    from mmc3_current_repairs import apply
    apply(OUT, Path(__file__).resolve().parent/'mmc3_oversized')

if __name__=='__main__':main()
