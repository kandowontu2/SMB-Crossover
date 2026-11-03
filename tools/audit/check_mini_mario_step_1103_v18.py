"""Original C state functions against private compiled Mini world Step.

Legal isolated fixtures have no scripts, power actors, swim, vines or moving
platforms. Native sampler sees exactly the same 16px terrain as source tile_at.
"""
from pathlib import Path
from zipfile import ZipFile
import json,random,re,subprocess,sys
from py65.devices.mpu6502 import MPU
sys.path.insert(0,str(Path(__file__).resolve().parent))
import prepare_mini_mario_world_1103_v11 as W
import prepare_mini_mario_step_1103_v16 as P
R,O=W.R,W.O

def function(s,name):
    m=re.search(r'void '+name+r'\(void\) BANKED\s*\{',s);assert m,name
    n=m.end();depth=1
    while depth:
        if s[n]=='{':depth+=1
        if s[n]=='}':depth-=1
        n+=1
    return s[m.start():n]

PRE=r'''
#include <stdint.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <fcntl.h>
#include <io.h>
typedef uint8_t UBYTE;typedef int8_t BYTE;typedef uint16_t UWORD;typedef int16_t WORD;
#define BANKED
#define TRUE 1
#define FALSE 0
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#define CLAMP(a,b,c) MIN(MAX(a,b),c)
#define SCREEN_WIDTH 160
#define INPUT_LEFT (held&2)
#define INPUT_RIGHT (held&1)
#define INPUT_DOWN (held&4)
#define INPUT_UP (held&8)
#define INPUT_PLATFORM_JUMP (held&128)
#define INPUT_PLATFORM_RUN (held&64)
#define INPUT_PRESSED(v) ((v)&~previous)
#define COLLISION_TOP 1
#define COLLISION_BOTTOM 2
#define COLLISION_LEFT 4
#define COLLISION_RIGHT 8
#define TILE_PROP_LADDER 16
#define DIR_DOWN 0
#define DIR_RIGHT 1
#define DIR_UP 2
#define DIR_LEFT 3
#define ANIM_JUMP_LEFT 0
#define ANIM_JUMP_RIGHT 2
#define STATE_DEFAULT 0
#define STATE_ATTACK 1
#define STATE_CROUCH 2
#define STATE_CROUCHATTACK 3
#define STATE_SKID 4
#define STATE_CLIMB 5
#define STATE_SWIM 6
#define VAR_MARIOSTATUS_0 0
#define VAR_CANSWIM 1
#define VAR_HASYOSHI 2
#define VAR_FRAMECOINS 3
#define VAR_PLAYER_IFRAMES 4
#define FELL_IN_PIT_EVENT 5
#define ENTER_DOWN_PIPE_EVENT 2
#define ENTER_RIGHT_PIPE_EVENT 3
#define ENTER_LEFT_PIPE_EVENT 6
#define COIN_COLLECTED_EVENT 0
#define MAX_ACTORS 1
#define VRAM_OFFSET(x,y) (0)
typedef struct{WORD x,y;}point16_t;
typedef struct{BYTE left,right,top,bottom;}bounding_box_t;
typedef struct actor_t{point16_t pos;bounding_box_t bounds;struct actor_t*prev;UBYTE disabled,collision_enabled,collision_group,dir,anim_tick,active;struct{UBYTE bank;void*ptr;}sprite,script;UBYTE animations[32];}actor_t;
actor_t actors[1];
#define PLAYER actors[0]
struct{UBYTE script_bank;void*script_addr;}state_events[24],specific_events[9];
enum{FALL_INIT,FALL_STATE,FALL_END,GROUND_INIT,GROUND_STATE,GROUND_END,CROUCH_INIT,CROUCH_STATE,CROUCH_END,SKID_INIT,SKID_STATE,SKID_END,JUMP_INIT,JUMP_STATE,JUMP_END,CLIMB_INIT,CLIMB_STATE,CLIMB_END,BLANK_INIT,BLANK_STATE,BLANK_END,SWIM_INIT,SWIM_STATE,SWIM_END};
WORD pl_vel_x,pl_vel_y,deltaX,deltaY,jump_reduction_val,jump_reduction,jump_per_frame=12288,boost_val=32;
WORD plat_min_vel=256,plat_walk_vel=3665,plat_run_vel=5602,plat_climb_vel=4096,plat_walk_acc=128,plat_run_acc=256,plat_dec=256,plat_jump_vel=12288,plat_grav=2048,plat_hold_grav=512,plat_max_fall_vel=8192,plat_air_dec=208,plat_turn_acc=712,plat_jump_min=0,plat_float_grav=912;
UBYTE plat_hold_jump_max=1,plat_coyote_max=2,plat_buffer_max=2,plat_run_boost=32,plat_float_input=0,plat_turn_control=0,plat_drop_through=0,plat_mp_group=8;
UBYTE plat_state,que_state,nocollide,ct_val,jb_val,hold_jump_val,actor_attached,enemy_bounce,grounded,current_vine_tile_x,crouched,que_attacking,stat_attacking,dj_val;
WORD mp_last_x,mp_last_y;actor_t*last_actor;
BYTE run_stage,last_wall,col,camera_deadzone_x,plat_camera_deadzone_x=4;
WORD edgeLeft,edgeRight,*edge_left=&edgeLeft,*edge_right=&edgeRight,scroll_y;
WORD script_memory[8];UBYTE held,previous,sram_map_data[1],fixture;
#define script_execute(...) ((void)0)
#define load_animations(...) ((void)0)
#define trigger_activate_at_intersection(...) ((void)0)
#define player_register_collision_with(...) ((void)0)
#define bb_intersects(...) 0
#define actor_behavior_update() ((void)0)
#define check_player_metatiles_entered() ((void)0)
void actor_set_dir(actor_t*a,UBYTE d,UBYTE moving){a->dir=d;}
void actor_set_anim(actor_t*a,UBYTE anim){}
void actor_set_anim_idle(actor_t*a){}
void climb_state(void){}void swim_state(void){}
void on_player_metatile_collision(UBYTE x,UBYTE y,UBYTE dir){}
void reset_collision_cache(UBYTE dir){}
int solid(int x,int y){
 if(y<32||y>=240)return 0;
 int bx=x>>4,by=y>>4;
 if(by>=13 && !(fixture==3&&bx>=5&&bx<=6))return 1;
 if(fixture==1&&bx==6&&by>=8)return 1;
 if(fixture==2&&by==9&&bx>=3&&bx<=6)return 1;
 if(fixture==4&&bx>=6&&by>=11)return 1;
 return 0;
}
UBYTE tile_at(UBYTE x,UBYTE y){return solid(x*8,y*8)?15:0;}
void ground_state(void);void crouch_state(void);void jump_state(void);void fall_state(void);
'''

POST=r'''
unsigned char m[129];
unsigned rd(unsigned p){return m[p]|m[p+1]<<8;}
void wr(unsigned p,unsigned v){m[p]=v;m[p+1]=v>>8;}
void step(void){
 pl_vel_x=(WORD)rd(0);deltaX=(WORD)rd(2);que_attacking=m[5];run_stage=m[7];
 pl_vel_y=(WORD)rd(32);deltaY=(WORD)rd(34);hold_jump_val=m[36];enemy_bounce=m[38];nocollide=m[39];que_state=m[40];actor_attached=m[41];
 ct_val=m[65];jb_val=m[66];crouched=m[67];script_memory[0]=m[68];PLAYER.dir=m[69];
 held=m[72];previous=m[73];PLAYER.pos.x=rd(80);PLAYER.pos.y=rd(82);PLAYER.bounds.left=m[84];PLAYER.bounds.right=m[85];PLAYER.bounds.top=m[86];PLAYER.bounds.bottom=m[87];
 edgeLeft=(WORD)rd(88)>>4;edgeRight=((WORD)rd(90)>>4)-SCREEN_WIDTH+16;
 platform_update();
 wr(0,pl_vel_x);wr(2,deltaX);m[6]=PLAYER.anim_tick;m[7]=run_stage;wr(32,pl_vel_y);wr(34,deltaY);m[36]=hold_jump_val;m[38]=enemy_bounce;m[39]=nocollide;m[40]=que_state;m[41]=actor_attached;
 m[4]=((held&2)>>1)|((held&1)<<1)|((held&64)>>4);m[37]=((held&128)>>7)|((held&8)>>2);
 m[64]=plat_state;m[65]=ct_val;m[66]=jb_val;m[67]=crouched;m[69]=PLAYER.dir;m[73]=held;m[74]=held&~previous;
 wr(80,PLAYER.pos.x);wr(82,PLAYER.pos.y);m[86]=PLAYER.bounds.top;
}
int main(){_setmode(_fileno(stdin),_O_BINARY);_setmode(_fileno(stdout),_O_BINARY);while(fread(m,1,129,stdin)==129){fixture=fgetc(stdin);step();fwrite(m,1,129,stdout);}return 0;}
'''

def csource():
    S=W.sources();a=S['Mini/plugins/PlatformerPlus/engine/src/states/platform.c'].decode();b=S['Mini/plugins/PlatformerPlus/engine/src/states/playerstates.c'].decode()
    names=[('ground_state',b),('crouch_state',b),('jump_state',b),('fall_state',a),('platform_update',a)]
    bodies=[function(s,n)for n,s in names]
    return PRE+'\n'+'\n\n'.join(bodies)+'\n'+POST,{n:W.sha(t.encode())for(n,_),t in zip(names,bodies)}

def compile_c():
    source,binds=csource();p=O/'original-world-v18.c';p.write_text(source)
    r=subprocess.run(['C:/Strawberry/c/bin/gcc.exe','-std=c99','-O2','-fwrapv',str(p),'-o',str(O/'original-world-v18.exe')],capture_output=True,text=True)
    assert r.returncode==0,r.stderr
    return binds

def initial(state=3,x=48*16,y=200*16-1,held=0,tier=0):
    m=bytearray(129);m[40]=state;m[43]=2;m[69]=1;m[72]=held;m[84:88]=bytes([1,6,1 if tier==0 else 249,7]);m[68]=tier
    m[80:82]=x.to_bytes(2,'little');m[82:84]=y.to_bytes(2,'little');m[90:92]=(192*16).to_bytes(2,'little');return m

def solid(f,x,y):
    if y<32 or y>=240:return False
    bx,by=x>>4,y>>4
    return (by>=13 and not(f==3 and 5<=bx<=6))or(f==1 and bx==6 and by>=8)or(f==2 and by==9 and 3<=bx<=6)or(f==4 and bx>=6 and by>=11)

def memory(data,L,f):
    m=MPU();m.memory[0xa000:0xa000+len(data)]=data
    attrs=(R/'build/mini-mario-native-tile-1103-v13/native-attributes.bin').read_bytes();m.memory[0xd000:0xd100]=attrs
    tile=next(i for i,a in enumerate(attrs)if a&3==1 and i!=0x26)
    for page in range(2):
        base=0x300+page*0xd0
        for y in range(13):
            for x in range(16):m.memory[base+y*16+x]=tile if solid(f,page*256+x*16,y*16+32)else 0
    return m

def call(m,pc):
    m.pc=pc;m.sp=0xf0;m.memory[0x1f1]=0xfd;m.memory[0x1f2]=0x7f
    start=m.processorCycles;n=0
    while m.pc!=0x7ffe:
        m.step();n+=1
        assert n<50000,(hex(m.pc),m.memory[0xc240:0xc281])
    return m.processorCycles-start

CHECK=[*range(4),6,7,*range(32,42),64,65,66,67,69,73,74,80,81,82,83,86]

def main():
    binds=compile_c();data=(O/'world-step-v16.bin').read_bytes();receipt=json.loads((O/'world-step-v16.json').read_text());L=receipt['exports']
    cases=[];rng=random.Random(41)
    for state in [0,1,3,4,6,7,9,10,12,13]:
        for fixture in range(5):
            for _ in range(16):
                tier=rng.randrange(2);m=initial(state,rng.randrange(40*16,112*16),rng.randrange(112*16,207*16),rng.choice([0,1,2,4,0x41,0x42,0x80,0x81,0x82]),tier)
                m[0:2]=(rng.randrange(-5602,5603)&65535).to_bytes(2,'little');m[32:34]=(rng.randrange(-12288,8193)&65535).to_bytes(2,'little');m[36]=rng.randrange(2);m[65]=rng.randrange(3);m[66]=rng.randrange(3);m[67]=int(state in(6,7));m[73]=rng.choice([0,m[72]])
                if m[67]:m[86]=1
                cases.append((m,fixture))
    raw=b''.join(bytes(m)+bytes([f])for m,f in cases)
    r=subprocess.run([str(O/'original-world-v18.exe')],input=raw,capture_output=True);assert r.returncode==0
    assert len(r.stdout)==129*len(cases)
    cycles=[]
    for i,(v,f)in enumerate(cases):
        m=memory(data,L,f);m.memory[0xc200:0xc281]=v;m.memory[0xc22a:0xc22c]=[0,2]
        cycles.append(call(m,L['MiniStep']));actual=m.memory[0xc200:0xc281];expected=r.stdout[i*129:(i+1)*129]
        diffs=[(hex(0xc200+j),v[j],actual[j],expected[j])for j in CHECK if actual[j]!=expected[j]]
        assert not diffs,dict(case=i,fixture=f,state=v[40],diffs=diffs,input=list(v))
    out=dict(passed=True,original_C_cases=len(cases),checked_offsets=CHECK,cycles=[min(cycles),max(cycles)],literal_source_function_SHA256=binds,component_SHA256=W.sha(data),scope='Exact five original C function bodies; no actors/scripts/swim/Yoshi; native16px terrains exposed through original8px tile_at. Ground/fall/crouch/skid/jump and poweredbounds included. Random single-update legal scalar inputs, no native acceptance.',bindings={str(p.relative_to(R)).replace('\\','/'):W.sha(p.read_bytes())for p in [Path(__file__),R/'tools/reference/mini_mario_world_1103_v16.inc',O/'world-step-v16.json']})
    (O/'world-step-CPU-v18.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
