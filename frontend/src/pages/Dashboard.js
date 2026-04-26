import { useEffect, useState } from "react";
import { createPayout, getPayouts, getBalance } from "../api/payoutApi";

export default function Dashboard() {
  const [balance, setBalance] = useState(0);
  const [payouts, setPayouts] = useState([]);
  const [amount, setAmount] = useState("");
  const [loading, setLoading] = useState(false);

  const loadData = async () => {
    setLoading(true);

    const balance = await getBalance();
    const payoutData = await getPayouts();

    setBalance(balance || 0);
    setPayouts(payoutData || []);

    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handlePayout = async () => {
    if (!amount) return;

    setLoading(true); // ✅ ADDED (fix eslint warning)

    try {
      const res = await createPayout(Number(amount));

      if (res?.error) {
        alert(res.error);
        setLoading(false);
        return;
      }

      setAmount("");
      await loadData();
    } catch (err) {
      console.error("Payout error:", err);
      alert("Something went wrong!");
    }

    setLoading(false); // ✅ ADDED
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">
          💸 Payout Dashboard
        </h1>

        <div className="bg-white shadow-md rounded-2xl p-6 mb-6">
          <p className="text-gray-500">Available Balance</p>
          <h2 className="text-3xl font-bold text-green-600 mt-2">
            ₹{(balance / 100).toFixed(2)}
          </h2>
        </div>

        <div className="bg-white shadow-md rounded-2xl p-6 mb-6">
          <h3 className="font-semibold mb-3">Request Payout</h3>

          <div className="flex gap-3">
            <input
              type="number"
              placeholder="Amount in paise"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="flex-1 border px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            />

            <button
              onClick={handlePayout}
              disabled={loading}
              className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {loading ? "Processing..." : "Withdraw"}
            </button>
          </div>
        </div>

        <div className="bg-white shadow-md rounded-2xl p-6">
          <h3 className="font-semibold mb-3">Payout History</h3>

          <div className="space-y-2">
            {payouts.length === 0 && (
              <p className="text-gray-400">No payouts yet</p>
            )}

            {payouts.map((p) => (
              <div
                key={p.id}
                className="flex justify-between items-center border p-3 rounded-lg"
              >
                <span className="font-medium">
                  ₹{(p.amount_paise || 0) / 100}
                </span>

                <span
                  className={`px-3 py-1 rounded-full text-sm ${
                    p.status === "completed"
                      ? "bg-green-100 text-green-700"
                      : p.status === "failed"
                      ? "bg-red-100 text-red-700"
                      : "bg-yellow-100 text-yellow-700"
                  }`}
                >
                  {p.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}