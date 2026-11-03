"""Prepare a private head candidate; a probe never qualifies nightly delivery."""
import argparse,hashlib,json,re
from pathlib import Path
import check_bub_head_projection_1102_v56 as H
from prepare_selected_native_packet_v1 import R,sha,prepare
O=R/'build/bub-head-root-candidate-1103-v81'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--isr',type=Path,required=True);ap.add_argument('--nested',type=Path);ap.add_argument('--nmi-i1',type=Path,required=True);ap.add_argument('--probe',action='store_true');a=ap.parse_args()
    assert a.nested is not None or a.probe,'Unqualified private probe must be explicit'
    O.mkdir(exist_ok=True);old,b,route,q,p,image=H.bundle();pin=hashlib.sha256(b['raw']).hexdigest();assert pin==p['memory_ROM_SHA256']
    proofs=[H.O/'head-projection-v55.json',H.O/'head-projection-v56-CPU.json',a.isr.resolve(),a.nmi_i1.resolve()]
    if a.nested is not None:proofs.append(a.nested.resolve())
    for path in proofs:
        proof=json.loads(path.read_text());assert proof['passed'] and proof['memory_ROM_SHA256']==pin
        for f,h in proof['bindings'].items():assert sha(R/f)==h,f
    assert len(image)==8192 and p['bytes']==107 and p['source_gap_remaining']==538
    # Root reviewed source: the original clamp runs unchanged; pending C3EF
    # holds the first-solid column; four original sweep/snapshot cells survive
    # until the sole actual head query. Native processing starts only after
    # resident return, using actual tile/row/preclampDY, never a deep call.
    source=(H.O/'head-projection-v55.s').read_text();assert 'jsr PlayerHeadCollision' not in source
    assert 'sbc $c382' in source and 'sta Player_Y_Speed' in source
    raw=b['raw'];rom=O/'bub-source-head.nes';rom.write_bytes(raw)
    oldrom=R/'build/bub-upgrades-root-candidate-1102-v72/bub-original-upgrades.nes'
    rom.with_suffix('.lbl').write_bytes(oldrom.with_suffix('.lbl').read_bytes());rom.with_suffix('.dbg').write_text('')
    packets=[('bub-mushroom',R/'build/bub-upgrades-root-earned-1102-v74/bub-mushroom/controller.lua',180),('bob-mushroom',R/'build/bub-upgrades-root-earned-1102-v74/bub-mushroom/controller.lua',180),('bub-full11',R/'build/bub-upgrades-root-route-1102-v78/bub-full11/controller.lua',240),('bob-full11',R/'build/bub-upgrades-root-bob-1102-v79/bob-full11/controller.lua',240)]
    paths=[]
    for name,controller,timeout in packets:
        text=controller.read_text();assert text.count(q['expected_memory_only_ROM_SHA256'])>=1
        extra_refs=[]
        if name=='bob-mushroom':
            bob=R/'build/bub-upgrades-root-bob-1102-v79/bob-full11/controller.lua'
            match=re.search(r'^local Q=(.*)$',bob.read_text(),re.M);assert match
            assert '["bob"]=1' in match[1] and '["tag"]="BOB"' in match[1]
            text,n=re.subn(r'^local Q=.*$',lambda m:'local Q='+match[1],text,count=1,flags=re.M);assert n==1
            assert text.count('["identity"]=0')==1
            text=text.replace('["identity"]=0','["identity"]=1');extra_refs.append(bob)
        if name.endswith('-mushroom'):
            # Retain the natural approach/collection assertions, but bound
            # repeated missed bumps across phase resets as well as within one.
            needle="local upgrade_rows,upgrade_mature,upgrade_immature={},false,false"
            assert text.count(needle)==1
            text=text.replace(needle,needle+'\nlocal upgrade_attempts=0')
            needle="then upgrade_phase='bump';upgrade_age=0;full_pad={}end"
            assert text.count(needle)==1
            text=text.replace(needle,"then upgrade_attempts=upgrade_attempts+1;assert(upgrade_attempts<=3,'Bounded three natural mushroom bump attempts');upgrade_phase='bump';upgrade_age=0;full_pad={}end")
        text=text.replace(q['expected_memory_only_ROM_SHA256'],pin)
        newcookie='["cookie"]={'+','.join(str(v) for v in bytes.fromhex(p['cookie']))+'}'
        text,n=re.subn(r'\["cookie"\]=\{[\d,]+\}',lambda m:newcookie,text,count=1);assert n==1
        # All existing passive hooks keep their physical PCs. Verify their
        # current four-byte preimages, including unchanged entry instructions.
        cfg=re.search(r'^local BUB_NATIVE_OBSERVER_CONFIG=(.*)$',text,re.M);assert cfg
        import sys
        sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime
        lua=LuaRuntime();config=lua.eval(cfg[1])
        for _,hook in config['hooks'].items():
            if hook['memory']=='nesWorkRam':
                pc=int(hook['pc']);assert bytes(int(hook['bytes'][i]) for i in range(1,5))==image[pc-0xa000:pc-0xa000+4],hook['name']
        assert lua.eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
        refs=[Path(__file__),controller,H.O/'head-projection-v55-image.bin',*proofs,*extra_refs]
        prepare(O/name,rom,text,refs,expected=pin,timeout=timeout,allow_interactive=True,scope=('Unqualified private probe; nested lag-audio IRQ proof remains pending. ' if a.probe else '')+'Root private native head candidate: source-owned actual ceiling event projects sampled tile/row/column/upwardDY into ordinary native head getter after movement transport returns. Both controller-only fullroutes retain all support/collision/source/hardware assertions; earnedfirstmushroom packet retains natural block emergence/maturity/collection/transform/no-life-loss assertions. No installation or allpowerup claim.')
        paths.append(str((O/name/'ready.json').relative_to(R)))
    out=dict(prepared=True,installed=False,probe=a.probe,CPU_qualified=not a.probe,parent_ROM_SHA256=q['expected_memory_only_ROM_SHA256'],ROM_SHA256=pin,cookie=p['cookie'],candidate=rom.relative_to(R).as_posix(),packets=paths,private_patches=p['private_patches'],new_RAM_or_CHR_pages=0,proofs=[str(f.relative_to(R)) for f in proofs],bindings={str(f.relative_to(R)):sha(f) for f in [Path(__file__),*proofs,H.O/'head-projection-v55-image.bin']})
    (O/'candidate.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['private_patches','bindings']}))
if __name__=='__main__':main()
