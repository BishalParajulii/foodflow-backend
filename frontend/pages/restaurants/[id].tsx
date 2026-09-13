import { useRouter } from "next/router";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import LoadingSpinner from "../../src/components/LoadingSpinner";
import ErrorMessage from "../../src/components/ErrorMessage";
import { useAuth } from "../../src/context/AuthContext";
import { api, BackendError, Restaurant, Review } from "../../src/lib/backend";

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "0.7rem 0.9rem",
  borderRadius: "0.6rem",
  border: "1px solid #e0cfb8",
  fontSize: "1rem",
  boxSizing: "border-box",
};

function Stars({ value, onPick }: { value: number; onPick?: (n: number) => void }) {
  return (
    <div style={{ display: "flex", gap: "0.25rem", fontSize: "1.5rem" }}>
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type={onPick ? "button" : undefined}
          onClick={onPick ? () => onPick(n) : undefined}
          disabled={!onPick}
          aria-label={`${n} star${n > 1 ? "s" : ""}`}
          style={{
            background: "transparent",
            border: "none",
            cursor: onPick ? "pointer" : "default",
            color: n <= value ? "var(--color-primary)" : "#d8c6ac",
            padding: 0,
          }}
        >
          ★
        </button>
      ))}
    </div>
  );
}

export default function RestaurantPage() {
  const { user } = useAuth();
  const router = useRouter();
  const { id } = router.query;
  const [restaurant, setRestaurant] = useState<Restaurant | null>(null);
  const [reviews, setReviews] = useState<Review[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [rating, setRating] = useState(5);
  const [title, setTitle] = useState("");
  const [comment, setComment] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    if (typeof id !== "string") return;
    setError(null);
    try {
      const [r, revs] = await Promise.all([
        api.get<Restaurant>(`/api/v1/restaurants/${id}/`),
        api.get<Review[]>(`/api/v1/reviews/?restaurant=${id}`),
      ]);
      setRestaurant(r);
      setReviews(revs);
    } catch (e: any) {
      setError(e?.message ?? "Failed to load restaurant");
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function submitReview(e: React.FormEvent) {
    e.preventDefault();
    if (!user) {
      router.push(`/login?next=/restaurants/${id}`);
      return;
    }
    setFormError(null);
    setBusy(true);
    try {
      await api.post<Review>("/api/v1/reviews/", {
        restaurant: id,
        rating,
        title,
        comment,
      });
      setTitle("");
      setComment("");
      setRating(5);
      await load();
    } catch (err: any) {
      setFormError(err instanceof BackendError ? err.message : "Could not submit review");
    } finally {
      setBusy(false);
    }
  }

  async function deleteReview(reviewId: string) {
    setFormError(null);
    try {
      await api.del(`/api/v1/reviews/${reviewId}/`);
      await load();
    } catch (err: any) {
      setFormError(err instanceof BackendError ? err.message : "Could not delete review");
    }
  }

  if (error) return <ErrorMessage message={error} />;
  if (!restaurant || !reviews) return <LoadingSpinner />;

  return (
    <section className="section-padding">
      <div className="container" style={{ maxWidth: "720px" }}>
        <p>
          <Link href="/menu">← Menu</Link>
        </p>
        <h1>{restaurant.name}</h1>
        {restaurant.description && <p style={{ color: "#6d5c55" }}>{restaurant.description}</p>}
        <p style={{ color: "#6d5c55", fontSize: "0.9rem" }}>
          {[restaurant.address, restaurant.phone].filter(Boolean).join(" · ")}
        </p>
        <p style={{ fontWeight: 700 }}>
          {restaurant.rating_average != null ? (
            <>★ {restaurant.rating_average.toFixed(1)} · {restaurant.review_count} review{restaurant.review_count === 1 ? "" : "s"}</>
          ) : (
            "No ratings yet — be the first!"
          )}
        </p>

        <h2 style={{ marginTop: "2rem" }}>Reviews</h2>
        {reviews.length === 0 ? (
          <p style={{ color: "#6d5c55" }}>No reviews yet.</p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: "0.8rem" }}>
            {reviews.map((r) => (
              <li
                key={r.id}
                style={{ border: "1px solid #f0e2c8", borderRadius: "0.8rem", padding: "0.9rem 1rem", background: "#fff" }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <Stars value={r.rating} />
                  <span style={{ color: "#6d5c55", fontSize: "0.85rem" }}>
                    {new Date(r.created_at).toLocaleDateString()}
                  </span>
                </div>
                {r.title && <strong>{r.title}</strong>}
                {r.comment && <p style={{ margin: "0.4rem 0" }}>{r.comment}</p>}
                <div style={{ color: "#6d5c55", fontSize: "0.85rem" }}>
                  {r.user_email}
                  {user && r.user === user.id && (
                    <button
                      onClick={() => deleteReview(r.id)}
                      style={{ marginLeft: "0.8rem", background: "transparent", border: "none", color: "var(--color-primary)", cursor: "pointer", fontSize: "0.85rem" }}
                    >
                      Delete
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}

        <h2 style={{ marginTop: "2rem" }}>Write a review</h2>
        {!user ? (
          <p>
            <Link href={`/login?next=/restaurants/${id}`}>Log in</Link> to write a review.
          </p>
        ) : (
          <form onSubmit={submitReview} style={{ display: "grid", gap: "0.9rem" }}>
            <Stars value={rating} onPick={setRating} />
            <input style={inputStyle} placeholder="Title (optional)" value={title} onChange={(e) => setTitle(e.target.value)} />
            <textarea
              style={{ ...inputStyle, minHeight: "90px", resize: "vertical" }}
              placeholder="How was your meal? (Tip: order first — delivered orders get a verified review)"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
            />
            {formError && <p style={{ color: "var(--color-primary)", margin: 0 }}>{formError}</p>}
            <button type="submit" disabled={busy}>
              {busy ? "Submitting…" : "Submit review"}
            </button>
          </form>
        )}
      </div>
    </section>
  );
}
