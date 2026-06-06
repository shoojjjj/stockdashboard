// api/stock.js
export default async function handler(req, res) {
  try {
    // 여기서 각 사이트의 데이터를 수집 (현재는 예시 구조)
    const data = {
      nasdaq: 25700, nasdaqChg: -4.10,
      nasdaqFut: 29026.50, nasdaqFutChg: -4.70,
      sp500: 7383.74, sp500Chg: -2.60,
      sox: 12220.76, soxChg: -10.20,
      kospiFut: 341.20, kospiFutChg: -8.00,
      nvda: 124.50, nvdaChg: -6.20,
      samsung: 74200, samsungChg: 1.45,
      hynix: 188300, hynixChg: 2.81,
      vix: 21.51, vixChg: 39.6,
      wti: 82.50, wtiChg: 1.84,
      usdkrw: 1559.80, usdkrwChg: 2.0,
      fed: 6.682, tga: 0.801, rrp: 0.146, mmf: 6.54
    };
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: "데이터 수집 실패" });
  }
}