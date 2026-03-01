# ==========================================
# 32x32 自動都市 + 人ランダム + 信号 + 配送
# デバッグ統合版（完成）
# ==========================================
import random, heapq, copy
from itertools import permutations

H=W=32
DIRS={0:(-1,0),1:(0,-1),2:(1,0),3:(0,1)}
ARROW={0:"▲",1:"◀",2:"▼",3:"▶"}

# =========================================================
# A*
# =========================================================
def manhattan(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])

def astar(start,goal,map_):
    pq=[(0,start)]
    cost={start:0}
    prev={}
    while pq:
        _,cur=heapq.heappop(pq)
        if cur==goal: break
        for d in DIRS.values():
            nr,nc=cur[0]+d[0],cur[1]+d[1]
            if not(0<=nr<H and 0<=nc<W): continue
            if map_[nr][nc] in "■◆◎": continue
            ncst=cost[cur]+1
            if (nr,nc) not in cost or ncst<cost[(nr,nc)]:
                cost[(nr,nc)]=ncst
                heapq.heappush(pq,(ncst+manhattan((nr,nc),goal),(nr,nc)))
                prev[(nr,nc)]=cur
    if goal not in prev: return []
    path=[goal]
    while path[-1]!=start:
        path.append(prev[path[-1]])
    return path[::-1]

# =========================================================
# マップ生成
# =========================================================
def generate_map():

    while True:

        grid=[["■"]*W for _ in range(H)]

        # --- 縦道路2本 ---
        v1=random.randint(4,8)
        v2=random.randint(20,24)
        if abs(v1-v2)<8: continue

        # --- 横道路2本 ---
        h1=random.randint(4,8)
        h2=random.randint(20,24)
        if abs(h1-h2)<8: continue

        V=[v1,v2]
        Hs=[h1,h2]

        # 道幅4
        for v in V:
            for r in range(H):
                for w in range(4):
                    grid[r][v+w]="◆"

        for h in Hs:
            for c in range(W):
                for w in range(4):
                    grid[h+w][c]="◆"

        # 歩道幅2
        for r in range(H):
            for c in range(W):
                if grid[r][c]=="◆":
                    for dr,dc in DIRS.values():
                        for k in [1,2]:
                            nr,nc=r+dr*k,c+dc*k
                            if 0<=nr<H and 0<=nc<W and grid[nr][nc]=="■":
                                grid[nr][nc]="・"

        # 交差点ごとの横断歩道＆信号
        for v in V:
            for h in Hs:

                # 横断歩道
                crosses=[
                    (h, v-4, h+3, v-3),
                    (h, v+6, h+3, v+7),
                    (h-4, v, h-3, v+3),
                    (h+6, v, h+7, v+3),
                ]
                for r1,c1,r2,c2 in crosses:
                    for r in range(r1,r2+1):
                        for c in range(c1,c2+1):
                            if 0<=r<H and 0<=c<W:
                                grid[r][c]="＃"

                # 信号①
                sig1=[(h-1,v-3),(h+4,v-4),(h-1,v+7),(h+4,v+6)]
                for r,c in sig1:
                    if 0<=r<H and 0<=c<W:
                        grid[r][c]="①"

                # 信号②
                sig2=[(h-4,v-1),(h-3,v+4),(h+6,v-1),(h+7,v+4)]
                for r,c in sig2:
                    if 0<=r<H and 0<=c<W:
                        grid[r][c]="②"

        # 受/A/B/C配置
        def place_point(ch):
            cand=[]
            for r in range(H):
                for c in range(W):
                    if grid[r][c]=="■":
                        for d in DIRS.values():
                            nr,nc=r+d[0],c+d[1]
                            if 0<=nr<H and 0<=nc<W and grid[nr][nc]=="・":
                                cand.append((r,c)); break
            if not cand: return False
            r,c=random.choice(cand)
            grid[r][c]=ch
            return True

        for ch in ["受","Ａ","Ｂ","Ｃ"]:
            if not place_point(ch): break

        # 建物比率
        building=sum(grid[r][c]=="■" for r in range(H) for c in range(W))
        if building < int(0.14*H*W): continue

        # 到達可能性
        pos={}
        for r in range(H):
            for c in range(W):
                if grid[r][c] in "受ＡＢＣ":
                    pos[grid[r][c]]=(r,c)
        ok=True
        keys=list(pos.keys())
        for i in range(len(keys)):
            for j in range(i+1,len(keys)):
                if not astar(pos[keys[i]],pos[keys[j]],grid):
                    ok=False
        if not ok: continue

        return grid

# =========================================================
# 人配置
# =========================================================
def place_people(grid):

    walk=[(r,c) for r in range(H) for c in range(W)
          if grid[r][c] in "・＃"]

    x=len(walk)
    h_max=max(0,int(x/4)-4)
    h_total=random.randint(0,h_max)

    banned=set()
    for ch in "ＡＢＣ受":
        for r in range(H):
            for c in range(W):
                if grid[r][c]==ch:
                    banned.add((r,c))

    random.shuffle(walk)
    count=0
    for r,c in walk:
        if any(manhattan((r,c),b)<=2 for b in banned):
            continue
        grid[r][c]="◯"
        banned.add((r,c))
        count+=1
        if count>=h_total: break

    print("👤 人数:",count)

# =========================================================
# 信号
# =========================================================
def signal_color(step, offset):
    t=(step+offset)%50
    if t<20: return 0
    if t<30: return 1
    return 2

# =========================================================
# 実行
# =========================================================
grid=generate_map()
place_people(grid)

def find(ch):
    for r in range(H):
        for c in range(W):
            if grid[r][c]==ch:
                return (r,c)

agent=find("受")
dir=0

ITEMS=[20.0,5.0,1.0,0.0001]
WEIGHTS={p:random.choice(ITEMS) for p in ["Ａ","Ｂ","Ｃ"]}

POS={p:find(p) for p in ["受","Ａ","Ｂ","Ｃ"]}

DIST={(a,b):len(astar(POS[a],POS[b],grid))-1
      for a in POS for b in POS if a!=b}

def total_cost(order):
    remain=sum(WEIGHTS[x] for x in order)
    cost=0; cur="受"
    for nxt in order:
        cost+=DIST[(cur,nxt)]*remain
        remain-=WEIGHTS[nxt]
        cur=nxt
    return cost

best=min(permutations(["Ａ","Ｂ","Ｃ"]),key=total_cost)
queue=list(best)+["受"]
goal=POS[queue[0]]

print("📦 配送順:",queue)

# =========================================================
# メインループ
# =========================================================
for step in range(500):

    sig1=signal_color(step,0)
    sig2=signal_color(step,25)

    vis=copy.deepcopy(grid)
    vis[agent[0]][agent[1]]=ARROW[dir]

    print("\nSTEP",step,"目標:",queue[0])
    for r in vis: print("".join(r))

    if agent==goal:
        print("✅ 到達:",queue[0])
        queue.pop(0)
        if not queue:
            print("🎉 完了"); break
        goal=POS[queue[0]]
        continue

    path=astar(agent,goal,grid)
    if len(path)<2:
        print("❌ 経路なし"); break

    nr,nc=path[1]
    dr,dc=nr-agent[0],nc-agent[1]
    next_dir=[k for k,v in DIRS.items() if v==(dr,dc)][0]

    if dir!=next_dir:
        dir=next_dir
        print("🔄 回転")
        continue

    if grid[nr][nc]=="◯":
        grid[nr][nc]="◎"
        print("👀 人検出 → 再探索")
        continue

    if grid[nr][nc]=="＃":
        sig = sig1 if nr < 16 else sig2
        if sig==2:
            print("🚦 赤停止")
            continue

    agent=(nr,nc)