"""Fit donor injury/death in existing Shinobi code/metadata/art allocations."""
import hashlib,json,re,subprocess
from pathlib import Path
import prepare_shinobi_owning_graft_1101_v1 as P
import recover_shinobi_component_1101_v2 as S

R=P.R; OLD=P.O; O=R/'build/shinobi-hurt-layout-1101-v5'
ART=R/'build/shinobi-hurt-art-1101-v4'


def main():
    O.mkdir(parents=True,exist_ok=True)
    assert P.sha(S.ROM)==S.EXPECTED
    m=S.original_memory(S.ROM.read_bytes())
    extra=json.loads((ART/'packets.json').read_text())
    meta=(OLD/'native-metadata.inc').read_text()
    meta=meta.replace('.segment "SHINOBI_META"','.segment "SHINOBI_META"\nShMetaStart:')
    # Tile attributes are immutable lookup data. Move them into the unused
    # kernel tail, freeing metadata space without changing a single entry.
    attrs=re.search(r'^ShNativeTileAttributes:.*$',meta,re.M)[0]
    meta=meta.replace(attrs+'\n','')
    headers={pose:m.WordAt(0xe620+pose*2) for pose in [6,7]}
    for pose,h in headers.items():
        n=m.memory[h]; timer=m.WordAt(h+2)
        text=f'ShHeader_{h:04X}: .byte {n},{m.memory[h+1]}\n.word '+(f'ShTimer_{timer:04X}' if timer else '0')+'\n'
        if timer:
            assert f'ShTimer_{timer:04X}:' not in meta
            text+=f'ShTimer_{timer:04X}: .byte '+','.join(map(str,m.memory[timer:timer+n]))+'\n'
        meta=meta.replace('ShPosePointers:',text+'ShPosePointers:')
    prefix,tail=meta.split('ShPosePointers:\n')
    ptrs,tail=tail.split('ShOriginalHeaderLo:',1)
    ptrs=ptrs.splitlines()
    assert len(ptrs)==96
    for pose,h in headers.items():ptrs[pose]=f'.word ShHeader_{h:04X}'
    meta=prefix+'ShPosePointers:\n'+'\n'.join(ptrs)+'\nShOriginalHeaderLo:'+tail
    def modify_table(name,fn):
        nonlocal meta
        match=re.search(r'^'+name+r':\s*\.byte ([0-9,]+)$',meta,re.M)
        vals=list(map(int,match[1].split(',')));fn(vals)
        meta=meta[:match.start()]+name+': .byte '+','.join(map(str,vals))+meta[match.end():]
    modify_table('ShOriginalHeaderLo',lambda a:[a.__setitem__(p,h&255) for p,h in headers.items()])
    modify_table('ShNativePoseOrdinal',lambda a:[a.__setitem__(p,21+i) for i,p in enumerate([6,7])])
    counts=[m.memory[headers[p]] for p in [6,7]]
    modify_table('ShNativeFrameBase',lambda a:a.extend([26,26+counts[0]]))
    # Original body boxes: recover IDs from the donor lookup, never invent one.
    match=re.search(r'ShOriginalBoxData:\.byte ([0-9,]+)',meta)
    data=list(map(int,match[1].split(',')));boxes=[data[i:i+6] for i in range(0,len(data),6)]
    ids=[]
    for pose in [6,7]:
        m.memory[0x300]=pose;m.memory[0x30b]=0;m.x=0;m.pc=0xd93d;m.sp=239;m.stPushWord(0x5ffd)
        for _ in range(1000):
            if m.pc==0x5ffe:break
            m.step()
        else:raise AssertionError('bbox timeout')
        if m.memory[0x12]!=1:ids.append(255)
        else:
            at=m.WordAt(0x10);row=list(m.memory[at:at+6])
            if row not in boxes:boxes.append(row)
            ids.append(boxes.index(row))
    modify_table('ShOriginalBoxId',lambda a:a.extend(ids))
    modify_table('ShOriginalBoxOffsets',lambda a:a.extend(range(len(a)*6,len(boxes)*6,6)))
    modify_table('ShOriginalBoxData',lambda a:a.extend([v for row in boxes for v in row][len(a):]))
    pointers=[];descriptors=[]
    for packet in extra:
        if packet['facing']:continue
        name=f'ShHurtP{packet["pose"]}_{packet["frame"]}'
        pointers.append('.word '+name+',0')
        rows=packet['native_rows'];assert len(rows)<32
        desc=[len(rows)*4]
        for x,y,t,a in reversed(rows):
            pair=t//2
            if pair>=96:pair=117+(pair-96)
            assert pair<128
            desc.extend([pair*2+1,a,(y-224)&255,(x-128)&255])
        descriptors.append(name+': .byte '+','.join(map(str,desc)))
    marker='ShNativeP00_0_0_0:'
    meta=meta.replace(marker,'\n'.join(pointers+descriptors)+'\n'+marker,1)
    meta=meta.replace('ShMetadataEnd:','ShMetadataPayloadEnd:\n.assert *-ShMetaStart <= $6a0, error, "metadata overlaps hurt art"\n.res $6a0-(*-ShMetaStart),0\nShHurtArt:\n.incbin "additional-art.chr"\nShMetadataEnd:')
    (O/'native-metadata.inc').write_text(meta)
    (O/'additional-art.chr').write_bytes((ART/'additional-art.chr').read_bytes())
    (O/'source-kernel.inc').write_bytes((OLD/'source-kernel.inc').read_bytes())
    entry=(OLD/'component.s').read_text().replace('ShKernelEnd:',
        '.include "shinobi_injury_1101_v3.inc"\n'+attrs+'\nShKernelEnd:')
    (O/'component.s').write_text(entry)
    cfg='MEMORY { K:start=$a000,size=$2000,file="'+(O/'kernel.bin').as_posix()+'",fill=yes; M:start=$d000,size=$1000,file="'+(O/'metadata.bin').as_posix()+'",fill=yes; } SEGMENTS { SHINOBI_KERNEL:load=K,type=ro; SHINOBI_META:load=M,type=ro; }'
    (O/'component.cfg').write_text(cfg)
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe','-g','-I',O,'-I',R/'tools/reference',O/'component.s','-o',O/'component.o'],[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o','-o',O/'unused.bin','-Ln',O/'component.lbl','--dbgfile',O/'component.dbg']]:
        subprocess.run(list(map(str,cmd)),check=True)
    lab=P.labels(O/'component.lbl')
    assert lab['ShKernelEnd']<=0xbc00 and lab['ShMetadataEnd']==0xd800
    assert (O/'metadata.bin').read_bytes()[0x6a0:0x800]==(ART/'additional-art.chr').read_bytes()
    # Fourth visible sprite page is physical517, shared with metadata. Only
    # its tail (pairs117..127) is addressed by the new descriptors.
    (O/'native-art.chr').write_bytes((OLD/'native-art.chr').read_bytes()+(O/'metadata.bin').read_bytes()[1024:2048])
    poses=json.loads((P.V/'pose-packets.json').read_text())['poses']
    poses += [dict(pose=p['pose'],frame=p['frame'],facing=p['facing'],OAM=p['source_OAM']) for p in extra]
    (O/'pose-packets.json').write_text(json.dumps(dict(poses=poses)))
    (O/'source-body.chr').write_bytes((P.V/'source-body.chr').read_bytes())
    q=dict(assembled=True,installed=False,kernel_bytes=lab['ShKernelEnd']-0xa000,
           metadata_payload_bytes=lab['ShMetadataPayloadEnd']-0xd000,metadata_with_art_bytes=2048,
           sprite_pages=[503,504,505,517],new_pair_indices=[117,128],injury_entry=lab['Sh_DA1B'],
           bindings={str(p.resolve()):P.sha(p) for p in [O/'component.s',O/'native-metadata.inc',O/'kernel.bin',O/'metadata.bin',O/'native-art.chr']})
    P.save(O/'assembly.json',q)
    import check_shinobi_native_render_1101_v1 as N
    N.O=O;P.V=O
    N.main()
    P.save(O/'layout.json',q)
    payload=(O/'kernel.bin').read_bytes()[:7168]+(O/'metadata.bin').read_bytes()[:2048]+(O/'native-art.chr').read_bytes()
    (O/'shinobi-cookie.bin').write_bytes(bytes([0xa7,36,1])+hashlib.sha256(payload).digest()[:13])
    (O/'resident.s').write_bytes((OLD/'resident.s').read_bytes())
    import prepare_shinobi_cartridge_1101_v2 as Cartridge
    Cartridge.O=O;Cartridge.S.O=O
    Cartridge.main()
    import check_shinobi_cartridge_1101_v2 as Loader
    Loader.main()
    print(json.dumps({k:v for k,v in q.items() if k!='bindings'}))


if __name__=='__main__':main()
