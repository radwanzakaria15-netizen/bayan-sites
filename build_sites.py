import json, re, html, os
SRC="/tmp/claude-0/proj/ENSD_ARABIC_PRAIMERY-main/data/"
OUT="/tmp/claude-0/gsites/"
ld=lambda f: json.load(open(SRC+f,encoding="utf-8"))
cfg=ld("academic.json")["config"]
year=cfg["years"][0]; sem=year["semesters"][0]
groups=[g.get("code") for g in year.get("groups",[])] or ["A","B"]
subjects=sem["subjects"]

def groups_of(item,s):
    o=(item.get("sec") or {}).get(s)
    return o["groups"] if o and "groups" in o else item.get("groups")
def ok(item,g,s):
    gr=groups_of(item,s); return not isinstance(gr,list) or g in gr
def nm(item,g,s):
    o=((item.get("sec") or {}).get(s) or {}).get("names") or {}
    return o.get(g) or (item.get("names") or {}).get(g) or item["name"]
def tp(ch,g,s):
    o=((ch.get("sec") or {}).get(s) or {}).get("topicsByGroup") or {}
    if isinstance(o.get(g),list): return o[g]
    b=ch.get("topicsByGroup") or {}
    return b[g] if isinstance(b.get(g),list) else ch.get("topics",[])

# ---- subjects (قسم المواد والمقاييس، المجموعة الأولى) ----
g0=groups[0]
subj=[]
for s in subjects:
    axes=[]
    for a in s["axes"]:
        if not ok(a,g0,"S"): continue
        chs=[{"n":nm(c,g0,"S"),"t":tp(c,g0,"S")} for c in a["chapters"] if ok(c,g0,"S")]
        axes.append({"n":nm(a,g0,"S"),"c":chs})
    subj.append({"n":s["name"],"y":s.get("symbol","م"),"k":s.get("coefficient",""),"a":axes})

# ---- lessons (الدروس) ----
files={}
for f in ld("lessons.json"):
    files.setdefault(f["lessonKey"],[]).append({"n":f["name"],"k":f["key"],"s":f.get("size",0),"t":f.get("type","")})
lessons={}
for key,fl in files.items():
    m=re.match(r"^([A-Z])-(\d\d)-(\d\d)-(\d\d)$",key)
    if not m: continue
    g,si,ai,ci=m.group(1),int(m.group(2))-1,int(m.group(3))-1,int(m.group(4))-1
    try:
        sb=subjects[si]; ax=sb["axes"][ai]; ch=ax["chapters"][ci]
    except IndexError: continue
    sn=(sb.get("lessonNames") or {}).get(g) or sb["name"]
    lessons.setdefault(g,{}).setdefault(sn,[]).append({"axis":nm(ax,g,"L"),"unit":nm(ch,g,"L"),"files":fl})

# ---- announcements ----
ann=[]
for a in ld("announcements.json"):
    if a["title"].startswith("__ensd"): continue
    body=re.sub(r"\[\[ensd:.*?\]\]","",a.get("body",""),flags=re.S).strip()
    ann.append({"t":a["title"],"b":body,"c":a.get("category",""),"d":a.get("date",""),"p":bool(a.get("pinned")),"l":a.get("link",""),"lt":a.get("linkText","")})
# ---- resources ----
res=[{"t":r["title"],"s":r.get("subject",""),"k":r.get("kind",""),"y":r.get("year",""),"m":r.get("semester",""),"f":r.get("fileName",""),"i":r["fileKey"],"d":r.get("createdAt","")[:10]} for r in ld("resources.json") if r.get("status")=="approved"]

CSS="""
:root{--bg:#f4f7f8;--surface:#fff;--ink:#1e2935;--muted:#66737f;--line:#e8edf0;--primary:#287c78;--primary-dark:#1e6562;--soft:#e8f3f1;--gold:#c18c42;--soft-gold:#fbf4e9;--blue:#587eaa;--soft-blue:#edf3f9}
@media(prefers-color-scheme:dark){:root{--bg:#0e1519;--surface:#16212a;--ink:#e8eef2;--muted:#93a0a9;--line:#263540;--primary:#4fb3ad;--primary-dark:#3a918c;--soft:#173331;--gold:#e0b06a;--soft-gold:#2b2518;--blue:#8fb0d6;--soft-blue:#1a2633}}
*{box-sizing:border-box}html{direction:rtl}
body{margin:0;background:var(--bg);color:var(--ink);font-family:Tajawal,system-ui,sans-serif;line-height:1.7;padding:14px}
h1,h2,h3{margin:0;font-weight:800}.wrap{max-width:980px;margin:0 auto}
.head{display:flex;align-items:center;gap:12px;margin-bottom:14px}
.mark{width:44px;height:44px;border-radius:14px;background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;display:grid;place-items:center;font-weight:800;font-size:22px;flex:none}
.head small{color:var(--muted);display:block;font-size:13px}.head h1{font-size:22px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:14px 16px;box-shadow:0 1px 2px rgba(20,40,50,.04)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}
input,select{width:100%;font:inherit;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:10px 14px;outline:none}
input:focus,select:focus{border-color:var(--primary)}
.bar{display:grid;grid-template-columns:2fr 1fr 1fr;gap:10px;margin-bottom:14px}@media(max-width:620px){.bar{grid-template-columns:1fr}}
.chip{display:inline-block;background:var(--soft);color:var(--primary-dark);border-radius:999px;padding:2px 10px;font-size:12.5px;font-weight:700}
.chip.gold{background:var(--soft-gold);color:var(--gold)}.chip.blue{background:var(--soft-blue);color:var(--blue)}
details{background:var(--surface);border:1px solid var(--line);border-radius:16px;margin-bottom:10px;overflow:hidden}
summary{cursor:pointer;list-style:none;padding:12px 16px;font-weight:700;display:flex;align-items:center;gap:10px}summary::-webkit-details-marker{display:none}
summary::after{content:"⌄";margin-inline-start:auto;color:var(--primary);transition:.2s}details[open]>summary::after{transform:rotate(180deg)}
details .in{padding:2px 16px 14px}details details{background:var(--bg);border-radius:12px}
.sym{width:38px;height:38px;border-radius:12px;background:var(--soft);color:var(--primary-dark);display:grid;place-items:center;font-weight:800;flex:none}
ul{margin:6px 0 0;padding-inline-start:20px;color:var(--muted)}li{margin:2px 0}
a.btn{display:inline-block;background:var(--primary);color:#fff;text-decoration:none;border-radius:12px;padding:5px 14px;font-weight:700;font-size:14px}
a.btn.ghost{background:var(--soft);color:var(--primary-dark)}
.row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;padding:8px 0;border-top:1px dashed var(--line)}.row:first-child{border-top:0}
.row b{flex:1;min-width:150px;word-break:break-word}.muted{color:var(--muted);font-size:13.5px}
.tabs{display:flex;gap:8px;margin-bottom:12px}.tabs button{flex:1;font:inherit;font-weight:700;border:1px solid var(--line);background:var(--surface);color:var(--muted);border-radius:14px;padding:9px;cursor:pointer}.tabs button.on{background:var(--primary);color:#fff;border-color:var(--primary)}
.empty{text-align:center;color:var(--muted);padding:26px}.pin{border-color:var(--gold)}
.hero{background:linear-gradient(135deg,var(--primary),var(--primary-dark));color:#fff;border:0;border-radius:22px;padding:24px 20px;margin-bottom:14px}.hero h2{font-size:26px}.hero p{margin:6px 0 0;opacity:.9}
.stat{text-align:center}.stat b{display:block;font-size:30px;color:var(--primary)}.stat span{color:var(--muted);font-weight:700}
"""
HEAD='<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>@@T@@</title><link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet"><style>'+CSS+'</style></head><body><div class="wrap">'
def page(title,sub,body,script,name):
    head=HEAD.replace('@@T@@',title)+'<div class="head"><div class="mark">ب</div><div><small>%s</small><h1>%s</h1></div></div>'%(sub,title)
    js=lambda o: json.dumps(o,ensure_ascii=False).replace("</","<\\/")
    open(OUT+name,"w",encoding="utf-8").write(head+body+'</div><script>'+script+'</script></body></html>')
BASEJS='/* ضع هنا عنوان موقعك القديم (لفتح الملفات منه) مثل: https://اسم-موقعك.workers.dev  — أو اتركه فارغًا إن لم تنقل الملفات بعد */\nconst FILES_BASE="";\nconst esc=s=>String(s??"").replace(/[&<>"\']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",\'"\':"&quot;","\'":"&#39;"}[c]));\nconst $=id=>document.getElementById(id);\n'
J=lambda o: json.dumps(o,ensure_ascii=False).replace("</","<\\/")

nfiles=sum(len(x) for g in lessons.values() for v in g.values() for u in v for x in [u["files"]])
# home
page("المنصة التعليمية","بَيَان · اللغة العربية",
 '<div class="hero"><h2>مرحبًا بك في بَيَان</h2><p>برنامج المقاييس، الدروس والمحاضرات، الموارد، والإعلانات في مكان واحد.</p></div>'
 '<div class="grid"><div class="card stat"><b>%d</b><span>مقياسًا</span></div><div class="card stat"><b>%d</b><span>ملف درس منشور</span></div><div class="card stat"><b>%d</b><span>مورد</span></div><div class="card stat"><b>%d</b><span>إعلانًا</span></div></div>'%(len(subj),nfiles,len(res),len(ann)),"", "01-home.html")

# subjects
page("المواد والمقاييس","%s · %s"%(year["name"],sem["name"]),
 '<div class="bar" style="grid-template-columns:1fr"><input id="q" placeholder="ابحث في المقاييس والمحاور والوحدات…"></div><div id="list"></div>',
 BASEJS+'const DATA='+J(subj)+';\n'+'''
function render(){const q=$("q").value.trim();const out=DATA.map(s=>({s,axes:s.a.map(a=>({a,c:a.c.filter(c=>!q||(s.n+a.n+c.n+c.t.join(" ")).includes(q))})).filter(x=>!q||x.c.length||(s.n+x.a.n).includes(q))})).filter(x=>!q||x.axes.length||x.s.n.includes(q));
$("list").innerHTML=out.length?out.map(({s,axes})=>`<details${q?" open":""}><summary><span class="sym">${esc(s.y)}</span><span>${esc(s.n)}</span>${s.k!==""?`<span class="chip gold">المعامل ${esc(s.k)}</span>`:""}<span class="chip">${s.a.length} محاور</span></summary><div class="in">${axes.map(({a,c},i)=>`<details${q?" open":""}><summary><span class="chip blue">المحور ${i+1}</span>${esc(a.n)}</summary><div class="in">${c.map((c,j)=>`<details><summary><span class="chip">${String(j+1).padStart(2,"0")}</span>${esc(c.n)}</summary><div class="in"><ul>${c.t.map(t=>`<li>${esc(t)}</li>`).join("")}</ul></div></details>`).join("")}</div></details>`).join("")}</div></details>`).join(""):'<div class="empty">لا توجد نتائج مطابقة.</div>';}
$("q").addEventListener("input",render);render();''',"02-subjects.html")

# lessons
page("الدروس والمحاضرات","الملفات المنشورة لكل مجموعة",
 '<div class="tabs" id="tabs"></div><div id="list"></div>',
 BASEJS+'const DATA='+J(lessons)+';let G=Object.keys(DATA)[0];\n'+'''
const size=n=>n>1048576?(n/1048576).toFixed(1)+" MB":Math.max(1,Math.round(n/1024))+" KB";
function render(){$("tabs").innerHTML=Object.keys(DATA).map(g=>`<button class="${g===G?"on":""}" data-g="${g}">المجموعة ${g}</button>`).join("");
const d=DATA[G]||{};$("list").innerHTML=Object.keys(d).length?Object.keys(d).map(s=>`<details><summary><span class="sym">${esc(s[0])}</span>${esc(s)}<span class="chip">${d[s].reduce((n,u)=>n+u.files.length,0)} ملفات</span></summary><div class="in">${d[s].map(u=>`<div class="muted" style="margin-top:8px">${esc(u.axis)}</div><div class="card" style="padding:4px 14px;margin:4px 0"><div style="font-weight:800;padding-top:8px">${esc(u.unit)}</div>${u.files.map(f=>`<div class="row"><b>${esc(f.n)}</b><span class="muted">${size(f.s)}</span><a class="btn ghost" target="_blank" rel="noopener" href="${FILES_BASE}/api/file?key=${encodeURIComponent(f.k)}">فتح</a><a class="btn" href="${FILES_BASE}/api/file?key=${encodeURIComponent(f.k)}&download=1">تحميل</a></div>`).join("")}</div>`).join("")}</div></details>`).join(""):'<div class="empty">لا توجد ملفات منشورة لهذه المجموعة بعد.</div>';}
$("tabs").addEventListener("click",e=>{const b=e.target.closest("[data-g]");if(b){G=b.dataset.g;render()}});render();''',"03-lessons.html")

# announcements
page("الإعلانات","آخر المستجدات",'<div id="list"></div>',
 BASEJS+'const DATA='+J(ann)+';\n'+'''
const fmt=d=>d?new Date(d).toLocaleDateString("ar-DZ",{day:"numeric",month:"long",year:"numeric"}):"";
$("list").innerHTML=DATA.length?DATA.sort((a,b)=>(b.p-a.p)||String(b.d).localeCompare(a.d)).map(a=>`<div class="card${a.p?" pin":""}" style="margin-bottom:10px"><div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center"><h3>${esc(a.t)}</h3>${a.c?`<span class="chip blue">${esc(a.c)}</span>`:""}${a.p?'<span class="chip gold">مثبّت</span>':""}<span class="muted" style="margin-inline-start:auto">${fmt(a.d)}</span></div><p style="white-space:pre-wrap;margin:8px 0 0">${esc(a.b)}</p>${a.l?`<p><a class="btn" target="_blank" rel="noopener" href="${esc(a.l)}">${esc(a.lt||"فتح الرابط")}</a></p>`:""}</div>`).join(""):'<div class="empty">لا توجد إعلانات حاليًا.</div>';''',"04-announcements.html")

# resources
page("الموارد","ملخصات · تمارين · كتب · امتحانات",
 '<div class="bar"><input id="q" placeholder="ابحث في الموارد…"><select id="s"><option value="">كل المقاييس</option></select><select id="k"><option value="">كل الأنواع</option></select></div><div id="list"></div>',
 BASEJS+'const DATA='+J(res)+';\n'+'''
const uniq=k=>[...new Set(DATA.map(x=>x[k]).filter(Boolean))].sort((a,b)=>a.localeCompare(b,"ar"));
uniq("s").forEach(v=>$("s").insertAdjacentHTML("beforeend",`<option>${esc(v)}</option>`));uniq("k").forEach(v=>$("k").insertAdjacentHTML("beforeend",`<option>${esc(v)}</option>`));
function render(){const q=$("q").value.trim(),s=$("s").value,k=$("k").value;const L=DATA.filter(x=>(!s||x.s===s)&&(!k||x.k===k)&&(!q||(x.t+x.s+x.f).includes(q)));
$("list").innerHTML=L.length?L.map(x=>`<div class="card" style="margin-bottom:10px"><div class="row" style="border:0;padding:0"><b>${esc(x.t)}</b><span class="chip">${esc(x.k)}</span><span class="chip blue">${esc(x.s)}</span><a class="btn" target="_blank" rel="noopener" href="${FILES_BASE}/api/resource?key=${encodeURIComponent(x.i)}">فتح</a></div><div class="muted">${esc(x.y)} · ${esc(x.m)} · ${esc(x.d)}</div></div>`).join(""):'<div class="empty">لا توجد موارد مطابقة.</div>';}
["q","s","k"].forEach(i=>$(i).addEventListener("input",render));render();''',"05-resources.html")
print("built",os.listdir(OUT),len(subj),nfiles,len(res),len(ann))
