"""Bind all referenced observer symbols, including dynamic callback names."""
import json,re
from pathlib import Path
import propose_wwf_generic_helper_1102_v1 as P
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/thomas-full11-1102-v1'
def main():
    source=O/'native/controller.lua';text=source.read_text();b=P.scoped_load(P.BASE)
    names=set(re.findall(r"['\"]([A-Za-z_]\w*)['\"]",text))|set(re.findall(r'\bL\.(\w+)',text))
    labels={n:P.address(b,n) for n in names if n in b['syms']}
    text='L=L or {}\n'+'\n'.join(f'L[{json.dumps(n)}]={v}' for n,v in sorted(labels.items()))+'\n'+text
    rom=R/'build/wwf-helper-stable-1102-v2/candidate2.nes'
    prepare(O/'native-symbols',rom,text,[Path(__file__),source],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Same Thomas full-stage replay with complete observer labels. Prior attempt failed missingFmAlts before gameplay; no controls or gameplay assertions changed.')
if __name__=='__main__':main()
