export default function ErrorMessage({ message }: { message: string }) {
  return (
    <div style={{ textAlign: "center", padding: "2rem", color: "#c00" }}>
      <p>{message}</p>
    </div>
  );
}