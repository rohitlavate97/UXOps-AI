import { clsx } from "clsx";
import { Activity, Settings, LayoutDashboard, FileText, CheckSquare, Search } from "lucide-react";
import { Link, useLocation } from "react-router";
import styles from "./Sidebar.module.css";

const navItems = [
  { name: "Dashboard", path: "/", icon: LayoutDashboard },
  { name: "Audits", path: "/audits", icon: CheckSquare },
  { name: "Reports", path: "/reports", icon: FileText },
  { name: "Activity", path: "/activity", icon: Activity },
  { name: "Settings", path: "/settings", icon: Settings },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className={clsx(styles.sidebar, "glass")}>
      <div className={styles.logo}>
        <div className={styles.logoIcon}>
          <Search className={styles.icon} />
        </div>
        <span className={styles.logoText}>UXOps AI</span>
      </div>

      <nav className={styles.nav}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.name}
              to={item.path}
              className={clsx(styles.navItem, isActive && styles.active)}
            >
              <item.icon className={styles.navIcon} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className={styles.footer}>
        <div className={styles.userCard}>
          <div className={styles.avatar}>U</div>
          <div className={styles.userInfo}>
            <span className={styles.userName}>Workspace Admin</span>
            <span className={styles.userRole}>Pro Plan</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
