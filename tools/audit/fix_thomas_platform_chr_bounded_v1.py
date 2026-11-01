"""Give native platform sprites their own unchanged miscellaneous CHR window."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
P=R/'build/thomas-native-render';O=R/'build/thomas-platform-chr';W=R/'build/thomas-natural-host-1031-v6'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')


def main():
    assert not(O/'source-stage.json').exists();O.mkdir(exist_ok=True)
    assert sha(P/'candidate.nes')=='2ad560f9f7a56c7beb8400d11b4d859606ae494b949fdacae1087ab953a7fbf7'
    raw=(P/'candidate.nes').read_bytes();prefix=1048592+426*1024
    carrier=bytearray(raw[prefix:prefix+16384]);before=bytes(carrier)
    meta=bytearray(carrier[6144:8192]);body=bytearray(carrier[8192:])
    misc=R/'chr/mmc5/sprites_misc.chr';native=misc.read_bytes();assert len(native)==1024
    assert body[5*1024:6*1024]==bytes(1024),'Use only the already granted zero page'
    body[5*1024:6*1024]=native
    def descriptor(data,index):
        start=(data[1026+index]|data[1068+index]<<8)-0xd000
        length=data[start];assert 0<length<=64 and length%4==0
        return start,length
    def pixels(data,art,index):
        start,length=descriptor(data,index);windows=data[1110+index*4:1114+index*4]
        result=[]
        for at in range(start+1,start+1+length,4):
            t=data[at];address_=(t&1)*4096+(t&254)*16
            page=windows[address_//1024];offset=address_%1024
            result.append((bytes(data[at+1:at+4]),bytes(art[page*1024+offset:page*1024+offset+32])))
        return result
    original_meta=bytes(meta);original_body=bytes(carrier[8192:]);pages_per_pose=[]
    for index in range(42):
        start,length=descriptor(meta,index);windows=list(original_meta[1110+index*4:1114+index*4]);mapping={}
        replacement=[0,5,0,0]
        for at in range(start+1,start+1+length,4):
            t=meta[at];address_=(t&1)*4096+(t&254)*16
            page=windows[address_//1024];offset=address_%1024
            if page not in mapping:
                assert len(mapping)<3,'At most three original art pages per pose'
                mapping[page]=[0,2,3][len(mapping)];replacement[mapping[page]]=page
            target=mapping[page]*1024+offset
            meta[at]=(target//16)&254
        meta[1110+index*4:1114+index*4]=bytes(replacement)
        pages_per_pose.append(len(mapping))
    for index in range(42):assert pixels(original_meta,original_body,index)==pixels(meta,body,index),index
    start,length=descriptor(meta,0)
    assert meta[start:start+length+1]==original_meta[start:start+length+1],'Cold standing record stays exact'
    for i in range(42):assert meta[1110+4*i+1]==5
    carrier[6144:8192]=meta;carrier[8192:]=body
    (O/'metadata.bin').write_bytes(meta[:1278])
    (O/'metadata.s').write_text((W/'source/metadata.s').read_text(),encoding='utf-8')
    (O/'resident.s').write_text((P/'resident.s').read_text(),encoding='utf-8')
    (O/'carrier.s').write_text((P/'carrier.s').read_text(),encoding='utf-8')
    (O/'carrier.chr').write_bytes(carrier)
    (O/'cookie.bin').write_bytes((P/'cookie.bin').read_bytes())
    (O/'native-background-colors.bin').write_bytes((P/'native-background-colors.bin').read_bytes())
    cc=R/'tools/Windows/cc65/bin'
    def run(name,cmd):
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R)
        for q in guard['outputs']:Path(q['path']).parent.mkdir(parents=True,exist_ok=True)
        result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(name+'.json'),dict(command=cmd,guard=guard,returncode=result.returncode,stderr=result.stderr));assert result.returncode==0,result.stderr
    def asm(name):run(name+'-build',[cc/'ca65.exe',O/(name+'.s'),'-I',O,'-I',P,'-I',W/'source','-g','-o',O/(name+'.o'),'--create-full-dep',O/(name+'.dep')])
    count=0;outputs={}
    def redirect(match):
        nonlocal count
        if match[1]in['','%O']:return match[0]
        count+=1;path=O/'sideoutputs'/(f'{count:03d}-'+Path(match[1]).name);outputs[Path(match[1]).name]=path
        return 'file="'+path.as_posix()+'"'
    (O/'candidate.cfg').write_text(re.sub(r'file\s*=\s*"([^"\r\n]*)"',redirect,(P/'candidate.cfg').read_text()))
    link=json.loads((P/'final-link.json').read_text())['command'][:]
    for name,parent in [('resident',P),('carrier',P),('metadata',W)]:
        asm(name);link[link.index(str(parent/(name+'.o')))]=str(O/(name+'.o'))
    for flag,name in [('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl')]:link[link.index(flag)+1]=str(O/name)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg')
    def linked(tag):
        run(tag+'-link',link);path=O/'candidate.dbg';data=path.read_bytes();keep={'version','info','file','lib','mod','seg','scope','sym'}
        path.write_bytes(b''.join(s for s in data.splitlines(keepends=True)if s.split(b'\t',1)[0].decode('ascii')in keep))
        save(O/(tag+'-debug-format.json'),dict(full_bytes=len(data),full_sha256=hashlib.sha256(data).hexdigest(),compact_bytes=path.stat().st_size,compact_sha256=sha(path)))
    linked('provisional')
    kernel=next(p for n,p in outputs.items()if n.endswith('kernel.bin')).read_bytes()
    state=next(p for n,p in outputs.items()if n.endswith('state.bin')).read_bytes()
    assert kernel[:6144]==before[:6144] and state[0x1000:0x1800]==meta
    (O/'cookie.bin').write_bytes(bytes([167,10,64,1])+hashlib.sha256(kernel+state).digest()[:12]);asm('resident');linked('final')
    final=(O/'candidate.nes').read_bytes()
    assert final[prefix:prefix+16384]==carrier
    changed=[i for i,(a,b)in enumerate(zip(raw[:1048592],final[:1048592]))if a!=b]
    cookie=scoped_load(O/'candidate.nes');at=__import__('check_tmnt_render_oa').location(cookie,'ThCookie')
    assert all(at+4<=i<at+16 for i in changed),'Only own cookie digest changes in native PRG'
    assert raw[1048592:prefix]==final[1048592:prefix] and raw[prefix+16384:]==final[prefix+16384:]
    refs={Path(__file__),misc,P/'source-stage.json',P/'final-link.json',P/'resident.s',P/'carrier.s',W/'source/metadata.s'}
    refs|={Path(p)for p in link if p.endswith('.o')};refs|={p for p in O.rglob('*')if p.is_file()}
    save(O/'source-stage.json',dict(passed=True,source=True,native=False,installed=False,candidate=sha(O/'candidate.nes'),parent=sha(P/'candidate.nes'),
        source_poses_pixel_exact=42,maximum_original_pages_per_pose=max(pages_per_pose),native_platform_CHR_source=str(misc),native_platform_CHR_sha256=sha(misc),
        private_body_page5_replaces_previous_zero=True,native_changed_offsets=changed,
        adaptation='Reserve sprite window1 for unchanged native miscellaneous art. Reindex original Thomas parts into windows0/2/3; all42 complete original pose pixel/attribute/position inputs remain identical. No physics/native platform instructions changed.',
        bindings={str(p.resolve()):sha(p)for p in refs}))
    print(json.dumps(dict(candidate=sha(O/'candidate.nes'),poses_pixel_exact=42,native_PRG_changes=len(changed))))


if __name__=='__main__':main()
