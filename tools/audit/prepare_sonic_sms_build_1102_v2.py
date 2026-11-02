"""Fetch only the pinned original-ROM extractor and two assembler tools."""
import hashlib,io,json,urllib.request,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
REV='91e9dd6f77393cd820efd5785229141b525f56b2'
O=R/'build/sonic-sms-original-1102-v2'

def get(url,limit):
    with urllib.request.urlopen(url,timeout=30) as response:data=response.read(limit+1)
    assert len(data)<=limit
    return data

def main():
    O.mkdir(exist_ok=True);rows=[]
    names=['tools/rom_unpack.py','tools/dislib/__init__.py','tools/dislib/annotator.py','tools/dislib/miscdefs.py','tools/dislib/rom.py','tools/dislib/saver.py','tools/dislib/tracer.py','tools/dislib/z80ops.py','src/whole.lnk']
    for name in names:
        url=f'https://raw.githubusercontent.com/iamgreaser/s1smsdisasm-gm/{REV}/{name}'
        data=get(url,100000);p=O/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        rows.append(dict(path=name,url=url,SHA256=sha(p)))
    ref=R/'docs/qa/checkpoints/2026-11-02/sonic-sms-reference-v1/reference.zip'
    with zipfile.ZipFile(ref) as z:
        p=O/'annot/sonic1.cfg';p.parent.mkdir(exist_ok=True);p.write_bytes(z.read('annot/sonic1.cfg'))
    url='https://github.com/vhelin/wla-dx/releases/download/v10.7/wla_dx_v10.7_Win64.zip'
    archive=get(url,4000000);selected=[]
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        for name in z.namelist():
            if Path(name).name.lower() in ['wla-z80.exe','wlalink.exe']:
                data=z.read(name);assert len(data)<4000000
                p=O/'bin'/Path(name).name;p.parent.mkdir(exist_ok=True);p.write_bytes(data)
                selected.append(dict(path=p.relative_to(O).as_posix(),SHA256=sha(p)))
    assert len(selected)==2
    q=dict(prepared=True,source_revision=REV,extractor=rows,tools=selected,tool_archive_URL=url,tool_archive_SHA256=hashlib.sha256(archive).hexdigest(),scope='Downloaded only. Extractor code review and original-ROM reproduction remain pending. No NES port or gameplay claim.')
    (O/'prepared.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(prepared=True,files=len(rows)+len(selected)+2)))

if __name__=='__main__':main()
