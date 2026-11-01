"""Strict sampled-roster/heading/mask sweep of the actual selectable WIP."""
from pathlib import Path
import json,sys
import prepare_karnov_menu_native_1101_v1 as K
from prepare_selected_native_packet_v1 import sha


def main():
    K.main()
    root=Path(sys.argv[sys.argv.index('--output')+1]).resolve()
    path=root/'controller.lua';t=path.read_text()
    marker='ok=ok and headingErrors==0 and lateMasks==0'
    assert t.count(marker)==1
    path.write_text(t.replace(marker,marker+' and#bad==0'),encoding='utf-8',newline='\n')
    path=root/'ready.json';q=json.loads(path.read_text())
    q['bindings'][str(root/'controller.lua')]=sha(root/'controller.lua')
    q['bindings'][str(Path(__file__).resolve())]=sha(__file__)
    q['scope']='Actual selectable86 WIP: all90 roster identities/124 transitions. Exact heading, unchanged sampled gray roster and no visible PPUMASK writes. Four PNG cap; no full-stage or complete-character claim.'
    path.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
