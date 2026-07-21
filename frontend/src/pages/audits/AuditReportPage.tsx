import { useEffect, useState } from "react";
import { useParams, Link } from "react-router";
import { useAudits } from "../../hooks/useAudits";
import { ImageViewer } from "../../components/audits/ImageViewer";
import styles from "./AuditReport.module.css";
import { clsx } from "clsx";
import { ArrowLeft, CheckCircle2, AlertCircle, Info } from "lucide-react";
import { apiClient } from "../../api/apiClient"; // Need to get full image URL

export function AuditReportPage() {
  const { auditId } = useParams<{ auditId: string }>();
  const { currentAudit, fetchAuditDetails, isLoading } = useAudits();
  const [activeFindingId, setActiveFindingId] = useState<string | null>(null);

  useEffect(() => {
    if (auditId) {
      fetchAuditDetails(auditId);
    }
  }, [auditId, fetchAuditDetails]);

  if (isLoading || !currentAudit) {
    return <div className={styles.loading}>Loading report details...</div>;
  }

  // Construct full image URL from s3 key. In a real app, backend would return a presigned URL.
  // Assuming our backend serves raw images or we have a proxy, or the frontend needs to fetch it.
  // For UI sake, if screenshot_s3_key is absolute, use it, else point to backend.
  const imageUrl = currentAudit.screenshot_s3_key.startsWith('http') 
    ? currentAudit.screenshot_s3_key 
    : `${apiClient.defaults.baseURL}/workspaces/${currentAudit.workspace_id}/audits/${currentAudit.id}/image`;
  
  const findings = currentAudit.findings || [];

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high': return <AlertCircle size={16} className={styles.iconHigh} />;
      case 'medium': return <Info size={16} className={styles.iconMedium} />;
      default: return <CheckCircle2 size={16} className={styles.iconLow} />;
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.headerLeft}>
          <Link to="/audits" className={styles.backBtn}>
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className={styles.title}>{currentAudit.title}</h1>
            <p className={styles.subtitle}>
              Date: {new Date(currentAudit.created_at).toLocaleDateString()} | 
              Status: <span className={styles.statusBadge}>{currentAudit.status}</span>
            </p>
          </div>
        </div>
        
        <div className={styles.scores}>
          <div className={styles.scoreItem}>
            <span className={styles.scoreLabel}>Overall</span>
            <span className={clsx(styles.scoreValue, styles.scoreValueMain)}>
              {currentAudit.overall_score ?? '--'}%
            </span>
          </div>
          <div className={styles.scoreDivider} />
          <div className={styles.scoreItem}>
            <span className={styles.scoreLabel}>UI</span>
            <span className={styles.scoreValue}>{currentAudit.ui_score ?? '--'}</span>
          </div>
          <div className={styles.scoreItem}>
            <span className={styles.scoreLabel}>UX</span>
            <span className={styles.scoreValue}>{currentAudit.ux_score ?? '--'}</span>
          </div>
          <div className={styles.scoreItem}>
            <span className={styles.scoreLabel}>A11y</span>
            <span className={styles.scoreValue}>{currentAudit.accessibility_score ?? '--'}</span>
          </div>
        </div>
      </header>

      <div className={styles.content}>
        <div className={styles.mainView}>
          <div className={clsx(styles.imageCard, "glass")}>
            <ImageViewer 
              imageUrl={imageUrl} 
              findings={findings}
              activeFindingId={activeFindingId}
              onFindingClick={(id) => setActiveFindingId(id === activeFindingId ? null : id)}
            />
          </div>
        </div>

        <div className={styles.sidebar}>
          <div className={clsx(styles.findingsCard, "glass")}>
            <h2 className={styles.sectionTitle}>Findings ({findings.length})</h2>
            
            {findings.length === 0 ? (
              <p className={styles.emptyText}>No findings recorded.</p>
            ) : (
              <div className={styles.findingsList}>
                {findings.map(finding => (
                  <div 
                    key={finding.id}
                    className={clsx(styles.findingItem, {
                      [styles.findingActive]: activeFindingId === finding.id
                    })}
                    onClick={() => setActiveFindingId(finding.id === activeFindingId ? null : finding.id)}
                  >
                    <div className={styles.findingHeader}>
                      <span className={styles.findingCategory}>{finding.category}</span>
                      {getSeverityIcon(finding.severity)}
                    </div>
                    <p className={styles.findingDesc}>{finding.description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
