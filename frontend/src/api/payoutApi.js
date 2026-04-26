const BASE_URL = process.env.REACT_APP_API_URL;

export const createPayout = async (amount) => {
  const res = await fetch(`${BASE_URL}/payouts/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Idempotency-Key": crypto.randomUUID(),
    },
    body: JSON.stringify({
      merchant_id: 1,
      amount_paise: amount,
    }),
  });
  return res.json();
};

export const getPayouts = async () => {
  try {
    const res = await fetch("http://localhost:8000/api/v1/payouts/");

    if (!res.ok) throw new Error("Failed");

    return res.json();
  } catch (err) {
    console.error("Payout fetch error:", err);
    return [];
  }
};

export const getBalance = async () => {
  try {
    const res = await fetch("http://localhost:8000/api/v1/balance/1/");

    if (!res.ok) throw new Error("Failed");

    const data = await res.json();

    return data.balance_paise;   // ✅ return NUMBER directly
  } catch (err) {
    console.error("Balance error:", err);
    return 0;
  }
};