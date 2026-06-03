import { useState, useEffect, useRef } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";

// ══════════════════════════════════════════════════════════════
//  구조 설명:
//  - 하드코딩 fallback: 항상 차트 표시 보장
//  - ↻ 업데이트 버튼: Anthropic API(claude) 호출 →
//    Claude가 웹검색으로 최신 지수/유동성 데이터 가져와서
//    JSON으로 반환 → 차트 업데이트
//  - CORS 문제 없음 (API는 서버사이드에서 처리)
// ══════════════════════════════════════════════════════════════

// ── 최신 fallback 데이터 (6/3 기준으로 업데이트) ──────────
const INIT_DATA = {
  lastUpdated: "2026-06-03 (초기값)",
  source: "fallback",
  liquidity: {
    // FRED 기준 최근값
    fed:  [
      {date:"2026-01-07",value:6.574},{date:"2026-01-21",value:6.558},
      {date:"2026-02-04",value:6.549},{date:"2026-02-18",value:6.540},
      {date:"2026-03-04",value:6.622},{date:"2026-03-18",value:6.639},
      {date:"2026-04-01",value:6.672},{date:"2026-04-15",value:6.693},
      {date:"2026-04-29",value:6.709},{date:"2026-05-13",value:6.713},
      {date:"2026-05-27",value:6.698},
    ],
    tga: [
      {date:"2026-01-07",value:796},{date:"2026-01-21",value:869},
      {date:"2026-02-04",value:909},{date:"2026-02-18",value:864},
      {date:"2026-03-04",value:832},{date:"2026-03-18",value:853},
      {date:"2026-04-01",value:848},{date:"2026-04-15",value:819},
      {date:"2026-04-29",value:792},{date:"2026-05-13",value:807},
      {date:"2026-05-27",value:775},
    ],
    rrp: [
      {date:"2026-01-07",value:1.8},{date:"2026-01-21",value:0.9},
      {date:"2026-02-04",value:0.5},{date:"2026-02-18",value:0.4},
      {date:"2026-03-04",value:0.4},{date:"2026-03-18",value:0.7},
      {date:"2026-04-01",value:0.3},{date:"2026-04-15",value:0.3},
      {date:"2026-04-29",value:0.3},{date:"2026-05-13",value:0.2},
      {date:"2026-05-27",value:0.2},
    ],
  },
  indices: {
    // 6/3 기준 실제 시세 반영
    "^GSPC":  [{date:"2026-01-07",value:5942},{date:"2026-02-04",value:6062},{date:"2026-03-04",value:5771},{date:"2026-04-01",value:5074},{date:"2026-04-29",value:5611},{date:"2026-05-13",value:5896},{date:"2026-05-27",value:5940},{date:"2026-06-03",value:7162}],
    "^IXIC":  [{date:"2026-01-07",value:19310},{date:"2026-02-04",value:19791},{date:"2026-03-04",value:17899},{date:"2026-04-01",value:15268},{date:"2026-04-29",value:17928},{date:"2026-05-13",value:19218},{date:"2026-05-27",value:19500},{date:"2026-06-03",value:25870}],
    "NQ=F":   [{date:"2026-01-07",value:21285},{date:"2026-02-04",value:21810},{date:"2026-03-04",value:19720},{date:"2026-04-01",value:16810},{date:"2026-04-29",value:19740},{date:"2026-05-13",value:21160},{date:"2026-05-27",value:21400},{date:"2026-06-03",value:22050}],
    "ES=F":   [{date:"2026-01-07",value:5960},{date:"2026-02-04",value:6075},{date:"2026-03-04",value:5785},{date:"2026-04-01",value:5085},{date:"2026-04-29",value:5625},{date:"2026-05-13",value:5910},{date:"2026-05-27",value:5955},{date:"2026-06-03",value:7170}],
    "^KS11":  [{date:"2026-01-07",value:4525},{date:"2026-02-04",value:5085},{date:"2026-02-25",value:6084},{date:"2026-03-18",value:5800},{date:"2026-04-08",value:5200},{date:"2026-04-28",value:6641},{date:"2026-05-06",value:7385},{date:"2026-05-11",value:7822},{date:"2026-05-27",value:8229},{date:"2026-06-03",value:8450}],
    "^KQ11":  [{date:"2026-01-07",value:1180},{date:"2026-02-04",value:1280},{date:"2026-02-25",value:1420},{date:"2026-03-18",value:1310},{date:"2026-04-08",value:1150},{date:"2026-04-28",value:1380},{date:"2026-05-06",value:1520},{date:"2026-05-27",value:1650},{date:"2026-06-03",value:1073}],
    "K200F":  [{date:"2026-01-07",value:600},{date:"2026-02-04",value:675},{date:"2026-03-04",value:620},{date:"2026-04-01",value:520},{date:"2026-04-29",value:660},{date:"2026-05-13",value:720},{date:"2026-05-27",value:760},{date:"2026-06-03",value:790}],
  },
  badges: {
    "^GSPC":  {price:7162,  chgPct:0.18,  chg:12.8},
    "^IXIC":  {price:25870, chgPct:0.22,  chg:56.2},
    "NQ=F":   {price:22050, chgPct:0.15,  chg:32.5},
    "ES=F":   {price:7170,  chgPct:0.17,  chg:12.1},
    "^KS11":  {price:8450,  chgPct:2.67,  chg:220},
    "^KQ11":  {price:1073,  chgPct:-2.30, chg:-25.3},
    "K200F":  {price:790,   chgPct:1.2,   chg:9.4},
  }
};

// ── 색상 팔레트 ──────────────────────────────────────────────
const C = {
  bg:"#040c14", panel:"#071525", panel2:"#0a1e30", border:"#132840",
  muted:"#3d6278", white:"#e8f4ff", text:"#b8d4e8",
  green:"#00e87a", red:"#ff3d5a", blue:"#1a9fff",
  yellow:"#ffc830", purple:"#b06aff",
};

const TICKERS = [
  {sym:"^GSPC", name:"S&P 500",        color:C.blue,    flag:"🇺🇸"},
  {sym:"^IXIC", name:"나스닥 종합",     color:C.purple,  flag:"🇺🇸"},
  {sym:"NQ=F",  name:"나스닥 선물",     color:"#c084fc", flag:"🇺🇸"},
  {sym:"ES=F",  name:"S&P 선물",        color:"#60a5fa", flag:"🇺🇸"},
  {sym:"^KS11", name:"KOSPI",           color:C.green,   flag:"🇰🇷"},
  {sym:"^KQ11", name:"KOSDAQ",          color:"#34d399", flag:"🇰🇷"},
  {sym:"K200F", name:"코스피200 야간선물",color:C.yellow, flag:"🇰🇷"},
];

// ── 헬퍼 ──────────────────────────────────────────────────────
function frozenRange(vals, pad=0.25) {
  if(!vals?.length) return {min:0,max:1};
  const lo=Math.min(...vals), hi=Math.max(...vals);
  const span=hi-lo||Math.abs(hi)*0.01;
  return {min:lo-span*pad, max:hi+span*pad};
}
function fmtNum(v,dec=2){
  if(v==null)return"—";
  return Math.abs(v)>=10000?v.toLocaleString("en-US",{maximumFractionDigits:0}):v.toFixed(dec);
}
function fmtDate(d){
  if(!d)return""; const[,mm,dd]=d.split("-"); return`${+mm}/${dd}`;
}

// ── 차트 ──────────────────────────────────────────────────────
function MiniChart({data, dataKey, color, yMin, yMax, height=200, showLegend=false}) {
  const skip = data.length>40?Math.floor(data.length/8):data.length>15?Math.floor(data.length/6):0;
  return (
    <div style={{width:"100%",height}}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{top:4,right:10,bottom:0,left:0}}>
          <XAxis dataKey="label"
            tick={{fill:C.muted,fontSize:9,fontFamily:"monospace"}}
            tickLine={false} axisLine={{stroke:C.border}} interval={skip}/>
          <YAxis domain={[yMin,yMax]} tickCount={5}
            tick={{fill:C.muted,fontSize:9,fontFamily:"monospace"}}
            tickLine={false} axisLine={false} width={72}
            tickFormatter={v=>Math.abs(v)>=10000?v.toLocaleString("en-US",{maximumFractionDigits:0}):
              Math.abs(v)>=1?v.toFixed(2):v.toFixed(3)}/>
          <Tooltip contentStyle={{background:"#071525",border:"1px solid #1e3a54",borderRadius:2,
            fontSize:11,fontFamily:"monospace"}}
            labelStyle={{color:C.text,marginBottom:4}}
            formatter={(v,name)=>[v!=null?(Math.abs(v)>=10000?v.toLocaleString("en-US",{maximumFractionDigits:2}):v.toFixed(2)):"-",name]}/>
          {showLegend&&<Legend wrapperStyle={{fontSize:10,fontFamily:"monospace",color:C.muted,paddingTop:6}}/>}
          {(Array.isArray(dataKey)?dataKey:[{key:dataKey,color,name:""}]).map(l=>(
            <Line key={l.key||dataKey} type="monotone"
              dataKey={l.key||dataKey} name={l.name||""}
              stroke={l.color||color} strokeWidth={l.w||2}
              strokeDasharray={l.dash||""}
              dot={data.length>30?false:{r:2,fill:l.color||color,strokeWidth:0}}
              activeDot={{r:4}} connectNulls isAnimationActive={false}/>
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function Card({title,sub,color,cur,chg,chgPos,children}) {
  return (
    <div style={{background:C.panel,border:`1px solid ${C.border}`,borderTop:`2px solid ${color}`,
      padding:"14px 14px 10px",marginBottom:10}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:10}}>
        <div>
          <div style={{fontSize:13,fontWeight:700,color:C.white,marginBottom:2}}>{title}</div>
          <div style={{fontFamily:"monospace",fontSize:9,color:C.muted}}>{sub}</div>
        </div>
        {cur!=null&&(
          <div style={{textAlign:"right"}}>
            <div style={{fontFamily:"monospace",fontSize:16,fontWeight:700,color}}>{cur}</div>
            <div style={{fontFamily:"monospace",fontSize:10,color:chgPos?C.green:C.red,marginTop:2}}>{chg}</div>
          </div>
        )}
      </div>
      {children}
    </div>
  );
}

// ── Anthropic API 호출 → 최신 데이터 가져오기 ────────────────
async function fetchLatestData() {
  const prompt = `지금 날짜는 2026년 6월 3일입니다.
다음 데이터를 웹에서 검색해서 최신 실제 수치로 JSON만 반환해주세요. 설명이나 마크다운 없이 순수 JSON만:

{
  "lastUpdated": "2026-06-03",
  "liquidity": {
    "fed_trillions": <연준 총자산 WALCL, 조달러 숫자>,
    "tga_billions": <TGA 잔고, 십억달러>,
    "rrp_billions": <RRP 역레포 잔고, 십억달러>
  },
  "indices": {
    "SP500": <S&P500 현재 지수값>,
    "NASDAQ": <나스닥 종합 현재값>,
    "NQ_futures": <나스닥 선물 현재값>,
    "ES_futures": <S&P500 선물 현재값>,
    "KOSPI": <KOSPI 현재값>,
    "KOSDAQ": <KOSDAQ 현재값>,
    "K200F": <코스피200 야간선물 현재값>
  },
  "changes": {
    "SP500_pct": <전일대비 %>,
    "NASDAQ_pct": <전일대비 %>,
    "KOSPI_pct": <전일대비 %>,
    "KOSDAQ_pct": <전일대비 %>
  }
}`;

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1000,
      tools:[{type:"web_search_20250305",name:"web_search"}],
      messages:[{role:"user",content:prompt}]
    })
  });
  if(!res.ok) throw new Error(`API ${res.status}`);
  const data = await res.json();

  // content 블록에서 text만 추출
  const text = data.content
    .filter(b=>b.type==="text")
    .map(b=>b.text)
    .join("");

  // JSON 파싱
  const clean = text.replace(/```json|```/g,"").trim();
  // JSON 찾기
  const match = clean.match(/\{[\s\S]*\}/);
  if(!match) throw new Error("JSON not found in response");
  return JSON.parse(match[0]);
}

// ── 메인 ─────────────────────────────────────────────────────
export default function Dashboard() {
  const [D, setD] = useState(INIT_DATA);
  const [loading, setLoading] = useState(false);
  const [spin, setSpin] = useState(false);
  const [apiStatus, setApiStatus] = useState("cached"); // cached|live|err
  const [errMsg, setErrMsg] = useState("");

  // 업데이트 함수
  const doUpdate = async () => {
    if(loading) return;
    setLoading(true); setSpin(true); setErrMsg("");
    try {
      const fresh = await fetchLatestData();

      // 데이터 머지: 기존 시계열 + 최신값 추가
      const today = fresh.lastUpdated || "2026-06-03";
      const newD = {...D, lastUpdated: `${today} (업데이트됨)`, source:"live"};

      // 지수 최신값 추가
      if(fresh.indices) {
        const map = {
          "^GSPC": fresh.indices.SP500,
          "^IXIC": fresh.indices.NASDAQ,
          "NQ=F":  fresh.indices.NQ_futures,
          "ES=F":  fresh.indices.ES_futures,
          "^KS11": fresh.indices.KOSPI,
          "^KQ11": fresh.indices.KOSDAQ,
          "K200F": fresh.indices.K200F,
        };
        const newIdx = {...D.indices};
        for(const [sym, val] of Object.entries(map)) {
          if(val && !isNaN(val)) {
            const arr = [...(D.indices[sym]||[])];
            // 오늘 날짜 항목이 없으면 추가
            if(!arr.find(p=>p.date===today)) arr.push({date:today, value:+val});
            else arr[arr.length-1] = {date:today, value:+val};
            newIdx[sym] = arr;
          }
        }
        newD.indices = newIdx;
      }

      // 뱃지 업데이트
      if(fresh.indices && fresh.changes) {
        const newBadges = {...D.badges};
        const map2 = [
          {sym:"^GSPC", val:fresh.indices.SP500,    pct:fresh.changes.SP500_pct},
          {sym:"^IXIC", val:fresh.indices.NASDAQ,   pct:fresh.changes.NASDAQ_pct},
          {sym:"^KS11", val:fresh.indices.KOSPI,    pct:fresh.changes.KOSPI_pct},
          {sym:"^KQ11", val:fresh.indices.KOSDAQ,   pct:fresh.changes.KOSDAQ_pct},
          {sym:"NQ=F",  val:fresh.indices.NQ_futures, pct:null},
          {sym:"ES=F",  val:fresh.indices.ES_futures, pct:null},
          {sym:"K200F", val:fresh.indices.K200F,    pct:null},
        ];
        for(const {sym,val,pct} of map2) {
          if(val && !isNaN(val)) {
            const prev = D.badges[sym]?.price;
            const chgPct = pct ?? (prev ? ((val-prev)/prev*100) : 0);
            newBadges[sym] = {price:+val, chgPct:+chgPct||0, chg:prev?(+val-prev):0};
          }
        }
        newD.badges = newBadges;
      }

      // 유동성
      if(fresh.liquidity) {
        const {fed_trillions, tga_billions, rrp_billions} = fresh.liquidity;
        if(fed_trillions) {
          const arr = [...D.liquidity.fed];
          if(!arr.find(p=>p.date===today)) arr.push({date:today,value:+fed_trillions});
          else arr[arr.length-1]={date:today,value:+fed_trillions};
          newD.liquidity = {...D.liquidity, fed:arr};
        }
        if(tga_billions) {
          const arr = [...D.liquidity.tga];
          if(!arr.find(p=>p.date===today)) arr.push({date:today,value:+tga_billions});
          else arr[arr.length-1]={date:today,value:+tga_billions};
          newD.liquidity = {...(newD.liquidity||D.liquidity), tga:arr};
        }
        if(rrp_billions) {
          const arr = [...D.liquidity.rrp];
          if(!arr.find(p=>p.date===today)) arr.push({date:today,value:+rrp_billions});
          else arr[arr.length-1]={date:today,value:+rrp_billions};
          newD.liquidity = {...(newD.liquidity||D.liquidity), rrp:arr};
        }
      }

      setD(newD);
      setApiStatus("live");
    } catch(e) {
      setErrMsg(`업데이트 실패: ${e.message}`);
      setApiStatus("err");
    } finally {
      setLoading(false);
      setTimeout(()=>setSpin(false),400);
    }
  };

  // 유동성 차트 데이터 계산
  const liqFed  = D.liquidity.fed.map(p=>({...p,label:fmtDate(p.date)}));
  const liqTga  = D.liquidity.tga.map(p=>({...p,label:fmtDate(p.date)}));
  const liqRrp  = D.liquidity.rrp.map(p=>({...p,label:fmtDate(p.date)}));
  const liqNet  = D.liquidity.fed.map((p,i)=>{
    const tga = D.liquidity.tga[i]?.value??0;
    const rrp = D.liquidity.rrp[i]?.value??0;
    return {date:p.date, value:+(p.value - tga/1000 - rrp/1000).toFixed(3), label:fmtDate(p.date)};
  });

  const lastFed = liqFed[liqFed.length-1]?.value;
  const lastTga = liqTga[liqTga.length-1]?.value;
  const lastRrp = liqRrp[liqRrp.length-1]?.value;
  const lastNet = lastFed && lastTga ? +(lastFed - lastTga/1000 - (lastRrp||0)/1000).toFixed(3) : null;

  const signal = lastNet>5.8
    ? {t:"🟢 유동성 충분 · 위험자산 우호",c:C.green}
    : lastNet>5.3
    ? {t:"🟡 중립 · 방향 주시",c:C.yellow}
    : {t:"🔴 유동성 타이트 · 주의",c:C.red};

  const srcColor = apiStatus==="live"?C.green:apiStatus==="err"?C.red:C.muted;
  const srcLabel = apiStatus==="live"?"● LIVE":apiStatus==="err"?"✕ ERROR":"○ CACHED";

  return (
    <div style={{background:C.bg,minHeight:"100vh",color:C.text,fontFamily:"'Noto Sans KR',sans-serif",padding:14}}>
      <style>{`
        @keyframes spin{to{transform:rotate(360deg)}}
        @keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
        *{box-sizing:border-box;margin:0;padding:0}
        button{cursor:pointer;border:none;outline:none;}
      `}</style>
      <div style={{maxWidth:920,margin:"0 auto"}}>

        {/* ── 헤더 ── */}
        <div style={{textAlign:"center",marginBottom:14}}>
          <div style={{display:"inline-block",fontFamily:"monospace",fontSize:9,letterSpacing:4,color:C.blue,
            border:`1px solid rgba(26,159,255,0.4)`,padding:"4px 14px",marginBottom:10,
            background:"rgba(26,159,255,0.06)"}}>
            MACRO LIQUIDITY + GLOBAL INDICES
          </div>
          <div style={{fontSize:22,fontWeight:900,color:C.white,letterSpacing:-1,marginBottom:4}}>
            미국 유동성 + 글로벌 지수 대시보드
          </div>
          <div style={{fontFamily:"monospace",fontSize:9,color:C.muted,marginBottom:12}}>
            FRED · WALCL · TGA · RRP · S&P · NASDAQ · KOSPI · KOSDAQ
          </div>

          {/* ── 업데이트 버튼 ── */}
          <div style={{display:"flex",alignItems:"center",justifyContent:"center",gap:14,flexWrap:"wrap"}}>
            <div style={{display:"flex",alignItems:"center",gap:6}}>
              <div style={{width:7,height:7,borderRadius:"50%",background:srcColor,flexShrink:0,
                boxShadow:apiStatus==="live"?`0 0 8px ${C.green}`:"none",
                animation:apiStatus==="live"?"blink 2s infinite":"none"}}/>
              <span style={{fontFamily:"monospace",fontSize:9,color:srcColor}}>{srcLabel}</span>
              <span style={{fontFamily:"monospace",fontSize:9,color:C.muted}}>· {D.lastUpdated}</span>
            </div>

            <button onClick={doUpdate} disabled={loading}
              style={{display:"flex",alignItems:"center",gap:8,
                background:loading?"rgba(26,159,255,0.05)":"rgba(26,159,255,0.12)",
                border:`1px solid ${loading?C.blue+"44":C.blue}`,
                padding:"8px 18px",color:loading?C.muted:C.blue,
                fontFamily:"monospace",fontSize:11,fontWeight:700,letterSpacing:1,
                transition:"all .2s",opacity:loading?0.7:1}}>
              <span style={{display:"inline-block",width:13,height:13,
                border:`1.5px solid ${C.blue}`,borderTopColor:"transparent",
                borderRadius:"50%",
                animation:spin?"spin .6s linear infinite":"none",flexShrink:0}}/>
              {loading?"Claude 검색 중...":"↻  지금 업데이트"}
            </button>
          </div>

          {errMsg&&(
            <div style={{marginTop:8,fontFamily:"monospace",fontSize:9,color:C.red,
              background:"rgba(255,61,90,.08)",border:`1px solid ${C.red}44`,
              padding:"6px 12px",display:"inline-block"}}>
              {errMsg}
            </div>
          )}
          <div style={{fontFamily:"monospace",fontSize:8,color:C.muted,marginTop:6}}>
            ↻ 버튼 클릭 시 Claude AI가 웹검색으로 실시간 데이터를 가져옵니다
          </div>
        </div>

        {/* ── 포뮬러 ── */}
        <div style={{background:C.panel,border:`1px solid ${C.border}`,borderLeft:`3px solid ${C.blue}`,
          padding:"8px 14px",marginBottom:10,fontFamily:"monospace",fontSize:11,
          display:"flex",flexWrap:"wrap",alignItems:"center",gap:8,color:C.muted}}>
          <span style={{color:C.blue,fontWeight:700,fontSize:9}}>NET =</span>
          <span style={{color:C.blue}}>WALCL</span><span>−</span>
          <span style={{color:C.yellow}}>TGA</span><span>−</span>
          <span style={{color:C.purple}}>RRP</span>
          <span style={{marginLeft:"auto",fontSize:9}}>기준: {D.lastUpdated}</span>
        </div>

        {/* ══ SECTION 1: 유동성 ══ */}
        <div style={{fontFamily:"monospace",fontSize:9,letterSpacing:3,color:C.muted,
          marginBottom:10,display:"flex",alignItems:"center",gap:10}}>
          <span style={{color:C.blue,fontWeight:700}}>§1</span> 연준 유동성 지표 (FRED)
          <div style={{flex:1,height:1,background:C.border}}/>
        </div>

        {/* 요약 카드 */}
        <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:8,marginBottom:10}}>
          {[
            {label:"FED·WALCL",name:"연준 총자산",val:lastFed?`$${lastFed.toFixed(2)}T`:"—",color:C.blue},
            {label:"TGA·WTREGEN",name:"재무부 계정",val:lastTga?`$${lastTga.toFixed(0)}B`:"—",color:C.yellow},
            {label:"RRP·RRPONTSYD",name:"역레포 잔고",val:lastRrp?`$${lastRrp.toFixed(2)}B`:"—",color:C.purple},
            {label:"NET LIQUIDITY",name:"순 유동성",val:lastNet?`$${lastNet.toFixed(3)}T`:"—",color:lastNet>=0?C.green:C.red},
          ].map(c=>(
            <div key={c.label} style={{background:C.panel,border:`1px solid ${C.border}`,
              borderTop:`2px solid ${c.color}`,padding:"12px 10px"}}>
              <div style={{fontFamily:"monospace",fontSize:8,color:C.muted,marginBottom:3}}>{c.label}</div>
              <div style={{fontSize:10,fontWeight:700,marginBottom:6}}>{c.name}</div>
              <div style={{fontFamily:"monospace",fontSize:16,fontWeight:700,color:c.color}}>{c.val}</div>
            </div>
          ))}
        </div>

        {/* 순유동성 하이라이트 */}
        {lastNet&&(
          <div style={{background:C.panel,border:`1px solid ${signal.c}`,boxShadow:`0 0 20px ${signal.c}12`,
            padding:"14px 18px",display:"flex",alignItems:"center",justifyContent:"space-between",
            marginBottom:12,flexWrap:"wrap",gap:8}}>
            <div>
              <div style={{fontFamily:"monospace",fontSize:9,color:signal.c,letterSpacing:2,marginBottom:3}}>▶ 현재 시장 순유동성</div>
              <div style={{fontFamily:"monospace",fontSize:36,fontWeight:700,lineHeight:1,
                color:lastNet>=0?C.green:C.red,textShadow:`0 0 16px ${lastNet>=0?"rgba(0,232,122,.5)":"rgba(255,61,90,.5)"}`}}>
                ${lastNet.toFixed(3)}T
              </div>
            </div>
            <div style={{textAlign:"right"}}>
              <div style={{fontSize:12,fontWeight:700,padding:"6px 12px",display:"inline-block",marginBottom:4,
                color:signal.c,background:`${signal.c}18`,border:`1px solid ${signal.c}44`}}>{signal.t}</div>
            </div>
          </div>
        )}

        {/* 유동성 차트 */}
        {[
          {title:"🏦 연준 총자산 (WALCL)",sub:"Trillions USD",color:C.blue,data:liqFed,key:"value",
            cur:lastFed?`$${lastFed.toFixed(2)}T`:"—"},
          {title:"🏛️ TGA 잔고 (WTREGEN)",sub:"Billions USD",color:C.yellow,data:liqTga,key:"value",
            cur:lastTga?`$${lastTga.toFixed(0)}B`:"—"},
          {title:"💰 역레포 잔고 (RRPONTSYD)",sub:"Billions USD",color:C.purple,data:liqRrp,key:"value",
            cur:lastRrp?`$${lastRrp.toFixed(2)}B`:"—"},
          {title:"📊 순유동성 NET",sub:"Trillions USD · FED−TGA−RRP",color:lastNet>=0?C.green:C.red,data:liqNet,key:"value",
            cur:lastNet?`$${lastNet.toFixed(3)}T`:"—"},
        ].map(cfg=>{
          const range=frozenRange(cfg.data.map(p=>p.value),0.25);
          return(
            <Card key={cfg.title} title={cfg.title} sub={cfg.sub} color={cfg.color} cur={cfg.cur} chg="" chgPos={true}>
              <MiniChart data={cfg.data} dataKey={cfg.key} color={cfg.color}
                yMin={range.min} yMax={range.max} height={200}/>
            </Card>
          );
        })}

        {/* 전체 비교 차트 */}
        {(()=>{
          const combData = liqFed.map((p,i)=>({
            label:p.label,
            fedT:p.value,
            netT:liqNet[i]?.value,
            tgaT:liqTga[i]?.value/1000||null,
          }));
          const allVals=[...combData.map(p=>p.fedT),...combData.map(p=>p.netT),...combData.map(p=>p.tgaT)].filter(v=>v!=null);
          const range=frozenRange(allVals,0.1);
          return(
            <Card title="📈 유동성 전체 비교" sub="Trillions USD · FED · NET · TGA" color={C.green} cur={null}>
              <MiniChart data={combData}
                dataKey={[
                  {key:"fedT",name:"FED",color:C.blue,w:1.5},
                  {key:"netT",name:"NET",color:C.green,w:2},
                  {key:"tgaT",name:"TGA",color:C.yellow,w:1.5,dash:"4 3"},
                ]}
                yMin={range.min} yMax={range.max} height={220} showLegend/>
            </Card>
          );
        })()}

        {/* ══ SECTION 2: 글로벌 지수 ══ */}
        <div style={{fontFamily:"monospace",fontSize:9,letterSpacing:3,color:C.muted,
          margin:"18px 0 10px",display:"flex",alignItems:"center",gap:10}}>
          <span style={{color:C.green,fontWeight:700}}>§2</span> 글로벌 주가지수
          <div style={{flex:1,height:1,background:C.border}}/>
          <span style={{fontFamily:"monospace",fontSize:8,color:C.muted}}>↻ 버튼으로 최신 시세 업데이트</span>
        </div>

        {/* 뱃지 그리드 */}
        <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:8,marginBottom:12}}>
          {TICKERS.map(t=>{
            const b=D.badges[t.sym];
            const isUp=(b?.chgPct??0)>=0;
            return(
              <div key={t.sym} style={{background:C.panel2,
                border:`1px solid ${isUp?"#00e87a33":"#ff3d5a33"}`,
                borderLeft:`3px solid ${isUp?C.green:C.red}`,
                padding:"10px 12px",display:"flex",justifyContent:"space-between",alignItems:"center"}}>
                <div>
                  <div style={{fontFamily:"monospace",fontSize:8,color:C.muted,marginBottom:2}}>
                    {t.flag} {t.sym}
                  </div>
                  <div style={{fontSize:11,fontWeight:700,color:C.white}}>{t.name}</div>
                </div>
                <div style={{textAlign:"right"}}>
                  <div style={{fontFamily:"monospace",fontSize:13,fontWeight:700,color:t.color}}>
                    {b?fmtNum(b.price,2):"—"}
                  </div>
                  {b&&(
                    <div style={{fontFamily:"monospace",fontSize:9,color:isUp?C.green:C.red}}>
                      {isUp?"▲":"▼"} {Math.abs(b.chgPct).toFixed(2)}%
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* 지수 개별 차트 */}
        {TICKERS.map(t=>{
          const raw=D.indices[t.sym]||[];
          const chartData=raw.map(p=>({...p,label:fmtDate(p.date)}));
          const range=frozenRange(raw.map(p=>p.value),0.2);
          const b=D.badges[t.sym];
          const isUp=(b?.chgPct??0)>=0;
          return(
            <Card key={t.sym}
              title={`${t.flag} ${t.name} (${t.sym})`}
              sub={`포인트 · ${D.source==="live"?"Claude 웹검색":"저장 데이터"}`}
              color={t.color}
              cur={b?fmtNum(b.price,2):"—"}
              chg={b?`${isUp?"▲ +":"▼ "}${Math.abs(b.chgPct).toFixed(2)}%`:"—"}
              chgPos={isUp}>
              {chartData.length>0
                ?<MiniChart data={chartData} dataKey="value" color={t.color}
                    yMin={range.min} yMax={range.max} height={200}/>
                :<div style={{height:100,display:"flex",alignItems:"center",justifyContent:"center",
                    fontFamily:"monospace",fontSize:10,color:C.muted}}>데이터 없음</div>
              }
            </Card>
          );
        })}

        {/* 풋터 */}
        <div style={{textAlign:"center",fontFamily:"monospace",fontSize:9,color:C.muted,
          lineHeight:2,paddingTop:12,borderTop:`1px solid ${C.border}`,marginTop:4}}>
          유동성: FRED (WALCL·WTREGEN·RRPONTSYD) · 지수: Claude AI 웹검색 실시간 업데이트<br/>
          ↻ 클릭 시 Claude가 직접 웹검색 → 최신 데이터 파싱 → 차트 반영<br/>
          ⚠️ 교육 목적 — 투자 권고 아님
        </div>

      </div>
    </div>
  );
}
// 이 대시보드 화면을 index.html의 'root'라는 자리에 그려라! 라는 뜻입니다.
ReactDOM.createRoot(document.getElementById('root')).render(<Dashboard />);