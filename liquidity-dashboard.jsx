// 1. 브라우저용 리액트 및 차트 부품 지정
const { useState, useEffect, useRef } = React;
const { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } = Recharts;

// 2. 가짜 데이터 (API 연동 전 테스트용)
const mockData = [
  { date: '2024-01', netLiquidity: 6100, sp500: 4800, ndx: 16800, kospi: 2500, wti: 72 },
  { date: '2024-02', netLiquidity: 6250, sp500: 5000, ndx: 18000, kospi: 2650, wti: 78 },
  { date: '2024-03', netLiquidity: 6180, sp500: 5200, ndx: 18200, kospi: 2750, wti: 83 },
  { date: '2024-04', netLiquidity: 6300, sp500: 5100, ndx: 17700, kospi: 2600, wti: 81 },
  { date: '2024-05', netLiquidity: 6420, sp500: 5300, ndx: 18800, kospi: 2680, wti: 77 },
];

// 3. 메인 대시보드 컴포넌트
function Dashboard() {
  const [data, setData] = useState(mockData);

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* 상단 헤더 */}
      <div className="flex justify-between items-center border-b border-gray-800 pb-4">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-blue-400">Macro Liquidity Dashboard</h1>
          <p className="text-sm text-gray-400 mt-1">미국 순유동성 지표 및 글로벌 자산 실시간 모니터링</p>
        </div>
        <div className="text-right">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/20">
            ● 시스템 정상 작동중
          </span>
        </div>
      </div>

      {/* 요약 카드 섹션 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#0b1520] p-4 rounded-xl border border-gray-800">
          <p className="text-xs text-gray-400 font-bold">미국 순유동성 (Net Liquidity)</p>
          <p className="text-2xl font-black mt-1 text-blue-400">$ 6.42 T</p>
        </div>
        <div className="bg-[#0b1520] p-4 rounded-xl border border-gray-800">
          <p className="text-xs text-gray-400 font-bold">S&P 500</p>
          <p className="text-2xl font-black mt-1 text-white">5,300.25</p>
        </div>
        <div className="bg-[#0b1520] p-4 rounded-xl border border-gray-800">
          <p className="text-xs text-gray-400 font-bold">NASDAQ 100</p>
          <p className="text-2xl font-black mt-1 text-white">18,800.50</p>
        </div>
        <div className="bg-[#0b1520] p-4 rounded-xl border border-gray-800">
          <p className="text-xs text-gray-400 font-bold">KOSPI</p>
          <p className="text-2xl font-black mt-1 text-orange-400">2,680.10</p>
        </div>
      </div>

      {/* 메인 차트 */}
      <div className="bg-[#0b1520] p-6 rounded-2xl border border-gray-800">
        <h3 className="text-lg font-bold mb-4 text-gray-200">순유동성 vs 주요 지수 트렌드</h3>
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <XAxis dataKey="date" stroke="#4b5563" tick={{ fill: '#9ca3af', fontSize: 12 }} />
              <YAxis stroke="#4b5563" tick={{ fill: '#9ca3af', fontSize: 12 }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px' }}
                labelStyle={{ color: '#9ca3af', fontWeight: 'bold' }}
              />
              <Legend dy={10} />
              <Line type="monotone" dataKey="netLiquidity" name="순유동성($)" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="sp500" name="S&P 500" stroke="#10b981" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="ndx" name="NASDAQ" stroke="#8b5cf6" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

// 4. 화면에 렌더링
ReactDOM.createRoot(document.getElementById('root')).render(<Dashboard />);
