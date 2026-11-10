"""Source-only Prince native foot-motion diagnostic; stdout and RAM only."""
import json
from pathlib import Path
import re
import sys

from py65.assembler import Assembler

import check_prince_fourth_route_1110 as F

C,N,I=F.C,F.N,F.I
SOURCE=C.R/'tools/reference/prince_native_foot_motion_1110.s'
ORIGIN=0xd4d7
PREVIOUS_SOLE=0xd4b1


def code(bundle):
    assembler=Assembler(N.NesMPU(memory=[0]*65536));labels={}
    for name in ('Player_Y_Speed','Player_Y_Position','Player_Y_HighPos','Player_X_Position','Player_PageLoc'):
        labels[name]=I.address(bundle,name)
    lines=[s.split(';',1)[0].strip() for s in SOURCE.read_text().splitlines()]
    labels.update({s[:-1]:ORIGIN for s in lines if s.endswith(':')})
    for _ in range(2):
        out=bytearray()
        for line in lines:
            if not line or line.startswith('.'):continue
            if line.endswith(':'):labels[line[:-1]]=ORIGIN+len(out);continue
            line=re.sub(r'\b([A-Za-z_][A-Za-z_0-9]*)\b',
                lambda m:f'${labels[m[1]]:04x}' if m[1] in labels else m[0],line)
            line=re.sub(r'#(\d+)\b',lambda m:f'#${int(m[1]):02x}',line)
            if line.split()[0].lower() in ('bcc','bcs','bne','beq') and not '$' in line:
                line=line.split()[0]+f' ${ORIGIN:04x}'
            out.extend(assembler.assemble(line,pc=ORIGIN+len(out)))
    assert len(out)<128,len(out)
    return bytes(out)


def apply(model):
    worker=code(model.bundle)
    assert bytes(model.ram[3][0x1d3e:0x1d42])==bytes.fromhex('a0063860')
    assert bytes(model.ram[2][ORIGIN-0xc000:ORIGIN-0xc000+len(worker)])==bytes([255])*len(worker)
    assert bytes(model.ram[2][PREVIOUS_SOLE-0xc001:PREVIOUS_SOLE-0xc000])==bytes([0xc9])
    model.ram[2][ORIGIN-0xc000:ORIGIN-0xc000+len(worker)]=worker
    model.ram[3][0x1d3e:0x1d42]=bytes([0x4c])+ORIGIN.to_bytes(2,'little')+bytes([0xea])
    return model


def matrix(seed):
    cases=[
        ('floor-static',900,213,8,'floor',176),
        ('floor-subphase',900,211,6,'floor',176),
        ('floor-exact',900,208,3,'floor',176),
        ('typed-cap-one-pixel',723,145,3,'pipe',112),
        ('logical-anchor-inside-floor',900,213,5,'floor',181),
        ('deep-descending',900,223,5,'floor',191),
        ('rising-airborne',900,207,3,'floor',175),
        ('covered-floor',900,213,8,'covered',181),
        ('embedded-pipe',914,213,8,'pipe',181),
        ('beside-pipe',900,213,8,'pipe',176),
        ('first-gap',1105,213,8,'gap',181),
        ('one-foot-gap-lip',1099,213,8,'gap',176),
        ('page-carry',1023,213,8,'floor',176),
    ]
    rows=[]
    for name,x,foot,delta,terrain,expected in cases:
        def tile(u,y):
            u%=512
            if terrain=='covered' and y>=192:return 0x54
            if terrain=='pipe':
                if 224<=u<256 and y>=144:return 0x12 if y==144 else 0x14
                if 400<=u<432 and y>=144:return 0x10 if y==144 else 0x14
            if terrain=='gap' and 80<=u<112:return 0
            return 0x54 if y>=208 else 0
        m=N.fork(seed);C.Seam.terrain(m,tile)
        m.raw_page(2,2);N.put(m,CurrentBankC=2)
        N.put(m,Player_X_Position=x&255,Player_PageLoc=x>>8,
            Player_Y_Position=foot-32,Player_Y_HighPos=1)
        m.ram[2][0x84:0x86]=foot.to_bytes(2,'little');m.ram[2][0x88]=delta
        m.ram[2][0x611]=(foot-delta-77)&255
        source=bytes(m.ram[2][:0x800]);scratch=bytes(m[3:11])
        regs=I.invoke(m,3,0xbd3e,(83,71,109,0x71))['regs']
        y=N.get(m,'Player_Y_Position')
        assert y==expected,(name,y,expected)
        assert regs==[83,71,6,0x71,224],(name,regs)
        assert bytes(m.ram[2][:0x800])==source and bytes(m[3:11])==scratch,name
        assert N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')==x
        rows.append(dict(name=name,x=x,physical_sole=foot,delta=delta,native_Y=y,regs=regs))
    return rows


def overlap_funding(meta):
    """Share exact packet bytes; flags/decoded records stay frame-identical."""
    end=0xd46e-0xc800;grid=meta[:end]
    tags=[int.from_bytes(grid[i:i+2],'little') for i in range(0,478,2)]
    order=sorted(set(tags)-{65535},key=lambda t:t&0x3fff)
    packets={t:grid[t&0x3fff:at] for t,at in zip(order,[t&0x3fff for t in order[1:]]+[end])}
    kept=[t for i,t in enumerate(order) if not any(
        packets[t] in packets[q] and (len(packets[q])>len(packets[t]) or j<i)
        for j,q in enumerate(order) if q!=t)]
    edges=[]
    for a in kept:
        for b in kept:
            if a==b:continue
            x,y=packets[a],packets[b]
            k=max((k for k in range(1,min(len(x),len(y))) if x[-k:]==y[:k]),default=0)
            if k:edges.append((k,a,b))
    candidates=[];best=None
    for tie in ('forward','backward','length'):
        nxt={};previous={};links={}
        key=lambda e:(-e[0],e[1],e[2]) if tie=='forward' else (-e[0],-e[1],-e[2]) if tie=='backward' else (-e[0],-len(packets[e[1]]),e[2])
        for k,a,b in sorted(edges,key=key):
            if a in nxt or b in previous:continue
            tail=b
            while tail in nxt:tail=nxt[tail]
            if tail==a:continue
            nxt[a]=b;previous[b]=a;links[a]=k
        heads=[t for t in kept if t not in previous]
        for arrange in ('forward','bytes','length'):
            seq=sorted(heads,key=lambda t:t if arrange=='forward' else packets[t] if arrange=='bytes' else -len(packets[t]))
            body=bytearray()
            for h in seq:
                body.extend(packets[h]);at=h
                while at in nxt:
                    following=nxt[at];body.extend(packets[following][links[at]:]);at=following
            offsets={t:478+body.find(packets[t]) for t in order}
            assert all(at>=478 for at in offsets.values())
            packed=bytearray(bytes([255])*478)+body
            for frame,t in enumerate(tags):
                if t!=65535:packed[2*frame:2*frame+2]=((t&0xc000)|offsets[t]).to_bytes(2,'little')
            assert len(packed)<=end
            used=len(packed);packed.extend(bytes([255])*(end-used))
            assert all(C.Camera.Funded.Pack.geometry(grid,f)==C.Camera.Funded.Pack.geometry(packed,f) for f in range(239))
            candidate=bytes(packed)+meta[end:];size=len(C.P.Q.M.CODEC.encode(candidate))
            row=dict(tie=tie,chains=arrange,used=used,reclaimed=end-used,packed_bytes=size,
                     packets_before=len(order),packets_not_contained=len(kept),overlap_links=len(nxt),geometry_exact=239)
            candidates.append(row);print('OVERLAP_TRIAL '+json.dumps(row),flush=True)
            if best is None or size<best[0]:best=(size,candidate,row)
    return best[1],dict(best=best[2],candidates=candidates)


def fit(seed):
    original,_,_=C.P.Q.source_images()
    def chunks(m):
        rt=bytearray(m.ram[3][:len(original)])
        rt[0x1fa3:0x1fd8]=original[0x1fa3:0x1fd8]
        return bytes(rt),bytes(m.ram[2][0x800:0x1fcc])
    old=chunks(seed);new=chunks(apply(N.fork(seed)))
    encode=C.P.Q.M.CODEC.encode
    sizes=[list(map(lambda b:len(encode(b)),pair)) for pair in (old,new)]
    result=dict(worker_bytes=len(code(seed.bundle)),old_packed=sizes[0],new_packed=sizes[1],
        growth=sum(sizes[1])-sum(sizes[0]),allocation=[ORIGIN,ORIGIN+len(code(seed.bundle))])
    if '--overlap-funding' in sys.argv:
        funded,report=overlap_funding(new[1]);result['overlap']=report
        result['funded_packed']=[sizes[1][0],len(encode(funded))]
        result['funded_growth']=sum(result['funded_packed'])-sum(sizes[0])
    if '--search-funding' in sys.argv:
        meta=new[1];grid=meta[:0xd46e-0xc800]
        tags=[int.from_bytes(grid[i:i+2],'little') for i in range(0,478,2)]
        order=sorted(set(tags)-{65535},key=lambda t:t&0x3fff)
        packets={t:grid[t&0x3fff:end] for t,end in zip(order,[t&0x3fff for t in order[1:]]+[len(grid)])}
        orders={'original':order,'reversed':order[::-1]}
        for n,key in (('bytes',lambda t:packets[t]),('reverse-bytes',lambda t:packets[t][::-1]),
                      ('length',lambda t:len(packets[t])),('body',lambda t:packets[t][4:]),
                      ('encoding',lambda t:(t>>14,packets[t])),
                      ('header-length',lambda t:(packets[t][:2],len(packets[t])))):
            orders[n]=sorted(order,key=key);orders[n+'-descending']=sorted(order,key=key,reverse=True)
        for off in range(1,len(order),max(1,len(order)//12)):
            orders['rotate-'+str(off)]=order[off:]+order[:off]
        rows=[]
        for label,seq in orders.items():
            packed=bytearray(bytes([255])*478);moved={}
            for t in seq:moved[t]=(t&0xc000)|len(packed);packed.extend(packets[t])
            for i,t in enumerate(tags):
                if t!=65535:packed[2*i:2*i+2]=moved[t].to_bytes(2,'little')
            assert len(packed)==len(grid)
            candidate=bytes(packed)+meta[len(grid):]
            size=len(encode(candidate))
            rows.append(dict(order=label,packed=size))
            if size<result.get('best_meta_packed',sizes[1][1]):
                result.update(best_meta_packed=size,best_order=label)
            print('FUNDING_TRIAL '+json.dumps(rows[-1]),flush=True)
        result['funding_search']=rows
    return result


def main():
    raw=F.Exit.ROM.read_bytes();assert C.digest(raw)==F.Exit.PIN
    bundle=C.Start.W.bundle(raw);cold,_=C.P.Q.C.C.cold(bundle,38)
    print('PACKED_FIT '+json.dumps(fit(cold)),flush=True)
    if '--search-funding' in sys.argv or '--overlap-funding' in sys.argv:return
    env,seed,labels=C.fixture(bundle)
    N.put(seed,CrossoverBehaviorVersion=0);N.consume(seed)
    F.REAL_NMI=True;_,seed=F.authored(seed)
    print('SEED '+json.dumps(dict(sample=F.sample(seed,0),source_actor_y=seed.ram[2][0x611],
        projection=dict(foot=int.from_bytes(seed.ram[2][0x84:0x86],'little'),
        oldfoot=int.from_bytes(seed.ram[2][0x86:0x88],'little'),delta=seed.ram[2][0x88],
        origin=int.from_bytes(seed.ram[2][0x89:0x8b],'little'),last_y=seed.ram[2][0x8b]),
        fullbox_hex=bytes(seed.ram[2][0x798:0x7b3]).hex())),flush=True)
    if '--compare' in sys.argv:
        after=apply(N.fork(seed));before=N.fork(seed)
        def state(m,t):
            row=F.sample(m,t)
            return {k:row[k] for k in ('x','y','foot','native_state','source_x','source_y','action','frame','mode','phase')}
        for tick in range(40):
            C.Route.controls(env,before,labels,1);N.consume(before)
            C.Route.controls(env,after,labels,1);N.consume(after)
            a,b=state(before,tick),state(after,tick)
            print('COMPARE '+json.dumps(dict(tick=tick,before=a,after=b,
                before_projection=bytes(before.ram[2][0x84:0x8c]).hex(),
                after_projection=bytes(after.ram[2][0x84:0x8c]).hex())),flush=True)
        return
    seed=apply(seed)
    print('DIRECT_MATRIX '+json.dumps(matrix(seed),separators=(',',':')),flush=True)
    if '--direct' in sys.argv:return
    for policy in ('roll-up','up','settle','roll-right-up'):
        result,_=F.trial(env,seed,labels,policy,bound=450)
        print('EXPERIMENT '+json.dumps(result,separators=(',',':')),flush=True)


if __name__=='__main__':main()
