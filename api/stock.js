export default async function handler(req, res) {
  try {
    // 1. 야후 파이낸스 API 호출 (필요한 심볼만 명확히 정의)
    const symbols = '005930.KS,000660.KS,NVDA,^IXIC,^GSPC,^SOX';
    const response = await fetch(`https://query1.finance.yahoo.com/v7/finance/quote?symbols=${symbols}`, {
      headers: { 'User-Agent': 'Mozilla/5.0' } // 서버 호출 시 차단 방지
    });
    
    if (!response.ok) throw new Error('API Response Error');
    
    const data = await response.json();
    const results = data.quoteResponse.result;

    // 2. 데이터 안전하게 추출하는 함수
    const getVal = (s) => results.find(r => r.symbol === s)?.regularMarketPrice || 0;
    const getChg = (s) => results.find(r => r.symbol === s)?.regularMarketChangePercent || 0;

    // 3. 결과 반환
    res.status(200).json({
      samsung: getVal('005930.KS'), samsungChg: getChg('005930.KS'),
      hynix: getVal('000660.KS'), hynixChg: getChg('000660.KS'),
      nvda: getVal('NVDA'), nvdaChg: getChg('NVDA'),
      nasdaq: getVal('^IXIC'), nasdaqChg: getChg('^IXIC'),
      sp500: getVal('^GSPC'), sp500Chg: getChg('^GSPC'),
      sox: getVal('^SOX'), soxChg: getChg('^SOX')
    });
  } catch (error) {
    // 에러 발생 시에도 클라이언트가 뻗지 않게 200으로 안전한 기본값 반환
    res.status(200).json({ samsung: 0, hynix: 0, nvda: 0, nasdaq: 0, sp500: 0, sox: 0 });
  }
}