import React,{useEffect,useMemo,useState} from 'react';
import {PHOTOS,PhotoBanner} from './Photography.jsx';

const TABS=[
 {id:'future',name:'Crisis Time Machine',eyebrow:'01 / MULTIPLE FUTURES',sub:'See consequences, not just balances'},
 {id:'guard',name:'EssentialGuard',eyebrow:'02 / PEOPLE FIRST',sub:'Protect essentials before paying bills'},
 {id:'xray',name:'Decision X-Ray',eyebrow:'03 / REASON CODES',sub:'Find the exact cause of a risk'},
 {id:'chaos',name:'Chaos Lab',eyebrow:'04 / JUDGE MODE',sub:'Run real adversarial checks'},
 {id:'fx',name:'FX Shock',eyebrow:'05 / CURRENCY STRESS',sub:'Test exchange-rate sensitivity'},
];
const titleCase=s=>s.replaceAll('_',' ').toLowerCase().replace(/(^|\s)\w/g,x=>x.toUpperCase());
function Sparkline({points,bad}){
 const p=(points||[]).filter(x=>Number.isFinite(Number(x.available_myr)));
 if(p.length<2)return <div className="wow-spark-empty">No chart data</div>;
 const values=p.map(x=>Number(x.available_myr));const low=Math.min(...values,-10),hi=Math.max(...values,10);const range=Math.max(1,hi-low);
 const coords=p.map((x,i)=>`${8+i*202/(p.length-1)},${59-(Number(x.available_myr)-low)/range*49}`);
 const path='M'+coords.join(' L');
 const zero=59-(0-low)/range*49;
 return <svg viewBox="0 0 220 72" role="img" aria-label="Projected cash-flow trend under this scenario" className="wow-sparkline"><line x1="7" y1={zero} x2="215" y2={zero} stroke="currentColor" strokeOpacity=".19" strokeDasharray="4 5"/><path d={path} fill="none" stroke={bad?'#ca5645':'#0e7c7b'} strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round"/><circle cx={coords[coords.length-1].split(',')[0]} cy={coords[coords.length-1].split(',')[1]} r="3.5" fill={bad?'#ca5645':'#0e7c7b'}/></svg>;
}
function SectionShell({eyebrow,title,body,children,tag}){return <div className="wow-section-shell"><div className="wow-section-heading"><div><span className="wow-kicker">{eyebrow}</span><h2>{title}</h2><p>{body}</p></div>{tag&&<span className="wow-section-tag">{tag}</span>}</div>{children}</div>}
function RiskMetric({label,value,detail,risk=false}){return <div className={'wow-metric '+(risk?'wow-metric-risk':'')}><span>{label}</span><strong>{value}</strong>{detail&&<small>{detail}</small>}</div>}

export function WowLab({api,Icon,Title,Pill,rm,short,scenario,overrides,onError,onDelayed,navigate}){
 const [tab,setTab]=useState('future');
 const [reserve,setReserve]=useState('250.00');
 const [shock,setShock]=useState(-5);
 const [future,setFuture]=useState(null),[guard,setGuard]=useState(null),[solver,setSolver]=useState(null),[xray,setXray]=useState(null),[fx,setFx]=useState(null),[chaos,setChaos]=useState(null);
 const [busy,setBusy]=useState(false);
 const request={scenario,arrival_overrides:overrides,essential_reserve_myr:reserve};
 const stableOverrides=JSON.stringify(overrides);
 useEffect(()=>{let active=true;setBusy(true);const post=(url,body)=>api(url,'POST',body);
  const job= tab==='future'?post('/wow/time-machine',request):
    tab==='guard'?Promise.all([post('/wow/essential-guard',request),post('/wow/rescue-solver',request)]):
    tab==='xray'?post('/wow/decision-xray',{scenario,arrival_overrides:overrides}):
    tab==='fx'?post('/wow/fx-shock',{scenario,arrival_overrides:overrides,percent_change:String(shock)}):null;
  if(!job){setBusy(false);return()=>{active=false}};
  Promise.resolve(job).then(data=>{if(!active)return;if(tab==='future')setFuture(data);
    if(tab==='guard'){setGuard(data[0]);setSolver(data[1]);}if(tab==='xray')setXray(data);if(tab==='fx')setFx(data)})
    .catch(e=>{if(active)onError(e.message)}).finally(()=>{if(active)setBusy(false)});
  return()=>{active=false};
 },[tab,scenario,stableOverrides,reserve,shock]);
 const runChaos=async()=>{setBusy(true);try{setChaos(await api('/wow/chaos-lab','POST',{}))}catch(e){onError(e.message)}finally{setBusy(false)}};
 const selection=TABS.find(t=>t.id===tab);
 return <>
  <Title eyebrow="CAMPUSFIN / INNOVATION STUDIO" title="See what's possible. Challenge what's safe." subtitle="A decision laboratory powered by actual synthetic cash-flow calculations — not a prerecorded animation." aside={<Pill kind="neutral">No external actions</Pill>}/>
  <PhotoBanner photo={PHOTOS.planning} kicker="INNOVATION STUDIO / PREDICT. RESCUE. PROVE." title="Five ways to see around financial corners." body="Rehearse different futures, protect living essentials, inspect every decision and try to break the model — all without moving money."/>
  <div className="wow-studio-intro"><div className="wow-studio-ornament" aria-hidden="true"><span/><span/><span/><span/></div><div><span className="wow-kicker">THE FINANCIAL DECISION STUDIO</span><h2>Intelligence you can inspect.</h2><p>Move an assumption. Reveal a consequence. See which plans survive the constraints.</p></div><div className="wow-live"><span className="wow-live-dot"/> ENGINE-VERIFIED DEMO</div></div>
  <div className="wow-tabs" role="tablist" aria-label="CampusFin innovation tools">{TABS.map((t,i)=><button type="button" role="tab" aria-selected={tab===t.id} className={'wow-tab '+(tab===t.id?'active':'')} key={t.id} onClick={()=>setTab(t.id)}><span>0{i+1}</span><strong>{t.name}</strong><small>{t.sub}</small></button>)}</div>
  <div className="wow-main-area" aria-busy={busy}>
   {busy&&<div className="wow-progress" role="status"><span className="wow-progress-dot"/> Recomputing financial evidence…</div>}
   {tab==='future'&&<SectionShell eyebrow={selection.eyebrow} title="Four possible futures." body="Compare funding timing and FX assumptions. These are scenarios, not predictions." tag="SIMULATED TIME MACHINE">
     <div className="wow-future-grid">{future?.variants.map((v,i)=><div key={v.id} className={'wow-future-card '+(v.status==='at_risk'?'danger':'safe')}><div className="wow-future-top"><span className="wow-number">0{i+1}</span><span className={'wow-signal '+(v.status==='at_risk'?'bad':'ok')}>{v.status==='at_risk'?'PAYMENT AT RISK':'COVERED'}</span></div><h3>{v.title}</h3><p>{v.description}</p><Sparkline points={v.points} bad={v.status==='at_risk'}/><div className="wow-future-result"><span>{v.status==='at_risk'?'Projected gap':'Listed obligations'}</span><strong>{v.status==='at_risk'?rm(v.gap_myr):'Covered'}</strong></div><div className="wow-mini-note">{v.essentials_protected?'Essential reserve maintained':'Essential reserve may be breached'}</div></div>)}</div>
     <div className="wow-info-row"><Icon name="info" size={18}/> {future?.disclaimer||'Illustrative assumptions. No scenario is a forecast of exchange rates or transfer delivery.'}</div>
     <button className="button-primary" onClick={()=>navigate('plan')}>Adjust a real scenario <Icon name="arrow" size={16}/></button>
    </SectionShell>}
   {tab==='guard'&&<SectionShell eyebrow={selection.eyebrow} title="Pay tuition. Still afford to live." body="Set a minimum balance you want preserved after each bill. The solver rejects plans that only succeed by sacrificing essential living funds." tag="DETERMINISTIC CONSTRAINTS">
     <div className="wow-guard-config"><div><span className="wow-kicker">ESSENTIAL SAFETY FLOOR</span><h3>RM {Number(reserve||0).toLocaleString('en-MY',{minimumFractionDigits:2})}</h3><p>Minimum remaining funds to protect for food, housing and essential travel. This is a user-selected buffer, not a charge.</p></div><div className="wow-guard-controls"><label htmlFor="essential-reserve">Reserve (MYR)</label><input id="essential-reserve" type="range" min="0" max="1000" step="50" value={Math.max(0,Math.min(1000,Number(reserve)||0))} onChange={e=>setReserve(e.target.value)}/><div className="wow-slider-ends"><span>RM 0</span><span>RM 1,000</span></div><input type="number" min="0" max="10000" step="0.01" value={reserve} aria-label="Exact essential reserve in ringgit" onChange={e=>setReserve(e.target.value)}/></div></div>
     <div className="wow-check-grid">{guard?.checks?.map(c=><div className={'wow-check-card '+(c.meets_guard?'good':'not-good')} key={c.id}><div className="wow-check-top"><strong>{c.obligation}</strong><span>{c.meets_guard?'● PROTECTED':'! UNDER MINIMUM'}</span></div><small>After payment · {short(c.due_date)}</small><div className="wow-check-number">{rm(c.projected_after_myr)}</div><div className="wow-check-detail">{c.meets_guard?`At least ${rm(c.essential_reserve_myr)} remains`:`${rm(c.reserve_deficit_myr)} below the safety floor`}</div></div>)}</div>
     {solver?.shortfall&&<div className="wow-solver-panel"><div className="wow-section-heading"><div><span className="wow-kicker">RESCUESOLVER / SAFETY VERIFICATION</span><h3>Which rescue ideas protect both priorities?</h3><p>Each option must cover listed bills and still retain your essential reserve. Real-world confirmation remains required.</p></div></div><div className="wow-solver-options">{solver?.enhanced_options?.map(o=><div className="wow-option-row" key={o.id}><div><strong>{o.title}</strong><small>{titleCase(o.guard_decision)} · After bill {rm(o.protected_amount_after_bill_myr)}</small></div><span className={'wow-signal '+(o.guard_decision==='CONDITIONALLY_FEASIBLE'?'ok':'bad')}>{o.guard_decision==='CONDITIONALLY_FEASIBLE'?'CONDITIONAL':'NOT SAFE YET'}</span></div>)}</div></div>}
     {!solver?.shortfall&&<div className="wow-info-row"><Icon name="info"/> No unpaid obligation shortfall is detected in this scenario. EssentialGuard still evaluates your reserve. Select a delayed scenario to reveal rescue options.</div>}
     <div className="wow-info-row"><Icon name="shield"/> {guard?.meaning}</div><button className="button-primary" onClick={()=>navigate('rescue')}>Open Rescue Planner <Icon name="arrow" size={16}/></button>
    </SectionShell>}
   {tab==='xray'&&<SectionShell eyebrow={selection.eyebrow} title="Nothing hidden behind the number." body="This explanation is assembled from ledger inputs, arrival dates and the financial engine — not invented by a chatbot." tag="TRACEABLE CAUSES">
     <div className="wow-xray-head"><div><span className="wow-kicker">EARLIEST-ARRIVAL BASELINE</span><strong>{rm(xray?.baseline_after_myr)}</strong><small>Projected position by {xray?short(xray.critical_date):'the deadline'}</small></div><span className="wow-xray-arrow">→</span><div className={xray?.status==='at_risk'?'risk':''}><span className="wow-kicker">YOUR {scenario.toUpperCase()} SCENARIO</span><strong>{rm(xray?.selected_after_myr)}</strong><small>{xray?.status==='at_risk'?`Unfunded gap ${rm(xray.gap_myr)}`:'Listed obligations covered'}</small></div></div>
     <div className="wow-xray-list"><div className="wow-kicker">REASON CODES & CAUSAL INPUT CHANGES</div>{xray?.causes?.length?xray.causes.map(c=><div className="wow-cause-card" key={c.id}><span className={'wow-cause-icon '+(c.affects_target_deadline?'at-risk':'')}>{c.affects_target_deadline?'!':'↗'}</span><div><strong>{c.label}</strong><p>{c.description}</p><small>{short(c.baseline_date)} → {short(c.scenario_date)} · {rm(c.expected_myr)} projected</small></div><span className="wow-code">{c.reason_code}</span></div>):<div className="wow-info-row">Current scenario has no changed funding arrival dates relative to the earliest-arrival assumption. Try the stress scenario.</div>}</div>
     <div className="wow-xray-bills"><span className="wow-kicker">RELEVANT LEDGER RECORDS</span><div className="wow-xray-rows">{xray?.contributing_items?.map((r,i)=><div key={i}><span>{r.label}</span><strong>{r.reason_code==='OUTSTANDING_OBLIGATION'?'-':'+'}{rm(r.amount_myr)}</strong></div>)}</div></div>
     <div className="wow-info-row"><Icon name="info"/> {xray?.disclaimer}</div><button className="button-primary" onClick={onDelayed}>Inspect delayed remittance <Icon name="arrow" size={16}/></button>
    </SectionShell>}
   {tab==='chaos'&&<SectionShell eyebrow={selection.eyebrow} title="Give the judges control." body="Seven real assertions run against an independent, reproducible synthetic test fixture. Nothing is marked passed until the checks execute." tag="ON-DEMAND ADVERSARIAL TESTS">
     <div className="wow-chaos-intro"><div><span className="wow-kicker">TRY TO BREAK CAMPUSFIN</span><h3>Designed to fail safely.</h3><p>Test delayed transfers, unsafe reserves, fee arithmetic, invalid FX rates, and no-mutation guarantees.</p></div><button className="button-primary" onClick={runChaos} disabled={busy}>{busy?'Running checks…':'Run 7 live checks'} <Icon name="arrow" size={16}/></button></div>
     {chaos?<><div className="wow-chaos-score"><div><span>ENGINE CHECKS COMPLETED</span><strong>{chaos.passed} <small>/ {chaos.total}</small></strong></div><div><span className="wow-score-indicator">{chaos.passed===chaos.total?'ALL CHECKS PASSED':'CHECKS FAILED'}</span><p>{chaos.scope}</p></div></div><div className="wow-chaos-results">{chaos.tests.map(t=><div className="wow-test-row" key={t.id}><span className={'wow-test-icon '+(t.pass?'pass':'fail')}>{t.pass?'✓':'×'}</span><div><strong>{t.name}</strong><small>Observed: {t.observed} · Expected: {t.expected}</small></div><span className="wow-code">{t.id}</span></div>)}</div><div className="wow-info-row"><Icon name="shield"/> {chaos.disclaimer}</div></>:<div className="wow-chaos-wait"><span className="wow-orb"/> <h3>Ready when you are.</h3><p>Run the checks to see actual calculated results, not a prerecorded green dashboard.</p></div>}
    </SectionShell>}
   {tab==='fx'&&<SectionShell eyebrow={selection.eyebrow} title="What if the currency shifts?" body="Stress-test the financial consequences of hypothetical exchange-rate changes. These are controlled assumptions, not live rates or FX predictions." tag="USD → MYR">
     <div className="wow-fx-head"><div className="wow-fx-input"><span className="wow-kicker">ILLUSTRATIVE FX RATE SHOCK</span><div className="wow-shock-num">{shock>0?'+':''}{shock}%</div><input aria-label="FX rate adjustment percentage" type="range" min="-20" max="20" step="1" value={shock} onChange={e=>setShock(Number(e.target.value))}/><div className="wow-slider-ends"><span>−20%</span><span>0%</span><span>+20%</span></div></div><div className="wow-fx-visual"><div className="wow-fx-circle"><span>USD / MYR</span><strong>{fx?.scenario_rate_myr_per_usd||'4.2000'}</strong><small>Simulation only</small></div></div></div>
     <div className="wow-metric-grid"><RiskMetric label="Original transfer value" value={rm(fx?.family_before_myr)} detail={`Rate ${fx?.original_rate_myr_per_usd||'—'} MYR/USD`}/><RiskMetric label="Under this FX assumption" value={rm(fx?.family_after_myr)} detail={`Rate ${fx?.scenario_rate_myr_per_usd||'—'} MYR/USD`} risk={Number(fx?.family_difference_myr)<0}/><RiskMetric label="Difference in funds received" value={(Number(fx?.family_difference_myr)>0?'+':'')+rm(fx?.family_difference_myr)} detail="Family remittance only" risk={Number(fx?.family_difference_myr)<0}/></div>
     <div className="wow-fx-risk"><span className="wow-kicker">TUITION GAP COMPARISON</span><div><div><span>Current rate assumption</span><strong>{rm(fx?.baseline?.gap_myr)}</strong></div><span>→</span><div><span>Shocked rate assumption</span><strong>{rm(fx?.stressed?.gap_myr)}</strong></div></div></div>
     <div className="wow-info-row"><Icon name="info"/> {fx?.disclaimer}</div><button className="button-outline" onClick={()=>navigate('transfers')}>Inspect detailed transfer fees <Icon name="arrow" size={16}/></button>
    </SectionShell>}
  </div>
  <div className="wow-bottom-cta"><div><span className="wow-kicker">BACK TO THE CORE WORKFLOW</span><strong>Predict. Rescue. Prove.</strong><p>Explore the flagship funding recovery journey, verified by the same calculation engine.</p></div><button className="button-primary" onClick={()=>navigate('rescue')}>Open Rescue Planner <Icon name="arrow" size={16}/></button></div>
 </>;
}
