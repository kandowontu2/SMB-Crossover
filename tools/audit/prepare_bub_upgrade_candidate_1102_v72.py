"""Emit the privately qualified upgrade candidate and a relocated passive replay."""
import hashlib,json,re,sys
from pathlib import Path
import compose_bub_tail_gateways_1102_v66 as G
from prepare_selected_native_packet_v1 import R,sha,prepare
O=R/'build/bub-upgrades-root-candidate-1102-v72'

def main():
    O.mkdir(exist_ok=True);old,b,route,q=G.bundles();pin=q['expected_memory_only_ROM_SHA256']
    proofs=[]
    for name in ['lifecycle-1102-v67','nested-1102-v68','interrupts-1102-v69','cold-1102-v71']:
        path=R/('build/bub-upgrades-root-'+name+'/receipt.json');p=json.loads(path.read_text());assert p['passed'] and p['ROM_memory_SHA256']==pin
        for f,h in p['bindings'].items():assert sha(R/f)==h,f
        proofs.append(path)
    grant=R/'docs/qa/allocations/joint-native-rare-gate-1102-v70.json';g=json.loads(grant.read_text());assert g['status']=='APPROVED_PRIVATE_SOURCE_COMPOSITION_AND_NATIVE_TEST_ONLY'
    for row in g['approved_exact_patches']:
        at=row['file_offset'];after=bytes.fromhex(row['new']);assert b['raw'][at:at+len(after)]==after
    raw=b['raw'];assert hashlib.sha256(raw).hexdigest()==pin
    source=R/'build/bub-root-delivery-1102-v43/downloads-bub-full11/controller.lua';text=source.read_text()
    sys.path.insert(0,str(R/'build/smb2-final62-observer-lua-deps-v1'));from lupa.lua54 import LuaRuntime,lua_type
    lua=LuaRuntime()
    def native(v):
        if lua_type(v)!='table':return v
        items=dict(v.items())
        if all(isinstance(k,int) for k in items) and set(items)==set(range(1,len(items)+1)):return [native(items[i]) for i in range(1,len(items)+1)]
        return {k:native(v) for k,v in items.items()}
    def literal(v):
        if isinstance(v,dict):return '{'+','.join('['+literal(k)+']='+literal(x) for k,x in sorted(v.items()))+'}'
        if isinstance(v,list):return '{'+','.join(literal(x) for x in v)+'}'
        if isinstance(v,str):return json.dumps(v)
        if v is True:return 'true'
        if v is False:return 'false'
        return str(v)
    image=(G.U.O/'private-image.bin').read_bytes();labels=q['labels'];changes=[]
    def hook(h):
        if h['name'] in labels:
            pc=labels[h['name']];h.update(pc=pc,physical=3*8192+pc-0xa000,bytes=list(image[pc-0xa000:pc-0xa000+4]));changes.append(h['name'])
    for name in ['FULL_CONTACT_HOOKS','BUB_NATIVE_OBSERVER_CONFIG']:
        match=re.search(r'^local '+name+r'=(.*)$',text,re.M);assert match
        val=native(lua.eval(match[1]))
        if name=='FULL_CONTACT_HOOKS':
            for h in val:hook(h)
        else:
            val['ROM_sha256']=pin;val['cookie']=list(bytes.fromhex(q['new_cookie']))
            for h in val['hooks'].values():
                if h['memory']=='nesWorkRam':hook(h)
        text=text[:match.start(1)]+literal(val)+text[match.end(1):]
    text=text.replace(G.U.PIN,pin)
    assert lua.eval('function(s)local f,e=load(s);assert(f,e);return true end')(text)
    for bad in ['emu.write','emu.loadSavestate','emu.loadState','emu.reset']:assert bad not in text
    rom=O/'bub-original-upgrades.nes';rom.write_bytes(raw)
    # Passive controller embeds its native addresses; no full DBG dependency or
    # old symbol tree is copied. Empty DBG is intentionally unused by Lua.
    rom.with_suffix('.lbl').write_text(''.join(f'al {int(value):06X} .{name}\n' for name,value in sorted(re.findall(r'L\["(\w+)"\]=(\d+)',text))))
    rom.with_suffix('.dbg').write_text('')
    refs=[Path(__file__),G.O/'proposal.json',G.U.O/'proposal.json',G.U.O/'private-image.bin',grant,source,*proofs]
    prepare(O/'bub-full11',rom,text,refs,expected=pin,timeout=240,allow_interactive=True,scope='Exact current successor cold controller-only Bub non-shortcut1-1 regression. All source/passive hook PCs/preimages and full payload cookie rebound to compact original component; native entries remain fixed. Uses same verified route with four pipes/three pits, original bubbles and natural combat. No earned upgrade block claim from this baseline route; candidate remains uninstalled.')
    out=dict(prepared=True,installed=False,parent_ROM_SHA256=G.U.PIN,ROM_SHA256=pin,candidate=rom.relative_to(R).as_posix(),relocated_passive_hook_names=sorted(set(changes)),source_short_branch_count=243,source_bytes_reclaimed=729,upgrade_rows=[24,33],original_item_adaptation=dict(mushroom='Original item4:01',flower='Original item2:06 OR into flags'),proofs=[str(p.relative_to(R)) for p in proofs],bindings={str(f.relative_to(R)):sha(f) for f in refs})
    (O/'candidate.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
