import { useState, useEffect } from "react";
import indiaMapPlaceholder from "../assets/india-groundwater-map.png";

const ImageViewer = ({ imageUrl }) => {
  const [imageError, setImageError] = useState(false);
  const [currentImageUrl, setCurrentImageUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  
  // Update current image URL when prop changes
  useEffect(() => {
    if (imageUrl && imageUrl !== currentImageUrl) {
      setIsLoading(true);
      setImageError(false);
      setCurrentImageUrl(imageUrl);
      console.log("ImageViewer received new URL:", imageUrl);
    }
  }, [imageUrl, currentImageUrl]);
  
  const displayImage = currentImageUrl && !imageError ? currentImageUrl : indiaMapPlaceholder;

  const handleImageLoad = () => {
    setIsLoading(false);
    setImageError(false);
    console.log("Image loaded successfully:", currentImageUrl);
  };

  const handleImageError = () => {
    setIsLoading(false);
    if (currentImageUrl) {
      setImageError(true);
      console.log("Image failed to load:", currentImageUrl);
    }
  };

  return (
    <div className="bg-surface rounded-lg border p-6 h-full">
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-foreground">
            Groundwater Analysis Chart
          </h3>
          <p className="text-sm text-muted-foreground">
            {currentImageUrl ? "AI-generated district comparison" : "Default India groundwater map"}
          </p>
        </div>

        {/* Image Container */}
        <div className="flex-1 flex items-center justify-center relative">
          {isLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-surface/80 rounded-lg">
              <div className="flex flex-col items-center gap-2">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <p className="text-sm text-muted-foreground">Loading new chart...</p>
              </div>
            </div>
          )}
          
          <img
            src={displayImage}
            alt="Groundwater Status Map"
            className="max-w-full max-h-full object-contain rounded-lg"
            onLoad={handleImageLoad}
            onError={handleImageError}
            key={currentImageUrl} // Force re-render when URL changes
          />
        </div>
        
        {/* Legend */}
        <div className="mt-4 pt-4 border-t">
          <div className="flex items-center justify-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-status-safe rounded"></div>
              <span className="text-muted-foreground">Safe</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-status-semi-critical rounded"></div>
              <span className="text-muted-foreground">Semi-Critical</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-status-over-exploit rounded"></div>
              <span className="text-muted-foreground">Over-Exploit</span>
            </div>
          </div>
          
          {/* Chart Info */}
          {currentImageUrl && !imageError && (
            <div className="mt-3 text-center">
              <p className="text-xs text-muted-foreground">
                📊 Chart updated • Generated from real groundwater data
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageViewer;
