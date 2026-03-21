const DB=[
  {id:'led_bulb',name:'LED Bulb',icon:'💡',w:10,cat:'Lighting',daily:true},
  {id:'cfl_bulb',name:'CFL Bulb',icon:'💡',w:20,cat:'Lighting',daily:true},
  {id:'tube_light',name:'Tube Light (36W)',icon:'💡',w:36,cat:'Lighting',daily:true},
  {id:'flood_45',name:'Floodlight (45W)',icon:'🔦',w:45,cat:'Lighting',daily:true},
  {id:'flood_100',name:'Floodlight (100W)',icon:'🔦',w:100,cat:'Lighting',daily:true},
  {id:'street_light',name:'Security / Street Light',icon:'🔦',w:60,cat:'Lighting',daily:true},
  {id:'ceil_fan',name:'Ceiling Fan',icon:'🌀',w:75,cat:'Cooling',daily:true},
  {id:'stand_fan',name:'Standing Fan',icon:'🌀',w:60,cat:'Cooling',daily:true},
  {id:'table_fan',name:'Table Fan',icon:'🌀',w:40,cat:'Cooling',daily:true},
  {id:'exhaust_fan',name:'Exhaust Fan',icon:'🌀',w:30,cat:'Cooling',daily:true},
  {id:'ac_1hp',name:'Air Conditioner (1 HP)',icon:'❄️',w:750,cat:'Cooling',daily:true},
  {id:'ac_1_5hp',name:'Air Conditioner (1.5 HP)',icon:'❄️',w:1125,cat:'Cooling',daily:true},
  {id:'ac_2hp',name:'Air Conditioner (2 HP)',icon:'❄️',w:1500,cat:'Cooling',daily:true},
  {id:'ac_2_5hp',name:'Air Conditioner (2.5 HP)',icon:'❄️',w:1875,cat:'Cooling',daily:true},
  {id:'ac_3hp',name:'Air Conditioner (3 HP)',icon:'❄️',w:2250,cat:'Cooling',daily:true},
  {id:'fridge_sm',name:'Refrigerator — Small (100L)',icon:'🧊',w:80,cat:'Kitchen',daily:true},
  {id:'fridge_md',name:'Refrigerator — Medium (200L)',icon:'🧊',w:130,cat:'Kitchen',daily:true},
  {id:'fridge_lg',name:'Refrigerator — Large (350L)',icon:'🧊',w:200,cat:'Kitchen',daily:true},
  {id:'fridge_xl',name:'Refrigerator — Extra Large',icon:'🧊',w:300,cat:'Kitchen',daily:true},
  {id:'deep_frz_sm',name:'Deep Freezer — Small (100L)',icon:'🧊',w:150,cat:'Kitchen',daily:true},
  {id:'deep_frz_md',name:'Deep Freezer — Medium (200L)',icon:'🧊',w:200,cat:'Kitchen',daily:true},
  {id:'deep_frz_lg',name:'Deep Freezer — Large (300L)',icon:'🧊',w:250,cat:'Kitchen',daily:true},
  {id:'microwave_sm',name:'Microwave — Small (700W)',icon:'📦',w:700,cat:'Kitchen',daily:true},
  {id:'microwave_lg',name:'Microwave — Large (1200W)',icon:'📦',w:1200,cat:'Kitchen',daily:true},
  {id:'elec_kettle',name:'Electric Kettle',icon:'☕',w:2000,cat:'Kitchen',daily:true},
  {id:'blender',name:'Blender',icon:'🥤',w:450,cat:'Kitchen',daily:true},
  {id:'toaster',name:'Toaster',icon:'🍞',w:900,cat:'Kitchen',daily:true},
  {id:'cooker_2plate',name:'Electric Cooker — 2 Plate',icon:'🍳',w:1500,cat:'Kitchen',daily:true},
  {id:'cooker_4plate',name:'Electric Cooker — 4 Plate',icon:'🍳',w:3000,cat:'Kitchen',daily:true},
  {id:'induction',name:'Induction Cooker',icon:'🍳',w:2000,cat:'Kitchen',daily:true},
  {id:'rice_cooker',name:'Rice Cooker',icon:'🍚',w:700,cat:'Kitchen',daily:true},
  {id:'food_warmer',name:'Food Warmer / Hot Plate',icon:'🍽️',w:200,cat:'Kitchen',daily:true},
  {id:'wm_hand',name:'Washing Machine — Manual',icon:'🫧',w:250,cat:'Laundry',daily:false},
  {id:'wm_semi',name:'Washing Machine — Semi-Auto',icon:'🫧',w:400,cat:'Laundry',daily:false},
  {id:'wm_top_load',name:'Washing Machine — Top Load Auto',icon:'🫧',w:500,cat:'Laundry',daily:false},
  {id:'wm_front_load',name:'Washing Machine — Front Load (7kg)',icon:'🫧',w:2000,cat:'Laundry',daily:false},
  {id:'wm_front_load_lg',name:'Washing Machine — Front Load (10kg+)',icon:'🫧',w:2500,cat:'Laundry',daily:false},
  {id:'dryer_sm',name:'Tumble Dryer — Small',icon:'🫧',w:2000,cat:'Laundry',daily:false},
  {id:'dryer_lg',name:'Tumble Dryer — Large',icon:'🫧',w:3000,cat:'Laundry',daily:false},
  {id:'pressing_iron',name:'Pressing Iron (dry)',icon:'👔',w:1200,cat:'Laundry',daily:false},
  {id:'steam_iron',name:'Steam Iron',icon:'👔',w:2000,cat:'Laundry',daily:false},
  {id:'tv_24',name:'TV — 24"',icon:'📺',w:50,cat:'Entertainment',daily:true},
  {id:'tv_32',name:'TV — 32"',icon:'📺',w:80,cat:'Entertainment',daily:true},
  {id:'tv_43',name:'TV — 43"',icon:'📺',w:120,cat:'Entertainment',daily:true},
  {id:'tv_55',name:'TV — 55"',icon:'📺',w:180,cat:'Entertainment',daily:true},
  {id:'tv_65',name:'TV — 65"',icon:'📺',w:250,cat:'Entertainment',daily:true},
  {id:'decoder',name:'Decoder / DSTV',icon:'📡',w:25,cat:'Entertainment',daily:true},
  {id:'sound_sm',name:'Sound System — Small',icon:'🔊',w:80,cat:'Entertainment',daily:true},
  {id:'sound_lg',name:'Sound System — Large',icon:'🔊',w:300,cat:'Entertainment',daily:true},
  {id:'laptop_sm',name:'Laptop — Ultrabook (13")',icon:'💻',w:45,cat:'Entertainment',daily:true},
  {id:'laptop',name:'Laptop — Standard (15")',icon:'💻',w:65,cat:'Entertainment',daily:true},
  {id:'laptop_lg',name:'Laptop — Gaming / Workstation',icon:'💻',w:180,cat:'Entertainment',daily:true},
  {id:'desktop',name:'Desktop PC',icon:'🖥️',w:200,cat:'Entertainment',daily:true},
  {id:'printer',name:'Printer',icon:'🖨️',w:120,cat:'Entertainment',daily:false},
  {id:'phone_chgr',name:'Phone Charger — Standard (5W)',icon:'📱',w:5,cat:'Entertainment',daily:true},
  {id:'phone_chgr_fast',name:'Phone Charger — Fast (25W)',icon:'📱',w:25,cat:'Entertainment',daily:true},
  {id:'phone_chgr_super',name:'Phone Charger — Super Fast (45W)',icon:'📱',w:45,cat:'Entertainment',daily:true},
  {id:'tablet_chgr',name:'Tablet Charger (20W)',icon:'📱',w:20,cat:'Entertainment',daily:true},
  {id:'laptop_chgr_usbc',name:'USB-C Laptop Charger (65W)',icon:'🔌',w:65,cat:'Entertainment',daily:true},
  {id:'laptop_chgr_lg',name:'Laptop Charger — High Power (140W)',icon:'🔌',w:140,cat:'Entertainment',daily:true},
  {id:'pump_half',name:'Pumping Machine — 0.5 HP',icon:'💧',w:375,cat:'Water & Pumps',daily:false},
  {id:'pump_1hp',name:'Pumping Machine — 1 HP',icon:'💧',w:750,cat:'Water & Pumps',daily:false},
  {id:'pump_1_5hp',name:'Pumping Machine — 1.5 HP',icon:'💧',w:1100,cat:'Water & Pumps',daily:false},
  {id:'pump_2hp',name:'Pumping Machine — 2 HP',icon:'💧',w:1500,cat:'Water & Pumps',daily:false},
  {id:'borehole_1hp',name:'Borehole Pump — 1 HP',icon:'💧',w:750,cat:'Water & Pumps',daily:false},
  {id:'borehole_2hp',name:'Borehole Pump — 2 HP',icon:'💧',w:1500,cat:'Water & Pumps',daily:false},
  {id:'submersible',name:'Submersible Pump — 0.5 HP',icon:'💧',w:375,cat:'Water & Pumps',daily:false},
  {id:'water_heater_ins',name:'Water Heater — Instant',icon:'🚿',w:3000,cat:'Water & Pumps',daily:true},
  {id:'water_heater_str',name:'Water Heater — Storage Tank',icon:'🚿',w:1500,cat:'Water & Pumps',daily:true},
  {id:'security_cam',name:'Security Camera (×1)',icon:'📷',w:15,cat:'Utilities',daily:true},
  {id:'cctv_dvr',name:'CCTV DVR (4-channel)',icon:'🎥',w:30,cat:'Utilities',daily:true},
  {id:'router',name:'Wi-Fi Router',icon:'📶',w:12,cat:'Utilities',daily:true},
  {id:'router_4g',name:'4G Router / MiFi',icon:'📶',w:20,cat:'Utilities',daily:true},
  {id:'hair_dryer',name:'Hair Dryer',icon:'💇',w:1500,cat:'Utilities',daily:false},
  {id:'clipper',name:'Hair Clipper',icon:'✂️',w:15,cat:'Utilities',daily:false},
  {id:'vacuum',name:'Vacuum Cleaner',icon:'🧹',w:1400,cat:'Utilities',daily:false},
  {id:'gate_motor',name:'Gate Motor',icon:'🚪',w:500,cat:'Utilities',daily:false},
  {id:'intercom',name:'Intercom / Video Door',icon:'🔔',w:10,cat:'Utilities',daily:true},
];
const DEFHRS={led_bulb:6,cfl_bulb:6,tube_light:6,flood_45:5,flood_100:5,street_light:10,ceil_fan:8,stand_fan:8,table_fan:6,exhaust_fan:4,ac_1hp:6,ac_1_5hp:6,ac_2hp:6,ac_2_5hp:6,ac_3hp:6,fridge_sm:24,fridge_md:24,fridge_lg:24,fridge_xl:24,deep_frz_sm:24,deep_frz_md:24,deep_frz_lg:24,microwave_sm:0.5,microwave_lg:0.5,elec_kettle:0.5,blender:0.5,toaster:0.3,cooker_2plate:2,cooker_4plate:2,induction:2,rice_cooker:1,food_warmer:4,wm_hand:1,wm_semi:1.5,wm_top_load:1.5,wm_front_load:2,wm_front_load_lg:2.5,dryer_sm:1,dryer_lg:1.5,pressing_iron:1,steam_iron:1,tv_24:6,tv_32:6,tv_43:6,tv_55:6,tv_65:6,decoder:6,sound_sm:4,sound_lg:4,laptop_sm:5,laptop:5,laptop_lg:4,desktop:5,printer:0.5,phone_chgr:3,phone_chgr_fast:2,phone_chgr_super:1.5,tablet_chgr:3,laptop_chgr_usbc:5,laptop_chgr_lg:4,pump_half:2,pump_1hp:2,pump_1_5hp:2,pump_2hp:2,borehole_1hp:3,borehole_2hp:3,submersible:3,water_heater_ins:0.5,water_heater_str:1,security_cam:24,cctv_dvr:24,router:24,router_4g:24,hair_dryer:0.5,clipper:0.5,vacuum:0.5,gate_motor:0.3,intercom:24};
const CATS=['All',...new Set(DB.map(a=>a.cat))];
const STD_INV_KVA=[1.8,3.6,4,6,10,12];
const STD_BAT_KWH=[1.8,2.5,3.8,5,7.5,10,15,20,25,30,40,50];
const PANEL_SIZES=[250,300,350,400,450,500,550,600,650];
const INV_PV_MAX={1.8:2000,3.6:3600,4:4000,6:5000,10:8000,12:10000};
/* STD_CC_AMPS removed – inverter is now upsized to cover panel input */
const selected={};
let activeCat='All',ddOpen=false,VOLTAGE=48,OVERSIZE=true;

function goToResults(){const p1=document.getElementById('page1'),p2=document.getElementById('page2');p1.classList.remove('active');p1.classList.add('hidden-left');p2.classList.remove('hidden-right');p2.classList.add('active');window.scrollTo({top:0,behavior:'instant'});}
function goBack(){const p1=document.getElementById('page1'),p2=document.getElementById('page2');p2.classList.remove('active');p2.classList.add('hidden-right');p1.classList.remove('hidden-left');p1.classList.add('active');window.scrollTo({top:0,behavior:'instant'});}
function toggleDropdown(){ddOpen=!ddOpen;document.getElementById('dropdown').classList.toggle('open',ddOpen);document.getElementById('trigger').classList.toggle('open',ddOpen);if(ddOpen){setTimeout(()=>document.getElementById('dd-search').focus(),60);buildDDList('',activeCat);}}
document.addEventListener('click',e=>{if(ddOpen&&!document.querySelector('.add-wrap').contains(e.target)){ddOpen=false;document.getElementById('dropdown').classList.remove('open');document.getElementById('trigger').classList.remove('open');}});
function buildCats(){document.getElementById('dd-cats').innerHTML=CATS.map(c=>`<span class="cat-pill${c===activeCat?' active':''}" onclick="setCategory(event,'${c}')">${c}</span>`).join('');}
function setCategory(e,cat){e.stopPropagation();activeCat=cat;buildCats();buildDDList(document.getElementById('dd-search').value,cat);}
function buildDDList(search,cat){const lc=search.toLowerCase();const items=DB.filter(a=>(cat==='All'||a.cat===cat)&&(!lc||a.name.toLowerCase().includes(lc)||a.cat.toLowerCase().includes(lc)));const el=document.getElementById('dd-list');if(!items.length){el.innerHTML='<div class="dd-empty">No appliances found</div>';return;}el.innerHTML=items.map(a=>{const isAdded=!!selected[a.id];return`<div class="dd-item${isAdded?' added':''}" onclick="toggleApp(event,'${a.id}')"><span class="dd-item-icon">${a.icon}</span><div class="dd-item-info"><div class="dd-item-name">${a.name}</div><div class="dd-item-meta">${a.cat} · ${a.w} W</div></div><span class="dd-item-badge">${isAdded?'− Remove':'+ Add'}</span></div>`;}).join('');}
function filterDD(val){buildDDList(val,activeCat);}
function toggleApp(e,id){e.stopPropagation();if(selected[id])delete selected[id];else selected[id]={qty:1,hrs:DEFHRS[id]||4};buildDDList(document.getElementById('dd-search').value,activeCat);renderList();}
function avgWh(a,s){return s.qty*a.w*s.hrs;}
function renderList(){const ids=Object.keys(selected);const el=document.getElementById('sel-list');if(!ids.length){el.innerHTML='<div class="list-empty">Click "Add appliance" to get started</div>';return;}el.innerHTML=ids.map(id=>{const a=DB.find(x=>x.id===id),s=selected[id],wh=avgWh(a,s);return`<div class="srow" id="srow-${id}"><div class="srow-name"><span class="srow-icon">${a.icon}</span><div><span class="srow-lbl">${a.name}</span><span class="srow-w">${a.w}W</span></div></div><input class="inp" type="number" min="1" max="20" value="${s.qty}" oninput="upd('${id}','qty',this.value)"><input class="inp" type="number" min="0.5" max="24" step="0.5" value="${s.hrs}" oninput="upd('${id}','hrs',this.value)"><div class="wh-cell" id="wh-${id}">${fmtN(Math.round(wh))}</div><button class="del" onclick="removeApp('${id}')">✕</button></div>`;}).join('');}
function removeApp(id){delete selected[id];renderList();buildDDList(document.getElementById('dd-search').value,activeCat);}
function upd(id,field,val){if(!selected[id])return;selected[id][field]=parseFloat(val)||0;const a=DB.find(x=>x.id===id),s=selected[id],wh=avgWh(a,s);const cell=document.getElementById(`wh-${id}`);if(cell)cell.innerHTML=fmtN(Math.round(wh));}
function toggleOversize(on){OVERSIZE=on;document.getElementById('oversize-display').innerHTML=`Oversizing <span>${on?'×1.2':'Off'}</span>`;}
function calculate(){
  const ids=Object.keys(selected);
  if(!ids.length){alert('Add at least one appliance first.');return;}
  let items=[],totalWhDay=0,peakW=0;
  ids.forEach(id=>{const a=DB.find(x=>x.id===id),s=selected[id];const loadW=s.qty*a.w,whDay=avgWh(a,s);totalWhDay+=whDay;peakW+=loadW;items.push({name:a.name,icon:a.icon,qty:s.qty,w:a.w,hrs:s.hrs,loadW,whDay});});
  /* Auto-select system voltage based on total daily energy */
  if(totalWhDay<=1500)VOLTAGE=12;
  else if(totalWhDay<=4000)VOLTAGE=24;
  else VOLTAGE=48;
  const PEAK_SUN=4;
  const O=OVERSIZE?1.2:1;
  const totalKwh=totalWhDay/1000;
  /* Inverter: peak load × 1.3 safety factor (startup surges), then oversize */
  const invKvaRaw=(peakW*1.3*O)/1000;
  let invKvaBase=roundUpList(invKvaRaw,STD_INV_KVA);
  /* invKva may be bumped later in renderPanelCard to cover panel PV input */
  let invKva=invKvaBase;
  /* Lithium battery: totalWhDay / 0.8 DOD, then oversize, min = inverter kVA */
  const DOD=0.8;
  const batKwhRaw=Math.max((totalWhDay/1000/DOD)*O,invKva);
  const batKwh=roundUpList(batKwhRaw,STD_BAT_KWH);
  const batAh=Math.ceil((batKwh*1000)/VOLTAGE);
  /* Panel: (totalEnergy*O + peakLoad*O) then oversize, then /sunHrs */
  const panelWattStep1=(totalWhDay*O)+(peakW*O);
  const panelOversize=panelWattStep1*O;
  const solarW=Math.ceil(panelOversize/PEAK_SUN);
  const series=VOLTAGE/12;
  const parallelStrings=Math.ceil(batAh/100);
  const totalBats=parallelStrings*series;
  document.getElementById('r-subtitle').textContent=`Residential · Nigeria · ${VOLTAGE}V${OVERSIZE?' · Oversized ×1.2':''}`;
  document.getElementById('r-energy').textContent=totalKwh.toFixed(2);
  document.getElementById('r-appliance-count').textContent=`${ids.length} appliance${ids.length!==1?'s':''} · peak load ${fmtN(peakW)} W`;
  document.getElementById('r-bat-kwh').textContent=batKwh+'kWh';
  document.getElementById('r-bat-sub').innerHTML=`<strong>${fmtN(batAh)} Ah</strong> @ ${VOLTAGE}V<br>${totalBats} × 100Ah/12V lithium batteries`;
  document.getElementById('r-volt-badge').textContent=VOLTAGE+'V system';
  document.getElementById('r-inv-kva').textContent=invKva+'kVA';
  document.getElementById('r-inv-sub').innerHTML=`<strong>${fmtN(Math.round(peakW*O))} W</strong> peak load${OVERSIZE?'<br>incl. 1.2× oversizing':''}`;
  document.getElementById('r-inv-volt-badge').textContent=VOLTAGE+'V system';
  const WA='https://wa.me/2348157511971?text=';
  function updateQuoteLink(pw,n){
    let msg=`Hi, I need a quote for this solar system:\n\n🔋 Lithium Battery: ${batKwh}kWh (${fmtN(batAh)}Ah @ ${VOLTAGE}V)\n🔌 Inverter: ${invKva}kVA (${VOLTAGE}V)\n☀️ Panels: ${n} × ${pw}W (${fmtN(n*pw)}W total)`;
    msg+=`\n\nDaily consumption: ${totalKwh.toFixed(2)} kWh/day`;
    document.getElementById('cta-quote').href=WA+encodeURIComponent(msg);
  }
  function renderPanelCard(pw){
    const n=Math.ceil(solarW/pw);
    const totalPanelW=n*pw;
    /* Upsize inverter if panels exceed its PV input capacity */
    invKva=invKvaBase;
    let maxPv=INV_PV_MAX[invKva]||invKva*1000;
    if(totalPanelW>maxPv){
      const needed=STD_INV_KVA.find(k=>(INV_PV_MAX[k]||k*1000)>=totalPanelW);
      invKva=needed||STD_INV_KVA[STD_INV_KVA.length-1];
      maxPv=INV_PV_MAX[invKva]||invKva*1000;
    }
    document.getElementById('r-inv-kva').textContent=invKva+'kVA';
    document.getElementById('r-inv-sub').innerHTML=`<strong>${fmtN(Math.round(peakW*O))} W</strong> peak load${totalPanelW>maxPv?'':invKva>invKvaBase?'<br>Upsized to handle '+fmtN(totalPanelW)+'W panels':''}${OVERSIZE?'<br>incl. 1.2× oversizing':''}`;
    document.getElementById('r-pan-main').textContent=`${pw}W (${n})`;
    document.getElementById('r-pan-sub').innerHTML=`<strong>${n} panel${n!==1?'s':''}</strong> × ${pw}W<br>Total: ${fmtN(totalPanelW)} W installed`;
    document.getElementById('cc-section').style.display='none';
    updateQuoteLink(pw,n);
    document.querySelectorAll('.ptag').forEach(t=>{const tw=parseInt(t.querySelector('.tag-w').textContent);const n2=Math.ceil(solarW/tw);t.querySelector('.tag-n').textContent=`${n2} panel${n2!==1?'s':''}`;t.classList.toggle('best',tw===pw);});
  }
  window.renderPanelCard=renderPanelCard;
  document.getElementById('panel-opts').innerHTML=PANEL_SIZES.map(pw=>{const n=Math.ceil(solarW/pw);return`<div class="ptag${pw===500?' best':''}" onclick="renderPanelCard(${pw})"><span class="tag-w">${pw}W</span><span class="tag-n">${n} panel${n!==1?'s':''}</span></div>`;}).join('');
  renderPanelCard(500);
  const maxWh=Math.max(...items.map(i=>i.whDay),1);
  document.getElementById('breakdown').innerHTML=[...items].sort((a,b)=>b.whDay-a.whDay).map(a=>{const pct=((a.whDay/totalWhDay)*100).toFixed(1),bw=Math.max(3,Math.round((a.whDay/maxWh)*52));return`<div class="bk-row"><div>${a.icon} ${a.name}</div><div style="color:var(--muted)">${a.qty}</div><div>${fmtN(a.loadW)}</div><div style="color:var(--sun)">${fmtN(Math.round(a.whDay))}</div><div class="bar-wrap"><div class="bar" style="width:${bw}px"></div><span style="color:var(--muted);font-size:10px">${pct}%</span></div></div>`;}).join('');
  goToResults();
}
function roundUpList(val,list){return list.find(s=>s>=val)||list[list.length-1];}
function fmtN(n){return Number(n).toLocaleString();}
buildCats();
