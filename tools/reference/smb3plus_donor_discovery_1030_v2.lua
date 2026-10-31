-- Original donor discovery; controller input and read-only snapshots.
local frame = 0
local samples = assert(io.open(OUTPUT .. 'observations.csv', 'w'))
samples:write('frame,ram07e2,ram0726,ram0090,ram00a2,buttons\n')
local function read(address)
    return emu.read(address, emu.memType.nesDebug)
end
local function dump(name, size, memory, base)
    local file = assert(io.open(OUTPUT .. name, 'wb'))
    local bytes = {}
    for offset = 0, size - 1 do
        bytes[#bytes + 1] = string.char(emu.read((base or 0) + offset, memory))
    end
    file:write(table.concat(bytes))
    file:close()
end
emu.addEventCallback(function()
    frame = frame + 1
    local start = (frame >= 65 and frame <= 68) or (frame >= 180 and frame <= 183)
    emu.setInput({start = start}, 0, 0)
    if frame % 30 == 0 then
        samples:write(table.concat({frame, read(0x7e2), read(0x726), read(0x90),
            read(0xa2), start and 16 or 0}, ',') .. '\n')
        samples:flush()
    end
    if frame == 120 or frame == 240 or frame == 360 then
        local file = assert(io.open(OUTPUT .. 'frame' .. frame .. '.png', 'wb'))
        file:write(emu.takeScreenshot())
        file:close()
        dump('ram' .. frame .. '.bin', 2048, emu.memType.nesDebug)
    end
    if frame == 360 then
        samples:close()
        dump('palette.bin', 32, emu.memType.nesPpuDebug, 0x3f00)
        emu.stop(0)
    end
end, emu.eventType.startFrame)
