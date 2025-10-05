import { useState } from "react";
import Header from "./components/Header.jsx";
import ChatAssistant from "./components/ChatAssistant.jsx";
import WaterExtractionDashboard from "./components/WaterExtractionDashboard.jsx";

const Index = () => {
  // State to hold the data for the visualization component. Initialized to null.
  const [visualizationData, setVisualizationData] = useState(null);

  // This handler is passed to the ChatAssistant.
  // The ChatAssistant must call this function with the data it gets from the backend.
  const handleDataUpdate = (data) => {
    setVisualizationData(data);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      
      <main className="h-[calc(100vh-80px)] p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
          
          {/* Left Side: The dynamic dashboard */}
          <div className="h-full min-h-0"> {/* min-h-0 is important for flex/grid children to not overflow */}
            <WaterExtractionDashboard data={visualizationData} />
          </div>
          
          {/* Right Side: The chat assistant */}
          <div className="h-full min-h-0">
            <ChatAssistant onDataUpdate={handleDataUpdate} />
          </div>

        </div>
      </main>
    </div>
  );
};

export default Index;