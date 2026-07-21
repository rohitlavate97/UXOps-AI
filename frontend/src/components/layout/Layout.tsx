import { Outlet } from "react-router";
import { Sidebar } from "./Sidebar";
import { Navbar } from "./Navbar";
import styles from "./Layout.module.css";

export function Layout() {
  return (
    <div className={styles.layout}>
      <Sidebar />
      <div className={styles.main}>
        <Navbar />
        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
