import { useState, useRef } from "react";
import { useAudits } from "../../hooks/useAudits";
import styles from "./NewAuditModal.module.css";
import { clsx } from "clsx";
import { X, UploadCloud, FileImage } from "lucide-react";

interface NewAuditModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function NewAuditModal({ isOpen, onClose }: NewAuditModalProps) {
  const { createAudit } = useAudits();
  const [title, setTitle] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.type.startsWith("image/")) {
        setError("Please select an image file (PNG, JPG)");
        return;
      }
      setFile(selectedFile);
      setError(null);
      // Create preview URL
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result as string);
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select an image to audit");
      return;
    }
    if (!title.trim()) {
      setError("Please provide a title");
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      await createAudit(title, file);
      // Reset and close
      setTitle("");
      setFile(null);
      setPreview(null);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to start audit");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={clsx(styles.modal, "glass")} onClick={e => e.stopPropagation()}>
        <div className={styles.header}>
          <h2 className={styles.title}>New Design Audit</h2>
          <button className={styles.closeBtn} onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <div className={styles.error}>{error}</div>}

          <div className={styles.inputGroup}>
            <label htmlFor="title">Audit Title</label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className={styles.input}
              placeholder="e.g. Landing Page Hero Redesign"
              required
            />
          </div>

          <div className={styles.inputGroup}>
            <label>Upload Screenshot</label>
            <div 
              className={styles.uploadArea}
              onClick={() => fileInputRef.current?.click()}
            >
              {preview ? (
                <div className={styles.previewContainer}>
                  <img src={preview} alt="Preview" className={styles.previewImage} />
                  <div className={styles.changeOverlay}>
                    <FileImage size={24} />
                    <span>Change image</span>
                  </div>
                </div>
              ) : (
                <div className={styles.uploadEmpty}>
                  <UploadCloud size={32} className={styles.uploadIcon} />
                  <span className={styles.uploadText}>Click to upload or drag and drop</span>
                  <span className={styles.uploadSubtext}>PNG, JPG up to 10MB</span>
                </div>
              )}
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept="image/*"
                className={styles.hiddenInput}
              />
            </div>
          </div>

          <div className={styles.footer}>
            <button type="button" className="btn" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting || !file}>
              {isSubmitting ? "Starting Audit..." : "Start Audit"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
