import { useState } from "react";
import Header from "./components/Header";
import ImageViewer from "./components/ImageViewer";
import ChatAssistant from "./components/ChatAssistant";

const Index = () => {
  const [currentImageUrl, setCurrentImageUrl] = useState("");

  const handleImageUpdate = (imageUrl) => {
    setCurrentImageUrl(imageUrl);
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="h-calc-100vh-80px p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
          <div className="h-full">
            <ImageViewer imageUrl={currentImageUrl} />
          </div>
          
          <div className="h-full">
            <ChatAssistant onImageUpdate={handleImageUpdate} />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
