import { useEffect } from "react";
import { Link } from "react-router";
import { useAudits } from "../../hooks/useAudits";
import { useWorkspace } from "../../contexts/WorkspaceContext";
import styles from "./Audits.module.css";
import { clsx } from "clsx";
import { Search, Filter, Image as ImageIcon } from "lucide-react";

export function AuditsPage() {
  const { activeWorkspace } = useWorkspace();
  const { audits, fetchAudits, isLoading } = useAudits();

  useEffect(() => {
    if (activeWorkspace) {
      fetchAudits();
    }
  }, [activeWorkspace, fetchAudits]);

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Audits</h1>
          <p className={styles.subtitle}>Manage and view all design audits</p>
        </div>
        <button className="btn btn-primary">New Audit</button>
      </header>

      <div className={clsx(styles.toolbar, "glass")}>
        <div className={styles.searchBox}>
          <Search className={styles.searchIcon} />
          <input 
            type="text" 
            placeholder="Search audits..." 
            className={styles.searchInput}
          />
        </div>
        <button className={styles.filterBtn}>
          <Filter size={18} />
          Filter
        </button>
      </div>

      <div className={clsx(styles.grid, "glass")}>
        <div className={styles.tableHeader}>
          <span>Title</span>
          <span>Status</span>
          <span>Score</span>
          <span>Date</span>
          <span>Actions</span>
        </div>

        {isLoading ? (
          <div className={styles.emptyState}>Loading audits...</div>
        ) : audits.length === 0 ? (
          <div className={styles.emptyState}>No audits found. Create one to get started.</div>
        ) : (
          audits.map((audit) => (
            <div key={audit.id} className={styles.tableRow}>
              <div className={styles.cellTitle}>
                <div className={styles.imagePlaceholder}>
                  <ImageIcon size={16} />
                </div>
                <span>{audit.title}</span>
              </div>
              <div className={styles.cell}>
                <span className={clsx(styles.badge, styles[`badge-${audit.status.toLowerCase()}`])}>
                  {audit.status.replace("_", " ")}
                </span>
              </div>
              <div className={styles.cell}>
                {audit.overall_score !== null ? (
                  <span className={clsx(
                    styles.score,
                    audit.overall_score >= 90 ? styles.scoreHigh :
                    audit.overall_score >= 70 ? styles.scoreMedium : styles.scoreLow
                  )}>
                    {audit.overall_score}%
                  </span>
                ) : (
                  <span className={styles.textMuted}>—</span>
                )}
              </div>
              <div className={styles.cell}>
                <span className={styles.textMuted}>
                  {new Date(audit.created_at).toLocaleDateString()}
                </span>
              </div>
              <div className={styles.cell}>
                <Link to={`/audits/${audit.id}`} className={styles.actionBtn}>
                  View Report
                </Link>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
