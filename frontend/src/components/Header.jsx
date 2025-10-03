import { Droplets } from "lucide-react";

const Header = () => {
  return (
    <header className="bg-surface border-b px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-lg">
            <Droplets className="w-6 h-6 text-primary-foreground" />
          </div>
          <h1 className="text-xl font-semibold text-foreground">
            INGRES Virtual Assistant
          </h1>
        </div>
        
        <nav className="flex items-center gap-6">
          {[
            { name: "Home", active: true },
            { name: "ChatBot", active: false },
            { name: "Maps", active: false },
            { name: "Alerts", active: false },
          ].map((item) => (
            <button
              key={item.name}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                item.active
                  ? "text-primary bg-primary-light/20"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
            >
              {item.name}
            </button>
          ))}
        </nav>
      </div>
    </header>
  );
};

export default Header;
