const state={all:[],filtered:[],page:1,pageSize:10};
const $=s=>document.querySelector(s);
const els={
  q:$("#q"),country:$("#country"),missionType:$("#missionType"),outcome:$("#outcome"),
  crewed:$("#crewed"),yearFrom:$("#yearFrom"),yearTo:$("#yearTo"),sort:$("#sort"),
  reset:$("#reset"),cards:$("#cards"),status:$("#status"),count:$("#count"),
  countryCount:$("#countryCount"),yearRange:$("#yearRange"),tpl:$("#cardTemplate")
};
const text=v=>String(v??"").trim();
const norm=v=>text(v).toLocaleLowerCase("zh-CN");
const uniq=a=>[...new Set(a.filter(Boolean))].sort((a,b)=>String(a).localeCompare(String(b),"zh-CN"));
function addOptions(el,values){values.forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=v;el.appendChild(o);});}
function searchable(x){
  return [x.name,x.country_region,x.operator,x.launch_site,x.launch_vehicle,x.vehicle_family,
    x.manufacturer,x.mission_type,x.destination,x.payload,x.description,
    ...(x.crew||[])].map(norm).join(" ");
}
function apply(){
  const q=norm(els.q.value),from=Number(els.yearFrom.value)||-Infinity,to=Number(els.yearTo.value)||Infinity;
  let rows=state.all.filter(x=>{
    const y=Number(x.year||String(x.date_utc||"").slice(0,4));
    return (!q||q.split(/\s+/).every(term=>searchable(x).includes(term)))
      &&(!els.country.value||x.country_region===els.country.value)
      &&(!els.missionType.value||x.mission_type===els.missionType.value)
      &&(!els.outcome.value||x.outcome===els.outcome.value)
      &&(!els.crewed.value||String(Boolean(x.crewed))===els.crewed.value)
      &&y>=from&&y<=to;
  });
  const mode=els.sort.value;
  rows.sort((a,b)=>{
    if(mode==="date-asc") return text(a.date_utc).localeCompare(text(b.date_utc));
    if(mode==="country") return text(a.country_region).localeCompare(text(b.country_region),"zh-CN");
    if(mode==="vehicle") return text(a.launch_vehicle).localeCompare(text(b.launch_vehicle),"zh-CN");
    return text(b.date_utc).localeCompare(text(a.date_utc));
  });
  state.filtered=rows;state.page=1;render();
}
function render(){
  const rows=state.filtered;els.cards.replaceChildren();
  els.count.textContent=rows.length.toLocaleString("zh-CN");
  els.countryCount.textContent=new Set(rows.map(x=>x.country_region).filter(Boolean)).size;
  const years=rows.map(x=>Number(x.year||String(x.date_utc||"").slice(0,4))).filter(Number.isFinite);
  els.yearRange.textContent=years.length?Math.min(...years)+"–"+Math.max(...years):"—";
  els.status.textContent=state.all.length?("数据库共 "+state.all.length.toLocaleString("zh-CN")+" 条记录"):"数据库目前尚无记录";
  let pager=document.querySelector('#pagination');
  if(!pager){pager=document.createElement('nav');pager.id='pagination';pager.setAttribute('aria-label','结果分页');els.cards.after(pager);}
  pager.replaceChildren();
  const pages=Math.max(1,Math.ceil(rows.length/state.pageSize));
  for(const [label,delta] of [['上一页',-1],['下一页',1]]){
    const b=document.createElement('button');b.textContent=label;b.disabled=delta<0?state.page===1:state.page===pages;
    b.onclick=()=>{state.page+=delta;render();els.status.scrollIntoView({block:'start'});};pager.append(b);
    if(delta<0){const info=document.createElement('span');info.textContent=`第 ${state.page} / ${pages} 页`;pager.append(info);}
  }
  if(!rows.length){const p=document.createElement("p");p.className="empty";p.textContent="没有符合条件的记录。";els.cards.appendChild(p);return;}
  rows.slice((state.page-1)*state.pageSize,state.page*state.pageSize).forEach(x=>{
    const node=els.tpl.content.cloneNode(true);
    node.querySelector(".date").textContent=x.date_utc||"日期待补";
    node.querySelector(".name").textContent=x.name||"未命名任务";
    const outcome=node.querySelector(".outcome");outcome.textContent=x.outcome||"结果待补";
    const meta=node.querySelector(".meta");
    [["国家/地区",x.country_region],["发射组织",x.operator],["运载器",x.launch_vehicle],["发射场",x.launch_site],
     ["任务类型",x.mission_type],["目的地",x.destination],["载荷",x.payload],["载人",x.crewed?"是":"否"]]
      .forEach(pair=>{const k=pair[0],v=pair[1];if(!v&&v!==false)return;const d=document.createElement("div");const dt=document.createElement("dt");const dd=document.createElement("dd");dt.textContent=k;dd.textContent=v;d.append(dt,dd);meta.appendChild(d);});
    node.querySelector(".description").textContent=x.description||"";
    const s=node.querySelector(".sources");
    (x.sources||[]).forEach((src,i)=>{const a=document.createElement("a");if(!/^https?:\/\//i.test(src.url))return;a.href=src.url;a.target="_blank";a.rel="noopener noreferrer";a.textContent=src.title||("来源 "+(i+1));s.appendChild(a);});
    const details=document.createElement('details');
    const summary=document.createElement('summary');summary.textContent='更多任务信息';details.append(summary);
    const info=document.createElement('p');
    info.textContent=[['运载器系列',x.vehicle_family],['制造方',x.manufacturer],['乘组',(x.crew||[]).join('、')],['轨道/目标天体',x.orbit_or_body],['数据核验',x.verification_status||'待逐项核验']].filter(pair=>pair[1]).map(pair=>pair.join('：')).join('；');
    details.append(info);node.querySelector('article').append(details);
    els.cards.appendChild(node);
  });
}
function reset(){[els.q,els.yearFrom,els.yearTo].forEach(e=>e.value="");[els.country,els.missionType,els.outcome,els.crewed].forEach(e=>e.value="");els.sort.value="date-desc";apply();}
async function init(){
  try{
    const r=await fetch("data/launches.json",{cache:"no-store"});
    if(!r.ok) throw new Error("HTTP "+r.status);
    state.all=await r.json();
    addOptions(els.country,uniq(state.all.map(x=>x.country_region)));
    addOptions(els.missionType,uniq(state.all.map(x=>x.mission_type)));
    addOptions(els.outcome,uniq(state.all.map(x=>x.outcome)));
    document.querySelectorAll("input,select").forEach(e=>e.addEventListener("input",apply));
    els.reset.addEventListener("click",reset);apply();
  }catch(err){els.status.textContent="数据库载入失败："+err.message;console.error(err);}
}
init();