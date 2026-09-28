import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { AdminOverviewStats, AdminAuditLogItem } from "../api/types";

export function AdminDashboard({ go }: { go: (page: string) => void }) {
  const [overview, setOverview] = useState<AdminOverviewStats | null>(null);

  useEffect(() => {
    api.getAdminOverview().then(setOverview).catch(() => {});
  }, []);

  return (
    <div className="admin-page">
      <div className="page-title">
        <div>
          <h1>Admin Overview</h1>
          <p>Live platform performance and operational health.</p>
        </div>
      </div>

      <div className="stats admin-stats">
        {[
          ["24h Revenue", `GHS ${overview?.revenue_24h_ghs || "0.00"}`],
          ["Active Orders", (overview?.active_orders || 0).toString()],
          ["Pending Payment Reviews", (overview?.pending_payment_reviews || 0).toString()],
          ["Total Registered Users", (overview?.total_users || 0).toString()],
          ["Failed Orders", (overview?.failed_orders || 0).toString()],
          ["Total System Orders", (overview?.total_orders || 0).toString()],
          ["Provider Balance", overview?.provider_balance || "Loading..."]
        ].map(([label, val]) => (
          <section className="card stat" key={label}>
            <div className="stat-head"><span>{label}</span></div>
            <strong>{val}</strong>
            <small>Updated live</small>
          </section>
        ))}
      </div>

      <div style={{ marginTop: "1.5rem" }}>
        <section className="card">
          <h2>Quick Actions</h2>
          <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginTop: "1rem" }}>
            <button className="btn primary" onClick={() => go("admin-payments")}>Review Payments ({overview?.pending_payment_reviews || 0})</button>
            <button className="btn secondary" onClick={() => go("admin-orders")}>Manage Orders ({overview?.active_orders || 0} active)</button>
            <button className="btn secondary" onClick={() => go("admin-services")}>Service Catalog</button>
            <button className="btn secondary" onClick={() => go("admin-audit")}>Audit Logs</button>
          </div>
        </section>
      </div>
    </div>
  );
}

export function AdminPayments({ go }: { go: (page: string) => void }) {
  const [payments, setPayments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getAdminPayments().then(res => {
      setPayments(res.payments);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <div className="admin-page">
      <div className="page-title">
        <div>
          <h1>Payment Reviews</h1>
          <p>Review AI-verified payments and resolve exceptions.</p>
        </div>
      </div>

      <section className="card">
        {loading ? <p>Loading payments...</p> : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Payment ID</th>
                  <th>Amount</th>
                  <th>Network</th>
                  <th>Status</th>
                  <th>Reference</th>
                  <th>Created</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {payments.map(p => (
                  <tr key={p.payment_id}>
                    <td><strong>{p.payment_id}</strong></td>
                    <td>GHS {p.amount_ghs}</td>
                    <td>{p.network}</td>
                    <td><span className={`status ${p.status.toLowerCase()}`}>{p.status}</span></td>
                    <td>{p.reference || "N/A"}</td>
                    <td>{new Date(p.created_at).toLocaleString()}</td>
                    <td>
                      <button className="btn secondary" onClick={() => go(`admin-payment-review?id=${p.payment_id}`)}>
                        Review
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export function AdminPaymentReview({ go }: { go: (page: string) => void }) {
  const [payment, setPayment] = useState<any | null>(null);
  const [reference, setReference] = useState("");
  const [reason, setReason] = useState("");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    const params = new URLSearchParams(location.hash.split("?")[1] || "");
    const id = params.get("id");
    if (id) {
      api.getAdminPayments({ search: id }).then(res => {
        if (res.payments.length > 0) setPayment(res.payments[0]);
      }).catch(() => {});
    }
  }, []);

  const handleApprove = async () => {
    if (!payment) return;
    try {
      const res = await api.adminVerifyPayment(payment.payment_id, reference || undefined);
      setMsg(res.message);
    } catch (err: any) {
      setMsg(err.message || "Failed to approve payment");
    }
  };

  const handleReject = async () => {
    if (!payment) return;
    try {
      const res = await api.adminRejectPayment(payment.payment_id, reason || undefined);
      setMsg(res.message);
    } catch (err: any) {
      setMsg(err.message || "Failed to reject payment");
    }
  };

  if (!payment) return <section className="card"><p>Loading payment details...</p></section>;

  return (
    <div className="admin-page">
      <button className="back-link" onClick={() => go("admin-payments")}>← Back to payments</button>
      <div className="page-title">
        <div>
          <h1>Review Payment {payment.payment_id}</h1>
          <p>Amount: GHS {payment.amount_ghs} · Network: {payment.network}</p>
        </div>
        <span className={`status ${payment.status.toLowerCase()}`}>{payment.status}</span>
      </div>

      <div className="payment-review-grid">
        <section className="card">
          <h2>Payment Details</h2>
          <dl className="detail-list">
            <div><dt>Payment ID</dt><dd>{payment.payment_id}</dd></div>
            <div><dt>Amount</dt><dd>GHS {payment.amount_ghs}</dd></div>
            <div><dt>Detected Amount</dt><dd>{payment.detected_amount_ghs ? `GHS ${payment.detected_amount_ghs}` : "N/A"}</dd></div>
            <div><dt>Network</dt><dd>{payment.network}</dd></div>
            <div><dt>Reference</dt><dd>{payment.reference || "N/A"}</dd></div>
            <div><dt>Status</dt><dd>{payment.status}</dd></div>
          </dl>
        </section>

        <section className="card">
          <h2>Admin Decision</h2>
          <label className="field">
            <span>Override Reference (optional)</span>
            <input value={reference} onChange={(e) => setReference(e.target.value)} placeholder="MANUAL-REF-123" />
          </label>
          <label className="field">
            <span>Rejection Reason (optional)</span>
            <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder="Unclear screenshot" />
          </label>
          {msg && <div className="payment-warning" style={{ margin: "1rem 0" }}><strong>{msg}</strong></div>}
          <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
            <button className="btn primary" onClick={handleApprove}>Approve & Credit</button>
            <button className="btn secondary" onClick={handleReject}>Reject Payment</button>
          </div>
        </section>
      </div>
    </div>
  );
}

export function AdminOrders() {
  const [orders, setOrders] = useState<any[]>([]);

  useEffect(() => {
    api.getAdminOrders().then(res => setOrders(res.orders)).catch(() => {});
  }, []);

  const handleAction = async (publicId: string, action: string) => {
    try {
      await api.adminOrderAction(publicId, action);
      const res = await api.getAdminOrders();
      setOrders(res.orders);
    } catch (err: any) {
      alert(err.message || "Action failed");
    }
  };

  return (
    <div className="admin-page">
      <div className="page-title">
        <div>
          <h1>Order Management</h1>
          <p>Track fulfillment status and resolve order issues.</p>
        </div>
      </div>

      <section className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Platform</th>
                <th>Service</th>
                <th>Target</th>
                <th>Status</th>
                <th>Attention</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {orders.map(o => (
                <tr key={o.public_order_id}>
                  <td><strong>{o.public_order_id}</strong></td>
                  <td>{o.platform}</td>
                  <td>{o.service_name}</td>
                  <td>{o.target}</td>
                  <td><span className={`status ${o.status.toLowerCase()}`}>{o.status}</span></td>
                  <td>{o.needs_attention ? <span className="status rejected">Needs Attention</span> : "Normal"}</td>
                  <td>
                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      {o.needs_attention && <button className="btn secondary" onClick={() => handleAction(o.public_order_id, "clear-attention")}>Clear Flag</button>}
                      <button className="btn secondary" onClick={() => handleAction(o.public_order_id, "mark-submitted")}>Mark Submitted</button>
                      <button className="btn ghost" onClick={() => handleAction(o.public_order_id, "cancel")}>Cancel</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export function AdminServices() {
  const [services, setServices] = useState<any[]>([]);

  useEffect(() => {
    api.getAdminServices().then(res => setServices(res.services)).catch(() => {});
  }, []);

  const toggleService = async (id: number, currentEnabled: boolean) => {
    try {
      await api.updateAdminService(id, { enabled: !currentEnabled });
      const res = await api.getAdminServices();
      setServices(res.services);
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleSync = async () => {
    try {
      await api.syncAdminServices();
      const res = await api.getAdminServices();
      setServices(res.services);
      alert("Services synchronized with provider.");
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="admin-page">
      <div className="page-title">
        <div>
          <h1>Services Catalog</h1>
          <p>Control service availability and provider rates.</p>
        </div>
        <button className="btn primary" onClick={handleSync}>Sync Catalog with Provider</button>
      </div>

      <section className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Platform</th>
                <th>Service Name</th>
                <th>Rate (USD / 1k)</th>
                <th>Min/Max</th>
                <th>Refill</th>
                <th>Enabled</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {services.map(s => (
                <tr key={s.id}>
                  <td>{s.id}</td>
                  <td>{s.platform}</td>
                  <td><strong>{s.name}</strong></td>
                  <td>${s.rate_usd_per_1000}</td>
                  <td>{s.min_qty} / {s.max_qty.toLocaleString()}</td>
                  <td>{s.refill_available ? "Yes" : "No"}</td>
                  <td><span className={`status ${s.enabled ? "completed" : "cancelled"}`}>{s.enabled ? "Active" : "Disabled"}</span></td>
                  <td>
                    <button className="btn secondary" onClick={() => toggleService(s.id, s.enabled)}>
                      {s.enabled ? "Disable" : "Enable"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export function AdminPlatforms() {
  const [platforms, setPlatforms] = useState<any[]>([]);

  useEffect(() => {
    api.getAdminPlatforms().then(res => setPlatforms(res.platforms)).catch(() => {});
  }, []);

  const togglePlatform = async (id: number, currentActive: boolean) => {
    try {
      await api.updateAdminPlatform(id, !currentActive);
      const res = await api.getAdminPlatforms();
      setPlatforms(res.platforms);
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="admin-page">
      <div className="page-title">
        <div>
          <h1>Platforms</h1>
          <p>Manage active social platforms on BoostX.</p>
        </div>
      </div>

      <div className="platform-admin-grid">
        {platforms.map(p => (
          <section className="card" key={p.id}>
            <h2>{p.name}</h2>
            <p>Status: <span className={`status ${p.active ? "completed" : "cancelled"}`}>{p.active ? "Active" : "Disabled"}</span></p>
            <button className="btn secondary" style={{ marginTop: "1rem" }} onClick={() => togglePlatform(p.id, p.active)}>
              {p.active ? "Disable Platform" : "Enable Platform"}
            </button>
          </section>
        ))}
      </div>
    </div>
  );
}

export function AdminConfigPage({ type }: { type: string }) {
  const [auditLogs, setAuditLogs] = useState<AdminAuditLogItem[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [rate, setRate] = useState("10.70");
  const [markup, setMarkup] = useState("5.00");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    if (type === "audit") {
      api.getAdminAuditLogs().then(res => setAuditLogs(res.audit_logs)).catch(() => {});
    } else if (type === "health") {
      api.getAdminHealth().then(setHealth).catch(() => {});
    } else if (type === "pricing") {
      api.getAdminPricing().then(res => {
        setRate(res.usd_to_ghs_rate);
        setMarkup(res.flat_markup_ghs);
      }).catch(() => {});
    }
  }, [type]);

  const handleUpdatePricing = async () => {
    try {
      const res = await api.updateAdminPricing(rate, markup);
      setMsg(res.message);
    } catch (err: any) {
      setMsg(err.message);
    }
  };

  if (type === "audit") {
    return (
      <div className="admin-page">
        <div className="page-title">
          <div>
            <h1>Audit Logs</h1>
            <p>Immutable record of administrator actions.</p>
          </div>
        </div>

        <section className="card">
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Admin ID</th>
                  <th>Action</th>
                  <th>Target Type</th>
                  <th>Target ID</th>
                  <th>Old Value</th>
                  <th>New Value</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map(l => (
                  <tr key={l.id}>
                    <td>Admin #{l.admin_id}</td>
                    <td><strong>{l.action}</strong></td>
                    <td>{l.target_type}</td>
                    <td>{l.target_id}</td>
                    <td>{l.old_value || "—"}</td>
                    <td>{l.new_value || "—"}</td>
                    <td>{new Date(l.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    );
  }

  if (type === "health") {
    return (
      <div className="admin-page">
        <div className="page-title">
          <div>
            <h1>System Health</h1>
            <p>Live status of database and provider services.</p>
          </div>
        </div>

        <section className="card">
          <h2>Overall Status: {health?.status || "Checking..."}</h2>
          <dl className="detail-list" style={{ marginTop: "1rem" }}>
            <div><dt>Database</dt><dd>{health?.database?.status === "ok" ? "OK" : "ERROR"}</dd></div>
            <div><dt>Provider API</dt><dd>{health?.provider?.status === "ok" ? "OK" : "ERROR"}</dd></div>
            <div><dt>Timestamp</dt><dd>{health?.timestamp ? new Date(health.timestamp).toLocaleString() : "N/A"}</dd></div>
          </dl>
        </section>
      </div>
    );
  }

  if (type === "pricing") {
    return (
      <div className="admin-page">
        <div className="page-title">
          <div>
            <h1>Pricing Configuration</h1>
            <p>Set exchange rates and flat markups for customer prices.</p>
          </div>
        </div>

        <section className="card">
          <label className="field">
            <span>USD to GHS Exchange Rate</span>
            <input value={rate} onChange={(e) => setRate(e.target.value)} placeholder="10.70" />
          </label>
          <label className="field">
            <span>Flat Processing Fee Markup (GHS)</span>
            <input value={markup} onChange={(e) => setMarkup(e.target.value)} placeholder="5.00" />
          </label>
          {msg && <div className="payment-warning" style={{ margin: "1rem 0" }}><strong>{msg}</strong></div>}
          <button className="btn primary" onClick={handleUpdatePricing} style={{ marginTop: "1rem" }}>
            Save Pricing Settings
          </button>
        </section>
      </div>
    );
  }

  return (
    <div className="admin-page">
      <div className="page-title">
        <div>
          <h1>Admin Settings ({type})</h1>
          <p>System configuration panel.</p>
        </div>
      </div>
      <section className="card">
        <p>Admin configuration page for {type}.</p>
      </section>
    </div>
  );
}
