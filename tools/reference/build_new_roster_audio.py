"""Compile source-captured music for the expanded roster with verified loops.

The new frame mask codec avoids a command dispatch for every APU register.
LZSS still uses the established 2 KiB audio history; no additional RAM is used.
"""
from pathlib import Path
import csv
import gzip
import hashlib
import io
import json
import argparse
from build_playlist_audio import cycle, lz

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'reference/new-roster-audio'
ORDER=['kirby','chip','tmnt','mac','mike','mario3','vic','zelda2','cv3','darkwing','meta']
AREAS=['normal','water','underground','castle','bonus','intro','star']
EVENTS=['die','game_over','win','win_castle','game_over','win','hurry']


def frames(record):
    raw=gzip.decompress(Path(record['path']).read_bytes())
    assert hashlib.sha256(raw).hexdigest()==record['capture_sha256']
    result=[{} for _ in range(record['frames'])];last={};dpcm=0
    for row in csv.DictReader(io.StringIO(raw.decode())):
        frame,reg,value=map(int,row.values())
        if reg>15 and reg!=21:
            dpcm+=1
            continue
        if frame>=len(result):continue
        if reg==21:value&=15
        if reg in (3,7,11,15,21) or last.get(reg)!=value:
            result[frame][reg]=value
        last[reg]=value
    return [tuple(sorted(f.items())) for f in result],dpcm


def encode(fs):
    data=bytearray();i=0
    while i<len(fs):
        if not fs[i]:
            n=1
            while n<127 and i+n<len(fs) and not fs[i+n]:n+=1
            data.append(n);i+=n
            continue
        f=dict(fs[i]);mask=sum(1<<r for r in f if r<16)
        data.extend((0x81 if 21 in f else 0x80,mask&255,mask>>8))
        data.extend(f[r] for r in range(16) if r in f)
        if 21 in f:data.append(f[21])
        i+=1
    # Independent decoder: ensure frame boundaries and forced timer writes survive.
    decoded=[];i=0
    while i<len(data):
        tag=data[i];i+=1
        if tag<128:
            decoded.extend([()] * tag)
            continue
        assert tag in (128,129)
        mask=data[i]+256*data[i+1];i+=2;frame=[]
        for reg in range(16):
            if mask>>reg&1:frame.append((reg,data[i]));i+=1
        if tag&1:frame.append((21,data[i]));i+=1
        decoded.append(tuple(frame))
    assert decoded==fs
    return bytes(data)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--roles',nargs='+',choices=ORDER,default=['kirby','meta'])
    args=parser.parse_args()
    order=args.roles
    captures=json.loads((SOURCE/'captures-manifest.json').read_text())
    plan=json.loads((SOURCE/'playlist-plan.json').read_text())
    plan['meta']={**plan['kirby'],'tracks':{**plan['kirby']['tracks'],'normal':13,'hurry':13}}
    plan={role:plan[role] for role in order}
    music={f"{role if role!='meta' else 'kirby'}-{spec['tracks'][kind]:02d}"
           for role,spec in plan.items() for kind in AREAS+['hurry']}
    streams={};loops={};metadata={}
    needed={f"{role if role!='meta' else 'kirby'}-{track:02d}"
            for role,spec in plan.items() for track in spec['tracks'].values()}
    for key,record in captures.items():
        if key not in needed:continue
        fs,dpcm=frames(record)
        found=cycle(fs) if key in music else None
        if found:
            start,period=found
            streams[key+'-intro']=lz(encode(fs[:start])+b'\xfe')
            streams[key+'-loop']=lz(encode(fs[start:start+period])+b'\xff')
            loops[key]=key+'-loop'
        else:
            streams[key+'-intro']=lz(encode(fs)+b'\xff')
            loops[key]=key+'-intro'
        metadata[key]=dict(capture_sha256=record['capture_sha256'],frames=record['frames'],
                           loop=None if not found else dict(start=found[0],period=found[1]),
                           dpcm_writes_not_encoded=dpcm)
        print(key,sum(map(len,streams.values())),flush=True)
    # Streams may cross banks: the existing raw-byte reader advances at $C000.
    data=bytearray();locations={};dedup={}
    for key,stream in streams.items():
        if stream not in dedup:
            dedup[stream]=len(data);data.extend(stream)
        locations[key]=dedup[stream]
    report=dict(bytes=len(data),banks=(len(data)+8191)//8192,streams=metadata,roles=order,
                codec='frame-mask-lzss-2k',host_roundtrip_verified=True)
    out=SOURCE/'encoding-report.json'
    out.write_text(json.dumps(report,indent=2)+'\n')
    print('TOTAL',report['bytes'],report['banks'],flush=True)
    if len(data)>26*8192:
        raise SystemExit('Prepared soundtrack exceeds reserved banks; no assets installed')
    folder=ROOT/'audio/full-roster';folder.mkdir(exist_ok=True)
    lines=['; Generated original-game frame masks; existing families stay unchanged.',
           '.if ::ENABLE_MMC5_EXPANDED','.pushseg']
    for bank in range(report['banks']):
        name=f'full-{bank:02x}.bin';(folder/name).write_bytes(data[bank*8192:(bank+1)*8192])
        lines += [f'.segment "X5_FULL_MUSIC_{bank:02X}"',f'X5MusicBank{bank:02X}:',
                  f'.incbin "audio/full-roster/{name}"']
    lines+=['.popseg']
    for prefix,kinds,loop in [('XgArea',AREAS,False),('XgLoop',AREAS,True),
                              ('XgEvent',EVENTS,False),('XgEventLoop',EVENTS,True)]:
        keys=[]
        for role in order:
            for kind in kinds:
                key=f"{role if role!='meta' else 'kirby'}-{plan[role]['tracks'][kind]:02d}"
                keys.append(loops[key] if loop else key+'-intro')
        for suffix in ('Banks','Lo','Hi'):
            values=[]
            for key in keys:
                pos=locations[key];label=f'X5MusicBank{pos//8192:02X}'
                values.append(f'.bank({label})' if suffix=='Banks' else
                              f'{"<" if suffix=="Lo" else ">"}({label}+${pos%8192:04x})')
            lines += [f'.macro Full{prefix}{suffix}', ' .byte '+','.join(values),'.endmacro']
    lines+=['.endif']
    (ROOT/'src/full_roster_music.inc').write_text('\n'.join(lines)+'\n')
    cfg=ROOT/'smb1base-mmc5-expanded.cfg';text=cfg.read_text()
    marker='SEGMENTS {\n'
    for bank in range(report['banks']):
        line=f'    X5_FULL_MUSIC_{bank:02X}:load=X5_NEW_{100+bank:02X},type=ro;\n'
        if line not in text:text=text.replace(marker,marker+line,1)
    cfg.write_text(text)


if __name__=='__main__':main()
