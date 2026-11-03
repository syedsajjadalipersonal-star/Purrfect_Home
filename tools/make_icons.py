# Renders the Purrfect Home logo (the cat-house) into the PWA icons and the Android launcher icons.
# Run: python3 tools/make_icons.py   (needs playwright + chromium)
import os,sys
from playwright.sync_api import sync_playwright
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO='''<defs><linearGradient id="lgRoof" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4896f"/><stop offset="1" stop-color="#e2625f"/></linearGradient><linearGradient id="lgWall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff6de"/><stop offset="1" stop-color="#ffe3b0"/></linearGradient></defs>
<g transform="translate(-120,0)"><g transform="translate(120,0)">
<path d="M24 92 L24 128 Q24 138 34 138 L86 138 Q96 138 96 128 L96 92 Z" fill="url(#lgWall)"/>
<path d="M10 78 L14 22 L40 44 Q60 36 80 44 L106 22 L110 78 Q110 92 96 92 L24 92 Q10 92 10 78 Z" fill="url(#lgRoof)"/>
<path d="M21 40 L23 29 L33 38 Z" fill="#ffc2c6"/><path d="M99 40 L97 29 L87 38 Z" fill="#ffc2c6"/>
<path d="M30 70 L90 70" stroke="#ffffff55" stroke-width="3" stroke-linecap="round"/>
<ellipse cx="44" cy="106" rx="10" ry="11" fill="#ffd45e"/><ellipse cx="76" cy="106" rx="10" ry="11" fill="#ffd45e"/>
<ellipse cx="44" cy="106" rx="3.2" ry="8.5" fill="#3a2a22"/><ellipse cx="76" cy="106" rx="3.2" ry="8.5" fill="#3a2a22"/>
<circle cx="46" cy="101" r="2.4" fill="#fff"/><circle cx="78" cy="101" r="2.4" fill="#fff"/>
<path d="M54 118 L66 118 L60 126 Z" fill="#ef7f95"/><path d="M60 126 Q56 132 51 129 M60 126 Q64 132 69 129" stroke="#8a4b3a" stroke-width="2.2" fill="none" stroke-linecap="round"/>
<g stroke="#fff6de" stroke-width="2.6" stroke-linecap="round"><path d="M22 112 L2 106"/><path d="M22 120 L2 124"/><path d="M98 112 L118 106"/><path d="M98 120 L118 124"/></g>
<path d="M16 84 Q60 98 104 84" stroke="#c9514f55" stroke-width="3" fill="none" stroke-linecap="round"/></g></g>'''
def svg(size,kind,frac):
    # logo art spans x 0..120, y 22..138 in its own box; centre it and scale so it fills `frac` of the icon
    k=size*frac/120.0; tx=size/2-60*k; ty=size/2-80*k
    bg={'full':'<defs><radialGradient id="bgg" cx="50%%" cy="30%%" r="90%%"><stop offset="0" stop-color="#4fae86"/><stop offset=".6" stop-color="#2e7658"/><stop offset="1" stop-color="#245f47"/></radialGradient></defs><rect width="%d" height="%d" fill="url(#bgg)"/>'%(size,size),
        'round':'<defs><radialGradient id="bgg" cx="50%%" cy="30%%" r="90%%"><stop offset="0" stop-color="#4fae86"/><stop offset=".6" stop-color="#2e7658"/><stop offset="1" stop-color="#245f47"/></radialGradient><clipPath id="cp"><circle cx="%f" cy="%f" r="%f"/></clipPath></defs><g clip-path="url(#cp)"><rect width="%d" height="%d" fill="url(#bgg)"/></g>'%(size/2,size/2,size/2,size,size),
        'fg':''}[kind]
    art='<g transform="translate(%f,%f) scale(%f)">%s</g>'%(tx,ty,k,LOGO)
    if kind=='round': art='<g clip-path="url(#cp)">'+art+'</g>'
    return '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">%s%s</svg>'%(size,size,size,size,bg,art)
jobs=[]
for n,sz in [('icon-192',192),('icon-512',512)]: jobs.append((f'{R}/icons/{n}.png',sz,'full',.74))
for n,sz in [('maskable-192',192),('maskable-512',512)]: jobs.append((f'{R}/icons/{n}.png',sz,'full',.56))
for d,sz,fg in [('mdpi',48,108),('hdpi',72,162),('xhdpi',96,216),('xxhdpi',144,324),('xxxhdpi',192,432)]:
    base=f'{R}/android-icons/mipmap-{d}'
    jobs.append((f'{base}/ic_launcher.png',sz,'full',.74)); jobs.append((f'{base}/ic_launcher_round.png',sz,'round',.74)); jobs.append((f'{base}/ic_launcher_foreground.png',fg,'fg',.5))
# native launch screen: same green with the logo in the middle
def splash(w,h):
    k=w*.5/120.0
    return '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d"><rect width="%d" height="%d" fill="#2e7658"/><g transform="translate(%f,%f) scale(%f)">%s</g></svg>'%(w,h,w,h,w,h,w/2-60*k,h/2-80*k,k,LOGO)
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page()
    for path,sz,kind,frac in jobs:
        os.makedirs(os.path.dirname(path),exist_ok=True)
        pg.set_viewport_size({'width':sz,'height':sz});pg.set_content('<body style="margin:0;background:transparent">'+svg(sz,kind,frac)+'</body>')
        pg.screenshot(path=path,omit_background=True,clip={'x':0,'y':0,'width':sz,'height':sz})
    pg.set_viewport_size({'width':720,'height':1280});pg.set_content('<body style="margin:0">'+splash(720,1280)+'</body>')
    os.makedirs(R+'/android-icons/drawable',exist_ok=True);pg.screenshot(path=R+'/android-icons/drawable/splash.png',clip={'x':0,'y':0,'width':720,'height':1280})
    b.close()
print(len(jobs),'icons written')
