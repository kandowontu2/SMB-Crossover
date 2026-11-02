"""Cold, controller-only route across all six native Thomas helper lifts."""
import json,re
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load

def main():
    out=R/'build/thomas-current-candidate-1102-v3'
    rom=out/'candidate.nes'
    source=R/'build/thomas-full11-1102-v1/native-elevated-support/controller.lua'
    text=source.read_text()
    symbols=scoped_load(R/'build/thomas-current-lifts-1102-v2/candidate.nes')['syms']
    def label(m):
        name=m[1]
        return 'L["'+name+'"]='+str(int(symbols[name]['val'],0)) if name.startswith(('Th','Thomas')) and name in symbols else m[0]
    text=re.sub(r'L\["([^"]+)"\]=\d+',label,text)
    text=text.replace('f5c30ceaa36894f3e814ef277081ecd9cf434a934c0f7b3f514c2291be0e1cfc',sha(rom))
    def once(a,b):
        nonlocal text
        assert text.count(a)==1,a
        text=text.replace(a,b)
    once('["pipes"]=4','["pipes"]=6')
    once('local targets={{400,176},{560,160},{688,144},{864,144}}','local targets={{400,176},{560,160},{688,144},{864,144},{2560,176},{2816,176}}')
    once(" if routeState=='full-stage' then", " if routeState=='full-stage' and #clears<6 and x>=targets[target][1]-112 then routeState='approach';previous=nil end\n if routeState=='full-stage' then")
    once("  else target=target+1;routeState='approach';previous=nil end", "  else target=target+1;routeState=(target>=5 and 'full-stage' or 'approach');previous=nil end")
    prepare(out/'native-six-lifts',rom,text,[Path(__file__),source,out/'composition.json'],expected=sha(rom),timeout=240,allow_interactive=True,
            scope='Cold full1-1 normal controller route: original four lifts plus native late lifts2560/2816; full raster/real interrupt and source pose checks retained. No gameplay RAM writes. Six crossings and active1-2 required; four PNG maximum.')
    ready=out/'native-six-lifts/ready.json';q=json.loads(ready.read_text());q['timeout']=450
    q['host_timeout_evidence']='Prior unchanged observer completed3900Main in240seconds; six-pipe full route keeps12000Main/24000physical and capture bounds.'
    ready.write_text(json.dumps(q,indent=2)+'\n')

if __name__=='__main__':main()
