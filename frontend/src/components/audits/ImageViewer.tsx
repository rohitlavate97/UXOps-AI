import { useState, useRef, useEffect } from "react";
import type { Finding } from "../../hooks/useAudits";
import styles from "./ImageViewer.module.css";
import { clsx } from "clsx";

interface ImageViewerProps {
  imageUrl: string;
  findings: Finding[];
  activeFindingId: string | null;
  onFindingClick: (findingId: string) => void;
}

export function ImageViewer({ imageUrl, findings, activeFindingId, onFindingClick }: ImageViewerProps) {
  const [imageSize, setImageSize] = useState({ width: 1, height: 1 });
  const containerRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const [containerSize, setContainerSize] = useState({ width: 0, height: 0 });

  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current) {
        setContainerSize({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight
        });
      }
    };
    
    // Initial size
    handleResize();
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleImageLoad = () => {
    if (imgRef.current) {
      setImageSize({
        width: imgRef.current.naturalWidth,
        height: imgRef.current.naturalHeight
      });
    }
  };

  // Calculate scaling factor to map original image coordinates to rendered size
  let scaleX = 1;
  let scaleY = 1;
  let offsetX = 0;
  let offsetY = 0;

  if (containerSize.width > 0 && containerSize.height > 0 && imageSize.width > 0) {
    const containerRatio = containerSize.width / containerSize.height;
    const imageRatio = imageSize.width / imageSize.height;

    // The image has object-fit: contain
    if (imageRatio > containerRatio) {
      // Image is wider than container, so it's constrained by width
      const renderedWidth = containerSize.width;
      const renderedHeight = renderedWidth / imageRatio;
      scaleX = renderedWidth / imageSize.width;
      scaleY = scaleX;
      offsetX = 0;
      offsetY = (containerSize.height - renderedHeight) / 2;
    } else {
      // Image is taller than container, so it's constrained by height
      const renderedHeight = containerSize.height;
      const renderedWidth = renderedHeight * imageRatio;
      scaleY = renderedHeight / imageSize.height;
      scaleX = scaleY;
      offsetX = (containerSize.width - renderedWidth) / 2;
      offsetY = 0;
    }
  }

  const getSeverityColor = (severity: string) => {
    switch(severity) {
      case 'high': return 'var(--error)';
      case 'medium': return 'var(--warning)';
      case 'low': return 'var(--info, #3b82f6)';
      default: return 'var(--accent-primary)';
    }
  };

  return (
    <div className={styles.container} ref={containerRef}>
      <img 
        ref={imgRef}
        src={imageUrl} 
        alt="Audit Screenshot" 
        className={styles.image}
        onLoad={handleImageLoad}
      />
      
      {/* SVG Overlay for Bounding Boxes */}
      <svg className={styles.svgOverlay}>
        {findings.map((finding) => {
          if (!finding.bounding_box) return null;
          
          const [x, y, w, h] = finding.bounding_box;
          const isActive = activeFindingId === finding.id;
          
          return (
            <rect
              key={finding.id}
              x={offsetX + x * scaleX}
              y={offsetY + y * scaleY}
              width={w * scaleX}
              height={h * scaleY}
              fill={isActive ? 'rgba(59, 130, 246, 0.2)' : 'transparent'}
              stroke={isActive ? 'var(--accent-primary)' : getSeverityColor(finding.severity)}
              strokeWidth={isActive ? 3 : 2}
              className={clsx(styles.boundingBox, { [styles.active]: isActive })}
              onClick={() => onFindingClick(finding.id)}
              rx={4}
            />
          );
        })}
      </svg>
    </div>
  );
}
