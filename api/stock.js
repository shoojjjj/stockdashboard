export default async function handler(req, res) {
  try {
    const symbols = '005930.KS,000660.KS,NVDA,^IXIC,^GSPC,^SOX';
    const response = await fetch(`https://query1.finance.yahoo.com/v7/finance/quote?symbols=${symbols}`);
    
    if (!response.ok) throw new Error('Yahoo API failed');
    
    const data = await response.json();
    const results = data.quoteResponse.result;

    // 데이터 안전하게 추출 (값이 없으면 0 반환)
    const getVal = (s) => results.find(r => r.symbol === s)?.regularMarketPrice || 0;
    const getChg = (s) => results.find(r => r.symbol === s)?.regularMarketChangePercent || 0;

    res.status(200).json({
      samsung: getVal('005930.KS'), samsungChg: getChg('005930.KS'),
      hynix: getVal('000660.KS'), hynixChg: getChg('000660.KS'),
      nvda: getVal('NVDA'), nvdaChg: getChg('NVDA'),
      nasdaq: getVal('^IXIC'), nasdaqChg: getChg('^IXIC'),
      sp500: getVal('^GSPC'), sp500Chg: getChg('^GSPC'),
      sox: getVal('^SOX'), soxChg: getChg('^SOX')
    });
  } catch (error) {
    console.error("API Error:", error);
    res.status(500).json({ error: "Data fetch failed" });
  }
}