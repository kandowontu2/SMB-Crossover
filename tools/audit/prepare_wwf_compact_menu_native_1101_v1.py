"""Require stable gray roster and heading through all90 menu identities."""
from pathlib import Path
import json,sys
import prepare_roster_flicker_native_bounded_v3 as V
from prepare_selected_native_packet_v1 import sha


def main():
    original=V.V.prepare
    def prepare(output,rom,controller,refs,**kw):
        old='local counts={7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,4,1,2,1,6,2,4,2}'
        assert controller.count(old)==1
        controller=controller.replace(old,old.replace('4,1,2,4,1,2,1,6','4,1,2,8,1,2,1,6')).replace('All86','All90')
        refs=[p.with_name('assembly-stage.json')if p.name=='source-stage.json'else p for p in refs]
        kw['scope']='Current85 compact WWF menu: all90 identities/124 transitions. Require unchanged sampled gray roster and exact heading on every observed frame, no visible PPUMASK writes; four PNG cap. No new-character admission.'
        return original(output,rom,controller,[*refs,Path(__file__)],**kw)
    V.V.prepare=prepare;V.main()
    output=Path(sys.argv[sys.argv.index('--output')+1]).resolve();path=output/'controller.lua'
    t=path.read_text();old='ok=ok and headingErrors==0 and lateMasks==0';assert t.count(old)==1
    path.write_text(t.replace(old,old+' and#bad==0'),encoding='utf-8',newline='\n')
    p=output/'ready.json';q=json.loads(p.read_text());q['bindings'][str(path)]=sha(path)
    q['scope']=q['scope'].replace('all2400','all2480')
    p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
