"""Inventory actual current menu confirmation and displayed status glyphs."""
from pathlib import Path
import sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from prepare_selected_native_packet_v1 import R
ROM=R/'build/thomas-current-candidate-1102-v3/candidate.nes'
O=R/'build/menu-indicators-1102-v1'

def bundle():
    b=scoped_load(R/'build/kirby-approach-owner-1101-v3/candidate.nes')
    for parent in [R/'build/bub-menu-candidate-1102-v2/combined-event.nes',ROM]:
        n=scoped_load(parent);mapping={}
        for key,seg in n['segs'].items():
            new=parent.parent.name+'_'+str(key);b['segs'][new]=seg;mapping[key]=new
        for name,sym in n['syms'].items():
            row=dict(sym)
            if 'seg' in row:row['seg']=mapping[row['seg']]
            b['syms'][name]=row
    b['raw']=ROM.read_bytes()
    return b

def main():
    b=bundle()
    source=R/'tools/audit/inventory_playable_menu_1101_v3.py'
    text=source.read_text().replace('for slot in range(32):','for slot in range(33):')
    space={'__name__':'menu_indicators','__file__':str(source)}
    exec(compile(text,str(source),'exec'),space)
    space['scoped_load']=lambda path:b
    sys.argv=[str(source),'--rom',str(ROM),'--output',str(O)]
    space['main']()

if __name__=='__main__':main()
