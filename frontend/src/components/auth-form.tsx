import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Loader2, Mail, Lock, User, LogIn, UserPlus } from "lucide-react";
import { toast } from "sonner";
import { supabase } from "@/lib/supabase";

interface AuthFormProps {
  onAuthSuccess: () => void;
}

export function AuthForm({ onAuthSuccess }: AuthFormProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [isMagicLink, setIsMagicLink] = useState(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isLogin) {
        // Sign in with email and password
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });

        if (error) {
          console.error("Sign in error:", error);

          // Provide more specific error messages
          if (error.message.includes("Invalid login credentials")) {
            toast.error(
              "Invalid email or password. Please check your credentials or sign up first."
            );
          } else if (error.message.includes("Email not confirmed")) {
            toast.error("Please verify your email address before signing in.");
          } else {
            toast.error(error.message || "Failed to sign in");
          }
          return;
        }

        if (data?.user) {
          toast.success("Welcome back!");
          onAuthSuccess();
        }
      } else {
        // Sign up with email and password
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: {
              name: name,
            },
          },
        });

        if (error) {
          console.error("Sign up error:", error);
          toast.error(error.message || "Failed to create account");
          return;
        }

        if (data?.user) {
          toast.success(
            "Account created! Please check your email to verify your account."
          );
          // Switch to login mode
          setIsLogin(true);
          setPassword(""); // Clear password
        }
      }
    } catch (error: any) {
      console.error("Auth error:", error);
      toast.error(error?.message || "An unexpected error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const handleMagicLink = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const { error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: window.location.origin,
        },
      });

      if (error) throw error;

      toast.success("Magic link sent! Check your email.");
      setIsMagicLink(false);
    } catch (error: any) {
      console.error("Magic link error:", error);
      toast.error(error.message || "Failed to send magic link");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setIsLoading(true);

    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: window.location.origin,
        },
      });

      if (error) throw error;
    } catch (error: any) {
      console.error("Google sign in error:", error);
      toast.error(error.message || "Failed to sign in with Google");
      setIsLoading(false);
    }
  };

  if (isMagicLink) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardHeader className="space-y-1">
          <CardTitle>Magic Link</CardTitle>
          <CardDescription>
            We'll send you a sign-in link to your email
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleMagicLink}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2 text-foreground">
                <Mail className="h-4 w-4" />
                Email
              </label>
              <Input
                type="email"
                placeholder="farmer@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col gap-2">
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Sending...
                </>
              ) : (
                "Send Magic Link"
              )}
            </Button>
            <Button
              type="button"
              variant="ghost"
              className="w-full"
              onClick={() => setIsMagicLink(false)}
              disabled={isLoading}
            >
              Back to login
            </Button>
          </CardFooter>
        </form>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="space-y-1">
        <CardTitle>{isLogin ? "Welcome Back" : "Create Account"}</CardTitle>
        <CardDescription>
          {isLogin
            ? "Sign in to continue your farming journey"
            : "Join Kheti to get personalized agricultural assistance"}
        </CardDescription>
      </CardHeader>
      <form onSubmit={handleEmailAuth}>
        <CardContent className="space-y-4">
          {!isLogin && (
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2 text-foreground">
                <User className="h-4 w-4" />
                Name
              </label>
              <Input
                type="text"
                placeholder="Your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required={!isLogin}
                disabled={isLoading}
              />
            </div>
          )}

          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2 text-foreground">
              <Mail className="h-4 w-4" />
              Email
            </label>
            <Input
              type="email"
              placeholder="farmer@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-2 text-foreground">
              <Lock className="h-4 w-4" />
              Password
            </label>
            <Input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={isLoading}
              minLength={6}
            />
          </div>
        </CardContent>
        <CardFooter className="flex flex-col gap-3">
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {isLogin ? "Signing in..." : "Creating account..."}
              </>
            ) : (
              <>
                {isLogin ? (
                  <>
                    <LogIn className="mr-2 h-4 w-4" />
                    Sign In
                  </>
                ) : (
                  <>
                    <UserPlus className="mr-2 h-4 w-4" />
                    Sign Up
                  </>
                )}
              </>
            )}
          </Button>

          <div className="relative w-full my-2">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-card px-2 text-muted-foreground">
                Or continue with
              </span>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            className="w-full"
            onClick={handleGoogleSignIn}
            disabled={isLoading}
          >
            <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="currentColor"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="currentColor"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="currentColor"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Sign in with Google
          </Button>

          <Button
            type="button"
            variant="link"
            className="w-full"
            onClick={() => setIsMagicLink(true)}
            disabled={isLoading}
          >
            <Mail className="mr-2 h-4 w-4" />
            Sign in with Magic Link
          </Button>

          <div className="text-center text-sm pt-2">
            {isLogin ? (
              <span>
                Don't have an account?{" "}
                <button
                  type="button"
                  onClick={() => setIsLogin(false)}
                  className="text-primary hover:underline font-medium"
                  disabled={isLoading}
                >
                  Sign up
                </button>
              </span>
            ) : (
              <span>
                Already have an account?{" "}
                <button
                  type="button"
                  onClick={() => setIsLogin(true)}
                  className="text-primary hover:underline font-medium"
                  disabled={isLoading}
                >
                  Sign in
                </button>
              </span>
            )}
          </div>
        </CardFooter>
      </form>
    </Card>
  );
}
