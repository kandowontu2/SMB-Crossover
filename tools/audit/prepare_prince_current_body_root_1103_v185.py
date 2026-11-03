"""Rebind the existing physical-controller/body observer to the current private Prince."""
from pathlib import Path
import argparse
import json
import re
from prepare_selected_native_packet_v1 import R, prepare, sha
from observe_chip_committed_write import lua

OLD = R / 'build/prince-native-followup-1103-v176/native/controller.lua'

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--sha',required=True)
    p.add_argument('--runtime',type=Path,required=True)
    p.add_argument('--metadata',type=Path,required=True)
    p.add_argument('--cookie',required=True)
    p.add_argument('--ref',type=Path,action='append',default=[])
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--jump',action='store_true')
    a=p.parse_args()
    assert sha(a.rom)==a.sha
    runtime=a.runtime.read_bytes();meta=a.metadata.read_bytes();raw=a.rom.read_bytes()
    source=OLD.read_text()
    # All named source entry addresses are unchanged by the zero-growth
    # repair. Each callback still checks its actual mapped physical address
    # and the successor's exact bytes, rather than accepting an old image.
    pattern=r'\["(\w+)"\]=\{\["pc"\]=(\d+),\["memory"\]="(\w+)",\["physical"\]=(\d+),\["bytes"\]=\{[^}]+\}\}'
    hooks={}
    for name,pc,memory,physical in re.findall(pattern,source):
        pc=int(pc);physical=int(physical)
        if memory=='nesPrgRom': code=raw[16+physical:16+physical+4]
        elif pc<0xc000: code=runtime[pc-0xa000:pc-0xa000+4]
        else: code=meta[pc-0xc800:pc-0xc800+4]
        assert len(code)==4,(name,hex(pc))
        hooks[name]=dict(pc=pc,memory=memory,physical=physical,bytes=list(code))
    assert len(hooks)==18,len(hooks)
    # PpLiveName is populated by the existing live installer, after decoding
    # the runtime. Its entry bytes are taken from that retained exact source.
    live=R/'build/prince-actor-1101-v1/native-live-v149.bin'
    h=hooks['PpLiveName'];off=h['pc']-0xbfa3
    assert 0<=off<len(live.read_bytes())-3
    h['bytes']=list(live.read_bytes()[off:off+4])
    insertion='\nQ.mode="Prince-current-body185";Q.maxFrames=5000;Q.ROM_sha256='+lua(a.sha)+'\nQ.cookie='+lua(list(bytes.fromhex(a.cookie)))+'\n'
    insertion+='for n,h in pairs('+lua(hooks)+')do Q.hooks[n]=h end\n'
    anchor='-- Controller-only source; Q is supplied by the hash-bound plan preparer.'
    assert source.count(anchor)==1
    source=source.replace(anchor,insertion+anchor)
    old='{"passed":true,"controller_only":true,"frames":%d'
    assert source.count(old)==1
    source=source.replace(old,'{"passed":true,"ROM_sha256":%q,"script_RAM_writes":false,"controller_only":true,"frames":%d')
    old="',frame,Q.mode,n,#observations,shots,activeData,lateEnable,tostring(Q.launch~=nil)"
    assert source.count(old)==1
    source=source.replace(old,"',Q.ROM_sha256,frame,Q.mode,n,#observations,shots,activeData,lateEnable,tostring(Q.launch~=nil)")
    receipts=[json.loads(t.read_text()) for t in a.ref]
    reads=[event for q in receipts for event in q.get('actual_first8_GameLoop',[])
           if event.get('event')=='actual_native_reservation_header']
    assert len(reads)==1
    reader=reads[0]['PC'];bank=reads[0]['Amap']&127
    assert 0xa000<=reader<0xc000
    physical=bank*8192+reader-0xa000
    assert raw[16+physical:18+physical]==bytes.fromhex('b103')
    observer='''
local reservationReads=0
emu.addMemoryCallback(function()
 if not sourceActive()or r('GameEngineSubroutine')~=8 or not lastDraw then return end
 local m=emu.convertAddress(READER_PC)
 if not m or m.memType~=emu.memType.nesPrgRom or m.address~=READER_PHYS then return end
 local ptr=ram(3)+256*ram(4);local length=ram(ptr)
 require(ptr==0x6b05 and ram(0x6e1)==0,'Actual native stable count header and absent legacy descriptor')
 require(length>=12 and length<=52 and length%4==0,'Actual native reservation uses original3..13 body parts')
 reservationReads=reservationReads+1
end,emu.callbackType.exec,READER_PC)
'''.replace('READER_PC',str(reader)).replace('READER_PHYS',str(physical))
    anchor='local function beginPart(name)'
    assert source.count(anchor)==1
    source=source.replace(anchor,observer+'\n'+anchor)
    old='render_evidence=renderEvidence~=nil,full_stage=false'
    assert source.count(old)==1
    source=source.replace(old,'render_evidence=renderEvidence~=nil,native_reservation_reads=reservationReads,full_stage=false')
    # Declare above summary's closure, so it records the local observer count.
    source=source.replace('local reservationReads=0\n','')
    anchor='local function summary(passed,why)'
    source=source.replace(anchor,'local reservationReads=0\n'+anchor)
    old="require(backdropCalls>0 and statusCalls>0 and renderEvidence~=nil,'Actual backdrop/status/body consumers')"
    assert source.count(old)==1
    source=source.replace(old,old+"\n  require(reservationReads>0,'Actual native projectile/enemy OAM reservation reader reached')")
    if a.jump:
        old="if part=='right-short'then return{'right'}elseif part=='left-turn'then return{'left'}end;return{}"
        assert source.count(old)==1
        source=source.replace(old,"if part=='source-jump'and advances-partAdvance<2 then return{'a'}end;"+old)
        old="elseif part=='reversed-rest'and advances-partAdvance>=2 then\n  completePart();require(phase0==advances"
        assert source.count(old)==1
        source=source.replace(old,"elseif part=='reversed-rest'and advances-partAdvance>=2 then\n  completePart();beginPart('source-jump');initialY=r('Player_Y_Position')\n elseif part=='source-jump'then\n  jumpMinY=math.min(jumpMinY or initialY,r('Player_Y_Position'))\n  if jumpMinY<initialY-8 and not jumpImage then jumpImage=true;shot('prince-original-jump')end\n  if not(jumpMinY<initialY-8 and advances-partAdvance>=4 and r('Player_State')==0 and math.abs(r('Player_Y_Position')-initialY)<=2)then return end\n  completePart();require(phase0==advances")
        anchor="local leftPeak,renderEvidence,renderFrame=nil,nil,nil"
        assert source.count(anchor)==1
        source=source.replace(anchor,anchor+'\nlocal jumpMinY,jumpImage=nil,false')
        source=source.replace("Real postdraw hardware body and original-source Left reversal","Real postdraw hardware body, original-source Left reversal and unarmed A jump/landing")
    # Native renderer snapshots are read only; source-state and object RAM
    # remain exclusively game-owned. Never patch memory to pass a scenario.
    assert not any(s in source for s in ['emu.write','emu.loadSavestate','emu.reset','emu.loadState'])
    prepare(a.output,a.rom,source,[Path(__file__),OLD,a.runtime,a.metadata,live,*a.ref],
        expected=a.sha,timeout=240,allow_interactive=True,
        scope='Current Prince cold menu/lives, full body draw/publication/hardware DMA and display snapshot; native OAM reservation fix; original source Right and Left reversal'+('; unarmed A jump and landing' if a.jump else '')+'. Existing176 strict body/motion/HP/lives guards retained. New mapped hook bytes/cookie bound to exact current image; no RAM seeds or emulated writes. Four PNG maximum; no full-stage/armed/audio claim.')

if __name__=='__main__':main()
