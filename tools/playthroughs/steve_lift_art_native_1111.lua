local liftArtDma,liftArtPng=0,false
local liftArtPending={}
local liftChrHigh,liftChrMode=0,0
local liftChrBanks={}
emu.addMemoryCallback(function(address,value)
  if address==0x5130 then liftChrHigh=value&3
  elseif address==0x5101 then liftChrMode=value&3
  elseif address>=0x5120 and address<=0x5127 then
    liftChrBanks[address-0x5120]=value+256*liftChrHigh
  end
end,emu.callbackType.write,0x5101,0x5130)
local function liftBase64(bytes)
  local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
  local out={}
  for i=1,#bytes,3 do
    local a,b,c=bytes:byte(i),bytes:byte(i+1),bytes:byte(i+2)
    local n=(a<<16)|((b or 0)<<8)|(c or 0)
    out[#out+1]=alphabet:sub((n>>18)+1,(n>>18)+1)
    local j=(n>>12)&63;out[#out+1]=alphabet:sub(j+1,j+1)
    j=(n>>6)&63;out[#out+1]=b and alphabet:sub(j+1,j+1) or '='
    j=n&63;out[#out+1]=c and alphabet:sub(j+1,j+1) or '='
  end
  return table.concat(out)
end
emu.addMemoryCallback(guard(function(_,value)
  if value~=2 or phase~='companion-route' or work(2,STEVE_LIFT_STATE)<4 then return end
  liftArtPending={}
  for i=0,255 do liftArtPending[i+1]=read(0x200+i) end
end),emu.callbackType.write,0x4014)
local function observeLiftArt()
  if #liftArtPending>0 then
    for i,value in ipairs(liftArtPending) do
      assert(emu.read(i-1,emu.memType.nesSpriteRam)==value,'Complete original lift DMA')
    end
    liftArtDma=liftArtDma+1;liftArtPending={}
  end
  if not liftArtPng and work(2,STEVE_LIFT_STATE)==7 and read(0xbd)==40 and liftArtDma>2 then
    print('SMB_NATIVE_IMAGE '..liftBase64(emu.takeScreenshot()))
    liftArtPng=true
    assert(liftChrMode==3 and liftChrBanks[0]==339,
      string.format('Physical sprite bank mode %d page %s',liftChrMode,tostring(liftChrBanks[0])))
    -- MMC5 switches its generic PPU view between background and sprite
    -- banks during rendering. Observe the actual sprite-register writes;
    -- a frame-end nesPpuMemory read does not identify the sprite bank.
    -- Mesen2/Core/NES/Mappers/Nintendo/MMC5.h: UpdateChrBanks.
  end
end
