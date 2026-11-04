"""Check the direct Mini packet against native callers, in memory only."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from prepare_mini_mario_native_power_1103_v56 import N, address, bundle
from prepare_selected_native_packet_v1 import R, sha

PARENT = R/'build/mini-zero-visible-direct/mini-empty-draw.nes'
PIN = 'a09a538e550b912e0d4e131c4328902e26aaa94844448c6eedf4a5dd1be317ad'
SPANS = [('RARE_CLASS',124,0xa8c7,15,0xea),('RARE_TABLE',124,0xa95e,15,0xea),
         ('RARE_PREPARE',124,0xab3d,15,0xea),('RARE_PREPARE_TAIL',124,0xabd7,13,0xea),
         ('DIRECT_BODY',84,0xb420,173,0xea),('DIRECT_RETURN',84,0xb5f0,16,0xff),
         ('DIRECT_FINISH',84,0xb3dd,15,0xea),('DIRECT_BOX',84,0xa754,5,0xea)]
NAMES = ['NrMovement','NrGraphics','NrDraw','NrPortrait','NrWeapons','NrInjury',
         'NrLegacyInjuryStatus','NrDeathStart','NrDeath','NrVisible','NrHead',
         'NrBody','NrAdder','NrBox','NrSide']


def compose(out):
    assert sha(PARENT) == PIN
    raw = bytearray(PARENT.read_bytes())
    patches = []
    old_names = dict(RARE_CLASS='RARE_CLASS',RARE_TABLE='RARE_TABLE',
                     RARE_PREPARE='RARE_CONSTANT',RARE_PREPARE_TAIL='RARE_FINISH')
    for name, bank, pc, cap, fill in SPANS:
        at = 16+8192*bank+(pc&8191)
        data = (out/(name+'.bin')).read_bytes()
        assert len(data)<=cap
        if name in old_names:
            old = (R/'build/mini-idle-constants-1103'/(old_names[name]+'.bin')).read_bytes()
            assert raw[at:at+cap] == old.ljust(cap,bytes([fill]))
        else:
            assert raw[at:at+cap] == bytes([fill])*cap,(name,raw[at:at+cap].hex())
        before = bytes(raw[at:at+len(data)])
        raw[at:at+len(data)] = data
        patches.append(dict(name=name, bank=bank, pc=pc, file_offset=at,
                            old_hex=before.hex(), new_hex=data.hex()))
    assert raw[16+126*8192+0xc2:16+126*8192+0xc9] == bytes.fromhex('8da17d8d165160')
    return bytes(raw), patches


def machine(image):
    m = N.fresh(image)
    N.put(m,SelectedCharacter=41,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,
          Mirror_PPUMASK=0,NmiDisable=255,Mirror_PPUCTRL=160)
    N.invoke(m,'MiniScene')
    N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,OperMode_Task=3,GameEngineSubroutine=8,
          PlayerStatus=0,PlayerSize=1,Player_X_Position=40,Player_PageLoc=0,
          Player_Y_Position=176,Player_Y_HighPos=1,PlayerFacingDir=1)
    for name in ('Block_Buffer_1','Block_Buffer_2'):
        at = address(image,name)
        m[at:at+208] = [0]*176+[0x54]*32
    m[address(image,'GameTimerDisplay')] = 4
    return m


def compare(pair, results, label):
    regs = [(r['A'],r['X'],r['Y'],r['P']&0xcf) for r in results]
    assert regs[0]==regs[1],(label,'AXYP',regs)
    assert pair[0].rawtags==pair[1].rawtags,(label,'mapper')
    assert [bytes(x) for x in pair[0].ram]==[bytes(x) for x in pair[1].ram],(label,'private RAM')
    for lo,hi in [(0,256),(0x200,0x8000)]:
        assert pair[0][lo:hi]==pair[1][lo:hi],(label,'native RAM',[
            (hex(a),pair[0][a],pair[1][a])for a in range(lo,hi)if pair[0][a]!=pair[1][a]][:12])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();out=args.output.resolve()
    after,patches=compose(out)
    images=[bundle(PARENT.read_bytes()),bundle(after)]
    seeds=[machine(image)for image in images]
    # Establish the actual movement epoch through native complete calls.
    for epoch in [1,2]:
        result=[]
        for m in seeds:
            N.put(m,FrameCounter=epoch,SavedJoypadBits=0,SavedJoypad1Bits=0)
            result.append(N.invoke(m,'GameCoreRoutine',x=0,y=0))
        compare(seeds,result,('initial',epoch))
    calls={}
    for name in NAMES:
        count=saved=0
        for engine,epoch,p in itertools.product([8,4],[0,2,3],[0x21,0xe0]):
            pair=[N.fork(seed)for seed in seeds]
            results=[]
            for m in pair:
                N.put(m,GameEngineSubroutine=engine,FrameCounter=epoch)
                results.append(N.invoke(m,name,a=41 if name in ['NrAdder','NrBox']else 83,
                                        x=7,y=14 if name=='NrSide'else 91,p=p))
            compare(pair,results,(name,engine,epoch,p))
            saved+=results[0]['CPU']-results[1]['CPU'];count+=1
        calls[name]=dict(cases=count,mean_cycles_saved=saved/count)
    frames=[]
    for pattern in ['idle','right','left','jump']:
        pair=[N.fork(seed)for seed in seeds];cycles=[0,0]
        for epoch in range(250,274):
            keys={'idle':0,'right':1,'left':2,'jump':128 if epoch<262 else 0}[pattern]
            results=[]
            for i,m in enumerate(pair):
                N.put(m,GameEngineSubroutine=8,FrameCounter=epoch&255,SavedJoypadBits=keys,
                      SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
                r=N.invoke(m,'GameCoreRoutine',x=0,y=0);cycles[i]+=r['CPU'];results.append(r)
            compare(pair,results,('frame',pattern,epoch))
        frames.append(dict(pattern=pattern,updates=24,old_cycles=cycles[0],direct_cycles=cycles[1]))
    report=dict(passed=True,source_CPU_only=True,ROM_written=False,parent_SHA256=PIN,
                memory_candidate_SHA256=hashlib.sha256(after).hexdigest(),patches=patches,
                native_calls=calls,native_frames=frames)
    (out/'CPU.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items()if k!='patches'}))


if __name__=='__main__':main()
