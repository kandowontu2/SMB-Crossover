"""Pack native grayscale roster portraits and the dedicated select nametable."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]


def tile(pixels):
    return bytes(sum(((pixels[y][x] >> plane) & 1) << (7-x) for x in range(8))
        for plane in range(2) for y in range(8))


def main():
    chr_data = bytearray((ROOT/'chr/mmc5/bg_ground.chr').read_bytes())
    nt = bytearray([0x24]*960+[0]*64)
    def text(row, column, value):
        chars = {' ':0x24, '-':0x28, '/':0x2d, '.':0x2c}
        for i, char in enumerate(value):
            nt[row*32+column+i] = chars[char] if char in chars else ord(char)-ord('A')+10
    text(3, 5, 'SELECT YOUR CHARACTER')
    text(5, 8, 'SMB CROSSOVER')
    text(27, 3, 'D-PAD CHOOSE  A/START PLAY')
    text(28, 12, 'B - BACK')
    mario = Image.new('RGBA', (16,16))
    source = (ROOT/'chr/mmc3/sprites_mario.chr').read_bytes()[2048:3072]
    colors = [(0,0,0,0),(182,40,0,255),(248,184,120,255),(170,90,0,255)]
    for half in range(2):
        for y in range(16):
            for x in range(8):
                base = half*32+(y//8)*16+y%8
                color = ((source[base]>>(7-x))&1) | (((source[base+8]>>(7-x))&1)<<1)
                mario.putpixel((half*8+x,y),colors[color])
    names = ['HAIR-STAND','SAMUS-0-STAND','BILL-0-STAND','LINK-0-STAND','SIMON-0-STAND']
    names += [role+'-0-STAND' for role in ['PIT','RYGAR','SCROOGE','BASS','RYU','SOPHIA']]
    pictures = [mario]+[Image.open(ROOT/f'build/reference-frames/{name}.png').convert('RGBA') for name in names]
    # Repeated transparent tiles and shared shapes let all twelve portraits
    # fit in one 4 KiB background without sacrificing the native font.
    unique={bytes(16):0x24}
    next_tile=0x40
    for index, picture in enumerate(pictures):
        picture = picture.crop(picture.getbbox())
        assert picture.width <= 32 and picture.height <= 40
        canvas = Image.new('RGBA', (32,40))
        canvas.alpha_composite(picture, ((32-picture.width)//2,40-picture.height))
        for ty in range(5):
            for tx in range(4):
                values = []
                for y in range(8):
                    row = []
                    for x in range(8):
                        r,g,b,a = canvas.getpixel((tx*8+x,ty*8+y))
                        shade = 1 if .299*r+.587*g+.114*b < 95 else 2 if .299*r+.587*g+.114*b < 200 else 3
                        row.append(shade if a>=128 else 0)
                    values.append(row)
                data=tile(values)
                if data not in unique:
                    assert next_tile<256,'Menu background CHR capacity'
                    unique[data]=next_tile;next_tile+=1
                number=unique[data]
                chr_data[number*16:(number+1)*16] = data
                nt[(6+(index//6)*6+ty)*32+1+(index%6)*5+tx] = number
    chr_data[0x3f*16:0x40*16] = tile([[3 if 3-y<=x<=4+y and y<=3 else 0 for x in range(8)] for y in range(8)])
    (ROOT/'chr/characters/crossover-menu.chr').write_bytes(chr_data)
    (ROOT/'chr/raw/character-select.bin').write_bytes(nt)
    print('Menu: twelve 32x40 portraits, native font,',next_tile-0x40,'unique portrait tiles, 4 KiB CHR')


if __name__ == '__main__':
    main()
