import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/auth-context";
import { Button } from "@/components/ui/button";
import { MessageSquare, Plus, Trash2, Globe, Lock, LogOut } from "lucide-react";
import { toast } from "sonner";
import { useNavigate, useParams } from "react-router";
import { authenticatedFetch } from "@/lib/api";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface Session {
  id: string;
  title: string;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export function SessionsSidebar() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [publicDialogOpen, setPublicDialogOpen] = useState(false);
  const [selectedSession, setSelectedSession] = useState<Session | null>(null);
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const { sessionId } = useParams();

  const fetchSessions = async () => {
    try {
      const response = await authenticatedFetch("/chat/sessions");

      if (!response.ok) throw new Error("Failed to fetch sessions");

      const data = await response.json();
      setSessions(data.sessions);
    } catch (error) {
      console.error("Error fetching sessions:", error);
      toast.error("Failed to load chat history");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchSessions();
    }
  }, [user]);

  // Refresh sessions when URL changes (e.g., after forking)
  useEffect(() => {
    if (user && sessionId) {
      // Slight delay to ensure backend has updated
      const timer = setTimeout(() => {
        fetchSessions();
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [sessionId, user]);

  const createNewSession = async () => {
    console.log(
      "Creating new session - current path:",
      window.location.pathname
    );

    // Navigate to home and force a clean state
    navigate("/", { replace: true });

    console.log("Navigated to home - new path:", window.location.pathname);

    // Small delay to ensure navigation completes
    setTimeout(() => {
      toast.success("Started new chat");
      console.log("Toast shown - final path:", window.location.pathname);
    }, 100);
  };

  const openDeleteDialog = (session: Session, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedSession(session);
    setDeleteDialogOpen(true);
  };

  const confirmDelete = async () => {
    if (!selectedSession) return;

    try {
      await authenticatedFetch(`/chat/sessions/${selectedSession.id}`, {
        method: "DELETE",
      });

      setSessions(sessions.filter((s) => s.id !== selectedSession.id));
      toast.success("Chat deleted");

      // Navigate to home if deleting current session
      if (selectedSession.id === sessionId) {
        navigate("/");
      }
    } catch (error) {
      console.error("Error deleting session:", error);
      toast.error("Failed to delete chat");
    } finally {
      setDeleteDialogOpen(false);
      setSelectedSession(null);
    }
  };

  const openPublicDialog = (session: Session, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedSession(session);
    setPublicDialogOpen(true);
  };

  const confirmTogglePublic = async () => {
    if (!selectedSession) return;

    try {
      await authenticatedFetch(`/chat/sessions/${selectedSession.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          is_public: !selectedSession.is_public,
        }),
      });

      setSessions(
        sessions.map((s) =>
          s.id === selectedSession.id ? { ...s, is_public: !s.is_public } : s
        )
      );

      toast.success(
        selectedSession.is_public ? "Chat is now private" : "Chat is now public"
      );
    } catch (error) {
      console.error("Error updating session:", error);
      toast.error("Failed to update chat");
    } finally {
      setPublicDialogOpen(false);
      setSelectedSession(null);
    }
  };

  return (
    <div className="w-56 border-r bg-card/50 flex flex-col h-full">
      {/* New Chat Button - Compact */}
      <div className="p-2">
        <Button
          onClick={createNewSession}
          className="w-full h-9 text-sm"
          variant="default"
        >
          <Plus className="h-4 w-4 mr-1" />
          New
        </Button>
      </div>

      {/* Sessions List - Minimal */}
      <div className="flex-1 overflow-y-auto px-2 py-1">
        {loading ? (
          <div className="text-center py-4">
            <p className="text-xs text-muted-foreground">Loading chats...</p>
          </div>
        ) : sessions.length === 0 ? (
          <div className="text-center py-8 px-2">
            <MessageSquare className="h-6 w-6 mx-auto mb-2 text-muted-foreground/50" />
            <p className="text-xs text-muted-foreground">No chats</p>
          </div>
        ) : (
          <div className="space-y-1">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={`group relative rounded-md px-2 py-2 cursor-pointer transition-colors ${
                  sessionId === session.id ? "bg-accent" : "hover:bg-accent/50"
                }`}
                onClick={() => navigate(`/chat/${session.id}`)}
              >
                <div className="flex items-center gap-2 pr-12">
                  <MessageSquare className="h-3.5 w-3.5 flex-shrink-0 text-muted-foreground" />
                  <p
                    className="text-xs font-medium truncate"
                    title={session.title}
                  >
                    {session.title}
                  </p>
                </div>

                {/* Action buttons - show on hover */}
                <div className="absolute top-1.5 right-1.5 flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-5 w-5"
                    onClick={(e) => openPublicDialog(session, e)}
                    title={session.is_public ? "Make private" : "Make public"}
                  >
                    {session.is_public ? (
                      <Globe className="h-3 w-3" />
                    ) : (
                      <Lock className="h-3 w-3" />
                    )}
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-5 w-5 text-destructive"
                    onClick={(e) => openDeleteDialog(session, e)}
                    title="Delete"
                  >
                    <Trash2 className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Account Section at Bottom - Ultra Minimal & Sleek */}
      <div className="border-t p-3 space-y-2.5">
        {user && (
          <>
            {/* User Email - Clean Typography */}
            <div className="px-2.5 py-2 text-xs font-medium text-muted-foreground truncate">
              {user.email}
            </div>
            {/* Sign Out - Subtle Button */}
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start h-8 text-xs text-muted-foreground hover:text-foreground hover:bg-accent/50"
              onClick={() => {
                signOut();
                toast.success("Signed out successfully");
              }}
            >
              <LogOut className="h-3.5 w-3.5 mr-2" />
              Sign Out
            </Button>
          </>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Chat?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This chat and all its messages will
              be permanently deleted.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Public/Private Toggle Confirmation Dialog */}
      <AlertDialog open={publicDialogOpen} onOpenChange={setPublicDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {selectedSession?.is_public
                ? "Make Chat Private?"
                : "Make Chat Public?"}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {selectedSession?.is_public
                ? "This chat will no longer be accessible to anyone with the link."
                : "Anyone with the link will be able to view this chat."}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmTogglePublic}>
              {selectedSession?.is_public ? "Make Private" : "Make Public"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
