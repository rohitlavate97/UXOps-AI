import { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { useWorkspace } from "../../contexts/WorkspaceContext";
import { NewAuditModal } from "../audits/NewAuditModal";
import styles from "./Navbar.module.css";
import { Bell, LogOut, Plus } from "lucide-react";
import { clsx } from "clsx";

export function Navbar() {
  const { user, logout } = useAuth();
  const { activeWorkspace } = useWorkspace();
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <nav className={clsx(styles.navbar, "glass")}>
        <div className={styles.left}>
          {activeWorkspace && (
            <span className={styles.workspaceBadge}>{activeWorkspace.name}</span>
          )}
        </div>

        <div className={styles.right}>
          <button 
            className="btn btn-primary" 
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem' }}
            onClick={() => setIsModalOpen(true)}
          >
            <Plus size={16} />
            New Audit
          </button>
          
          <button className={styles.iconBtn} aria-label="Notifications">
            <Bell size={20} />
          </button>
          
          <div className={styles.profile}>
            <div className={styles.avatar}>
              {user?.full_name?.charAt(0) || "U"}
            </div>
            <span className={styles.userName}>{user?.full_name}</span>
          </div>

          <button className={styles.iconBtn} onClick={logout} title="Sign out">
            <LogOut size={20} />
          </button>
        </div>
      </nav>

      <NewAuditModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </>
  );
}
