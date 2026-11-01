"""Source graft for authenticated Karnov combat and its cold-loaded carrier.

The caller must separately verify the proposed CHR1019/1020 ownership grant.
This module only returns source; it never writes or patches a ROM.
"""
from pathlib import Path
import re
from prepare_karnov_combat_stack_1101_v3 import transform_source
from prepare_karnov_loader_funding_1101_v6 import transform_sources as fund

R=Path(__file__).resolve().parents[2]
HELPER=R/'tools/reference/karnov_combat_carrier_loader_1101_v3.inc'


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def transform_sources(*,kernel,resident,terrain,entrypoint,config,output):
    """Preserve all native owners; add only an authenticated selected C2 child."""
    funded=fund(resident=resident,helper_source=HELPER.read_text(),carrier=True)
    resident=funded['resident'];fragments=dict(funded['fragments'])
    combat=transform_source()
    # These are definitions in the owning kernel object, not external imports.
    combat=once(combat,'.import KrState,KrReady,KrHaveEpoch,KrLastEpoch,KrCameraLo,KrCameraHi\n','')
    combat=once(combat,'.import PlayerSize,CrouchingFlag,Player_X_Position,Player_PageLoc',
                '.import PlayerSize,CrouchingFlag\n.importzp Player_X_Position,Player_PageLoc')
    combat=once(combat,'.import Player_Y_Position,Player_Y_HighPos,Player_Y_Speed,MmBlockAttack',
                '.import MmBlockAttack\n.importzp Player_Y_Position,Player_Y_HighPos,Player_Y_Speed')
    combat=once(combat,'.segment "KR_COMBAT_KERNEL"','.segment "KR_KERNEL"')
    # Original8x8 projectile tiles occupy the bottom half of each NES8x16
    # pair. The renderer deliberately uses the unchanged source anchor.
    # Contact bounds must describe that visible tile, not the blank top half.
    combat=once(combat,' lda KrState+$70,x\n sta KC_Y',
                ' lda KrState+$70,x\n clc\n adc #8\n sta KC_Y')
    fragments['kr-combat-v7.inc']=combat
    kernel=once(kernel,'KrKernelEnd:','.include "kr-combat-v7.inc"\nKrKernelEnd:')
    start=kernel.index('KrCacheServices:');end=kernel.index('KrReject:',start)
    rows=kernel[start:end].splitlines();indices=[i for i,s in enumerate(rows)if s.startswith(' jmp ')]
    assert len(indices)==37
    for row in [4,34]:
        assert rows[indices[row]]==' jmp KrReject'
        rows[indices[row]]=' jmp KrCombat'
    kernel=kernel[:start]+'\n'.join(rows)+'\n'+kernel[end:]
    # Both same-life scene transitions and new-life constructors clear source
    # shots. Reset their contact epoch and canonical victim mask at that owner.
    terrain=once(terrain,' jsr Kr_C2B7                ; original nine-projectile clear on scene transfer',
                 ' jsr Kr_C2B7                ; original nine-projectile clear on scene transfer\n jsr KrCombatReset')
    imports=[]
    for group in re.findall(r'\.import ([^\n]+)',combat):
        imports.extend(n.strip()for n in group.split(','))
    natives=[n for n in imports if not(n.startswith('KC_')and n.endswith('_BANK'))]
    entrypoint+='\n.export '+','.join(natives)+'\n'
    for n in imports:
        if n.startswith('KC_')and n.endswith('_BANK'):
            target=n[3:-5]
            entrypoint+=f'.export {n}\n{n}=.lobyte(.bank({target})|$80)\n'
    memory=f'KR_COMBAT_RAM_MEM:start=$c900,size=$500,type=ro,bank=2,fill=yes,fillval=$ff,file="{(Path(output)/"kr-combat.bin").as_posix()}";\n'
    assert 'KR_COMBAT_RAM_MEM'not in config
    config=once(config,'MEMORY {\n','MEMORY {\n'+memory)
    config+='\nSEGMENTS { KR_COMBAT_ROM:load=KR_COMBAT_RAM_MEM,type=ro; KR_COMBAT_IMAGE:load=CF_CHR_POST,type=ro,start=$fec00; }\n'
    return dict(kernel=kernel,resident=resident,terrain=terrain,entrypoint=entrypoint,config=config,fragments=fragments,
                service_rows={4:'KrCombat',34:'KrCombat'},carrier=[1019,1020],copy_C2=[0xc900,0xce00],
                frame_context_C2=[0xc868,0xc87a])
