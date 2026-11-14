import numpy as np, math, subprocess, wave, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
W,H,FPS,DUR=1080,1920,30,12.0
N=int(FPS*DUR)
SC=os.path.dirname(os.path.abspath(__file__))
OUT='/home/user/instagram-agent-skill/output/vice_city_clipz_gta6_6days.mp4'
F_BLACKI='/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf'
F_BOLD='/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
PINK=(255,46,170); CYAN=(0,240,255); ORANGE=(255,150,40); WHITE=(255,255,255)
CX=470  # text column centre: keeps right 230px clear for the action rail
random.seed(6); rng=np.random.default_rng(6)

# ---------- static background ----------
HOR=1180
y=np.arange(H)[:,None].astype(float)
def lerp(a,b,t): return a+(b-a)*t
sky=np.zeros((H,W,3))
stops=[(0,(10,4,30)),(500,(48,10,90)),(900,(150,30,140)),(1100,(255,90,120)),(HOR,(255,170,80))]
for (y0,c0),(y1,c1) in zip(stops,stops[1:]):
    m=(y>=y0)&(y<y1); t=((y-y0)/(y1-y0))
    for k in range(3): sky[...,k]=np.where(m,lerp(c0[k],c1[k],t),sky[...,k])
sky[HOR:]=(14,2,28)
bg=Image.fromarray(sky.clip(0,255).astype(np.uint8))
d=ImageDraw.Draw(bg)
for _ in range(160):
    sx,sy=random.randrange(W),random.randrange(0,700); r=random.choice([1,1,2])
    d.ellipse([sx-r,sy-r,sx+r,sy+r],fill=(255,255,255))
# striped sun
sun=Image.new('RGBA',(W,H),(0,0,0,0)); sd=ImageDraw.Draw(sun)
SR=330; SCX,SCY=W//2,HOR-110
for yy in range(SCY-SR,HOR):
    t=(yy-(SCY-SR))/(2*SR)
    col=tuple(int(lerp(a,b,min(t,1))) for a,b in zip((255,230,90),(255,40,150)))
    dx=SR**2-(yy-SCY)**2
    if dx<=0: continue
    dx=math.sqrt(dx)
    band=yy>SCY-60 and ((yy-SCY+60)%44)<(6+ (yy-SCY+60)/16)
    if not band: sd.line([(SCX-dx,yy),(SCX+dx,yy)],fill=col+(255,))
glow=sun.filter(ImageFilter.GaussianBlur(40))
bg=Image.alpha_composite(bg.convert('RGBA'),glow); bg=Image.alpha_composite(bg,sun)
# palm silhouettes
def palm(dr,x,base,h,lean,s=1.0):
    pts=[]
    for i in range(40):
        t=i/39; pts.append((x+lean*t*t, base-h*t))
    for i in range(len(pts)-1):
        w=int((22-12*i/40)*s); dr.line([pts[i],pts[i+1]],fill=(8,0,18),width=w)
    tx,ty=pts[-1]
    for ang in [-170,-140,-110,-70,-40,-10,20,200,160]:
        a=math.radians(ang); L=230*s
        prev=(tx,ty)
        for j in range(1,16):
            t=j/15
            px=tx+math.cos(a)*L*t; py=ty+math.sin(a)*L*t*0.5+ (L*0.55)*t*t
            dr.line([prev,(px,py)],fill=(8,0,18),width=max(2,int(16*(1-t)*s)+2)); prev=(px,py)
pl=Image.new('RGBA',(W,H),(0,0,0,0)); pd=ImageDraw.Draw(pl)
palm(pd,70,HOR+40,820,90,1.15); palm(pd,190,HOR+40,560,-60,0.85); palm(pd,1010,HOR+40,700,-110,1.05)
bg=Image.alpha_composite(bg,pl)
# city skyline strip at horizon
sk=Image.new('RGBA',(W,H),(0,0,0,0)); kd=ImageDraw.Draw(sk); x=0
while x<W:
    bw=random.randint(30,80); bh=random.randint(30,150)
    kd.rectangle([x,HOR-bh,x+bw,HOR],fill=(30,6,55,255))
    for wy in range(HOR-bh+8,HOR-6,14):
        for wx in range(x+6,x+bw-6,12):
            if random.random()<0.35: kd.rectangle([wx,wy,wx+4,wy+6],fill=(255,200,120,255))
    x+=bw+random.randint(0,10)
bg=Image.alpha_composite(Image.alpha_composite(bg.copy(),sk),pl)  # palms stay in front
BG=bg

scan=Image.new('RGBA',(W,H),(0,0,0,0)); scd=ImageDraw.Draw(scan)
for yy in range(0,H,4): scd.line([(0,yy),(W,yy)],fill=(0,0,0,38))
vig=np.zeros((H,W),float); xx=np.linspace(-1,1,W)[None,:]; yy2=np.linspace(-1,1,H)[:,None]
vig=(np.clip((xx**2+yy2**2)-0.55,0,2)*120).clip(0,170).astype(np.uint8)
VIG=Image.merge('RGBA',[Image.new('L',(W,H),0)]*3+[Image.fromarray(vig)])

def grid(t):
    g=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(g)
    span=H-HOR
    off=(t*1.6)%1.0
    for i in range(24):
        z=(i+1-off)
        if z<=0: continue
        yy=HOR+span*(1.0/ (z*0.35+0.0001))*0.06
        yy=HOR+span*(0.9/(z))
        if yy>H: continue
        gd.line([(0,yy),(W,yy)],fill=PINK+(int(200*min(1,(yy-HOR)/120)),),width=3)
    for k in range(-14,15):
        gd.line([(W/2+k*18,HOR),(W/2+k*260,H)],fill=PINK+(190,),width=3)
    return Image.alpha_composite(g.filter(ImageFilter.GaussianBlur(6)),g)

# ---------- text helpers ----------
_fc={}
def font(p,s):
    k=(p,s)
    if k not in _fc: _fc[k]=ImageFont.truetype(p,s)
    return _fc[k]
def neon(txt,size,col,cx,cy,scale=1.0,alpha=1.0,fp=F_BLACKI,outline=WHITE,shake=0):
    s=max(8,int(size*scale)); f=font(fp,s)
    l=Image.new('RGBA',(W,H),(0,0,0,0)); dd=ImageDraw.Draw(l)
    bb=dd.textbbox((0,0),txt,font=f); tw,th=bb[2]-bb[0],bb[3]-bb[1]
    x=cx-tw/2-bb[0]+shake; y=cy-th/2-bb[1]
    dd.text((x,y),txt,font=f,fill=col+(255,))
    core=Image.new('RGBA',(W,H),(0,0,0,0)); cd=ImageDraw.Draw(core)
    cd.text((x,y),txt,font=f,fill=outline+(255,),stroke_width=0)
    cd.text((x,y),txt,font=f,fill=(0,0,0,0),stroke_width=max(2,s//60),stroke_fill=col+(255,))
    g1=l.filter(ImageFilter.GaussianBlur(max(6,s//14))); g2=l.filter(ImageFilter.GaussianBlur(max(14,s//6)))
    out=Image.alpha_composite(Image.alpha_composite(g2,g1),g1)
    inner=Image.new('RGBA',(W,H),(0,0,0,0)); idd=ImageDraw.Draw(inner)
    idd.text((x,y),txt,font=f,fill=(255,235,250,255),stroke_width=max(3,s//45),stroke_fill=col+(255,))
    out=Image.alpha_composite(out,inner)
    if alpha<1:
        a=out.getchannel('A').point(lambda v:int(v*alpha)); out.putalpha(a)
    return out
def ease_out_back(t):
    c1=1.70158;c3=c1+1; return 1+c3*(t-1)**3+c1*(t-1)**2
def clamp(v,a=0,b=1): return max(a,min(b,v))

# ---------- timeline ----------
BEATS=[0.0,2.2,4.6,7.0,9.6,DUR]
def frame(i):
    t=i/FPS
    img=BG.copy()
    img=Image.alpha_composite(img,grid(t))
    sh=0
    # brand bug (inside safe zone, y>=230)
    img=Image.alpha_composite(img,neon('VICE CITY CLIPZ',44,CYAN,CX,280,fp=F_BOLD,alpha=0.95))
    if t<BEATS[1]:          # HOOK: 6 DAYS slam, on screen from frame 1
        if t<0.45:  # VI on screen at frame 1, then glitches into 6
            img=Image.alpha_composite(img,neon('VI',520,PINK,CX,760,scale=1.0+0.1*t,shake=int(10*math.sin(i*2.3))))
        else:
            p=clamp((t-0.45)/0.3); sc=1.6-0.6*ease_out_back(p) if p<1 else 1.0+0.03*math.sin(t*9)
            sh=int((1-p)*30*math.sin(i*3.1))
            img=Image.alpha_composite(img,neon('6',620,PINK,CX,760,scale=sc,shake=sh))
        q=clamp((t-0.75)/0.3)
        img=Image.alpha_composite(img,neon('DAYS',170,CYAN,CX,1150,scale=0.85+0.15*ease_out_back(q) if q>0 else 0.01,alpha=q))
        r=clamp((t-1.1)/0.3)
        img=Image.alpha_composite(img,neon('UNTIL GTA VI',92,ORANGE,CX,1340,alpha=r,fp=F_BLACKI))
    elif t<BEATS[2]:        # beat 2
        lt=t-BEATS[1]
        for k,(w,c,yy,sz) in enumerate([('SIX MORE',CYAN,700,140),('SUNSETS',PINK,880,170),('IN VICE CITY',ORANGE,1080,110)]):
            a=clamp((lt-k*0.25)/0.25)
            if a>0: img=Image.alpha_composite(img,neon(w,sz,c,CX+int((1-a)*-200),yy,alpha=a))
    elif t<BEATS[3]:        # beat 3: day pips counting down
        lt=t-BEATS[2]
        img=Image.alpha_composite(img,neon('THE WAIT IS',110,CYAN,CX,620))
        img=Image.alpha_composite(img,neon('ALMOST OVER',112,PINK,CX,790,scale=1+0.04*math.sin(lt*8)))
        pd2=Image.new('RGBA',(W,H),(0,0,0,0)); dd=ImageDraw.Draw(pd2)
        n_on=6
        for k in range(12):
            cx=CX-5.5*56+k*56; on=k<n_on
            col=PINK if on else (90,40,110)
            if on and k==n_on-1 and int(lt*4)%2==0: col=WHITE
            dd.rounded_rectangle([cx-21,1010,cx+21,1110],radius=10,fill=col+(255,))
        img=Image.alpha_composite(img,pd2.filter(ImageFilter.GaussianBlur(10)));img=Image.alpha_composite(img,pd2)
        img=Image.alpha_composite(img,neon('6 DAYS LEFT',80,ORANGE,CX,1230,fp=F_BOLD))
    elif t<BEATS[4]:        # beat 4: CTA
        lt=t-BEATS[3]
        a=clamp(lt/0.3)
        img=Image.alpha_composite(img,neon('FIRST THING',120,CYAN,CX,640,alpha=a))
        img=Image.alpha_composite(img,neon("YOU'RE DOING?",120,PINK,CX,800,alpha=clamp((lt-0.2)/0.3)))
        b=clamp((lt-0.6)/0.3)
        img=Image.alpha_composite(img,neon('COMMENT BELOW',84,ORANGE,CX,1060,alpha=b,scale=1+0.05*math.sin(lt*10)))
        img=Image.alpha_composite(img,neon('↓',150,ORANGE,CX,1230+int(12*math.sin(lt*10)),alpha=b,fp=F_BOLD))
    else:                   # loop back: the 6 returns
        lt=t-BEATS[4]; p=clamp(lt/0.3)
        img=Image.alpha_composite(img,neon('6',620,PINK,CX,760,scale=0.6+0.4*ease_out_back(p) if p>0 else 0.6))
        img=Image.alpha_composite(img,neon('DAYS',170,CYAN,CX,1150,alpha=clamp((lt-0.3)/0.3)))
        img=Image.alpha_composite(img,neon('FOLLOW FOR THE COUNTDOWN',52,ORANGE,CX,1340,alpha=clamp((lt-0.6)/0.3),fp=F_BOLD))
    # flash at each cut
    for b in BEATS[1:-1]:
        dt=t-b
        if 0<=dt<0.12:
            fl=Image.new('RGBA',(W,H),(255,255,255,int(150*(1-dt/0.12)))); img=Image.alpha_composite(img,fl)
    rgb=img.convert('RGB')
    # chromatic aberration glitch near cuts / hook
    glitch=0.35<t<0.7 or any(0<=t-b<0.25 for b in BEATS[1:-1])
    if glitch:
        r,g,bch=rgb.split(); o=random.randint(6,18)
        r=ImageChops.offset(r,o,0); bch=ImageChops.offset(bch,-o,0)
        rgb=Image.merge('RGB',(r,g,bch))
        arr=np.array(rgb)
        for _ in range(4):
            yy0=random.randrange(0,H-60); hh=random.randint(10,60); arr[yy0:yy0+hh]=np.roll(arr[yy0:yy0+hh],random.randint(-60,60),axis=1)
        rgb=Image.fromarray(arr)
    rgba=Image.alpha_composite(Image.alpha_composite(rgb.convert('RGBA'),scan),VIG)
    arr=np.array(rgba.convert('RGB')).astype(np.int16)
    arr+=rng.integers(-8,9,size=(H,W,1),dtype=np.int16)
    return arr.clip(0,255).astype(np.uint8)

# ---------- audio: original synthwave bed ----------
SR_=44100; BPM=110; beat=60/BPM; n=int(SR_*DUR)
au=np.zeros(n)
tt=np.arange(n)/SR_
def env(length,a=0.005,r=0.2):
    k=np.arange(length)/SR_; return np.minimum(1,k/a)*np.exp(-k/r)
def add(start,sig):
    s=int(start*SR_); e=min(n,s+len(sig)); 
    if s<n: au[s:e]+=sig[:e-s]
def saw(f,L): k=np.arange(L)/SR_; return 2*((k*f)%1)-1
def kick(): L=int(0.35*SR_); k=np.arange(L)/SR_; f=50+120*np.exp(-k*30); return np.sin(2*np.pi*np.cumsum(f)/SR_)*np.exp(-k*8)
def snare(): L=int(0.25*SR_); k=np.arange(L)/SR_; return (rng.standard_normal(L)*0.6+np.sin(2*np.pi*190*k)*0.4)*np.exp(-k*14)
def hat(): L=int(0.05*SR_); return rng.standard_normal(L)*np.exp(-np.arange(L)/SR_*90)*0.25
chords=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]  # Am F C G
mtof=lambda m:440*2**((m-69)/12)
bar=beat*4; t0=0.0
b=t0; ci=0
while b<DUR:
    ch=chords[ci%4]; L=int(bar*SR_)
    pad=sum(saw(mtof(m),L)+saw(mtof(m)*1.005,L) for m in ch)*0.035
    k=np.arange(L)/SR_; pad*=np.minimum(1,k/0.3)*np.minimum(1,(bar-k)/0.1)
    add(b,pad)
    for s16 in range(16):
        m=ch[0]-24 + (12 if s16%4==2 else 0)
        add(b+s16*beat/4, saw(mtof(m),int(beat/4*SR_))*env(int(beat/4*SR_),0.003,0.08)*0.22)
        arp=ch[s16%3]+12+(12 if s16>=8 else 0)
        add(b+s16*beat/4, np.sign(np.sin(2*np.pi*mtof(arp)*np.arange(int(beat/4*SR_))/SR_))*env(int(beat/4*SR_),0.002,0.06)*0.05)
    b+=bar; ci+=1
for q in np.arange(0,DUR,beat):
    add(q,kick()*0.9); add(q+beat/2,hat())
    if int(round(q/beat))%2==1: add(q,snare()*0.45)
# impacts on cuts + hook
for c in [0.0,0.45]+BEATS[1:-1]:
    L=int(1.2*SR_); k=np.arange(L)/SR_
    boom=np.sin(2*np.pi*(40+60*np.exp(-k*6))*k)*np.exp(-k*3)*0.9 + rng.standard_normal(L)*np.exp(-k*10)*0.3
    add(c,boom)
# riser into each cut
for c in BEATS[1:-1]:
    L=int(0.6*SR_); k=np.arange(L)/SR_
    add(c-0.6, rng.standard_normal(L)*(k/0.6)**2*0.18)
# simple low-pass smoothing + soft clip
au=np.tanh(au*1.1); au/=np.abs(au).max()*1.05
fade=int(0.25*SR_); au[-fade:]*=np.linspace(1,0,fade)
pcm=(au*32767).astype(np.int16)
st=np.stack([pcm,pcm],1)
wp=os.path.join(SC,'bed.wav')
with wave.open(wp,'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR_); w.writeframes(st.tobytes())

# ---------- encode ----------
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',wp,
  '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-profile:v','high','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
import sys
for i in range(N):
    p.stdin.write(frame(i).tobytes())
    if i%60==0: print(i,file=sys.stderr,flush=True)
p.stdin.close(); p.wait(); print('done',OUT)
