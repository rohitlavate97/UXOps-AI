import { useState, useCallback } from "react";
import { apiClient } from "../api/apiClient";
import { useWorkspace } from "../contexts/WorkspaceContext";

export interface Finding {
  id: string;
  category: string;
  description: string;
  severity: "high" | "medium" | "low";
  bounding_box: [number, number, number, number] | null; // [x, y, w, h]
  created_at: string;
}

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
  findings?: Finding[]; // Optional, populated on detail fetch
}

export function useAudits() {
  const { activeWorkspace } = useWorkspace();
  const [audits, setAudits] = useState<Audit[]>([]);
  const [currentAudit, setCurrentAudit] = useState<Audit | null>(null);
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

  const fetchAuditDetails = useCallback(async (auditId: string) => {
    if (!activeWorkspace) return null;
    
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<Audit>(`/workspaces/${activeWorkspace.id}/audits/${auditId}`);
      setCurrentAudit(response.data);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch audit details");
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [activeWorkspace]);

  return {
    audits,
    currentAudit,
    isLoading,
    error,
    fetchAudits,
    fetchAuditDetails,
    createAudit,
    triggerAnalysis
  };
}
