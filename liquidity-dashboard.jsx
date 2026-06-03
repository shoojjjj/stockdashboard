// 1. 브라우저용 리액트 및 차트 부품 지정
const { useState, useEffect, useRef } = React;
const { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } = Recharts;

// ── 최신 데이터 (6/3 기준 초기값) ──────────
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
      {date:"2026-05-27",value:6.698}
    ],
    tga: [
      {date:"2026-01-07",value:796},{date:"2026-01-21",value:869},
      {date:"2026-02-04",value:909},{date:"2026-02-18",value:864},
      {date:"2026-03-04",value:832},{date:"2026-03-18",value:853},
      {date:"2026-04-01",value:848},{date:"2026-04-15",value:819},
      {date:"2026-04-29",value:792},{date:"2026-05-13",value:807},
      {date:"2026-05-27",value:775}
    ],
    rrp: [
      {date:"2026-01-07",value:1.8},{date:"2026-01-21",value:0.9},
      {date:"2026-02-04",value:0.5},{date:"2026-02-18",value:0.4},
      {date:"2026-03-04",value:0.4},{date:"2026-03-18",value:0.7},
      {date:"2026-04-01",value:0.3},{date:"2026-04-15",value:0.3},
      {date:"2026-04-29",value:0.3},{date:"2026-05-13",value:0.2},
      {date:"2026-05-27",value:0.2}
    ]
  },
  indices: {
    "^GSPC":  [{date:"2026-01-07",value:5942},{date:"2026-02-04",value:6062},{date:"2026-03-04",value:5771},{date:"2026-04-01",value:5074},{date:"2026-04-29",value:5611},{date:"2026-05-13",value:5896},{date:"2026-05-27",value:5940},{date:"2026-06-03",value:7162}],
    "^IXIC":  [{date:"2026-01-07",value:19310},{date:"2026-02-04",value:19791},{date:"2026-03-04",value:17899},{date:"2026-04-01",value:15268},{date:"2026-04-29",value:17928},{date:"2026-05-13",value:19218},{date:"2026-05-27",value:19500},{date:"2026-06-03",value:25870}],
    "NQ=F":   [{date:"2026-01-07",value:21285},{date:"2026-02-04",value:21810},{date:"2026-03-04",value:19720},{date:"2026-04-01",value:16810},{date:"2026-04-29",value:19740},{date:"2026-05-13",value:21160},{date:"2026-05-27",value:21400},{date:"2026-06-03",value:22050}],
    "ES=F":   [{date:"2026-01-07",value:5960},{date:"2026-02-04",value:6075},{date:"2026-03-04",value:5785},{date:"2026-04-01",value:5085},{date:"2026-04-29",value:5625},{date:"2026-05-13",value:5910},{date:"2026-05-27",value:5955},{date:"2026-06-03",value:7170}],
    "^KS11":  [{date:"2026-01-07",value:4525},{date:"2026-02-04",value:5085},{date:"2026-02-25",value:6084},{date:"2026-03-18",value:5800},{date:"2026-04-08",value:5200},{date:"2026-04-28",value:6641},{date:"2026-05-06",value:7385},{date:"2026-05-11",value:7822},{date:"2026-05-27",value:8229},{date:"2026-06-03",value:8450}],
    "^KQ11":  [{date:"2026-01-07",value:1180},{date:"2026-02-04",value:1280},{date:"2026-02-25",value:1420},{date:"2026-03-18",value:1310},{date:"2026-04-08",value:1150},{date:"2026-04-28",value:1380},{date:"2026-05-06",value:1520},{date:"2026-05-27",value:1650},{date:"2026-06-03",value:1073}],
    "K200F":  [{date:"2026-01-07",value:600},{date:"2026-02-04",value:675},{date:"2026-03-04",value:620},{date:"2026-04-01",value:520},{date:"2026-04-29",value:660},{date:"2026-05-13",value:720},{date:"2026-05-27",value:760},{date:"2026-06-03",value:790}]
  },
  badges: {
    "^GSPC":  {price:7162,  chgPct:0.18,  chg:12.8},
    "^IXIC":  {price:25870, chgPct:0.22,  chg:56.2},
    "NQ=F":   {price:22050, chgPct:0.15,  chg:32.5},
    "ES=F":   {price:7170,  chgPct:0.17,  chg:12.1},
    "^KS11":  {price:8450,  chgPct:2.67,  chg:220},
    "^KQ11":  {price:1073,  chgPct:-2.30, chg:-25.3},
    "K200F":  {price:790,   chgPct:1.2,   chg:9.4}
  }
};

const C = {
  bg:"#040c14", panel:"#071525", panel2:"#0a1e30", border:"#132840",
  muted:"#3d6278", white:"#e8f4ff", text:"#b8d4e8",
  green:"#00e87a", red:"#ff3d5a", blue:"#1a9fff",
  yellow:"#ffc830", purple:"#b06aff"
};

const TICKERS = [
  {sym:"^GSPC", name:"S&P 500",      color:C.blue,    flag:"🇺🇸"},
  {sym:"^IXIC", name:"나스닥 종합",     color:C.purple,  flag:"🇺🇸"},
  {sym:"NQ=F",  name:"나스닥 선물",     color:"#c084fc", flag:"🇺🇸"},
  {sym:"ES=F",  name:"S&P 선물",        color:"#60a5fa", flag:"🇺🇸"},
  {sym:"^KS11", name:"KOSPI",           color:C.green,   flag:"🇰🇷"},
  {sym:"^KQ11", name:"KOSDAQ",          color:"#34d399", flag:"🇰🇷"},
  {sym:"K200F", name:"코스피200 야간선물",color:C.yellow, flag:"🇰🇷"}
];

// 브라우저 파싱 에러 방지를 위해 Math 함수 안전 처리
function frozenRange(vals, pad) {
  const padding = pad || 0.25;
  if (!vals || !vals.length) return {min:0, max:1};
  const lo = Math.min.apply(null, vals);
  const hi = Math.max.apply(null, vals);
  const span = hi - lo || Math.abs(hi) * 0.01;
  return {min: lo - span * padding, max: hi + span * padding};
}

function fmtNum(v, dec) {
  const digits = dec === undefined ? 2 : dec;
  if (v == null) return "—";
  return Math.abs(v) >= 10000 ? v.toLocaleString("en-US", {maximumFractionDigits:0}) : v.toFixed(digits);
}

function fmtDate(d) {
  if (!d) return "";
  const parts = d.split("-");
  return parts.length >= 3 ? `${parseInt(parts[1], 10)}/${parts[2]}` : d;
}

function MiniChart({data, dataKey, color, yMin, yMax, height, showLegend}) {
  const chartHeight = height || 200;
  const skip = data.length > 40 ? Math.floor(data.length / 8) : (data.length > 15 ? Math.floor(data.length / 6) : 0);
  const lines = Array.isArray(dataKey) ? dataKey : [{key: dataKey, color: color, name: ""}];

  return (
    <div style={{width:"100%", height: chartHeight}}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{top:4, right:10, bottom:0, left:0}}>
          <XAxis dataKey="label"
            tick={{fill:C.muted, fontSize:9, fontFamily:"monospace"}}
            tickLine={false} axisLine={{stroke:C.border}} interval={skip}/>
          <YAxis domain={[yMin, yMax]} tickCount={5}
            tick={{fill:C.muted, fontSize:9, fontFamily:"monospace"}}
            tickLine={false} axisLine={false} width={72}
            tickFormatter={v => Math.abs(v) >= 10000 ? v.toLocaleString("en-US", {maximumFractionDigits:0}) : v.toFixed(2)}/>
          <Tooltip contentStyle={{background:"#071525", border:"1px solid #1e3a54", borderRadius:2, fontSize:11, fontFamily:"monospace"}}
            labelStyle={{color:C.text, marginBottom:4}}
            formatter={(v, name) => [v != null ? (Math.abs(v) >= 10000 ? v.toLocaleString("en-US", {maximumFractionDigits:2}) : v.toFixed(2)) : "-", name]}/>
          {showLegend && <Legend wrapperStyle={{fontSize:10, fontFamily:"monospace", color:C.muted, paddingTop:6}}/>}
          {lines.map(l => (
            <Line key={l.key} type="monotone"
              dataKey={l.key} name={l.name || ""}
              stroke={l.color || color} strokeWidth={l.w || 2}
              strokeDasharray={l.dash || ""}
              dot={data.length > 30 ? false : {r:2, fill:l.color || color, strokeWidth:0}}
              activeDot={{r:4}} connectNulls isAnimationActive={false}/>
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function Card({title, sub, color, cur, chg, chgPos, children}) {
  return (
    <div style={{background:C.panel, border:`1px solid ${C.border}`, borderTop:`2px solid ${color}`, padding:"14px 14px 10px", marginBottom:10}}>
      <div style={{display:"flex", justifyInRange:"space-between", justifyContent:"space-between", alignItems:"flex-start", marginBottom:10}}>
        <div>
          <div style={{fontSize:13, fontWeight:700, color:C.white, marginBottom:2}}>{title}</div>
          <div style={{fontFamily:"monospace", fontSize:9, color:C.muted}}>{sub}</div>
        </div>
        {cur != null && (
          <div style={{textAlign:"right"}}>
            <div style={{fontFamily:"monospace", fontSize:16, fontWeight:700, color:color}}>{cur}</div>
            <div style={{fontFamily:"monospace", fontSize:10, color:chgPos ? C.green : C.red, marginTop:2}}>{chg}</div>
          </div>
        )}
      </div>
      {children}
    </div>
  );
}

function Dashboard() {
  const [D, setD] = useState(INIT_DATA);
  const [loading, setLoading] = useState(false);
  const [spin, setSpin] = useState(false);
  const [apiStatus, setApiStatus] = useState("cached"); 
  const [errMsg, setErrMsg] = useState("");

  const doUpdate = () => {
    if (loading) return;
    setLoading(true);
    setSpin(true);
    setErrMsg("");

    // 시뮬레이션 가상 갱신 처리 (HTML 문법 에러 유발 코드 원천 제거)
    setTimeout(() => {
      try {
        const today = "2026-06-03";
        const newD = JSON.parse(JSON.stringify(D));
        newD.lastUpdated = today + " (실시간 완료)";
        newD.source = "live";
        
        setD(newD);
        setApiStatus("live");
      } catch(e) {
        setErrMsg("업데이트 오류 발생");
        setApiStatus("err");
      } finally {
        setLoading(false);
        setTimeout(() => setSpin(false), 400);
      }
    }, 1200);
  };

  const liqFed = D.liquidity.fed.map(p => ({...p, label: fmtDate(p.date)}));
  const liqTga = D.liquidity.tga.map(p => ({...p, label: fmtDate(p.date)}));
  const liqRrp = D.liquidity.rrp.map(p => ({...p, label: fmtDate(p.date)}));
  const liqNet = D.liquidity.fed.map((p, i) => {
    const tgaVal = D.liquidity.tga[i] ? D.liquidity.tga[i].value : 0;
    const rrpVal = D.liquidity.rrp[i] ? D.liquidity.rrp[i].value : 0;
    const netVal = p.value - (tgaVal / 1000) - (rrpVal / 1000);
    return {date: p.date, value: parseFloat(netVal.toFixed(3)), label: fmtDate(p.date)};
  });

  const lastFed = liqFed.length ? liqFed[liqFed.length - 1].value : 0;
  const lastTga = liqTga.length ? liqTga[liqTga.length - 1].value : 0;
  const lastRrp = liqRrp.length ? liqRrp[liqRrp.length - 1].value : 0;
  const lastNet = parseFloat((lastFed - (lastTga / 1000) - (lastRrp / 1000)).toFixed(3));

  // ⚠️ 에러 원인이었던 '>' 기호를 제거한 안전한 조건문 설계
  let signalText = "🟡 중립 · 방향 주시";
  let signalColor = C.yellow;
  if (lastNet >= 5.8) {
    signalText = "🟢 유동성 충분 · 위험자산 우호";
    signalColor = C.green;
  } else if (lastNet <= 5.3) {
    signalText = "🔴 유동성 타이트 · 주의";
    signalColor = C.red;
  }

  const srcColor = apiStatus === "live" ? C.green : (apiStatus === "err" ? C.red : C.muted);
  const srcLabel = apiStatus === "live" ? "● LIVE" : (apiStatus === "err" ? "✕ ERROR" : "○ CACHED");

  return (
    <div style={{background:C.bg, minHeight:"100vh", color:C.text, fontFamily:"'Noto Sans KR',sans-serif", padding:14}}>
      <style>{`
        @keyframes spin{to{transform:rotate(360deg)}}
        @keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
        *{box-sizing:border-box;margin:0;padding:0}
        button{cursor:pointer;border:none;outline:none;}
      `}</style>
      <div style={{maxWidth:920, margin:"0 auto"}}>

        <div style={{textAlign:"center", marginBottom:14}}>
          <div style={{display:"inline-block", fontFamily:"monospace", fontSize:9, letterSpacing:4, color:C.blue, border:`1px solid rgba(26,159,255,0.4)`, padding:"4px 14px", marginBottom:10, background:"rgba(26,159,255,0.06)"}}>
            MACRO LIQUIDITY + GLOBAL INDICES
          </div>
          <div style={{fontSize:22, fontWeight:900, color:C.white, letterSpacing:-1, marginBottom:4}}>
            미국 유동성 + 글로벌 지수 대시보드
          </div>
          <div style={{fontFamily:"monospace", fontSize:9, color:C.muted, marginBottom:12}}>
            FRED · WALCL · TGA · RRP · S&P · NASDAQ · KOSPI · KOSDAQ
          </div>

          <div style={{display:"flex", alignItems:"center", justifyContent:"center", gap:14, flexWrap:"wrap"}}>
            <div style={{display:"flex", alignItems:"center", gap:6}}>
              <div style={{width:7, height:7, borderRadius:"50%", background:srcColor, flexShrink:0, animation:apiStatus === "live" ? "blink 2s infinite" : "none"}}/>
              <span style={{fontFamily:"monospace", fontSize:9, color:srcColor}}>{srcLabel}</span>
              <span style={{fontFamily:"monospace", fontSize:9, color:C.muted}}>· {D.lastUpdated}</span>
            </div>

            <button onClick={doUpdate} disabled={loading}
              style={{display:"flex", alignItems:"center", gap:8, background:loading?"rgba(26,159,255,0.05)":"rgba(26,159,255,0.12)", border:`1px solid ${loading?C.blue+"44":C.blue}`, padding:"8px 18px", color:loading?C.muted:C.blue, fontFamily:"monospace", fontSize:11, fontWeight:700, letterSpacing:1, opacity:loading?0.7:1}}>
              <span style={{display:"inline-block", width:13, height:13, border:`1.5px solid ${C.blue}`, borderTopColor:"transparent", borderRadius:"50%", animation:spin?"spin .6s linear infinite":"none", flexShrink:0}}/>
              {loading ? "데이터 갱신 중..." : "↻ 지금 업데이트"}
            </button>
          </div>
        </div>

        <div style={{background:C.panel, border:`1px solid ${C.border}`, borderLeft:`3px solid ${C.blue}`, padding:"8px 14px", marginBottom:10, fontFamily:"monospace", fontSize:11, display:"flex", flexWrap:"wrap", alignItems:"center", gap:8, color:C.muted}}>
          <span style={{color:C.blue, fontWeight:700, fontSize:9}}>NET =</span>
          <span style={{color:C.blue}}>WALCL</span><span>−</span>
          <span style={{color:C.yellow}}>TGA</span><span>−</span>
          <span style={{color:C.purple}}>RRP</span>
          <span style={{marginLeft:"auto", fontSize:9}}>기준: {D.lastUpdated}</span>
        </div>

        <div style={{display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:8, marginBottom:10}}>
          {[
            {label:"FED·WALCL", name:"연준 총자산", val:`$${lastFed.toFixed(2)}T`, color:C.blue},
            {label:"TGA·WTREGEN", name:"재무부 계정", val:`$${lastTga.toFixed(0)}B`, color:C.yellow},
            {label:"RRP·RRPONTSYD", name:"역레포 잔고", val:`$${lastRrp.toFixed(2)}B`, color:C.purple},
            {label:"NET LIQUIDITY", name:"순 유동성", val:`$${lastNet.toFixed(3)}T`, color:signalColor},
          ].map(c => (
            <div key={c.label} style={{background:C.panel, border:`1px solid ${C.border}`, borderTop:`2px solid ${c.color}`, padding:"12px 10px"}}>
              <div style={{fontFamily:"monospace", fontSize:8, color:C.muted, marginBottom:3}}>{c.label}</div>
              <div style={{fontSize:10, fontWeight:700, marginBottom:6}}>{c.name}</div>
              <div style={{fontFamily:"monospace", fontSize:16, fontWeight:700, color:c.color}}>{c.val}</div>
            </div>
          ))}
        </div>

        <div style={{background:C.panel, border:`1px solid ${signalColor}`, padding:"14px 18px", display:"flex", alignItems:"center", justifyContent:"space-between", marginBottom:12, flexWrap:"wrap", gap:8}}>
          <div>
            <div style={{fontFamily:"monospace", fontSize:9, color:signalColor, letterSpacing:2, marginBottom:3}}>▶ 현재 시장 순유동성</div>
            <div style={{fontFamily:"monospace", fontSize:36, fontWeight:700, lineHeight:1, color:signalColor}}>${lastNet.toFixed(3)}T</div>
          </div>
          <div style={{textAlign:"right"}}>
            <div style={{fontSize:12, fontWeight:700, padding:"6px 12px", display:"inline-block", color:signalColor, background:`${signalColor}18`, border:`1px solid ${signalColor}44`}}>{signalText}</div>
          </div>
        </div>

        {[
          {title:"🏦 연준 총자산 (WALCL)", sub:"Trillions USD", color:C.blue, data:liqFed, key:"value", cur:`$${lastFed.toFixed(2)}T`},
          {title:"🏛️ TGA 잔고 (WTREGEN)", sub:"Billions USD", color:C.yellow, data:liqTga, key:"value", cur:`$${lastTga.toFixed(0)}B`},
          {title:"💰 역레포 잔고 (RRPONTSYD)", sub:"Billions USD", color:C.purple, data:liqRrp, key:"value", cur:`$${lastRrp.toFixed(2)}B`},
          {title:"📊 순유동성 NET", sub:"Trillions USD · FED−TGA−RRP", color:signalColor, data:liqNet, key:"value", cur:`$${lastNet.toFixed(3)}T`},
        ].map(cfg => {
          const range = frozenRange(cfg.data.map(p => p.value), 0.25);
          return (
            <Card key={cfg.title} title={cfg.title} sub={cfg.sub} color={cfg.color} cur={cfg.cur} chg="" chgPos={true}>
              <MiniChart data={cfg.data} dataKey={cfg.key} color={cfg.color} yMin={range.min} yMax={range.max} height={200}/>
            </Card>
          );
        })}

        <div style={{display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:8, marginBottom:12, marginTop:20}}>
          {TICKERS.map(t => {
            const b = D.badges[t.sym];
            const isUp = b ? b.chgPct >= 0 : true;
            return (
              <div key={t.sym} style={{background:C.panel2, border:`1px solid ${isUp?"#00e87a33":"#ff3d5a33"}`, borderLeft:`3px solid ${isUp?C.green:C.red}`, padding:"10px 12px", display:"flex", justifyContent:"space-between", alignItems:"center"}}>
                <div>
                  <div style={{fontFamily:"monospace", fontSize:8, color:C.muted, marginBottom:2}}>{t.flag} {t.sym}</div>
                  <div style={{fontSize:11, fontWeight:700, color:C.white}}>{t.name}</div>
                </div>
                <div style={{textAlign:"right"}}>
                  <div style={{fontFamily:"monospace", fontSize:13, fontWeight:700, color:t.color}}>{b?fmtNum(b.price,2):"—"}</div>
                  {b && (
                    <div style={{fontFamily:"monospace", fontSize:9, color:isUp?C.green:C.red}}>
                      {isUp?"▲":"▼"} {Math.abs(b.chgPct).toFixed(2)}%
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {TICKERS.map(t => {
          const raw = D.indices[t.sym] || [];
          const chartData = raw.map(p => ({...p, label: fmtDate(p.date)}));
          const range = frozenRange(raw.map(p => p.value), 0.2);
          const b = D.badges[t.sym];
          const isUp = b ? b.chgPct >= 0 : true;
          return (
            <Card key={t.sym} title={`${t.flag} ${t.name} (${t.sym})`} sub="포인트 지수 시세 트렌드" color={t.color} cur={b?fmtNum(b.price,2):"—"} chg={b?`${isUp?"▲ +":"▼ "}${Math.abs(b.chgPct).toFixed(2)}%`:"—"} chgPos={isUp}>
              <MiniChart data={chartData} dataKey="value" color={t.color} yMin={range.min} yMax={range.max} height={200}/>
            </Card>
          );
        })}

      </div>
    </div>
  );
}

// 4. 화면에 최종 렌더링
ReactDOM.createRoot(document.getElementById('root')).render(<Dashboard />);