import { useEffect } from "react";
import { useAudits } from "../../hooks/useAudits";
import { useWorkspace } from "../../contexts/WorkspaceContext";
import styles from "./Dashboard.module.css";
import { clsx } from "clsx";
import { CheckSquare, AlertTriangle, TrendingUp, Clock } from "lucide-react";

export function DashboardPage() {
  const { activeWorkspace } = useWorkspace();
  const { audits, fetchAudits, isLoading } = useAudits();

  useEffect(() => {
    if (activeWorkspace) {
      fetchAudits();
    }
  }, [activeWorkspace, fetchAudits]);

  const completedAudits = audits.filter(a => a.status === "COMPLETED");
  const averageScore = completedAudits.length > 0
    ? Math.round(completedAudits.reduce((acc, curr) => acc + (curr.overall_score || 0), 0) / completedAudits.length)
    : 0;
  
  const metrics = [
    { label: "Total Audits", value: audits.length, icon: CheckSquare, color: "var(--accent-primary)" },
    { label: "Completed", value: completedAudits.length, icon: CheckSquare, color: "var(--success)" },
    { label: "Avg Score", value: `${averageScore}%`, icon: TrendingUp, color: "var(--warning)" },
    { label: "In Progress", value: audits.length - completedAudits.length, icon: Clock, color: "var(--accent-secondary)" },
  ];

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>Dashboard</h1>
        <p className={styles.subtitle}>
          Overview of your UXOps AI audits for <strong>{activeWorkspace?.name}</strong>
        </p>
      </header>

      <div className={styles.metricsGrid}>
        {metrics.map((metric) => (
          <div key={metric.label} className={clsx(styles.metricCard, "glass")}>
            <div className={styles.metricIconWrapper} style={{ backgroundColor: `${metric.color}20`, color: metric.color }}>
              <metric.icon className={styles.metricIcon} />
            </div>
            <div className={styles.metricInfo}>
              <span className={styles.metricLabel}>{metric.label}</span>
              <span className={styles.metricValue}>{metric.value}</span>
            </div>
          </div>
        ))}
      </div>

      <div className={styles.recentSection}>
        <h2 className={styles.sectionTitle}>Recent Activity</h2>
        <div className={clsx(styles.recentCard, "glass")}>
          {isLoading ? (
            <p className={styles.emptyState}>Loading audits...</p>
          ) : audits.length === 0 ? (
            <div className={styles.emptyState}>
              <AlertTriangle className={styles.emptyIcon} />
              <p>No audits found. Run your first audit to see insights here.</p>
              <button className="btn btn-primary" style={{ marginTop: '1rem' }}>
                New Audit
              </button>
            </div>
          ) : (
            <div className={styles.list}>
              {audits.slice(0, 5).map(audit => (
                <div key={audit.id} className={styles.listItem}>
                  <div className={styles.itemMain}>
                    <span className={styles.itemTitle}>{audit.title}</span>
                    <span className={styles.itemDate}>
                      {new Date(audit.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <span className={clsx(styles.badge, styles[`badge-${audit.status.toLowerCase()}`])}>
                    {audit.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
