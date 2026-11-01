"""Pure integration of the source HUD in already allocated Karnov carriers."""
from pathlib import Path
from prepare_karnov_equipment_hud_1101_v9 import split_source
from prepare_karnov_hud_funding_1101_v9 import transform_sources as fund
R=Path(__file__).resolve().parents[2]
HOST=R/'tools/reference/karnov_equipment_hud_1101_v9.inc'
FONT=R/'build/karnov-equipment-hud-1101-v9/equipment-font.chr'
GRANT=R/'build/karnov-hud-resource-1101-v9/resource-grant.json'
GRANT_SHA='98bd4f8626d7322edc437c3b8f1a049963342821d91d6527b24a0450d6b05885'


def once(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)


def transform_sources(*,kernel,resident,terrain,entrypoint,config,carrier_helper):
    funded=fund(resident=resident,carrier_helper=carrier_helper)
    resident=funded['resident'];fragments=dict(funded['fragments'])
    constants='''KrHudCache=$c87a
KrHudPhysicalLow=$ff
KrHudPhysicalHigh=3
.import SelectedCharacter,OperMode_Task,VRAM_Buffer_AddrCtrl
.import InvHudActive,InvHudPhysical,X5HudChrUpper,X5WideChrActive,ReloadCHRBank
'''
    source=constants+'.include "kr-hud-charmap.inc"\n'+split_source(HOST.read_text())
    source+='\n.assert KrHudEnd <= $de00,lderror,"HUD exceeds options carrier"\n.assert KrHudDataEnd <= $ce00,lderror,"HUD constants exceed combat carrier"\n'
    fragments['kr-hud-host-v9.inc']=source
    fragments['kr-hud-charmap.inc']=(R/'inc/charmap.inc').read_text()
    kernel=once(kernel,'KrKernelEnd:','.include "kr-hud-host-v9.inc"\nKrKernelEnd:')
    start=kernel.index('KrCacheServices:');end=kernel.index('KrReject:',start)
    rows=kernel[start:end].splitlines();indices=[i for i,s in enumerate(rows)if s.startswith(' jmp ')]
    assert len(indices)==37 and rows[indices[29]]==' jmp KrReject'
    rows[indices[29]]=' jmp KrHudTick'
    kernel=kernel[:start]+'\n'.join(rows)+'\n'+kernel[end:]
    # The authenticated constructor owns both new-life and same-life seams.
    # Force a new derived HUD packet after native scene text has been rebuilt.
    terrain=once(terrain,'KrConstruct:\n KrSave','KrConstruct:\n KrSave\n jsr KrHudCancel')
    entrypoint+='\n.export InvHudActive,InvHudPhysical,VRAM_Buffer_AddrCtrl,OperMode_Task\n'
    config+='\nSEGMENTS { KR_HUD_FONT_IMAGE:load=CF_CHR_POST,type=ro,start=$ffc00; }\n'
    return dict(kernel=kernel,resident=resident,terrain=terrain,entrypoint=entrypoint,config=config,fragments=fragments,
                service_rows={29:'KrHudTick'},font_page=1023,cache=[0xc87a,0xc880],ROM_retirement=True,
                constructor_cancel=True)
