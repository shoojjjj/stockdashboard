export default async function handler(req, res) {
  try {
    // 야후 파이낸스에서 실제 데이터 호출
    // 여러 종목을 한 번에 가져오는 방식
    const symbols = '005930.KS,000660.KS,NVDA'; 
    const response = await fetch(`https://query1.finance.yahoo.com/v7/finance/quote?symbols=${symbols}`);
    const data = await response.json();
    const results = data.quoteResponse.result;

    // 데이터 매핑
    const getPrice = (symbol) => results.find(r => r.symbol === symbol)?.regularMarketPrice || 0;
    const getChange = (symbol) => results.find(r => r.symbol === symbol)?.regularMarketChangePercent || 0;

    res.status(200).json({
      samsung: getPrice('005930.KS'), samsungChg: getChange('005930.KS'),
      hynix: getPrice('000660.KS'), hynixChg: getChange('000660.KS'),
      nvda: getPrice('NVDA'), nvdaChg: getChange('NVDA'),
      nasdaq: 0, nasdaqChg: 0 // (나스닥 등도 위와 같은 방식으로 추가 가능)
    });
  } catch (error) {
    res.status(500).json({ error: "API 연동 실패" });
  }
}