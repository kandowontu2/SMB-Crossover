"""Fix the native menu's behind-background preview priority, source only."""
from pathlib import Path
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/audit'))
import prepare_rogue_current_parity_v1 as parity

O = R / 'build/rogue-current-menu-v6'


def source(out):
    dependencies = parity.source(out)
    path = out / 'src/character_select.s'
    text = path.read_text()
    old = '''  farcall X5PortraitRender
.else
  farcall DrawMetasprite
.endif
  rts
PreviewX:'''
    new = '''  farcall X5PortraitRender
  ; The native Rogue descriptor carries source priority bit5. Menu panels
  ; use opaque background tiles, so publish all preview parts in front.
  ; This changes only the OAM already emitted by this menu invocation.
  ldx CurrentOAMOffset
  beq PreviewPriorityDone
PreviewPriority:
  lda Sprite_Attributes-4,x
  and #$df
  sta Sprite_Attributes-4,x
  txa
  sec
  sbc #4
  tax
  bne PreviewPriority
PreviewPriorityDone:
.else
  farcall DrawMetasprite
.endif
  rts
PreviewX:'''
    parity.base.put(path, parity.once(text, old, new))
    return dependencies + [Path(__file__).resolve()]


if __name__ == '__main__':
    parity.base.main(output=O, source_hook=source, link_hook=parity.link,
                    extra_dependencies=[Path(__file__).resolve(), O/'backend-composition.json'])
