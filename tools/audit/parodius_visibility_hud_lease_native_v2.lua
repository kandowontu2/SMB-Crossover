-- Additional all-life displayed label/font pairing. Existing guards stay exact.
-- Current foreground lease RAM is logged, never substituted for displayed PPU.
local PLC=assert(PARODIUS_VISIBILITY)
local PLF=assert(io.open(PLC.output..'hud-lease-frames.jsonl','w'))
local PLchecks,PLcustom,PLblank=0,0,0
local function pljson(v)
 if type(v)=='table'then local t={};if#v>0 then for _,x in ipairs(v)do t[#t+1]=pljson(x)end;return'['..table.concat(t,',')..']'end;for k,x in pairs(v)do t[#t+1]=string.format('%q',tostring(k))..':'..pljson(x)end;return'{'..table.concat(t,',')..'}'
 elseif type(v)=='string'then return string.format('%q',v)elseif v==nil then return'null'else return tostring(v)end
end
PARODIUS_HUD_VISIBLE_PAIR_OK=function(q,wanted)
 local equal=#q.labels==#wanted;local blank=#q.labels==28
 for i,v in ipairs(q.labels)do equal=equal and v==wanted[i];blank=blank and v==36 end
 if equal and q.font==395+q.variant then return true,'custom-pair'end
 if blank and q.font==0 then return true,'native-blank'end
 return false,'Displayed source labels and actual hardware font are unpaired'
end
emu.addEventCallback(function()
 local function read(n)return emu.read(assert(PLC.hud_ram[n],n),emu.memType.nesDebug)end
 local s=emu.getState();if read('SelectedCharacter')~=18 or read('VvVariant')~=PLC.variant or PLC.variant==0 or read('OperMode')~=1 or read('OperMode_Task')~=3 or read('DisableScreenFlag')~=0 or not s['ppu.mask.backgroundEnabled']then return end
 local q={ppu={frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],cycle=s['ppu.cycle'],cpu=s['cpu.cycleCount']},variant=read('VvVariant'),mode=read('CrossoverBehaviorVersion'),engine=read('GameEngineSubroutine'),font=s['mapper.chrBanks8'],labels={},active=read('InvHudActive'),upper=read('X5HudChrUpper'),physical=read('InvHudPhysical'),generation=PARODIUS_LIFECYCLE_GENERATION()}
 for i=0,27 do q.labels[#q.labels+1]=emu.read(0x2022+i,emu.memType.nesPpuDebug)end
 local _,p,d=PARODIUS_PUBLICATION_SNAPSHOT();q.displayed_publication=d and d.publication.id;q.displayed_source_generation=d and d.publication.generation
 q.passed,q.classification=PARODIUS_HUD_VISIBLE_PAIR_OK(q,assert(PLC.hud_labels[tostring(PLC.variant)]))
 PLF:write(pljson(q)..'\n');PLF:flush()
 if not q.passed then local f=assert(io.open(PLC.output..'first-HUD-lease-pair-mismatch.json','w'));f:write(pljson(q));f:close()end
 assert(q.passed,'Actual all-life displayed HUD source/font pair')
 PLchecks=PLchecks+1;if q.classification=='custom-pair'then PLcustom=PLcustom+1 else PLblank=PLblank+1 end
end,emu.eventType.startFrame)
PARODIUS_HUD_LEASE_FINISH=function()
 if emu.getState()['ppu.frameCount']~=PLC.limit then return end
 assert(PLchecks>=45 and PLcustom>=45,'Meaningful all-life displayed HUD pairs')
 local f=assert(io.open(PLC.output..'hud-lease-native-result.json','w'));f:write(pljson({passed=true,ROM_sha256=PLC.ROM_sha256,visible_pair_checks=PLchecks,custom_pair_checks=PLcustom,native_blank_checks=PLblank,no_emulated_writes=true,limits='Read-only actual hardware font/nametable pairing at each observed gameplay start. Existing scroll/RGB/native lifecycle guards remain independent; source exactness does not certify tiny-font readability.'}));f:close();PLF:close()
end
