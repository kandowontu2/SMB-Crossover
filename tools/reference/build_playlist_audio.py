"""Losslessly compress frame-quantized native APU playlists into the existing ROM.

Macros expand command tokens, never register values. Every encoded stream is
decoded again and compared before assets are written. Loop points require two
complete matching periods in the captured register trace.
"""
from pathlib import Path
from collections import Counter
import csv,hashlib,json,zlib
from collections import defaultdict,deque
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/reference-playlist'
ROLES=['pit','rygar','luigi','bass','ryu','sophia']
AREAS=['LT_NORMAL','LT_WATER','LT_UNDER_GROUND','LT_CASTLE','LT_COIN_HEAVEN','LT_INTRO','STAR']
EVENTS=['DIE','GAME_OVER','WIN','WIN_CASTLE','GAME_OVER','WIN','HURRY']

def frames(path,n):
    result=[{} for _ in range(n)];last={}
    for row in csv.DictReader(path.open()):
        f,a,v=map(int,row.values())
        if a>15 and a!=21:continue
        if f>=n:continue
        if a==21:v&=15
        if a in (3,7,11,15,21) or last.get(a)!=v:result[f][a]=v
        last[a]=v
    return [tuple(sorted(f.items())) for f in result]

def cycle(fs):
    n=len(fs);span=1024
    if n<2400:return None
    tail=fs[-span:]
    if sum(len(f) for f in tail)<64:return None
    for period in range(120,min(6500,(n-1)//2)):
        if tail!=fs[n-span-period:n-period]:continue
        start=n-span-period
        while start>0 and fs[start-1]==fs[start-1+period]:start-=1
        if n-start<2*period:continue
        if all(fs[i]==fs[start+(i-start)%period] for i in range(start,n)):
            return start,period
    return None

def tokens(fs):
    result=[];i=0
    while i<len(fs):
        if fs[i]:
            result.extend(bytes((a,v)) for a,v in fs[i]);result.append(b'\xfe');i+=1
        else:
            count=1
            while count<255 and i+count<len(fs) and not fs[i+count]:count+=1
            result.append(bytes((0x1d,count)));i+=count
    return result

def compress(streams):
    macros={};encoded={k:list(v) for k,v in streams.items()}
    for code in range(0x20,0xfe):
        counts=Counter()
        for stream in encoded.values():counts.update(zip(stream,stream[1:]))
        if not counts:break
        pair,count=max(counts.items(),key=lambda p:p[1]*(len(p[0][0])+len(p[0][1])-1))
        if count<3:break
        symbol=bytes((code,));macros[code]=pair
        for key,stream in encoded.items():
            dst=[];i=0
            while i<len(stream):
                if i+1<len(stream) and (stream[i],stream[i+1])==pair:dst.append(symbol);i+=2
                else:dst.append(stream[i]);i+=1
            encoded[key]=dst
    def expand(token):
        if len(token)==1 and token[0] in macros:return b''.join(expand(t) for t in macros[token[0]])
        return token
    for key,stream in encoded.items():assert b''.join(map(expand,stream))==b''.join(streams[key]),key
    def depth(token):return 1+max(map(depth,macros[token[0]])) if len(token)==1 and token[0] in macros else 0
    maximum=max(depth(t) for stream in encoded.values() for t in stream)
    assert maximum<=32,maximum
    return {k:b''.join(v) for k,v in encoded.items()},macros,maximum

def lz(data):
    """LZSS, 2KiB history, 3..34-byte matches; flags precede eight tokens."""
    positions=defaultdict(deque);result=bytearray();i=0
    while i<len(data):
        flag_at=len(result);result.append(0);flags=0
        for bit in range(8):
            if i>=len(data):break
            key=data[i:i+3];candidates=positions[key]
            while candidates and i-candidates[0]>2048:candidates.popleft()
            length=0;distance=0
            for pos in reversed(candidates):
                n=0
                while n<34 and i+n<len(data) and data[pos+n]==data[i+n]:n+=1
                if n>length:length=n;distance=i-pos
                if length==34:break
            if length>=3:
                flags|=1<<bit;d=distance-1
                result.extend((d&255,((length-3)<<3)|(d>>8)))
            else:result.append(data[i]);length=1
            for pos in range(i,i+length):positions[data[pos:pos+3]].append(pos)
            i+=length
        result[flag_at]=flags
    decoded=bytearray();i=0
    while len(decoded)<len(data):
        flags=result[i];i+=1
        for bit in range(8):
            if len(decoded)>=len(data):break
            if flags&(1<<bit):
                a,b=result[i:i+2];i+=2;d=1+a+((b&7)<<8)
                for _ in range((b>>3)+3):decoded.append(decoded[-d])
            else:decoded.append(result[i]);i+=1
    assert decoded==data
    return bytes(result)

def main():
    playlist=json.loads((ROOT/'docs/reference/expanded-playlist.json').read_text())
    fs={};metadata={}
    for role,p in playlist.items():
        for spec in p['types'].values():
            key=spec.get('capture')
            if not key or key in fs:continue
            if spec.get('fallback'):continue
            meta=json.loads((OUT/(key+'.complete.json')).read_text())
            path=OUT/(key+'.csv');assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['capture_sha256']
            length=meta['frames'] if role=='rygar' else min(meta['frames'],5400) if meta['frames']>1200 else meta['frames']
            fs[key]=frames(path,length);metadata[key]={**meta,'encoded_frames':length}
    for role in ('pit',):
        key=role;path=ROOT/f'build/reference-audio/{role}.csv'
        fs[key]=frames(path,5400);metadata[key]={'frames':5400,'capture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'source':'pinned native game capture'}
    for name,n in [('death',180),('victory',600)]:
        path=ROOT/f'build/reference-audio/{name}.csv';fs[name]=frames(path,n);metadata[name]={'frames':n,'source':'SMB fallback for prototype/adapted guests'}
    fs['silent']=[((21,0),)]
    music={v['capture'] for p in playlist.values() for k,v in p['types'].items() if (k.startswith('LT_') or k in ('STAR','HURRY')) and 'capture' in v}|{'pit'}
    segments={};loops={}
    for key,trace in fs.items():
        found=cycle(trace) if key in music else None
        if found:
            start,period=found;segments[key+':intro']=tokens(trace[:start]);segments[key+':loop']=tokens(trace[start:start+period]);loops[key]=key+':loop'
            metadata[key]['verified_loop']={'start_frame':start,'period':period,'matching_full_periods':(len(trace)-start)//period}
        else:
            segments[key+':intro']=tokens(trace);loops[key]=key+':intro'
            if key in music:metadata[key]['verified_loop']=None
    key=hashlib.sha256(b''.join(k.encode()+b''.join(v) for k,v in segments.items())).hexdigest()
    cache_path=OUT/'encoding-cache.json'
    cache=json.loads(cache_path.read_text()) if cache_path.exists() else {}
    if cache.get('input_sha256')==key:
        compressed={k:bytes.fromhex(v) for k,v in cache['streams'].items()}
        macros={int(k):tuple(bytes.fromhex(t) for t in v) for k,v in cache['macros'].items()}
        depth=cache['depth']
    else:
        compressed,macros,depth=compress(segments)
        cache_path.write_text(json.dumps({'input_sha256':key,'streams':{k:v.hex() for k,v in compressed.items()},'macros':{k:[t.hex() for t in v] for k,v in macros.items()},'depth':depth}))
    data=bytearray();addresses={};loop_addresses={}
    def address():return (0x27+len(data)//8192,0xa000+len(data)%8192)
    for key in fs:
        addresses[key]=address()
        if loops[key]!=key+':intro':
            data+=lz(compressed[key+':intro']+bytes((28,)))
            loop_addresses[key]=address();data+=lz(compressed[loops[key]]+bytes((255,)))
        else:
            data+=lz(compressed[key+':intro']+bytes((255,)));loop_addresses[key]=addresses[key]
    (OUT/'capacity-analysis.json').write_text(json.dumps({'macros_bytes':len(data),'loop_metadata':metadata,'zlib_sizes':{w:len(zlib.compress(data,wbits=w)) for w in (10,11,12,15)}},indent=2))
    assert len(data)<=20*8192,('compressed playlist exceeds capacity reserved before inventory/weapons banks',len(data))
    role_tables=[];event_tables=[];loop_tables=[];event_loops=[]
    for role in ROLES:
        if role in playlist:
            def get(kind):return playlist[role]['types'][kind].get('capture','silent')
            keys=[get(k) for k in AREAS];ev=[get(k) for k in EVENTS]
        elif role in ('pit','rygar'):
            keys=[role]*7;ev=['death','death','victory','victory','death','victory',role]
        else:keys=['silent']*7;ev=['silent']*7
        role_tables.extend(addresses[k] for k in keys);loop_tables.extend(loop_addresses[k] for k in keys)
        event_tables.extend(addresses[k] for k in ev)
        event_loops.extend(loop_addresses[k] for k in ev)
    lines=['; Generated source playlist streams; lossless command macros.','.pushseg']
    folder=ROOT/'audio/expanded';folder.mkdir(exist_ok=True)
    for i in range(23):
        chunk=data[i*8192:(i+1)*8192]
        if not chunk:break
        (folder/f'playlist-{i:02x}.bin').write_bytes(chunk)
        lines.extend([f'.segment "XG_MUSIC_{0x27+i:02X}"',f'.incbin "audio/expanded/playlist-{i:02x}.bin"'])
    lines.append('.segment "XG_AUDIO"')
    for prefix,table in [('XgArea',role_tables),('XgLoop',loop_tables),('XgEvent',event_tables),('XgEventLoop',event_loops)]:
        for suffix,fn in [('Banks',lambda b,a:b),('Lo',lambda b,a:a&255),('Hi',lambda b,a:a>>8)]:
            values=[f'${fn(b,a):02x}' for b,a in table]
            if prefix in ('XgArea','XgLoop'):
                label='ScroogeMusicIntro' if prefix=='XgArea' else 'ScroogeMusicLoop'
                values += [dict(Banks=f'.bank({label})',Lo=f'<{label}',Hi=f'>{label}')[suffix]]*7
            else:
                values += values[:7] # Shared Mario event adaptation for Scrooge.
            lines.extend([prefix+suffix+':',' .byte '+','.join(values)])
    lines.extend(['XgMacroLo:',' .byte '+','.join('<XgMacro'+str(c) for c in macros),'XgMacroHi:',' .byte '+','.join('>XgMacro'+str(c) for c in macros)])
    for code,pair in macros.items():lines.extend(['XgMacro'+str(code)+':',' .byte '+','.join(str(b) for t in pair for b in t)+',31'])
    lines.append('.popseg')
    generated='\n'.join(lines)+'\n'
    generated='.include "full_roster_music.inc"\n'+generated
    for prefix in ('XgArea','XgLoop','XgEvent','XgEventLoop'):
        for suffix in ('Banks','Lo','Hi'):
            label=prefix+suffix
            start=generated.index(label+':')
            end=generated.index('\n',generated.index('\n',start)+1)
            generated=generated[:end]+'\n.if ::ENABLE_MMC5_EXPANDED\n Full'+label+'\n.endif'+generated[end:]
    (ROOT/'src/expanded_music.inc').write_text(generated)
    (ROOT/'docs/reference/expanded-playlist-encoding.json').write_text(json.dumps({'compressed_bytes':len(data),'macros':len(macros),'maximum_macro_stack':depth,'decode_equals_reference_tokens':True,'streams':metadata,'limitations':['Frame-quantized APU writes, DPCM omitted','Pit has one stage theme; Pit/Rygar retain fallback death/victory music','Unverified loop points explicitly retained in the stream records']},indent=2)+'\n')
    print('Playlist:',len(fs),'streams,',len(data),'bytes,',len(macros),'macros, stack',depth,flush=True)
    print('Verified music loops',sum('verified_loop' in m and m['verified_loop'] is not None for m in metadata.values()),'/',len(music),flush=True)
if __name__=='__main__':main()
