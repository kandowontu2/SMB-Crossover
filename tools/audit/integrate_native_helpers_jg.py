"""Merge frozen private native components; never modifies the public checkout."""
from pathlib import Path
import hashlib, json, shutil

R=Path(__file__).resolve().parents[2]
S=R/'build/verification/crossover-helpers-jb/source'
A=R/'build/verification/level-variants-candidate-agent'
G=R/'build/player-guide-agent/platform-axis-private'
def replace(path,old,new):
    p=S/path; text=p.read_text()
    if text.count(new)==1:return
    assert text.count(old)==1,(path,old)
    p.write_text(text.replace(old,new))
def main():
    assert not (S/'native-merge-jg.json').exists()
    manifest=json.loads((A/'manifest.json').read_text())
    for name, expected in manifest['source_overlay'].items():
        if name in ('smb1base.cfg','src/entrypoint.s'): continue
        p=A/'source'/name; assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
        shutil.copyfile(p,S/name)
    p=S/'src/entrypoint.s'; t=p.read_text()
    if '.include "level_variants.s"' not in t:
        t=t.replace('.include "crossover_helpers.s"','.include "level_variants.s"\n.include "crossover_helpers.s"')
    p.write_text(t)
    replace('smb1base.cfg','    ZELDA_WRAP_MEM:start=$c000, size=$2000, type=ro, file=%O, fill=yes, fillval=$ff, bank=$1a;',
        '    LEVEL_VARIANTS_MEM:start=$a000, size=$1a00, type=ro, file=%O, fill=yes, fillval=$ff, bank=$1a;\n    HELPER_SELECTOR_MEM:start=$ba00, size=$0200, type=ro, file=%O, fill=yes, fillval=$ff, bank=$1a;\n    ZELDA_WRAP_MEM:start=$dc00, size=$0400, type=ro, file=%O, fill=yes, fillval=$ff, bank=$1a;')
    replace('smb1base.cfg','    ZELDA_WRAP: load=ZELDA_WRAP_MEM, type=ro, start=$dc00, optional=yes;',
        '    LEVEL_VARIANTS: load=LEVEL_VARIANTS_MEM, type=ro, optional=yes;\n    LEVEL_VARIANTS_BRIDGE: load=PRGA_02, type=ro, optional=yes, start=$bfef;\n    ZELDA_WRAP: load=ZELDA_WRAP_MEM, type=ro, start=$dc00, optional=yes;')
    for name in ('native_platform16.s','native_platform16_v2.s','native_platform_bbox_gate.s'):
        shutil.copyfile(G/name,S/'src'/name)
    # The descriptor component owns these aliases once, not twice.
    p=S/'src/crossover_helper_ram.s';t=p.read_text()
    for line in ('HpNativeDrawLo = HpRects\n','HpNativeDrawHi = HpRects+7\n','HpNativeSmallDescriptor = HpRects+14\n'):t=t.replace(line,'')
    p.write_text(t)
    replace('src/sprite_render.s','.include "level_lift_bridges.inc"', '.include "level_lift_bridges.inc"\n.include "native_platform_bbox_gate.s"')
    # Native variable-width helper descriptors use the existing native pose IDs.
    p=S/'src/native_platform16_v2.s';t=p.read_text()
    t=t.replace('  cmp #$60\n  bne Next','  cmp #$40\n  beq OrdinaryWidth\n  cmp #$60\n  bne Next\n  lda #METASPRITE_PLATFORM_GIRDER_SMALL\n  bne SetSmall\nOrdinaryWidth:\n  lda Enemy_BoundBoxCtrl-1,x\n  cmp #6\n  beq Large\n  lda #METASPRITE_PLATFORM_GIRDER_SMALL\n  bne SetPose\nLarge:\n  lda #METASPRITE_PLATFORM_GIRDER_LARGE\nSetPose:\n  sta EnemyMetasprite-1,x\n  jmp Next\nSetSmall:\n  sta EnemyMetasprite-1,x')
    p.write_text(t)
    (S/'native-merge-jg.json').write_text(json.dumps(dict(authored_manifest_sha256=hashlib.sha256((A/'manifest.json').read_bytes()).hexdigest(),main_modified=False),indent=2))
if __name__=='__main__':main()
