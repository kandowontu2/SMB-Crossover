"""Prepare source-funded77B router proposal; no candidate ROM mutation."""
from pathlib import Path
import json,re,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_excitebike_dispatch_1101_v1 import O,sha,labels,save
from prepare_excitebike_host_1101_v1 import BASE,PIN

def main():
    assert sha(BASE)==PIN;b=scoped_load(BASE);raw=b['raw'];start=16+79*8192
    old=bytes.fromhex('ba bc0201 bd0101 9d0201 68 28 68 aa 68 68 4c6101'.replace(' ',''))
    assert raw[start+0x1f91:start+0x1fa4]==old
    tables=raw[start+0x1fa4:start+0x1fb0];assert len(tables)==12
    (O/'router-callback-tables.bin').write_bytes(tables)
    assert raw[start+0x1f7e:start+0x1f85]==bytes.fromhex('d030a99d4ccfbf')
    assert raw[start+0x1fb0:start+0x1fb3]==bytes.fromhex('4c07a7')
    assert raw[start+0x707:start+0x737]==bytes.fromhex('c020d00668a8284ce7baad0260c924d0034cb3bfa9ab8d6d01988d6c010a6d6c01696d8d6c01a9ce8d62014cb2b8eaea')
    assert raw[start+0x1fb3:start+0x1fcd]==bytes.fromhex('a9aa8d6d01988d6c010a6d6c0169888d6c01a9c18d62014cb2b8')
    reads={}
    for name,target in [('Hi',0xbfa4),('Bank',0xbfaa)]:
        pattern=bytes([0xb9,target&255,target>>8]);positions=[]
        for i in range(8190):
            if raw[start+i:start+i+3]==pattern:positions.append(0xa000+i)
        assert len(positions)==1,(name,positions);reads[name]=positions
    # Source-owned immutable table references are exactly these two indexed
    # readers. The 72-byte drops/weapons compiler macro provides no other
    # address-taken references. The sole native Kr branch names MetalRoute.
    source=(R/'tools/reference/metal_storm_union_funding_1101_v12.inc').read_text()
    for name in ['Hi','Bank']:assert len(re.findall(r'lda Ms12Callback'+name+r',y',source))==1
    assert source.count('bne Ms12MetalRoute')==1
    definitions=''.join(f'{n}=${address(b,n):04x}\n'for n in ['SelectedCharacter','FarcallJmpTarget_SMC','NextBank_SMC','HuCommonRestore','HuNativeWorldPalette'])
    entry=definitions+(R/'tools/reference/excitebike_shared_router_1101_v1.s').read_text()+'''
.segment "EX_CALLBACK"
.export ExCallbackRestore,ExCallbackHi,ExCallbackBank,ExMetalRouteEntry
ExCallbackRestore:
 pla
 tay
 pla
 tax
 tya
 pha
 plp
 txa
 tay
 pla
 tax
 pla
 pla
 jmp NextBank_SMC
ExCallbackHi:.incbin "router-callback-tables.bin",0,6
ExCallbackBank:.incbin "router-callback-tables.bin",6,6
ExMetalRouteEntry:jmp ExThreeOwnerGate
'''
    (O/'router.s').write_text(entry)
    cfg='MEMORY{G:start=$a707,size=48,file="'+(O/'router-gate.bin').as_posix()+'";R:start=$bfb0,size=29,file="'+(O/'router-route.bin').as_posix()+'";C:start=$bf91,size=31,file="'+(O/'router-callback.bin').as_posix()+'";}SEGMENTS{EX_THREE_GATE:load=G,type=ro;EX_THREE_ROUTE:load=R,type=ro;EX_CALLBACK:load=C,type=ro;}'
    (O/'router.cfg').write_text(cfg);cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe','--bin-include-dir',O,O/'router.s','-o',O/'router.o'],[cc/'ld65.exe','-C',O/'router.cfg',O/'router.o','-o',O/'router-unused.bin','-Ln',O/'router.lbl']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    lab=labels(O/'router.lbl');assert [len((O/n).read_bytes())for n in ['router-gate.bin','router-route.bin','router-callback.bin']]==[48,29,31]
    assert lab['ExCallbackRestore']==0xbf91 and lab['ExCallbackHi']==0xbfa1 and lab['ExCallbackBank']==0xbfa7 and lab['ExMetalRouteEntry']==0xbfad
    patches=[]
    for name,pc,data in [('gate',0xa707,(O/'router-gate.bin').read_bytes()),('callback+route',0xbf91,(O/'router-callback.bin').read_bytes()+(O/'router-route.bin').read_bytes())]:
        at=start+pc-0xa000;patches.append(dict(role=name,offset=at,old=raw[at:at+len(data)].hex(),new=data.hex()))
    for name,pcs in reads.items():
        pc=pcs[0];at=start+pc-0xa000;old=raw[at:at+3];target=lab['ExCallback'+name]
        patches.append(dict(role='relocated_callback_'+name,offset=at,old=old.hex(),new=bytes([0xb9,target&255,target>>8]).hex()))
    at=start+0x1f7e;patches.append(dict(role='sole_native_Kr_branch',offset=at,old='d030',new='d02d'))
    q=dict(passed=True,proposal_only=True,ROM_written=False,base_ROM_SHA256=PIN,
           bank=79,gate_bytes=48,route_bytes=29,callback_restore_old_bytes=19,callback_restore_new_bytes=16,
           relocated_private_tables=dict(Hi=[0xbfa4,0xbfa1],Bank=[0xbfaa,0xbfa7]),
           sole_NativeKr_branch=0xbf7e,old_route_entry=0xbfb0,new_route_entry=0xbfad,
           table_readers=reads,patches=patches,extra_source_bytes_granted=0,
           native=False,installed=False,scope='Concrete current exact-preimage source-funded callback compaction and three-owner selector. CPU/IRQ/NMI/foreign routing proof required before candidate mutation.',
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),R/'tools/reference/metal_storm_union_funding_1101_v12.inc',R/'tools/reference/excitebike_shared_router_1101_v1.s',O/'router-gate.bin',O/'router-route.bin',O/'router-callback.bin',O/'router.lbl',BASE]})
    save('router-assembly.json',q);print(json.dumps(q))

if __name__=='__main__':main()
