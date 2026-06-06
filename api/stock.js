// api/stock.js
export default async function handler(req, res) {
  try {
    const symbols = '005930.KS,000660.KS,NVDA,^IXIC,^GSPC,^SOX';
    const response = await fetch(`https://query1.finance.yahoo.com/v7/finance/quote?symbols=${symbols}`);
    const data = await response.json();
    const q = data.quoteResponse.result;

    const map = (s) => q.find(x => x.symbol === s) || {};
    
    res.status(200).json({
      samsung: map('005930.KS').regularMarketPrice, samsungChg: map('005930.KS').regularMarketChangePercent,
      hynix: map('000660.KS').regularMarketPrice, hynixChg: map('000660.KS').regularMarketChangePercent,
      nvda: map('NVDA').regularMarketPrice, nvdaChg: map('NVDA').regularMarketChangePercent,
      nasdaq: map('^IXIC').regularMarketPrice, nasdaqChg: map('^IXIC').regularMarketChangePercent
      // 필요 시 sp500, sox 등 추가 매핑
    });
  } catch (e) {
    res.status(500).json({ error: "Fail" });
  }
}