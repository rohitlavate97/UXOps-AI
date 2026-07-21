import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { apiClient } from "../api/apiClient";
import { useAuth } from "./AuthContext";

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
}

interface WorkspaceContextType {
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  setActiveWorkspace: (workspace: Workspace | null) => void;
  isLoading: boolean;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const { token, user } = useAuth();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeWorkspace, setActiveWorkspace] = useState<Workspace | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  useEffect(() => {
    const fetchWorkspaces = async () => {
      if (!token || !user) {
        setWorkspaces([]);
        setActiveWorkspace(null);
        return;
      }
      
      setIsLoading(true);
      try {
        const response = await apiClient.get<Workspace[]>("/workspaces/");
        setWorkspaces(response.data);
        
        // If we have workspaces, and no active workspace is selected, pick the first one
        if (response.data.length > 0 && !activeWorkspace) {
          // Alternatively, we could read from localStorage to remember the last active workspace
          const savedWorkspaceId = localStorage.getItem("active_workspace_id");
          const savedWorkspace = response.data.find(w => w.id === savedWorkspaceId);
          setActiveWorkspace(savedWorkspace || response.data[0]);
        }
      } catch (error) {
        console.error("Failed to fetch workspaces", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchWorkspaces();
  }, [token, user]);

  // Persist active workspace choice
  const handleSetActiveWorkspace = (workspace: Workspace | null) => {
    setActiveWorkspace(workspace);
    if (workspace) {
      localStorage.setItem("active_workspace_id", workspace.id);
    } else {
      localStorage.removeItem("active_workspace_id");
    }
  };

  return (
    <WorkspaceContext.Provider 
      value={{ 
        workspaces, 
        activeWorkspace, 
        setActiveWorkspace: handleSetActiveWorkspace, 
        isLoading 
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext);
  if (context === undefined) {
    throw new Error("useWorkspace must be used within a WorkspaceProvider");
  }
  return context;
}
