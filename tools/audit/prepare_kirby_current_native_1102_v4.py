"""Rebind the focused Kirby regression to the current 33-slot cartridge."""
import sys,json
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha,prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
ROM=R/'build/thomas-current-candidate-1102-v3/candidate.nes'
OLD=R/'build/kirby-approach-owner-1101-v3/candidate.nes'
MENU=R/'build/bub-menu-candidate-1102-v2/combined-event.nes'
O=R/'build/kirby-current-native-1102-v4'

def main():
    assert sha(ROM)=='d0b445a71d6c539804d7c559fafc2c328ebf97ab4e35e8f3273f94ff8a25d01d'
    b=scoped_load(OLD);raw=ROM.read_bytes()
    for name in ['KbWeapons','KbBodyContact','KbMovement','KbInjuryStart','MkWeapons']:
        at=location(b,name);size=int(b['syms'][name]['size'],0)
        assert b['raw'][at:at+size]==raw[at:at+size],name
    # Current slim symbols supersede historical locations, including menu tables.
    for parent in [MENU,ROM]:
        n=scoped_load(parent);mapping={}
        for key,seg in n['segs'].items():
            new='current_'+parent.parent.name+'_'+str(key);b['segs'][new]=seg;mapping[key]=new
        for name,sym in n['syms'].items():
            row=dict(sym)
            if 'seg' in row:row['seg']=mapping[row['seg']]
            b['syms'][name]=row
    b['raw']=raw
    source=R/'tools/audit/prepare_kirby_owner_native_1101_v2.py'
    text=source.read_text()
    for old,new in [('+32])for k', '+33])for k'),('for start in range(32):','for start in range(33):'),('assert 0<=z<32','assert 0<=z<33')]:
        assert text.count(old)==1,old;text=text.replace(old,new)
    space={'__name__':'kirby_current_packet','__file__':str(source)}
    exec(compile(text,str(source),'exec'),space)
    space['scoped_load']=lambda path:b
    def publish(output,rom,controller,refs,**kw):
        old="world()+((task.face or 1)==1 and 8 or -8),184,0"
        assert controller.count(old)==1;controller=controller.replace(old,"world()+((task.face or 1)==1 and 2 or -2),184,0")
        old="if phase=='warm'then b.b=true"
        assert controller.count(old)==1;controller=controller.replace(old,"if phase=='warm'then b.b=true;b[(task.face or 1)==1 and 'right'or 'left']=true")
        kw['allow_interactive']=True
        return prepare(output,rom,controller,[*refs,Path(__file__),OLD,OLD.with_suffix('.dbg'),MENU,MENU.with_suffix('.dbg')],**kw)
    space['prepare']=publish
    sys.argv=[str(source),'--rom',str(ROM),'--output',str(O/'native')]
    space['main']()

if __name__=='__main__':main()
