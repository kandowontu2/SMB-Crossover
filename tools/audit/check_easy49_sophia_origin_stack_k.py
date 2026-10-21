"""Exact negative-query stack/write oracle, without stack or RAM masks."""
from pathlib import Path
import hashlib,importlib.util,json,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';D=V/'root49-sophia-head-axis-d'
G=V/'ryu49-head-status-bridge-g';sys.path.insert(0,str(G))
sp=importlib.util.spec_from_file_location('origin_stack_bus',G/'check.py')
g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g);CPU=g.loadcpu().NesMPU
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out=D/'origin-stack-k.json';assert not out.exists();proofs=[]
    for mapper in ['mmc3','mmc5']:
        im=g.Image(D/f'source/build/smb-crossover-{mapper}.nes');L=im.ram
        wrapper=im.hook('SophiaTerrainBoundedQuery');body=im.hook('SophiaTerrainQuery')
        raw=im.raw[wrapper['rom_offset']:wrapper['rom_offset']+im.sym('SophiaTerrainBoundedQuery')['size']]
        jsr=bytes([0x20,body['address']&255,body['address']>>8]);assert raw.count(jsr)==1
        return_word=wrapper['address']+raw.index(jsr)+2
        cases=0;digest=hashlib.sha256()
        for p in range(256):
            if p&0x30:continue
            for tile in [0,0x54,0xc2,0xff]:
                ram=bytearray((i*13+tile)&255 for i in range(10240))
                def put(n,v):ram[g.at(L[n])]=v&255
                for n,v in dict(Player_PageLoc=0,Player_X_Position=0,RgTempX=254,RgTempPage=255,RgTempY=176,SmTemp=30).items():put(n,v)
                a=L['Block_Buffer_1']+208+15+9*16;ram[g.at(a)]=tile
                s=233;ram[s+257]=(g.RET-1)&255;ram[s+258]=(g.RET-1)>>8
                regs=[73,7,29,p,s];banks={0x8000:62,0xa000:5,0xc000:36,0xe000:63}
                a=g.execute(im,CPU,ram,regs,banks,body['address'],g.RET,native_status=True)
                b=g.execute(im,CPU,ram,regs,banks,wrapper['address'],g.RET,native_status=True)
                expected=bytearray(a['ram'])
                extra=[(0x100+s,return_word>>8),(0xff+s,return_word&255)]
                for address,value in extra:expected[address]=value
                expected[g.at(L['R3'])]=0
                assert b['ram']==expected,('All10240 exact explicit new writes',mapper,p,tile)
                wanted=extra+[(ad,val)for pc,op,ad,phys,val in a['trace']]+[(L['R3'],0)]
                assert [(ad,val)for pc,op,ad,phys,val in b['trace']]==wanted
                r=a['regs'].copy();r[0]=0;r[3]=(r[3]&~0x82)|2
                assert b['regs']==r and b['banks']==a['banks']==banks
                assert b['ram'][s+257:512]==ram[s+257:512]
                assert b['cycles']-a['cycles']==30
                digest.update(b['ram']);digest.update(bytes(b['regs'][:5]));cases+=1
        proofs.append(dict(mapper=mapper,cases=cases,all64_native_status_patterns=True,representative_tiles=[0,84,194,255],
                           exact_extra_ordered_writes=extra+[(L['R3'],0)],all10240_RAM_live_stack_AXYP_SP_PC_exact=True,
                           exact_added_cycles=30,digest=digest.hexdigest()))
    report=dict(status='PASS_NEGATIVE_ORIGIN_QUERY_EXPLICIT_WHOLE_STACK_RAM_AND_ORDERED_WRITES',script_sha256=sha(__file__),proofs=proofs)
    out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(status=report['status'],cases=sum(z['cases']for z in proofs))))


if __name__=='__main__':main()
