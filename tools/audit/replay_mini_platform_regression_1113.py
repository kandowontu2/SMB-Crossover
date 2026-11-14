"""Rebind the retained Mini route for stdout-only current platform regression.

The route, collision/render assertions and input decisions are retained. Old
file writers, screenshots and instruction/audio profilers are removed. The
additional observer counts real source/Main progress and skipped native NMIs.
Run through run_bounded_build_v1 with the existing root two-file output.
"""
from hashlib import sha256
import argparse
import json
from pathlib import Path
import re

import check_ff_white_mushroom_current_1110 as W
from check_ff_stdout_controller_source_1110 import LuaRuntime
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

R=W.R
PIN='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
BUB_NIGHTLY='f88cfe5aee15bb3921c691b7f06d905246be9ff88b9b43eea71c2405722724a7'
FOREGROUND_NIGHTLY='3684f3d2a418a484befd80fca351d0dc5f9b472f6f067a0a7894994ea343679d'
POSTBG_NIGHTLY='12397b1c2557834f6a2b7e23c9915d5dc40c6cabff7a6ee844c1adebf6564c52'
ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
SOURCE=R/'build/complete-roster-native-1110/packets/regression/mini/controller.lua'
SOURCE_SHA='d20ec6a9c7481b902a5b45033e1a2e4448df4555ba31d4e0981d1a371e920677'
OUT=R/'build/metal-flower-native-1112'


def once(text,before,after):
    assert text.count(before)==1,before[:160]
    return text.replace(before,after,1)


def controller(raw, *, contact_candidate=False, descending_candidate=False, bub_nightly=False, foreground_nightly=False, postbg_nightly=False):
    digest=sha256(raw).hexdigest()
    assert sum((contact_candidate,descending_candidate,bub_nightly,foreground_nightly,postbg_nightly))<=1
    if descending_candidate:
        import compose_dkjr_descending_platform_1113 as Contact
        assert digest==Contact.PIN
        public=Contact.P.inverse_current(Contact.reverse(raw))
        assert sha256(public).hexdigest()==PIN
        start=16+128*8192+962*1024
        assert raw[start:start+5120]==public[start:start+5120], 'Mini carrier must remain exact'
    elif contact_candidate:
        import compose_dkjr_platform_contact_1113 as Contact
        assert digest==Contact.PIN
        public=Contact.P.inverse_current(Contact.reverse(raw))
        assert sha256(public).hexdigest()==PIN
        start=16+128*8192+962*1024
        assert raw[start:start+5120]==public[start:start+5120], 'Mini carrier must remain exact'
    elif bub_nightly or foreground_nightly or postbg_nightly:
        import bub_native_noops_1113 as Bub
        previous=raw
        if postbg_nightly:
            import compose_smb2_postbg_mirror_1113 as PostBG
            assert digest==POSTBG_NIGHTLY
            previous=PostBG.inverse(raw)
            assert sha256(previous).hexdigest()==FOREGROUND_NIGHTLY
        if foreground_nightly or postbg_nightly:
            import compose_smb2_foreground_current_1113 as Current
            if foreground_nightly:assert digest==FOREGROUND_NIGHTLY
            previous=Current.inverse(previous)
            assert sha256(previous).hexdigest()==BUB_NIGHTLY
        else:
            assert digest==BUB_NIGHTLY
            previous=raw
        public=Bub.combined_reverse(previous)
        assert sha256(public).hexdigest()==PIN
        start=16+128*8192+962*1024
        assert raw[start:start+5120]==public[start:start+5120], 'Mini carrier must remain exact'
    else:
        assert digest==PIN
    original=SOURCE.read_bytes()
    assert sha256(original).hexdigest()==SOURCE_SHA
    full=original.decode('utf-8')
    text=full.split('local MiniProfileHooks=',1)[0]
    assert full.count('local MiniProfileHooks=')==1
    old='c10b7d87f466bf028096bddd33b7ac2baee242870ee83ccc4eebd529af57bd7f'
    text=once(text,old,digest)
    kernel=raw[16+128*8192+962*1024:16+128*8192+967*1024]
    oldkernel=re.search(r'\["kernel_SHA256"\]="([0-9a-f]{64})"',text)[1]
    # Rebind only after each retained hook authenticates against the actual
    # current loaded image or native PRG, never a stale symbol address alone.
    for pc,physical,kind,values in re.findall(
            r'\["pc"\]=(\d+),\["physical"\]=(\d+),\["memory"\]="(nesWorkRam|nesPrgRom)",\["bytes"\]=\{([\d,]+)\}',text):
        pc,physical=int(pc),int(physical)
        expected=bytes(map(int,values.split(',')))
        actual=kernel[pc-0xa000:pc-0xa000+len(expected)] if kind=='nesWorkRam' else raw[16+physical:16+physical+len(expected)]
        assert actual==expected,(hex(pc),kind,actual.hex(),expected.hex())
    text=once(text,oldkernel,sha256(kernel).hexdigest())
    text=once(text,"local csv=assert(io.open(OUTPUT..'smoke.csv','w'))\ncsv:write('frame,Main,source,phase,x16,y16,xvel,yvel,current,queued,class,contacts,held,fresh,nativeX,nativeY,nativeState,pose\\n')",
        "local cadence={physical=0,source_updates=0,completed_Main=0,skipped_NMI=0,zero_source_frames=0,zero_Main_frames=0,input_polled_frames=0,max_source_per_frame=0,exceptions={}}\nlocal cadencePrevious=nil\nlocal cadencePolled=false")
    text=once(text," local f=assert(io.open(OUTPUT..'result.json','w'));f:write(json(q)..'\\n');f:close();csv:flush();return q",
        " q.ROM_SHA256=C.ROM_sha256;q.cadence=cadence;q.capture_files=0;q.screenshots=0\n q.scope='Retained ordinary Mini1-1 controls and source/body/DMA assertions, fresh current ROM; acoustic and extended end-of-level profilers omitted.'\n print('SMB_NATIVE_RECEIPT '..json(q));return q")
    start=text.index('local function guard(fn)')
    end=text.index('local function check(ok,why)',start)
    text=text[:start]+'''local function guard(fn)return function(...)
 if done then return end
 local ok,e=pcall(fn,...)
 if not ok then if native_snapshot then end_native.terminal=native_snapshot()end;result(false,tostring(e));done=true;emu.stop(1)end
end end
'''+text[end:]
    start=text.index('local function shot(tag)')
    end=text.index('local function snapshot()',start)
    text=text[:start]+"local function shot(tag)end -- Capture-free regression.\n"+text[end:]
    text=once(text," csv:write(table.concat({frame,mains,updates,phase,s.x,s.y,s.vx,s.vy,s.current,s.queued,s.class,s.contacts,s.held,s.fresh,s.nativeX,s.nativeY,s.nativeState,s.pose},',')..'\\n')",'')
    text=once(text,"shot('mini-active-1-2');audioAssertFinished();result(true);csv:close();done=true;print('PASS Mini actual nonshortcut1-1');emu.stop(0)",
        "shot('mini-active-1-2');result(true);done=true;emu.stop(0)")
    text=once(text,"local end_csv=assert(io.open(OUTPUT..'native-end.csv','w'))\nend_csv:write('frame,source,Main,worldX,Ready,sourceX16,sourceY16,sourceCurrent,sourceQueued,gameTimer,'..table.concat(native_fields,',')..'\\n')",'')
    text=once(text," end_csv:write(table.concat(values,',')..'\\n');end_csv:flush();last_end_log=frame",' last_end_log=frame')
    # The retained route's boarding assertions depend on this passive birth
    # observer. Keep it even though its old standalone JSON writer is omitted.
    start=full.index('-- Observe constructor ingress after the real actor fields are published.')
    end=full.index('local beforeCameraFinish=profileFinish',start)
    text+='\n'+full[start:end]
    bundle=dict(W.Symbols.bundle(),raw=raw)
    skipped=W.address(bundle,'NmiSkipped')
    # Appended observers run after the unchanged controller's callbacks. Only
    # consecutive live original1-1 frames are charged to the cadence window;
    # native flag/castle/area transition intentionally has no source updates.
    text+=f'\nlocal skippedAddress={skipped}\n'
    text+=r'''
emu.addEventCallback(guard(function()cadencePolled=true end),emu.eventType.inputPolled)
emu.addEventCallback(guard(function()
 local now={source=updates,main=mains,skipped=read(skippedAddress),frame=frame,
  eligible=phase=='fullstage'and active()and r('WorldNumber')==0 and r('LevelNumber')==0}
 if cadencePrevious and cadencePrevious.eligible and now.eligible and now.frame==cadencePrevious.frame+1 then
  local sources=now.source-cadencePrevious.source
  local cores=now.main-cadencePrevious.main
  cadence.physical=cadence.physical+1
  cadence.source_updates=cadence.source_updates+sources
  cadence.completed_Main=cadence.completed_Main+cores
  local skips=(now.skipped-cadencePrevious.skipped)&255
  cadence.skipped_NMI=cadence.skipped_NMI+skips
  if sources==0 then cadence.zero_source_frames=cadence.zero_source_frames+1 end
  if cores==0 then cadence.zero_Main_frames=cadence.zero_Main_frames+1 end
  if cadencePolled then cadence.input_polled_frames=cadence.input_polled_frames+1 end
  cadence.max_source_per_frame=math.max(cadence.max_source_per_frame,sources)
  if (sources~=1 or cores~=1 or skips~=0)and #cadence.exceptions<12 then
   local cpu=emu.getState()
   cadence.exceptions[#cadence.exceptions+1]={frame=frame,source=updates,Main=mains,
    sources=sources,cores=cores,skips=skips,PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],
    nativeX=r('Player_X_Position')+256*r('Player_PageLoc'),nativeY=r('Player_Y_Position'),
    nativeState=r('Player_State'),sourceCurrent=ram(0xc240),sourceQueued=ram(0xc228)}
  end
 end
 cadencePrevious=now;cadencePolled=false
end),emu.eventType.endFrame)
assert(os.getenv('SMB_STDOUT_ROM_SHA')==C.ROM_sha256,'Exact current Mini ROM binding')
'''
    assert not re.search(r'\bio\s*[.:]|\bemu\s*[.:]\s*(?:write|save|load)|takeScreenshot',text)
    LuaRuntime().compile(text)
    return text


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--metadata',action='store_true')
    p.add_argument('--require-zero-lag',action='store_true')
    modes=p.add_mutually_exclusive_group()
    modes.add_argument('--contact-candidate',action='store_true',help='Frozen b420 negative only; candidate must already be staged by root.')
    modes.add_argument('--descending-candidate',action='store_true',help='Explicit exact14ae private successor; retains the frozen b420 mode.')
    args=p.parse_args()
    public_now=check(ROM)['ROM_sha256']
    assert public_now in(PIN,BUB_NIGHTLY,FOREGROUND_NIGHTLY,POSTBG_NIGHTLY)
    rom=OUT/'candidate.nes' if args.contact_candidate or args.descending_candidate else ROM
    raw=rom.read_bytes();digest=sha256(raw).hexdigest()
    text=controller(raw,contact_candidate=args.contact_candidate,descending_candidate=args.descending_candidate,
        bub_nightly=not(args.contact_candidate or args.descending_candidate)and public_now==BUB_NIGHTLY,
        foreground_nightly=not(args.contact_candidate or args.descending_candidate)and public_now==FOREGROUND_NIGHTLY,
        postbg_nightly=not(args.contact_candidate or args.descending_candidate)and public_now==POSTBG_NIGHTLY)
    summary=dict(ROM_SHA256=digest,public_ROM_SHA256=public_now,recipe_parent_SHA256=PIN,source_SHA256=SOURCE_SHA,
        script_SHA256=sha256(text.encode()).hexdigest(),native_run=not args.metadata)
    if not args.metadata:
        script=OUT/'controller.lua'
        script.write_text(text,encoding='utf-8',newline='\n')
        q=run(script,rom,OUT/'capture',digest,240)
        receipt=q['receipt']
        # The full actual receipt is hashed above. Print only bounded useful
        # fields; the old native-end observer has dozens of redundant states.
        compact={k:receipt.get(k)for k in('passed','error','physical_frames','completed_Main','source_updates',
            'checks','cadence','full_stage','terminal_native','capture_files','script_RAM_writes')}
        compact['lifts']=receipt.get('phases',{}).get('fullstage',{}).get('lifts',[])
        compact['obstacles']=receipt.get('phases',{}).get('fullstage',{}).get('actual_obstacle_clears',[])
        summary.update(passed=q['passed'],receipt_SHA256=q['receipt_SHA256'],receipt=compact,outputs_written=q['outputs_written'])
        print(json.dumps(summary,separators=(',',':')),flush=True)
        assert check(ROM)['ROM_sha256']==public_now
        assert q['passed'],'Retained current Mini full-stage replay failed'
        if args.require_zero_lag:
            cadence=q['receipt']['cadence']
            assert cadence['physical']>3000,cadence
            assert cadence['source_updates']==cadence['completed_Main']==cadence['physical'],cadence
            assert cadence['skipped_NMI']==cadence['zero_source_frames']==cadence['zero_Main_frames']==0,cadence
            assert cadence['input_polled_frames']==cadence['physical'],cadence
    else:
        print(json.dumps(summary,separators=(',',':')),flush=True)


if __name__=='__main__':main()
