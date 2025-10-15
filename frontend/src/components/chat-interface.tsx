import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Loader2, Bot, User, Mic, MicOff, Eye } from "lucide-react";
import { toast } from "sonner";
import { SuggestionQueries } from "@/components/suggestion-queries";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useParams } from "react-router";
import { authenticatedFetch } from "@/lib/api";
import { supabase } from "@/lib/supabase";

interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

interface ChatInterfaceProps {
  onNewSession?: (sessionId: string, shouldNavigate?: boolean) => void;
}

export function ChatInterface({ onNewSession }: ChatInterfaceProps = {}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoadingSession, setIsLoadingSession] = useState(false); // Loading session from DB
  const [isBotThinking, setIsBotThinking] = useState(false); // Bot is generating response
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const { sessionId } = useParams();
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(
    sessionId || null
  );
  const [isPublicSession, setIsPublicSession] = useState(false);
  const [hasForked, setHasForked] = useState(false);
  const [skipNextLoad, setSkipNextLoad] = useState(false); // Skip loading after fork

  // Debug: Log when component mounts/unmounts
  useEffect(() => {
    console.log("ChatInterface mounted with sessionId:", sessionId);
    return () => {
      console.log("ChatInterface unmounting");
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check if user is logged in
  useEffect(() => {
    const checkAuth = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();
      setIsLoggedIn(!!session);
    };
    checkAuth();

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setIsLoggedIn(!!session);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  // Load session messages when sessionId changes
  useEffect(() => {
    if (skipNextLoad) {
      console.log("Skipping load after fork");
      setSkipNextLoad(false);
      return;
    }

    if (sessionId) {
      setCurrentSessionId(sessionId);
      // Show loading state immediately
      setShowSuggestions(false);
      loadSessionMessages(sessionId);
    } else {
      // No session selected, reset everything and show suggestions
      console.log("No sessionId in URL, resetting to new chat");
      setMessages([]);
      setShowSuggestions(true);
      setCurrentSessionId(null);
      setIsPublicSession(false);
      setHasForked(false);
    }
  }, [sessionId]);

  const loadSessionMessages = async (sid: string) => {
    // Don't try to load temporary sessions from the server
    if (sid.startsWith("temp-") || sid.startsWith("anon-")) {
      setMessages([]);
      setShowSuggestions(true);
      setIsPublicSession(false);
      return;
    }

    // Show skeleton/loading state
    setIsLoadingSession(true);

    try {
      // Try to load session (works for both public and private sessions)
      const response = await authenticatedFetch(`/chat/sessions/${sid}`).catch(
        (error) => {
          console.log(
            "Authenticated fetch failed, trying anonymous fetch:",
            error
          );
          // If authenticated fetch fails, try anonymous fetch (for public sessions)
          return fetch(`/chat/sessions/${sid}`, {
            headers: {
              "Content-Type": "application/json",
            },
          });
        }
      );

      console.log("Session fetch response:", response.status, response.ok);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Failed to load session:", response.status, errorText);

        // If it's a 403, show error that session is private
        if (response.status === 403) {
          toast.error("This chat is private. Please sign in to view.");
        } else if (response.status === 404) {
          toast.error("Chat not found.");
        }

        // If session not found or access denied, show homepage
        console.warn("Session not accessible, showing homepage");
        setMessages([]);
        setShowSuggestions(true);
        setCurrentSessionId(null);
        setIsPublicSession(false);
        return;
      }

      const data = await response.json();
      console.log("Session data loaded:", data);

      // Check if this is a public session that we don't own
      const {
        data: { session: currentSession },
      } = await supabase.auth.getSession();
      const userId = currentSession?.user?.id || null;

      const isPublic = data.session.is_public;
      const ownerId = data.session.user_id;
      const isOwner = userId && ownerId === userId;

      console.log("Session check:", { userId, ownerId, isPublic, isOwner });

      setIsPublicSession(isPublic && !isOwner);
      setHasForked(false);

      const loadedMessages: Message[] = data.messages.map(
        (msg: any, index: number) => ({
          id: `${sid}-${index}`,
          content: msg.content,
          isUser: msg.role === "user",
          timestamp: new Date(msg.created_at),
        })
      );

      setMessages(loadedMessages);
      setShowSuggestions(loadedMessages.length === 0);
    } catch (error) {
      console.error("Error loading session (network/parsing error):", error);
      toast.error("Failed to load chat. Please check your connection.");
      // On network errors, keep current state but show error
      // Don't reset to homepage unless the server explicitly said so
    } finally {
      setIsLoadingSession(false);
    }
  };

  // Initialize session on component mount (only if no sessionId from route)
  useEffect(() => {
    if (!sessionId && !currentSessionId) {
      // Don't auto-create session, wait for first message
      setShowSuggestions(true);
    }
  }, []);

  // Voice recording handlers
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);

      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });
        await transcribeAudio(audioBlob);

        // Stop all tracks to release microphone
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
      toast.info("Recording... Click again to stop");
    } catch (error) {
      console.error("Error starting recording:", error);
      toast.error("Failed to access microphone");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    setIsTranscribing(true);
    toast.info("Transcribing audio...");

    try {
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");

      const response = await fetch("/asr/transcribe", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Transcription failed");
      }

      const data = await response.json();
      const transcription = data.transcription;

      setInput(transcription);
      toast.success("Audio transcribed!");

      // Automatically send the transcribed message
      setTimeout(() => {
        sendMessage(transcription);
      }, 100);
    } catch (error) {
      console.error("Error transcribing audio:", error);
      toast.error("Failed to transcribe audio");
    } finally {
      setIsTranscribing(false);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const sendMessage = async (messageText: string = input) => {
    if (!messageText.trim() || isBotThinking) return;

    console.log("Sending message:", messageText.trim());
    console.log("Current session ID:", currentSessionId);
    console.log("Is public session:", isPublicSession);
    console.log("Has forked:", hasForked);

    const userMessage: Message = {
      id: Date.now().toString(),
      content: messageText.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsBotThinking(true);
    setShowSuggestions(false);

    try {
      // If this is a public session we don't own, fork it silently before sending
      let sessionToUse = currentSessionId;

      if (isPublicSession && !hasForked && currentSessionId) {
        console.log("Forking public session silently...");

        try {
          const forkResponse = await authenticatedFetch(
            `/chat/sessions/${currentSessionId}/fork`,
            { method: "POST" }
          ).catch(async (error) => {
            console.log("Authenticated fork failed, trying anonymous:", error);
            return fetch(`/chat/sessions/${currentSessionId}/fork`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
            });
          });

          console.log(
            "Fork response status:",
            forkResponse.status,
            forkResponse.ok
          );

          if (forkResponse.ok) {
            const forkData = await forkResponse.json();
            console.log("Fork successful:", forkData);
            sessionToUse = forkData.session_id;

            // Update state silently
            setCurrentSessionId(forkData.session_id);
            setIsPublicSession(false);
            setHasForked(true);
            setSkipNextLoad(true); // Don't reload when URL changes

            // Update URL without reload
            window.history.replaceState({}, "", `/chat/${forkData.session_id}`);

            // Notify parent to refresh sidebar WITHOUT navigating
            if (onNewSession) {
              onNewSession(forkData.session_id, false);
            }

            console.log("Forked to new session:", forkData.session_id);
          } else {
            const errorText = await forkResponse.text();
            console.error(
              "Fork failed with status:",
              forkResponse.status,
              errorText
            );
          }
        } catch (forkError) {
          console.error("Fork failed with exception:", forkError);
          // Continue with original session if fork fails
        }
      }

      const requestBody = {
        text: messageText.trim(),
        session_id: sessionToUse || undefined,
      };

      console.log("Request body:", requestBody);

      // Use authenticated fetch if user is logged in, otherwise regular fetch
      const response = await authenticatedFetch("/chat", {
        method: "POST",
        body: JSON.stringify(requestBody),
      }).catch(() => {
        // If authenticated fetch fails (no auth), try regular fetch for anonymous
        return fetch("/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestBody),
        });
      });

      console.log("Response status:", response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error response:", errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Response data:", data);

      // Update session ID if it changed (new session created)
      if (data.session_id && data.session_id !== currentSessionId) {
        setCurrentSessionId(data.session_id);

        // For anonymous sessions, update URL without navigation
        if (
          data.session_id.startsWith("anon-") ||
          data.session_id.startsWith("temp-")
        ) {
          console.log(
            "Anonymous session created, updating URL without navigation"
          );
          window.history.replaceState({}, "", `/chat/${data.session_id}`);
          setSkipNextLoad(true); // Skip the next load effect
        } else if (onNewSession) {
          // For logged-in users with persistent sessions, update sidebar
          onNewSession(data.session_id, false); // Don't navigate, just update sidebar
        }
      } else if (
        data.session_id &&
        onNewSession &&
        !data.session_id.startsWith("anon-") &&
        !data.session_id.startsWith("temp-")
      ) {
        // Session exists but title might have been updated, refresh sidebar
        onNewSession(data.session_id, false);
      }

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.output || "I'm sorry, I couldn't process your request.",
        isUser: false,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content:
          "I'm sorry, I'm having trouble connecting right now. Please try again later.",
        isUser: false,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
      toast.error("Failed to send message. Please check your connection.");
    } finally {
      setIsBotThinking(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage();
  };

  const handleSuggestionClick = (query: string) => {
    sendMessage(query);
  };

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Public Session Banner - positioned after sidebar for logged-in users, full width for guests */}
      {isPublicSession && !hasForked && (
        <div
          className={`fixed top-14 ${
            isLoggedIn ? "left-56" : "left-0"
          } right-0 z-40 bg-primary/10 border-b border-primary/20 px-4 py-2.5`}
        >
          <div className="max-w-4xl mx-auto flex items-center gap-2">
            <Eye className="h-4 w-4 text-primary flex-shrink-0" />
            <p className="text-sm text-foreground">
              <strong>Viewing public chat.</strong> Send a message to create
              your own copy and continue the conversation.
            </p>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div
        className={`flex-1 overflow-hidden ${
          isPublicSession && !hasForked ? "pt-[8.5rem]" : "pt-14"
        }`}
      >
        {isLoadingSession ? (
          // Loading skeleton while fetching messages from database
          <div className="h-full overflow-y-auto">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-4">
              <div className="text-center py-12">
                <Loader2 className="h-8 w-8 animate-spin mx-auto text-muted-foreground" />
                <p className="text-sm text-muted-foreground mt-4">
                  Loading chat...
                </p>
              </div>
            </div>
          </div>
        ) : showSuggestions && messages.length === 0 ? (
          <div className="h-full overflow-y-auto">
            <div className="max-w-4xl mx-auto px-6 py-8">
              <SuggestionQueries onQueryClick={handleSuggestionClick} />
            </div>
          </div>
        ) : (
          <div className="h-full overflow-y-auto">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-primary flex items-center justify-center">
                    <Bot className="h-8 w-8 text-primary-foreground" />
                  </div>
                  <h3 className="text-lg font-medium mb-2 text-foreground">
                    Welcome to Kheti
                  </h3>
                  <p className="text-muted-foreground">
                    Ask me anything about agriculture in India
                  </p>
                </div>
              )}

              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.isUser ? "flex-row-reverse" : ""
                  }`}
                >
                  <div className="flex-shrink-0">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        message.isUser ? "bg-accent" : "bg-primary"
                      }`}
                    >
                      {message.isUser ? (
                        <User className="h-4 w-4 text-accent-foreground" />
                      ) : (
                        <Bot className="h-4 w-4 text-primary-foreground" />
                      )}
                    </div>
                  </div>

                  <div className="flex-1 max-w-[85%]">
                    <div
                      className={`rounded-lg px-4 py-2.5 ${
                        message.isUser
                          ? "bg-accent text-accent-foreground ml-auto"
                          : "bg-muted"
                      }`}
                    >
                      {message.isUser ? (
                        <p className="text-sm leading-relaxed whitespace-pre-wrap">
                          {message.content}
                        </p>
                      ) : (
                        <div className="text-sm leading-relaxed markdown-content">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              h1: ({ children }) => (
                                <h1 className="text-xl font-bold mb-3 mt-3 text-foreground border-b border-border pb-1">
                                  {children}
                                </h1>
                              ),
                              h2: ({ children }) => (
                                <h2 className="text-lg font-bold mb-2 mt-3 text-foreground">
                                  {children}
                                </h2>
                              ),
                              h3: ({ children }) => (
                                <h3 className="text-base font-semibold mb-2 mt-2 text-foreground">
                                  {children}
                                </h3>
                              ),
                              h4: ({ children }) => (
                                <h4 className="text-sm font-semibold mb-1 mt-2 text-foreground">
                                  {children}
                                </h4>
                              ),
                              h5: ({ children }) => (
                                <h5 className="text-sm font-medium mb-1 mt-1 text-foreground">
                                  {children}
                                </h5>
                              ),
                              h6: ({ children }) => (
                                <h6 className="text-xs font-medium mb-1 mt-1 text-muted-foreground uppercase tracking-wide">
                                  {children}
                                </h6>
                              ),
                              a: ({ children, href }) => (
                                <a
                                  href={href}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-primary hover:text-primary/80 underline underline-offset-2 transition-colors duration-200"
                                >
                                  {children}
                                </a>
                              ),
                              p: ({ children }) => (
                                <p className="mb-2 last:mb-0">{children}</p>
                              ),
                              ul: ({ children }) => (
                                <ul className="list-disc ml-4 mb-2 space-y-1">
                                  {children}
                                </ul>
                              ),
                              ol: ({ children }) => (
                                <ol className="list-decimal ml-4 mb-2 space-y-1">
                                  {children}
                                </ol>
                              ),
                              li: ({ children }) => <li>{children}</li>,
                              strong: ({ children }) => (
                                <strong className="font-semibold">
                                  {children}
                                </strong>
                              ),
                              em: ({ children }) => (
                                <em className="italic">{children}</em>
                              ),
                              code: ({ children, className }) => {
                                const isInline = !className;
                                return isInline ? (
                                  <code className="bg-muted-foreground/10 px-1 py-0.5 rounded text-xs font-mono">
                                    {children}
                                  </code>
                                ) : (
                                  <code className={className}>{children}</code>
                                );
                              },
                              pre: ({ children }) => (
                                <pre className="bg-muted-foreground/5 p-3 rounded-md overflow-x-auto text-xs font-mono mb-2">
                                  {children}
                                </pre>
                              ),
                              blockquote: ({ children }) => (
                                <blockquote className="border-l-4 border-muted-foreground/20 pl-4 italic mb-2">
                                  {children}
                                </blockquote>
                              ),
                              table: ({ children }) => (
                                <table className="border-collapse border border-muted-foreground/20 mb-2 text-xs">
                                  {children}
                                </table>
                              ),
                              th: ({ children }) => (
                                <th className="border border-muted-foreground/20 px-2 py-1 bg-muted-foreground/5 font-semibold text-left">
                                  {children}
                                </th>
                              ),
                              td: ({ children }) => (
                                <td className="border border-muted-foreground/20 px-2 py-1">
                                  {children}
                                </td>
                              ),
                            }}
                          >
                            {message.content}
                          </ReactMarkdown>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {/* Bot thinking indicator */}
              {isBotThinking && (
                <div className="flex gap-3">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                      <Bot className="h-4 w-4 text-primary-foreground" />
                    </div>
                  </div>
                  <div className="flex-1 max-w-[85%]">
                    <div className="bg-muted rounded-lg px-4 py-2.5">
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">
                          Thinking...
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-border bg-card">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-3">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <div className="flex-1 relative">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about crops, weather, schemes..."
                disabled={isBotThinking || isRecording}
                className="h-11 rounded-lg"
              />
            </div>

            {/* Microphone Button */}
            <Button
              type="button"
              onClick={toggleRecording}
              disabled={isBotThinking || isTranscribing}
              size="icon"
              variant={isRecording ? "destructive" : "secondary"}
              className={`h-11 w-11 rounded-lg ${
                isRecording || isTranscribing ? "animate-pulse" : ""
              }`}
            >
              {isTranscribing ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : isRecording ? (
                <MicOff className="h-4 w-4" />
              ) : (
                <Mic className="h-4 w-4" />
              )}
            </Button>

            {/* Send Button */}
            <Button
              type="submit"
              disabled={
                isBotThinking || !input.trim() || isRecording || isTranscribing
              }
              size="icon"
              className="h-11 w-11 rounded-lg"
            >
              {isBotThinking ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
