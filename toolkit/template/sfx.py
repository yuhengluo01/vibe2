import numpy as np
SR = 44100; SCALE = 1.0; BAR = 2.1258; D = 52 * BAR + 0.5; N = int(SR * D)
rng = np.random.default_rng(11)
mix = np.zeros(N)

def add(sig, at, gain=1.0):  # `at` in design seconds
    i = int(at * SCALE * SR); j = min(N, i + len(sig))
    if j > i: mix[i:j] += sig[: j - i] * gain

def env(n, a, d):
    x = np.arange(n) / SR
    return np.minimum(1, x / max(a, 1e-4)) * np.exp(-x / d)

def lp(x, k):
    y = np.empty_like(x); s = 0.0
    for i, v in enumerate(x):
        s += k * (v - s); y[i] = s
    return y

def tone(f, dur, decay, harm=(1, 2.01, 3.02)):
    n = int(dur * SR); x = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * h * x) / (i + 1) ** 1.5 for i, h in enumerate(harm)) * env(n, .003, decay)

def hit(dur=1.6):
    n = int(dur * SR); x = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(35 + 70 * np.exp(-x * 12)) / SR) * np.exp(-x * 2.2)
    return boom + lp(rng.standard_normal(n), 0.08) * np.exp(-x * 6) * .8

def whoosh(dur=.75):
    n = int(dur * SR); x = np.arange(n) / n; nz = rng.standard_normal(n); y = np.empty(n); s = 0.0
    for i in range(n):
        s += (0.01 + 0.25 * x[i] ** 2) * (nz[i] - s); y[i] = s
    return y * x ** 2 * 2.2

def creak(dur=.7, f0=150, f1=95):  # door swinging
    n = int(dur * SR); x = np.arange(n) / SR
    f = np.linspace(f0, f1, n)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 28 * x)))
    s = lp(s, .2) + lp(rng.standard_normal(n), .05) * .5
    return s * np.minimum(1, x / .05) * np.clip((dur - x) / .2, 0, 1)

def blip(f0, f1, dur=.18):
    n = int(dur * SR); x = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f1, n)) / SR) * env(n, .002, dur / 3)

bar = lambda b: (b - 1) * BAR
H = hit()
def ch(at, f=1318.5, g=.3, d=.6): add(tone(f, 2.0, d), at, g)
def rustle(at, g=.25):
    n=int(.45*SR); x=np.arange(n)/SR; nz=rng.standard_normal(n); y=nz-lp(nz,.15); y=lp(y,.5)
    add(y*np.exp(-x*9)*(1+0.6*np.sin(x*90)), at, g)
def boom(at, g=1.0):
    n=int(3.0*SR); x=np.arange(n)/SR; f=55*np.exp(-x*1.2)+28; ph=2*np.pi*np.cumsum(f)/SR
    add(np.sin(ph)*np.exp(-x*1.3)*np.minimum(1,x/.004), at, g)
def roar(at, dur, g):
    n=int(dur*SR); x=np.arange(n)/n; nz=rng.standard_normal(n); y=np.empty(n); s=0.0
    for i in range(n):
        s += (0.02+0.25*x[i])*(nz[i]-s); y[i]=s
    add(y*np.minimum(1,x*20)*(1-x)**.6*2.2, at, g)
def thump(at,g=.6):
    n=int(.35*SR); x=np.arange(n)/SR; add(np.sin(2*np.pi*(60*np.exp(-x*6)+35)*x)*np.exp(-x*14), at, g)
FOLD0,FSTEP=3.2,1.3
for k in range(1,11): rustle(FOLD0+(k-1)*FSTEP, .22+.02*k)
thump(16.45,.5); thump(16.78,.6)
for X,E,big in ((bar(9),22.9,1),(bar(45),99.6,1)):
    add(hit(2.5),X,1.3); boom(X,1.1); add(whoosh(.6),X,.9)
    roar(X+.05,E-X,.75)
    add(hit(2.5),E,1.0); boom(E,.8)
for b in (15,19,23,31,37,49): add(H,bar(b),.55)
for b in (18,22,35): add(H,bar(b),.85)
add(H,bar(31),.9)
for i in range(64):
    tt = (bar(25)+.2+i*(bar(29)-bar(25)-.4)/24) if i<24 else (bar(29)+.2+((i-24)/39)**.8*(bar(31)-bar(29)-.5))
    add(blip(900+i*12,1300+i*12,.05),tt,.07)
rustle(85.1,.3); thump(92.85,.55); thump(93.2,.65)
ch(bar(49)+1.2,1046.5,.3,1.2); ch(bar(49)+1.2,1568,.15,1.2); ch(bar(51),1318.5,.22,1.0)
mix *= 0.89 / np.max(np.abs(mix))
np.save("sfx.npy", mix); print("sfx ok", N / SR)
