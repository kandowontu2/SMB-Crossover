; Dedicated Sunny identity and future power-state ownership. No menu alternate.
.ifndef __SUNNY_STATE_INC
__SUNNY_STATE_INC=1
.ifndef CHARACTER_SUNNY
CHARACTER_SUNNY=23
.endif
SUNNY_FIRST_CHR=724
SunnyForm=$5fb8                ; own0 small /1 big /2 host Fire tier
SunnyReady=$5fb9
SunnyLife=$5fba
SunnyArea=$5fbb
SunnyWorld=$5fbc
SunnyPalette=$5fbd             ; FF dirty;0 normal /1 source alternate colors
SunnyLastForm=$5fbe
SunnyFuture=$5fbf              ; reserved, initialized0, no invented ability
SunnyClock=$5c00               ; dedicated active overlay, never another ID
SunnyPose=$5c01
SunnyFrame=$5c02
SunnyTemp=$5c03
SunnyAnimationStep=$5c04       ; owned temporary source-animation divisor
SUNNY_POSE_IDLE=0
SUNNY_POSE_WALK0=1
SUNNY_POSE_WALK1=2
SUNNY_POSE_WALK2=3
SUNNY_POSE_SKID=4
SUNNY_POSE_JUMP=5
SUNNY_POSE_FALL=6
SUNNY_POSE_CROUCH=7
SUNNY_POSE_SWIM0=8
SUNNY_POSE_SWIM1=9
SUNNY_POSE_SWIM2=10
SUNNY_POSE_CLIMB0=11
SUNNY_POSE_CLIMB1=12
SUNNY_POSE_DEATH=13
SUNNY_POSE_THROW=14
SUNNY_POSE_GROWTH=15
SUNNY_POSE_PORTRAIT=16
SUNNY_POSE_COUNT=17
.export SunnyForm,SunnyReady,SunnyLife,SunnyArea,SunnyWorld
.export SunnyPalette,SunnyLastForm,SunnyFuture,SunnyClock,SunnyPose,SunnyFrame
.endif
