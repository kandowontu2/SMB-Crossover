"""Prepare isolated Zelda II terrain correction; do not install or publish it."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load, address, location

ROOT = Path(__file__).resolve().parents[2]


def replace(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    source = out/'source'; (source/'src').mkdir(parents=True)
    shutil.copy2(ROOT/'smb1base-mmc5-expanded.cfg', source)
    paths = ['characters.s', 'samus.s', 'little_mac_terrain.s', 'tmnt_probe_gates.s',
             'zelda2_link_motion.s', 'entrypoint.s', 'megaman_weapons.s']
    for name in paths:
        text = (ROOT/'src'/name).read_text()
        if name == 'characters.s':
            start = text.index('::CrossoverSourceFootProbe:\n')
            end = text.index('.endproc', start)
            old = text[start:end]
            new = '''::CrossoverSourceFootProbe:
.if ::ENABLE_MMC5_EXPANDED
  lda SelectedCharacter
  cmp #CHARACTER_LINK
  beq FootCold
  cmp #CHARACTER_SOPHIA
  bne FootNative
  cpy #31
  bne FootCold
  bit SmClearance
  bmi FootNative
FootCold:
  farcall Z2SourceFeetDispatch, jmp
FootNative:
  jmp BlockBufferColli_Feet
  .assert *-CrossoverHeadProbe=62,error,"Expanded head/feet dispatch span"
.else
''' + old + '.endif\n'
            text = text[:start]+new+text[end:]
            text = replace(text, '  .res 12,$ea\n .else\n  farcall TnFastSideGate,jmp', '''::Z2NativeSideSelector:
  cmp #CHARACTER_LINK
  beq OwnZ2Side
  cmp #CHARACTER_SOPHIA
  rts
OwnZ2Side:sec
  rts
  .res 3,$ea
 .else
  farcall TnFastSideGate,jmp''')
            start = text.index('.proc CrossoverHeadWithinTerrain\n')
            end = text.index('.endproc', start)
            old = text[start:end]
            text = text[:start]+''' .if ::ENABLE_MMC5_EXPANDED
.proc CrossoverHeadWithinTerrain
  farcall Z2HeadWithinTerrain, jmp
  .res 1,$ea ; Reuse two bytes for the expanded feet selector above.
.else
'''+old+'.endif\n'+text[end:]
        elif name == 'samus.s':
            old = '''  cmp #CHARACTER_SAMUS
  bne Done
  lda SmCeilingHit               ; Ordinary walking never enters another bank.
  beq Done
  farcall SamusAfterBGCollision
'''
            text = replace(text, old, '''.if ::ENABLE_MMC5_EXPANDED
  cmp #CHARACTER_SAMUS
  beq Handle
  cmp #CHARACTER_LINK
  bne Done
Handle:
  farcall Z2AfterBGDispatch
  nop ; Caller already tests SmCeilingHit; original bridge size is retained.
.else
'''+old+'.endif\n')
        elif name == 'little_mac_terrain.s':
            text = replace(text, '.proc LmWallGate\n', '.proc Z2WallLegacy\n')
        elif name == 'tmnt_probe_gates.s':
            text = replace(text, 'TnMacSideProbe,M3SideDispatch', 'TnMacSideProbe,Z2SideAdmission')
            text = replace(text, 'jmp TnCv3HeadGate', 'jmp Z2HeadAdmission')
        elif name == 'megaman_weapons.s':
            text = replace(text, '  cmp #CHARACTER_SOPHIA\n  bcs OtherSide',
                           '  jsr Z2NativeSideSelector\n  bcs OtherSide')
            text = replace(text, '  .res 3,$ea\n  .assert *-MegaManFullShotBank=55',
                           '  .res 2,$ea\n  .assert *-MegaManFullShotBank=55')
        elif name == 'zelda2_link_motion.s':
            start = text.index('Ordinary:\n')
            end = text.index(' lda SavedJoypadBits\n', start)
            text = text[:start]+'''Ordinary:
 jsr Z2MovementTerrainBegin
 .res 17,$ea ; Preserve every existing movement/native routine address.
'''+text[end:]
        elif name == 'entrypoint.s':
            text = replace(text, '.include "roll.s"', '.include "roll.s"\n.include "zelda2_link_terrain.s"')
        (source/'src'/name).write_text(text)
    # Nested includes resolve beside their parent before the overlay search path.
    for name in ['little_mac.s', 'tmnt.s']:
        shutil.copy2(ROOT/'src'/name, source/'src')
    shutil.copy2(ROOT/'tools/audit/zelda2_link_terrain.candidate.s', source/'src/zelda2_link_terrain.s')
    rom=out/'candidate.nes'
    with(out/'host-build.log').open('w')as log:
        result=subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),
                               '--source-overlay',str(source),'--output',str(rom)],
                              cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    assert result.returncode==0,(out/'host-build.log').read_text()[-4000:]
    old,new=load(a.parent),load(rom)
    assert old['raw'][16+1048576:]==new['raw'][16+1048576:]
    for name,symbol in old['syms'].items():
        if 'seg'in symbol and address(old,name)<0x8000:
            assert address(old,name)==address(new,name),name
    changes=[i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y]
    proof=dict(compiled=True,adopted=False,goal_complete=False,
               ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),
               parent_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
               existing_RAM_and_CHR_exact=True,
               changed_PRG_banks=sorted(set((i-16)//8192 for i in changes)),
               source={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in source.rglob('*')if p.is_file()},
               scope='Private standing/crouched and Fairy terrain points, ceiling separation, floor depth and wall clamp. Fairy lower side points are centered for SMB terrain instead of reproducing the original face-dependent asymmetric lower query. No native admission, enemy-hitbox or full-roster claim.')
    (out/'build-proof.json').write_text(json.dumps(proof,indent=2))
    print(json.dumps(proof),flush=True)


if __name__=='__main__':main()
