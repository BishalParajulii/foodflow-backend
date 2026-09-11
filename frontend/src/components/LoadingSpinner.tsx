export default function LoadingSpinner() {
  return (
    <div style={{ textAlign: "center", padding: "3rem" }}>
      <div
        style={{
          width: "40px",
          height: "40px",
          border: "4px solid rgba(196,30,58,0.2)",
          borderTopColor: "var(--color-primary)",
          borderRadius: "50%",
          animation: "spin 0.8s linear infinite",
          margin: "0 auto",
        }}
      />
    </div>
  );
}