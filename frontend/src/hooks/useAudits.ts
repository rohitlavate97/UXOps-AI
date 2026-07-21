import { useState, useCallback } from "react";
import { apiClient } from "../api/apiClient";
import { useWorkspace } from "../contexts/WorkspaceContext";

export interface Audit {
  id: string;
  workspace_id: string;
  title: string;
  status: string;
  screenshot_s3_key: string;
  overall_score: number | null;
  ui_score: number | null;
  ux_score: number | null;
  accessibility_score: number | null;
  consistency_score: number | null;
  readability_score: number | null;
  created_at: string;
  updated_at: string;
}

export function useAudits() {
  const { activeWorkspace } = useWorkspace();
  const [audits, setAudits] = useState<Audit[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAudits = useCallback(async () => {
    if (!activeWorkspace) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<Audit[]>(`/workspaces/${activeWorkspace.id}/audits/`);
      setAudits(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch audits");
    } finally {
      setIsLoading(false);
    }
  }, [activeWorkspace]);

  const createAudit = async (title: string, file: File) => {
    if (!activeWorkspace) throw new Error("No active workspace");

    // Upload requires multipart/form-data
    const formData = new FormData();
    formData.append("title", title);
    formData.append("file", file);

    const response = await apiClient.post<Audit>(
      `/workspaces/${activeWorkspace.id}/audits/upload`,
      formData,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );
    
    // Trigger the analysis pipeline right after creation
    await triggerAnalysis(response.data.id);
    
    // Refresh the list
    await fetchAudits();
    
    return response.data;
  };

  const triggerAnalysis = async (auditId: string) => {
    if (!activeWorkspace) throw new Error("No active workspace");
    
    const response = await apiClient.post(
      `/workspaces/${activeWorkspace.id}/analyze`,
      { audit_id: auditId }
    );
    return response.data;
  };

  return {
    audits,
    isLoading,
    error,
    fetchAudits,
    createAudit,
    triggerAnalysis
  };
}
