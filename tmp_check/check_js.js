
/* в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
   INIT
в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ */
const tg = window.Telegram?.WebApp;
let user=null, prizes=[], rStat={}, selRt=null, cond={sub:false,fwd:false}, paidChoice={luck:20,count:1};

const CHANNELS=[
  {t:'CodeTMG',url:'https://t.me/CodeTMG'},
  {t:'SuperStars',url:'https://t.me/SuperStarsChanell'},
];
const PAID_LUCK_LEVELS=[20,30,40,50,60,70];
const PAID_COUNT_OPTIONS=[1,3,5];
const PAID_PRICES={20:50,30:100,40:150,50:200,60:250,70:300};
const PRIZES_CFG={
  day:[{n:'10в‚Ѕ',c:5},{n:'5в‚Ѕ',c:10},{n:'1в‚Ѕ',c:25},{n:'0.1в‚Ѕ',c:40},{n:'РќРёС‡РµРіРѕ',c:20}],
  three_days:[{n:'20в‚Ѕ',c:5},{n:'10в‚Ѕ',c:10},{n:'5в‚Ѕ',c:25},{n:'1в‚Ѕ',c:40},{n:'РќРёС‡РµРіРѕ',c:20}],
  week:[{n:'30в‚Ѕ',c:3},{n:'20в‚Ѕ',c:7},{n:'10в‚Ѕ',c:15},{n:'5в‚Ѕ',c:25},{n:'2.5в‚Ѕ',c:30},{n:'РќРёС‡РµРіРѕ',c:20}],
  paid:[{n:'РђРєРєР°СѓРЅС‚',c:5},{n:'Р“РѕР»РґР°',c:10},{n:'50в‚Ѕ',c:15},{n:'25в‚Ѕ',c:30},{n:'15в‚Ѕ',c:40}],
};
const RT_INFO={
  day:  {name:'Р•Р¶РµРґРЅРµРІРЅР°СЏ',sub:'РљР°Р¶РґС‹Рµ 24 С‡Р°СЃР°',ico:'day',cd:86400},
  three_days:{name:'РљР°Р¶РґС‹Рµ 3 РґРЅСЏ',sub:'Р Р°Р· РІ 3 РґРЅСЏ',ico:'three',cd:259200},
  week: {name:'Р•Р¶РµРЅРµРґРµР»СЊРЅР°СЏ',sub:'Р Р°Р· РІ 7 РґРЅРµР№',ico:'week',cd:604800},
  paid: {name:'РџР»Р°С‚РЅР°СЏ',sub:'20-70% СѓРґР°С‡Рё В· РѕС‚ 50в‚Ѕ',ico:'paid'},
};

const RT_SVGS={
  day:`<svg viewBox="0 0 24 24" fill="none" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg>`,
  three:`<svg viewBox="0 0 24 24" fill="none" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M23 4v6h-6"/><path d="M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.64A9 9 0 0 0 20.49 15"/></svg>`,
  week:`<svg viewBox="0 0 24 24" fill="none" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>`,
  paid:`<svg viewBox="0 0 24 24" fill="none" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M15 8.5H12.5C11.1 8.5 10 9.6 10 11s1.1 2.5 2.5 2.5H13c1.4 0 2.5 1.1 2.5 2.5S14.4 18.5 13 18.5H10"/><line x1="12" y1="7" x2="12" y2="20"/></svg>`,
};

// SVG icons for prize overlay
const PRIZE_ICONS={
  win:`<svg viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>`,
  money:`<svg viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M15 8.5H12.5C11.1 8.5 10 9.6 10 11s1.1 2.5 2.5 2.5H13c1.4 0 2.5 1.1 2.5 2.5S14.4 18.5 13 18.5H10"/><line x1="12" y1="7" x2="12" y2="20"/></svg>`,
  account:`<svg viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4M8 10v4"/><circle cx="15" cy="12" r="1"/><circle cx="18" cy="12" r="1"/></svg>`,
  nothing:`<svg viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
};

// Rank SVGs replacing medal emojis
const RANK_SVGS=[
  `<svg viewBox="0 0 24 24" class="rank-gold"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>`,
  `<svg viewBox="0 0 24 24" class="rank-silver"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5-2 4-2 4 2 4 2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>`,
  `<svg viewBox="0 0 24 24" class="rank-bronze"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2z"/></svg>`,
];

// Game controller icon for ldr-id
const GAME_ICON_SVG=`<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4M8 10v4"/><circle cx="15" cy="12" r="1"/><circle cx="18" cy="12" r="1"/></svg>`;

(function boot(){
  if(tg){tg.ready();tg.expand();tg.setHeaderColor('#03040e');tg.setBackgroundColor('#03040e');}
  let waited=0;
  const waitInit=setInterval(()=>{
    waited+=100;
    if(tg?.initData||waited>=2000){clearInterval(waitInit);loadUser();}
  },100);
})();

/* в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
   API
в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ */
async function api(path,opts={}){
  const r=await fetch('https://tankblitz.onrender.com'+path,{
    ...opts,
    headers:{'Content-Type':'application/json','X-Telegram-Init-Data':tg?.initData||'',...(opts.headers||{})},
  });
  if(!r.ok) throw new Error('HTTP '+r.status);
  return r.json();
}
const GET=p=>api(p);
const POST=(p,b)=>api(p,{method:'POST',body:JSON.stringify(b)});

/* в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
   USER
в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ */
async function loadUser(){
  try{
    const d=await GET('/api/user/me');
    if(!d.success){return d.blocked?showBlocked():null;}
    user=d.user;
    applyUser();
    loadPrizes();
  }catch(e){console.error(e);}
}

function applyUser(){
  if(!user)return;
  const ss=user.spin_stats||{};
  const bal=user.balance.toFixed(2);
  // header
  document.getElementById('hdr-bal').innerHTML=`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M15 8.5H12.5C11.1 8.5 10 9.6 10 11s1.1 2.5 2.5 2.5H13c1.4 0 2.5 1.1 2.5 2.5S14.4 18.5 13 18.5H10"/><line x1="12" y1="7" x2="12" y2="20"/></svg>${bal}в‚Ѕ`;
  // info page
  setTxt('hero-name',user.first_name||'РРіСЂРѕРє');
  document.getElementById('hero-bal').innerHTML=`${bal}<span>в‚Ѕ</span>`;
  countUp('st-spins',ss.total||0);
  countUp('st-wins',ss.wins||0);
  setTxt('st-best',(ss.biggest||0)>0?ss.biggest+'в‚Ѕ':'вЂ”');
  // profile
  const init=(user.first_name||'?')[0].toUpperCase();
  setTxt('prof-av',init);
  setTxt('prof-name',user.first_name||'вЂ”');
  setTxt('prof-user',user.username?'@'+user.username:'Р±РµР· username');
  document.getElementById('prof-bal').textContent=user.balance.toFixed(2);
  setTxt('pm-gid',user.game_id||'РќРµ СѓРєР°Р·Р°РЅ');
  setTxt('pm-joined',user.created_at||'вЂ”');
  setTxt('ps-spins',ss.total||0);
  setTxt('ps-wins',ss.wins||0);
  setTxt('ps-best',(ss.biggest||0)>0?ss.biggest+'в‚Ѕ':'вЂ”');
}

function countUp(id,target){
  const el=document.getElementById(id);
  if(!el)return;
  let cur=0;
  const step=Math.max(1,Math.ceil(target/30));
  const t=setInterval(()=>{
    cur=Math.min(cur+step,target);
    el.textContent=cur;
    if(cur>=target)clearInterval(t);
  },20);
}

/* в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
   PRIZES
в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ */
async function loadPrizes(){
  try{
    const d=await GET('/api/user/prizes');
    if(!d.success)return;
    prizes=(d.prizes||[]).filter(p=>p.prize_type!=='nothing');
    renderPrizes();
  }catch(e){}
}

function renderPrizes(){
  const cnt=prizes.length;
  setTxt('prizes-count',cnt);
  setTxt('pm-prizes',cnt+(cnt===1?' РїСЂРёР·':cnt>=2&&cnt<=4?' РїСЂРёР·Р°':' РїСЂРёР·РѕРІ'));

  const el=document.getElementById('prizes-list');
  if(!cnt){
    el.innerHTML=`<div class="empty-state">
      <div class="es-icon"><svg viewBox="0 0 24 24" fill="none" stroke-width="1.2" stroke-linecap="round"><polyline points="20,12 20,22 4,22 4,12"/><rect x="2" y="7" width="20" height="5"/><line x1="12" y1="22" x2="12" y2="7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/></svg></div>
      <div class="es-text">РџСЂРёР·РѕРІ РїРѕРєР° РЅРµС‚</div>
      <div class="es-sub">РљСЂСѓС‚РёС‚Рµ СЂСѓР»РµС‚РєСѓ Рё РІС‹РёРіСЂС‹РІР°Р№С‚Рµ!</div>
    </div>`;
    return;
  }

  el.innerHTML=prizes.slice(0,10).map((p,i)=>{
    const typ=p.prize_type;
    const icoClass=typ==='account'?'acc':typ==='gold'?'gld':'bal';
    const icoSvg=typ==='account'
      ?`<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4M8 10v4"/><circle cx="15" cy="12" r="1"/><circle cx="18" cy="12" r="1"/></svg>`
      :typ==='gold'
      ?`<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/></svg>`
      :`<svg viewBox="0 0 24 24" fill="none" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M15 8.5H12.5C11.1 8.5 10 9.6 10 11s1.1 2.5 2.5 2.5H13c1.4 0 2.5 1.1 2.5 2.5S14.4 18.5 13 18.5H10"/><line x1="12" y1="7" x2="12" y2="20"/></svg>`;
    const date=new Date(p.won_at).toLocaleDateString('ru',{day:'2-digit',month:'2-digit',year:'numeric'});
    const isActive=!p.is_received;
    const canClaim=isActive&&(typ==='account'||typ==='gold');
    const typLabel=typ==='account'?'РђРљРљРђРЈРќРў':typ==='gold'?'Р“РћР›Р”Рђ':'Р‘РђР›РђРќРЎ';
    const canTransfer=p.can_transfer&&isActive&&(typ==='account'||typ==='gold');
    return `<div class="prize-item" style="animation-delay:${i*55}ms">
      <div class="pi-icon ${icoClass}">${icoSvg}</div>
      <div class="pi-body">
        <div class="pi-name">${p.prize_name}</div>
        <div class="pi-meta"><span class="pi-date">${date}</span><span class="pi-type-tag">${typLabel}</span></div>
      </div>
      <div style="display:flex;flex-direction:column;gap:5px;flex-shrink:0">
      ${canClaim
        ?`<button class="btn btn-primary btn-sm" onclick="claimPrize(${p.id},'${typ}')">Р—Р°Р±СЂР°С‚СЊ</button>`
        :`<div class="pi-status ${isActive?'active':'done'}"><span class="status-dot"></span>${isActive?'РђРљРўРР’Р•Рќ':'РџРћР›РЈР§Р•Рќ'}</div>`}
      ${canTransfer?`<button class="btn btn-secondary btn-sm" style="font-size:10px;padding:5px 10px" onclick="openTransferModal(${p.id})">РџРµСЂРµРґР°С‚СЊ</button>`:''}
      </div>
    </div>`;
  }).join('');
}

/* в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
   ROULETTE PAGE
в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ */
async function loadRoulettePage(){
  document.getElementById('rt-grid').innerHTML='<div class="loading-state"><div class="ld-spin"></div> Р—Р°РіСЂСѓР·РєР°...</div>';
  try{
    const types=['day','three_days','week','paid'];
    const res=await Promise.allSettled(types.map(t=>{
      if(t==='paid'){
        return GET(`/api/roulette/status?type=paid&luck=${paidChoice.luck}&count=${paidChoice.count}`);
      }
      return GET(`/api/roulette/status?type=${t}`);
    }));
    rStat={};
    types.forEach((t,i)=>{
      rStat[t]=(res[i].status==='fulfilled'&&res[i].value.success)?res[i].value:{cooldown:0,conditions_met:false};
    });
    renderRt();
  }catch(e){
    document.getElementById('rt-grid').innerHTML='<div class="empty-state"><div class="es-text">РћС€РёР±РєР° Р·Р°РіСЂСѓР·РєРё</div></div>';
  }
}

function renderRt(){
  const el=document.getElementById('rt-grid');
  el.innerHTML=Object.entries(RT_INFO).map(([type,info],idx)=>{
    const st=rStat[type]||{};
    const isSel=selRt===type;
    let badge='',bc='';
    if(type==='paid'){
      const ok=user&&user.balance>=150;
      badge=ok?'Р”РѕСЃС‚СѓРїРЅР°':'РќРµС‚ СЃСЂРµРґСЃС‚РІ';
      bc=ok?'sb-ready':'sb-wait';
    }else{
      if(st.cooldown>0){badge=fmtTime(st.cooldown);bc='sb-wait';}
      else if(st.conditions_met){badge='Р“РѕС‚РѕРІРѕ!';bc='sb-ready';}
      else{badge='РЈСЃР»РѕРІРёСЏ';bc='sb-cond';}
    }
    return `<div class="rt-card${isSel?' sel':''}" onclick="pickRt('${type}')" style="animation:slideUp .35s ${idx*70}ms ease both">
      <div class="rt-orb"></div>
      <div class="rt-ico ${info.ico}">${RT_SVGS[info.ico]}</div>
      <div class="rt-info">
        <div class="rt-name">${info.name}</div>
        <div class="rt-sub">${info.sub}</div>
      </div>
      <div class="rt-right">
        <div class="status-badge ${bc}"><div class="sb-dot"></div>${badge}</div>
        ${st.cooldown>0?`<div class="rt-timer">Р§РµСЂРµР· ${fmtTime(st.cooldown)}</div>`:''}
      </div>
    </div>`;
  }).join('');
}

function pickRt(type){
  selRt=type;cond={sub:false,fwd:false};
  renderRt();
  openRtModal(type);
}

async function openRtModal(type){
  const st=rStat[type]||{};
  const info=RT_INFO[type];
  const prText=prizesHtml(type,st.prizes);

  if(type!=='paid'&&st.cooldown>0){
    showModal('РљСѓР»РґР°СѓРЅ',
      `<p class="modal-info">РЎР»РµРґСѓСЋС‰РёР№ РїСЂРѕРєСЂСѓС‚ С‡РµСЂРµР· <strong style="color:var(--nova)">${fmtTime(st.cooldown)}</strong></p>${prText}`,
      [{l:'Р—Р°РєСЂС‹С‚СЊ',a:'closeModal()',c:'btn-secondary btn-full'}],
      `<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg>`);
    return;
  }
  if(type==='paid'){
    openPaidModal();
    return;
  }
  if(st.conditions_met){
    showModal(info.name,
      `<p class="modal-info" style="color:var(--mint)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" width="14" height="14" style="vertical-align:middle;margin-right:5px"><polyline points="20,6 9,17 4,12"/></svg>
        Р’СЃРµ СѓСЃР»РѕРІРёСЏ РІС‹РїРѕР»РЅРµРЅС‹!
      </p>${prText}`,
      [{l:'РљСЂСѓС‚РёС‚СЊ!',a:`doSpin("${type}")`,c:'btn-primary',id:'spin-btn',
        icon:`<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>`},
       {l:'РћС‚РјРµРЅР°',a:'closeModal()',c:'btn-secondary'}],
      RT_SVGS[info.ico]);
    cond={sub:true,fwd:true};
  }else{
    showCondModal(type);
  }
}

/* в•ђв•ђ PAID ROULETTE MODAL в•ђв•ђ */
function _paidPrice(){return PAID_PRICES[paidChoice.luck]||50;}
function _paidTotal(){return _paidPrice()*paidChoice.count;}

function openPaidModal(){
  const price=_paidPrice();
  const total=_paidTotal();
  const bal=user?user.balance:0;
  const canAfford=bal>=total;
  const st=rStat['paid']||{};
  const prText=prizesHtml('paid',st.prizes);

  const luckPct=((PAID_LUCK_LEVELS.indexOf(paidChoice.luck)/(PAID_LUCK_LEVELS.length-1))*100).toFixed(0);

  const body=`
  <div class="paid-controls">
    <div class="pc-section">
      <div class="pc-label">
        РЁР°РЅСЃ СѓРґР°С‡Рё
        <span class="pc-label-val" id="luck-val-lbl">${paidChoice.luck}%</span>
      </div>
      <div class="luck-slider-wrap">
        <input type="range" class="luck-slider" id="luck-slider"
          min="0" max="${PAID_LUCK_LEVELS.length-1}" step="1"
          value="${PAID_LUCK_LEVELS.indexOf(paidChoice.luck)}"
          oninput="onLuckSlide(this.value)">
        <div class="luck-ticks" id="luck-ticks">
          ${PAID_LUCK_LEVELS.map((l,i)=>`<span class="luck-tick${l===paidChoice.luck?' active':''}" id="lt-${i}">${l}%</span>`).join('')}
        </div>
      </div>
    </div>
    <div class="pc-section">
      <div class="pc-label">РљРѕР»РёС‡РµСЃС‚РІРѕ РїСЂРѕРєСЂСѓС‚РѕРІ</div>
      <div class="count-btns">
        ${PAID_COUNT_OPTIONS.map(n=>`<div class="count-btn${n===paidChoice.count?' sel':''}" onclick="onCountPick(${n})">${n}Г—</div>`).join('')}
      </div>
    </div>
  </div>
  <div class="paid-price-row" id="paid-price-row">
    <div>
      <div class="ppr-left">Рљ РѕРїР»Р°С‚Рµ</div>
      <div class="ppr-sub" id="ppr-sub">${price}в‚Ѕ Г— ${paidChoice.count} = ${total}в‚Ѕ</div>
    </div>
    <div class="ppr-right" id="ppr-total">${total}в‚Ѕ</div>
  </div>
  ${!canAfford?`<p class="modal-info" style="color:var(--red);margin-bottom:8px">РќРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ СЃСЂРµРґСЃС‚РІ (${bal.toFixed(2)}в‚Ѕ). <a href="https://t.me/CodeTMG" style="color:var(--iris3)">РџРѕРїРѕР»РЅРёС‚СЊ</a></p>`:''}
  ${prText}`;

  showModal('РџР»Р°С‚РЅР°СЏ СЂСѓР»РµС‚РєР°',body,
    canAfford
      ?[{l:`РљСЂСѓС‚РёС‚СЊ Р·Р° ${total}в‚Ѕ`,a:'doSpinPaid()',c:'btn-primary',id:'spin-btn',
          icon:`<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>`},
        {l:'РћС‚РјРµРЅР°',a:'closeModal()',c:'btn-secondary'}]
      :[{l:'РџРѕРЅСЏС‚РЅРѕ',a:'closeModal()',c:'btn-secondary btn-full'}],
    `<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M15 8.5H12.5C11.1 8.5 10 9.6 10 11s1.1 2.5 2.5 2.5H13c1.4 0 2.5 1.1 2.5 2.5S14.4 18.5 13 18.5H10"/><line x1="12" y1="7" x2="12" y2="20"/></svg>`
  );
  // Apply slider gradient fill after render
  setTimeout(()=>_updateSliderFill(document.getElementById('luck-slider')),30);
}

function onLuckSlide(idx){
  const lvl=PAID_LUCK_LEVELS[parseInt(idx)];
  paidChoice.luck=lvl;
  const lbl=document.getElementById('luck-val-lbl');
  if(lbl)lbl.textContent=lvl+'%';
  // update active tick
  PAID_LUCK_LEVELS.forEach((_,i)=>{
    const el=document.getElementById('lt-'+i);
    if(el)el.className='luck-tick'+(i===parseInt(idx)?' active':'');
  });
  _updatePaidPriceRow();
  // update slider fill
  _updateSliderFill(document.getElementById('luck-slider'));
}

function _updateSliderFill(el){
  if(!el)return;
  const pct=(parseInt(el.value)/(PAID_LUCK_LEVELS.length-1)*100).toFixed(1);
  el.style.background=`linear-gradient(to right,var(--iris) 0%,var(--plasma) ${pct}%,rgba(255,255,255,.1) ${pct}%)`;
}

function onCountPick(n){
  paidChoice.count=n;
  document.querySelectorAll('.count-btn').forEach(b=>{
    b.className='count-btn'+(parseInt(b.textContent)===n?' sel':'');
  });
  _updatePaidPriceRow();
}

function _updatePaidPriceRow(){
  const price=_paidPrice();
  const total=_paidTotal();
  const sub=document.getElementById('ppr-sub');
  const tot=document.getElementById('ppr-total');
  const spinBtn=document.getElementById('spin-btn');
  if(sub)sub.textContent=`${price}в‚Ѕ Г— ${paidChoice.count} = ${total}в‚Ѕ`;
  if(tot)tot.textContent=total+'в‚Ѕ';
  if(spinBtn)spinBtn.innerHTML=`<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>РљСЂСѓС‚РёС‚СЊ Р·Р° ${total}в‚Ѕ`;
  const canAfford=user&&user.balance>=total;
  if(spinBtn)spinBtn.disabled=!canAfford;
}

function doSpinPaid(){
  closeModal();
  doSpin('paid');
}

function showCondModal(type){
  const info=RT_INFO[type];
  const st=rStat[type]||{};
  const si=cond.sub,fi=cond.fwd;
  const chkOk=`<svg viewBox="0 0 24 24"><polyline points="20,6 9,17 4,12"/></svg>`;
  const chkNo=`<svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;
  const chHtml=CHANNELS.map(ch=>`<div class="cond-row">
    <div class="cond-check ${si?'ok':'no'}">${si?chkOk:chkNo}</div>
    <div class="cond-text">РџРѕРґРїРёСЃРєР° РЅР° ${ch.t}</div>
    <a href="${ch.url}" target="_blank" class="cond-link">РџРµСЂРµР№С‚Рё</a>
  </div>`).join('');
  const body=`
    <p class="modal-info">Р’С‹РїРѕР»РЅРёС‚Рµ СѓСЃР»РѕРІРёСЏ РґР»СЏ РїСЂРѕРєСЂСѓС‚Р°:</p>
    ${chHtml}
    <div class="cond-row">
      <div class="cond-check ${fi?'ok':'no'}">${fi?chkOk:chkNo}</div>
      <div class="cond-text">РџРµСЂРµС€Р»РёС‚Рµ СЃРѕРѕР±С‰РµРЅРёРµ 3 РґСЂСѓР·СЊСЏРј</div>
    </div>
    ${prizesHtml(type,st.prizes)}`;
  const btns=[];
  if(!si||!fi){
    btns.push({l:'РЇ РІС‹РїРѕР»РЅРёР» СѓСЃР»РѕРІРёСЏ',a:`chkCond("${type}")`,c:'btn-primary btn-full',id:'cond-btn',
      icon:`<svg viewBox="0 0 24 24" fill="none" stroke-width="2.2" stroke-linecap="round"><polyline points="20,6 9,17 4,12"/></svg>`});
  }else{
    btns.push({l:'РљСЂСѓС‚РёС‚СЊ!',a:`doSpin("${type}")`,c:'btn-primary',id:'spin-btn',
      icon:`<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>`});
  }
  btns.push({l:'РћС‚РјРµРЅР°',a:'closeModal()',c:'btn-secondary'});
  showModal(info.name,body,btns,RT_SVGS[info.ico]);
}

async function chkCond(type){
  const btn=document.getElementById('cond-btn');
  if(btn){btn.disabled=true;btn.textContent='РџСЂРѕРІРµСЂСЏРµРј...';}
  try{
    const d=await POST('/api/roulette/check-conditions',{type,forwarded:true});
    cond={sub:d.subscribed,fwd:d.forwarded};
    if(d.conditions_met){
        rStat[type]={...(rStat[type]||{}),conditions_met:true};
        closeModal();
        const info=RT_INFO[type];
        const st2=rStat[type]||{};
        const chkSvg=`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" width="14" height="14" style="vertical-align:middle;margin-right:4px"><polyline points="20,6 9,17 4,12"/></svg>`;
        showModal(info.name,
          `<p class="modal-info" style="color:var(--mint)">${chkSvg}Р’СЃРµ СѓСЃР»РѕРІРёСЏ РІС‹РїРѕР»РЅРµРЅС‹!</p>${prizesHtml(type,st2.prizes)}`,
        [{l:'РљСЂСѓС‚РёС‚СЊ!',a:`doSpin("${type}")`,c:'btn-primary',id:'spin-btn',
          icon:`<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>`},
         {l:'РћС‚РјРµРЅР°',a:'closeModal()',c:'btn-secondary'}],
        RT_SVGS[info.ico]);
    }else{
      if(!d.subscribed)toast('РџРѕРґРїРёС€РёС‚РµСЃСЊ РЅР° РІСЃРµ РєР°РЅР°Р»С‹','err');
      else toast('РџРµСЂРµС€Р»РёС‚Рµ СЃРѕРѕР±С‰РµРЅРёРµ РґСЂСѓР·СЊСЏРј','err');
      showCondModal(type);
    }
  }catch(e){toast('РћС€РёР±РєР° СЃРѕРµРґРёРЅРµРЅРёСЏ','err');}
}

/* в•ђв•ђ SLOT MACHINE ANIMATION в•ђв•ђ */
const SLOT_ICONS={
  balance:`<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M15 8.5H12.5C11.1 8.5 10 9.6 10 11s1.1 2.5 2.5 2.5H13c1.4 0 2.5 1.1 2.5 2.5S14.4 18.5 13 18.5H10"/><line x1="12" y1="7" x2="12" y2="20"/></svg>`,
  account:`<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4M8 10v4"/><circle cx="15" cy="12" r="1"/><circle cx="18" cy="12" r="1"/></svg>`,
  gold:`<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/></svg>`,
  nothing:`<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`,
};

function _slotItemHtml(p){
  const t=p.type||'nothing';
  const ico=SLOT_ICONS[t]||SLOT_ICONS.nothing;
  return `<div class="slot-item">
    <div class="slot-item-ico t-${t}">${ico}</div>
    <div class="slot-item-name">${p.name||'РќРёС‡РµРіРѕ'}</div>
  </div>`;
}

function startSlotAnimation(prizes,winnerPrize){
  const reel=document.getElementById('slot-reel');
  if(!reel)return;

  // Build a long list: random items + winner at a fixed position near end
  const allPrizes=prizes.length?prizes:[{name:'РќРёС‡РµРіРѕ',type:'nothing'}];
  const items=[];
  // 30 random items for illusion of spinning
  for(let i=0;i<30;i++){
    items.push(allPrizes[Math.floor(Math.random()*allPrizes.length)]);
  }
  // winner lands at index 28
  items[28]=winnerPrize;

  reel.innerHTML=items.map(_slotItemHtml).join('');
  reel.style.transition='none';
  reel.style.transform='translateY(15px)'; // start offset

  const itemH=50;
  const targetIdx=28;
  const targetY=-(targetIdx*itemH)+15; // center item in 80px viewport (80/2-25=-15+15=0 => center)
  const centerOffset=(80/2)-25; // 15px
  const finalY=-(targetIdx*itemH)+centerOffset;

  // Start scroll after brief delay
  setTimeout(()=>{
    reel.style.transition=`transform 2.6s cubic-bezier(.08,.85,.1,1)`;
    reel.style.transform=`translateY(${finalY}px)`;
  },80);
}

async function doSpin(type){
  const btn=document.getElementById('spin-btn');
  if(btn)btn.disabled=true;
  showSpinOv();

  // Set spin text
  const spinText=document.getElementById('spin-text');
  if(spinText)spinText.textContent=type==='paid'?`РљСЂСѓС‚РёРј ${paidChoice.count}Г—...`:'РљСЂСѓС‚РёРј СЂСѓР»РµС‚РєСѓ...';

  try{
    const spinBody={type};
    if(type==='paid'){spinBody.luck=paidChoice.luck;spinBody.count=paidChoice.count;}
    const[d]=await Promise.all([
      POST('/api/roulette/spin',spinBody),
      sleep(800), // wait a bit before starting animation
    ]);
    if(!d.success){
      hideSpinOv();
      toast(d.error||'РћС€РёР±РєР° РїСЂРѕРєСЂСѓС‚Р°','err');
      await loadRoulettePage();
      return;
    }
    // Determine prizes list for animation
    const prizesForAnim=(rStat[type]&&rStat[type].prizes)||PRIZES_CFG[type]?.map(p=>({name:p.n,type:'balance'}))||[];
    const winner=d.prize;
    startSlotAnimation(prizesForAnim,winner);

    await sleep(2800); // wait for animation
    hideSpinOv();
    if(d.user)user.balance=d.user.balance;
    renderUserBal();
    await loadRoulettePage();
    showPrize(d,type);
    loadPrizes();
  }catch(e){
    hideSpinOv();
    toast('РћС€РёР±РєР° СЃРѕРµРґРёРЅРµРЅРёСЏ','err');
    await loadRoulettePage();
  }
}

function renderUserBal(){
  if(!user)return;
  const bal=user.balance.toFixed(2);
  document.getElementById('hdr-bal').innerHTML=`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M15 8.5H12.5C11.1 8.5 10 9.6 10 11s1.1 2.5 2.5 2.5H13c1.4 0 2.5 1.1 2.5 2.5S14.4 18.5 13 18.5H10"/><line x1="12" y1="7" x2="12" y2="20"/></svg>${bal}в‚Ѕ`;
  document.getElementById('hero-bal').innerHTML=`${bal}<span>в‚Ѕ</span>`;
  document.getElementById('prof-bal').textContent=user.balance.toFixed(2);
}

function showPrize(d,type){
  // d is full API response: {prize, results, count, ...}
  const pr=d.prize||d; // support both call styles
  const results=d.results||[pr];
  const count=d.count||1;
  const nothing=pr.type==='nothing';
  const ov=document.getElementById('prize-overlay');
  const iconWrap=document.getElementById('po-icon');

  document.getElementById('po-badge').textContent=nothing?'РџРѕРїС‹С‚РєР°':(RT_INFO[type]?.name||'Р СѓР»РµС‚РєР°')+(count>1?` Г— ${count}`:'');

  let iconSvg;
  if(nothing){
    iconSvg=PRIZE_ICONS.nothing;
    iconWrap.className='po-icon-wrap';
  }else if(pr.type==='balance'){
    iconSvg=PRIZE_ICONS.money;
    iconWrap.className='po-icon-wrap win';
  }else if(pr.type==='account'){
    iconSvg=PRIZE_ICONS.account;
    iconWrap.className='po-icon-wrap win';
  }else{
    iconSvg=PRIZE_ICONS.win;
    iconWrap.className='po-icon-wrap win';
  }
  iconWrap.innerHTML=iconSvg;

  // If multiple spins вЂ” show summary
  if(count>1&&results.length>1){
    const wins=results.filter(r=>r.type!=='nothing');
    document.getElementById('po-title').textContent=wins.length?`Р’С‹РёРіСЂР°РЅРѕ ${wins.length} РёР· ${count}!`:`${count} РїРѕРїС‹С‚РѕРє вЂ” РЅРµ РїРѕРІРµР·Р»Рѕ`;
    document.getElementById('po-amount').textContent=wins.length?wins.map(r=>r.name).join(', '):'';
    document.getElementById('po-sub').textContent=wins.length?'РџСЂРѕРІРµСЂСЊС‚Рµ СЂР°Р·РґРµР» В«РњРѕРё РїСЂРёР·С‹В»':'РџРѕРїСЂРѕР±СѓР№С‚Рµ РµС‰С‘ СЂР°Р·!';
  }else{
    document.getElementById('po-title').textContent=nothing?'РќРµ РїРѕРІРµР·Р»Рѕ...':'РџРѕР·РґСЂР°РІР»СЏРµРј!';
    document.getElementById('po-amount').textContent=nothing?'':(pr.type==='balance'?'+'+pr.value+'в‚Ѕ':pr.name);
    document.getElementById('po-sub').textContent=nothing?'РџРѕРїСЂРѕР±СѓР№С‚Рµ РµС‰С‘ СЂР°Р·!':pr.type==='balance'?'Р—Р°С‡РёСЃР»РµРЅРѕ РЅР° Р±Р°Р»Р°РЅСЃ':'РџСЂРѕРІРµСЂСЊС‚Рµ СЂР°Р·РґРµР» В«РњРѕРё РїСЂРёР·С‹В»';
  }

  const acts=document.getElementById('po-actions');
  acts.innerHTML='';

  // Collect claimable prizes from results
  const claimables=results.filter(r=>r.can_claim&&r.prize_id&&(r.type==='account'||r.type==='gold'));
  const transferables=results.filter(r=>r.can_transfer&&r.prize_id&&(r.type==='account'||r.type==='gold'));

  if(claimables.length){
    const b=document.createElement('button');
    b.className='btn btn-primary btn-full';
    b.innerHTML=`<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7,10 12,15 17,10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>Р—Р°Р±СЂР°С‚СЊ РїСЂРёР·`;
    b.onclick=()=>{closePrize();claimPrize(claimables[0].prize_id,claimables[0].type);};
    acts.appendChild(b);
  }

  if(transferables.length){
    const bt=document.createElement('button');
    bt.className='btn btn-secondary btn-full';
    bt.innerHTML=`<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><path d="M22 2L11 13"/><path d="M22 2L15 22l-4-9-9-4 20-7z"/></svg>РџРµСЂРµРґР°С‚СЊ РїСЂРёР·`;
    bt.onclick=()=>{closePrize();openTransferModal(transferables[0].prize_id);};
    acts.appendChild(bt);
  }

  const close=document.createElement('button');
  close.className='btn btn-secondary btn-full';
  close.textContent='Р—Р°РєСЂС‹С‚СЊ';
  close.onclick=closePrize;
  acts.appendChild(close);

  if(!nothing)spawnConfetti();
  ov.classList.add('on');
}

function closePrize(){
  document.getElementById('prize-overlay').classList.remove('on');
  document.getElementById('confetti-field').innerHTML='';
}
function showSpinOv(){document.getElementById('spin-overlay').classList.add('on')}
function hideSpinOv(){document.getElementById('spin-overlay').classList.remove('on')}

/* в•ђв•ђ TRANSFER PRIZE в•ђв•ђ */
function openTransferModal(prizeId){
  showModal('РџРµСЂРµРґР°С‚СЊ РїСЂРёР·',
    `<p class="modal-info">Р’РІРµРґРёС‚Рµ Telegram ID РёР»Рё @username РїРѕР»СѓС‡Р°С‚РµР»СЏ:</p>
     <input class="modal-input" id="transfer-inp" placeholder="@username РёР»Рё 123456789" maxlength="40">
     <p class="modal-info" style="margin-top:10px;color:var(--muted2)">РџРµСЂРµРґР°С‡Р° РґРѕСЃС‚СѓРїРЅР° С‡РµСЂРµР· 2 С‡Р°СЃР° РїРѕСЃР»Рµ РІС‹РёРіСЂС‹С€Р°</p>`,
    [{l:'РџРµСЂРµРґР°С‚СЊ',a:`confirmTransfer(${prizeId})`,c:'btn-primary',id:'transfer-btn',
       icon:`<svg viewBox="0 0 24 24" fill="none" stroke-width="2.2" stroke-linecap="round"><path d="M22 2L11 13"/><path d="M22 2L15 22l-4-9-9-4 20-7z"/></svg>`},
     {l:'РћС‚РјРµРЅР°',a:'closeModal()',c:'btn-secondary'}],
    `<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><path d="M22 2L11 13"/><path d="M22 2L15 22l-4-9-9-4 20-7z"/></svg>`
  );
  setTimeout(()=>document.getElementById('transfer-inp')?.focus(),80);
}

async function confirmTransfer(prizeId){
  const btn=document.getElementById('transfer-btn');
  const inp=document.getElementById('transfer-inp');
  const target=(inp?.value||'').trim().replace('@','');
  if(!target){toast('Р’РІРµРґРёС‚Рµ РїРѕР»СѓС‡Р°С‚РµР»СЏ','err');return;}
  if(btn){btn.disabled=true;btn.textContent='РџРµСЂРµРґР°С‘Рј...';}
  try{
    const d=await POST('/api/user/transfer-prize',{prize_id:prizeId,target});
    if(d.success){closeModal();toast('РџСЂРёР· РїРµСЂРµРґР°РЅ!');loadPrizes();}
    else{toast(d.error||'РћС€РёР±РєР°','err');if(btn){btn.disabled=false;btn.innerHTML=`<svg viewBox="0 0 24 24" fill="none" stroke-width="2.2" stroke-linecap="round"><path d="M22 2L11 13"/><path d="M22 2L15 22l-4-9-9-4 20-7z"/></svg>РџРµСЂРµРґР°С‚СЊ`;}}
  }catch(e){toast('РћС€РёР±РєР° СЃРѕРµРґРёРЅРµРЅРёСЏ','err');}
}

/* в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
   LEADERS
в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ */
async function loadLeaders(){
  const el=document.getElementById('ldrs-list');
  el.innerHTML='<div class="loading-state"><div class="ld-spin"></div> Р—Р°РіСЂСѓР·РєР°...</div>';
  try{
    const d=await GET('/api/leaders');
    if(!d.success||!d.leaders.length){
      el.innerHTML='<div class="empty-state"><div class="es-text">РџРѕРєР° РЅРµС‚ РґР°РЅРЅС‹С…</div></div>';
      return;
    }
    el.innerHTML=d.leaders.map((u,i)=>{
      const name=u.first_name||(u.username?'@'+u.username:'РРіСЂРѕРє');
      const init=name[0].toUpperCase();
      const isMe=user&&u.telegram_id===user.telegram_id;
      let rankHtml;
      if(i<3){
        rankHtml=`<div class="ldr-rank ${i===0?'r1':i===1?'r2':'r3'}">${RANK_SVGS[i]}</div>`;
      }else{
        rankHtml=`<div class="ldr-rank"><span class="rn">#${i+1}</span></div>`;
      }
      return `<div class="ldr-card${isMe?' me':''}" style="animation-delay:${i*50}ms">
        ${rankHtml}
        <div class="ldr-av">${init}</div>
        <div class="ldr-body">
          <div class="ldr-name">${name}${isMe?' <span style="color:var(--iris3);font-size:11px;font-weight:700">(Р’С‹)</span>':''}</div>
          <div class="ldr-id">${GAME_ICON_SVG}${u.game_id?u.game_id:'ID: '+u.telegram_id}</div>
        </div>
        <div class="ldr-bal">${u.balance.toFixed(2)}в‚Ѕ</div>
      </div>`;
    }).join('');
  }catch(e){el.innerHTML='<div class="empty-state"><div class="es-text">РћС€РёР±РєР° Р·Р°РіСЂСѓР·РєРё</div></div>';}
}

/* в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
   PROFILE
в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ */
function openEditId(){
  showModal('Game ID',
    `<p class="modal-info">РўРµРєСѓС‰РёР№ ID: <strong>${user?.game_id||'РќРµ СѓРєР°Р·Р°РЅ'}</strong></p>
     <input class="modal-input" id="gid-inp" placeholder="Р’РІРµРґРёС‚Рµ Game ID..." maxlength="30" value="${user?.game_id||''}">`,
    [{l:'РЎРѕС…СЂР°РЅРёС‚СЊ',a:'saveId()',c:'btn-primary',
      icon:`<svg viewBox="0 0 24 24" fill="none" stroke-width="2.2" stroke-linecap="round"><polyline points="20,6 9,17 4,12"/></svg>`},
     {l:'РћС‚РјРµРЅР°',a:'closeModal()',c:'btn-secondary'}],
    `<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>`);
  setTimeout(()=>document.getElementById('gid-inp')?.focus(),80);
}
async function saveId(){
  const v=document.getElementById('gid-inp')?.value?.trim()||'';
  if(v.length<3){toast('РњРёРЅРёРјСѓРј 3 СЃРёРјРІРѕР»Р°','err');return;}
  try{
    const d=await POST('/api/user/set-game-id',{game_id:v});
    if(d.success){user.game_id=v;applyUser();closeModal();toast('Game ID РѕР±РЅРѕРІР»С‘РЅ');}
    else toast(d.error||'РћС€РёР±РєР°','err');
  }catch(e){toast('РћС€РёР±РєР° СЃРѕРµРґРёРЅРµРЅРёСЏ','err');}
}

async function claimPrize(id,type){
  showModal('РџРѕР»СѓС‡РёС‚СЊ РїСЂРёР·',
    `<p class="modal-info">Р”Р°РЅРЅС‹Рµ Р±СѓРґСѓС‚ РїРѕРєР°Р·Р°РЅС‹ С‚РѕР»СЊРєРѕ РѕРґРёРЅ СЂР°Р·. РЎРѕС…СЂР°РЅРёС‚Рµ РёС…!</p>`,
    [{l:'РџРѕР»СѓС‡РёС‚СЊ',a:`confirmClaim(${id})`,c:'btn-primary',id:'claim-btn',
      icon:`<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7,10 12,15 17,10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`},
     {l:'РћС‚РјРµРЅР°',a:'closeModal()',c:'btn-secondary'}],
    `<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7,10 12,15 17,10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`);
}
async function confirmClaim(id){
  const btn=document.getElementById('claim-btn');
  if(btn){btn.disabled=true;btn.textContent='Р—Р°РіСЂСѓР·РєР°...';}
  try{
    const d=await POST('/api/user/claim-prize',{prize_id:id});
    closeModal();
    if(d.success){
      const dd=d.data||{};
      const emailIcon=`<svg viewBox="0 0 24 24" fill="none" stroke="var(--nova)" stroke-width="1.8" stroke-linecap="round" width="14" height="14" style="vertical-align:middle;margin-right:4px"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="22,4 12,13 2,4"/></svg>`;
      const keyIcon=`<svg viewBox="0 0 24 24" fill="none" stroke="var(--nova)" stroke-width="1.8" stroke-linecap="round" width="14" height="14" style="vertical-align:middle;margin-right:4px"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>`;
      const ticketIcon=`<svg viewBox="0 0 24 24" fill="none" stroke="var(--nova)" stroke-width="1.8" stroke-linecap="round" width="14" height="14" style="vertical-align:middle;margin-right:4px"><path d="M15 5v2M15 11v2M15 17v2M5 5h14a2 2 0 0 1 2 2v3a2 2 0 0 0 0 4v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-3a2 2 0 0 0 0-4V7a2 2 0 0 1 2-2z"/></svg>`;
      if(dd.email){
        showModal('РђРєРєР°СѓРЅС‚ Tank Blitz',
          `<p class="modal-info">РЎРѕС…СЂР°РЅРёС‚Рµ РґР°РЅРЅС‹Рµ, СЃРјРµРЅРёС‚Рµ РїР°СЂРѕР»СЊ РїРѕСЃР»Рµ РІС…РѕРґР°!</p>
           <div class="modal-code-box">${emailIcon}${dd.email}<br>${keyIcon}${dd.password}</div>`,
          [{l:'РџРѕРЅСЏС‚РЅРѕ',a:'closeModal()',c:'btn-primary btn-full'}],
          `<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 12h4M8 10v4"/><circle cx="15" cy="12" r="1"/><circle cx="18" cy="12" r="1"/></svg>`);
      }else if(dd.promo){
        showModal('РџСЂРѕРјРѕРєРѕРґ РЅР° Р“РѕР»РґСѓ',
          `<p class="modal-info">Р’РІРµРґРёС‚Рµ РїСЂРѕРјРѕРєРѕРґ РІ РёРіСЂРµ:</p>
           <div class="modal-code-box">${ticketIcon}${dd.promo}</div>`,
          [{l:'РџРѕРЅСЏС‚РЅРѕ',a:'closeModal()',c:'btn-primary btn-full'}],
          `<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>`);
      }else{
        toast('РџСЂРёР· РїРѕР»СѓС‡РµРЅ!');
      }
      loadPrizes();
    }else toast(d.error||'РћС€РёР±РєР°','err');
  }catch(e){toast('РћС€РёР±РєР° СЃРѕРµРґРёРЅРµРЅРёСЏ','err');}
}

function openHelp(){
  showModal('РџРѕРјРѕС‰СЊ',
    `<p class="modal-info"><strong style="color:var(--text)">РљР°Рє СЂР°Р±РѕС‚Р°РµС‚ СЂСѓР»РµС‚РєР°?</strong><br>Р’С‹Р±РµСЂРёС‚Рµ С‚РёРї, РІС‹РїРѕР»РЅРёС‚Рµ СѓСЃР»РѕРІРёСЏ вЂ” РїРѕРґРїРёС€РёС‚РµСЃСЊ РЅР° РєР°РЅР°Р»С‹ Рё РїРµСЂРµС€Р»РёС‚Рµ СЃРѕРѕР±С‰РµРЅРёРµ 3 РґСЂСѓР·СЊСЏРј.</p>
     <p class="modal-info"><strong style="color:var(--text)">Р§С‚Рѕ СЃ РїСЂРёР·РѕРј?</strong><br>Р‘Р°Р»Р°РЅСЃ Р·Р°С‡РёСЃР»СЏРµС‚СЃСЏ СЃСЂР°Р·Сѓ. РђРєРєР°СѓРЅС‚С‹ Рё РіРѕР»РґСѓ РЅР°Р¶РјРёС‚Рµ В«Р—Р°Р±СЂР°С‚СЊВ» РІ СЂР°Р·РґРµР»Рµ РРЅС„Рѕ.</p>
     <p class="modal-info"><strong style="color:var(--text)">Р’РѕРїСЂРѕСЃС‹?</strong><br><a href="https://t.me/CodeTMG">@CodeTMG</a></p>`,
    [{l:'РџРѕРЅСЏС‚РЅРѕ',a:'closeModal()',c:'btn-primary btn-full'}],
    `<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`);
}

/* в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
   NAVIGATION
в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ */
let curPage='info';
function showPage(name){
  if(name==='roulette'||name!==curPage){
    curPage=name;
    document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
    const pg=document.getElementById('page-'+name);
    if(pg)pg.classList.add('active');
    document.querySelectorAll('.nav-item,.nav-spin').forEach(b=>{
      b.classList.remove('active');
    });
    const navEl=document.getElementById('nav-'+name)||document.getElementById('nav-roulette');
    if(navEl)navEl.classList.add('active');
    if(name==='roulette')loadRoulettePage();
    else if(name==='leaders')loadLeaders();
  }
}

/* в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
   MODAL
в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ */
function showModal(title,body,btns=[],titleIconSvg=null){
  const bg=document.getElementById('modal-bg');
  const titleEl=document.getElementById('modal-title');
  if(titleIconSvg){
    titleEl.innerHTML=`<div class="modal-title-icon">${titleIconSvg}</div>${title}`;
  }else{
    titleEl.textContent=title;
  }
  document.getElementById('modal-body').innerHTML=body;
  const footer=document.getElementById('modal-footer');
  footer.innerHTML='';
  btns.forEach(b=>{
    const el=document.createElement('button');
    el.className='btn '+b.c;
    if(b.id)el.id=b.id;
    el.onclick=new Function(b.a);
    if(b.icon){el.innerHTML=b.icon+b.l;}
    else{el.textContent=b.l;}
    footer.appendChild(el);
  });
  bg.classList.add('open');
}
function closeModal(){document.getElementById('modal-bg').classList.remove('open')}
function closeBg(e){if(e.target===document.getElementById('modal-bg'))closeModal()}

/* в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
   PRIZES HTML HELPER
в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ */
function prizesHtml(type, apiPrizes){
  // Prefer live prizes from API (they have real chances including luck adjustments)
  if(apiPrizes&&apiPrizes.length){
    const rows=apiPrizes.map(p=>`<div>
      <div class="pt-dot"></div>
      <span class="pt-name">${p.name}</span>
      <span class="pt-pct">${p.chance}%</span>
    </div>`).join('');
    return`<div class="prizes-text">${rows}</div>`;
  }
  const cfg=PRIZES_CFG[type]||[];
  if(!cfg.length)return'';
  const rows=cfg.map(p=>`<div>
    <div class="pt-dot"></div>
    <span class="pt-name">${p.n}</span>
    <span class="pt-pct">${p.c}%</span>
  </div>`).join('');
  return`<div class="prizes-text">${rows}</div>`;
}

/* в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
   CONFETTI
в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ */
function spawnConfetti(){
  const field=document.getElementById('confetti-field');
  const colors=['#7c5ef9','#be74ff','#f7cb45','#26e89a','#00e5ff','#ff4060','#fff'];
  for(let i=0;i<70;i++){
    const el=document.createElement('div');
    el.className='cf';
    const x=Math.random()*100;
    const size=Math.random()*10+5;
    const dur=Math.random()*2+1.5;
    const del=Math.random()*1.2;
    const color=colors[Math.floor(Math.random()*colors.length)];
    el.style.cssText=`left:${x}%;width:${size}px;height:${size*(Math.random()>.5?.4:1)}px;background:${color};border-radius:${Math.random()>.5?'50%':'2px'};animation-duration:${dur}s;animation-delay:${del}s;transform-origin:center;`;
    field.appendChild(el);
    setTimeout(()=>el.remove(),(dur+del)*1000+200);
  }
}

/* в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
   TOAST
в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ */
let toastTimer=null;
function toast(msg,type='ok'){
  const t=document.getElementById('toast');
  const icon=document.getElementById('toast-icon');
  const text=document.getElementById('toast-text');
  t.className=type==='err'?'err':'ok';
  if(type==='err'){
    icon.innerHTML='<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>';
  }else{
    icon.innerHTML='<polyline points="20,6 9,17 4,12"/>';
  }
  text.textContent=msg;
  t.classList.add('show');
  if(toastTimer)clearTimeout(toastTimer);
  toastTimer=setTimeout(()=>t.classList.remove('show'),2600);
}

/* в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ
   UTILS
в•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђв•ђ */
function setTxt(id,v){const e=document.getElementById(id);if(e)e.textContent=v}
function sleep(ms){return new Promise(r=>setTimeout(r,ms))}
function fmtTime(s){
  const h=Math.floor(s/3600),m=Math.floor((s%3600)/60),sec=s%60;
  if(h>0)return`${h}С‡ ${m}Рј`;
  if(m>0)return`${m}Рј ${sec}СЃ`;
  return`${sec}СЃ`;
}
function showBlocked(){
  document.getElementById('app').innerHTML=`
    <div class="blocked-wrap">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>
      <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;margin-bottom:8px">Р”РѕСЃС‚СѓРї Р·Р°РєСЂС‹С‚</div>
      <div style="color:var(--muted2);font-size:13px;font-family:'Space Grotesk',sans-serif">Р’С‹ Р·Р°Р±Р»РѕРєРёСЂРѕРІР°РЅС‹. РћР±СЂР°С‚РёС‚РµСЃСЊ РІ РїРѕРґРґРµСЂР¶РєСѓ.</div>
    </div>`;
}

/* Cooldown countdown updater */
setInterval(()=>{
  Object.keys(rStat).forEach(t=>{
    if(rStat[t].cooldown>0){
      rStat[t].cooldown=Math.max(0,rStat[t].cooldown-1);
    }
  });
  if(curPage==='roulette')renderRt();
},1000);

