export function NotFoundPage({ go }: { go: (page: string) => void }) {
  return (
    <div className="not-found-page" style={{ textAlign: "center", padding: "4rem 1rem" }}>
      <div className="card" style={{ maxWidth: "500px", margin: "0 auto", padding: "3rem 2rem" }}>
        <h1 style={{ fontSize: "3.5rem", margin: 0, color: "var(--primary)" }}>404</h1>
        <h2>Page Not Found</h2>
        <p style={{ color: "var(--muted)", margin: "1rem 0 2rem" }}>
          The page or resource you are looking for does not exist or has moved.
        </p>
        <button className="btn primary" onClick={() => go("dashboard")}>
          Return to Dashboard
        </button>
      </div>
    </div>
  );
}
