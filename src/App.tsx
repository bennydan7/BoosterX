import { useEffect, useMemo, useState, type ReactNode } from "react";
import logo from "./imports/boosterx-logo-rocket.svg";

type IconName =
  | "home" | "plus" | "orders" | "services" | "wallet" | "transactions"
  | "support" | "user" | "settings" | "search" | "bell" | "sun"
  | "moon" | "menu" | "close" | "arrow" | "copy" | "logout" | "check"
  | "clock" | "eye" | "users" | "chart" | "card" | "shield";

const paths: Record<IconName, ReactNode> = {
  home: <><path d="m3 10 9-7 9 7"/><path d="M5 9v11h14V9M9 20v-6h6v6"/></>,
  plus: <><path d="M12 5v14M5 12h14"/></>,
  orders: <><rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></>,
  services: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
  wallet: <><path d="M4 6h14a2 2 0 0 1 2 2v11H4a2 2 0 0 1-2-2V6.5A2.5 2.5 0 0 1 4.5 4H17"/><path d="M15 12h5v4h-5a2 2 0 0 1 0-4Z"/></>,
  transactions: <><path d="m7 7 3-3 3 3M10 4v12M17 17l-3 3-3-3M14 20V8"/></>,
  support: <><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.6 2.6 0 1 1 4.2 2c-1 .7-1.7 1.2-1.7 2.5M12 17h.01"/></>,
  user: <><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></>,
  settings: <><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3A1.7 1.7 0 0 0 10 3V2.8h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1Z"/></>,
  search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
  bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4"/></>,
  sun: <><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></>,
  moon: <path d="M20 15.2A8 8 0 0 1 8.8 4a8 8 0 1 0 11.2 11.2Z"/>,
  menu: <path d="M4 6h16M4 12h16M4 18h16"/>,
  close: <path d="m6 6 12 12M18 6 6 18"/>,
  arrow: <path d="m9 18 6-6-6-6"/>,
  copy: <><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></>,
  logout: <><path d="M10 17l5-5-5-5M15 12H3M15 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4"/></>,
  check: <path d="m5 12 4 4L19 6"/>,
  clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
  eye: <><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="2.5"/></>,
  users: <><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/></>,
  chart: <><path d="M4 19V9M10 19V5M16 19v-7M22 19V2"/><path d="M2 19h22"/></>,
  card: <><rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/></>,
  shield: <><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/></>,
};

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  return <svg className="icon" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}

function SocialIcon({ platform }: { platform: string }) {
  const filename = platform.toLowerCase();
  return <span className="platform-mark"><img src={`/social/${filename}.svg`} alt="" /></span>;
}

function Button({ children, variant = "primary", icon, onClick, type = "button", disabled, full }: { children: ReactNode; variant?: "primary" | "secondary" | "ghost"; icon?: IconName; onClick?: () => void; type?: "button" | "submit"; disabled?: boolean; full?: boolean }) {
  return <button type={type} disabled={disabled} onClick={onClick} className={`btn ${variant} ${full ? "full" : ""}`}>{icon && <Icon name={icon} />}{children}</button>;
}

function Field({ label, placeholder, value, type = "text", onChange }: { label?: string; placeholder?: string; value?: string; type?: string; onChange?: (value: string) => void }) {
  return <label className="field">{label && <span>{label}</span>}<input type={type} placeholder={placeholder} value={value} onChange={(e) => onChange?.(e.target.value)} /></label>;
}

function SelectField({ label, value, children, onChange }: { label?: string; value?: string; children: ReactNode; onChange?: (value: string) => void }) {
  return <label className="field">{label && <span>{label}</span>}<select value={value} onChange={(e) => onChange?.(e.target.value)}>{children}</select></label>;
}

function PageTitle({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return <div className="page-title"><div><h1>{title}</h1>{description && <p>{description}</p>}</div>{action}</div>;
}

function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`card ${className}`}>{children}</section>;
}

const orders = [
  { id: "#BX10482", platform: "Instagram", service: "Followers", quantity: "2,500", price: "GHS 55.00", status: "Completed", date: "26 Sep 2026" },
  { id: "#BX10481", platform: "TikTok", service: "Video views", quantity: "10,000", price: "GHS 38.00", status: "Processing", date: "26 Sep 2026" },
  { id: "#BX10477", platform: "X", service: "Post likes", quantity: "1,000", price: "GHS 22.00", status: "Pending", date: "25 Sep 2026" },
  { id: "#BX10465", platform: "Facebook", service: "Page followers", quantity: "5,000", price: "GHS 84.00", status: "Completed", date: "24 Sep 2026" },
  { id: "#BX10454", platform: "Telegram", service: "Channel members", quantity: "1,500", price: "GHS 42.00", status: "Cancelled", date: "22 Sep 2026" },
];

const navGroups = [
  { label: "Main", links: [["dashboard", "Dashboard", "home"], ["new-order", "New Order", "plus"], ["orders", "My Orders", "orders"], ["services", "Services", "services"]] },
  { label: "Finance", links: [["wallet", "Wallet", "wallet"], ["transactions", "Transactions", "transactions"], ["payment", "Payment History", "card"]] },
  { label: "Help", links: [["support", "Support", "support"]] },
  { label: "Account", links: [["profile", "Profile", "user"], ["settings", "Settings", "settings"]] },
] as const;

function Status({ children }: { children: ReactNode }) { return <span className={`status ${String(children).toLowerCase()}`}>{children}</span>; }

function OrderTable({ onView }: { onView: (id: string) => void }) {
  return <div className="table-wrap"><table><thead><tr><th>Order ID</th><th>Platform</th><th>Service</th><th>Quantity</th><th>Price</th><th>Status</th><th>Date</th><th></th></tr></thead><tbody>
    {orders.map((order) => <tr key={order.id}><td><strong>{order.id}</strong></td><td>{order.platform}</td><td>{order.service}</td><td>{order.quantity}</td><td>{order.price}</td><td><Status>{order.status}</Status></td><td>{order.date}</td><td><button className="icon-btn" onClick={() => onView(order.id)} aria-label={`View ${order.id}`}><Icon name="arrow" /></button></td></tr>)}
  </tbody></table></div>;
}

function Dashboard({ go }: { go: (page: string) => void }) {
  const stats = [
    ["Total Orders", "184", "+12 this month", "orders"],
    ["Completed Orders", "156", "84.8% completion rate", "check"],
    ["Pending Orders", "8", "3 need attention", "clock"],
    ["Wallet Balance", "GHS 250.00", "Available to spend", "wallet"],
  ] as const;
  return <><PageTitle title="Good morning, Joseph" description="Manage your orders and social media growth from one place." action={<Button icon="plus" onClick={() => go("new-order")}>Create New Order</Button>} />
    <div className="stats">{stats.map(([label, value, note, icon]) => <Card className="stat" key={label}><div className="stat-head"><span>{label}</span><span className="icon-tile"><Icon name={icon} /></span></div><strong>{value}</strong><small>{note}</small></Card>)}</div>
    <div className="dashboard-grid">
      <Card className="chart-card"><div className="card-head"><div><span className="eyebrow">Order activity</span><h2>Growth overview</h2></div><div className="segmented"><button>7D</button><button className="active">30D</button><button>3M</button></div></div>
        <div className="chart-legend"><span><i className="dot primary"/>Completed 156</span><span><i className="dot secondary"/>Placed 184</span></div>
        <div className="chart"><svg viewBox="0 0 700 230" preserveAspectRatio="none"><g className="grid"><path d="M0 20H700M0 72H700M0 124H700M0 176H700M0 228H700"/></g><path className="line-secondary" d="M0 190 C70 160 90 180 150 145 S250 125 300 145 S390 70 450 105 S540 40 600 70 S660 24 700 35"/><path className="line-primary" d="M0 208 C55 195 105 155 150 175 S250 100 310 120 S380 92 440 76 S530 82 590 42 S660 58 700 18"/></svg><div className="x-axis"><span>1 Sep</span><span>8 Sep</span><span>15 Sep</span><span>22 Sep</span><span>30 Sep</span></div></div>
      </Card>
      <Card className="quick-card"><span className="eyebrow">Quick order</span><h2>Start growing today</h2><p>Choose a platform and launch a new campaign in minutes.</p>
        <div className="platform-list">{["Instagram", "TikTok", "Facebook", "X", "Telegram"].map((p, i) => <button onClick={() => go("new-order")} key={p}><SocialIcon platform={p}/><span>{p}<small>{["24 services", "18 services", "16 services", "9 services", "11 services"][i]}</small></span><Icon name="arrow" /></button>)}</div>
      </Card>
    </div>
    <Card><div className="card-head"><div><span className="eyebrow">Latest activity</span><h2>Recent orders</h2></div><Button variant="secondary" onClick={() => go("orders")}>View all orders</Button></div><OrderTable onView={() => go("order-details")} /></Card>
  </>;
}

function NewOrder({ go }: { go: (page: string) => void }) {
  const [platform, setPlatform] = useState("Instagram");
  const [service, setService] = useState("Followers");
  const [quantity, setQuantity] = useState("1000");
  const [placed, setPlaced] = useState(false);
  const total = ((Number(quantity || 0) / 1000) * 20 + 5).toFixed(2);
  return <><PageTitle title="Create New Order" description="Launch a new campaign in a few simple steps." />
    <div className="steps">{["Platform", "Service", "Details", "Review & pay"].map((s, i) => <div className={i === 0 ? "active" : ""} key={s}><span>{i + 1}</span>{s}</div>)}</div>
    <div className="form-layout">
      <Card><div className="form-section"><div className="number">01</div><div><h2>Select a platform</h2><p>Choose where you want to grow your audience.</p></div></div>
        <div className="platform-grid">{["Instagram", "TikTok", "Facebook", "X", "Telegram"].map((p) => <button className={platform === p ? "selected" : ""} onClick={() => setPlatform(p)} key={p}><SocialIcon platform={p}/>{p}{platform === p && <Icon name="check" />}</button>)}</div>
        <hr/>
        <div className="form-section"><div className="number">02</div><div><h2>Order details</h2><p>Tell us exactly what you need.</p></div></div>
        <div className="fields-grid"><SelectField label="Service" value={service} onChange={setService}><option>Followers</option><option>Likes</option><option>Video views</option><option>Comments</option><option>Shares</option></SelectField><Field label="Target URL or username" placeholder="https://instagram.com/yourprofile" /></div>
        <div className="fields-grid"><Field label="Quantity" value={quantity} type="number" onChange={setQuantity}/><div className="info-box"><span>Service limits</span><strong>Min 100 · Max 100,000</strong><small>Estimated delivery: 10–30 minutes</small></div></div>
        <div className="service-note"><Icon name="shield"/><div><strong>High-quality {platform} {service.toLowerCase()}</strong><p>Gradual delivery with refill protection. Keep your profile public during delivery.</p></div></div>
      </Card>
      <Card className="summary"><span className="eyebrow">Order summary</span><h2>Review your order</h2><dl><div><dt>Platform</dt><dd>{platform}</dd></div><div><dt>Service</dt><dd>{service}</dd></div><div><dt>Quantity</dt><dd>{Number(quantity || 0).toLocaleString()}</dd></div><div><dt>Service cost</dt><dd>GHS {(Number(quantity || 0) / 1000 * 20).toFixed(2)}</dd></div><div><dt>Processing fee</dt><dd>GHS 5.00</dd></div></dl><div className="total"><span>Total</span><strong>GHS {total}</strong></div><Button full icon="arrow" disabled={!quantity} onClick={() => setPlaced(true)}>Place Order</Button><small className="secure"><Icon name="shield" size={14}/> Secure guest checkout. No account required.</small></Card>
    </div>
    {placed && <div className="modal-backdrop"><div className="modal"><button className="modal-close" onClick={() => setPlaced(false)}><Icon name="close"/></button><span className="success-icon"><Icon name="check" size={28}/></span><h2>Order created</h2><p>Your order <strong>#BX10483</strong> is ready for payment. Pay the exact amount and upload your receipt.</p><div className="receipt-total"><span>Amount due</span><strong>GHS {total}</strong></div><Button full onClick={() => go("payment")}>Continue to payment</Button><Button full variant="ghost" onClick={() => setPlaced(false)}>Pay later</Button></div></div>}
  </>;
}

function Orders({ go }: { go: (page: string) => void }) {
  const [filter, setFilter] = useState("All");
  return <><PageTitle title="My Orders" description="Track and manage all your campaigns." action={<Button icon="plus" onClick={() => go("new-order")}>New Order</Button>} />
    <Card><div className="filters"><div className="search"><Icon name="search"/><input placeholder="Search by order ID or service..." /></div><SelectField value={filter} onChange={setFilter}><option>All statuses</option><option>Pending</option><option>Processing</option><option>Completed</option><option>Cancelled</option></SelectField><SelectField><option>Newest first</option><option>Oldest first</option><option>Highest price</option></SelectField></div>
      <div className="tabs">{["All", "Pending", "Processing", "Completed", "Cancelled"].map((x) => <button onClick={() => setFilter(x)} className={filter === x ? "active" : ""} key={x}>{x}<span>{x === "All" ? 184 : x === "Completed" ? 156 : x === "Pending" ? 8 : x === "Processing" ? 12 : 8}</span></button>)}</div>
      <OrderTable onView={() => go("order-details")} /><div className="pagination"><span>Showing 1–5 of 184 orders</span><div><Button variant="secondary">Previous</Button><Button variant="secondary">Next</Button></div></div>
    </Card>
  </>;
}

function OrderDetails({ go }: { go: (page: string) => void }) {
  return <><button className="back-link" onClick={() => go("orders")}>← Back to orders</button><PageTitle title="Order #BX10481" description="Placed on 26 September 2026 at 10:42 AM" action={<Status>Processing</Status>} />
    <Card className="tracking"><div className="card-head"><div><span className="eyebrow">Delivery progress</span><h2>7,240 of 10,000 views delivered</h2></div><strong>72%</strong></div><div className="progress"><span style={{ width: "72%" }}/></div><div className="tracking-labels"><span>Started at 18,430</span><span>Current count 25,670</span><span>2,760 remaining</span></div></Card>
    <div className="details-grid"><Card><h2>Order details</h2><dl className="detail-list">{[["Platform","TikTok"],["Service","Video views"],["Target","tiktok.com/@joseph/video/742..."],["Quantity","10,000"],["Price","GHS 38.00"],["Estimated completion","Today, 2:30 PM"]].map(([a,b]) => <div key={a}><dt>{a}</dt><dd>{b}</dd></div>)}</dl></Card>
      <Card><h2>Order timeline</h2><div className="timeline">{[["Order confirmed","26 Sep, 10:42 AM"],["Sent to provider","26 Sep, 10:43 AM"],["Delivery started","26 Sep, 10:51 AM"],["Estimated completion","Today, 2:30 PM"]].map(([a,b],i) => <div className={i < 3 ? "done" : ""} key={a}><span><Icon name={i < 3 ? "check" : "clock"}/></span><div><strong>{a}</strong><small>{b}</small></div></div>)}</div></Card>
    </div><div className="action-row"><Button variant="secondary" icon="support" onClick={() => go("support")}>Contact Support</Button><Button variant="secondary" onClick={() => go("new-order")}>Reorder</Button><Button variant="ghost">Cancel order</Button></div>
  </>;
}

function Services({ go }: { go: (page: string) => void }) {
  const services = [["Instagram","Followers","High-quality followers with gradual delivery","100","100,000","GHS 20.00","Fast"],["TikTok","Video views","Stable views for public videos","1,000","1,000,000","GHS 3.30","Instant"],["Facebook","Page followers","Followers for public pages","100","100,000","GHS 17.00","Fast"],["X","Post likes","Likes for public posts","50","50,000","GHS 17.00","Instant"],["Telegram","Channel members","Members for public channels","100","100,000","GHS 25.00","Fast"]];
  return <><PageTitle title="Services" description="Explore our complete catalog of social growth services." />
    <Card><div className="filters"><div className="search"><Icon name="search"/><input placeholder="Search services..." /></div><SelectField><option>All platforms</option><option>Instagram</option><option>TikTok</option><option>Facebook</option><option>X</option><option>Telegram</option></SelectField><SelectField><option>All categories</option><option>Followers</option><option>Likes</option><option>Views</option></SelectField></div>
      <div className="table-wrap"><table><thead><tr><th>Platform</th><th>Service</th><th>Description</th><th>Min / Max</th><th>Price / 1,000</th><th>Speed</th><th></th></tr></thead><tbody>{services.map((s) => <tr key={s[0]}><td><span className="platform-cell"><SocialIcon platform={s[0]}/>{s[0]}</span></td><td><strong>{s[1]}</strong></td><td>{s[2]}</td><td>{s[3]} / {s[4]}</td><td><strong>{s[5]}</strong></td><td><Status>{s[6]}</Status></td><td><Button variant="secondary" onClick={() => go("new-order")}>Order now</Button></td></tr>)}</tbody></table></div>
    </Card>
  </>;
}

function Wallet({ go }: { go: (page: string) => void }) {
  const cards = [["Available Balance","GHS 250.00","wallet"],["Pending Balance","GHS 45.00","clock"],["Total Deposited","GHS 1,850.00","plus"],["Total Spent","GHS 1,555.00","transactions"]] as const;
  return <><PageTitle title="Wallet" description="Manage your balance and payments." action={<Button icon="plus" onClick={() => go("payment")}>Add Funds</Button>} />
    <Card className="balance-hero"><div><span>Available balance</span><strong>GHS 250.00</strong><p>Ready to use on any BoostX service.</p></div><div><Button variant="secondary" onClick={() => go("payment")}>Add funds</Button><Button variant="ghost">Request refund</Button></div></Card>
    <div className="stats wallet-stats">{cards.map(([a,b,c]) => <Card className="stat" key={a}><div className="stat-head"><span>{a}</span><span className="icon-tile"><Icon name={c}/></span></div><strong>{b}</strong><small>Updated just now</small></Card>)}</div>
    <Card><div className="card-head"><div><span className="eyebrow">Recent activity</span><h2>Transaction history</h2></div><Button variant="secondary" onClick={() => go("transactions")}>View all</Button></div><TransactionTable /></Card>
  </>;
}

function TransactionTable() {
  const rows = [["#TX90842","Deposit","Mobile money top-up","+ GHS 100.00","Mobile Money","Completed","26 Sep 2026"],["#TX90838","Order","Order #BX10481","− GHS 38.00","Wallet","Completed","26 Sep 2026"],["#TX90765","Deposit","Wallet funding","+ GHS 250.00","Card","Completed","20 Sep 2026"],["#TX90712","Refund","Order #BX10392","+ GHS 22.00","Wallet","Completed","18 Sep 2026"]];
  return <div className="table-wrap"><table><thead><tr><th>Transaction ID</th><th>Type</th><th>Description</th><th>Amount</th><th>Method</th><th>Status</th><th>Date</th></tr></thead><tbody>{rows.map((r) => <tr key={r[0]}>{r.map((x,i) => <td key={i}>{i === 0 || i === 3 ? <strong>{x}</strong> : i === 5 ? <Status>{x}</Status> : x}</td>)}</tr>)}</tbody></table></div>;
}

function Payment({ go }: { go: (page: string) => void }) {
  const [amount, setAmount] = useState("100");
  const [network, setNetwork] = useState("Telecel");
  const [upload, setUpload] = useState<"idle" | "uploading" | "success" | "verifying" | "verified" | "rejected" | "review">("idle");
  const [dragging, setDragging] = useState(false);
  const [filename, setFilename] = useState("");
  const instructions: Record<string, string[]> = {
    Telecel: ["Dial *110#", "Select Send Money", "Enter 0202979378", `Enter the exact amount — GHS ${Number(amount || 0).toFixed(2)}`, "Enter PIN"],
    MTN: ["Dial *170#", "Select Transfer Money", "Select Other Networks", "Select Telecel", "Enter 0202979378", `Enter GHS ${Number(amount || 0).toFixed(2)}`, "Confirm the recipient name is BOOSTX", "Enter PIN"],
    AirtelTigo: ["Dial *110#", "Select Send Money", "Select To Mobile Number", "Select Other Networks", "Select Telecel", "Enter 0202979378", `Enter GHS ${Number(amount || 0).toFixed(2)}`, "Enter PIN"],
  };
  const selectFile = (file?: File) => {
    if (!file) return;
    setFilename(file.name);
    setUpload("uploading");
    setTimeout(() => {
      setUpload("success");
      setTimeout(() => {
        setUpload("verifying");
        setTimeout(() => setUpload(file.name.toLowerCase().includes("reject") ? "rejected" : file.name.toLowerCase().includes("review") ? "review" : "verified"), 1100);
      }, 500);
    }, 700);
  };
  const copyNumber = () => navigator.clipboard?.writeText("0202979378");
  return <><PageTitle title="Complete Payment" description="Send the exact amount, then upload your payment screenshot." />
    <div className="payment-layout">
      <div className="payment-main">
        <Card><div className="card-head"><div><span className="eyebrow">Amount to send</span><h2>Choose your payment amount</h2></div><span className="icon-tile"><Icon name="wallet"/></span></div><Field label="Amount in Ghana Cedi" value={amount} type="number" onChange={setAmount}/><div className="amounts">{["50","100","250","500"].map(a => <button className={amount === a ? "selected" : ""} onClick={() => setAmount(a)} key={a}>GHS {a}</button>)}</div></Card>
        <Card><span className="eyebrow">Mobile money</span><h2>Select your network</h2><div className="network-tabs">{["Telecel","MTN","AirtelTigo"].map(n => <button className={network === n ? "active" : ""} onClick={() => setNetwork(n)} key={n}>{n}</button>)}</div>
          <div className="payment-account"><div><small>Send payment to</small><strong>0202979378</strong><span>Telecel Cash · Account name: BOOSTX</span></div><Button variant="secondary" icon="copy" onClick={copyNumber}>Copy</Button></div>
          <div className="payment-warning"><Icon name="shield"/><strong>Send the exact amount shown — any network fee is added on top, not deducted.</strong></div>
          <ol className="instructions">{instructions[network].map((step, i) => <li key={step}><span>{i + 1}</span><p>{step}</p></li>)}</ol>
        </Card>
        <Card><span className="eyebrow">Payment proof</span><h2>Upload your screenshot</h2><p>Upload a clear screenshot showing the amount, recipient, reference and successful status.</p>
          <label className={`upload-zone ${dragging ? "dragging" : ""} ${upload !== "idle" ? "has-file" : ""}`} onDragOver={(e) => { e.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={(e) => { e.preventDefault(); setDragging(false); selectFile(e.dataTransfer.files[0]); }}>
            <input type="file" accept="image/png,image/jpeg,image/webp" onChange={(e) => selectFile(e.target.files?.[0])}/>
            <span className="upload-icon"><Icon name={upload === "verified" ? "check" : "plus"} size={22}/></span>
            <strong>{upload === "idle" ? "Drop your payment screenshot here" : upload === "uploading" ? "Uploading screenshot…" : filename}</strong>
            <small>{upload === "idle" ? "PNG, JPG or WEBP · Maximum 10 MB" : upload === "uploading" ? "Please keep this page open" : "Screenshot uploaded successfully"}</small>
            {upload === "idle" && <span className="browse">Choose file</span>}
          </label>
        </Card>
      </div>
      <div className="payment-side">
        <Card className="summary"><span className="eyebrow">Payment summary</span><h2>Review payment</h2><dl><div><dt>Amount</dt><dd>GHS {Number(amount || 0).toFixed(2)}</dd></div><div><dt>Recipient</dt><dd>BOOSTX</dd></div><div><dt>Number</dt><dd>0202979378</dd></div><div><dt>Receiving network</dt><dd>Telecel Cash</dd></div></dl><div className="total"><span>Exact amount due</span><strong>GHS {Number(amount || 0).toFixed(2)}</strong></div><small className="secure"><Icon name="shield" size={14}/> Your screenshot is securely processed.</small></Card>
        {upload === "verifying" && <Card className="verification-state"><span className="spinner"/><h2>Verifying your payment</h2><p>Checking the amount, recipient, status and transaction reference.</p></Card>}
        {upload === "verified" && <Card className="verification-result"><span className="success-icon"><Icon name="check" size={24}/></span><Status>Verified</Status><h2>Payment confirmed</h2><dl className="detail-list"><div><dt>Detected amount</dt><dd>GHS {Number(amount || 0).toFixed(2)}</dd></div><div><dt>Expected amount</dt><dd>GHS {Number(amount || 0).toFixed(2)}</dd></div><div><dt>Recipient</dt><dd>BOOSTX</dd></div><div><dt>Reference</dt><dd>TXN804291</dd></div></dl><Button full onClick={() => go("orders")}>Continue to Order</Button></Card>}
        {upload === "rejected" && <Card className="verification-result"><Status>Rejected</Status><h2>Payment could not be verified</h2><p>The screenshot does not show a successful payment to the BoostX number. Please check it and try again.</p><Button full variant="secondary" onClick={() => { setUpload("idle"); setFilename(""); }}>Upload New Screenshot</Button></Card>}
        {upload === "review" && <Card className="verification-result"><Status>Review Required</Status><h2>Manual review required</h2><p>Some payment details were unclear. Our team will review your screenshot before you can continue.</p><Button full disabled>Awaiting review</Button></Card>}
      </div>
    </div>
  </>;
}

function Transactions() {
  return <><PageTitle title="Transactions" description="A complete record of money moving through your account." /><div className="stats mini-stats">{[["Money in","GHS 1,872.00"],["Money out","GHS 1,555.00"],["Refunds","GHS 68.00"]].map(([a,b]) => <Card className="stat" key={a}><span>{a}</span><strong>{b}</strong><small>All time</small></Card>)}</div><Card><div className="filters"><div className="search"><Icon name="search"/><input placeholder="Search transactions..." /></div><SelectField><option>All types</option><option>Deposits</option><option>Orders</option><option>Refunds</option></SelectField><SelectField><option>Last 30 days</option><option>Last 90 days</option></SelectField></div><TransactionTable/><div className="pagination"><span>Showing 1–4 of 78 transactions</span><Button variant="secondary">Next</Button></div></Card></>;
}

function Support() {
  const [ticket, setTicket] = useState(false);
  return <><PageTitle title="Support Center" description="Find answers or get help from our team." action={<Button icon="plus" onClick={() => setTicket(true)}>Create Ticket</Button>} />
    <Card className="support-search"><h2>What can we help you with?</h2><div className="search big"><Icon name="search"/><input placeholder="Search help articles and FAQs..." /></div></Card>
    <div className="support-grid">{[["orders","Orders & delivery","Tracking, delivery times and refills"],["wallet","Payments & wallet","Deposits, refunds and verification"],["user","Account & security","Profile, password and account access"],["plus","Getting started","Learn how to place and track your first order"]].map(([i,a,b]) => <Card key={a}><span className="icon-tile"><Icon name={i as IconName}/></span><h2>{a}</h2><p>{b}</p><button className="text-link">Browse articles <Icon name="arrow"/></button></Card>)}</div>
    <Card><div className="card-head"><div><span className="eyebrow">Your requests</span><h2>Recent tickets</h2></div></div><div className="table-wrap"><table><thead><tr><th>Ticket ID</th><th>Subject</th><th>Category</th><th>Status</th><th>Last updated</th></tr></thead><tbody><tr><td><strong>#TK2094</strong></td><td>Order delivery is slower than expected</td><td>Orders</td><td><Status>Answered</Status></td><td>2 hours ago</td></tr><tr><td><strong>#TK1983</strong></td><td>Payment verification question</td><td>Payment</td><td><Status>Closed</Status></td><td>14 Sep 2026</td></tr></tbody></table></div></Card>
    {ticket && <div className="modal-backdrop"><div className="modal wide"><button className="modal-close" onClick={() => setTicket(false)}><Icon name="close"/></button><h2>Create a support ticket</h2><p>Tell us what happened and we’ll get back to you shortly.</p><Field label="Subject" placeholder="Briefly describe your issue"/><div className="fields-grid"><Field label="Order ID (optional)" placeholder="#BX..."/><SelectField label="Category"><option>Orders & delivery</option><option>Payments</option><option>Account</option><option>General</option></SelectField></div><label className="field"><span>Message</span><textarea placeholder="Share any helpful details..."/></label><Button full onClick={() => setTicket(false)}>Submit Ticket</Button></div></div>}
  </>;
}

function Profile() {
  const [editing, setEditing] = useState(false);
  return <><PageTitle title="Profile" description="Manage your personal information." action={<Button variant="secondary" onClick={() => setEditing(!editing)}>{editing ? "Cancel" : "Edit Profile"}</Button>} />
    <div className="details-grid profile-grid"><Card><div className="profile-head"><span className="avatar large">JA</span><div><h2>Joseph Asare</h2><p>Customer since March 2026</p><Status>Verified account</Status></div></div><dl className="detail-list">{[["Account ID","BX-80942"],["Total orders","184"],["Completed","156"],["Wallet balance","GHS 250.00"]].map(([a,b]) => <div key={a}><dt>{a}</dt><dd>{b}</dd></div>)}</dl></Card>
      <Card><h2>Personal information</h2><div className="profile-fields"><Field label="Full name" value="Joseph Asare"/><Field label="Email address" value="joseph.asare@example.com"/><Field label="Phone number" value="+233 24 555 0192"/><Button disabled={!editing}>{editing ? "Save changes" : "Information is up to date"}</Button></div></Card></div>
  </>;
}

function Toggle({ on = true }: { on?: boolean }) { const [active,setActive] = useState(on); return <button onClick={() => setActive(!active)} className={`toggle ${active ? "on" : ""}`} aria-label="Toggle setting"><span/></button>; }

function Settings({ dark, setDark }: { dark: boolean; setDark: (v: boolean) => void }) {
  return <><PageTitle title="Settings" description="Control your account preferences and security." /><div className="settings-layout"><div className="settings-nav">{["Account","Security","Notifications","Appearance","Payment"].map((x,i) => <button className={i === 3 ? "active" : ""} key={x}>{x}</button>)}</div><div className="settings-content">
    <Card><span className="eyebrow">Appearance</span><h2>Choose your theme</h2><p>Select how BoostX looks on this device.</p><div className="theme-cards"><button className={!dark ? "selected" : ""} onClick={() => setDark(false)}><div className="theme-preview light"><span/><i/><b/><em/></div><span><Icon name="sun"/>Light mode</span></button><button className={dark ? "selected" : ""} onClick={() => setDark(true)}><div className="theme-preview dark"><span/><i/><b/><em/></div><span><Icon name="moon"/>Dark mode</span></button></div></Card>
    <Card><span className="eyebrow">Notifications</span><h2>Notification preferences</h2>{[["Order updates","Status changes and delivery updates"],["Payment updates","Deposits, refunds and payment status"],["Promotions","Offers and new service announcements"],["Security alerts","Important account security notifications"]].map(([a,b],i) => <div className="setting-row" key={a}><div><strong>{a}</strong><p>{b}</p></div><Toggle on={i !== 2}/></div>)}</Card>
    <Card><span className="eyebrow">Security</span><h2>Password & sessions</h2><div className="setting-row"><div><strong>Change password</strong><p>Last changed 4 months ago</p></div><Button variant="secondary">Update</Button></div><div className="setting-row"><div><strong>Two-factor authentication</strong><p>Add an extra layer of protection</p></div><Toggle on={false}/></div></Card>
  </div></div></>;
}

function AdminDashboard({ go }: { go: (page: string) => void }) {
  return <><PageTitle title="Admin Overview" description="Live platform performance and operational health." action={<Button variant="secondary">Export report</Button>} />
    <div className="stats admin-stats">{[["Today's Orders","128","orders"],["Today's Revenue","GHS 4,840","chart"],["Pending Payments","14","clock"],["Verified Payments","96","check"],["Failed Payments","6","close"],["Active Orders","47","transactions"],["Provider Balance","GHS 12,450","wallet"]].map(([a,b,c]) => <Card className="stat" key={a}><div className="stat-head"><span>{a}</span><span className="icon-tile"><Icon name={c as IconName}/></span></div><strong>{b}</strong><small>Updated just now</small></Card>)}</div>
    <div className="dashboard-grid"><Card className="chart-card"><div className="card-head"><div><span className="eyebrow">Revenue</span><h2>GHS 84,520 this month</h2></div><SelectField><option>Last 30 days</option></SelectField></div><div className="bar-chart">{[42,62,48,78,55,88,66,92,74,98,82,94].map((h,i) => <span key={i} style={{height:`${h}%`}}/>)}</div><div className="x-axis"><span>1 Sep</span><span>8 Sep</span><span>15 Sep</span><span>22 Sep</span><span>30 Sep</span></div></Card><Card><span className="eyebrow">System health</span><h2>All systems operational</h2>{[["Provider API","Operational"],["Database","Operational"],["AI verification","Operational"],["Queue / worker","Operational"],["Storage","Operational"]].map(([a,b]) => <div className="health-row" key={a}><span><i/>{a}</span><strong>{b}</strong></div>)}<Button full variant="secondary" onClick={() => go("admin-health")}>View system health</Button></Card></div>
    <div className="details-grid"><Card><div className="card-head"><div><span className="eyebrow">Payment queue</span><h2>Recent payments</h2></div><Button variant="secondary" onClick={() => go("admin-payments")}>View all</Button></div><AdminPaymentTable compact onView={() => go("admin-payment-review")}/></Card><Card><div className="card-head"><div><span className="eyebrow">Order activity</span><h2>Recent orders</h2></div><Button variant="secondary" onClick={() => go("admin-orders")}>Manage</Button></div><OrderTable onView={() => go("admin-orders")}/></Card></div>
  </>;
}

const adminPayments = [
  ["#PAY8042","#BX10483","Ama Mensah","MTN","GHS 100.00","GHS 100.00","BOOSTX","TX804291","Matched","Verified","Today, 11:42"],
  ["#PAY8041","#BX10482","Kwame Asare","Telecel","GHS 55.00","GHS 50.00","BOOSTX","TX804188","Mismatch","Review Required","Today, 11:18"],
  ["#PAY8039","#BX10479","Nana Boateng","AirtelTigo","GHS 84.00","—","Unknown","—","Unreadable","Rejected","Today, 10:54"],
];

function AdminPaymentTable({ compact = false, onView }: { compact?: boolean; onView: () => void }) {
  return <div className="table-wrap"><table><thead><tr><th>Payment ID</th><th>Order ID</th><th>Customer</th>{!compact && <><th>Network</th><th>Expected</th><th>AI Detected</th><th>Recipient</th><th>Reference</th><th>AI Result</th></>}<th>Status</th><th>Date</th><th></th></tr></thead><tbody>{adminPayments.map(r => <tr key={r[0]}><td><strong>{r[0]}</strong></td><td>{r[1]}</td><td>{r[2]}</td>{!compact && <>{r.slice(3,9).map((x,i) => <td key={i}>{x}</td>)}</>}<td><Status>{r[9]}</Status></td><td>{r[10]}</td><td><Button variant="secondary" onClick={onView}>Review</Button></td></tr>)}</tbody></table></div>;
}

function AdminPayments({ go }: { go: (page: string) => void }) {
  return <><PageTitle title="Payments" description="Review AI-verified payments and resolve exceptions." /><div className="stats mini-stats">{[["Pending review","14"],["Verified today","96"],["Rejected today","6"]].map(([a,b]) => <Card className="stat" key={a}><span>{a}</span><strong>{b}</strong><small>Today</small></Card>)}</div><Card><div className="filters"><div className="search"><Icon name="search"/><input placeholder="Search payment, order or customer..."/></div><SelectField><option>All results</option><option>Verified</option><option>Review Required</option><option>Rejected</option></SelectField><SelectField><option>Today</option><option>Last 7 days</option></SelectField></div><AdminPaymentTable onView={() => go("admin-payment-review")}/></Card></>;
}

function AdminPaymentReview({ go }: { go: (page: string) => void }) {
  const [decision, setDecision] = useState("");
  return <><button className="back-link" onClick={() => go("admin-payments")}>← Back to payments</button><PageTitle title="Review Payment #PAY8041" description="AI flagged an amount mismatch · Submitted today at 11:18 AM" action={<Status>{decision || "Review Required"}</Status>} />
    <div className="payment-review-grid"><Card><span className="eyebrow">Uploaded screenshot</span><div className="receipt-preview"><div className="receipt-phone"><span className="success-icon"><Icon name="check"/></span><h2>Transaction Successful</h2><strong>GHS 50.00</strong><dl><div><dt>Recipient</dt><dd>BOOSTX</dd></div><div><dt>Number</dt><dd>0202979378</dd></div><div><dt>Reference</dt><dd>TX804188</dd></div><div><dt>Date</dt><dd>26 Sep 2026, 11:16</dd></div></dl></div></div></Card>
      <div className="payment-review-side"><Card><span className="eyebrow">Payment information</span><h2>AI verification result</h2><dl className="detail-list"><div><dt>Expected amount</dt><dd>GHS 55.00</dd></div><div><dt>Detected amount</dt><dd>GHS 50.00</dd></div><div><dt>Network</dt><dd>Telecel</dd></div><div><dt>Recipient</dt><dd>BOOSTX</dd></div><div><dt>Reference</dt><dd>TX804188</dd></div><div><dt>AI result</dt><dd><Status>Mismatch</Status></dd></div></dl></Card>
        <Card><span className="eyebrow">Admin decision</span><h2>Resolve this payment</h2><p>Approving credits the detected payment and releases the order. Rejection asks the customer for new proof.</p><div className="decision-actions"><Button full onClick={() => setDecision("Approved")}>Approve Payment</Button><Button full variant="secondary" onClick={() => setDecision("Rejected")}>Reject Payment</Button></div>{decision && <div className="decision-note"><Icon name="check"/><span>Payment marked as <strong>{decision}</strong>. The audit log has been updated.</span></div>}</Card>
      </div>
    </div></>;
}

function AdminOrders() {
  return <><PageTitle title="Orders" description="Track fulfillment and take operational action." /><Card><div className="filters"><div className="search"><Icon name="search"/><input placeholder="Search orders..."/></div><SelectField><option>All statuses</option><option>Pending</option><option>Processing</option><option>Completed</option></SelectField><SelectField><option>Newest first</option></SelectField></div><OrderTable onView={() => {}}/><div className="admin-order-actions"><Button variant="secondary">Track Order</Button><Button variant="secondary">View Payment</Button><Button variant="secondary">Event History</Button><Button variant="ghost">Refill</Button><Button variant="ghost">Cancel</Button></div></Card></>;
}

function AdminServices() {
  const rows = [["Instagram","Followers","GHS 20.00","100","100,000","Yes"],["TikTok","Video views","GHS 3.30","1,000","1,000,000","Yes"],["Facebook","Page followers","GHS 17.00","100","100,000","No"],["X","Post likes","GHS 17.00","50","50,000","Yes"],["Telegram","Channel members","GHS 25.00","100","100,000","Yes"]];
  return <><PageTitle title="Services" description="Control availability, pricing and fulfillment rules." action={<Button icon="plus">Add Service</Button>}/><Card><div className="table-wrap"><table><thead><tr><th>Platform</th><th>Service</th><th>Customer price / 1,000</th><th>Minimum</th><th>Maximum</th><th>Refill</th><th>Active</th><th></th></tr></thead><tbody>{rows.map(r => <tr key={r[0]}><td><span className="platform-cell"><SocialIcon platform={r[0]}/>{r[0]}</span></td>{r.slice(1).map((x,i) => <td key={i}>{x}</td>)}<td><Toggle/></td><td><Button variant="secondary">Edit</Button></td></tr>)}</tbody></table></div></Card></>;
}

function AdminPlatforms() {
  return <><PageTitle title="Platforms" description="The five social platforms available across BoostX." /><div className="platform-admin-grid">{["TikTok","Instagram","Facebook","X","Telegram"].map((p,i) => <Card key={p}><div className="card-head"><SocialIcon platform={p}/><Toggle/></div><h2>{p}</h2><p>{[18,24,16,9,11][i]} active services</p><Button full variant="secondary">Manage services</Button></Card>)}</div></>;
}

function AdminConfigPage({ type }: { type: string }) {
  if (type === "health") return <><PageTitle title="System Health" description="Live status of critical BoostX services." /><div className="health-grid">{[["Provider API","Operational","99.98% uptime"],["Database","Operational","18 ms response"],["AI Verification","Operational","96 queued"],["Queue / Worker","Operational","4 active workers"],["Storage","Operational","42% used"]].map(([a,b,c]) => <Card key={a}><div className="health-row"><span><i/>{a}</span><Status>{b}</Status></div><strong className="health-metric">{c}</strong><p>Last checked less than a minute ago.</p></Card>)}</div></>;
  if (type === "audit") return <><PageTitle title="Audit Logs" description="Immutable history of administrator actions." /><Card><div className="table-wrap"><table><thead><tr><th>Admin ID</th><th>Action</th><th>Object</th><th>Old Value</th><th>New Value</th><th>Timestamp</th></tr></thead><tbody>{[["ADM-001","Payment approved","PAY8041","Review Required","Verified","26 Sep, 11:52"],["ADM-003","Price updated","IG-FOLLOWERS","GHS 18.00","GHS 20.00","26 Sep, 10:18"],["ADM-001","Service disabled","FB-LIKES","Active","Disabled","25 Sep, 18:42"]].map(r => <tr key={r.join()}>{r.map((x,i) => <td key={i}>{i === 0 ? <strong>{x}</strong> : x}</td>)}</tr>)}</tbody></table></div></Card></>;
  if (type === "provider" || type === "api") return <><PageTitle title={type === "api" ? "Provider API" : "Provider Balance"} description="Secure fulfillment provider connection and funding status." /><div className="details-grid"><Card><span className="eyebrow">Connection</span><h2>Provider API</h2><div className="setting-row"><div><strong>Connection status</strong><p>Last checked 30 seconds ago</p></div><Status>Connected</Status></div><Field label="Provider API URL" value="https://boostcenter2.com/api/v2"/><Field label="API key" value="••••••••••••••••d9f2"/><Button variant="secondary">Test Connection</Button></Card><Card><span className="eyebrow">Provider balance</span><h2>GHS 12,450.80</h2><p>Estimated capacity for 2,480 average orders.</p><Button variant="secondary">Refresh balance</Button></Card></div></>;
  if (type === "settings") return <><PageTitle title="Admin Settings" description="Payment receiving account and internal configuration." /><Card className="admin-settings-card"><span className="eyebrow">Payment configuration</span><h2>Mobile money receiving account</h2><div className="fields-grid"><SelectField label="Network"><option>Telecel Cash</option></SelectField><Field label="Account name" value="BOOSTX"/><Field label="Account number" value="0202979378"/><SelectField label="Status"><option>Active</option><option>Disabled</option></SelectField></div><label className="field"><span>Payment instructions</span><textarea value="Send the exact amount shown. Network fees must be added on top, not deducted." readOnly/></label><Button>Save Payment Settings</Button></Card></>;
  const title = type === "users" ? "Users" : type === "pricing" ? "Pricing" : type === "transactions" ? "Transactions" : type === "support" ? "Support" : "Admin";
  return <><PageTitle title={title} description={`Manage BoostX ${title.toLowerCase()} from one place.`}/><Card><div className="filters"><div className="search"><Icon name="search"/><input placeholder={`Search ${title.toLowerCase()}...`}/></div><SelectField><option>All statuses</option><option>Active</option><option>Disabled</option></SelectField><SelectField><option>Newest first</option></SelectField></div><div className="admin-empty"><span className="icon-tile"><Icon name={type === "users" ? "users" : type === "support" ? "support" : "transactions"}/></span><h2>{title} management</h2><p>Search, filter and manage all {title.toLowerCase()} records here.</p></div></Card></>;
}

function Auth({ mode, go }: { mode: "login" | "register"; go: (page: string) => void }) {
  return <div className="auth-page"><div className="auth-brand"><img src={logo} alt="BoostX"/><div><span className="eyebrow">Social growth, simplified</span><h1>Build momentum.<br/>Reach more people.</h1><p>Premium social media growth services with transparent GHS pricing, fast delivery and real-time tracking.</p></div><small>© 2026 BoostX. Built in Ghana.</small></div>
    <div className="auth-form"><div className="auth-mobile-logo"><img src={logo} alt="BoostX"/></div><Card><span className="eyebrow">{mode === "login" ? "Welcome back" : "Create an account"}</span><h2>{mode === "login" ? "Sign in to BoostX" : "Start growing with BoostX"}</h2><p>{mode === "login" ? "Access your orders, wallet and account." : "Track orders and manage everything in one place."}</p>{mode === "register" && <Field label="Full name" placeholder="Joseph Asare"/>}<Field label="Email or phone" placeholder="you@example.com"/><Field label="Password" placeholder="Enter your password" type="password"/>{mode === "register" && <Field label="Confirm password" placeholder="Re-enter your password" type="password"/>}<Button full onClick={() => go("dashboard")}>{mode === "login" ? "Sign in" : "Create account"}</Button><div className="auth-switch">{mode === "login" ? "New to BoostX?" : "Already have an account?"}<button onClick={() => go(mode === "login" ? "register" : "login")}>{mode === "login" ? "Create an account" : "Sign in"}</button></div><div className="guest-divider"><span>or</span></div><Button full variant="secondary" onClick={() => go("new-order")}>Continue as guest</Button></Card></div>
  </div>;
}

function Shell({ page, go, children, dark, setDark }: { page: string; go: (page: string) => void; children: ReactNode; dark: boolean; setDark: (v: boolean) => void }) {
  const [open, setOpen] = useState(false);
  return <div className="app-shell"><aside className={open ? "open" : ""}><div className="sidebar-logo"><img src={logo} alt="BoostX"/><button onClick={() => setOpen(false)}><Icon name="close"/></button></div><nav>{navGroups.map(g => <div className="nav-group" key={g.label}><span>{g.label}</span>{g.links.map(([id,label,icon]) => <button className={page === id || (page === "order-details" && id === "orders") ? "active" : ""} onClick={() => { go(id); setOpen(false); }} key={id}><Icon name={icon}/>{label}</button>)}</div>)}</nav><div className="sidebar-bottom"><button onClick={() => setDark(!dark)}><Icon name={dark ? "sun" : "moon"}/>{dark ? "Light mode" : "Dark mode"}</button><button onClick={() => go("login")}><Icon name="logout"/>Log out</button></div></aside>{open && <button className="drawer-backdrop" onClick={() => setOpen(false)} aria-label="Close menu"/>}
    <div className="main"><header><button className="mobile-menu" onClick={() => setOpen(true)}><Icon name="menu"/></button><div className="top-search"><Icon name="search"/><input placeholder="Search orders, services..."/></div><div className="top-actions"><button className="notification"><Icon name="bell"/><i/></button><button className="balance" onClick={() => go("wallet")}><span>Wallet balance</span><strong>GHS 250.00</strong></button><button className="user-menu" onClick={() => go("profile")}><span className="avatar">JA</span><span><strong>Joseph</strong><small>Customer</small></span><Icon name="arrow"/></button></div></header><main>{children}</main><nav className="bottom-nav">{[["dashboard","Home","home"],["orders","Orders","orders"],["new-order","New","plus"],["wallet","Wallet","wallet"],["profile","Profile","user"]].map(([id,label,icon]) => <button className={page === id ? "active" : ""} onClick={() => go(id)} key={id}><Icon name={icon as IconName}/><span>{label}</span></button>)}</nav></div>
  </div>;
}

const adminNav = [
  ["admin","Dashboard","home"],["admin-orders","Orders","orders"],["admin-payments","Payments","card"],["admin-transactions","Transactions","transactions"],["admin-users","Users","users"],["admin-services","Services","services"],["admin-platforms","Platforms","chart"],["admin-pricing","Pricing","wallet"],["admin-provider","Provider Balance","wallet"],["admin-api","API","shield"],["admin-health","System Health","chart"],["admin-audit","Audit Logs","orders"],["admin-support","Support","support"],["admin-settings","Settings","settings"],
] as const;

function AdminShell({ page, go, children, dark, setDark }: { page: string; go: (page: string) => void; children: ReactNode; dark: boolean; setDark: (v: boolean) => void }) {
  const [open, setOpen] = useState(false);
  return <div className="app-shell admin-shell"><aside className={open ? "open" : ""}><div className="sidebar-logo"><img src={logo} alt="BoostX"/><button onClick={() => setOpen(false)}><Icon name="close"/></button></div><div className="admin-label"><span>Internal workspace</span><strong>Administrator</strong></div><nav><div className="nav-group"><span>Admin</span>{adminNav.map(([id,label,icon]) => <button className={page === id ? "active" : ""} onClick={() => { go(id); setOpen(false); }} key={`${id}-${label}`}><Icon name={icon}/>{label}</button>)}</div></nav><div className="sidebar-bottom"><button onClick={() => setDark(!dark)}><Icon name={dark ? "sun" : "moon"}/>{dark ? "Light mode" : "Dark mode"}</button><button onClick={() => go("login")}><Icon name="logout"/>Log out</button></div></aside>{open && <button className="drawer-backdrop" onClick={() => setOpen(false)} aria-label="Close menu"/>}<div className="main"><header><button className="mobile-menu" onClick={() => setOpen(true)}><Icon name="menu"/></button><div className="top-search"><Icon name="search"/><input placeholder="Search orders, payments, users..."/></div><div className="top-actions"><button className="notification"><Icon name="bell"/><i/></button><button className="user-menu"><span className="avatar">EA</span><span><strong>Enock</strong><small>Administrator</small></span><Icon name="arrow"/></button></div></header><main>{children}</main></div></div>;
}

export default function App() {
  const initial = location.hash.replace("#/", "") || "dashboard";
  const [page, setPage] = useState(initial);
  const [dark, setDarkState] = useState(() => localStorage.getItem("boostx-theme") === "dark");
  const setDark = (value: boolean) => { setDarkState(value); localStorage.setItem("boostx-theme", value ? "dark" : "light"); };
  useEffect(() => { document.documentElement.dataset.theme = dark ? "dark" : "light"; }, [dark]);
  useEffect(() => { const sync = () => setPage(location.hash.replace("#/", "") || "dashboard"); addEventListener("hashchange", sync); return () => removeEventListener("hashchange", sync); }, []);
  const go = (next: string) => { location.hash = `/${next}`; setPage(next); scrollTo({ top: 0, behavior: "smooth" }); };
  const screen = useMemo(() => {
    switch (page) {
      case "dashboard": return <Dashboard go={go}/>;
      case "new-order": return <NewOrder go={go}/>;
      case "orders": return <Orders go={go}/>;
      case "order-details": return <OrderDetails go={go}/>;
      case "services": return <Services go={go}/>;
      case "wallet": return <Wallet go={go}/>;
      case "payment": return <Payment go={go}/>;
      case "transactions": return <Transactions/>;
      case "support": return <Support/>;
      case "profile": return <Profile/>;
      case "settings": return <Settings dark={dark} setDark={setDark}/>;
      default: return <Dashboard go={go}/>;
    }
  }, [page, dark]);
  if (page === "login" || page === "register") return <Auth mode={page} go={go}/>;
  if (page.startsWith("admin")) {
    let adminScreen: ReactNode;
    if (page === "admin") adminScreen = <AdminDashboard go={go}/>;
    else if (page === "admin-payments") adminScreen = <AdminPayments go={go}/>;
    else if (page === "admin-payment-review") adminScreen = <AdminPaymentReview go={go}/>;
    else if (page === "admin-orders") adminScreen = <AdminOrders/>;
    else if (page === "admin-services") adminScreen = <AdminServices/>;
    else if (page === "admin-platforms") adminScreen = <AdminPlatforms/>;
    else adminScreen = <AdminConfigPage type={page.replace("admin-", "")}/>;
    return <AdminShell page={page} go={go} dark={dark} setDark={setDark}>{adminScreen}</AdminShell>;
  }
  return <Shell page={page} go={go} dark={dark} setDark={setDark}>{screen}</Shell>;
}
