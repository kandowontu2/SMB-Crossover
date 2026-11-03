"""Rebind actual controller packets to the owner-only initial-tier candidate."""
import json,re,sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha,prepare
O=R/'build/bub-initial-tier-native-1103-v88'
OLD='cc7b9bddfd39c62fadb5c1afc34bc82361432eab5a8a8e5b5a18bde184813a4e'
def main():
    O.mkdir(exist_ok=True);manifest=R/'build/bub-initial-tier-1103-v87/proposal.json';q=json.loads(manifest.read_text())
    assert q['passed']and q['stack_growth']==0 and not q['installed']
    for f,h in q['bindings'].items():assert sha(R/f)==h,f
    rom=R/q['candidate'];assert sha(rom)==q['ROM_SHA256'];image=(R/'build/bub-initial-tier-1103-v87/private-image.bin').read_bytes()
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
    for identity in ['bub','bob']:
        for task in ['mushroom','full11']:
            source=R/(f'build/bub-head-earned-alignment-1103-v83/{identity}-mushroom/controller.lua'if task=='mushroom'else f'build/bub-head-root-candidate-1103-v81/{identity}-full11/controller.lua')
            text=source.read_text();assert text.count(OLD)>0;text=text.replace(OLD,q['ROM_SHA256'])
            field='["cookie"]={'+','.join(str(v)for v in bytes.fromhex(q['cookie']))+'}'
            text,n=re.subn(r'\["cookie"\]=\{[\d,]+\}',lambda _:field,text,count=1);assert n==1
            cfg=re.search(r'^local BUB_NATIVE_OBSERVER_CONFIG=(.*)$',text,re.M);assert cfg
            lua=LuaRuntime();config=lua.eval(cfg[1])
            for _,hook in config['hooks'].items():
                if hook['memory']=='nesWorkRam':
                    pc=int(hook['pc']);assert bytes(int(hook['bytes'][i])for i in range(1,5))==image[pc-0xa000:pc-0xa000+4],hook['name']
            assert lua.eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
            prepare(O/f'{identity}-{task}',rom,text,[Path(__file__),source,manifest],expected=q['ROM_SHA256'],timeout=180 if task=='mushroom'else 240,allow_interactive=True,scope='Private actual native initial-tier probe. Source/native constructor and20genuine IRQ/FF new-instruction cuts pass; parent head nested audio proof remains pending. Actual menu previously visits SMB2 before Bub/Bob; own cold/new-life tier now0, sourceflags0; warmFresh unchanged. Retain original fullroutes and actual mushroom emergence/maturity/pickup/transformation/lives/hardware assertions. No installation or allpowerup claim.')
    (O/'prepared.json').write_text(json.dumps(dict(prepared=True,installed=False,fully_qualified=False,ROM_SHA256=q['ROM_SHA256'],candidate=q['candidate'],bindings={str(f.relative_to(R)):sha(f)for f in[Path(__file__),manifest]}),indent=2)+'\n')
if __name__=='__main__':main()
