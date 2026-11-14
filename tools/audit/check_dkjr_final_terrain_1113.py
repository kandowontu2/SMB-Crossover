"""Parse actual1-1 final columns, then query them with declared DK bodies."""
from hashlib import sha256
import json

import compose_dkjr_direct_platform_1113 as T
import check_dkjr_direct_platform_1113 as Gate


def main():
    parent,raw=T.load_inputs();P,H,N,W,L=Gate.P,Gate.H,Gate.N,Gate.W,Gate.L
    bundle=W.Symbols.bundle();bundle['raw']=raw;parsed=N.fresh(bundle)
    N.put(parsed,AreaPointer=0x25,SelectedCharacter=0)
    N.invoke(parsed,'GetAreaDataAddrs')
    N.put(parsed,CurrentPageLoc=11,CurrentColumnPos=0,BlockBufferColumnPos=16,
        ScreenLeft_PageLoc=11,ScreenLeft_X_Pos=0,ColumnSets=11,AreaParserTaskNum=0,
        CurrentNTAddr_High=0x24,CurrentNTAddr_Low=0x80,BackloadingFlag=11,NmiDisable=255)
    for _ in range(12):
        N.put(parsed,VRAM_Buffer2_Offset=0,VRAM_Buffer_AddrCtrl=0)
        N.invoke(parsed,'AreaParserTaskControl')
    assert N.get(parsed,'CurrentPageLoc')*16+N.get(parsed,'CurrentColumnPos')==200
    attrs_at=W.location(bundle,'MTileAttribute');attrs=raw[attrs_at:attrs_at+256]
    tiles=[]
    for wx in range(3008,3089,16):
        base=W.address(bundle,'Block_Buffer_2'if(wx>>8)&1 else'Block_Buffer_1')
        values=[]
        for y in range(32,240,16):
            value=parsed[base+((y-32)&240)+((wx>>4)&15)]
            if value:values.append(dict(top=y,tile=value,source_solid=attrs[value]&3==1))
        tiles.append(dict(left=wx,cells=values))
    e73=T.Old.reverse(parent);_,seed=H.cold(e73,e73[P.B.COOKIE_AT:P.B.COOKIE_AT+16])
    model=Gate.Q.mounted(seed,raw)
    for name in('Block_Buffer_1','Block_Buffer_2'):
        at=W.address(bundle,name);model[at:at+208]=parsed[at:at+208]
    N.put(model,ScreenLeft_PageLoc=11,ScreenLeft_X_Pos=128)
    model.ram[2][0x8da]=1;hook=P.frozen_labels()['DkjrNativeTerrainHook'];queries=[]
    for x,y in((3039,41),(3039,46),(3039,48),(3039,64),(3039,96),(3039,128),(3039,160),(3039,163),(3048,46),(3048,64),(3048,160)):
        # Original standing [7,0,24,15], source origin X-8/Y+15.
        origin=x-2944-8;rect=[origin+7,y+15,origin+24,y+30]
        model.ram[2][0x3e:0x42]=bytes(rect)
        H.call(model,hook,a=2)
        count=model.ram[2][0x8dd];values=list(model.ram[2][0x880:0x880+count])
        queries.append(dict(nativeX=x,nativeY=y,body_rect=rect,kind2_count=count,
            static_rectangles=[values[i:i+4]for i in range(0,len(values),4)]))
    print('DKJR_FINAL_TERRAIN '+json.dumps(dict(candidate_SHA256=sha256(raw).hexdigest(),
        native_area_pointer=0x25,parsed_world_columns=[176,199],tiles=tiles,queries=queries,
        parser_fixture_and_explicit_query_rectangles=True,helper_actor_not_inserted_into_static_query=True,
        source_or_native_ROM_writes=False,outputs_written=0,
        scope='Actual compiled native1-1 backloading/parser plus explicit original-body queries. Not a genuine late-route state or physical native writer trace.'),separators=(',',':')),flush=True)


if __name__=='__main__':main()
