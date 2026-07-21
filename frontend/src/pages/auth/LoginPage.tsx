import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { useAuth } from "../../contexts/AuthContext";
import { apiClient } from "../../api/apiClient";
import styles from "./Auth.module.css";
import { clsx } from "clsx";

export function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      // FastAPI OAuth2PasswordRequestForm expects form-data
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await apiClient.post("/auth/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      login(response.data.access_token);
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to login. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={clsx(styles.card, "glass")}>
        <div className={styles.header}>
          <h1 className={styles.title}>Welcome back</h1>
          <p className={styles.subtitle}>Sign in to your account to continue</p>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.inputGroup}>
            <label htmlFor="email">Email address</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className={styles.input}
              placeholder="you@example.com"
            />
          </div>

          <div className={styles.inputGroup}>
            <div className="flex justify-between w-full">
              <label htmlFor="password">Password</label>
              <a href="#" className={styles.link}>Forgot password?</a>
            </div>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className={styles.input}
              placeholder="••••••••"
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary w-full"
            disabled={isSubmitting}
            style={{ marginTop: '0.5rem', padding: '0.75rem' }}
          >
            {isSubmitting ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className={styles.footer}>
          Don't have an account? <Link to="/signup" className={styles.link}>Sign up</Link>
        </p>
      </div>
    </div>
  );
}
