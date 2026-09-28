import { useState } from "react";
import { api } from "../api/client";
import type { OrderDetail } from "../api/types";

export function TrackOrderPage({ go }: { go: (page: string) => void }) {
  const [orderId, setOrderId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [order, setOrder] = useState<OrderDetail | null>(null);

  const handleTrack = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!orderId.trim()) return;
    setLoading(true);
    setError("");
    setOrder(null);

    try {
      const cleanId = orderId.trim().toUpperCase();
      const res = await api.getOrderDetail(cleanId);
      setOrder(res.order);
    } catch (err: any) {
      setError(err.message || "Order not found. Please verify your order ID.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="track-order-page">
      <div className="page-title">
        <div>
          <h1>Track Your Order</h1>
          <p>Enter your BoostX Order ID (e.g. BX-ORD-102948) to see live progress.</p>
        </div>
      </div>

      <section className="card">
        <form onSubmit={handleTrack} className="filters">
          <div className="search big" style={{ flex: 1 }}>
            <input
              type="text"
              placeholder="Enter Order ID (e.g. BX-ORD-8F9A1B2C)..."
              value={orderId}
              onChange={(e) => setOrderId(e.target.value)}
            />
          </div>
          <button type="submit" className="btn primary" disabled={loading || !orderId.trim()}>
            {loading ? "Searching..." : "Track Order"}
          </button>
        </form>
        {error && <div className="payment-warning" style={{ marginTop: "1rem" }}><strong>{error}</strong></div>}
      </section>

      {order && (
        <div style={{ marginTop: "1.5rem" }}>
          <section className="card tracking">
            <div className="card-head">
              <div>
                <span className="eyebrow">Delivery progress</span>
                <h2>{order.quantity - (order.remains ?? order.quantity)} of {order.quantity.toLocaleString()} delivered</h2>
              </div>
              <strong>{order.progress_percent}%</strong>
            </div>
            <div className="progress">
              <span style={{ width: `${order.progress_percent}%` }} />
            </div>
            <div className="tracking-labels">
              <span>Start count: {order.start_count ?? 0}</span>
              <span>Status: <span className={`status ${order.status.toLowerCase()}`}>{order.status}</span></span>
              <span>{order.remains ?? order.quantity} remaining</span>
            </div>
          </section>

          <div className="details-grid" style={{ marginTop: "1.5rem" }}>
            <section className="card">
              <h2>Order details</h2>
              <dl className="detail-list">
                <div><dt>Order ID</dt><dd><strong>{order.public_order_id}</strong></dd></div>
                <div><dt>Platform</dt><dd>{order.platform}</dd></div>
                <div><dt>Service</dt><dd>{order.service_name}</dd></div>
                <div><dt>Target</dt><dd>{order.target}</dd></div>
                <div><dt>Quantity</dt><dd>{order.quantity.toLocaleString()}</dd></div>
                <div><dt>Price</dt><dd>GHS {order.charge_ghs}</dd></div>
                <div><dt>Date Placed</dt><dd>{new Date(order.created_at).toLocaleString()}</dd></div>
              </dl>
            </section>

            {order.events && order.events.length > 0 && (
              <section className="card">
                <h2>Event History</h2>
                <div className="timeline">
                  {order.events.map((ev, i) => (
                    <div className="done" key={ev.id || i}>
                      <div>
                        <strong>{ev.event_type}</strong>
                        <p style={{ margin: "2px 0 0", fontSize: "0.85rem", opacity: 0.8 }}>{ev.description}</p>
                        <small>{new Date(ev.created_at).toLocaleString()}</small>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
