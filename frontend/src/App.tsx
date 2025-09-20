import { ThemeProvider } from "@/components/theme-provider";
import { ChatInterface } from "@/components/chat-interface";
import { ModeToggle } from "@/components/mode-toggle";
import { Toaster } from "@/components/ui/sonner";

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <div className="h-screen flex flex-col bg-background">
        {/* Theme toggle in top-right corner */}
        <div className="absolute top-4 right-4 z-50">
          <ModeToggle />
        </div>

        {/* Main chat interface */}
        <ChatInterface />

        {/* Toast notifications */}
        <Toaster />
      </div>
    </ThemeProvider>
  );
}

export default App;
