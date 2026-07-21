import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { useAuth } from "../../contexts/AuthContext";
import { apiClient } from "../../api/apiClient";
import styles from "./Auth.module.css";
import { clsx } from "clsx";

export function SignupPage() {
  const [fullName, setFullName] = useState("");
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
      // 1. Register User
      await apiClient.post("/auth/register", {
        email,
        password,
        full_name: fullName,
      });

      // 2. Login immediately after
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const loginRes = await apiClient.post("/auth/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      // 3. Create a default workspace
      // Set the token temporarily so we can create a workspace
      localStorage.setItem("access_token", loginRes.data.access_token);
      await apiClient.post("/workspaces/", {
        name: "My Workspace",
        slug: `workspace-${Date.now()}`
      }, {
        headers: { Authorization: `Bearer ${loginRes.data.access_token}` }
      });

      // 4. Call global login to finalize
      login(loginRes.data.access_token);
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create account.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={clsx(styles.card, "glass")}>
        <div className={styles.header}>
          <h1 className={styles.title}>Create an account</h1>
          <p className={styles.subtitle}>Start auditing your designs today</p>
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.inputGroup}>
            <label htmlFor="fullName">Full Name</label>
            <input
              id="fullName"
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              className={styles.input}
              placeholder="John Doe"
            />
          </div>

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
            <label htmlFor="password">Password</label>
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
            {isSubmitting ? "Creating account..." : "Sign up"}
          </button>
        </form>

        <p className={styles.footer}>
          Already have an account? <Link to="/login" className={styles.link}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
