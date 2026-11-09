"""Rebase the DK Jr frontend and OAM repair on the current Mini nightly for private QA."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from observe_chip_committed_write import lua
from prepare_selected_native_packet_v1 import R, prepare, sha


CURRENT = R/'build/mini-parser-lift-1109/candidate.nes'
PIN = 'a08d839b187fc6866a3fd3658200c2f26b8e3724b3b4de3b5e7d2a65702598d2'
FRONTEND = R/'build/dkjr-current-ingress-1108-v1/frontend-v2.json'
LAYOUT = R/'build/dkjr-native-source-1102-v2/native-entrance-v89-layout.json'
SOURCE = Path(__file__).with_name('dkjr_smoke_1108.lua')
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
FRONTEND_BASE = R/'build/mini-two-fireballs-1103/mini-empty-draw.nes'


def apply(raw,rows,seen):
    for row in rows:
        at=row['file_offset']
        before,after=(bytes.fromhex(row[key]) for key in ('old_hex','new_hex'))
        claimed=range(at,at+len(before))
        assert len(before)==len(after) and raw[at:at+len(before)]==before,hex(at)
        assert seen.isdisjoint(claimed),hex(at)
        raw[at:at+len(before)]=after
        seen.update(claimed)


def observer(config):
    body=SOURCE.read_text()
    anchor='local body = {returns=0,writes=0}'
    assert body.count(anchor)==1
    body=body.replace(anchor,anchor+'''
local pendingBody, dmaBody
body.dma_matches=0
body.hardware_matches=0
''')
    anchor=' if body.first then return end'
    assert body.count(anchor)==1
    body=body.replace(anchor,'''
 local before,after=body.offset_before,read(0x6de)
 if private(2,0x8fa)~=0 and before and after>before then
  local rotate=read(0x6c0b)~=0 and read(0x6c08) or 0
  pendingBody={}
  for offset=before,after-1,4 do
   local slot=(offset+rotate)&255
   local y=read(0x200+slot)
   if y<240 then
    pendingBody[#pendingBody+1]={slot=slot,y=y,tile=read(0x201+slot),attr=read(0x202+slot),x=read(0x203+slot)}
   end
  end
 else pendingBody=nil end
'''+anchor)
    anchor="emu.addEventCallback(function()\n local keys={}"
    assert body.count(anchor)==1
    body=body.replace(anchor,'''emu.addMemoryCallback(function(_,page)
 if not active() or page~=2 or not pendingBody or #pendingBody==0 then return end
 for _,o in ipairs(pendingBody) do
  assert(read(0x200+o.slot)==o.y and read(0x201+o.slot)==o.tile and
         read(0x202+o.slot)==o.attr and read(0x203+o.slot)==o.x,'DK Jr body survives native render to DMA')
 end
 body.dma_matches=body.dma_matches+1
 dmaBody=pendingBody
 pendingBody=nil
end,emu.callbackType.write,0x4014)
'''+anchor)
    anchor=" local skipped=read(0x013a)"
    assert body.count(anchor)==1
    body=body.replace(anchor,'''
 if dmaBody then
  local function oam(at) return emu.read(at,emu.memType.nesSpriteRam) end
  for _,o in ipairs(dmaBody) do
   assert(oam(o.slot)==o.y and oam(o.slot+1)==o.tile and
          oam(o.slot+2)==o.attr and oam(o.slot+3)==o.x,'Actual hardware OAM contains DK Jr body')
  end
  body.hardware_matches=body.hardware_matches+1
  dmaBody=nil
 end
'''+anchor)
    anchor="    shot('dkjr-gameplay')"
    assert body.count(anchor)==1
    body=body.replace(anchor,'''    assert(body.first and body.first.offset_before==0 and body.first.offset_after>0,
           'Initial logical zero reserves the first DK Jr body')
    assert(body.writes>0 and body.hardware_matches>0,'Native DK Jr reaches visible hardware OAM')
'''+anchor)
    return 'local C='+lua(config)+'\n'+body


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--oam',type=Path,required=True)
    parser.add_argument('--cpu-proof',type=Path,required=True)
    args=parser.parse_args()
    assert sha(CURRENT)==sha(NIGHTLY)==PIN
    frontend,oam,cpu=(json.loads(path.read_text()) for path in (FRONTEND,args.oam,args.cpu_proof))
    assert frontend['passed'] and oam['passed'] and cpu['passed']
    assert oam['base_SHA256']==frontend['expected_memory_only_SHA256']
    assert cpu['base_SHA256']==oam['base_SHA256']
    assert cpu['memory_only_SHA256']==oam['memory_only_hashes'][oam['base_SHA256']]
    for proof in (frontend,oam,cpu):
        for path,digest in proof.get('bindings',{}).items():
            bound=R/path
            if proof is frontend and bound.resolve()==NIGHTLY.resolve():
                # The original delivery path has since advanced. Authenticate
                # its former bytes using the preserved exact candidate.
                assert digest==frontend['parent_SHA256']
                bound=FRONTEND_BASE
            assert sha(bound)==digest,path
    raw=bytearray(CURRENT.read_bytes())
    seen=set()
    apply(raw,oam['patches'],seen)
    assert hashlib.sha256(raw).hexdigest()==oam['memory_only_hashes'][PIN]
    apply(raw,frontend['patches'],seen)
    args.output.mkdir()
    rom=args.output/'dkjr-private.nes'
    rom.write_bytes(raw)
    for suffix in ('.lbl','.dbg'):
        shutil.copyfile(CURRENT.with_suffix(suffix),rom.with_suffix(suffix))
    symbols=json.loads(LAYOUT.read_text())['labels']
    cookie,=[row['new_hex'] for row in oam['patches'] if row.get('physical_PRG')==65]
    config=dict(pin=sha(rom),main=symbols['DkNativeMain'],draw=oam['labels']['DkNativeDraw'],
                cookie=list(bytes.fromhex(cookie)))
    prepare(args.output/'native',rom,observer(config),[Path(__file__),CURRENT,NIGHTLY,SOURCE,LAYOUT,FRONTEND,args.oam,args.cpu_proof],
            expected=sha(rom),timeout=120,allow_interactive=True,
            scope='Private controller-only DK Jr menu and motion. Initial logical slot and physical OAM DMA checked.')


if __name__=='__main__':
    main()
