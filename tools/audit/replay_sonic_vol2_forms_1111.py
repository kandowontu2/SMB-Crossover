"""Replay each Sonic form from the roster to the native World 1-2."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_sonic_ring_physical_1110 as Original
from prepare_sonic_vol2_art_1111 import BODY_TILES, NORMAL_CHR, SUPER_CHR, SHEET, body_cells, decode_sheet
from run_stdout_mesen_1110 import R, run


PORTRAIT = R / 'tools/playthroughs/sonic_static_portrait_stdout_1110.lua'
FORMS = {
    'sonic': (3, 'SONIC', NORMAL_CHR, 0x12),
    'super': (4, 'SUPER SONIC', SUPER_CHR, 0x28),
}


def edit(source, before, after):
    assert source.count(before) == 1, before
    return source.replace(before, after)


def portrait(form, body_hex):
    selects, label, page, shade = FORMS[form]
    source = PORTRAIT.read_text(encoding='utf-8')
    source = edit(source, 'local menuProof, livesProof', f'''local menuProof, livesProof
local page,shade,selects,label={page},{shade},{selects},"{label}"
local expectedArt="{body_hex}"
local function labelMatches()
  local letters={{}}
  for i=0,15 do
    local tile=emu.read(0x2328+i,emu.memType.nesPpuDebug)
    letters[#letters+1]=tile>=10 and tile<=35 and string.char(tile+55) or ' '
  end
  return table.concat(letters):match('^%s*(.-)%s*$')==label
end
local function artMatches()
  local hex={{}}
  for _,tile in ipairs({{0,2,32,34}}) do
    for i=0,31 do
      local pixel=emu.read(page*1024+tile*16+i,emu.memType.nesChrRom)
      hex[#hex+1]=string.format('%02x',pixel)
    end
  end
  return table.concat(hex)==expectedArt
end''')
    source = edit(source, 'chrPage ~= 224', 'chrPage ~= page')
    source = edit(source, 'colors[2] ~= 0x12', 'colors[2] ~= shade')
    source = edit(source, 'if count ~= 4 then', 'if count ~= 4 or not artMatches() then')
    source = edit(source, 'local cell = expected[read(offset+1)]',
                  'local cell = expected[emu.read(offset-0x200+1,emu.memType.nesSpriteRam)]')
    source = edit(source, 'if cell and read(offset+3) == cell[1] and read(offset) == cell[2]\n'
                          '        and read(offset+2) & 0x43 == 0 then\n'
                          '      expected[read(offset+1)] = nil',
                  '''if cell and emu.read(offset-0x200+3,emu.memType.nesSpriteRam) == cell[1]
        and emu.read(offset-0x200,emu.memType.nesSpriteRam) == cell[2]
        and emu.read(offset-0x200+2,emu.memType.nesSpriteRam) & 0x43 == 0 then
      expected[emu.read(offset-0x200+1,emu.memType.nesSpriteRam)] = nil''')
    source = edit(source, '"CHR_page":224,"palette":[22,18,48]}\',frame,x,y)',
                  '"CHR_page":%d,"palette":[22,%d,48]}\',frame,x,y,page,shade)')
    source = edit(source, 'for _=1,3 do press(32) end', 'for _=1,selects do press(32) end')
    source = edit(source, 'read(0x5ffe)==3,\'Sonic selection\'', 'read(0x5ffe)==selects,label')
    source = edit(source, 'menuProof=proofAt(120,160);return menuProof',
                  'menuProof=proofAt(120,160);return menuProof and labelMatches()')
    return source


def stage(form, cookie):
    selects, label, page, shade = FORMS[form]
    source = Original.STAGE.read_text(encoding='utf-8')
    assert sha256(Original.STAGE.read_bytes()).hexdigest() == Original.STAGE_PIN
    source = edit(source, Original.OLD_COOKIE.decode(), cookie)
    source = edit(source, 'local frame,updates,completed,polls,activeUpdates=0,0,0,0,0',
                  f'''local frame,updates,completed,polls,activeUpdates=0,0,0,0,0
local activePage,shade,selects={page},{shade},{selects}
local chrUpper,bodyPage,bodyFrames=0,-1,0''')
    source = edit(source, "character='Sonic SMS'", f"character='{label}'")
    source = edit(source, 'native_flag=flag,native_castle=castle,native_entrance=entrance,active_1_2=active12,',
                  'native_flag=flag,native_castle=castle,native_entrance=entrance,active_1_2=active12,'
                  'body_frames=bodyFrames,body_chr_page=activePage,')
    source = edit(source, 'for _=1,3 do press(32)end', 'for _=1,selects do press(32)end')
    source = edit(source, "r('FmAlts')==3,'Gimmick Select3 Sonic'", "r('FmAlts')==selects,'Sonic form selection'")
    source = edit(source, 'index=25,Select=3,raw=43', 'index=25,Select=selects,raw=43')
    source = edit(source, 'local function install()',
                  '''local function verifyBody()
 if not active(state()) or bodyPage~=activePage then return end
 if selects==4 then assert(r('FmAlts')==4,'Super Sonic form was lost') end
 if emu.read(0x3f12,emu.memType.nesPpuDebug)~=shade then return end
 local cells={}
 for i=0,252,4 do
  local y=emu.read(i,emu.memType.nesSpriteRam)
  local tile=emu.read(i+1,emu.memType.nesSpriteRam)
  local attr=emu.read(i+2,emu.memType.nesSpriteRam)
  if y>=32 and y<224 and attr&3==0 and (tile==0 or tile==2 or tile==32 or tile==34) then
   cells[tile]={y,emu.read(i+3,emu.memType.nesSpriteRam)}
  end
 end
 local a,b,c,d=cells[0],cells[2],cells[32],cells[34]
 if a and b and c and d and a[1]==b[1] and c[1]==d[1] and c[1]-a[1]==16
    and a[2]==c[2] and b[2]==d[2] and math.abs(a[2]-b[2])==8 then
  bodyFrames=bodyFrames+1
 end
end
local function install()
 emu.addMemoryCallback(guarded('CHR upper',function(_,v)chrUpper=v&3 end),emu.callbackType.write,0x5130)
 emu.addMemoryCallback(guarded('body page',function(_,v)bodyPage=v+256*chrUpper end),emu.callbackType.write,0x5120)''')
    source = edit(source, 'local count=completed-priorCompleted',
                  'if gameplay then verifyBody() end\n  local count=completed-priorCompleted')
    source = edit(source, "assert(flag and castle and entrance,'Native flag/castle/entrance witnesses')",
                  "assert(flag and castle and entrance,'Native flag/castle/entrance witnesses')\n"
                  "  assert(bodyFrames>=8,'Missing selected-form hardware body frames')")
    return source


def rings(form):
    selects, label, page, _ = FORMS[form]
    source = Original.RING.read_text(encoding='utf-8')
    source = edit(source, 'bodyPage~=224', f'bodyPage~={page}')
    source = edit(source, 'local at=224*1024+s.tile*16', f'local at={page}*1024+s.tile*16')
    source = edit(source, 'for _=1,3 do press(32) end', f'for _=1,{selects} do press(32) end')
    source = edit(source, "native('alternate')==3,'Mr. Gimmick Select3 Sonic'",
                  f"native('alternate')=={selects},'{label} selection'")
    return edit(source, 'menu={slot=25,select=3,raw=43}', f'menu={{slot=25,select={selects},raw=43}}')


def mushroom(form, pin, cookie):
    selects, label, _, _ = FORMS[form]
    source = Original.power_controller(pin, cookie.encode())
    source = edit(source, 'for _=1,3 do press(32)end', f'for _=1,{selects} do press(32)end')
    source = edit(source, "r('FmAlts')==3,'Gimmick Select3 Sonic'",
                  f"r('FmAlts')=={selects},'{label} selection'")
    if form == 'super':
        source = edit(source, 'if ready and epoch-jumpStarted>24 then\n   for _,ahead',
                      '''if ready and phase=='resume' and goomba and epoch-jumpStarted>24 then
   requestJump('recovery_Goomba',s)
  elseif ready and epoch-jumpStarted>24 then
   for _,ahead''')
    return edit(source, 'index=25,Select=3,raw=43', f'index=25,Select={selects},raw=43')


def replays(rom, output, *, forms, tests=('portrait', 'stage', 'rings', 'mushroom')):
    assert output.resolve().is_relative_to(R / 'build')
    data = rom.read_bytes()
    pin = sha256(data).hexdigest()
    cookie = data[1034472:1034488].hex()
    art = body_cells(decode_sheet(SHEET.read_bytes()))
    assert len(art[0]) == len(art[1]) == len(BODY_TILES)
    script = output / 'controller.lua'
    output.mkdir(parents=True, exist_ok=True)
    results = {}
    for form in forms:
        controllers = {
            'portrait': portrait(form, b''.join(art[form == 'super']).hex()),
            'stage': stage(form, cookie),
            'rings': rings(form),
            'mushroom': mushroom(form, pin, cookie),
        }
        for name in tests:
            source = controllers[name]
            script.write_text(source, encoding='utf-8', newline='\n')
            q = run(script, rom, output / 'capture', pin, 200,
                    extra_env={'SMB_STDOUT_IMAGES': '0', 'SMB_SONIC_COOKIE': cookie})
            result = q['receipt']
            proof = dict(form=form, test=name, passed=q['passed'], receipt_SHA256=q['receipt_SHA256'],
                         physical_frames=result.get('physical_frames'), body_frames=result.get('body_frames'),
                         menu=result.get('menu'), lives=result.get('lives'),
                         reason=result.get('reason'), terminal=result.get('terminal'))
            print(json.dumps(proof, sort_keys=True), flush=True)
            assert q['passed'], (form, name, result.get('reason'))
            results[(form, name)] = q
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--form', choices=(*FORMS, 'both'), default='both')
    parser.add_argument('--tests', nargs='+', choices=('portrait', 'stage', 'rings', 'mushroom'),
                        default=('portrait', 'stage', 'rings', 'mushroom'))
    args = parser.parse_args()
    forms = tuple(FORMS) if args.form == 'both' else (args.form,)
    replays(args.rom.resolve(), args.output.resolve(), forms=forms, tests=args.tests)


if __name__ == '__main__':
    main()
