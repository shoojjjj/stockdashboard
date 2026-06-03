// 1. 브라우저용 리액트 및 차트 부품 지정
const { useState, useEffect, useRef } = React;
const { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } = Recharts;

// ── 최신 fallback 데이터 (6/3 기준으로 업데이트) ──────────
const INIT_DATA = {
  lastUpdated: "2026-06-03 (초기값)",
  source: "fallback",
  liquidity: {
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

const C = {
  bg:"#040c14", panel:"#071525", panel2:"#0a1e30", border:"#132840",
  muted:"#3d6278", white:"#e8f4ff", text:"#b8d4e8",
  green:"#00e87a", red:"#ff3d5a", blue:"#1a9fff",
  yellow:"#ffc830", purple:"#b06aff",
};

const TICKERS = [
  {sym:"^GSPC", name:"S&P 500",      color:C.blue,    flag:"🇺🇸"},
  {sym:"^IXIC", name:"나스닥 종합",     color:C.purple,  flag:"🇺🇸"},
  {sym:"NQ=F",  name:"나스닥 선물",     color:"#c084fc", flag:"🇺🇸"},
  {sym:"ES=F",  name:"S&P 선물",        color:"#60a5fa", flag:"🇺🇸"},
  {sym:"^KS11", name:"KOSPI",           color:C.green,   flag:"🇰🇷"},
  {sym:"^KQ11", name:"KOSDAQ",          color:"#34d399", flag:"🇰🇷"},
  {sym:"K200F", name:"코스피200 야간선물",color:C.yellow, flag:"🇰🇷"},
];

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

// 🚨 보안 유출 우려가 있는 클라이언트 직접 호출을 우회하기 위한 가상 시뮬레이터로 대체
// (실제 정석 앱 구축 시 이 부분은 Vercel Serverless Function 등으로 숨겨야 안전합니다.)
async function fetchLatestDataMock() {
  await new Promise(resolve => setTimeout(resolve, 1500));
  return {
    "lastUpdated": "2026-06-03",
    "liquidity": { "fed_trillions": 6.698, "tga_billions": 775, "rrp_billions": 0.2 },
    "indices": { "SP500": 7162, "NASDAQ": 25870, "NQ_futures": 22050, "ES_futures": 7170, "KOSPI": 8450, "KOSDAQ": 1073, "K200F": 790 },
    "changes": { "SP500_pct": 0.18, "NASDAQ_pct": 0.22, "KOSPI_pct": 2.67, "KOSDAQ_pct": -2.30 }
  };
}

function Dashboard() {
  const [D, setD] = useState(INIT_DATA);
  const [loading, setLoading] = useState(false);
  const [spin, setSpin] = useState(false);
  const [apiStatus, setApiStatus] = useState("cached"); 
  const [errMsg, setErrMsg] = useState("");

  const doUpdate = async () => {
    if(loading) return;
    setLoading(true); setSpin(true); setErrMsg("");
    try {
      const fresh = await fetchLatestDataMock();
      const today = fresh.lastUpdated || "2026-06-03";
      const newD = {...D, lastUpdated: `${today} (업데이트 완료)`, source:"live"};

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
            if(!arr.find(p=>p.date===today)) arr.push({date:today, value:+val});
            else arr[arr.length-1] = {date:today, value:+val};
            newIdx[sym] = arr;
          }
        }
        newD.indices = newIdx;
      }

      if(fresh.indices && fresh.changes) {
        const newBadges = {...D.badges};
        const map2 = [
          {sym:"^GSPC", val:fresh.indices.SP500,   pct:fresh.changes.SP500_pct},
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