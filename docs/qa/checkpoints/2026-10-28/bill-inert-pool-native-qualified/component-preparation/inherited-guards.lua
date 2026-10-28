local saved=nil
local function store(pc,target)return emu.read(pc,emu.memType.nesDebug)==0x8d and emu.read(pc+1,emu.memType.nesDebug)==target%256 and emu.read(pc+2,emu.memType.nesDebug)==target//256 end
local function window(pc,target,shadow)
 if store(pc,target)then return store(pc-3,shadow)or(emu.read(pc-2,emu.memType.nesDebug)==0xa9 and store(pc-5,shadow))end
 return emu.read(pc,emu.memType.nesDebug)==0xa9 and store(pc+2,target)and store(pc-3,shadow)
end
hook('NonMaskableInterrupt',function()
 if not entered or done then return end
 local s=emu.getState();local sp=s['cpu.sp'];local pc=emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+3)%256,emu.memType.nesDebug)
 saved={a=bank(0xa000),c=bank(0xc000),sa=r('CurrentBank')&127,sc=r('CurrentBankC')&127,sp=sp,cpu_a=s['cpu.a'],fields={}}
 saved.wa=saved.a~=saved.sa and window(pc,0x5115,L.CurrentBank);saved.wc=saved.c~=saved.sc and window(pc,0x5116,L.CurrentBankC)
 for _,a in ipairs(C.smc_fields)do saved.fields[#saved.fields+1]=emu.read(a,emu.memType.nesDebug)end;nmis=nmis+1
end)
hook('NmiReturn',function()
 if not saved then return end
 assert(bank(0xa000)==(saved.wa and saved.sa or saved.a)and bank(0xc000)==(saved.wc and saved.sc or saved.c),'NMI actual foreground banks')
 assert(r('CurrentBank')&127==saved.sa and r('CurrentBankC')&127==saved.sc,'NMI shadow banks')
 assert(emu.getState()['cpu.sp']==saved.sp and emu.getState()['cpu.a']==saved.cpu_a,'NMI stack/register restore')
 for i,a in ipairs(C.smc_fields)do assert(emu.read(a,emu.memType.nesDebug)==saved.fields[i],'Five SMC operands restored')end
 saved=nil
end)
emu.addMemoryCallback(function()if entered and not done then assert(emu.getState()['cpu.sp']>=128,'Native lower stack guard')end end,emu.callbackType.write,0x17f)
emu.addMemoryCallback(function(a,v)
 if entered then local s=emu.getState();apuWrites=apuWrites+1;apu:write(table.concat({wall,updates,index,phase,a,v,s['cpu.pc'],bank(s['cpu.pc']),s['cpu.cycleCount']},',')..'\n')end
end,emu.callbackType.write,0x4000,0x4017)
