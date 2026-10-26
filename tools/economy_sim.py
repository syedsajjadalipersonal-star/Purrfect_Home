import random, statistics as st, json, sys
# ---------------- catalog (from index.html) ----------------
FP=dict(bed=50,side=10,sofa=35,chair=25,tv=15,lamp=5,coffee=5,rug=10,plant=5,shelf=20,dining=30,wardrobe=30,fridge=25,stove=20,hood=10,counter=10,ksink=20,toilet=20,shower=20,tub=20,vanity=20,washer=25,wallcab=15,bin=5,towel=5,bathmat=5,walllight=5,lantern=5,paintland=5,paintabs=5,paintcat=5,clock=5,mirror=5,wshelf=5,palm=8,fvase=6,pouf=8,basket=8,rrug=10,succ=3,fvase2=3,books=3,candles=3,photo=3,fruit=3,desklamp=5,teddy=3,catbed=15,fireplace=60,aquarium=70,desk=35,coffeemaker=25,hammock=20)
LV_OLD={2:'hammock sofa coffee rug clock mirror towel bathmat wshelf walllight succ books fruit hood',3:'desk coffeemaker dining tv wardrobe shower vanity wallcab rrug basket pouf candles photo fvase fvase2 desklamp',4:'tub washer palm lantern teddy paintland paintabs paintcat fireplace aquarium'}
SHOP_OLD=dict(scratch=30,tree=80,tower=140,bowl3=30,bowl5=60,wat3=30,wat5=60,tray2=40,tray3=80,toys=30)
ACC_OLD=dict(bowred=12,bowblue=12,flower=15)
BUILD_OLD=[150,250,400,600,800,1000]   # optional house build-out stages (walls/floors/doors) a player may chase
def lvl_of(table):
    d={}
    for L,s in table.items():
        for k in s.split():d[k]=L
    return d
# ---------------- parameter sets ----------------
OLD=dict(start=1200,tutorial=1960,dayend=lambda a,style:round((a-40)*1.2)+style if a>=50 else 0,style_k=.4,
 goal_r=lambda r:r,streak=lambda s:120+20*min(s,7),lvl_need=lambda L:80+40*(L-1),lvl_reward=lambda L:100+30*L,
 gift=(20,60),cuddle=40,desk=(8,12,180),coffee_cd=60,coffee_resets=True,fprice=FP,levels=lvl_of(LV_OLD),shop=SHOP_OLD,acc=ACC_OLD,build=BUILD_OLD,xp_goal=15,cos=[])
# archetypes: real minutes of play per calendar day, care quality (avg stat), goal completion prob, xp per game-day, desk use, gifts catch
ARCH={
 'casual 10min':dict(daily=.85,min=10,avg=70,pg=.85,xp=95,desk=.5,care=.8),
 'regular 25min':dict(daily=.9,min=25,avg=82,pg=.92,xp=134,desk=.7,care=.95),
 'hardcore 60min':dict(min=60,avg=92,pg=.97,xp=230,desk=1.0,care=1.0),
 'neglectful 25min':dict(daily=.6,min=25,avg=45,pg=.35,xp=60,desk=.3,care=.4),
 'grinder 60min':dict(min=60,avg=90,pg=1.0,xp=330,desk=1.0,care=1.0,exploit=True)}
def simulate(P,A,days=60,seed=0):
    r=random.Random(seed)
    coins=P['start']+P['tutorial'];lv=1;xp=0;streak=0;lastfull=-9;gday=0.0
    owned=set();shop_owned=set();acc_owned=set();bi=0;cos_owned=0
    core_total=sum(P['fprice'].values())+sum(P['shop'].values())+sum(P['build'])
    hist=[];core_done=None;lvl_hist=[];spent_core=0;income_log=[]
    desk_next=0;ls_state=[0]
    for d in range(1,days+1):
        inc_login=0
        if P.get('login') and r.random()<A.get('daily',1.0):
            ls=min(7,(ls_state[0]+1)) ; ls_state[0]=ls; inc_login=20+10*ls
        elif P.get('login'): ls_state[0]=0
        gd_adv=A['min']/24.0   # game days that elapse this calendar day
        gday+=gd_adv
        n_full_days=int(gday);gday-=n_full_days
        inc=inc_login
        # events that happen once per elapsed game day
        for _ in range(n_full_days):
            # dayEnd payout
            a=A['avg']+r.uniform(-8,8)
            style=min(100,len(owned)*3)  # approx style progress from owned items
            inc+=P['dayend'](a,round(style*P['style_k']))
            # daily goals
            done=0
            for gi in range(3):
                if r.random()<A['pg']:
                    done+=1;inc+=P['goal_r'](52);xp+=P['xp_goal']
            if done==3:
                streak=streak+1 if lastfull==d-1 or streak==0 else 1;lastfull=d;inc+=P['streak'](streak)
            elif done<3 and streak and d-lastfull>1:streak=0
            # gifts and cuddles during the day (9 events/game day)
            inc+=9*(1/6)*r.uniform(*P['gift'])*A['care'] if True else 0
            inc+=9*(1/3)*.5*P['cuddle']*A['care']*0.6
            # desk shifts
            dsk=P['desk'];cd=dsk[2]
            sh=int(1440/(cd if not (A.get('exploit') and P['coffee_resets']) else P['coffee_cd']))
            inc+=A['desk']*sh*(dsk[0]+min(100,len(owned)*3)/dsk[1])*(1 if 'desk' in owned else 0)
            xp+=A['xp']
        # partial day: pro-rate desk/gift in the remaining fraction (minor)
        # level ups
        while xp>=P['lvl_need'](lv):
            xp-=P['lvl_need'](lv);lv+=1;inc+=P['lvl_reward'](lv)
        coins+=inc;income_log.append(inc)
        # spending policy
        def buy_list():
            L=[]
            for k,p in P['fprice'].items():
                if k not in owned and P['levels'].get(k,1)<=lv:L.append((p,'f',k))
            for k,p in P['shop'].items():
                if k not in shop_owned:L.append((p,'s',k))
            return sorted(L)
        for p,t,k in buy_list():
            if coins>=p:
                coins-=p;spent_core+=p
                (owned if t=='f' else shop_owned).add(k)
        # house build-out stage
        while bi<len(P['build']) and coins>=P['build'][bi]*1.0 and len(owned)>=8*(bi+1)//2:
            coins-=P['build'][bi];spent_core+=P['build'][bi];bi+=1
        # cosmetics after core nearly done
        if core_done is None and len(owned)==len(P['fprice']) and len(shop_owned)==len(P['shop']) and bi==len(P['build']):core_done=d
        if core_done is not None:
            for c in P['cos']:
                pass
        hist.append((d,round(coins),lv,len(owned)+len(shop_owned),bi,round(inc)))
    return dict(core_done=core_done,hist=hist,final_coins=hist[-1][1],lv_day={l:next((h[0] for h in hist if h[2]>=l),None) for l in (2,3,4,5,6,8)},avg_inc=st.mean(income_log[:14]),core_total=core_total)
if __name__=='__main__':
    P=OLD
    for name,A in ARCH.items():
        R=[simulate(P,A,60,s) for s in range(30)]
        cd=[x['core_done'] for x in R if x['core_done']]
        print(f"{name:20s} core done day: {st.median(cd) if cd else None} ({len(cd)}/30)  lv4 day: {st.median([x['lv_day'][4] or 99 for x in R])}  avg inc/day(first14): {st.mean(x['avg_inc'] for x in R):.0f}  coins@day14: {st.median([x['hist'][13][1] for x in R])}  coins@60: {st.median([x['final_coins'] for x in R])}")
    print('core catalog cost',R[0]['core_total'])

# ======================= proposed balance =======================
FP_NEW=dict(bed=50,side=10,chair=25,lamp=10,plant=10,shelf=25,fridge=40,stove=40,counter=15,ksink=30,toilet=30,bin=8,catbed=20,
 sofa=70,coffee=15,rug=20,clock=10,mirror=15,towel=10,bathmat=10,wshelf=12,walllight=15,succ=8,books=8,fruit=8,hood=25,hammock=35,
 desk=70,coffeemaker=50,dining=80,tv=80,wardrobe=70,shower=60,vanity=45,wallcab=30,rrug=30,basket=20,pouf=20,candles=12,photo=10,fvase=15,fvase2=10,desklamp=15,
 tub=80,washer=70,lantern=25,teddy=15,paintland=40,paintabs=40,paintcat=40,palm=45,fireplace=220,aquarium=260)
LV_NEW={2:'hammock sofa coffee rug clock mirror towel bathmat wshelf walllight succ books fruit hood',3:'desk coffeemaker dining tv wardrobe shower vanity wallcab rrug basket pouf candles photo fvase fvase2 desklamp',4:'tub washer lantern teddy paintland',5:'paintabs paintcat palm',6:'fireplace',7:'aquarium'}
SHOP_NEW=dict(scratch=40,tree=120,tower=220,bowl3=40,bowl5=90,wat3=40,wat5=90,tray2=60,tray3=120,toys=40)
NEW=dict(start=450,tutorial=590,dayend=lambda a,style:round((a-50)*.6)+style if a>=50 else 0,style_k=.15,
 goal_r=lambda r:round(r*.45),streak=lambda s:40+10*min(s,7),lvl_need=lambda L:100+60*(L-1),lvl_reward=lambda L:40+15*L,
 gift=(10,30),cuddle=25,desk=(4,40,240),coffee_cd=120,coffee_resets=False,fprice=FP_NEW,levels=lvl_of(LV_NEW),shop=SHOP_NEW,acc=dict(bowred=90,bowblue=90,flower=110),build=BUILD_OLD,xp_goal=15,cos=[])
def report(P,title,days=90):
    print('\n==',title)
    print(f"{'archetype':20s}{'core day':>9s}{'L4':>5s}{'L7':>5s}{'inc/day':>9s}{'coins d14':>10s}{'coins d30':>10s}{'coins d90':>10s}")
    for name,A in ARCH.items():
        R=[simulate(P,A,days,s) for s in range(40)]
        cd=[x['core_done'] for x in R if x['core_done']]
        med=lambda v:st.median(v)
        print(f"{name:20s}{(str(med(cd))+('*' if len(cd)<40 else '')) if cd else '-':>9s}{med([x['lv_day'][4] or 99 for x in R]):>5.0f}{med([ (next((h[0] for h in x['hist'] if h[2]>=7),99)) for x in R]):>5.0f}{st.mean(x['avg_inc'] for x in R):>9.0f}{med([x['hist'][13][1] for x in R]):>10.0f}{med([x['hist'][29][1] for x in R]):>10.0f}{med([x['hist'][days-1][1] for x in R]):>10.0f}")
    print('catalog:',R[0]['core_total'])
if __name__=='__main__':
    report(OLD,'BEFORE (current game)');report(NEW,'AFTER (proposed)')
