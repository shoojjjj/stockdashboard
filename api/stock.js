// api/stock.js
export default async function handler(req, res) {
  try {
    // 실제 실시간 데이터를 가져오는 로직 (예시)
    // 보안상 브라우저에서 직접 불가능한 외부 API 호출을 여기서 처리합니다.
    const response = await fetch('https://query1.finance.yahoo.com/v8/finance/chart/005930.KS');
    const data = await response.json();
    
    // 삼성전자 가격 예시 추출
    const price = data.chart.result[0].meta.regularMarketPrice;
    
    res.status(200).json({ samsung: price, hynix: 184500 }); // 하이닉스는 예시값
  } catch (error) {
    res.status(500).json({ error: '데이터를 가져올 수 없습니다.' });
  }
}