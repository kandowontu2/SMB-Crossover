"""Actual cold ROM portrait/colors, with poisoned RAM3 and native CHR publisher."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_native_adapter_controls_v1 as T
from battletoads_small_core_assets_v1 import decode
from arthur_cache_host_controls_v1 import OverlayMemory
O=R/'build/battletoads-cold-acquire-v4';J=O/'joint'

class Watched(OverlayMemory):
    def __getitem__(self,i):
        if isinstance(i,int)and i>=0x8000 and self.rawtags[(i-0x8000)//8192]==3:self.cache_reads.append(i)
        return super().__getitem__(i)

def main():
    out=O/'cold-controls.json';assert not out.exists();q=dict(passed=False,native=False,portrait=[],palette=[])
    try:
        b=T.H.C.qualified(J/'candidate.nes')
        poses=json.loads((R/'build/battletoads-small-core-assets-v1/poses.json').read_text())['frames'];pose=poses[0]
        art=(R/'build/battletoads-small-core-assets-v1/art.chr').read_bytes();expected={}
        rec=pose['descriptor']
        for i in range(1,len(rec),4):
            tile,a,y,x=rec[i:i+4];expected.update(decode(art[tile*16:tile*16+32],x-256 if x>127 else x,y-256 if y>127 else y,a))
        for player,variant,flags,scene in itertools.product(range(2),range(2),range(64),['menu','lives']):
            m=T.L.make(b,CurrentPlayer=player,FmGroups=variant<<5,OperMode=0 if scene=='menu'else 1,
                Player_X_Position=120 if scene=='menu'else 88,Player_Y_Position=160 if scene=='menu'else 96,
                CurrentOAMOffset=0,GuestAudioCharacter=9)
            m.__class__=Watched;m.cache_reads=[]
            before=[bytes(x)for x in m.ram];a=173;x=91;y=37;p=T.L.flags(flags)
            c,low=T.L.call(m,'BtColdPortrait',a=a,x=x,y=y,p=p)
            assert(c.a,c.x,c.y,c.p,c.sp)==(a,x,y,(p&0x7d)|128,224)
            assert not m.cache_reads and [bytes(z)for z in m.ram]==before
            count=T.H.get(m,'CurrentOAMOffset');assert count==32
            assert m.rawtags[2]==216 and T.H.get(m,'CurrentBankC')==216
            T.H.invoke(m,'X5PublishChr');assert m.chr_latches[0]==915
            actual={};cx=T.H.get(m,'Player_X_Position')+8;cy=T.H.get(m,'Player_Y_Position')+21
            for i in range(0,count,4):
                oy,t,attr,ox=bytes(m[512+i:516+i]);assert oy<240
                at=16+0x100000+915*1024+t*16
                for key,v in decode(b['raw'][at:at+32],ox-cx,oy+1-cy,attr&3,bool(attr&64)).items():
                    if key not in actual:actual[key]=v
            assert actual==expected,('cold source standing pixels/roles',scene,player,variant,flags)
            q['portrait'].append(dict(player=player,variant=variant,flags=flags,scene=scene,parts=8,
                opaque_pixels=len(actual),no_cache_reads=True,minimum_SP=low,CPU=c.processorCycles))
        colors=[34,34,15,15,15,34,15,15]
        for variant,background,area,offset in itertools.product(range(2),range(8),range(4),[0,30,67,68]):
            m=T.L.make(b,OperMode=0,FmGroups=variant<<5,BackgroundColorCtrl=background,AreaType=area,VRAM_Buffer1_Offset=offset)
            m.__class__=Watched;m.cache_reads=[]
            at=T.address(b,'VRAM_Buffer1');m[at:at+84]=[137]*84
            before=[bytes(z)for z in m.ram]
            c,low=T.L.call(m,'BtColdColors',a=173,x=91,y=37,p=0xff)
            assert(c.a,c.x,c.y,c.p,c.sp)==(173,91,37,253,224)
            assert not m.cache_reads and[bytes(z)for z in m.ram]==before
            packet=bytes(m[at:at+84]);assert packet[:offset]==bytes([137])*offset
            if offset>=68:assert packet==bytes([137])*84 and T.H.get(m,'VRAM_Buffer1_Offset')==offset
            else:
                expectedpacket=bytes([63,16,1,colors[background or area],63,17,3,15,10 if variant==0 else 23,26 if variant==0 else 39,63,21,3,24,40,32,0])
                assert packet[offset:offset+17]==expectedpacket
                assert T.H.get(m,'VRAM_Buffer1_Offset')==offset+16
                assert packet[offset+17:]==bytes([137])*(84-offset-17)
            q['palette'].append(dict(variant=variant,BackgroundColorCtrl=background,AreaType=area,offset=offset,
                accepted=offset<68,original_native_universal_restored=True,CPU=c.processorCycles))
        q.update(passed=True,public_ABI='Actual own entry AXYP preserved; genuine outer SFC derives NZ from returned A, CVDI preserved',retained_observer_negative=str(R/'build/battletoads-cold-preview-v2/cold-controls.json'),cold_portrait_pairs=len(q['portrait']),cold_palette_pairs=len(q['palette']),
            no_RAM3_initialization_or_reads=True,AXYP_SP_C_maps_exact=True,source_standing_pixels_palette_roles_anchor_exact=True,
            scope='Actual no-cache ROM portrait and menu palette. Real controller/menu/lives pipeline, gameplay acquisition and P1 retirement remain pending; forcedblank acquisition is tested separately.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):T.L.sha(p)for p in[Path(__file__),Path(T.__file__),O/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'bt/preview.s',R/'build/battletoads-small-core-assets-v1/controls.json']}
    out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['portrait','palette','bindings','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
