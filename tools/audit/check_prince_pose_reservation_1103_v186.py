"""Actual current cold, original408 poses and complete native reservation seam."""
from pathlib import Path
from collections import Counter
import json, sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit')]
import prepare_prince_pose_reservation_1103_v185 as M
import check_prince_body_cold_1103_v181 as C
O, V, N, I = M.O, C.V, C.N, C.I


def source_images():
    return ((O/'pose-runtime.bin').read_bytes(), (O/'pose-metadata.bin').read_bytes(),
            M.OLD.images()[2])


def loaded(base, seed=None):
    if seed is None:
        seed, _ = C.C.cold(base,38)
    m = N.fork(seed)
    N.put(m,NmiDisable=1,DisableScreenFlag=0,TimerControl=0,AreaType=1,
          Player_Rel_XPos=48,Player_Rel_YPos=176,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,
          ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,Mirror_PPUMASK=30)
    m[0x2001]=30
    return base,m,json.loads((V.O/'native-labels-v153.json').read_text())


def first8(base, seed=None):
    prior=V.loaded
    V.loaded=lambda:loaded(base,seed)
    try:
        return V.first8()
    finally:
        V.loaded=prior


def compare_private(before,after,allowed):
    for bank in [2,3]:
        diff=[i for i,(a,b) in enumerate(zip(before.ram[bank],after.ram[bank]))
              if a!=b and i not in allowed[bank]]
        assert not diff,(bank,diff[:12])


def main(proof_name='pose-CPU-v186.json'):
    base,q=M.image()
    runtime,meta,state=source_images()
    print('Actual current five-owner cold -> Prince38',flush=True)
    seed,cold=C.C.cold(base,38)
    want=bytearray(runtime)
    want[0x1fa3:0x1fd8]=(V.O/'native-live-v149.bin').read_bytes()
    assert bytes(seed.ram[3][:8159])==want
    assert bytes(seed.ram[2][0x800:0x800+len(meta)])==meta
    assert bytes(seed.ram[2][0x200:0x235])==bytes(53)
    cookie=bytes.fromhex(q['Prince_cookie'])
    assert all(bytes(seed.ram[k][0x1fe0:0x1ff0])==cookie for k in [2,3])
    lab=json.loads((V.O/'native-labels-v153.json').read_text())
    # The independent positive180 oracle is injected only into a reference
    # clone. The candidate always executes the bytes decoded by genuine cold.
    ref=N.fork(seed)
    oldruntime,oldmeta,_=M.OLD.images()
    prior=bytearray(oldruntime)
    prior[0x1fa3:0x1fd8]=(V.O/'native-live-v149.bin').read_bytes()
    ref.ram[3][:len(prior)]=prior
    ref.ram[2][0x800:0x800+len(oldmeta)]=oldmeta
    allowed={2:set(),3:{i for i,(a,b) in enumerate(zip(prior,want)) if a!=b}}
    art=json.loads((V.O/'source-art.json').read_text())
    pattern=(V.O/'prince-body-8x16.chr').read_bytes()
    original_lo=(V.O/'native-runtime-v153.bin').read_bytes()[0x1da4:0x1dc3]
    original_hi=bytes([1]*22+[2]*9)
    hist=Counter();parts=patternbytes=0
    for pose in art['poses']:
        pair=[N.fork(ref),N.fork(seed)]
        for m in pair:
            m.raw_page(2,2);N.put(m,CurrentBankC=2,CurrentOAMOffset=0,
                                 GuestOamRotationActive=1,RgOamRotation=0)
            m.ram[2][0x617]=pose['source_frame'];m.ram[2][0x615]=pose['source_facing']
            m[0x200:0x300]=bytes([0xf8])*256
            I.invoke(m,3,lab['PpHostProject'],(83,71,109,0x61))
            I.invoke(m,3,0xc383,(83,71,109,0x61))
        outs=[I.invoke(m,3,lab['PpHostDraw'],(83,71,109,0x61)) for m in pair]
        assert outs[0]['regs']==outs[1]['regs']
        for start,end in [(3,11),(0x15a,0x17b),(0x200,0x800)]:
            if bytes(pair[0][start:end])!=bytes(pair[1][start:end]):
                print('Candidate/reference native differences',[(hex(i),pair[0][i],pair[1][i])
                      for i in range(start,end) if pair[0][i]!=pair[1][i]][:24],flush=True)
            assert bytes(pair[0][start:end])==bytes(pair[1][start:end]),(pose['source_frame'],start)
        compare_private(pair[0],pair[1],allowed)
        n=len(pose['parts_8x16']);hist[n]+=1
        assert N.get(pair[1],'SmPose')==4*n
        frame=pose['source_frame'];tagged=int.from_bytes(meta[2*frame:2*frame+2],'little')
        assert tagged!=65535 and (meta[tagged&0x7fff]&15)==n
        at=len(pair[1].writes);N.invoke(pair[1],'BankSwitchCHR',a=83,x=71,y=109,p=0x61)
        upper=0;banks={}
        for address,value in pair[1].writes[at:]:
            if address==0x5130:upper=value&3
            elif 0x5120<=address<0x512c:banks[address-0x5120]=value+256*upper
        pages=sorted({p['pattern_pair']//32 for p in pose['parts_8x16']})
        for window,page in enumerate(pages):
            assert banks[window]==original_lo[page]+256*original_hi[page]
        for i,p in enumerate(pose['parts_8x16']):
            tile=pair[1][0x201+4*i];logical=(tile&1)*4096+(tile&254)*16
            actual=bytes(base['raw'][1048592+banks[(logical+j)//1024]*1024+(logical+j)%1024]
                         for j in range(32))
            assert actual==pattern[p['pattern_pair']*32:p['pattern_pair']*32+32]
            parts+=1;patternbytes+=32
    assert sum(hist.values())==408 and parts==2578
    print('Original408 poses/2578parts/count and final CHR pattern bytes exact',flush=True)
    # Actual first8 then wholeGameLoop. Observe the native header indirect
    # read with its real native A/C maps, and preserve body through native
    # object rendering. No emulator or controller/native outcome seeding.
    e,m,lab=first8(base,seed)
    reader=I.address(base,'RosterProjectileOamReady')+12
    reader_bank=((I.location(base,'RosterProjectileOamReady')-16)//8192)|128
    emitter=I.address(base,'MetaspriteRenderLoop')
    emitter_bank=((I.location(base,'MetaspriteRenderLoop')-16)//8192)|128
    actual=N.NesMPU;events=[];pending=None;body=None;steps=0;dead_A_inputs=set()
    poses={(p['source_frame'],p['source_facing']):p for p in art['poses']}
    class Trace(actual):
        def step(self):
            nonlocal pending,body,steps
            mem=self.memory
            bank=mem.rawtags[(self.pc-0x8000)//8192] if self.pc>=0x8000 else None
            if pending is not None and (self.pc,self.sp)==pending['return']:
                row=pending;pending=None
                size=row['count'];start=(row['prefix']+row['rotation'])&255
                snapshot=bytes(mem[0x200+((start+i)&255)] for i in range(size))
                body=dict(start=start,count=size,bytes=snapshot)
                events.append(dict(event='source_body_emitted',parts=size//4,header=N.get(mem,'SmPose'),
                                   prefix=row['prefix'],rotation=row['rotation']))
            if (self.pc,bank)==(emitter,emitter_bank) and mem[3]+256*mem[4]==0xc200:
                frame=mem.ram[2][0x617];face=mem.ram[2][0x615]
                count=4*len(poses[frame,face]['parts_8x16'])
                assert mem.ram[2][0x200]==N.get(mem,'SmPose')==count
                dead_A_inputs.add(self.a)
                ret=((mem[0x101+self.sp]|mem[0x102+self.sp]<<8)+1)&65535
                pending=dict(return_=(ret,self.sp+2),count=count,prefix=N.get(mem,'CurrentOAMOffset'),
                             rotation=N.get(mem,'RgOamRotation') if N.get(mem,'GuestOamRotationActive') else 0)
                pending['return']=pending.pop('return_')
            if (self.pc,bank)==(reader,reader_bank):
                ptr=mem[3]+256*mem[4];count=mem[ptr]
                assert ptr==0x6b05 and count==4*len(poses[mem.ram[2][0x617],mem.ram[2][0x615]]['parts_8x16'])
                assert mem.rawtags[2]!=2 and N.get(mem,'ObjectMetasprite')==0
                events.append(dict(event='actual_native_reservation_header',PC=self.pc,
                                   Amap=mem.rawtags[1],Cmap=mem.rawtags[2],SP=self.sp,
                                   pointer=ptr,count=count,before=N.get(mem,'CurrentOAMOffset')))
            return super().step()
    N.NesMPU=Trace
    try:
        out=e['run'](m,'GameLoop',lab)
    finally:
        N.NesMPU=actual
    assert pending is None and body and any(r['event']=='actual_native_reservation_header' for r in events)
    assert bytes(m[0x200+((body['start']+i)&255)] for i in range(body['count']))==body['bytes']
    assert N.get(m,'PlayerChrBank')==85 and N.get(m,'SmPosePtr')+256*N.get(m,'SmPosePtr',1)==0x6b05
    # Each byte in both complete auth headers rejects the public entry.
    poisons=0
    for bank in [2,3]:
        for index in range(16):
            h=N.fork(seed);h.ram[bank][0x1fe0+index]^=1
            before=[bytes(a) for a in h.ram]
            got=I.invoke(h,193,0xb08c,(83,71,109,0x21))
            assert not got['regs'][3]&1 and before==[bytes(a) for a in h.ram]
            poisons+=1
    qout=dict(passed=True,CPU_only=True,ROM_written=False,source_code_injected=False,
              reference_only_injected=True,memory_SHA256=q['expected_memory_only_SHA256'],
              current_parent_SHA256=q['parent_SHA256'],Prince_cookie=q['Prince_cookie'],
              actual_Prince_cold=dict(CPU=cold['CPU'],minimum_SP=cold['minSP'],
                                     runtime_metadata_exact=True,packet_zero=True,both_full_headers=True),
              source_facing_poses=408,source_parts=parts,exact_final_pattern_bytes=patternbytes,
              source_part_histogram=dict(hist),stable_length_bytes=[12,52],
              exact_renderer_AXYP_R0_R7_SMC_maps_and_source_state=True,
              actual_first8_GameLoop=events,body_preserved_after_native_objects=True,
              whole_Main_minimum_SP=out['minSP'],actual_dead_native_A_inputs=sorted(dead_A_inputs),
              bad_header_bytes_rejected_without_private_write=poisons,
              shared_five_owner_code_tables_and_all_Mini_bytes_exact=True,
              reuse='Unchanged5owner shared code/header protocol, foreign owners and cold/retire/IRQ grants are retained by exact byte equality. New private render instruction paths require distinct bounded IRQ/FF checks before native-ready.',
              scope='Actual source-backed currentca90 cold and complete first8 nativeGameLoop;408typed original poses compare the positive180 render oracle and originalpattern data. Only reference clone has oldcode injected. No ROM/menu/native emulator/fullstage/audio/helper claim.',
              bindings={p.relative_to(R).as_posix():M.sha(p) for p in [Path(__file__),Path(M.__file__),
                       O/'pose-manifest.json',O/'pose-source.json',V.O/'source-art.json',
                       R/'src/metasprite_engine.s',R/'src/game.s']})
    (O/proof_name).write_text(json.dumps(qout,indent=2)+'\n')
    print(json.dumps({k:v for k,v in qout.items() if k!='bindings'}))


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        if not (O/'pose-negative-v186.json').exists():
            (O/'pose-negative-v186.json').write_text(json.dumps(dict(passed=False,error=repr(error)),indent=2)+'\n')
        raise
