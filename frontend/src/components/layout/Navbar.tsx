import { clsx } from "clsx";
import { Bell, Search } from "lucide-react";
import styles from "./Navbar.module.css";

export function Navbar() {
  return (
    <header className={clsx(styles.navbar, "glass")}>
      <div className={styles.searchContainer}>
        <Search className={styles.searchIcon} />
        <input 
          type="text" 
          placeholder="Search audits, reports, or issues..." 
          className={styles.searchInput}
        />
      </div>

      <div className={styles.actions}>
        <button className={styles.iconBtn}>
          <Bell className={styles.icon} />
          <span className={styles.badge}></span>
        </button>
        <button className="btn btn-primary">
          New Audit
        </button>
      </div>
    </header>
  );
}
