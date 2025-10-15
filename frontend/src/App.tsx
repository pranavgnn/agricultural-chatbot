import { ThemeProvider } from "@/components/theme-provider";
import { ChatInterface } from "@/components/chat-interface";
import { SessionsSidebar } from "@/components/sessions-sidebar";
import { ModeToggle } from "@/components/mode-toggle";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider, useAuth } from "@/contexts/auth-context";
import { AuthForm } from "@/components/auth-form";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import {
  BrowserRouter,
  Routes,
  Route,
  useNavigate,
  useLocation,
} from "react-router";

// Consistent top bar for all pages
function TopBar() {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="fixed top-0 left-0 right-0 h-14 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 z-50">
      <div className="flex items-center justify-between h-full px-4">
        <button
          onClick={() => navigate("/")}
          className="flex items-center gap-2 hover:opacity-80 transition-opacity cursor-pointer"
        >
          <span className="text-2xl">🌾</span>
          <h1 className="text-xl font-bold text-primary">Kheti</h1>
        </button>

        <div className="flex items-center gap-2">
          {!user && (
            <Button
              variant="default"
              size="sm"
              onClick={() => navigate("/login")}
            >
              Sign In
            </Button>
          )}
          <ModeToggle />
        </div>
      </div>
    </div>
  );
}

function AppContent() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Handle new session - navigate only if we're not already on a chat page
  const handleNewSession = (
    sessionId: string,
    shouldNavigate: boolean = true
  ) => {
    if (shouldNavigate) {
      navigate(`/chat/${sessionId}`);
    }
    // If not navigating, the session list will refresh automatically
  };

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Login/Guest page
  if (!user) {
    return (
      <>
        <Routes>
          {/* Guest can access chat without login */}
          <Route
            path="/"
            element={
              <div className="h-screen flex flex-col bg-background">
                <TopBar />
                <div className="flex-1 overflow-hidden pt-14">
                  <ChatInterface
                    key={location.pathname}
                    onNewSession={handleNewSession}
                  />
                </div>
                <Toaster />
              </div>
            }
          />

          {/* Guest can view public chats */}
          <Route
            path="/chat/:sessionId"
            element={
              <div className="h-screen flex flex-col bg-background">
                <TopBar />
                <div className="flex-1 overflow-hidden pt-14">
                  <ChatInterface
                    key={location.pathname}
                    onNewSession={handleNewSession}
                  />
                </div>
                <Toaster />
              </div>
            }
          />

          {/* Login page */}
          <Route
            path="/login"
            element={
              <div className="min-h-screen bg-background">
                <TopBar />

                <div className="min-h-screen flex items-center justify-center p-4 pt-20">
                  <div className="w-full max-w-md space-y-6">
                    <div className="text-center">
                      <h2 className="text-2xl font-bold mb-2">Welcome Back</h2>
                      <p className="text-sm text-muted-foreground">
                        Sign in to save your chat history
                      </p>
                    </div>

                    <AuthForm onAuthSuccess={() => navigate("/")} />

                    <div className="relative">
                      <div className="absolute inset-0 flex items-center">
                        <span className="w-full border-t" />
                      </div>
                      <div className="relative flex justify-center text-xs uppercase">
                        <span className="bg-background px-2 text-muted-foreground">
                          Or continue as
                        </span>
                      </div>
                    </div>

                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => navigate("/")}
                    >
                      Guest
                    </Button>

                    <p className="text-xs text-center text-muted-foreground">
                      Guest chats are temporary and won't be saved
                    </p>
                  </div>
                </div>

                <Toaster />
              </div>
            }
          />

          {/* Redirect any other route to home for guests */}
          <Route
            path="*"
            element={
              <div className="h-screen flex flex-col bg-background">
                <TopBar />
                <div className="flex-1 overflow-hidden pt-14">
                  <ChatInterface
                    key={location.pathname}
                    onNewSession={handleNewSession}
                  />
                </div>
                <Toaster />
              </div>
            }
          />
        </Routes>
      </>
    );
  }

  // Main app (logged in)
  return (
    <div className="h-screen flex flex-col bg-background">
      <TopBar />

      <div className="flex-1 flex overflow-hidden pt-14">
        {/* Sidebar for logged-in users */}
        <SessionsSidebar />

        {/* Main chat area - Use location.pathname as key to force remount on route change */}
        <div className="flex-1 overflow-hidden">
          <Routes>
            <Route
              path="/"
              element={
                <ChatInterface
                  key={location.pathname}
                  onNewSession={handleNewSession}
                />
              }
            />
            <Route
              path="/chat/:sessionId"
              element={
                <ChatInterface
                  key={location.pathname}
                  onNewSession={handleNewSession}
                />
              }
            />
            <Route
              path="/login"
              element={
                <ChatInterface
                  key={location.pathname}
                  onNewSession={handleNewSession}
                />
              }
            />
            {/* Catch-all: redirect to home */}
            <Route
              path="*"
              element={
                <ChatInterface
                  key={location.pathname}
                  onNewSession={handleNewSession}
                />
              }
            />
          </Routes>
        </div>
      </div>

      <Toaster />
    </div>
  );
}

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <AuthProvider>
        <BrowserRouter>
          <AppContent />
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
